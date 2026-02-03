"""GraphDB 외부 트리플 스토어 어댑터.

Ontotext GraphDB에 SPARQLWrapper를 통해 연동합니다.
"""

import logging
import os
from typing import Any

from SPARQLWrapper import SPARQLWrapper, JSON, POST, POSTDIRECTLY

from .base_store import BaseTripleStore

logger = logging.getLogger(__name__)

DEFAULT_GRAPHDB_URL = "http://localhost:7200"
DEFAULT_REPO = "bim-ontology"


class GraphDBStore(BaseTripleStore):
    """GraphDB SPARQLWrapper 기반 외부 트리플 스토어."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        repo: str | None = None,
    ):
        base = endpoint_url or os.getenv("GRAPHDB_URL", DEFAULT_GRAPHDB_URL)
        repo_name = repo or os.getenv("GRAPHDB_REPO", DEFAULT_REPO)
        self._query_url = f"{base}/repositories/{repo_name}"
        self._update_url = f"{base}/repositories/{repo_name}/statements"

        self._sparql = SPARQLWrapper(self._query_url)
        self._sparql.setReturnFormat(JSON)

        self._update = SPARQLWrapper(self._update_url)
        self._update.setMethod(POST)
        self._update.setRequestMethod(POSTDIRECTLY)

        logger.info("GraphDB 연결: %s (repo=%s)", base, repo_name)

    def query(self, sparql: str) -> list[dict[str, Any]]:
        """SPARQL SELECT 쿼리를 실행한다."""
        self._sparql.setQuery(sparql)
        results = self._sparql.query().convert()

        rows = []
        bindings = results.get("results", {}).get("bindings", [])
        for binding in bindings:
            row = {}
            for var, val_info in binding.items():
                val = val_info.get("value", "")
                dtype = val_info.get("datatype", "")
                if dtype and ("integer" in dtype or "int" in dtype):
                    row[var] = int(val)
                elif dtype and ("double" in dtype or "float" in dtype or "decimal" in dtype):
                    row[var] = float(val)
                elif dtype and "boolean" in dtype:
                    row[var] = val.lower() in ("true", "1")
                else:
                    row[var] = val
            rows.append(row)

        return rows

    def insert(self, triples: list[tuple]) -> int:
        """트리플을 SPARQL UPDATE INSERT로 삽입한다."""
        if not triples:
            return 0

        statements = []
        for s, p, o in triples:
            o_str = f'"{o}"' if isinstance(o, str) and not o.startswith("http") else f"<{o}>"
            statements.append(f"<{s}> <{p}> {o_str}")

        update_query = "INSERT DATA { " + " . ".join(statements) + " }"
        self._update.setQuery(update_query)
        self._update.query()
        return len(triples)

    def count(self) -> int:
        """전체 트리플 수를 반환한다."""
        rows = self.query("SELECT (COUNT(*) AS ?num) WHERE { ?s ?p ?o }")
        return rows[0]["num"] if rows else 0

    def load(self, filepath: str) -> int:
        """로컬 파일에서 GraphDB로 데이터를 로딩한다.

        GraphDB의 Import API 또는 SPARQL LOAD를 사용합니다.
        """
        import requests

        before = self.count()
        # GraphDB Importfile API
        base_url = self._query_url.rsplit("/repositories", 1)[0]
        repo_name = self._query_url.rsplit("/", 1)[1]
        import_url = f"{base_url}/rest/repositories/{repo_name}/import/upload/file"

        with open(filepath, "rb") as f:
            resp = requests.post(
                import_url,
                files={"file": (filepath, f, "text/turtle")},
            )

        if resp.status_code not in (200, 201, 202):
            # Fallback: SPARQL LOAD
            load_query = f'LOAD <file://{filepath}>'
            self._update.setQuery(load_query)
            self._update.query()

        after = self.count()
        loaded = after - before
        logger.info("GraphDB 로딩: %s (%d 트리플)", filepath, loaded)
        return loaded

    def save(self, filepath: str) -> str:
        """GraphDB에서 모든 트리플을 파일로 내보낸다."""
        import requests

        resp = requests.get(
            self._query_url,
            headers={"Accept": "text/turtle"},
        )
        resp.raise_for_status()

        with open(filepath, "w") as f:
            f.write(resp.text)

        logger.info("GraphDB 내보내기: %s", filepath)
        return filepath
