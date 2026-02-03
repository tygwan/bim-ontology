"""SHACL 검증 모듈.

BIM 온톨로지 데이터에 대한 SHACL 형상 제약조건을 검증합니다.
"""

import logging
from pathlib import Path
from typing import Any

from rdflib import Graph

logger = logging.getLogger(__name__)

SHAPES_FILE = Path("data/ontology/shapes.ttl")


def load_shapes(shapes_path: str | None = None) -> Graph:
    """SHACL 형상 그래프를 로딩한다."""
    path = Path(shapes_path) if shapes_path else SHAPES_FILE
    shapes_graph = Graph()
    if path.exists():
        shapes_graph.parse(str(path), format="turtle")
        logger.info("SHACL shapes 로딩: %d 트리플", len(shapes_graph))
    else:
        logger.warning("SHACL shapes 파일 없음: %s", path)
    return shapes_graph


def validate(
    data_graph: Graph,
    shapes_path: str | None = None,
) -> dict[str, Any]:
    """데이터 그래프를 SHACL shapes로 검증한다.

    Returns:
        검증 결과 딕셔너리:
        - conforms: 전체 적합 여부
        - violations_count: 위반 건수
        - violations: 위반 상세 리스트
    """
    try:
        import pyshacl
    except ImportError:
        return {
            "conforms": None,
            "violations_count": 0,
            "violations": [],
            "error": "pyshacl not installed. Install with: pip install pyshacl>=0.26",
        }

    shapes_graph = load_shapes(shapes_path)
    if len(shapes_graph) == 0:
        return {
            "conforms": None,
            "violations_count": 0,
            "violations": [],
            "error": "No SHACL shapes found",
        }

    conforms, results_graph, results_text = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
    )

    # 위반 사항 파싱
    violations = []
    SH = "http://www.w3.org/ns/shacl#"
    for result_node in results_graph.subjects(
        predicate=None, object=None
    ):
        result_type = None
        for _, _, o in results_graph.triples((result_node, None, None)):
            if str(o).endswith("ValidationResult"):
                result_type = result_node
                break

        if result_type is None:
            continue

        violation = {}
        for p, o in results_graph.predicate_objects(result_node):
            p_name = str(p).replace(SH, "sh:")
            if "focusNode" in str(p):
                violation["focus_node"] = str(o)
            elif "resultMessage" in str(p):
                violation["message"] = str(o)
            elif "resultSeverity" in str(p):
                violation["severity"] = str(o).split("#")[-1]
            elif "sourceConstraintComponent" in str(p):
                violation["constraint"] = str(o).split("#")[-1]
            elif "resultPath" in str(p):
                violation["path"] = str(o)

        if violation:
            violations.append(violation)

    return {
        "conforms": conforms,
        "violations_count": len(violations),
        "violations": violations,
        "results_text": results_text[:2000] if results_text else "",
    }
