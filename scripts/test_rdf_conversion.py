"""IFC → RDF 기본 변환 테스트 스크립트.

IFC 데이터를 RDF 트리플로 변환하고 SPARQL 쿼리를 테스트합니다.
ifcOWL 패턴을 참고하여 기본적인 온톨로지 구조를 생성합니다.
"""

import re
import time
from pathlib import Path
from collections import Counter

import ifcopenshell
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, XSD, URIRef, BNode


# 네임스페이스 정의
IFC = Namespace("http://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#")
INST = Namespace("http://example.org/bim-ontology/instance#")
BIM = Namespace("http://example.org/bim-ontology/schema#")
EXPRESS = Namespace("http://purl.org/voc/express#")


def classify_by_name(name: str) -> str:
    """요소 이름을 기반으로 BIM 카테고리를 추정한다.

    Navisworks 내보내기로 타입 정보가 손실된 경우
    이름 패턴으로 원래 타입을 추정합니다.
    """
    if not name:
        return "Unknown"

    name_lower = name.lower()
    patterns = {
        "Slab": [r"slab", r"floor"],
        "Wall": [r"wall", r"partition"],
        "Column": [r"column", r"pillar"],
        "Beam": [r"beam", r"girder", r"joist"],
        "Pipe": [r"pipe", r"piping"],
        "Duct": [r"duct"],
        "CableTray": [r"cable\s*tray", r"cable"],
        "Insulation": [r"insulation"],
        "Valve": [r"valve"],
        "Pump": [r"pump"],
        "Equipment": [r"equipment", r"tank", r"vessel"],
        "Foundation": [r"foundation", r"footing"],
        "Railing": [r"railing", r"handrail"],
        "Stair": [r"stair"],
        "MemberPart": [r"memberpart"],
        "Structural": [r"structural"],
        "Aspect": [r"aspect"],
        "Geometry": [r"geometry"],
    }

    for category, regexes in patterns.items():
        for regex in regexes:
            if re.search(regex, name_lower):
                return category
    return "Other"


def ifc_to_rdf(ifc_path: str, output_path: str = None) -> Graph:
    """IFC 파일을 RDF 그래프로 변환한다."""
    path = Path(ifc_path)
    print(f"\n{'='*60}")
    print(f"RDF 변환: {path.name}")
    print(f"{'='*60}")

    start = time.time()
    ifc_file = ifcopenshell.open(str(path))
    print(f"IFC 로딩: {time.time() - start:.1f}초")

    g = Graph()
    g.bind("ifc", IFC)
    g.bind("inst", INST)
    g.bind("bim", BIM)
    g.bind("express", EXPRESS)
    g.bind("owl", OWL)

    # --- 온톨로지 스키마 정의 ---
    # BIM 클래스 계층
    g.add((BIM.BIMElement, RDF.type, OWL.Class))
    g.add((BIM.BIMElement, RDFS.label, Literal("BIM Element")))

    g.add((BIM.SpatialElement, RDF.type, OWL.Class))
    g.add((BIM.SpatialElement, RDFS.subClassOf, BIM.BIMElement))

    g.add((BIM.PhysicalElement, RDF.type, OWL.Class))
    g.add((BIM.PhysicalElement, RDFS.subClassOf, BIM.BIMElement))

    # 공간 구조 클래스
    for cls_name in ["Project", "Site", "Building", "BuildingStorey", "Space"]:
        cls = BIM[cls_name]
        g.add((cls, RDF.type, OWL.Class))
        g.add((cls, RDFS.subClassOf, BIM.SpatialElement))

    # 물리적 요소 카테고리 클래스
    categories = set()

    # 속성 정의
    g.add((BIM.hasName, RDF.type, OWL.DatatypeProperty))
    g.add((BIM.hasName, RDFS.domain, BIM.BIMElement))
    g.add((BIM.hasName, RDFS.range, XSD.string))

    g.add((BIM.hasGlobalId, RDF.type, OWL.DatatypeProperty))
    g.add((BIM.hasGlobalId, RDFS.domain, BIM.BIMElement))
    g.add((BIM.hasGlobalId, RDFS.range, XSD.string))

    g.add((BIM.hasCategory, RDF.type, OWL.DatatypeProperty))
    g.add((BIM.hasCategory, RDFS.domain, BIM.PhysicalElement))
    g.add((BIM.hasCategory, RDFS.range, XSD.string))

    g.add((BIM.hasOriginalType, RDF.type, OWL.DatatypeProperty))
    g.add((BIM.hasOriginalType, RDFS.domain, BIM.BIMElement))
    g.add((BIM.hasOriginalType, RDFS.range, XSD.string))

    # 관계 속성
    g.add((BIM.containsElement, RDF.type, OWL.ObjectProperty))
    g.add((BIM.containsElement, RDFS.domain, BIM.SpatialElement))
    g.add((BIM.containsElement, RDFS.range, BIM.BIMElement))

    g.add((BIM.isContainedIn, RDF.type, OWL.ObjectProperty))
    g.add((BIM.isContainedIn, OWL.inverseOf, BIM.containsElement))

    g.add((BIM.aggregates, RDF.type, OWL.ObjectProperty))
    g.add((BIM.decomposes, RDF.type, OWL.ObjectProperty))
    g.add((BIM.decomposes, OWL.inverseOf, BIM.aggregates))

    convert_start = time.time()

    # --- 공간 구조 변환 ---
    # IfcProject
    for project in ifc_file.by_type('IfcProject'):
        uri = INST[f"project_{project.GlobalId}"]
        g.add((uri, RDF.type, BIM.Project))
        g.add((uri, RDF.type, IFC.IfcProject))
        g.add((uri, BIM.hasGlobalId, Literal(project.GlobalId)))
        if project.Name:
            g.add((uri, BIM.hasName, Literal(project.Name)))
            g.add((uri, RDFS.label, Literal(project.Name)))

    # IfcSite
    for site in ifc_file.by_type('IfcSite'):
        uri = INST[f"site_{site.GlobalId}"]
        g.add((uri, RDF.type, BIM.Site))
        g.add((uri, RDF.type, IFC.IfcSite))
        g.add((uri, BIM.hasGlobalId, Literal(site.GlobalId)))
        if site.Name:
            g.add((uri, BIM.hasName, Literal(site.Name)))
            g.add((uri, RDFS.label, Literal(site.Name)))

    # IfcBuilding
    for building in ifc_file.by_type('IfcBuilding'):
        uri = INST[f"building_{building.GlobalId}"]
        g.add((uri, RDF.type, BIM.Building))
        g.add((uri, RDF.type, IFC.IfcBuilding))
        g.add((uri, BIM.hasGlobalId, Literal(building.GlobalId)))
        if building.Name:
            g.add((uri, BIM.hasName, Literal(building.Name)))
            g.add((uri, RDFS.label, Literal(building.Name)))

    # IfcBuildingStorey
    for storey in ifc_file.by_type('IfcBuildingStorey'):
        uri = INST[f"storey_{storey.GlobalId}"]
        g.add((uri, RDF.type, BIM.BuildingStorey))
        g.add((uri, RDF.type, IFC.IfcBuildingStorey))
        g.add((uri, BIM.hasGlobalId, Literal(storey.GlobalId)))
        if storey.Name:
            g.add((uri, BIM.hasName, Literal(storey.Name)))
            g.add((uri, RDFS.label, Literal(storey.Name)))
        if storey.Elevation is not None:
            g.add((uri, BIM["hasElevation"],
                   Literal(storey.Elevation, datatype=XSD.double)))

    # --- 공간 관계 (IfcRelAggregates) 변환 ---
    for rel in ifc_file.by_type('IfcRelAggregates'):
        relating = rel.RelatingObject
        relating_uri = _get_uri(relating)
        for related in rel.RelatedObjects:
            related_uri = _get_uri(related)
            g.add((relating_uri, BIM.aggregates, related_uri))
            g.add((related_uri, BIM.decomposes, relating_uri))

    # --- 물리적 요소 변환 (IfcBuildingElementProxy) ---
    proxies = ifc_file.by_type('IfcBuildingElementProxy')
    category_counter = Counter()

    for proxy in proxies:
        uri = INST[f"element_{proxy.GlobalId}"]
        category = classify_by_name(proxy.Name)
        category_counter[category] += 1
        categories.add(category)

        # 카테고리별 클래스 생성 및 인스턴스 추가
        cat_class = BIM[category]
        g.add((uri, RDF.type, cat_class))
        g.add((uri, RDF.type, BIM.PhysicalElement))
        g.add((uri, RDF.type, IFC.IfcBuildingElementProxy))
        g.add((uri, BIM.hasGlobalId, Literal(proxy.GlobalId)))
        g.add((uri, BIM.hasCategory, Literal(category)))
        g.add((uri, BIM.hasOriginalType, Literal("IfcBuildingElementProxy")))

        if proxy.Name:
            g.add((uri, BIM.hasName, Literal(proxy.Name)))
            g.add((uri, RDFS.label, Literal(proxy.Name)))

    # 동적 카테고리 클래스를 스키마에 추가
    for cat in categories:
        cat_class = BIM[cat]
        g.add((cat_class, RDF.type, OWL.Class))
        g.add((cat_class, RDFS.subClassOf, BIM.PhysicalElement))
        g.add((cat_class, RDFS.label, Literal(cat)))

    # --- 공간 포함 관계 (IfcRelContainedInSpatialStructure) ---
    for rel in ifc_file.by_type('IfcRelContainedInSpatialStructure'):
        structure = rel.RelatingStructure
        structure_uri = _get_uri(structure)
        for element in rel.RelatedElements:
            element_uri = _get_uri(element)
            g.add((structure_uri, BIM.containsElement, element_uri))
            g.add((element_uri, BIM.isContainedIn, structure_uri))

    convert_time = time.time() - convert_start

    # --- 통계 출력 ---
    print(f"\n변환 시간: {convert_time:.1f}초")
    print(f"총 트리플 수: {len(g):,}")
    print(f"\n--- 카테고리별 요소 수 ---")
    for cat, count in category_counter.most_common():
        print(f"  {cat:<30} {count:>6}")

    # RDF 파일 저장
    if output_path is None:
        output_path = f"/home/coffin/dev/bim-ontology/data/rdf/{path.stem}.ttl"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    save_start = time.time()
    g.serialize(destination=output_path, format="turtle")
    save_time = time.time() - save_start
    file_size = Path(output_path).stat().st_size / 1024
    print(f"\n저장 완료: {output_path}")
    print(f"파일 크기: {file_size:.1f} KB")
    print(f"저장 시간: {save_time:.1f}초")

    return g


def _get_uri(element) -> URIRef:
    """IFC 요소의 URI를 반환한다."""
    type_name = element.is_a().lower()
    return INST[f"{type_name}_{element.GlobalId}"]


def run_sparql_tests(g: Graph):
    """SPARQL 쿼리 테스트를 수행한다."""
    print(f"\n{'='*60}")
    print("SPARQL 쿼리 테스트")
    print(f"{'='*60}")

    # 쿼리 1: 전체 클래스 및 인스턴스 수
    q1 = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?cls (COUNT(?inst) AS ?num)
    WHERE {
        ?cls rdf:type owl:Class .
        ?inst rdf:type ?cls .
        FILTER(?cls != owl:Class)
    }
    GROUP BY ?cls
    ORDER BY DESC(?num)
    """
    print("\n[Q1] 클래스별 인스턴스 수:")
    for row in g.query(q1):
        cls_name = str(row.cls).split("#")[-1]
        print(f"  {cls_name:<40} {int(row.num):>6}")

    # 쿼리 2: 공간 구조 계층
    q2 = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?parent ?parentLabel ?child ?childLabel
    WHERE {
        ?parent bim:aggregates ?child .
        OPTIONAL { ?parent rdfs:label ?parentLabel }
        OPTIONAL { ?child rdfs:label ?childLabel }
    }
    """
    print("\n[Q2] 공간 구조 계층:")
    for row in g.query(q2):
        parent = str(row.parent).split("#")[-1]
        child = str(row.child).split("#")[-1]
        p_label = row.parentLabel or ""
        c_label = row.childLabel or ""
        print(f"  {parent} ({p_label}) → {child} ({c_label})")

    # 쿼리 3: 카테고리별 요소 수
    q3 = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?category (COUNT(?elem) AS ?num)
    WHERE {
        ?elem rdf:type bim:PhysicalElement .
        ?elem bim:hasCategory ?category .
    }
    GROUP BY ?category
    ORDER BY DESC(?num)
    """
    print("\n[Q3] 카테고리별 물리적 요소 수:")
    for row in g.query(q3):
        print(f"  {str(row.category):<30} {int(row.num):>6}")

    # 쿼리 4: 특정 층에 포함된 요소
    q4 = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?storey ?storeyName (COUNT(?elem) AS ?elementCount)
    WHERE {
        ?storey rdf:type bim:BuildingStorey .
        ?storey bim:containsElement ?elem .
        OPTIONAL { ?storey rdfs:label ?storeyName }
    }
    GROUP BY ?storey ?storeyName
    """
    print("\n[Q4] 층별 포함 요소 수:")
    for row in g.query(q4):
        name = row.storeyName or "(이름 없음)"
        print(f"  {name}: {int(row.elementCount):,}개 요소")

    # 쿼리 5: Pipe 카테고리 요소 이름 샘플
    q5 = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?name
    WHERE {
        ?elem bim:hasCategory "Pipe" .
        ?elem bim:hasName ?name .
    }
    LIMIT 10
    """
    print("\n[Q5] Pipe 카테고리 요소 이름 (최대 10개):")
    results = list(g.query(q5))
    if results:
        for row in results:
            print(f"  {row.name}")
    else:
        print("  (결과 없음)")

    # 쿼리 6: 이름에 'Slab' 포함하는 요소 검색
    q6 = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>

    SELECT ?name ?category
    WHERE {
        ?elem bim:hasName ?name .
        ?elem bim:hasCategory ?category .
        FILTER(CONTAINS(LCASE(?name), "slab"))
    }
    LIMIT 10
    """
    print("\n[Q6] 이름에 'Slab' 포함 요소 (최대 10개):")
    for row in g.query(q6):
        print(f"  {row.name} [카테고리: {row.category}]")


if __name__ == "__main__":
    # IFC4 파일로 테스트 (작은 파일)
    g = ifc_to_rdf("/home/coffin/dev/bim-ontology/references/nwd4op-12.ifc")
    run_sparql_tests(g)
