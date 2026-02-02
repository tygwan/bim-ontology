"""SPARQL 쿼리 템플릿.

실제 데이터 특성에 맞춘 10개 표준 쿼리.
Navisworks 내보내기 데이터는 IfcBuildingElementProxy가 주요 엔티티이며,
이름 기반 분류(bim:hasCategory)로 카테고리를 구분합니다.
"""

PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX inst: <http://example.org/bim-ontology/instance#>
"""


def get_all_elements_by_category(category: str, limit: int = 100, offset: int = 0) -> str:
    """특정 카테고리의 모든 요소를 조회한다."""
    return f"""{PREFIXES}
SELECT ?uri ?name ?globalId
WHERE {{
    ?uri bim:hasCategory "{category}" .
    OPTIONAL {{ ?uri bim:hasName ?name }}
    OPTIONAL {{ ?uri bim:hasGlobalId ?globalId }}
}}
ORDER BY ?name
LIMIT {limit}
OFFSET {offset}
"""


def get_spaces_by_storey(storey_name: str | None = None) -> str:
    """층별 포함 요소를 조회한다."""
    filter_clause = ""
    if storey_name:
        filter_clause = f'FILTER(CONTAINS(LCASE(?storeyName), "{storey_name.lower()}"))'
    return f"""{PREFIXES}
SELECT ?storey ?storeyName ?element ?elementName ?category
WHERE {{
    ?storey rdf:type bim:BuildingStorey .
    ?storey bim:containsElement ?element .
    OPTIONAL {{ ?storey bim:hasName ?storeyName }}
    OPTIONAL {{ ?element bim:hasName ?elementName }}
    OPTIONAL {{ ?element bim:hasCategory ?category }}
    {filter_clause}
}}
ORDER BY ?storeyName ?category ?elementName
"""


def get_component_statistics() -> str:
    """카테고리별 구성요소 통계를 조회한다."""
    return f"""{PREFIXES}
SELECT ?category (COUNT(?elem) AS ?num)
WHERE {{
    ?elem rdf:type bim:PhysicalElement .
    ?elem bim:hasCategory ?category .
}}
GROUP BY ?category
ORDER BY DESC(?num)
"""


def get_property_sets(element_uri: str | None = None) -> str:
    """속성셋 정보를 조회한다."""
    filter_clause = ""
    if element_uri:
        filter_clause = f"FILTER(?element = <{element_uri}>)"
    return f"""{PREFIXES}
SELECT ?element ?elementName ?psetName ?propName ?propValue
WHERE {{
    ?element bim:hasPropertySet ?pset .
    ?pset bim:hasName ?psetName .
    ?pset bim:hasProperty ?prop .
    ?prop bim:hasName ?propName .
    OPTIONAL {{ ?prop bim:hasPropertyValue ?propValue }}
    OPTIONAL {{ ?element bim:hasName ?elementName }}
    {filter_clause}
}}
ORDER BY ?elementName ?psetName ?propName
LIMIT 500
"""


def get_building_hierarchy() -> str:
    """프로젝트 → 사이트 → 건물 → 층 계층 구조를 조회한다."""
    return f"""{PREFIXES}
SELECT ?parent ?parentName ?parentType ?child ?childName ?childType
WHERE {{
    ?parent bim:aggregates ?child .
    OPTIONAL {{ ?parent bim:hasName ?parentName }}
    OPTIONAL {{ ?child bim:hasName ?childName }}
    ?parent rdf:type ?parentType .
    ?child rdf:type ?childType .
    FILTER(?parentType IN (bim:Project, bim:Site, bim:Building, bim:BuildingStorey))
    FILTER(?childType IN (bim:Site, bim:Building, bim:BuildingStorey, bim:Space))
}}
ORDER BY ?parentType ?childType
"""


def get_entities_by_type(ifc_type: str, limit: int = 100) -> str:
    """특정 IFC 원본 타입의 엔티티를 조회한다."""
    return f"""{PREFIXES}
SELECT ?uri ?name ?category ?globalId
WHERE {{
    ?uri bim:hasOriginalType "{ifc_type}" .
    OPTIONAL {{ ?uri bim:hasName ?name }}
    OPTIONAL {{ ?uri bim:hasCategory ?category }}
    OPTIONAL {{ ?uri bim:hasGlobalId ?globalId }}
}}
ORDER BY ?category ?name
LIMIT {limit}
"""


def get_relationships() -> str:
    """모든 공간-요소 포함 관계를 조회한다."""
    return f"""{PREFIXES}
SELECT ?structure ?structureName ?structureType ?element ?elementName ?elementCategory
WHERE {{
    ?structure bim:containsElement ?element .
    OPTIONAL {{ ?structure bim:hasName ?structureName }}
    OPTIONAL {{ ?element bim:hasName ?elementName }}
    OPTIONAL {{ ?element bim:hasCategory ?elementCategory }}
    ?structure rdf:type ?structureType .
    FILTER(?structureType IN (bim:Building, bim:BuildingStorey, bim:Space))
}}
ORDER BY ?structureType ?elementCategory
LIMIT 500
"""


def get_element_detail(global_id: str) -> str:
    """특정 요소의 상세 정보를 조회한다."""
    return f"""{PREFIXES}
SELECT ?predicate ?object
WHERE {{
    ?s bim:hasGlobalId "{global_id}" .
    ?s ?predicate ?object .
}}
"""


def get_all_buildings() -> str:
    """모든 건물 정보를 조회한다."""
    return f"""{PREFIXES}
SELECT ?uri ?name ?globalId
WHERE {{
    ?uri rdf:type bim:Building .
    OPTIONAL {{ ?uri bim:hasName ?name }}
    OPTIONAL {{ ?uri bim:hasGlobalId ?globalId }}
}}
"""


def get_overall_statistics() -> str:
    """전체 온톨로지 통계를 조회한다."""
    return f"""{PREFIXES}
SELECT
    (COUNT(DISTINCT ?elem) AS ?totalElements)
    (COUNT(DISTINCT ?cat) AS ?totalCategories)
    (COUNT(DISTINCT ?building) AS ?buildings)
    (COUNT(DISTINCT ?storey) AS ?storeys)
WHERE {{
    OPTIONAL {{
        ?elem rdf:type bim:PhysicalElement .
        ?elem bim:hasCategory ?cat .
    }}
    OPTIONAL {{ ?building rdf:type bim:Building }}
    OPTIONAL {{ ?storey rdf:type bim:BuildingStorey }}
}}
"""


# 쿼리 템플릿 레지스트리
QUERY_TEMPLATES = {
    "get_all_elements_by_category": get_all_elements_by_category,
    "get_spaces_by_storey": get_spaces_by_storey,
    "get_component_statistics": get_component_statistics,
    "get_property_sets": get_property_sets,
    "get_building_hierarchy": get_building_hierarchy,
    "get_entities_by_type": get_entities_by_type,
    "get_relationships": get_relationships,
    "get_element_detail": get_element_detail,
    "get_all_buildings": get_all_buildings,
    "get_overall_statistics": get_overall_statistics,
}
