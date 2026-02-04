"""RDF 데이터 감사용 SPARQL 쿼리 템플릿.

현재 RDF 그래프에 존재하는 모든 데이터 유형과 통계를 조사한다.
"""

PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX inst: <http://example.org/bim-ontology/instance#>
"""


def audit_data_summary() -> str:
    """전체 데이터 요약: 요소 수, 카테고리 수, 층 수, PropertySet 여부."""
    return f"""{PREFIXES}
SELECT
    (COUNT(DISTINCT ?elem) AS ?totalElements)
    (COUNT(DISTINCT ?cat) AS ?totalCategories)
    (COUNT(DISTINCT ?storey) AS ?totalStoreys)
    (COUNT(DISTINCT ?pset) AS ?totalPropertySets)
    (COUNT(DISTINCT ?mat) AS ?totalMaterials)
    (COUNT(DISTINCT ?qty) AS ?totalQuantities)
WHERE {{
    OPTIONAL {{
        ?elem rdf:type bim:PhysicalElement .
        OPTIONAL {{ ?elem bim:hasCategory ?cat }}
    }}
    OPTIONAL {{ ?storey rdf:type bim:BuildingStorey }}
    OPTIONAL {{ ?pset rdf:type bim:PropertySet }}
    OPTIONAL {{ ?mat rdf:type bim:Material }}
    OPTIONAL {{ ?qty bim:hasArea ?qtyVal }}
}}
"""


def audit_category_stats() -> str:
    """카테고리별 요소 수 + PropertySet 보유 현황."""
    return f"""{PREFIXES}
SELECT ?category
    (COUNT(DISTINCT ?elem) AS ?elementCount)
    (COUNT(DISTINCT ?pset) AS ?withPropertySet)
    (COUNT(DISTINCT ?mat) AS ?withMaterial)
WHERE {{
    ?elem rdf:type bim:PhysicalElement ;
          bim:hasCategory ?category .
    OPTIONAL {{ ?elem bim:hasPropertySet ?pset }}
    OPTIONAL {{ ?elem bim:hasMaterial ?mat }}
}}
GROUP BY ?category
ORDER BY DESC(?elementCount)
"""


def audit_property_sets() -> str:
    """PropertySet 이름별 속성 목록."""
    return f"""{PREFIXES}
SELECT ?psetName
    (COUNT(DISTINCT ?prop) AS ?propCount)
    (GROUP_CONCAT(DISTINCT ?propName; SEPARATOR=", ") AS ?propertyNames)
    (COUNT(DISTINCT ?elem) AS ?usedByElements)
WHERE {{
    ?pset rdf:type bim:PropertySet ;
          bim:hasName ?psetName ;
          bim:hasProperty ?prop .
    ?prop bim:hasName ?propName .
    OPTIONAL {{ ?elem bim:hasPropertySet ?pset }}
}}
GROUP BY ?psetName
ORDER BY DESC(?propCount)
"""


def audit_element_completeness() -> str:
    """요소별 속성 완성도: 보유 속성 체크."""
    return f"""{PREFIXES}
SELECT ?elem ?name ?category ?originalType
    (BOUND(?desc) AS ?hasDescription)
    (BOUND(?tag) AS ?hasTag)
    (BOUND(?objectType) AS ?hasObjectType)
    (COUNT(DISTINCT ?pset) AS ?propertySetCount)
    (BOUND(?mat) AS ?hasMaterial)
    (BOUND(?area) AS ?hasArea)
    (BOUND(?length) AS ?hasLength)
    (BOUND(?volume) AS ?hasVolume)
    (BOUND(?weight) AS ?hasWeight)
WHERE {{
    ?elem rdf:type bim:PhysicalElement ;
          bim:hasName ?name ;
          bim:hasCategory ?category .
    OPTIONAL {{ ?elem bim:hasOriginalType ?originalType }}
    OPTIONAL {{ ?elem bim:hasDescription ?desc }}
    OPTIONAL {{ ?elem bim:hasTag ?tag }}
    OPTIONAL {{ ?elem bim:hasObjectType ?objectType }}
    OPTIONAL {{ ?elem bim:hasPropertySet ?pset }}
    OPTIONAL {{ ?elem bim:hasMaterial ?mat }}
    OPTIONAL {{ ?elem bim:hasArea ?area }}
    OPTIONAL {{ ?elem bim:hasLength ?length }}
    OPTIONAL {{ ?elem bim:hasVolume ?volume }}
    OPTIONAL {{ ?elem bim:hasWeight ?weight }}
}}
GROUP BY ?elem ?name ?category ?originalType ?desc ?tag ?objectType ?mat ?area ?length ?volume ?weight
LIMIT 200
"""


def audit_spatial_hierarchy() -> str:
    """공간 계층 구조 전체 + 요소 수."""
    return f"""{PREFIXES}
SELECT ?project ?projectName
       ?site ?siteName
       ?building ?buildingName
       ?storey ?storeyName ?storeyElev
       (COUNT(DISTINCT ?elem) AS ?elemCount)
WHERE {{
    ?project rdf:type bim:Project .
    OPTIONAL {{ ?project bim:hasName ?projectName }}
    ?project bim:aggregates ?site .
    OPTIONAL {{ ?site bim:hasName ?siteName }}
    ?site bim:aggregates ?building .
    OPTIONAL {{ ?building bim:hasName ?buildingName }}
    ?building bim:aggregates ?storey .
    OPTIONAL {{ ?storey bim:hasName ?storeyName }}
    OPTIONAL {{ ?storey bim:hasElevation ?storeyElev }}
    OPTIONAL {{ ?storey bim:containsElement ?elem }}
}}
GROUP BY ?project ?projectName ?site ?siteName ?building ?buildingName ?storey ?storeyName ?storeyElev
ORDER BY ?storeyElev
"""


def audit_all_predicates() -> str:
    """RDF 그래프에 존재하는 모든 predicate(속성/관계)와 사용 횟수."""
    return f"""{PREFIXES}
SELECT ?predicate (COUNT(*) AS ?usageCount)
WHERE {{
    ?s ?predicate ?o .
    FILTER(STRSTARTS(STR(?predicate), STR(bim:)))
}}
GROUP BY ?predicate
ORDER BY DESC(?usageCount)
"""


# 감사 쿼리 레지스트리
AUDIT_QUERY_TEMPLATES = {
    "audit_data_summary": audit_data_summary,
    "audit_category_stats": audit_category_stats,
    "audit_property_sets": audit_property_sets,
    "audit_element_completeness": audit_element_completeness,
    "audit_spatial_hierarchy": audit_spatial_hierarchy,
    "audit_all_predicates": audit_all_predicates,
}
