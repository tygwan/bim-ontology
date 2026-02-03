"""IFC → RDF 변환 메인 모듈.

IFC 파일의 엔티티를 ifcOWL 기반 RDF 트리플로 변환합니다.
공간 구조, 물리적 요소, 속성, 관계를 모두 변환합니다.
"""

import logging
import time
from typing import Any

from rdflib import Graph, Literal, URIRef, RDF, RDFS, OWL, XSD

from .namespace_manager import (
    BIM, INST, BOT, SP3D, bind_namespaces, get_ifc_namespace,
)
from .mapping import (
    SPATIAL_TYPES, CONVERTIBLE_TYPES, GEOMETRY_TYPES,
    get_entity_category, is_convertible, map_ifc_value,
)
from ..parser.ifc_parser import IFCParser, classify_element_name

logger = logging.getLogger(__name__)


class RDFConverter:
    """IFC 엔티티를 RDF 트리플로 변환하는 클래스."""

    def __init__(self, schema: str = "IFC4"):
        self._schema = schema
        self._ifc_ns = get_ifc_namespace(schema)
        self._graph = Graph()
        bind_namespaces(self._graph, schema)
        self._stats = {
            "entities_converted": 0,
            "triples_generated": 0,
            "unknown_types": set(),
            "convert_time": 0.0,
        }

    @property
    def graph(self) -> Graph:
        return self._graph

    @property
    def stats(self) -> dict:
        return {
            **self._stats,
            "unknown_types": list(self._stats["unknown_types"]),
            "total_triples": len(self._graph),
        }

    def convert_file(self, parser: IFCParser) -> Graph:
        """전체 IFC 파일을 RDF Graph로 변환한다.

        Args:
            parser: 로딩된 IFCParser 인스턴스

        Returns:
            변환된 rdflib Graph
        """
        start = time.time()

        self._build_schema()
        self._convert_spatial_structure(parser)
        self._convert_physical_elements(parser)
        self._convert_aggregation_relations(parser)
        self._convert_containment_relations(parser)
        self._convert_property_sets(parser)

        self._stats["convert_time"] = time.time() - start
        self._stats["triples_generated"] = len(self._graph)

        logger.info(
            "RDF 변환 완료: %d 엔티티, %d 트리플, %.1f초",
            self._stats["entities_converted"],
            self._stats["triples_generated"],
            self._stats["convert_time"],
        )
        return self._graph

    def convert_entity(self, entity: Any) -> list[tuple]:
        """단일 IFC 엔티티를 RDF 트리플 리스트로 변환한다."""
        ifc_type = entity.is_a()
        uri = self._entity_uri(entity)
        triples = []

        # rdf:type - ifcOWL 클래스
        ifc_class = self._ifc_ns[ifc_type]
        triples.append((uri, RDF.type, ifc_class))

        # GlobalId
        if hasattr(entity, "GlobalId") and entity.GlobalId:
            triples.append((uri, BIM.hasGlobalId, Literal(entity.GlobalId)))

        # Name
        if hasattr(entity, "Name") and entity.Name:
            triples.append((uri, BIM.hasName, Literal(entity.Name)))
            triples.append((uri, RDFS.label, Literal(entity.Name)))

        # Description
        if hasattr(entity, "Description") and entity.Description:
            triples.append((uri, BIM.hasDescription, Literal(entity.Description)))
            triples.append((uri, RDFS.comment, Literal(entity.Description)))

        # ObjectType (IfcBuildingElementProxy의 원래 타입 힌트)
        if hasattr(entity, "ObjectType") and entity.ObjectType:
            triples.append((uri, BIM.hasObjectType, Literal(entity.ObjectType)))

        # Tag
        if hasattr(entity, "Tag") and entity.Tag:
            triples.append((uri, BIM.hasTag, Literal(entity.Tag)))

        self._stats["entities_converted"] += 1
        return triples

    def map_entity_type(self, ifc_type: str) -> URIRef:
        """IFC 타입명을 ifcOWL 클래스 URI로 매핑한다."""
        return self._ifc_ns[ifc_type]

    def serialize(self, destination: str, fmt: str = "turtle") -> str:
        """RDF 그래프를 파일로 직렬화한다.

        Args:
            destination: 출력 파일 경로
            fmt: 직렬화 포맷 ('turtle', 'xml', 'json-ld', 'n3')

        Returns:
            출력 파일 경로
        """
        self._graph.serialize(destination=destination, format=fmt)
        return destination

    # ---------- 내부 메서드 ----------

    def _build_schema(self):
        """온톨로지 스키마(TBox)를 정의한다."""
        g = self._graph

        # 최상위 클래스
        g.add((BIM.BIMElement, RDF.type, OWL.Class))
        g.add((BIM.BIMElement, RDFS.label, Literal("BIM Element")))

        g.add((BIM.SpatialElement, RDF.type, OWL.Class))
        g.add((BIM.SpatialElement, RDFS.subClassOf, BIM.BIMElement))

        g.add((BIM.PhysicalElement, RDF.type, OWL.Class))
        g.add((BIM.PhysicalElement, RDFS.subClassOf, BIM.BIMElement))

        # 공간 클래스
        for cls_name in ["Project", "Site", "Building", "BuildingStorey", "Space"]:
            cls = BIM[cls_name]
            g.add((cls, RDF.type, OWL.Class))
            g.add((cls, RDFS.subClassOf, BIM.SpatialElement))
            g.add((cls, RDFS.label, Literal(cls_name)))

        # 데이터 프로퍼티
        data_props = {
            "hasGlobalId": (BIM.BIMElement, XSD.string),
            "hasName": (BIM.BIMElement, XSD.string),
            "hasDescription": (BIM.BIMElement, XSD.string),
            "hasObjectType": (BIM.BIMElement, XSD.string),
            "hasTag": (BIM.BIMElement, XSD.string),
            "hasCategory": (BIM.PhysicalElement, XSD.string),
            "hasOriginalType": (BIM.PhysicalElement, XSD.string),
            "hasElevation": (BIM.BuildingStorey, XSD.double),
        }
        for prop_name, (domain, range_type) in data_props.items():
            prop = BIM[prop_name]
            g.add((prop, RDF.type, OWL.DatatypeProperty))
            g.add((prop, RDFS.domain, domain))
            g.add((prop, RDFS.range, range_type))

        # 오브젝트 프로퍼티
        g.add((BIM.containsElement, RDF.type, OWL.ObjectProperty))
        g.add((BIM.containsElement, RDFS.domain, BIM.SpatialElement))
        g.add((BIM.containsElement, RDFS.range, BIM.BIMElement))

        g.add((BIM.isContainedIn, RDF.type, OWL.ObjectProperty))
        g.add((BIM.isContainedIn, OWL.inverseOf, BIM.containsElement))

        g.add((BIM.aggregates, RDF.type, OWL.ObjectProperty))
        g.add((BIM.decomposes, RDF.type, OWL.ObjectProperty))
        g.add((BIM.decomposes, OWL.inverseOf, BIM.aggregates))

        g.add((BIM.hasPropertySet, RDF.type, OWL.ObjectProperty))
        g.add((BIM.hasProperty, RDF.type, OWL.ObjectProperty))
        g.add((BIM.hasPropertyValue, RDF.type, OWL.DatatypeProperty))

    def _convert_spatial_structure(self, parser: IFCParser):
        """공간 구조 요소를 변환한다."""
        spatial_map = {
            "IfcProject": BIM.Project,
            "IfcSite": BIM.Site,
            "IfcBuilding": BIM.Building,
            "IfcBuildingStorey": BIM.BuildingStorey,
            "IfcSpace": BIM.Space,
        }

        for ifc_type, bim_class in spatial_map.items():
            for entity in parser.get_entities(ifc_type):
                uri = self._entity_uri(entity)
                triples = self.convert_entity(entity)
                for t in triples:
                    self._graph.add(t)

                self._graph.add((uri, RDF.type, bim_class))

                # 층 표고
                if ifc_type == "IfcBuildingStorey" and entity.Elevation is not None:
                    self._graph.add((
                        uri, BIM.hasElevation,
                        Literal(entity.Elevation, datatype=XSD.double),
                    ))

    def _convert_physical_elements(self, parser: IFCParser):
        """물리적 요소를 변환한다.

        모든 IfcProduct 하위 타입을 순회하며 변환합니다.
        IfcBuildingElementProxy는 이름 기반 분류를 추가로 수행합니다.
        """
        g = self._graph
        type_counts = parser.get_type_counts()
        category_classes_added = set()

        for ifc_type in type_counts:
            if not is_convertible(ifc_type):
                continue
            if ifc_type in SPATIAL_TYPES:
                continue  # 이미 처리됨

            for entity in parser.get_entities(ifc_type):
                # GlobalId가 없는 엔티티(IfcPresentationLayerAssignment 등)는 스킵
                if not hasattr(entity, "GlobalId") or not entity.GlobalId:
                    continue
                uri = self._entity_uri(entity)
                triples = self.convert_entity(entity)
                for t in triples:
                    g.add(t)

                g.add((uri, RDF.type, BIM.PhysicalElement))
                g.add((uri, BIM.hasOriginalType, Literal(ifc_type)))

                # IfcBuildingElementProxy: 이름 기반 카테고리 분류
                if ifc_type == "IfcBuildingElementProxy":
                    category = classify_element_name(entity.Name)
                    g.add((uri, BIM.hasCategory, Literal(category)))

                    cat_class = BIM[category]
                    g.add((uri, RDF.type, cat_class))

                    if category not in category_classes_added:
                        g.add((cat_class, RDF.type, OWL.Class))
                        g.add((cat_class, RDFS.subClassOf, BIM.PhysicalElement))
                        g.add((cat_class, RDFS.label, Literal(category)))
                        category_classes_added.add(category)

    def _convert_aggregation_relations(self, parser: IFCParser):
        """IfcRelAggregates 관계를 변환한다."""
        for parent, child in parser.get_aggregation_relations():
            parent_uri = self._entity_uri(parent)
            child_uri = self._entity_uri(child)
            self._graph.add((parent_uri, BIM.aggregates, child_uri))
            self._graph.add((child_uri, BIM.decomposes, parent_uri))

    def _convert_containment_relations(self, parser: IFCParser):
        """IfcRelContainedInSpatialStructure 관계를 변환한다."""
        for structure, element in parser.get_containment_relations():
            structure_uri = self._entity_uri(structure)
            element_uri = self._entity_uri(element)
            self._graph.add((structure_uri, BIM.containsElement, element_uri))
            self._graph.add((element_uri, BIM.isContainedIn, structure_uri))

    def _convert_property_sets(self, parser: IFCParser):
        """IfcRelDefinesByProperties를 통한 속성셋을 변환한다."""
        g = self._graph

        for rel in parser.get_entities("IfcRelDefinesByProperties"):
            pset_def = rel.RelatingPropertyDefinition

            if not hasattr(pset_def, "HasProperties"):
                continue
            if not pset_def.HasProperties:
                continue

            pset_uri = INST[f"pset_{pset_def.GlobalId}"]
            g.add((pset_uri, RDF.type, BIM.PropertySet))
            if pset_def.Name:
                g.add((pset_uri, BIM.hasName, Literal(pset_def.Name)))
                g.add((pset_uri, RDFS.label, Literal(pset_def.Name)))

                # Smart Plant 3D / Smart3D PropertySet 감지
                is_sp3d = (
                    pset_def.Name.startswith("SP3D")
                    or "SmartPlant" in pset_def.Name
                    or "Smart3D" in pset_def.Name
                )
                if is_sp3d:
                    g.add((pset_uri, RDF.type, BIM.PlantPropertySet))

            # 속성 변환
            for prop in pset_def.HasProperties:
                prop_uri = INST[f"prop_{pset_def.GlobalId}_{prop.Name}"]
                g.add((pset_uri, BIM.hasProperty, prop_uri))
                g.add((prop_uri, BIM.hasName, Literal(prop.Name)))

                value = map_ifc_value(getattr(prop, "NominalValue", None))
                if value is not None:
                    g.add((prop_uri, BIM.hasPropertyValue, value))

            # 요소 → 속성셋 연결
            for obj in rel.RelatedObjects:
                obj_uri = self._entity_uri(obj)
                g.add((obj_uri, BIM.hasPropertySet, pset_uri))

    def _entity_uri(self, entity: Any) -> URIRef:
        """IFC 엔티티의 고유 URI를 생성한다.

        GlobalId가 없는 엔티티는 entity id로 대체합니다.
        """
        ifc_type = entity.is_a().lower()
        if hasattr(entity, "GlobalId") and entity.GlobalId:
            return INST[f"{ifc_type}_{entity.GlobalId}"]
        return INST[f"{ifc_type}_{entity.id()}"]
