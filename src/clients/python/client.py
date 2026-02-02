"""BIM Ontology Python 클라이언트.

API 서버 또는 로컬 TripleStore에 직접 연결하여
BIM 데이터를 쿼리합니다.
"""

import logging
from typing import Any

import httpx

from ...parser import IFCParser
from ...converter import RDFConverter
from ...storage import TripleStore
from ...api.queries.templates import (
    PREFIXES,
    get_all_buildings,
    get_all_elements_by_category,
    get_building_hierarchy,
    get_component_statistics,
    get_element_detail,
    get_entities_by_type,
    get_overall_statistics,
    get_property_sets,
    get_relationships,
    get_spaces_by_storey,
)

logger = logging.getLogger(__name__)


class BIMOntologyClient:
    """BIM Ontology 쿼리 클라이언트.

    로컬 모드(TripleStore 직접 접근) 또는 원격 모드(API 서버 연결)를 지원합니다.

    Usage (로컬 모드):
        client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")
        stats = client.get_statistics()

    Usage (원격 모드):
        client = BIMOntologyClient(api_url="http://localhost:8000")
        stats = client.get_statistics()
    """

    def __init__(
        self,
        store: TripleStore | None = None,
        api_url: str | None = None,
    ):
        self._store = store
        self._api_url = api_url.rstrip("/") if api_url else None

        if store is None and api_url is None:
            raise ValueError("store 또는 api_url 중 하나를 지정해야 합니다.")

    @classmethod
    def from_ifc(cls, ifc_path: str) -> "BIMOntologyClient":
        """IFC 파일에서 직접 클라이언트를 생성한다."""
        parser = IFCParser(ifc_path)
        parser.open()
        converter = RDFConverter(schema=parser.get_schema())
        graph = converter.convert_file(parser)
        store = TripleStore(graph)
        logger.info(
            "로컬 클라이언트 생성: %s (%d 트리플)",
            ifc_path, len(store),
        )
        return cls(store=store)

    @classmethod
    def from_rdf(cls, rdf_path: str) -> "BIMOntologyClient":
        """기존 RDF 파일에서 클라이언트를 생성한다."""
        store = TripleStore()
        store.load(rdf_path)
        return cls(store=store)

    @classmethod
    def from_api(cls, api_url: str) -> "BIMOntologyClient":
        """원격 API 서버에 연결하는 클라이언트를 생성한다."""
        return cls(api_url=api_url)

    @property
    def is_local(self) -> bool:
        return self._store is not None

    # ---------- 쿼리 메서드 ----------

    def query(self, sparql: str) -> list[dict[str, Any]]:
        """임의의 SPARQL 쿼리를 실행한다."""
        if self._store:
            return self._store.query(sparql)
        return self._api_query(sparql)

    def get_buildings(self) -> list[dict]:
        """모든 건물을 조회한다."""
        return self.query(get_all_buildings())

    def get_storeys(self) -> list[dict]:
        """모든 층을 조회한다."""
        q = f"""{PREFIXES}
SELECT ?uri ?name ?globalId ?elevation
WHERE {{
    ?uri rdf:type bim:BuildingStorey .
    OPTIONAL {{ ?uri bim:hasName ?name }}
    OPTIONAL {{ ?uri bim:hasGlobalId ?globalId }}
    OPTIONAL {{ ?uri bim:hasElevation ?elevation }}
}}
"""
        return self.query(q)

    def get_elements(
        self,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """물리적 요소를 조회한다."""
        if category:
            return self.query(get_all_elements_by_category(category, limit, offset))
        q = f"""{PREFIXES}
SELECT ?uri ?name ?category ?globalId
WHERE {{
    ?uri rdf:type bim:PhysicalElement .
    OPTIONAL {{ ?uri bim:hasName ?name }}
    OPTIONAL {{ ?uri bim:hasCategory ?category }}
    OPTIONAL {{ ?uri bim:hasGlobalId ?globalId }}
}}
ORDER BY ?category ?name
LIMIT {limit}
OFFSET {offset}
"""
        return self.query(q)

    def get_element(self, global_id: str) -> list[dict]:
        """특정 요소의 상세 정보를 조회한다."""
        return self.query(get_element_detail(global_id))

    def get_statistics(self) -> dict:
        """카테고리별 통계를 조회한다."""
        rows = self.query(get_component_statistics())
        return {r["category"]: r["num"] for r in rows}

    def get_hierarchy(self) -> list[dict]:
        """건물 계층 구조를 조회한다."""
        return self.query(get_building_hierarchy())

    def get_relationships(self) -> list[dict]:
        """공간-요소 포함 관계를 조회한다."""
        return self.query(get_relationships())

    def get_categories(self) -> list[str]:
        """사용 가능한 카테고리 목록을 반환한다."""
        stats = self.get_statistics()
        return sorted(stats.keys())

    def count_triples(self) -> int:
        """총 트리플 수를 반환한다."""
        if self._store:
            return len(self._store)
        r = self._api_get("/health")
        return r.get("triples", 0)

    # ---------- 내부 메서드 ----------

    def _api_query(self, sparql: str) -> list[dict]:
        """원격 API에 SPARQL 쿼리를 보낸다."""
        r = httpx.post(
            f"{self._api_url}/api/sparql",
            json={"query": sparql},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["results"]

    def _api_get(self, path: str) -> dict:
        """원격 API에 GET 요청을 보낸다."""
        r = httpx.get(f"{self._api_url}{path}", timeout=30)
        r.raise_for_status()
        return r.json()
