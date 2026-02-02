"""Phase 4 벤치마크 스크립트.

StreamingConverter, QueryCache, OWLReasoner의 성능을 측정합니다.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import IFCParser
from src.converter import RDFConverter
from src.converter.streaming_converter import StreamingConverter
from src.cache.query_cache import QueryCache
from src.inference.reasoner import OWLReasoner
from src.storage import TripleStore

IFC4_FILE = "references/nwd4op-12.ifc"
IFC2X3_FILE = "references/nwd23op-12.ifc"


def benchmark_conversion(filepath: str, schema: str):
    """일반 변환 vs 스트리밍 변환 비교."""
    print(f"\n{'='*60}")
    print(f"Benchmark: {Path(filepath).name} ({schema})")
    print(f"{'='*60}")

    parser = IFCParser(filepath)
    t0 = time.time()
    parser.open()
    load_time = time.time() - t0
    print(f"IFC Loading: {load_time:.1f}s ({parser.get_entity_count():,} entities)")

    # 일반 변환
    t0 = time.time()
    converter = RDFConverter(schema=schema)
    graph = converter.convert_file(parser)
    normal_time = time.time() - t0
    normal_triples = len(graph)
    print(f"Normal Converter: {normal_time:.1f}s ({normal_triples:,} triples)")

    # 스트리밍 변환
    output_path = f"/tmp/benchmark_streaming_{schema.lower()}.ttl"
    t0 = time.time()
    streaming = StreamingConverter(schema=schema, batch_size=500)
    streaming.convert(parser, output_path)
    stream_time = time.time() - t0
    stream_stats = streaming.stats
    print(f"Streaming Converter: {stream_time:.1f}s ({stream_stats['triples_generated']:,} triples, {stream_stats['batches']} batches)")

    return {
        "file": Path(filepath).name,
        "schema": schema,
        "load_time": load_time,
        "entities": parser.get_entity_count(),
        "normal_time": normal_time,
        "normal_triples": normal_triples,
        "stream_time": stream_time,
        "stream_triples": stream_stats["triples_generated"],
    }


def benchmark_cache():
    """쿼리 캐시 성능 측정."""
    print(f"\n{'='*60}")
    print("Benchmark: QueryCache")
    print(f"{'='*60}")

    # 스토어 로딩
    parser = IFCParser(IFC4_FILE)
    parser.open()
    converter = RDFConverter(schema="IFC4")
    graph = converter.convert_file(parser)
    store = TripleStore(graph)

    queries = [
        ("Count all", "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX bim: <http://example.org/bim-ontology/schema#>\nSELECT (COUNT(?e) AS ?num) WHERE { ?e rdf:type bim:PhysicalElement }"),
        ("Categories", "PREFIX bim: <http://example.org/bim-ontology/schema#>\nSELECT DISTINCT ?cat WHERE { ?e bim:hasCategory ?cat }"),
        ("Buildings", "PREFIX bim: <http://example.org/bim-ontology/schema#>\nSELECT ?name WHERE { ?b a bim:Building . ?b bim:hasName ?name }"),
        ("Storeys", "PREFIX bim: <http://example.org/bim-ontology/schema#>\nSELECT ?name ?elev WHERE { ?s a bim:BuildingStorey . ?s bim:hasName ?name . OPTIONAL { ?s bim:hasElevation ?elev } }"),
    ]

    cache = QueryCache(max_size=256, ttl=300)

    # Cold run (no cache)
    cold_times = []
    for name, q in queries:
        t0 = time.time()
        result = store.query(q)
        elapsed = time.time() - t0
        cold_times.append(elapsed)
        cache.put(q, result)
        print(f"  Cold '{name}': {elapsed*1000:.1f}ms ({len(result)} rows)")

    # Hot run (cache hit)
    hot_times = []
    for name, q in queries:
        t0 = time.time()
        result = cache.get(q)
        elapsed = time.time() - t0
        hot_times.append(elapsed)
        print(f"  Hot  '{name}': {elapsed*1000:.3f}ms")

    avg_cold = sum(cold_times) / len(cold_times)
    avg_hot = sum(hot_times) / len(hot_times)
    speedup = avg_cold / avg_hot if avg_hot > 0 else float("inf")
    print(f"\n  Average cold: {avg_cold*1000:.1f}ms")
    print(f"  Average hot:  {avg_hot*1000:.3f}ms")
    print(f"  Cache speedup: {speedup:.0f}x")

    return {"avg_cold_ms": avg_cold * 1000, "avg_hot_ms": avg_hot * 1000, "speedup": speedup}


def benchmark_reasoning():
    """OWL 추론 성능 측정."""
    print(f"\n{'='*60}")
    print("Benchmark: OWLReasoner")
    print(f"{'='*60}")

    parser = IFCParser(IFC4_FILE)
    parser.open()
    converter = RDFConverter(schema="IFC4")
    graph = converter.convert_file(parser)

    before = len(graph)
    reasoner = OWLReasoner(graph)

    t0 = time.time()
    result = reasoner.run_all()
    reasoning_time = time.time() - t0

    after = len(graph)
    print(f"  Before: {before:,} triples")
    print(f"  After:  {after:,} triples")
    print(f"  Inferred: {result['total_inferred']:,} triples")
    print(f"  Custom rules: {result['custom_rules_triples']:,}")
    print(f"  RDFS reasoning: {result['rdfs_triples']:,}")
    print(f"  Time: {reasoning_time:.1f}s")
    print(f"  Rules: {', '.join(result['rules_applied'])}")

    return {
        "before": before,
        "after": after,
        "inferred": result["total_inferred"],
        "custom_rules": result["custom_rules_triples"],
        "rdfs_triples": result["rdfs_triples"],
        "time": reasoning_time,
    }


def main():
    print("BIM Ontology - Phase 4 Performance Benchmark")
    print(f"{'='*60}")

    results = {}

    # IFC4 파일 변환 벤치마크
    results["ifc4"] = benchmark_conversion(IFC4_FILE, "IFC4")

    # IFC2X3 파일 변환 벤치마크 (대용량)
    if Path(IFC2X3_FILE).exists():
        results["ifc2x3"] = benchmark_conversion(IFC2X3_FILE, "IFC2X3")
    else:
        print(f"\n[SKIP] {IFC2X3_FILE} not found")

    # 캐시 벤치마크
    results["cache"] = benchmark_cache()

    # 추론 벤치마크
    results["reasoning"] = benchmark_reasoning()

    # 요약
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    if "ifc4" in results:
        r = results["ifc4"]
        print(f"\n[IFC4] {r['file']}")
        print(f"  Entities: {r['entities']:,}")
        print(f"  Normal: {r['normal_time']:.1f}s → {r['normal_triples']:,} triples")
        print(f"  Streaming: {r['stream_time']:.1f}s → {r['stream_triples']:,} triples")

    if "ifc2x3" in results:
        r = results["ifc2x3"]
        print(f"\n[IFC2X3] {r['file']}")
        print(f"  Entities: {r['entities']:,}")
        print(f"  Normal: {r['normal_time']:.1f}s → {r['normal_triples']:,} triples")
        print(f"  Streaming: {r['stream_time']:.1f}s → {r['stream_triples']:,} triples")

    r = results["cache"]
    print(f"\n[Cache]")
    print(f"  Cold avg: {r['avg_cold_ms']:.1f}ms")
    print(f"  Hot avg:  {r['avg_hot_ms']:.3f}ms")
    print(f"  Speedup:  {r['speedup']:.0f}x")

    r = results["reasoning"]
    print(f"\n[Reasoning]")
    print(f"  Inferred: {r['inferred']:,} triples in {r['time']:.1f}s")


if __name__ == "__main__":
    main()
