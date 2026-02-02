"""로컬 RDF Triple Store 모듈.

rdflib 기반 인메모리/파일 트리플 스토어입니다.
SPARQL 쿼리 실행, 그래프 저장/로딩, 배치 처리를 지원합니다.
추후 GraphDB 등 외부 스토어 연동 시 이 인터페이스를 확장합니다.
"""

import logging
import time
from pathlib import Path
from typing import Any

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.query import Result

logger = logging.getLogger(__name__)


class TripleStore:
    """rdflib 기반 로컬 트리플 스토어."""

    def __init__(self, graph: Graph | None = None):
        self._graph = graph if graph is not None else Graph()

    @property
    def graph(self) -> Graph:
        return self._graph

    def __len__(self) -> int:
        return len(self._graph)

    def insert(self, triples: list[tuple]) -> int:
        """트리플 리스트를 삽입한다.

        Args:
            triples: (subject, predicate, object) 튜플의 리스트

        Returns:
            삽입된 트리플 수
        """
        count = 0
        for s, p, o in triples:
            self._graph.add((s, p, o))
            count += 1
        return count

    def insert_graph(self, graph: Graph) -> int:
        """다른 Graph의 모든 트리플을 삽입한다.

        Returns:
            삽입된 트리플 수
        """
        before = len(self._graph)
        self._graph += graph
        inserted = len(self._graph) - before
        logger.info("그래프 삽입: %d 트리플 추가 (총 %d)", inserted, len(self._graph))
        return inserted

    def insert_batch(self, triples: list[tuple], batch_size: int = 1000) -> int:
        """트리플을 배치 단위로 삽입한다.

        대량 삽입 시 메모리 효율을 위해 배치 단위로 처리합니다.

        Args:
            triples: 트리플 리스트
            batch_size: 배치당 트리플 수

        Returns:
            총 삽입된 트리플 수
        """
        total = 0
        for i in range(0, len(triples), batch_size):
            batch = triples[i:i + batch_size]
            total += self.insert(batch)
            if (i // batch_size + 1) % 10 == 0:
                logger.debug("배치 진행: %d / %d", total, len(triples))
        return total

    def query(self, sparql: str) -> list[dict[str, Any]]:
        """SPARQL SELECT 쿼리를 실행하고 결과를 딕셔너리 리스트로 반환한다.

        Args:
            sparql: SPARQL 쿼리 문자열

        Returns:
            결과 행의 리스트. 각 행은 {변수명: 값} 딕셔너리.
        """
        start = time.time()
        result: Result = self._graph.query(sparql)
        elapsed = time.time() - start

        rows = []
        if result.type == "SELECT":
            vars_ = [str(v) for v in result.vars]
            for row in result:
                row_dict = {}
                for i, var in enumerate(vars_):
                    val = row[i]
                    if isinstance(val, Literal):
                        row_dict[var] = val.toPython()
                    elif isinstance(val, URIRef):
                        row_dict[var] = str(val)
                    else:
                        row_dict[var] = val
                rows.append(row_dict)

        logger.debug("SPARQL 쿼리 실행: %d 결과, %.3f초", len(rows), elapsed)
        return rows

    def query_raw(self, sparql: str) -> Result:
        """SPARQL 쿼리를 실행하고 rdflib Result 원본을 반환한다."""
        return self._graph.query(sparql)

    def ask(self, sparql: str) -> bool:
        """SPARQL ASK 쿼리를 실행한다."""
        result = self._graph.query(sparql)
        return bool(result.askAnswer)

    def count(self) -> int:
        """스토어의 전체 트리플 수를 반환한다."""
        return len(self._graph)

    def count_by_type(self, type_uri: str) -> int:
        """특정 rdf:type의 인스턴스 수를 반환한다."""
        rows = self.query(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT (COUNT(?s) AS ?num)
            WHERE {{ ?s rdf:type <{type_uri}> }}
        """)
        return rows[0]["num"] if rows else 0

    def clear(self):
        """모든 트리플을 삭제한다."""
        self._graph = Graph()
        # 네임스페이스 바인딩 복원
        for prefix, ns in list(self._graph.namespaces()):
            self._graph.bind(prefix, ns)
        logger.info("트리플 스토어 초기화됨")

    def save(self, filepath: str, fmt: str = "turtle") -> str:
        """그래프를 파일로 저장한다.

        Args:
            filepath: 출력 파일 경로
            fmt: 직렬화 포맷 ('turtle', 'xml', 'json-ld', 'n3', 'ntriples')

        Returns:
            저장된 파일 경로
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        self._graph.serialize(destination=filepath, format=fmt)
        size_kb = Path(filepath).stat().st_size / 1024
        logger.info("저장 완료: %s (%.1f KB, %s 포맷)", filepath, size_kb, fmt)
        return filepath

    def load(self, filepath: str, fmt: str | None = None) -> int:
        """파일에서 트리플을 로딩한다.

        Args:
            filepath: 입력 파일 경로
            fmt: 파일 포맷 (None이면 확장자에서 자동 감지)

        Returns:
            로딩된 트리플 수
        """
        before = len(self._graph)
        self._graph.parse(filepath, format=fmt)
        loaded = len(self._graph) - before
        logger.info("로딩 완료: %s (%d 트리플)", filepath, loaded)
        return loaded

    def get_subjects_of_type(self, type_uri: str) -> list[str]:
        """특정 타입의 모든 subject URI를 반환한다."""
        rows = self.query(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?s WHERE {{ ?s rdf:type <{type_uri}> }}
        """)
        return [r["s"] for r in rows]

    def describe(self, subject_uri: str) -> list[dict]:
        """특정 subject의 모든 프로퍼티를 반환한다."""
        return self.query(f"""
            SELECT ?p ?o
            WHERE {{ <{subject_uri}> ?p ?o }}
        """)
