"""RDF 네임스페이스 관리 모듈.

ifcOWL 및 프로젝트 온톨로지 네임스페이스를 정의하고 관리합니다.
"""

from rdflib import Namespace, Graph, RDF, RDFS, OWL, XSD


# ifcOWL 표준 네임스페이스 (buildingSMART)
IFC4 = Namespace("https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#")
IFC2X3 = Namespace("https://standards.buildingsmart.org/IFC/DEV/IFC2x3/TC1/OWL#")

# 프로젝트 온톨로지 네임스페이스
BIM = Namespace("http://example.org/bim-ontology/schema#")
INST = Namespace("http://example.org/bim-ontology/instance#")
SCHED = Namespace("http://example.org/bim-ontology/schedule#")
AWP = Namespace("http://example.org/bim-ontology/awp#")

# EXPRESS 스키마 네임스페이스
EXPRESS = Namespace("https://w3id.org/express#")

# Linked Building Data 네임스페이스
BOT = Namespace("https://w3id.org/bot#")

# Smart Plant 3D 네임스페이스
SP3D = Namespace("http://example.org/bim-ontology/sp3d#")

# 스키마별 네임스페이스 매핑
SCHEMA_NAMESPACES = {
    "IFC4": IFC4,
    "IFC2X3": IFC2X3,
}


def get_ifc_namespace(schema: str) -> Namespace:
    """IFC 스키마 버전에 맞는 네임스페이스를 반환한다.

    Args:
        schema: IFC 스키마 버전 ('IFC4' 또는 'IFC2X3')

    Returns:
        해당 스키마의 Namespace 객체

    Raises:
        ValueError: 지원하지 않는 스키마일 때
    """
    if schema not in SCHEMA_NAMESPACES:
        raise ValueError(
            f"지원하지 않는 스키마: {schema}. "
            f"지원 목록: {list(SCHEMA_NAMESPACES.keys())}"
        )
    return SCHEMA_NAMESPACES[schema]


def bind_namespaces(graph: Graph, schema: str = "IFC4") -> Graph:
    """RDF 그래프에 표준 네임스페이스를 바인딩한다.

    Args:
        graph: rdflib Graph 객체
        schema: IFC 스키마 버전

    Returns:
        네임스페이스가 바인딩된 Graph
    """
    ifc_ns = get_ifc_namespace(schema)

    graph.bind("ifc", ifc_ns)
    graph.bind("bim", BIM)
    graph.bind("inst", INST)
    graph.bind("sched", SCHED)
    graph.bind("awp", AWP)
    graph.bind("express", EXPRESS)
    graph.bind("bot", BOT)
    graph.bind("sp3d", SP3D)
    graph.bind("owl", OWL)
    graph.bind("rdfs", RDFS)
    graph.bind("rdf", RDF)
    graph.bind("xsd", XSD)

    return graph
