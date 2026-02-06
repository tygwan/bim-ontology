"""Navisworks CSV (dxtnavis export) → RDF 변환기.

dxtnavis에서 추출한 CSV를 RDF로 변환합니다.
IFC 중간 단계 없이 원본 데이터의 풍부한 속성을 보존합니다.

지원 포맷:
- UnifiedExport CSV (v2): 오브젝트당 1행, PropertiesJson + BBox/Centroid/Volume
- AllHierarchy CSV (v1): 속성당 1행, 플랫 컬럼 (하위 호환)
- schedule.csv: ConstructionTask + 요소 연결
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD

logger = logging.getLogger(__name__)

# Namespaces
BIM = Namespace("http://example.org/bim-ontology/schema#")
INST = Namespace("http://example.org/bim-ontology/instance#")
NAVIS = Namespace("http://example.org/bim-ontology/navis#")
SP3D = Namespace("http://example.org/bim-ontology/sp3d#")
SCHED = Namespace("http://example.org/bim-ontology/schedule#")
PROP = Namespace("http://example.org/bim-ontology/property#")  # Property-Value 패턴용
BSO = Namespace("http://example.org/bim-ontology/spatial#")  # BoundingBox/Spatial 정보


class NavisToRDFConverter:
    """dxtnavis CSV를 RDF로 변환하는 변환기."""

    # SmartPlant 3D 속성 → RDF 프로퍼티 매핑
    SP3D_PROPERTY_MAP = {
        "Name": (SP3D.hasName, XSD.string),
        "System Path": (SP3D.hasSystemPath, XSD.string),
        "BOM description": (SP3D.hasBOMDescription, XSD.string),
        "Support Assembly": (SP3D.hasSupportAssembly, XSD.string),
        "Support Dry Weight": (SP3D.hasDryWeight, XSD.string),
        "Support Location": (SP3D.hasLocation, XSD.string),
        "Status": (SP3D.hasStatus, XSD.string),
        "User Created": (SP3D.hasCreatedBy, XSD.string),
        "Date Created": (SP3D.hasCreatedDate, XSD.string),
        "User Last Modified": (SP3D.hasModifiedBy, XSD.string),
        "Date Last Modified": (SP3D.hasModifiedDate, XSD.string),
        "SP3d Moniker": (SP3D.hasMoniker, XSD.string),
        "Reporting Type": (SP3D.hasReportingType, XSD.string),
        "Construction Type": (SP3D.hasConstructionType, XSD.string),
        "Permission Group ID": (SP3D.hasPermissionGroupId, XSD.string),
    }

    # 카테고리 분류 매핑 (DisplayName 패턴 → BIM 카테고리)
    CATEGORY_PATTERNS = {
        "Pipe": ["Pipe-", "Pipe ", "Piping"],
        "Valve": ["Valve-", "Valve ", "VG3-", "VC", "VL"],
        "PipeFitting": ["Direction Change", "Eccentric", "Concentric", "Weldolet",
                        "Sockolet", "Nipple", "Flange-", "Elbow"],
        "Equipment": ["Tank", "Pump", "Vessel", "Exchanger", "Reactor", "Compressor",
                      "40E-", "40V-", "41P-", "41V-"],
        "Hanger": ["Hgr", "Anvil_", "ASSY_", "Assy_", "Support"],
        "Structure": ["Beam_", "Column_", "Member", "Slab", "Foundation"],
        "Conduit": ["Conduit", "COND-", "Cable"],
        "Instrument": ["Instrument", "Gauge", "Meter", "Sensor"],
        "Insulation": ["Insulation"],
        "Ladder": ["Ladder", "Stair", "Platform", "Walkway"],
        "Nozzle": ["Nozzle", "STNoz"],
    }

    @staticmethod
    def _parse_int_like(value: str) -> Optional[int]:
        """정수/실수 문자열을 정수로 파싱한다."""
        text = (value or "").strip()
        if not text:
            return None
        text = text.replace(",", "")
        try:
            return int(float(text))
        except ValueError:
            return None

    @staticmethod
    def _parse_float_like(value: str) -> Optional[float]:
        """숫자 문자열을 실수로 파싱한다."""
        text = (value or "").strip()
        if not text:
            return None
        text = text.replace(",", "")
        try:
            return float(text)
        except ValueError:
            return None

    def __init__(self):
        self.graph = Graph()
        self._bind_namespaces()
        self._add_schema()
        self._object_cache: Dict[str, URIRef] = {}
        self._hierarchy: Dict[str, Dict] = {}
        self._path_node_cache: Dict[str, URIRef] = {}  # System Path → URI
        self._path_element_counts: Dict[str, int] = {}  # System Path → element count
        self._child_counts: Dict[str, int] = {}  # ObjectId → direct child count
        self._descendant_counts: Dict[str, int] = {}  # ObjectId → total descendant count

    def _bind_namespaces(self):
        """네임스페이스를 그래프에 바인딩한다."""
        self.graph.bind("bim", BIM)
        self.graph.bind("inst", INST)
        self.graph.bind("navis", NAVIS)
        self.graph.bind("sp3d", SP3D)
        self.graph.bind("sched", SCHED)
        self.graph.bind("prop", PROP)
        self.graph.bind("bso", BSO)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)

    def _add_schema(self):
        """기본 스키마 클래스와 프로퍼티를 추가한다."""
        # Navis 전용 클래스
        self.graph.add((NAVIS.NavisElement, RDF.type, OWL.Class))
        self.graph.add((NAVIS.NavisElement, RDFS.subClassOf, BIM.BIMElement))
        self.graph.add((NAVIS.NavisElement, RDFS.label, Literal("Navisworks Element")))

        self.graph.add((NAVIS.NavisGroup, RDF.type, OWL.Class))
        self.graph.add((NAVIS.NavisGroup, RDFS.subClassOf, NAVIS.NavisElement))
        self.graph.add((NAVIS.NavisGroup, RDFS.label, Literal("Navisworks Group")))

        self.graph.add((NAVIS.SP3DEntity, RDF.type, OWL.Class))
        self.graph.add((NAVIS.SP3DEntity, RDFS.subClassOf, NAVIS.NavisElement))
        self.graph.add((NAVIS.SP3DEntity, RDFS.label, Literal("SmartPlant 3D Entity")))

        # System Path 계층 구조 클래스
        hierarchy_classes = [
            (NAVIS.Project, "Project", "프로젝트 (최상위)"),
            (NAVIS.Area, "Area", "영역 (Depth 1)"),
            (NAVIS.Unit, "Unit", "유닛 (Depth 2)"),
            (NAVIS.System, "System", "시스템 (Depth 3+)"),
        ]
        for cls, name, label in hierarchy_classes:
            self.graph.add((cls, RDF.type, OWL.Class))
            self.graph.add((cls, RDFS.subClassOf, NAVIS.NavisGroup))
            self.graph.add((cls, RDFS.label, Literal(label)))

        # 계층 관계 프로퍼티
        self.graph.add((NAVIS.containsElement, RDF.type, OWL.ObjectProperty))
        self.graph.add((NAVIS.containsElement, RDFS.label, Literal("Contains Element")))
        self.graph.add((NAVIS.isContainedIn, RDF.type, OWL.ObjectProperty))
        self.graph.add((NAVIS.isContainedIn, RDFS.label, Literal("Is Contained In")))
        self.graph.add((NAVIS.hasSystemPathParent, RDF.type, OWL.ObjectProperty))
        self.graph.add((NAVIS.hasSystemPathParent, RDFS.label, Literal("System Path Parent")))
        self.graph.add((NAVIS.hasElementCount, RDF.type, OWL.DatatypeProperty))
        self.graph.add((NAVIS.hasElementCount, RDFS.label, Literal("Element Count (pre-computed)")))
        self.graph.add((NAVIS.hasChildCount, RDF.type, OWL.DatatypeProperty))
        self.graph.add((NAVIS.hasChildCount, RDFS.label, Literal("Direct Child Count")))
        self.graph.add((NAVIS.hasDescendantCount, RDF.type, OWL.DatatypeProperty))
        self.graph.add((NAVIS.hasDescendantCount, RDFS.label, Literal("Total Descendant Count")))

        # Navis 프로퍼티
        props = [
            (NAVIS.hasObjectId, "Object ID (UUID)"),
            (NAVIS.hasParentId, "Parent Object ID"),
            (NAVIS.hasLevel, "Hierarchy Level"),
            (NAVIS.hasInternalType, "Internal Type"),
            (NAVIS.hasSourceFile, "Source File"),
            (NAVIS.hasParent, "Has Parent (ObjectProperty)"),
            (NAVIS.hasChild, "Has Child (ObjectProperty)"),
        ]
        for prop, label in props:
            self.graph.add((prop, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop, RDFS.label, Literal(label)))

        # SP3D 프로퍼티
        for name, (prop, _) in self.SP3D_PROPERTY_MAP.items():
            self.graph.add((prop, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop, RDFS.label, Literal(f"SP3D {name}")))

        # Lean/Schedule 확장 프로퍼티 (CSV 확장 컬럼 대응)
        schedule_props = [
            (SCHED.hasDuration, "Task Duration (legacy string)"),
            (SCHED.hasPlannedDuration, "Task Planned Duration (days)"),
            (SCHED.hasActualDuration, "Task Actual Duration (days)"),
            (SCHED.hasCost, "Task Cost"),
            (BIM.hasConsumeDuration, "Element Consume Duration (days)"),
            (BIM.hasUnitCost, "Element Unit Cost"),
        ]
        for prop, label in schedule_props:
            self.graph.add((prop, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop, RDFS.label, Literal(label)))

        # Property-Value 패턴용 스키마 (모든 CSV 속성 저장)
        self.graph.add((PROP.PropertyValue, RDF.type, OWL.Class))
        self.graph.add((PROP.PropertyValue, RDFS.label, Literal("Property Value")))
        self.graph.add((PROP.PropertyValue, RDFS.comment, Literal("CSV 속성값을 저장하는 클래스")))

        prop_schema = [
            (PROP.hasProperty, "Has Property", OWL.ObjectProperty),
            (PROP.category, "Category", OWL.DatatypeProperty),
            (PROP.propertyName, "Property Name", OWL.DatatypeProperty),
            (PROP.rawValue, "Raw Value", OWL.DatatypeProperty),
            (PROP.dataType, "Data Type", OWL.DatatypeProperty),
            (PROP.unit, "Unit", OWL.DatatypeProperty),
            (PROP.numericValue, "Numeric Value (pre-parsed)", OWL.DatatypeProperty),
        ]
        for prop, label, prop_type in prop_schema:
            self.graph.add((prop, RDF.type, prop_type))
            self.graph.add((prop, RDFS.label, Literal(label)))

        # Spatial/BoundingBox 스키마 (BSO namespace)
        self.graph.add((BSO.BoundingBox, RDF.type, OWL.Class))
        self.graph.add((BSO.BoundingBox, RDFS.label, Literal("Bounding Box")))

        bso_props = [
            (BSO.hasBoundingBox, "Has Bounding Box", OWL.ObjectProperty),
            (BSO.minX, "Min X", OWL.DatatypeProperty),
            (BSO.minY, "Min Y", OWL.DatatypeProperty),
            (BSO.minZ, "Min Z", OWL.DatatypeProperty),
            (BSO.maxX, "Max X", OWL.DatatypeProperty),
            (BSO.maxY, "Max Y", OWL.DatatypeProperty),
            (BSO.maxZ, "Max Z", OWL.DatatypeProperty),
            (BSO.centroidX, "Centroid X", OWL.DatatypeProperty),
            (BSO.centroidY, "Centroid Y", OWL.DatatypeProperty),
            (BSO.centroidZ, "Centroid Z", OWL.DatatypeProperty),
            (BSO.volume, "BBox Volume", OWL.DatatypeProperty),
            (BSO.hasMesh, "Has Mesh", OWL.DatatypeProperty),
            (BSO.meshUri, "Mesh URI", OWL.DatatypeProperty),
        ]
        for prop, label, prop_type in bso_props:
            self.graph.add((prop, RDF.type, prop_type))
            self.graph.add((prop, RDFS.label, Literal(label)))

    def _classify_element(self, display_name: str, internal_type: str) -> URIRef:
        """요소 이름과 타입을 기반으로 BIM 카테고리를 분류한다."""
        name_upper = display_name.upper()

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern.upper() in name_upper:
                    return BIM[category]

        # 내부 타입 기반 분류
        if internal_type:
            if "SP3D" in internal_type:
                return NAVIS.SP3DEntity
            if "Group" in internal_type or "그룹" in internal_type:
                return NAVIS.NavisGroup

        return BIM.Other

    def _get_or_create_element(self, object_id: str, display_name: str) -> URIRef:
        """ObjectId로 요소 URI를 가져오거나 생성한다."""
        if object_id in self._object_cache:
            return self._object_cache[object_id]

        # UUID를 안전한 URI로 변환
        safe_id = object_id.replace("-", "_")
        uri = INST[f"navis_{safe_id}"]
        self._object_cache[object_id] = uri
        return uri

    def _get_or_create_path_node(self, system_path: str) -> URIRef:
        """System Path에 해당하는 계층 노드를 가져오거나 생성한다.

        Args:
            system_path: 전체 시스템 경로 (예: "TRAINING\\Refining Area\\U01")

        Returns:
            해당 경로의 노드 URI
        """
        if system_path in self._path_node_cache:
            return self._path_node_cache[system_path]

        # 경로를 파싱
        parts = system_path.split("\\")

        # 모든 중간 경로 노드 생성
        current_path = ""
        parent_uri = None

        for i, part in enumerate(parts):
            if not part:
                continue

            if current_path:
                current_path = current_path + "\\" + part
            else:
                current_path = part

            if current_path in self._path_node_cache:
                parent_uri = self._path_node_cache[current_path]
                continue

            # 안전한 URI 생성 (특수문자 제거)
            safe_path = current_path.replace("\\", "_").replace(" ", "_").replace("-", "_")
            safe_path = "".join(c for c in safe_path if c.isalnum() or c == "_")
            uri = INST[f"path_{safe_path}"]

            # 깊이에 따른 타입 결정
            if i == 0:
                node_type = NAVIS.Project
            elif i == 1:
                node_type = NAVIS.Area
            elif i == 2:
                node_type = NAVIS.Unit
            else:
                node_type = NAVIS.System

            # 트리플 추가
            self.graph.add((uri, RDF.type, node_type))
            self.graph.add((uri, RDF.type, NAVIS.NavisGroup))
            self.graph.add((uri, RDFS.label, Literal(part)))
            self.graph.add((uri, BIM.hasName, Literal(part)))
            self.graph.add((uri, SP3D.hasSystemPath, Literal(current_path)))
            self.graph.add((uri, NAVIS.hasLevel, Literal(i, datatype=XSD.integer)))

            # 부모-자식 관계
            if parent_uri:
                self.graph.add((uri, NAVIS.hasSystemPathParent, parent_uri))
                self.graph.add((parent_uri, NAVIS.containsElement, uri))
                self.graph.add((uri, NAVIS.isContainedIn, parent_uri))

            self._path_node_cache[current_path] = uri
            parent_uri = uri

        return self._path_node_cache.get(system_path, parent_uri)

    def convert_hierarchy_csv(self, csv_path: str) -> Dict[str, Any]:
        """AllHierarchy CSV를 RDF로 변환한다.

        Args:
            csv_path: AllHierarchy CSV 파일 경로

        Returns:
            변환 결과 통계
        """
        logger.info(f"Converting hierarchy CSV: {csv_path}")

        stats = {
            "total_rows": 0,
            "unique_objects": 0,
            "sp3d_entities": 0,
            "groups": 0,
            "path_nodes": 0,
            "triples_added": 0,
            "property_values": 0,  # Property-Value 노드 수
            "max_level": 0,  # 최대 계층 깊이
            "categories": {},
        }

        # 1단계: 모든 행을 읽어 객체별로 그룹화
        objects: Dict[str, Dict] = {}

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                stats["total_rows"] += 1

                obj_id = row.get("ObjectId", "").strip()
                if not obj_id or obj_id == "00000000-0000-0000-0000-000000000000":
                    continue

                if obj_id not in objects:
                    objects[obj_id] = {
                        "parent_id": row.get("ParentId", "").strip(),
                        "level": row.get("Level", "0"),
                        "display_name": row.get("DisplayName", ""),
                        "properties": {},
                        "sp3d_properties": {},
                        "all_properties": [],  # 모든 속성 저장 (Property-Value 패턴용)
                        "internal_type": "",
                    }

                category = row.get("Category", "")
                prop_name = row.get("PropertyName", "")
                raw_value = row.get("RawValue", "")
                data_type = row.get("DataType", "")
                unit = row.get("Unit", "")

                # 항목 카테고리에서 내부 타입 추출
                if category == "항목" and prop_name == "내부 유형":
                    objects[obj_id]["internal_type"] = raw_value

                # SmartPlant 3D 속성 수집 (기존 호환성 유지)
                if category == "SmartPlant 3D":
                    objects[obj_id]["sp3d_properties"][prop_name] = raw_value

                # 기타 속성 (항목 제외)
                elif category not in ["항목", "재질", "형상"]:
                    if category not in objects[obj_id]["properties"]:
                        objects[obj_id]["properties"][category] = {}
                    objects[obj_id]["properties"][category][prop_name] = raw_value

                # 모든 속성을 Property-Value 패턴으로 저장 (RawValue가 있는 경우만)
                if raw_value:
                    objects[obj_id]["all_properties"].append({
                        "category": category,
                        "name": prop_name,
                        "raw_value": raw_value,
                        "data_type": data_type,
                        "unit": unit,
                    })

        stats["unique_objects"] = len(objects)
        logger.info(f"Found {len(objects)} unique objects")

        # 2단계: RDF 트리플 생성
        initial_triples = len(self.graph)

        for obj_id, obj_data in objects.items():
            uri = self._get_or_create_element(obj_id, obj_data["display_name"])

            # 타입 결정
            internal_type = obj_data["internal_type"]
            if "SP3D" in internal_type:
                self.graph.add((uri, RDF.type, NAVIS.SP3DEntity))
                self.graph.add((uri, RDF.type, BIM.PhysicalElement))
                stats["sp3d_entities"] += 1
            elif "Group" in internal_type or "그룹" in internal_type:
                self.graph.add((uri, RDF.type, NAVIS.NavisGroup))
                stats["groups"] += 1
            else:
                self.graph.add((uri, RDF.type, NAVIS.NavisElement))

            # 기본 속성
            self.graph.add((uri, NAVIS.hasObjectId, Literal(obj_id)))
            self.graph.add((uri, BIM.hasName, Literal(obj_data["display_name"])))
            self.graph.add((uri, RDFS.label, Literal(obj_data["display_name"])))
            level = int(obj_data["level"])
            self.graph.add((uri, NAVIS.hasLevel, Literal(level, datatype=XSD.integer)))

            # 최대 레벨 추적
            if level > stats["max_level"]:
                stats["max_level"] = level

            if obj_data["internal_type"]:
                self.graph.add((uri, NAVIS.hasInternalType, Literal(obj_data["internal_type"])))

            # 카테고리 분류
            category_uri = self._classify_element(obj_data["display_name"], internal_type)
            self.graph.add((uri, BIM.hasCategory, Literal(category_uri.split("#")[-1])))
            self.graph.add((uri, RDF.type, category_uri))

            cat_name = str(category_uri).split("#")[-1]
            stats["categories"][cat_name] = stats["categories"].get(cat_name, 0) + 1

            # 부모-자식 관계
            parent_id = obj_data["parent_id"]
            if parent_id and parent_id != "00000000-0000-0000-0000-000000000000":
                parent_uri = self._get_or_create_element(parent_id, "")
                self.graph.add((uri, NAVIS.hasParent, parent_uri))
                self.graph.add((parent_uri, NAVIS.hasChild, uri))
                self.graph.add((uri, NAVIS.hasParentId, Literal(parent_id)))

            # SmartPlant 3D 속성 (기존 방식 - 호환성)
            for prop_name, prop_value in obj_data["sp3d_properties"].items():
                if prop_name in self.SP3D_PROPERTY_MAP and prop_value:
                    prop_uri, datatype = self.SP3D_PROPERTY_MAP[prop_name]
                    self.graph.add((uri, prop_uri, Literal(prop_value, datatype=datatype)))

            # 모든 속성을 Property-Value 패턴으로 저장 (동적 조회 지원)
            for idx, prop_data in enumerate(obj_data.get("all_properties", [])):
                # PropertyValue 노드 URI 생성
                prop_node_id = f"{obj_id}_{idx}".replace("-", "_")
                prop_node = INST[f"prop_{prop_node_id}"]

                self.graph.add((prop_node, RDF.type, PROP.PropertyValue))
                self.graph.add((uri, PROP.hasProperty, prop_node))
                self.graph.add((prop_node, PROP.category, Literal(prop_data["category"])))
                self.graph.add((prop_node, PROP.propertyName, Literal(prop_data["name"])))
                self.graph.add((prop_node, PROP.rawValue, Literal(prop_data["raw_value"])))

                if prop_data["data_type"]:
                    self.graph.add((prop_node, PROP.dataType, Literal(prop_data["data_type"])))
                if prop_data["unit"]:
                    self.graph.add((prop_node, PROP.unit, Literal(prop_data["unit"])))

                stats["property_values"] += 1

            # System Path 기반 계층 연결 + 카운트
            system_path = obj_data["sp3d_properties"].get("System Path", "")
            if system_path:
                path_node = self._get_or_create_path_node(system_path)
                if path_node:
                    self.graph.add((uri, NAVIS.isContainedIn, path_node))
                    self.graph.add((path_node, NAVIS.containsElement, uri))

                    # 해당 경로와 모든 상위 경로의 요소 수 증가
                    parts = system_path.split("\\")
                    for i in range(len(parts)):
                        ancestor_path = "\\".join(parts[: i + 1])
                        self._path_element_counts[ancestor_path] = (
                            self._path_element_counts.get(ancestor_path, 0) + 1
                        )

        # 계층 노드에 미리 계산된 요소 수 추가 (System Path 기반)
        for path, count in self._path_element_counts.items():
            if path in self._path_node_cache:
                node_uri = self._path_node_cache[path]
                self.graph.add((node_uri, NAVIS.hasElementCount, Literal(count, datatype=XSD.integer)))

        # 3단계: ParentId 기반 자식/자손 수 계산
        logger.info("Computing child and descendant counts...")
        self._compute_hierarchy_counts(objects)

        # 각 노드에 자식 수와 자손 수 추가
        for obj_id, child_count in self._child_counts.items():
            if obj_id in self._object_cache:
                uri = self._object_cache[obj_id]
                self.graph.add((uri, NAVIS.hasChildCount, Literal(child_count, datatype=XSD.integer)))

        for obj_id, desc_count in self._descendant_counts.items():
            if obj_id in self._object_cache:
                uri = self._object_cache[obj_id]
                self.graph.add((uri, NAVIS.hasDescendantCount, Literal(desc_count, datatype=XSD.integer)))

        # 계층 노드 통계
        stats["path_nodes"] = len(self._path_node_cache)
        stats["hierarchy_nodes"] = sum(1 for c in self._child_counts.values() if c > 0)
        stats["triples_added"] = len(self.graph) - initial_triples

        # 그래프 메타데이터에 최대 깊이 저장
        graph_uri = URIRef("http://example.org/bim-ontology/graph#metadata")
        self.graph.add((graph_uri, RDF.type, OWL.NamedIndividual))
        self.graph.add((graph_uri, NAVIS.maxHierarchyLevel, Literal(stats["max_level"], datatype=XSD.integer)))
        self.graph.add((graph_uri, NAVIS.totalObjects, Literal(stats["unique_objects"], datatype=XSD.integer)))
        self.graph.add((graph_uri, NAVIS.totalPropertyValues, Literal(stats["property_values"], datatype=XSD.integer)))

        logger.info(f"Added {stats['triples_added']} triples, {stats['path_nodes']} path nodes")
        logger.info(f"Max hierarchy level: {stats['max_level']}, Property values: {stats['property_values']}")

        return stats

    def _compute_hierarchy_counts(self, objects: Dict[str, Dict]):
        """ParentId 기반으로 자식 수와 자손 수를 계산한다."""
        from collections import defaultdict

        # 부모별 자식 목록 생성
        children_map: Dict[str, List[str]] = defaultdict(list)
        null_parent = "00000000-0000-0000-0000-000000000000"

        for obj_id, obj_data in objects.items():
            parent_id = obj_data["parent_id"]
            if parent_id and parent_id != null_parent:
                children_map[parent_id].append(obj_id)

        # 직접 자식 수 계산
        for parent_id, children in children_map.items():
            self._child_counts[parent_id] = len(children)

        # 자손 수 계산 (재귀적으로 모든 하위 노드 카운트)
        def count_descendants(obj_id: str) -> int:
            if obj_id in self._descendant_counts:
                return self._descendant_counts[obj_id]

            children = children_map.get(obj_id, [])
            total = len(children)
            for child_id in children:
                total += count_descendants(child_id)

            self._descendant_counts[obj_id] = total
            return total

        # 모든 부모 노드에 대해 자손 수 계산
        for parent_id in children_map.keys():
            if parent_id not in self._descendant_counts:
                count_descendants(parent_id)

    def convert_unified_csv(self, csv_path: str) -> Dict[str, Any]:
        """UnifiedExport CSV (v2 포맷)를 RDF로 변환한다.

        오브젝트당 1행, PropertiesJson에 모든 속성이 JSON 배열로 포함되어 있고,
        BBox/Centroid/Volume 컬럼으로 기하 정보가 통합된 포맷.

        Args:
            csv_path: UnifiedExport CSV 파일 경로

        Returns:
            변환 결과 통계
        """
        logger.info(f"Converting unified CSV: {csv_path}")

        stats = {
            "total_rows": 0,
            "unique_objects": 0,
            "sp3d_entities": 0,
            "groups": 0,
            "path_nodes": 0,
            "triples_added": 0,
            "property_values": 0,
            "max_level": 0,
            "categories": {},
            "bbox_count": 0,
            "format": "unified_v2",
        }

        objects: Dict[str, Dict] = {}
        initial_triples = len(self.graph)

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                stats["total_rows"] += 1

                obj_id = row.get("ObjectId", "").strip()
                if not obj_id or obj_id == "00000000-0000-0000-0000-000000000000":
                    continue

                display_name = row.get("DisplayName", "")
                parent_id = row.get("ParentId", "").strip()
                level = int(row.get("Level", "0"))
                hierarchy_path = row.get("HierarchyPath", "")

                # PropertiesJson 파싱
                props_json_raw = row.get("PropertiesJson", "")
                props_list = []
                sp3d_properties = {}
                internal_type = ""

                if props_json_raw:
                    try:
                        props_list = json.loads(props_json_raw)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON for {obj_id}: {props_json_raw[:100]}")

                for p in props_list:
                    cat = p.get("category", "")
                    name = p.get("name", "")
                    raw_value = p.get("rawValue", "")

                    if cat == "항목" and name == "내부 유형":
                        internal_type = raw_value
                    if cat == "SmartPlant 3D":
                        sp3d_properties[name] = raw_value

                objects[obj_id] = {
                    "parent_id": parent_id,
                    "level": level,
                    "display_name": display_name,
                    "internal_type": internal_type,
                    "sp3d_properties": sp3d_properties,
                    "props_list": props_list,
                    "hierarchy_path": hierarchy_path,
                    # Geometry
                    "bbox_min_x": row.get("BBoxMinX", "").strip(),
                    "bbox_min_y": row.get("BBoxMinY", "").strip(),
                    "bbox_min_z": row.get("BBoxMinZ", "").strip(),
                    "bbox_max_x": row.get("BBoxMaxX", "").strip(),
                    "bbox_max_y": row.get("BBoxMaxY", "").strip(),
                    "bbox_max_z": row.get("BBoxMaxZ", "").strip(),
                    "centroid_x": row.get("CentroidX", "").strip(),
                    "centroid_y": row.get("CentroidY", "").strip(),
                    "centroid_z": row.get("CentroidZ", "").strip(),
                    "volume": row.get("BBoxVolume", "").strip(),
                    "has_mesh": row.get("HasMesh", "").strip().lower() == "true",
                    "mesh_uri": row.get("MeshUri", "").strip(),
                }

        stats["unique_objects"] = len(objects)
        logger.info(f"Found {len(objects)} unique objects from unified CSV")

        # RDF 트리플 생성
        for obj_id, obj_data in objects.items():
            uri = self._get_or_create_element(obj_id, obj_data["display_name"])
            level = obj_data["level"]

            # 타입 결정
            internal_type = obj_data["internal_type"]
            if "SP3D" in internal_type:
                self.graph.add((uri, RDF.type, NAVIS.SP3DEntity))
                self.graph.add((uri, RDF.type, BIM.PhysicalElement))
                stats["sp3d_entities"] += 1
            elif "Group" in internal_type or "그룹" in internal_type:
                self.graph.add((uri, RDF.type, NAVIS.NavisGroup))
                stats["groups"] += 1
            else:
                self.graph.add((uri, RDF.type, NAVIS.NavisElement))

            # 기본 속성
            self.graph.add((uri, NAVIS.hasObjectId, Literal(obj_id)))
            self.graph.add((uri, BIM.hasName, Literal(obj_data["display_name"])))
            self.graph.add((uri, RDFS.label, Literal(obj_data["display_name"])))
            self.graph.add((uri, NAVIS.hasLevel, Literal(level, datatype=XSD.integer)))

            if level > stats["max_level"]:
                stats["max_level"] = level

            if internal_type:
                self.graph.add((uri, NAVIS.hasInternalType, Literal(internal_type)))

            # HierarchyPath 저장
            if obj_data["hierarchy_path"]:
                self.graph.add((uri, NAVIS.hasHierarchyPath, Literal(obj_data["hierarchy_path"])))

            # 카테고리 분류
            category_uri = self._classify_element(obj_data["display_name"], internal_type)
            self.graph.add((uri, BIM.hasCategory, Literal(category_uri.split("#")[-1])))
            self.graph.add((uri, RDF.type, category_uri))

            cat_name = str(category_uri).split("#")[-1]
            stats["categories"][cat_name] = stats["categories"].get(cat_name, 0) + 1

            # 부모-자식 관계
            parent_id = obj_data["parent_id"]
            if parent_id and parent_id != "00000000-0000-0000-0000-000000000000":
                parent_uri = self._get_or_create_element(parent_id, "")
                self.graph.add((uri, NAVIS.hasParent, parent_uri))
                self.graph.add((parent_uri, NAVIS.hasChild, uri))
                self.graph.add((uri, NAVIS.hasParentId, Literal(parent_id)))

            # SmartPlant 3D 속성 (기존 방식 - 호환성)
            for prop_name, prop_value in obj_data["sp3d_properties"].items():
                if prop_name in self.SP3D_PROPERTY_MAP and prop_value:
                    prop_uri, datatype = self.SP3D_PROPERTY_MAP[prop_name]
                    self.graph.add((uri, prop_uri, Literal(prop_value, datatype=datatype)))

            # PropertyValue 패턴 (PropertiesJson의 모든 속성)
            for idx, p in enumerate(obj_data["props_list"]):
                raw_value = p.get("rawValue", "")
                if not raw_value:
                    continue

                prop_node_id = f"{obj_id}_{idx}".replace("-", "_")
                prop_node = INST[f"prop_{prop_node_id}"]

                self.graph.add((prop_node, RDF.type, PROP.PropertyValue))
                self.graph.add((uri, PROP.hasProperty, prop_node))
                self.graph.add((prop_node, PROP.category, Literal(p.get("category", ""))))
                self.graph.add((prop_node, PROP.propertyName, Literal(p.get("name", ""))))
                self.graph.add((prop_node, PROP.rawValue, Literal(raw_value)))

                data_type = p.get("dataType", "")
                if data_type:
                    self.graph.add((prop_node, PROP.dataType, Literal(data_type)))

                unit = p.get("unit", "")
                if unit:
                    self.graph.add((prop_node, PROP.unit, Literal(unit)))

                # numericValue (UnifiedExport에서 사전 파싱된 숫자값)
                numeric_val = p.get("numericValue")
                if numeric_val is not None:
                    self.graph.add((prop_node, PROP.numericValue,
                                    Literal(float(numeric_val), datatype=XSD.double)))

                stats["property_values"] += 1

            # Geometry (BoundingBox + Centroid + Volume)
            if obj_data["bbox_min_x"]:
                bbox_id = f"{obj_id}".replace("-", "_")
                bbox_node = INST[f"bbox_{bbox_id}"]

                self.graph.add((bbox_node, RDF.type, BSO.BoundingBox))
                self.graph.add((uri, BSO.hasBoundingBox, bbox_node))

                for attr, pred in [
                    ("bbox_min_x", BSO.minX), ("bbox_min_y", BSO.minY), ("bbox_min_z", BSO.minZ),
                    ("bbox_max_x", BSO.maxX), ("bbox_max_y", BSO.maxY), ("bbox_max_z", BSO.maxZ),
                    ("centroid_x", BSO.centroidX), ("centroid_y", BSO.centroidY), ("centroid_z", BSO.centroidZ),
                    ("volume", BSO.volume),
                ]:
                    val = self._parse_float_like(obj_data[attr])
                    if val is not None:
                        self.graph.add((bbox_node, pred, Literal(val, datatype=XSD.double)))

                if obj_data["has_mesh"]:
                    self.graph.add((bbox_node, BSO.hasMesh, Literal(True, datatype=XSD.boolean)))
                    if obj_data["mesh_uri"]:
                        self.graph.add((bbox_node, BSO.meshUri, Literal(obj_data["mesh_uri"])))

                stats["bbox_count"] += 1

            # System Path 기반 계층 연결
            system_path = obj_data["sp3d_properties"].get("System Path", "")
            if system_path:
                path_node = self._get_or_create_path_node(system_path)
                if path_node:
                    self.graph.add((uri, NAVIS.isContainedIn, path_node))
                    self.graph.add((path_node, NAVIS.containsElement, uri))

                    parts = system_path.split("\\")
                    for i in range(len(parts)):
                        ancestor_path = "\\".join(parts[: i + 1])
                        self._path_element_counts[ancestor_path] = (
                            self._path_element_counts.get(ancestor_path, 0) + 1
                        )

        # System Path 노드에 요소 수 추가
        for path, count in self._path_element_counts.items():
            if path in self._path_node_cache:
                node_uri = self._path_node_cache[path]
                self.graph.add((node_uri, NAVIS.hasElementCount, Literal(count, datatype=XSD.integer)))

        # ParentId 기반 자식/자손 수 계산
        logger.info("Computing child and descendant counts...")
        self._compute_hierarchy_counts(objects)

        for obj_id, child_count in self._child_counts.items():
            if obj_id in self._object_cache:
                uri = self._object_cache[obj_id]
                self.graph.add((uri, NAVIS.hasChildCount, Literal(child_count, datatype=XSD.integer)))

        for obj_id, desc_count in self._descendant_counts.items():
            if obj_id in self._object_cache:
                uri = self._object_cache[obj_id]
                self.graph.add((uri, NAVIS.hasDescendantCount, Literal(desc_count, datatype=XSD.integer)))

        # 통계
        stats["path_nodes"] = len(self._path_node_cache)
        stats["hierarchy_nodes"] = sum(1 for c in self._child_counts.values() if c > 0)
        stats["triples_added"] = len(self.graph) - initial_triples

        # 그래프 메타데이터
        graph_uri = URIRef("http://example.org/bim-ontology/graph#metadata")
        self.graph.add((graph_uri, RDF.type, OWL.NamedIndividual))
        self.graph.add((graph_uri, NAVIS.maxHierarchyLevel, Literal(stats["max_level"], datatype=XSD.integer)))
        self.graph.add((graph_uri, NAVIS.totalObjects, Literal(stats["unique_objects"], datatype=XSD.integer)))
        self.graph.add((graph_uri, NAVIS.totalPropertyValues, Literal(stats["property_values"], datatype=XSD.integer)))
        self.graph.add((graph_uri, BSO.totalBoundingBoxes, Literal(stats["bbox_count"], datatype=XSD.integer)))

        logger.info(f"Added {stats['triples_added']} triples, {stats['path_nodes']} path nodes")
        logger.info(f"Max level: {stats['max_level']}, Properties: {stats['property_values']}, BBoxes: {stats['bbox_count']}")

        return stats

    def convert_schedule_csv(self, csv_path: str) -> Dict[str, Any]:
        """Schedule CSV를 RDF로 변환한다.

        Args:
            csv_path: schedule CSV 파일 경로

        Returns:
            변환 결과 통계
        """
        logger.info(f"Converting schedule CSV: {csv_path}")

        stats = {
            "total_tasks": 0,
            "matched_elements": 0,
            "tasks_with_cost": 0,
            "tasks_with_duration": 0,
            "triples_added": 0,
        }

        initial_triples = len(self.graph)

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                sync_id = row.get("SyncID", "").strip()
                task_name = row.get("TaskName", "").strip()
                planned_start = row.get("PlannedStart", "").strip()
                planned_end = row.get("PlannedEnd", "").strip()
                task_type = row.get("TaskType", "").strip()
                parent_set = row.get("ParentSet", "").strip()
                progress = row.get("Progress", "0").strip()
                planned_duration_raw = row.get("PlannedDuration", "").strip()
                if not planned_duration_raw:
                    planned_duration_raw = row.get("Duration", "").strip()
                actual_duration_raw = row.get("ActualDuration", "").strip()
                cost_raw = row.get("Cost", "").strip() or row.get("UnitCost", "").strip()
                planned_duration_days = self._parse_int_like(planned_duration_raw)
                actual_duration_days = self._parse_int_like(actual_duration_raw)
                cost_value = self._parse_float_like(cost_raw)

                if not sync_id or not task_name:
                    continue

                stats["total_tasks"] += 1

                # Task URI 생성
                safe_id = sync_id.replace("-", "_")
                task_uri = INST[f"task_{safe_id}"]

                # Task 트리플 추가
                self.graph.add((task_uri, RDF.type, SCHED.ConstructionTask))
                self.graph.add((task_uri, RDFS.label, Literal(task_name)))
                self.graph.add((task_uri, SCHED.hasTaskName, Literal(task_name)))
                self.graph.add((task_uri, NAVIS.hasObjectId, Literal(sync_id)))

                if planned_start:
                    self.graph.add((task_uri, SCHED.hasPlannedStart, Literal(planned_start, datatype=XSD.date)))
                if planned_end:
                    self.graph.add((task_uri, SCHED.hasPlannedEnd, Literal(planned_end, datatype=XSD.date)))
                if task_type:
                    self.graph.add((task_uri, SCHED.hasTaskType, Literal(task_type)))
                if parent_set:
                    self.graph.add((task_uri, SCHED.hasParentSet, Literal(parent_set)))
                if progress:
                    try:
                        self.graph.add((task_uri, SCHED.hasProgress, Literal(float(progress), datatype=XSD.double)))
                    except ValueError:
                        logger.warning("Invalid progress value skipped: %s", progress)

                # Duration/Cost 확장 컬럼 주입
                if planned_duration_raw:
                    self.graph.add((task_uri, SCHED.hasDuration, Literal(planned_duration_raw, datatype=XSD.string)))
                    stats["tasks_with_duration"] += 1
                if planned_duration_days is not None:
                    self.graph.add((task_uri, SCHED.hasPlannedDuration, Literal(planned_duration_days, datatype=XSD.integer)))
                if actual_duration_days is not None:
                    self.graph.add((task_uri, SCHED.hasActualDuration, Literal(actual_duration_days, datatype=XSD.integer)))
                if cost_value is not None:
                    self.graph.add((task_uri, SCHED.hasCost, Literal(cost_value, datatype=XSD.double)))
                    stats["tasks_with_cost"] += 1

                # SyncID로 요소 매칭 (dxtnavis에서 SyncID는 ObjectId와 매칭될 수 있음)
                if sync_id in self._object_cache:
                    elem_uri = self._object_cache[sync_id]
                    self.graph.add((elem_uri, SCHED.assignedToTask, task_uri))
                    self.graph.add((task_uri, SCHED.hasAssignedElement, elem_uri))
                    if cost_value is not None:
                        self.graph.add((elem_uri, BIM.hasUnitCost, Literal(cost_value, datatype=XSD.double)))
                    consume_days = actual_duration_days if actual_duration_days is not None else planned_duration_days
                    if consume_days is not None:
                        self.graph.add((elem_uri, BIM.hasConsumeDuration, Literal(consume_days, datatype=XSD.integer)))
                    stats["matched_elements"] += 1

        stats["triples_added"] = len(self.graph) - initial_triples
        logger.info(f"Added {stats['triples_added']} task triples, {stats['matched_elements']} matched")

        return stats

    def save(self, output_path: str, format: str = "turtle") -> int:
        """RDF 그래프를 파일로 저장한다."""
        self.graph.serialize(destination=output_path, format=format)
        total = len(self.graph)
        logger.info(f"Saved {total} triples to {output_path}")
        return total

    def get_graph(self) -> Graph:
        """RDF 그래프를 반환한다."""
        return self.graph


def detect_csv_format(csv_path: str) -> str:
    """CSV 파일의 포맷을 자동 감지한다.

    Returns:
        "unified" (PropertiesJson 포함) 또는 "legacy" (플랫 컬럼)
    """
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        if "PropertiesJson" in header:
            return "unified"
        return "legacy"


def convert_navis_to_rdf(
    hierarchy_csv: str,
    schedule_csv: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """dxtnavis CSV 파일들을 RDF로 변환하는 편의 함수.

    CSV 포맷을 자동 감지하여 적절한 변환 메서드를 호출한다.
    - UnifiedExport (v2): PropertiesJson + BBox/Centroid/Volume
    - AllHierarchy (v1): 플랫 컬럼 (속성당 1행)

    Args:
        hierarchy_csv: AllHierarchy 또는 UnifiedExport CSV 파일 경로
        schedule_csv: Schedule CSV 파일 경로 (선택)
        output_path: 출력 TTL 파일 경로 (선택)

    Returns:
        변환 결과 통계
    """
    converter = NavisToRDFConverter()

    fmt = detect_csv_format(hierarchy_csv)
    logger.info(f"Detected CSV format: {fmt}")

    if fmt == "unified":
        result = {"hierarchy": converter.convert_unified_csv(hierarchy_csv)}
    else:
        result = {"hierarchy": converter.convert_hierarchy_csv(hierarchy_csv)}

    if schedule_csv and Path(schedule_csv).exists():
        result["schedule"] = converter.convert_schedule_csv(schedule_csv)

    if output_path:
        result["total_triples"] = converter.save(output_path)
    else:
        result["total_triples"] = len(converter.graph)

    return result


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python navis_to_rdf.py <hierarchy.csv> [schedule.csv] [output.ttl]")
        sys.exit(1)

    hierarchy_csv = sys.argv[1]
    schedule_csv = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else "navis_output.ttl"

    result = convert_navis_to_rdf(hierarchy_csv, schedule_csv, output_path)

    print("\n=== Conversion Results ===")
    h = result['hierarchy']
    print(f"Format: {h.get('format', 'legacy_v1')}")
    print(f"Total triples: {result['total_triples']}")
    print(f"Unique objects: {h['unique_objects']}")
    print(f"SP3D entities: {h['sp3d_entities']}")
    print(f"Groups: {h['groups']}")
    print(f"System Path nodes: {h.get('path_nodes', 0)}")
    print(f"Property values: {h.get('property_values', 0)}")
    print(f"Bounding Boxes: {h.get('bbox_count', 0)}")
    print(f"Max hierarchy level: {h.get('max_level', 0)}")
    print(f"\nCategories:")
    for cat, count in sorted(h['categories'].items(), key=lambda x: -x[1])[:15]:
        print(f"  {cat}: {count}")

    if "schedule" in result:
        print(f"\nSchedule tasks: {result['schedule']['total_tasks']}")
        print(f"Matched elements: {result['schedule']['matched_elements']}")
