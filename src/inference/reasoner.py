"""OWL/RDFS 추론 엔진 모듈.

owlrl 라이브러리를 사용하여 RDF 그래프에 추론 규칙을 적용합니다.
RDFS 클래스 계층, OWL inverse 속성, 커스텀 SPARQL CONSTRUCT 규칙을 지원합니다.
"""

import logging
import time

from rdflib import Graph, Literal, RDF, RDFS, OWL, XSD, URIRef
import owlrl

from ..converter.namespace_manager import BIM, INST

logger = logging.getLogger(__name__)

# 커스텀 추론 규칙 (SPARQL CONSTRUCT)
CUSTOM_RULES = {
    "infer_structural_element": {
        "description": "Beam, Column, Slab, Wall, Foundation → StructuralElement 추론",
        "construct": """
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            CONSTRUCT { ?elem rdf:type bim:StructuralElement }
            WHERE {
                ?elem bim:hasCategory ?cat .
                FILTER(?cat IN ("Beam", "Column", "Slab", "Wall", "Foundation"))
            }
        """,
    },
    "infer_mep_element": {
        "description": "Pipe, Duct, CableTray, Valve, Pump → MEPElement 추론",
        "construct": """
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            CONSTRUCT { ?elem rdf:type bim:MEPElement }
            WHERE {
                ?elem bim:hasCategory ?cat .
                FILTER(?cat IN ("Pipe", "Duct", "CableTray", "Valve", "Pump",
                               "Insulation", "Equipment"))
            }
        """,
    },
    "infer_access_element": {
        "description": "Stair, Railing → AccessElement 추론",
        "construct": """
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            CONSTRUCT { ?elem rdf:type bim:AccessElement }
            WHERE {
                ?elem bim:hasCategory ?cat .
                FILTER(?cat IN ("Stair", "Railing"))
            }
        """,
    },
    "infer_storey_has_elements": {
        "description": "층이 포함하는 요소가 있으면 hasElements = true 추론",
        "construct": """
            PREFIX bim: <http://example.org/bim-ontology/schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            CONSTRUCT { ?storey bim:hasElements "true"^^xsd:boolean }
            WHERE {
                ?storey rdf:type bim:BuildingStorey .
                ?storey bim:containsElement ?elem .
            }
        """,
    },
    "infer_element_in_building": {
        "description": "층에 포함된 요소 → 건물에도 속함 추론 (전이적)",
        "construct": """
            PREFIX bim: <http://example.org/bim-ontology/schema#>

            CONSTRUCT { ?elem bim:isInBuilding ?building }
            WHERE {
                ?building bim:aggregates ?storey .
                ?storey bim:containsElement ?elem .
            }
        """,
    },
}


class OWLReasoner:
    """OWL/RDFS 추론 엔진.

    owlrl을 사용한 RDFS/OWL 추론과
    커스텀 SPARQL CONSTRUCT 규칙을 적용합니다.
    """

    def __init__(self, graph: Graph):
        self._graph = graph
        self._inferred_count = 0
        self._rules_applied: list[str] = []

    @property
    def graph(self) -> Graph:
        return self._graph

    @property
    def stats(self) -> dict:
        return {
            "total_triples": len(self._graph),
            "inferred_triples": self._inferred_count,
            "rules_applied": self._rules_applied,
        }

    def run_rdfs_reasoning(self) -> int:
        """RDFS 추론을 수행한다.

        subClassOf 계층에 따른 타입 추론 등을 적용합니다.

        Returns:
            추론된 새 트리플 수
        """
        before = len(self._graph)
        start = time.time()

        owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(self._graph)

        added = len(self._graph) - before
        self._inferred_count += added
        self._rules_applied.append("RDFS_Semantics")

        logger.info("RDFS 추론: +%d 트리플 (%.1f초)", added, time.time() - start)
        return added

    def run_owl_reasoning(self) -> int:
        """OWL RL 추론을 수행한다.

        inverseOf, equivalentClass 등 OWL 추론을 적용합니다.

        Returns:
            추론된 새 트리플 수
        """
        before = len(self._graph)
        start = time.time()

        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(self._graph)

        added = len(self._graph) - before
        self._inferred_count += added
        self._rules_applied.append("OWLRL_Semantics")

        logger.info("OWL RL 추론: +%d 트리플 (%.1f초)", added, time.time() - start)
        return added

    def apply_custom_rules(self, rule_names: list[str] | None = None) -> int:
        """커스텀 SPARQL CONSTRUCT 규칙을 적용한다.

        Args:
            rule_names: 적용할 규칙 이름 목록. None이면 전체 적용.

        Returns:
            추론된 새 트리플 수
        """
        if rule_names is None:
            rule_names = list(CUSTOM_RULES.keys())

        total_added = 0
        for name in rule_names:
            rule = CUSTOM_RULES.get(name)
            if not rule:
                logger.warning("알 수 없는 규칙: %s", name)
                continue

            before = len(self._graph)
            result = self._graph.query(rule["construct"])

            # CONSTRUCT 결과를 그래프에 추가
            for triple in result:
                self._graph.add(triple)

            added = len(self._graph) - before
            total_added += added
            self._rules_applied.append(name)

            logger.info("규칙 '%s': +%d 트리플 (%s)", name, added, rule["description"])

        self._inferred_count += total_added
        return total_added

    def add_schema_classes(self):
        """추론용 추가 스키마 클래스를 정의한다."""
        g = self._graph

        # 구조 요소 상위 클래스
        g.add((BIM.StructuralElement, RDF.type, OWL.Class))
        g.add((BIM.StructuralElement, RDFS.subClassOf, BIM.PhysicalElement))
        g.add((BIM.StructuralElement, RDFS.label, Literal("Structural Element")))

        # MEP 요소 상위 클래스
        g.add((BIM.MEPElement, RDF.type, OWL.Class))
        g.add((BIM.MEPElement, RDFS.subClassOf, BIM.PhysicalElement))
        g.add((BIM.MEPElement, RDFS.label, Literal("MEP Element")))

        # 접근 요소 상위 클래스
        g.add((BIM.AccessElement, RDF.type, OWL.Class))
        g.add((BIM.AccessElement, RDFS.subClassOf, BIM.PhysicalElement))
        g.add((BIM.AccessElement, RDFS.label, Literal("Access Element")))

        # 건물 포함 관계
        g.add((BIM.isInBuilding, RDF.type, OWL.ObjectProperty))
        g.add((BIM.isInBuilding, RDFS.domain, BIM.PhysicalElement))
        g.add((BIM.isInBuilding, RDFS.range, BIM.Building))

        # 속성
        g.add((BIM.hasElements, RDF.type, OWL.DatatypeProperty))

    def run_all(self) -> dict:
        """스키마 추가 + 커스텀 규칙 + RDFS 추론을 모두 실행한다.

        Returns:
            추론 통계 딕셔너리
        """
        start = time.time()
        self.add_schema_classes()

        custom_added = self.apply_custom_rules()
        rdfs_added = self.run_rdfs_reasoning()

        total_time = time.time() - start
        return {
            "custom_rules_triples": custom_added,
            "rdfs_triples": rdfs_added,
            "total_inferred": self._inferred_count,
            "total_triples": len(self._graph),
            "elapsed": total_time,
            "rules_applied": self._rules_applied,
        }
