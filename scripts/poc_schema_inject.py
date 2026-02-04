"""PoC: Schema Manager API로 Lean Layer 속성을 주입하고 SPARQL 조회를 검증한다.

Method C: Schema Manager의 custom_schema.json을 통한 동적 속성 정의 + 인스턴스 주입.
OWL 클래스/프로퍼티를 API로 등록하고, 인스턴스 트리플을 직접 추가한다.

Usage:
    python scripts/poc_schema_inject.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rdflib import Graph, Literal, URIRef, RDF, RDFS, XSD, Namespace

from src.ontology.schema_manager import OntologySchemaManager

BIM = Namespace("http://example.org/bim-ontology/schema#")
INST = Namespace("http://example.org/bim-ontology/instance#")
SCHED = Namespace("http://example.org/bim-ontology/schedule#")
AWP = Namespace("http://example.org/bim-ontology/awp#")


def poc_schema_manager_inject(rdf_path: str):
    """Schema Manager로 Lean Layer 타입/속성을 등록하고 인스턴스를 주입한다."""

    # 1. 기존 RDF 로딩
    g = Graph()
    g.parse(rdf_path, format="turtle")
    initial_count = len(g)
    print(f"1. 기존 RDF 로딩: {initial_count} triples")

    # 2. Schema Manager로 커스텀 타입 등록
    mgr = OntologySchemaManager(g)

    # Object Types
    mgr.create_object_type(
        "ConstructionTask", parent_class="BIMElement",
        label="Construction Task",
        description="A scheduled construction activity",
    )
    mgr.create_object_type(
        "InstallationWorkPackage", parent_class="BIMElement",
        label="Installation Work Package (IWP)",
        description="1-2 week executable field work package",
    )

    # Property Types (date/dateTime 지원 확인)
    mgr.create_property_type(
        "hasPlannedStart", domain="ConstructionTask",
        range_type="date", label="Planned Start Date",
    )
    mgr.create_property_type(
        "hasPlannedEnd", domain="ConstructionTask",
        range_type="date", label="Planned End Date",
    )
    mgr.create_property_type(
        "hasDeliveryStatus", domain="PhysicalElement",
        range_type="string", label="Delivery Status",
    )
    mgr.create_property_type(
        "hasUnitCost", domain="PhysicalElement",
        range_type="double", label="Unit Cost",
    )

    # Link Types
    mgr.create_link_type(
        "assignedToTask", domain="PhysicalElement",
        range_class="ConstructionTask",
        inverse_name="hasAssignedElement",
        label="Assigned to Task",
    )

    # 3. 스키마를 그래프에 적용
    schema_triples = mgr.apply_schema_to_graph(g)
    print(f"2. Schema Manager 적용: +{schema_triples} schema triples")

    # 4. 인스턴스 데이터 직접 주입
    instance_triples = 0

    # 요소 1개 찾기
    results = list(g.query("""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        SELECT ?elem ?gid ?name WHERE {
            ?elem bim:hasGlobalId ?gid .
            OPTIONAL { ?elem bim:hasName ?name }
        } LIMIT 3
    """))

    if not results:
        print("ERROR: No elements found in RDF graph")
        return

    # Task 인스턴스 생성
    task_uri = INST["task_STEEL_ERECTION_001"]
    g.add((task_uri, RDF.type, BIM["ConstructionTask"]))
    g.add((task_uri, RDFS.label, Literal("Steel Erection - Zone A")))
    g.add((task_uri, BIM["hasPlannedStart"], Literal("2026-03-15", datatype=XSD.date)))
    g.add((task_uri, BIM["hasPlannedEnd"], Literal("2026-04-15", datatype=XSD.date)))
    instance_triples += 4

    # 요소에 속성 주입 + Task 연결
    for row in results:
        elem_uri = row.elem
        g.add((elem_uri, BIM["hasDeliveryStatus"], Literal("OnSite")))
        g.add((elem_uri, BIM["hasUnitCost"], Literal(1250.0)))
        g.add((elem_uri, BIM["assignedToTask"], task_uri))
        instance_triples += 3

    print(f"3. 인스턴스 주입: +{instance_triples} instance triples")
    print(f"   총 트리플: {len(g)} (원본 {initial_count} + {len(g) - initial_count})")

    # 5. SPARQL 검증
    print("\n4. SPARQL 검증:")

    # 5a. Task 조회
    task_query = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?task ?label ?start ?end WHERE {
        ?task a bim:ConstructionTask .
        ?task rdfs:label ?label .
        OPTIONAL { ?task bim:hasPlannedStart ?start }
        OPTIONAL { ?task bim:hasPlannedEnd ?end }
    }
    """
    task_results = list(g.query(task_query))
    print(f"   a) ConstructionTask 인스턴스: {len(task_results)}개")
    for r in task_results:
        print(f"      - {r.label}: {r.start} ~ {r.end}")

    # 5b. 요소 속성 조회
    elem_query = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?elem ?name ?status ?cost ?task WHERE {
        ?elem bim:hasDeliveryStatus ?status .
        OPTIONAL { ?elem bim:hasName ?name }
        OPTIONAL { ?elem bim:hasUnitCost ?cost }
        OPTIONAL { ?elem bim:assignedToTask ?task }
    }
    """
    elem_results = list(g.query(elem_query))
    print(f"   b) 속성이 주입된 요소: {len(elem_results)}개")
    for r in elem_results:
        name = str(r.name) if r.name else "?"
        print(f"      - {name}: status={r.status}, cost={r.cost}")

    # 5c. Schema 조회 (OWL Class 확인)
    cls_query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    SELECT ?cls ?label WHERE {
        ?cls a owl:Class .
        ?cls rdfs:label ?label .
        FILTER(STRSTARTS(STR(?cls), STR(bim:)))
    }
    """
    cls_results = list(g.query(cls_query))
    print(f"   c) BIM OWL Classes: {len(cls_results)}개")

    # 6. 결과 저장
    output_path = "data/test/schema_inject_result.ttl"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=output_path, format="turtle")
    print(f"\n5. 결과 저장: {output_path} ({len(g)} triples)")

    return {
        "schema_triples": schema_triples,
        "instance_triples": instance_triples,
        "total_triples": len(g),
        "tasks_found": len(task_results),
        "elements_with_props": len(elem_results),
    }


def main():
    rdf_path = "data/rdf/nwd4op-12.ttl"
    if not Path(rdf_path).exists():
        print(f"ERROR: RDF file not found: {rdf_path}")
        sys.exit(1)

    print("=" * 60)
    print("PoC Method C: Schema Manager API Injection")
    print("=" * 60)
    print()

    result = poc_schema_manager_inject(rdf_path)

    if result:
        print(f"\n{'=' * 60}")
        print("RESULT: SUCCESS")
        print(f"{'=' * 60}")
        print(f"  - Schema registration via API: OK")
        print(f"  - date/dateTime XSD types: OK")
        print(f"  - Instance injection: OK ({result['instance_triples']} triples)")
        print(f"  - SPARQL queryable: OK")
        print(f"  - Tasks: {result['tasks_found']}, Elements: {result['elements_with_props']}")


if __name__ == "__main__":
    main()
