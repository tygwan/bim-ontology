"""Python 클라이언트 테스트."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import IFCParser
from src.converter import RDFConverter
from src.storage import TripleStore
from src.clients.python import BIMOntologyClient

requires_ifc = pytest.mark.skipif(
    not Path("references/nwd4op-12.ifc").exists(),
    reason="IFC test data not available",
)

IFC4_FILE = "references/nwd4op-12.ifc"


@pytest.fixture(scope="module")
def client():
    """로컬 모드 클라이언트."""
    parser = IFCParser(IFC4_FILE)
    parser.open()
    converter = RDFConverter(schema=parser.get_schema())
    graph = converter.convert_file(parser)
    store = TripleStore(graph)
    return BIMOntologyClient(store=store)


@requires_ifc
class TestClientInit:
    def test_from_ifc(self):
        c = BIMOntologyClient.from_ifc(IFC4_FILE)
        assert c.is_local
        assert c.count_triples() > 0

    def test_requires_store_or_url(self):
        with pytest.raises(ValueError):
            BIMOntologyClient()

    def test_from_api_creates_remote(self):
        c = BIMOntologyClient.from_api("http://localhost:8000")
        assert not c.is_local


@requires_ifc
class TestClientQueries:
    def test_get_buildings(self, client):
        buildings = client.get_buildings()
        assert len(buildings) >= 1

    def test_get_storeys(self, client):
        storeys = client.get_storeys()
        assert len(storeys) >= 1

    def test_get_elements_all(self, client):
        elements = client.get_elements(limit=10)
        assert len(elements) > 0

    def test_get_elements_by_category(self, client):
        elements = client.get_elements(category="Pipe", limit=5)
        assert len(elements) > 0

    def test_get_statistics(self, client):
        stats = client.get_statistics()
        assert isinstance(stats, dict)
        assert len(stats) > 0
        assert all(isinstance(v, int) for v in stats.values())

    def test_get_categories(self, client):
        cats = client.get_categories()
        assert len(cats) > 0
        assert "Pipe" in cats or "Beam" in cats

    def test_get_hierarchy(self, client):
        hierarchy = client.get_hierarchy()
        assert len(hierarchy) > 0

    def test_count_triples(self, client):
        count = client.count_triples()
        assert count > 1000

    def test_custom_query(self, client):
        results = client.query("""
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            SELECT ?name WHERE { ?s bim:hasName ?name } LIMIT 3
        """)
        assert len(results) == 3

    def test_get_element_detail(self, client):
        # 먼저 요소 하나 조회
        elements = client.get_elements(limit=1)
        assert len(elements) > 0
        gid = elements[0].get("globalId")
        if gid:
            detail = client.get_element(gid)
            assert len(detail) > 0
