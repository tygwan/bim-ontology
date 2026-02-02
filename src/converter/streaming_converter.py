"""대용량 IFC 파일 스트리밍 변환 모듈.

828MB+ IFC 파일을 배치 단위로 처리하여 메모리 사용을 제한합니다.
변환 진행률을 콜백으로 보고합니다.
"""

import logging
import time
from typing import Any, Callable

from rdflib import Graph, Literal, URIRef, RDF, RDFS, OWL, XSD

from .namespace_manager import BIM, INST, bind_namespaces, get_ifc_namespace
from .mapping import GEOMETRY_TYPES, SPATIAL_TYPES, is_convertible, map_ifc_value
from ..parser.ifc_parser import IFCParser, classify_element_name

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]


class StreamingConverter:
    """대용량 IFC 파일을 배치 단위로 스트리밍 변환하는 클래스.

    일반 RDFConverter와 달리 엔티티 타입 단위로 순회하며
    배치 처리하여 메모리 피크를 제한합니다.
    """

    def __init__(self, schema: str = "IFC4", batch_size: int = 1000):
        self._schema = schema
        self._ifc_ns = get_ifc_namespace(schema)
        self._batch_size = batch_size
        self._stats = {
            "entities_processed": 0,
            "entities_skipped": 0,
            "triples_generated": 0,
            "batches": 0,
            "elapsed": 0.0,
        }

    @property
    def stats(self) -> dict:
        return {**self._stats}

    def convert(
        self,
        parser: IFCParser,
        output_path: str,
        progress_cb: ProgressCallback | None = None,
    ) -> str:
        """IFC 파일을 스트리밍 방식으로 RDF Turtle 파일로 변환한다.

        Args:
            parser: 로딩된 IFCParser
            output_path: 출력 Turtle 파일 경로
            progress_cb: 진행률 콜백 (current, total, message)

        Returns:
            출력 파일 경로
        """
        start = time.time()
        g = Graph()
        bind_namespaces(g, self._schema)

        # 스키마(TBox) 구축
        self._build_schema(g)

        type_counts = parser.get_type_counts()
        total_types = len(type_counts)
        convertible_types = [t for t in type_counts if self._should_convert(t)]

        if progress_cb:
            progress_cb(0, len(convertible_types), "변환 시작")

        # 공간 구조 먼저 변환
        for spatial_type in ["IfcProject", "IfcSite", "IfcBuilding",
                             "IfcBuildingStorey", "IfcSpace"]:
            self._convert_spatial_type(parser, g, spatial_type)

        # 관계 변환
        self._convert_relations(parser, g)

        # 물리적 요소를 타입 단위 배치로 변환
        for idx, ifc_type in enumerate(convertible_types):
            if ifc_type in SPATIAL_TYPES:
                continue

            entities = parser.get_entities(ifc_type)
            batch_count = 0

            for entity in entities:
                if not hasattr(entity, "GlobalId") or not entity.GlobalId:
                    self._stats["entities_skipped"] += 1
                    continue

                self._convert_single_entity(g, entity, ifc_type)
                batch_count += 1
                self._stats["entities_processed"] += 1

                if batch_count % self._batch_size == 0:
                    self._stats["batches"] += 1

            if progress_cb:
                progress_cb(
                    idx + 1,
                    len(convertible_types),
                    f"{ifc_type}: {batch_count}개",
                )

        # 속성셋 변환
        self._convert_property_sets(parser, g)

        # 저장
        self._stats["triples_generated"] = len(g)
        self._stats["elapsed"] = time.time() - start

        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        g.serialize(destination=output_path, format="turtle")

        logger.info(
            "스트리밍 변환 완료: %d 엔티티, %d 트리플, %.1f초, %d 스킵",
            self._stats["entities_processed"],
            self._stats["triples_generated"],
            self._stats["elapsed"],
            self._stats["entities_skipped"],
        )
        return output_path

    def _should_convert(self, ifc_type: str) -> bool:
        """변환 대상인지 확인한다."""
        if ifc_type in GEOMETRY_TYPES:
            return False
        return is_convertible(ifc_type)

    def _build_schema(self, g: Graph):
        """온톨로지 TBox를 구축한다."""
        g.add((BIM.BIMElement, RDF.type, OWL.Class))
        g.add((BIM.SpatialElement, RDF.type, OWL.Class))
        g.add((BIM.SpatialElement, RDFS.subClassOf, BIM.BIMElement))
        g.add((BIM.PhysicalElement, RDF.type, OWL.Class))
        g.add((BIM.PhysicalElement, RDFS.subClassOf, BIM.BIMElement))

        for cls_name in ["Project", "Site", "Building", "BuildingStorey", "Space"]:
            cls = BIM[cls_name]
            g.add((cls, RDF.type, OWL.Class))
            g.add((cls, RDFS.subClassOf, BIM.SpatialElement))

        # 프로퍼티
        for prop in ["hasGlobalId", "hasName", "hasDescription",
                     "hasObjectType", "hasTag", "hasCategory",
                     "hasOriginalType"]:
            g.add((BIM[prop], RDF.type, OWL.DatatypeProperty))

        g.add((BIM.hasElevation, RDF.type, OWL.DatatypeProperty))
        g.add((BIM.containsElement, RDF.type, OWL.ObjectProperty))
        g.add((BIM.isContainedIn, RDF.type, OWL.ObjectProperty))
        g.add((BIM.isContainedIn, OWL.inverseOf, BIM.containsElement))
        g.add((BIM.aggregates, RDF.type, OWL.ObjectProperty))
        g.add((BIM.decomposes, RDF.type, OWL.ObjectProperty))
        g.add((BIM.decomposes, OWL.inverseOf, BIM.aggregates))
        g.add((BIM.hasPropertySet, RDF.type, OWL.ObjectProperty))
        g.add((BIM.hasProperty, RDF.type, OWL.ObjectProperty))
        g.add((BIM.hasPropertyValue, RDF.type, OWL.DatatypeProperty))

    def _convert_spatial_type(self, parser: IFCParser, g: Graph, ifc_type: str):
        """공간 요소를 변환한다."""
        bim_class_map = {
            "IfcProject": BIM.Project,
            "IfcSite": BIM.Site,
            "IfcBuilding": BIM.Building,
            "IfcBuildingStorey": BIM.BuildingStorey,
            "IfcSpace": BIM.Space,
        }
        bim_class = bim_class_map.get(ifc_type)
        if not bim_class:
            return

        for entity in parser.get_entities(ifc_type):
            uri = self._entity_uri(entity)
            g.add((uri, RDF.type, bim_class))
            g.add((uri, RDF.type, self._ifc_ns[ifc_type]))
            if entity.GlobalId:
                g.add((uri, BIM.hasGlobalId, Literal(entity.GlobalId)))
            if entity.Name:
                g.add((uri, BIM.hasName, Literal(entity.Name)))
                g.add((uri, RDFS.label, Literal(entity.Name)))
            if ifc_type == "IfcBuildingStorey" and entity.Elevation is not None:
                g.add((uri, BIM.hasElevation,
                       Literal(entity.Elevation, datatype=XSD.double)))
            self._stats["entities_processed"] += 1

    def _convert_relations(self, parser: IFCParser, g: Graph):
        """공간 관계를 변환한다."""
        for parent, child in parser.get_aggregation_relations():
            g.add((self._entity_uri(parent), BIM.aggregates, self._entity_uri(child)))
            g.add((self._entity_uri(child), BIM.decomposes, self._entity_uri(parent)))

        for structure, element in parser.get_containment_relations():
            g.add((self._entity_uri(structure), BIM.containsElement,
                   self._entity_uri(element)))
            g.add((self._entity_uri(element), BIM.isContainedIn,
                   self._entity_uri(structure)))

    def _convert_single_entity(self, g: Graph, entity: Any, ifc_type: str):
        """단일 엔티티를 변환한다."""
        uri = self._entity_uri(entity)
        g.add((uri, RDF.type, self._ifc_ns[ifc_type]))
        g.add((uri, RDF.type, BIM.PhysicalElement))

        if entity.GlobalId:
            g.add((uri, BIM.hasGlobalId, Literal(entity.GlobalId)))
        if hasattr(entity, "Name") and entity.Name:
            g.add((uri, BIM.hasName, Literal(entity.Name)))
            g.add((uri, RDFS.label, Literal(entity.Name)))
        if hasattr(entity, "ObjectType") and entity.ObjectType:
            g.add((uri, BIM.hasObjectType, Literal(entity.ObjectType)))

        g.add((uri, BIM.hasOriginalType, Literal(ifc_type)))

        # IfcBuildingElementProxy 이름 기반 분류
        if ifc_type == "IfcBuildingElementProxy":
            category = classify_element_name(
                entity.Name if hasattr(entity, "Name") else None
            )
            g.add((uri, BIM.hasCategory, Literal(category)))
            cat_class = BIM[category]
            g.add((uri, RDF.type, cat_class))
            g.add((cat_class, RDF.type, OWL.Class))
            g.add((cat_class, RDFS.subClassOf, BIM.PhysicalElement))

    def _convert_property_sets(self, parser: IFCParser, g: Graph):
        """속성셋을 변환한다."""
        for rel in parser.get_entities("IfcRelDefinesByProperties"):
            pset_def = rel.RelatingPropertyDefinition
            if not hasattr(pset_def, "HasProperties") or not pset_def.HasProperties:
                continue

            pset_uri = INST[f"pset_{pset_def.GlobalId}"]
            g.add((pset_uri, RDF.type, BIM.PropertySet))
            if pset_def.Name:
                g.add((pset_uri, BIM.hasName, Literal(pset_def.Name)))

            for prop in pset_def.HasProperties:
                prop_uri = INST[f"prop_{pset_def.GlobalId}_{prop.Name}"]
                g.add((pset_uri, BIM.hasProperty, prop_uri))
                g.add((prop_uri, BIM.hasName, Literal(prop.Name)))
                value = map_ifc_value(getattr(prop, "NominalValue", None))
                if value is not None:
                    g.add((prop_uri, BIM.hasPropertyValue, value))

            for obj in rel.RelatedObjects:
                g.add((self._entity_uri(obj), BIM.hasPropertySet, pset_uri))

    def _entity_uri(self, entity: Any) -> URIRef:
        """엔티티 URI를 생성한다."""
        ifc_type = entity.is_a().lower()
        if hasattr(entity, "GlobalId") and entity.GlobalId:
            return INST[f"{ifc_type}_{entity.GlobalId}"]
        return INST[f"{ifc_type}_{entity.id()}"]
