"""IFC 파일 파싱 모듈.

ifcopenshell을 사용하여 IFC4/IFC2X3 파일을 로딩하고
엔티티를 추출, 분류, 통계를 제공합니다.
"""

import logging
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import ifcopenshell

logger = logging.getLogger(__name__)

# Navisworks 내보내기에서 손실된 타입을 이름 패턴으로 복원하기 위한 분류 규칙
# 순서 중요: 구체적인 패턴이 범용 패턴보다 먼저 와야 함 (예: PipeFitting > Pipe)
CATEGORY_PATTERNS: dict[str, list[str]] = {
    # -- Smart3D Plant / Navisworks 특화 패턴 --
    "MemberSystem": [r"membersystem", r"member\s*system"],
    "Hanger": [r"hanger", r"spring\s*hanger", r"clamp"],
    "PipeFitting": [r"pipe\s*fitting", r"fitting", r"elbow", r"tee\b", r"reducer"],
    "Flange": [r"flange"],
    "ProcessUnit": [r"process\s*unit"],
    "Conduit": [r"conduit", r"wireway"],
    "Assembly": [r"assembly"],
    "Brace": [r"brace", r"bracing"],
    "GroutPad": [r"grout\s*pad", r"grout"],
    "Nozzle": [r"nozzle"],
    # -- 기본 구조/건축 패턴 (순서 재배치) --
    "Slab": [r"slab", r"floor"],
    "Wall": [r"wall", r"partition"],
    "Column": [r"column", r"pillar"],
    "Beam": [r"beam", r"girder", r"joist"],
    "Pipe": [r"pipe", r"piping"],          # PipeFitting 이후
    "Duct": [r"duct"],
    "CableTray": [r"cable\s*tray", r"cable"],
    "Insulation": [r"insulation"],
    "Valve": [r"valve"],
    "Pump": [r"pump"],
    "Equipment": [r"equipment", r"tank", r"vessel"],
    "Foundation": [r"foundation", r"footing"],
    "Railing": [r"railing", r"handrail"],
    "Stair": [r"stair"],
    "Support": [r"support"],               # Hanger 이후 (구체적 지지물 우선)
    "MemberPart": [r"memberpart"],
    "Structural": [r"structural"],
    "Aspect": [r"aspect"],
    "Geometry": [r"geometry"],
}

SUPPORTED_SCHEMAS = {"IFC4", "IFC2X3"}


class IFCParser:
    """IFC 파일 파싱 및 엔티티 추출 클래스."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._ifc_file: Optional[ifcopenshell.file] = None
        self._load_time: float = 0.0

    def open(self) -> "ifcopenshell.file":
        """IFC 파일을 로딩한다.

        Returns:
            ifcopenshell.file 객체

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ValueError: 지원하지 않는 IFC 스키마일 때
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"IFC 파일을 찾을 수 없습니다: {self.file_path}")

        start = time.time()
        self._ifc_file = ifcopenshell.open(str(self.file_path))
        self._load_time = time.time() - start

        schema = self.get_schema()
        if schema not in SUPPORTED_SCHEMAS:
            raise ValueError(
                f"지원하지 않는 스키마: {schema}. 지원 스키마: {SUPPORTED_SCHEMAS}"
            )

        logger.info(
            "IFC 파일 로딩 완료: %s (스키마=%s, %.1f초)",
            self.file_path.name,
            schema,
            self._load_time,
        )
        return self._ifc_file

    @property
    def ifc_file(self) -> "ifcopenshell.file":
        """로딩된 IFC 파일 객체를 반환한다."""
        if self._ifc_file is None:
            raise RuntimeError("IFC 파일이 로딩되지 않았습니다. open()을 먼저 호출하세요.")
        return self._ifc_file

    @property
    def load_time(self) -> float:
        """파일 로딩 소요 시간(초)."""
        return self._load_time

    def get_schema(self) -> str:
        """IFC 스키마 버전을 반환한다."""
        return self.ifc_file.schema

    def get_entities(self, entity_type: str) -> list:
        """특정 IFC 엔티티 타입의 인스턴스 목록을 반환한다.

        Args:
            entity_type: IFC 엔티티 타입명 (예: 'IfcWall', 'IfcBuildingElementProxy')

        Returns:
            해당 타입의 엔티티 리스트
        """
        return self.ifc_file.by_type(entity_type)

    def get_entity_count(self) -> int:
        """전체 엔티티 수를 반환한다."""
        return len(list(self.ifc_file))

    def get_type_counts(self) -> Counter:
        """엔티티 타입별 개수를 반환한다."""
        counter = Counter()
        for entity in self.ifc_file:
            counter[entity.is_a()] += 1
        return counter

    def get_spatial_structure(self) -> dict[str, Any]:
        """프로젝트 → 사이트 → 건물 → 층 공간 구조를 반환한다."""
        structure: dict[str, Any] = {
            "projects": [],
            "sites": [],
            "buildings": [],
            "storeys": [],
        }

        for project in self.get_entities("IfcProject"):
            structure["projects"].append({
                "global_id": project.GlobalId,
                "name": project.Name,
            })

        for site in self.get_entities("IfcSite"):
            structure["sites"].append({
                "global_id": site.GlobalId,
                "name": site.Name,
            })

        for building in self.get_entities("IfcBuilding"):
            structure["buildings"].append({
                "global_id": building.GlobalId,
                "name": building.Name,
            })

        for storey in self.get_entities("IfcBuildingStorey"):
            structure["storeys"].append({
                "global_id": storey.GlobalId,
                "name": storey.Name,
                "elevation": storey.Elevation,
            })

        return structure

    def get_element_summary(self) -> dict[str, int]:
        """물리적 요소를 이름 기반 분류하여 카테고리별 수를 반환한다.

        Navisworks 내보내기에서 모든 요소가 IfcBuildingElementProxy로
        변환되므로, 이름 패턴을 분석하여 원래 타입을 추정합니다.
        """
        counter = Counter()
        for proxy in self.get_entities("IfcBuildingElementProxy"):
            category = classify_element_name(proxy.Name)
            counter[category] += 1
        return dict(counter.most_common())

    def get_aggregation_relations(self) -> list[tuple[Any, Any]]:
        """IfcRelAggregates 관계를 (상위, 하위) 튜플 목록으로 반환한다."""
        relations = []
        for rel in self.get_entities("IfcRelAggregates"):
            for related in rel.RelatedObjects:
                relations.append((rel.RelatingObject, related))
        return relations

    def get_containment_relations(self) -> list[tuple[Any, Any]]:
        """IfcRelContainedInSpatialStructure 관계를 (공간, 요소) 튜플로 반환한다."""
        relations = []
        for rel in self.get_entities("IfcRelContainedInSpatialStructure"):
            for element in rel.RelatedElements:
                relations.append((rel.RelatingStructure, element))
        return relations

    def get_property_sets(self, element: Any) -> list[dict]:
        """특정 요소의 속성셋 목록을 반환한다."""
        psets = []
        for rel in self.get_entities("IfcRelDefinesByProperties"):
            if element in rel.RelatedObjects:
                pset_def = rel.RelatingPropertyDefinition
                if hasattr(pset_def, "HasProperties") and pset_def.HasProperties:
                    props = {}
                    for prop in pset_def.HasProperties:
                        val = getattr(prop, "NominalValue", None)
                        props[prop.Name] = val.wrappedValue if val else None
                    psets.append({"name": pset_def.Name, "properties": props})
        return psets

    def validate(self) -> dict[str, Any]:
        """IFC 파일 유효성 검증 결과를 반환한다."""
        schema = self.get_schema()
        entity_count = self.get_entity_count()
        type_counts = self.get_type_counts()

        has_project = len(self.get_entities("IfcProject")) > 0
        has_site = len(self.get_entities("IfcSite")) > 0
        has_building = len(self.get_entities("IfcBuilding")) > 0

        return {
            "valid": has_project and has_site and has_building,
            "schema": schema,
            "entity_count": entity_count,
            "unique_types": len(type_counts),
            "has_project": has_project,
            "has_site": has_site,
            "has_building": has_building,
            "file_size_mb": self.file_path.stat().st_size / (1024 * 1024),
            "load_time": self._load_time,
        }

    def __repr__(self) -> str:
        status = "loaded" if self._ifc_file else "not loaded"
        return f"IFCParser('{self.file_path.name}', {status})"


def classify_element_name(name: str | None) -> str:
    """요소 이름을 기반으로 BIM 카테고리를 추정한다."""
    if not name:
        return "Unknown"

    name_lower = name.lower()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, name_lower):
                return category
    return "Other"
