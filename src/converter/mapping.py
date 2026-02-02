"""IFC → ifcOWL RDF 매핑 룰 모듈.

IFC 엔티티 타입을 ifcOWL 클래스로, IFC 속성을 RDF 프로퍼티로 매핑합니다.
알려지지 않은 엔티티 타입도 동적으로 처리할 수 있습니다.
"""

from rdflib import Namespace, URIRef, Literal, XSD


# ---------- IFC 엔티티 → ifcOWL 클래스 매핑 ----------

# 공간 구조 (Spatial Structure)
SPATIAL_TYPES = {
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
}

# 구조 요소 (Structural Elements)
STRUCTURAL_TYPES = {
    "IfcWall",
    "IfcWallStandardCase",
    "IfcColumn",
    "IfcBeam",
    "IfcSlab",
    "IfcFooting",
    "IfcPile",
    "IfcRamp",
    "IfcRampFlight",
    "IfcStair",
    "IfcStairFlight",
    "IfcRoof",
    "IfcCurtainWall",
    "IfcPlate",
    "IfcMember",
}

# 개구부/마감 (Openings & Finishes)
OPENING_TYPES = {
    "IfcDoor",
    "IfcWindow",
    "IfcOpeningElement",
    "IfcCovering",
    "IfcRailing",
}

# MEP 요소 (Mechanical, Electrical, Plumbing)
MEP_TYPES = {
    "IfcPipeSegment",
    "IfcPipeFitting",
    "IfcDuctSegment",
    "IfcDuctFitting",
    "IfcCableCarrierSegment",
    "IfcCableSegment",
    "IfcFlowTerminal",
    "IfcFlowSegment",
    "IfcFlowFitting",
    "IfcFlowController",
    "IfcFlowMovingDevice",
    "IfcFlowStorageDevice",
    "IfcFlowTreatmentDevice",
    "IfcEnergyConversionDevice",
    "IfcDistributionPort",
    "IfcDistributionElement",
}

# 가구/장비 (Furnishing & Equipment)
FURNISHING_TYPES = {
    "IfcFurnishingElement",
    "IfcBuildingElementProxy",
    "IfcDiscreteAccessory",
    "IfcMechanicalFastener",
    "IfcFastener",
}

# 관계 (Relationships)
RELATIONSHIP_TYPES = {
    "IfcRelAggregates",
    "IfcRelContainedInSpatialStructure",
    "IfcRelDefinesByProperties",
    "IfcRelDefinesByType",
    "IfcRelAssociatesMaterial",
    "IfcRelAssociatesClassification",
    "IfcRelConnectsPathElements",
    "IfcRelFillsElement",
    "IfcRelVoidsElement",
    "IfcRelSpaceBoundary",
}

# 속성/자원 (Properties & Resources)
PROPERTY_TYPES = {
    "IfcPropertySet",
    "IfcPropertySingleValue",
    "IfcQuantityArea",
    "IfcQuantityLength",
    "IfcQuantityVolume",
    "IfcQuantityWeight",
    "IfcMaterial",
    "IfcMaterialLayer",
    "IfcMaterialLayerSet",
    "IfcMaterialLayerSetUsage",
    "IfcClassification",
    "IfcClassificationReference",
}

# 기하 형상 및 프레젠테이션 (Geometry & Presentation) - RDF 변환 스킵
GEOMETRY_TYPES = {
    "IfcCartesianPoint",
    "IfcCartesianPointList3D",
    "IfcDirection",
    "IfcAxis2Placement3D",
    "IfcLocalPlacement",
    "IfcShapeRepresentation",
    "IfcProductDefinitionShape",
    "IfcTriangulatedFaceSet",
    "IfcFacetedBrep",
    "IfcExtrudedAreaSolid",
    "IfcBooleanClippingResult",
    "IfcPolyLoop",
    "IfcFace",
    "IfcFaceBound",
    # 프레젠테이션/스타일 타입
    "IfcPresentationLayerAssignment",
    "IfcPresentationStyleAssignment",
    "IfcColourRgb",
    "IfcSurfaceStyle",
    "IfcSurfaceStyleRendering",
    "IfcStyledItem",
    # 기타 비-IfcRoot 타입
    "IfcSIUnit",
    "IfcOwnerHistory",
    "IfcOrganization",
    "IfcApplication",
    "IfcPerson",
    "IfcPersonAndOrganization",
    "IfcUnitAssignment",
    "IfcGeometricRepresentationContext",
    "IfcGeometricRepresentationSubContext",
    "IfcConversionBasedUnit",
    "IfcDimensionalExponents",
    "IfcMeasureWithUnit",
    "IfcConnectedFaceSet",
    "IfcClosedShell",
    "IfcFaceOuterBound",
}

# 전체 알려진 타입 집합
ALL_KNOWN_TYPES = (
    SPATIAL_TYPES
    | STRUCTURAL_TYPES
    | OPENING_TYPES
    | MEP_TYPES
    | FURNISHING_TYPES
    | RELATIONSHIP_TYPES
    | PROPERTY_TYPES
    | GEOMETRY_TYPES
)

# RDF 변환 대상 엔티티 타입 (기하 형상 제외)
CONVERTIBLE_TYPES = (
    SPATIAL_TYPES
    | STRUCTURAL_TYPES
    | OPENING_TYPES
    | MEP_TYPES
    | FURNISHING_TYPES
)


def get_entity_category(ifc_type: str) -> str:
    """IFC 엔티티 타입의 카테고리를 반환한다.

    알려지지 않은 타입은 'Unknown'을 반환합니다.
    """
    if ifc_type in SPATIAL_TYPES:
        return "Spatial"
    if ifc_type in STRUCTURAL_TYPES:
        return "Structural"
    if ifc_type in OPENING_TYPES:
        return "Opening"
    if ifc_type in MEP_TYPES:
        return "MEP"
    if ifc_type in FURNISHING_TYPES:
        return "Furnishing"
    if ifc_type in RELATIONSHIP_TYPES:
        return "Relationship"
    if ifc_type in PROPERTY_TYPES:
        return "Property"
    if ifc_type in GEOMETRY_TYPES:
        return "Geometry"
    return "Unknown"


def is_convertible(ifc_type: str) -> bool:
    """해당 IFC 타입이 RDF 변환 대상인지 확인한다.

    기하 형상, 관계, 속성 타입은 직접 변환하지 않고
    상위 엔티티의 속성으로 포함됩니다.
    알려지지 않은 타입은 변환 대상으로 포함합니다.
    """
    if ifc_type in GEOMETRY_TYPES:
        return False
    if ifc_type in RELATIONSHIP_TYPES:
        return False
    if ifc_type in PROPERTY_TYPES:
        return False
    return True


# ---------- IFC 속성 → RDF 데이터타입 매핑 ----------

IFC_TO_XSD_TYPE = {
    "IfcLabel": XSD.string,
    "IfcText": XSD.string,
    "IfcIdentifier": XSD.string,
    "IfcDescriptiveMeasure": XSD.string,
    "IfcReal": XSD.double,
    "IfcPositiveLengthMeasure": XSD.double,
    "IfcLengthMeasure": XSD.double,
    "IfcAreaMeasure": XSD.double,
    "IfcVolumeMeasure": XSD.double,
    "IfcMassMeasure": XSD.double,
    "IfcThermodynamicTemperatureMeasure": XSD.double,
    "IfcPressureMeasure": XSD.double,
    "IfcForceMeasure": XSD.double,
    "IfcPlaneAngleMeasure": XSD.double,
    "IfcInteger": XSD.integer,
    "IfcCountMeasure": XSD.integer,
    "IfcBoolean": XSD.boolean,
    "IfcLogical": XSD.boolean,
}


def map_ifc_value(ifc_value) -> Literal | None:
    """IFC 속성값을 RDF Literal로 변환한다.

    Args:
        ifc_value: ifcopenshell의 IfcPropertySingleValue.NominalValue

    Returns:
        RDF Literal 또는 None (변환 불가 시)
    """
    if ifc_value is None:
        return None

    ifc_type = ifc_value.is_a()
    wrapped = ifc_value.wrappedValue

    if wrapped is None:
        return None

    xsd_type = IFC_TO_XSD_TYPE.get(ifc_type)
    if xsd_type:
        return Literal(wrapped, datatype=xsd_type)

    # 알려지지 않은 타입은 문자열로 처리
    return Literal(str(wrapped), datatype=XSD.string)
