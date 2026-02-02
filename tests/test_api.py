"""API 통합 테스트.

FastAPI TestClient로 SPARQL/REST 엔드포인트를 검증합니다.
실제 IFC 데이터를 변환한 TripleStore를 사용합니다.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import IFCParser
from src.converter import RDFConverter
from src.storage import TripleStore
from src.api.server import create_app

IFC4_FILE = "references/nwd4op-12.ifc"


@pytest.fixture(scope="module")
def store():
    """IFC 파일에서 변환한 TripleStore."""
    parser = IFCParser(IFC4_FILE)
    parser.open()
    converter = RDFConverter(schema=parser.get_schema())
    graph = converter.convert_file(parser)
    return TripleStore(graph)


@pytest.fixture(scope="module")
def client(store):
    """TestClient with loaded store."""
    app = create_app(store=store)
    return TestClient(app)


# ---------- Health ----------

class TestHealth:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "BIM Ontology" in r.text

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"
        assert r.json()["triples"] > 0


# ---------- SPARQL ----------

class TestSPARQL:
    def test_sparql_select(self, client):
        r = client.post("/api/sparql", json={
            "query": """
                PREFIX bim: <http://example.org/bim-ontology/schema#>
                SELECT ?name WHERE { ?s bim:hasName ?name } LIMIT 5
            """
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        assert len(data["results"]) > 0

    def test_sparql_count(self, client):
        r = client.post("/api/sparql", json={
            "query": """
                PREFIX bim: <http://example.org/bim-ontology/schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT (COUNT(?e) AS ?num)
                WHERE { ?e rdf:type bim:PhysicalElement }
            """
        })
        assert r.status_code == 200
        assert r.json()["results"][0]["num"] > 0

    def test_sparql_empty_query(self, client):
        r = client.post("/api/sparql", json={"query": ""})
        assert r.status_code == 422  # Validation error

    def test_sparql_invalid_query(self, client):
        r = client.post("/api/sparql", json={"query": "INVALID SPARQL"})
        assert r.status_code == 500


# ---------- Buildings ----------

class TestBuildings:
    def test_list_buildings(self, client):
        r = client.get("/api/buildings")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1

    def test_get_building_by_id(self, client):
        # 먼저 건물 목록 조회
        r = client.get("/api/buildings")
        buildings = r.json()
        assert len(buildings) > 0

        gid = buildings[0]["global_id"]
        r2 = client.get(f"/api/buildings/{gid}")
        assert r2.status_code == 200
        assert r2.json()["global_id"] == gid

    def test_get_building_not_found(self, client):
        r = client.get("/api/buildings/NONEXISTENT_ID")
        assert r.status_code == 404

    def test_list_storeys(self, client):
        r = client.get("/api/storeys")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1

    def test_list_elements_all(self, client):
        r = client.get("/api/elements?limit=10")
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0

    def test_list_elements_by_category(self, client):
        r = client.get("/api/elements?category=Pipe&limit=5")
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0

    def test_list_elements_pagination(self, client):
        r1 = client.get("/api/elements?limit=5&offset=0")
        r2 = client.get("/api/elements?limit=5&offset=5")
        assert r1.status_code == 200
        assert r2.status_code == 200
        # 결과가 다른지 확인 (페이지네이션 동작)
        if len(r1.json()) == 5 and len(r2.json()) > 0:
            assert r1.json()[0]["uri"] != r2.json()[0]["uri"]


# ---------- Statistics ----------

class TestStatistics:
    def test_overall_statistics(self, client):
        r = client.get("/api/statistics")
        assert r.status_code == 200
        data = r.json()
        assert data["total_triples"] > 0
        assert data["total_elements"] > 0
        assert len(data["categories"]) > 0

    def test_category_statistics(self, client):
        r = client.get("/api/statistics/categories")
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        # 각 카테고리에 count가 있는지 확인
        for cat in data:
            assert "category" in cat
            assert "count" in cat
            assert cat["count"] > 0

    def test_hierarchy(self, client):
        r = client.get("/api/hierarchy")
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0


# ---------- Query Templates ----------

class TestQueryTemplates:
    def test_component_statistics_query(self, client):
        from src.api.queries.templates import get_component_statistics
        r = client.post("/api/sparql", json={"query": get_component_statistics()})
        assert r.status_code == 200
        assert r.json()["count"] > 0

    def test_building_hierarchy_query(self, client):
        from src.api.queries.templates import get_building_hierarchy
        r = client.post("/api/sparql", json={"query": get_building_hierarchy()})
        assert r.status_code == 200
        assert r.json()["count"] > 0

    def test_entities_by_type_query(self, client):
        from src.api.queries.templates import get_entities_by_type
        r = client.post("/api/sparql", json={
            "query": get_entities_by_type("IfcBuildingElementProxy", limit=5)
        })
        assert r.status_code == 200
        assert r.json()["count"] > 0

    def test_overall_statistics_query(self, client):
        from src.api.queries.templates import get_overall_statistics
        r = client.post("/api/sparql", json={"query": get_overall_statistics()})
        assert r.status_code == 200
        assert r.json()["count"] > 0


# ---------- Reasoning ----------

class TestReasoning:
    def test_run_reasoning(self, client):
        r = client.post("/api/reasoning")
        assert r.status_code == 200
        data = r.json()
        assert "total_inferred" in data
        assert data["total_inferred"] > 0
        assert "rules_applied" in data
