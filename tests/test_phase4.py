"""Phase 4 테스트: 스트리밍 변환, 쿼리 캐싱, OWL 추론.

StreamingConverter, QueryCache, OWLReasoner 모듈을 검증합니다.
"""

import sys
import time
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef, RDF, RDFS, OWL, XSD

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cache.query_cache import QueryCache
from src.inference.reasoner import OWLReasoner, CUSTOM_RULES
from src.converter.namespace_manager import BIM, INST, bind_namespaces
from src.converter.streaming_converter import StreamingConverter
from src.parser import IFCParser
from src.storage import TripleStore
from conftest import requires_ifc

IFC4_FILE = "references/nwd4op-12.ifc"


# ---------- QueryCache 테스트 ----------

class TestQueryCache:
    def test_put_and_get(self):
        cache = QueryCache(max_size=10, ttl=60)
        cache.put("SELECT ?s WHERE { ?s ?p ?o }", [{"s": "test"}])
        result = cache.get("SELECT ?s WHERE { ?s ?p ?o }")
        assert result == [{"s": "test"}]

    def test_cache_miss(self):
        cache = QueryCache()
        result = cache.get("SELECT ?s WHERE { ?s ?p ?o }")
        assert result is None

    def test_lru_eviction(self):
        cache = QueryCache(max_size=3, ttl=0)
        cache.put("q1", "r1")
        cache.put("q2", "r2")
        cache.put("q3", "r3")
        cache.put("q4", "r4")  # q1 should be evicted
        assert cache.get("q1") is None
        assert cache.get("q4") == "r4"
        assert cache.size == 3

    def test_ttl_expiry(self):
        cache = QueryCache(max_size=10, ttl=1)
        cache.put("query", "result")
        assert cache.get("query") == "result"

        # Manually expire the entry
        key = cache._key("query")
        cache._cache[key] = (time.time() - 2, "result")
        assert cache.get("query") is None

    def test_hit_rate(self):
        cache = QueryCache(max_size=10, ttl=60)
        cache.put("q1", "r1")
        cache.get("q1")  # hit
        cache.get("q1")  # hit
        cache.get("q2")  # miss
        assert cache.hit_rate == pytest.approx(2 / 3, rel=0.01)

    def test_invalidate(self):
        cache = QueryCache(max_size=10, ttl=60)
        cache.put("q1", "r1")
        cache.put("q2", "r2")
        assert cache.size == 2
        cache.invalidate()
        assert cache.size == 0

    def test_stats(self):
        cache = QueryCache(max_size=256, ttl=300)
        cache.put("q1", "r1")
        cache.get("q1")
        cache.get("q2")
        stats = cache.stats
        assert stats["size"] == 1
        assert stats["max_size"] == 256
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_whitespace_normalization(self):
        """같은 쿼리가 공백만 다르면 동일 키로 매핑되는지 확인."""
        cache = QueryCache(max_size=10, ttl=60)
        cache.put("SELECT  ?s  WHERE  { ?s ?p ?o }", "result")
        result = cache.get("SELECT ?s WHERE { ?s ?p ?o }")
        assert result == "result"

    def test_lru_access_reorder(self):
        """접근된 항목이 LRU 순서에서 최근으로 이동하는지 확인."""
        cache = QueryCache(max_size=3, ttl=0)
        cache.put("q1", "r1")
        cache.put("q2", "r2")
        cache.put("q3", "r3")
        # q1에 접근하여 최근으로 이동
        cache.get("q1")
        # q4 삽입 시 가장 오래된 q2가 제거되어야 함
        cache.put("q4", "r4")
        assert cache.get("q1") == "r1"
        assert cache.get("q2") is None


# ---------- OWLReasoner 테스트 ----------

class TestOWLReasoner:
    @pytest.fixture
    def sample_graph(self):
        """추론 테스트용 샘플 그래프를 생성한다."""
        g = Graph()
        bind_namespaces(g, "IFC4")

        # 공간 구조
        building = INST["building_001"]
        storey = INST["storey_001"]
        g.add((building, RDF.type, BIM.Building))
        g.add((building, BIM.aggregates, storey))
        g.add((storey, RDF.type, BIM.BuildingStorey))

        # 물리적 요소 (다양한 카테고리)
        elements = [
            ("beam_001", "Beam"),
            ("column_001", "Column"),
            ("slab_001", "Slab"),
            ("pipe_001", "Pipe"),
            ("duct_001", "Duct"),
            ("stair_001", "Stair"),
            ("wall_001", "Wall"),
        ]
        for eid, category in elements:
            uri = INST[eid]
            g.add((uri, RDF.type, BIM.PhysicalElement))
            g.add((uri, BIM.hasCategory, Literal(category)))
            g.add((storey, BIM.containsElement, uri))

        return g

    def test_add_schema_classes(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        before = len(sample_graph)
        reasoner.add_schema_classes()
        after = len(sample_graph)
        assert after > before

        # StructuralElement, MEPElement, AccessElement 클래스가 존재해야 함
        assert (BIM.StructuralElement, RDF.type, OWL.Class) in sample_graph
        assert (BIM.MEPElement, RDF.type, OWL.Class) in sample_graph
        assert (BIM.AccessElement, RDF.type, OWL.Class) in sample_graph

    def test_infer_structural_element(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        added = reasoner.apply_custom_rules(["infer_structural_element"])
        assert added > 0

        # Beam, Column, Slab, Wall → StructuralElement
        structural = list(sample_graph.subjects(RDF.type, BIM.StructuralElement))
        assert len(structural) >= 4

    def test_infer_mep_element(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        added = reasoner.apply_custom_rules(["infer_mep_element"])
        assert added > 0

        mep = list(sample_graph.subjects(RDF.type, BIM.MEPElement))
        assert len(mep) >= 2  # Pipe, Duct

    def test_infer_access_element(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        added = reasoner.apply_custom_rules(["infer_access_element"])
        assert added > 0

        access = list(sample_graph.subjects(RDF.type, BIM.AccessElement))
        assert len(access) >= 1  # Stair

    def test_infer_storey_has_elements(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        added = reasoner.apply_custom_rules(["infer_storey_has_elements"])
        assert added > 0

        storey = INST["storey_001"]
        has_elements = list(sample_graph.objects(storey, BIM.hasElements))
        assert len(has_elements) >= 1
        assert True in [v.toPython() for v in has_elements if isinstance(v, Literal)]

    def test_infer_element_in_building(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        added = reasoner.apply_custom_rules(["infer_element_in_building"])
        assert added > 0

        # 모든 요소가 isInBuilding 관계를 가져야 함
        in_building = list(sample_graph.subjects(BIM.isInBuilding, None))
        assert len(in_building) >= 7

    def test_unknown_rule(self, sample_graph):
        """알 수 없는 규칙 이름은 무시되어야 한다."""
        reasoner = OWLReasoner(sample_graph)
        added = reasoner.apply_custom_rules(["nonexistent_rule"])
        assert added == 0

    def test_rdfs_reasoning(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        added = reasoner.run_rdfs_reasoning()
        assert added > 0
        assert "RDFS_Semantics" in reasoner.stats["rules_applied"]

    def test_run_all(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        result = reasoner.run_all()
        assert result["total_inferred"] > 0
        assert result["total_triples"] > 0
        assert result["elapsed"] > 0
        assert len(result["rules_applied"]) > 0

    def test_stats(self, sample_graph):
        reasoner = OWLReasoner(sample_graph)
        reasoner.add_schema_classes()
        reasoner.apply_custom_rules()
        stats = reasoner.stats
        assert stats["inferred_triples"] > 0
        assert stats["total_triples"] > 0
        assert len(stats["rules_applied"]) > 0

    def test_custom_rules_registry(self):
        """모든 커스텀 규칙이 등록되어 있는지 확인."""
        expected = [
            "infer_structural_element",
            "infer_mep_element",
            "infer_access_element",
            "infer_storey_has_elements",
            "infer_element_in_building",
        ]
        for rule in expected:
            assert rule in CUSTOM_RULES
            assert "description" in CUSTOM_RULES[rule]
            assert "construct" in CUSTOM_RULES[rule]


# ---------- StreamingConverter 테스트 ----------

@requires_ifc
class TestStreamingConverter:
    @pytest.fixture(scope="class")
    def ifc4_parser(self):
        parser = IFCParser(IFC4_FILE)
        parser.open()
        return parser

    def test_basic_conversion(self, ifc4_parser, tmp_path):
        converter = StreamingConverter(schema="IFC4", batch_size=500)
        output_path = str(tmp_path / "streaming_output.ttl")
        result = converter.convert(ifc4_parser, output_path)
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0

    def test_stats(self, ifc4_parser, tmp_path):
        converter = StreamingConverter(schema="IFC4", batch_size=500)
        output_path = str(tmp_path / "streaming_stats.ttl")
        converter.convert(ifc4_parser, output_path)
        stats = converter.stats
        assert stats["entities_processed"] > 0
        assert stats["triples_generated"] > 0
        assert stats["elapsed"] > 0

    def test_progress_callback(self, ifc4_parser, tmp_path):
        progress_calls = []

        def on_progress(current, total, message):
            progress_calls.append((current, total, message))

        converter = StreamingConverter(schema="IFC4", batch_size=500)
        output_path = str(tmp_path / "streaming_progress.ttl")
        converter.convert(ifc4_parser, output_path, progress_cb=on_progress)
        assert len(progress_calls) > 0

    def test_output_is_valid_rdf(self, ifc4_parser, tmp_path):
        """생성된 파일이 유효한 RDF인지 확인."""
        converter = StreamingConverter(schema="IFC4", batch_size=500)
        output_path = str(tmp_path / "streaming_valid.ttl")
        converter.convert(ifc4_parser, output_path)

        g = Graph()
        g.parse(output_path, format="turtle")
        assert len(g) > 1000

    def test_output_has_spatial_structure(self, ifc4_parser, tmp_path):
        """공간 구조가 포함되어 있는지 확인."""
        converter = StreamingConverter(schema="IFC4", batch_size=500)
        output_path = str(tmp_path / "streaming_spatial.ttl")
        converter.convert(ifc4_parser, output_path)

        store = TripleStore()
        store.load(output_path)
        buildings = store.count_by_type(str(BIM.Building))
        assert buildings >= 1

    def test_ifc2x3_schema(self):
        converter = StreamingConverter(schema="IFC2X3")
        assert converter is not None


# ---------- 통합 테스트: 추론 + 캐시 ----------

@requires_ifc
class TestReasoningIntegration:
    @pytest.fixture(scope="class")
    def converted_store(self):
        """IFC4 파일을 변환하여 스토어에 적재한다."""
        from src.converter import RDFConverter
        parser = IFCParser(IFC4_FILE)
        parser.open()
        converter = RDFConverter(schema="IFC4")
        graph = converter.convert_file(parser)
        return TripleStore(graph)

    def test_reasoning_on_real_data(self, converted_store):
        """실제 변환 데이터에 추론을 적용한다."""
        reasoner = OWLReasoner(converted_store.graph)
        result = reasoner.run_all()
        assert result["total_inferred"] > 0
        assert result["custom_rules_triples"] > 0

    def test_cache_with_store(self, converted_store):
        """캐시와 TripleStore를 함께 사용한다."""
        cache = QueryCache(max_size=50, ttl=60)
        query = """
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT (COUNT(?e) AS ?num)
            WHERE { ?e rdf:type bim:PhysicalElement }
        """
        # First call - miss
        cached = cache.get(query)
        assert cached is None
        result = converted_store.query(query)
        cache.put(query, result)

        # Second call - hit
        cached = cache.get(query)
        assert cached is not None
        assert cached == result
        assert cache.hit_rate == pytest.approx(0.5)

    def test_reasoning_then_query(self, converted_store):
        """추론 후 새로운 타입으로 쿼리가 가능한지 확인."""
        reasoner = OWLReasoner(converted_store.graph)
        reasoner.add_schema_classes()
        reasoner.apply_custom_rules()

        # StructuralElement 타입으로 쿼리
        rows = converted_store.query("""
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT (COUNT(?e) AS ?num)
            WHERE { ?e rdf:type bim:StructuralElement }
        """)
        # Beam, Column, Slab, Wall 등이 StructuralElement로 추론되어야 함
        assert rows[0]["num"] > 0
