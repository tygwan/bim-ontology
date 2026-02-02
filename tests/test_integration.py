"""E2E 통합 테스트: IFC → RDF → TripleStore → SPARQL.

실제 IFC 파일을 사용하여 전체 파이프라인을 검증합니다.
"""

import sys
from pathlib import Path

import pytest

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import IFCParser
from src.converter import RDFConverter
from src.converter.namespace_manager import BIM, INST
from src.storage import TripleStore

IFC4_FILE = "references/nwd4op-12.ifc"
IFC2X3_FILE = "references/nwd23op-12.ifc"


@pytest.fixture(scope="module")
def ifc4_parser():
    """IFC4 파일을 로딩한 파서를 반환한다."""
    parser = IFCParser(IFC4_FILE)
    parser.open()
    return parser


@pytest.fixture(scope="module")
def converted_graph(ifc4_parser):
    """IFC4 파일을 RDF로 변환한 그래프를 반환한다."""
    converter = RDFConverter(schema="IFC4")
    return converter.convert_file(ifc4_parser)


@pytest.fixture(scope="module")
def store(converted_graph):
    """변환된 그래프가 로딩된 TripleStore를 반환한다."""
    ts = TripleStore(converted_graph)
    return ts


# ---------- IFC Parser 테스트 ----------

class TestIFCParser:
    def test_open_ifc4(self, ifc4_parser):
        assert ifc4_parser.get_schema() == "IFC4"

    def test_entity_count(self, ifc4_parser):
        assert ifc4_parser.get_entity_count() > 0

    def test_spatial_structure(self, ifc4_parser):
        structure = ifc4_parser.get_spatial_structure()
        assert len(structure["projects"]) >= 1
        assert len(structure["sites"]) >= 1
        assert len(structure["buildings"]) >= 1
        assert len(structure["storeys"]) >= 1

    def test_building_element_proxy(self, ifc4_parser):
        proxies = ifc4_parser.get_entities("IfcBuildingElementProxy")
        assert len(proxies) > 0

    def test_type_counts(self, ifc4_parser):
        counts = ifc4_parser.get_type_counts()
        assert len(counts) > 0
        assert "IfcBuildingElementProxy" in counts

    def test_element_summary(self, ifc4_parser):
        summary = ifc4_parser.get_element_summary()
        assert len(summary) > 0
        # 이름 기반 분류가 동작해야 함
        categories = set(summary.keys())
        assert categories - {"Unknown", "Other"}, "최소 하나의 구체적 카테고리가 있어야 함"

    def test_validate(self, ifc4_parser):
        result = ifc4_parser.validate()
        assert result["valid"]
        assert result["schema"] == "IFC4"
        assert result["entity_count"] > 0

    def test_aggregation_relations(self, ifc4_parser):
        rels = ifc4_parser.get_aggregation_relations()
        assert len(rels) > 0

    def test_file_not_found(self):
        parser = IFCParser("nonexistent.ifc")
        with pytest.raises(FileNotFoundError):
            parser.open()

    def test_ifc_file_not_loaded(self):
        parser = IFCParser(IFC4_FILE)
        with pytest.raises(RuntimeError):
            _ = parser.ifc_file


# ---------- RDF Converter 테스트 ----------

class TestRDFConverter:
    def test_conversion_produces_triples(self, converted_graph):
        assert len(converted_graph) > 1000

    def test_has_spatial_elements(self, store):
        project_count = store.count_by_type(str(BIM.Project))
        assert project_count >= 1

        building_count = store.count_by_type(str(BIM.Building))
        assert building_count >= 1

    def test_has_physical_elements(self, store):
        phys_count = store.count_by_type(str(BIM.PhysicalElement))
        assert phys_count > 0

    def test_has_categories(self, store):
        rows = store.query("""
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            SELECT DISTINCT ?cat WHERE {
                ?e bim:hasCategory ?cat .
            }
        """)
        categories = {r["cat"] for r in rows}
        assert len(categories) > 1

    def test_aggregation_chain(self, store):
        """프로젝트 → 사이트 → 건물 → 층 계층이 존재하는지 확인."""
        rows = store.query("""
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            SELECT ?parent ?child WHERE {
                ?parent bim:aggregates ?child .
            }
        """)
        assert len(rows) >= 3  # project→site, site→building, building→storey

    def test_schema_support(self):
        converter = RDFConverter(schema="IFC2X3")
        assert converter is not None

    def test_invalid_schema(self):
        with pytest.raises(ValueError):
            RDFConverter(schema="IFC9999")

    def test_convert_entity_single(self, ifc4_parser):
        converter = RDFConverter(schema="IFC4")
        projects = ifc4_parser.get_entities("IfcProject")
        triples = converter.convert_entity(projects[0])
        assert len(triples) > 0

    def test_serialize(self, converted_graph, tmp_path):
        converter = RDFConverter(schema="IFC4")
        converter._graph = converted_graph
        out = converter.serialize(str(tmp_path / "test.ttl"))
        assert Path(out).exists()
        assert Path(out).stat().st_size > 0


# ---------- TripleStore 테스트 ----------

class TestTripleStore:
    def test_count(self, store):
        assert store.count() > 1000

    def test_sparql_select(self, store):
        rows = store.query("""
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            SELECT ?name WHERE {
                ?s bim:hasName ?name .
            } LIMIT 5
        """)
        assert len(rows) > 0
        assert "name" in rows[0]

    def test_sparql_count_by_type(self, store):
        count = store.count_by_type(str(BIM.PhysicalElement))
        assert count > 0

    def test_save_and_load(self, store, tmp_path):
        out = str(tmp_path / "test_store.ttl")
        store.save(out)
        assert Path(out).exists()

        new_store = TripleStore()
        loaded = new_store.load(out)
        assert loaded > 0
        assert new_store.count() > 0

    def test_describe(self, store):
        subjects = store.get_subjects_of_type(str(BIM.Building))
        assert len(subjects) > 0

        props = store.describe(subjects[0])
        assert len(props) > 0

    def test_insert_batch(self):
        from rdflib import URIRef, Literal, RDF
        store = TripleStore()
        triples = [
            (URIRef(f"http://test.org/{i}"), RDF.type, URIRef("http://test.org/Thing"))
            for i in range(2500)
        ]
        inserted = store.insert_batch(triples, batch_size=500)
        assert inserted == 2500
        assert store.count() == 2500

    def test_clear(self):
        from rdflib import URIRef, RDF
        store = TripleStore()
        store.insert([(URIRef("http://a"), RDF.type, URIRef("http://b"))])
        assert store.count() == 1
        store.clear()
        assert store.count() == 0


# ---------- E2E 파이프라인 테스트 ----------

class TestEndToEnd:
    def test_full_pipeline(self, ifc4_parser, tmp_path):
        """IFC → RDF → Store → SPARQL → 파일 저장 전체 파이프라인."""
        # 1. 변환
        converter = RDFConverter(schema="IFC4")
        graph = converter.convert_file(ifc4_parser)
        assert len(graph) > 1000

        # 2. 스토어 적재
        store = TripleStore()
        store.insert_graph(graph)
        assert store.count() > 1000

        # 3. SPARQL 쿼리
        rows = store.query("""
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?cat (COUNT(?e) AS ?num)
            WHERE {
                ?e rdf:type bim:PhysicalElement .
                ?e bim:hasCategory ?cat .
            }
            GROUP BY ?cat
            ORDER BY DESC(?num)
        """)
        assert len(rows) > 0

        # 4. 파일 저장
        out = str(tmp_path / "pipeline_output.ttl")
        store.save(out)
        assert Path(out).stat().st_size > 0

        # 5. 재로딩 검증
        new_store = TripleStore()
        new_store.load(out)
        assert abs(new_store.count() - store.count()) < 10  # 약간의 차이 허용

    def test_stats(self, ifc4_parser):
        """변환 통계가 정상적으로 집계되는지 확인."""
        converter = RDFConverter(schema="IFC4")
        converter.convert_file(ifc4_parser)
        stats = converter.stats
        assert stats["entities_converted"] > 0
        assert stats["total_triples"] > 0
        assert stats["convert_time"] > 0
