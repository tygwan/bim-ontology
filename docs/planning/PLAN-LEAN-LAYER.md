# Lean Layer 구현 계획 (Phase 15-17)

## 현황 분석

### 현재 RDF에 존재하는 데이터 (nwd4op-12.ttl)

| 데이터 종류 | 소스 | RDF 속성 | 상태 |
|---|---|---|---|
| 공간 계층 | IfcProject/Site/Building/Storey | `bim:aggregates`, `bim:decomposes` | O 추출됨 |
| 층 표고 | IfcBuildingStorey.Elevation | `bim:hasElevation` (xsd:double) | O 추출됨 |
| 요소 식별 | IfcProduct.GlobalId | `bim:hasGlobalId` (xsd:string) | O 추출됨 |
| 요소 이름 | IfcProduct.Name | `bim:hasName`, `rdfs:label` | O 추출됨 |
| IFC 원본 타입 | entity.is_a() | `bim:hasOriginalType` | O 추출됨 |
| 29개 카테고리 분류 | 이름 패턴 매칭 | `bim:hasCategory`, `rdf:type bim:Pipe` 등 | O 추출됨 |
| 공간 포함 관계 | IfcRelContainedInSpatialStructure | `bim:containsElement` / `bim:isContainedIn` | O 추출됨 |
| PropertySet 값 | IfcRelDefinesByProperties | `bim:hasPropertySet` → `bim:hasProperty` → `bim:hasPropertyValue` | △ 스키마만 존재, 인스턴스 없음* |
| **수량 (Quantity)** | IfcQuantityArea/Length/Volume/Weight | - | X 미추출 |
| **재료 (Material)** | IfcMaterial/IfcMaterialLayer | - | X 미추출 |
| **분류 (Classification)** | IfcClassification/Reference | - | X 미추출 |
| **일정 (Schedule)** | IfcWorkSchedule/IfcTask | - | X IFC에 없음 |
| **비용 (Cost)** | IfcCostSchedule/IfcCostItem | - | X IFC에 없음 |
| **상태 (Status)** | - | - | X 없음 |
| **AWP (CWA/CWP/IWP)** | - | - | X 없음 |
| **장비 (Equipment specs)** | - | - | X 없음 |

> *PropertySet: `_convert_property_sets()` 로직은 존재하나, 현재 IFC 파일(Navisworks export)에 PropertySet 데이터가 없어 인스턴스가 0개.

### 핵심 기술적 판단 사항

1. **Schema Manager가 이미 CRUD를 지원** → Lean Layer 스키마를 `custom_schema.json`에 정의하면 `apply_schema_to_graph()`로 자동 적용 가능
2. **XSD_MAP에 "date" 미지원** → `xsd:date`, `xsd:dateTime` 타입 추가 필요
3. **PropertySet이 비어있음** → IFC 파일 자체에 Pset이 없는 것이므로, Quantity/Material 추출 전에 IFC 파일 내 존재 여부 확인 필요
4. **Schedule/Cost/AWP는 IFC에 없음** → 외부 데이터 주입(CSV/API/IfcOpenShell) 방식 필수

---

## Phase 15: IFC/RDF 데이터 감사 & 추출 확장

### 목표
현재 IFC에서 추출 가능한 모든 데이터를 파악하고, 누락된 Quantity/Material/Classification 추출을 구현한다.

### Dependencies
Phase 14 (완료)

### Task 15-1: IFC 파일 전수 조사 스크립트

**파일**: `scripts/audit_ifc.py` (신규)

ifcopenshell로 IFC 파일을 열어 모든 엔티티 타입, PropertySet 이름, Quantity 존재 여부, Material, Classification, Schedule/Cost 엔티티 유무를 리포트한다.

```python
# 핵심 조사 항목
audit_targets = {
    "PropertySets": "IfcPropertySet",           # Pset 이름 + 속성 목록
    "Quantities": "IfcElementQuantity",          # IfcQuantityArea/Length/Volume/Weight
    "Materials": "IfcMaterial",                  # 재료 정보
    "MaterialLayers": "IfcMaterialLayerSetUsage", # 레이어 구성
    "Classifications": "IfcClassification",       # 분류 체계
    "ClassificationRefs": "IfcClassificationReference",
    "Schedules": "IfcWorkSchedule",              # 일정 (존재 여부만)
    "Tasks": "IfcTask",                          # 작업 (존재 여부만)
    "CostSchedules": "IfcCostSchedule",          # 비용 (존재 여부만)
    "CostItems": "IfcCostItem",
    "RelAssignsToProcess": "IfcRelAssignsToProcess",  # 작업-요소 연결
    "RelSequence": "IfcRelSequence",             # 선후행 관계
}
```

**산출물**: `data/audit/ifc_audit_report.json` - 모든 엔티티 타입 카운트, PropertySet 목록, 존재/부재 현황

### Task 15-2: RDF 데이터 감사 SPARQL 쿼리셋

**파일**: `src/api/queries/audit_queries.py` (신규)

```sparql
# Q1: 전체 데이터 요약
SELECT (COUNT(?e) AS ?total)
       (COUNT(DISTINCT ?cat) AS ?categories)
       (COUNT(DISTINCT ?storey) AS ?storeys)
WHERE {
  ?e a bim:PhysicalElement .
  OPTIONAL { ?e bim:hasCategory ?cat }
  OPTIONAL { ?e bim:isContainedIn ?storey }
}

# Q2: 카테고리별 요소 수 + 속성 보유 현황
SELECT ?cat (COUNT(?e) AS ?count)
       (COUNT(?pset) AS ?withPropertySet)
WHERE {
  ?e a bim:PhysicalElement ;
     bim:hasCategory ?cat .
  OPTIONAL { ?e bim:hasPropertySet ?pset }
}
GROUP BY ?cat ORDER BY DESC(?count)

# Q3: PropertySet 이름별 속성 목록
SELECT ?psetName (COUNT(?prop) AS ?propCount)
       (GROUP_CONCAT(?propName; SEPARATOR=", ") AS ?properties)
WHERE {
  ?pset a bim:PropertySet ;
        bim:hasName ?psetName ;
        bim:hasProperty ?prop .
  ?prop bim:hasName ?propName .
}
GROUP BY ?psetName

# Q4: 요소별 보유 속성 완성도
SELECT ?e ?name ?cat
       (COUNT(?pset) AS ?psetCount)
       (BOUND(?desc) AS ?hasDescription)
       (BOUND(?tag) AS ?hasTag)
WHERE {
  ?e a bim:PhysicalElement ;
     bim:hasName ?name ;
     bim:hasCategory ?cat .
  OPTIONAL { ?e bim:hasDescription ?desc }
  OPTIONAL { ?e bim:hasTag ?tag }
  OPTIONAL { ?e bim:hasPropertySet ?pset }
}
GROUP BY ?e ?name ?cat ?desc ?tag
LIMIT 100

# Q5: 공간 계층 구조 전체
SELECT ?project ?site ?building ?storey ?storeyElev
       (COUNT(?elem) AS ?elemCount)
WHERE {
  ?project a bim:Project .
  ?project bim:aggregates ?site .
  ?site bim:aggregates ?building .
  ?building bim:aggregates ?storey .
  ?storey bim:hasElevation ?storeyElev .
  OPTIONAL { ?storey bim:containsElement ?elem }
}
GROUP BY ?project ?site ?building ?storey ?storeyElev
```

### Task 15-3: Quantity 추출 구현

**수정 파일**: `src/converter/ifc_to_rdf.py`

`_convert_property_sets()` 이후에 `_convert_quantities()` 메서드 추가:

```python
def _convert_quantities(self, parser: IFCParser):
    """IfcElementQuantity를 통한 수량 정보를 변환한다."""
    for rel in parser.get_entities("IfcRelDefinesByProperties"):
        qset = rel.RelatingPropertyDefinition
        if not qset.is_a("IfcElementQuantity"):
            continue
        # IfcQuantityArea → bim:hasArea (xsd:double)
        # IfcQuantityLength → bim:hasLength (xsd:double)
        # IfcQuantityVolume → bim:hasVolume (xsd:double)
        # IfcQuantityWeight → bim:hasWeight (xsd:double)
```

**추가 Data Properties**:
- `bim:hasArea` (domain: PhysicalElement, range: xsd:double)
- `bim:hasLength` (domain: PhysicalElement, range: xsd:double)
- `bim:hasVolume` (domain: PhysicalElement, range: xsd:double)
- `bim:hasWeight` (domain: PhysicalElement, range: xsd:double)

### Task 15-4: Material 추출 구현

**수정 파일**: `src/converter/ifc_to_rdf.py`

```python
def _convert_materials(self, parser: IFCParser):
    """IfcRelAssociatesMaterial을 통한 재료 정보를 변환한다."""
    # IfcMaterial → bim:Material 클래스
    # bim:hasMaterial (ObjectProperty: PhysicalElement → Material)
    # bim:hasMaterialName (DatatypeProperty: Material → xsd:string)
```

### Task 15-5: Classification 추출 구현

**수정 파일**: `src/converter/ifc_to_rdf.py`

```python
def _convert_classifications(self, parser: IFCParser):
    """IfcRelAssociatesClassification을 통한 분류 정보를 변환한다."""
    # IfcClassificationReference → bim:ClassificationReference
    # bim:hasClassification (ObjectProperty)
    # bim:hasClassificationName, bim:hasClassificationSystem
```

### Task 15-6: 감사 결과 Dashboard 탭 추가

**수정 파일**: `src/dashboard/index.html`, `src/dashboard/app.js`

Data Audit 탭 추가: 카테고리별 요소 수, PropertySet 현황, Quantity/Material/Classification 유무 시각화

### Deliverables
- `scripts/audit_ifc.py` (IFC 전수 조사)
- `src/api/queries/audit_queries.py` (감사 SPARQL 5종)
- `src/converter/ifc_to_rdf.py` (Quantity/Material/Classification 추출 추가)
- `data/audit/ifc_audit_report.json` (감사 결과)
- SHACL Shape 추가: `QuantityShape`, `MaterialShape`

### 검증 기준
- [  ] IFC 파일 내 모든 엔티티 타입이 리포트에 출력됨
- [  ] Quantity가 있는 경우 RDF에 `bim:hasArea/Length/Volume/Weight` 추출됨
- [  ] Material이 있는 경우 RDF에 `bim:hasMaterial` 관계 추출됨
- [  ] 감사 SPARQL 5종 모두 실행 가능
- [  ] 사용자의 실제 IFC 모델 객체 정보와 RDF 데이터 일치 확인

---

## Phase 16: Property 주입 PoC & Lean Layer 스키마 정의

### 목표
4가지 property 주입 방법을 PoC로 검증하고, Lean Layer(Schedule/Status/AWP/Equipment) 온톨로지 스키마를 정의한다.

### Dependencies
Phase 15

### Task 16-1: Property 주입 방법 A - IfcOpenShell 직접 삽입

**파일**: `scripts/poc_ifc_inject.py` (신규)

```python
import ifcopenshell
import ifcopenshell.api

model = ifcopenshell.open("data/ifc/nwd4op-12.ifc")
element = model.by_type("IfcBuildingElementProxy")[0]

# Custom PropertySet 추가
pset = ifcopenshell.api.run("pset.add_pset", model,
                             product=element,
                             name="EPset_Schedule")
ifcopenshell.api.run("pset.edit_pset", model, pset=pset,
                     properties={
                         "PlannedInstallDate": "2026-03-15",
                         "DeliveryStatus": "OnSite",
                         "CWP_ID": "CWP-A01-001",
                         "UnitCost": 1250.0
                     })
model.write("data/ifc/nwd4op-12_enriched.ifc")
# → RDF 재변환 후 PropertySet 추출 확인
```

**검증**: 추가된 PropertySet이 RDF 변환 시 `bim:hasPropertySet` → `bim:hasPropertyValue`로 나오는지 확인

### Task 16-2: Property 주입 방법 B - CSV → RDF 직접 삽입

**파일**: `src/converter/csv_to_rdf.py` (신규)

```python
class CSVToRDFInjector:
    """CSV 데이터를 RDF 그래프에 직접 주입한다.

    CSV 컬럼:
    - GlobalId: IFC 요소의 GlobalId (매핑 키)
    - PropertyName: 속성 이름
    - PropertyValue: 속성 값
    - PropertyType: 값 타입 (string/double/date)
    """

    def inject(self, graph: Graph, csv_path: str) -> int:
        """CSV를 읽어 기존 RDF 그래프에 트리플 추가.
        Returns: 추가된 트리플 수
        """
```

**테스트 CSV**: `data/test/schedule_sample.csv`
```csv
GlobalId,PlannedInstallDate,DeliveryStatus,CWP_ID,UnitCost
0$74$cMx2CMxs7R$fzekqT,2026-03-15,OnSite,CWP-A01-001,1250.0
0$8JtW$h2WTcCNy7lWZ4AS,2026-03-20,Delayed,CWP-A01-002,800.0
```

**검증**: 주입 후 SPARQL로 `bim:hasPlannedInstallDate` 등 조회 가능한지 확인

### Task 16-3: Property 주입 방법 C - Schema Manager API 활용

**파일**: `scripts/poc_schema_inject.py` (신규)

Schema Manager의 기존 CRUD로 Lean Layer 타입/속성/링크를 등록하고 `apply_schema_to_graph()`로 적용하는 PoC.

```python
mgr = OntologySchemaManager(graph)

# Custom Type
mgr.create_object_type("ConstructionTask", "BIMElement", "Construction Task")
mgr.create_object_type("WorkPackage", "BIMElement", "Work Package")

# Custom Property
mgr.create_property_type("hasPlannedStart", "ConstructionTask", "string")  # date 미지원 → string 우선
mgr.create_property_type("hasDeliveryStatus", "PhysicalElement", "string")

# Custom Link
mgr.create_link_type("assignedToTask", "PhysicalElement", "ConstructionTask",
                      inverse_name="hasAssignedElement")

triples_added = mgr.apply_schema_to_graph(graph)
```

**검증**: `custom_schema.json`에 정의 저장되고, 그래프에 OWL Class/Property 트리플 추가되는지 확인

### Task 16-4: 4가지 방법 비교 평가

**산출물**: `docs/PROPERTY-INJECTION-COMPARISON.md`

| 기준 | A: IfcOpenShell | B: CSV→RDF | C: Schema Manager | D: Dynamo* |
|------|----------------|------------|-------------------|-----------|
| 구현 난이도 | 중 | 하 | 하 | 상(외부 도구) |
| BIM 모델 반영 | O (IFC 수정) | X | X | O (Revit 수정) |
| Round-trip | O | X | X | O |
| 실시간 업데이트 | X (재변환 필요) | O (직접 주입) | O (API 호출) | X |
| 대량 데이터 | O | O | △ | △ |
| 현재 파이프라인 호환 | O (재변환) | O (그래프 합체) | O (네이티브) | X (별도 환경) |

*D: Dynamo는 Revit 환경이 필요하므로 코드 PoC 없이 문서 검토만 수행

### Task 16-5: Lean Layer 온톨로지 스키마 정의

**파일**: `data/ontology/lean_schema.ttl` (신규)

total-summary-kr 연구에 기반한 전체 Lean Layer 스키마:

```turtle
@prefix bim: <http://example.org/bim-ontology/schema#> .
@prefix opm: <http://www.w3id.org/opm#> .
@prefix awp: <http://example.org/bim-ontology/awp#> .
@prefix sched: <http://example.org/bim-ontology/schedule#> .

# ===== Schedule Ontology =====

sched:ConstructionTask a owl:Class ;
    rdfs:subClassOf bim:BIMElement ;
    rdfs:label "Construction Task" .

sched:WorkSchedule a owl:Class ;
    rdfs:label "Work Schedule" .

sched:hasPlannedStart a owl:DatatypeProperty ;
    rdfs:domain sched:ConstructionTask ;
    rdfs:range xsd:date .

sched:hasPlannedEnd a owl:DatatypeProperty ;
    rdfs:domain sched:ConstructionTask ;
    rdfs:range xsd:date .

sched:hasActualStart a owl:DatatypeProperty ;
    rdfs:domain sched:ConstructionTask ;
    rdfs:range xsd:date .

sched:hasActualEnd a owl:DatatypeProperty ;
    rdfs:domain sched:ConstructionTask ;
    rdfs:range xsd:date .

sched:hasDuration a owl:DatatypeProperty ;
    rdfs:domain sched:ConstructionTask ;
    rdfs:range xsd:duration .

sched:precedes a owl:ObjectProperty ;
    rdfs:domain sched:ConstructionTask ;
    rdfs:range sched:ConstructionTask .

sched:follows a owl:ObjectProperty ;
    owl:inverseOf sched:precedes .

sched:assignedToTask a owl:ObjectProperty ;
    rdfs:domain bim:PhysicalElement ;
    rdfs:range sched:ConstructionTask .

sched:hasAssignedElement a owl:ObjectProperty ;
    owl:inverseOf sched:assignedToTask .

# ===== Status / OPM Ontology =====

bim:ElementStatus a owl:Class ;
    rdfs:label "Element Status" .

bim:hasStatus a owl:ObjectProperty ;
    rdfs:domain bim:PhysicalElement ;
    rdfs:range bim:ElementStatus .

bim:hasStatusValue a owl:DatatypeProperty ;
    rdfs:domain bim:ElementStatus ;
    rdfs:range xsd:string .
    # Planned | Designed | Fabricated | Shipped | OnSite | Installed | Inspected

bim:hasStatusDate a owl:DatatypeProperty ;
    rdfs:domain bim:ElementStatus ;
    rdfs:range xsd:dateTime .

bim:hasDeliveryStatus a owl:DatatypeProperty ;
    rdfs:domain bim:PhysicalElement ;
    rdfs:range xsd:string .
    # Ordered | InProduction | Shipped | OnSite | Installed

bim:isReady a owl:DatatypeProperty ;
    rdfs:domain bim:PhysicalElement ;
    rdfs:range xsd:boolean .

# ===== AWP Ontology =====

awp:ConstructionWorkArea a owl:Class ;
    rdfs:subClassOf bim:SpatialElement ;
    rdfs:label "Construction Work Area (CWA)" .

awp:ConstructionWorkPackage a owl:Class ;
    rdfs:label "Construction Work Package (CWP)" .

awp:InstallationWorkPackage a owl:Class ;
    rdfs:label "Installation Work Package (IWP)" .

awp:belongsToCWA a owl:ObjectProperty ;
    rdfs:domain awp:ConstructionWorkPackage ;
    rdfs:range awp:ConstructionWorkArea .

awp:belongsToCWP a owl:ObjectProperty ;
    rdfs:domain awp:InstallationWorkPackage ;
    rdfs:range awp:ConstructionWorkPackage .

awp:includesElement a owl:ObjectProperty ;
    rdfs:domain awp:InstallationWorkPackage ;
    rdfs:range bim:PhysicalElement .

awp:assignedToIWP a owl:ObjectProperty ;
    rdfs:domain bim:PhysicalElement ;
    rdfs:range awp:InstallationWorkPackage ;
    owl:inverseOf awp:includesElement .

awp:hasStartDate a owl:DatatypeProperty ;
    rdfs:domain awp:InstallationWorkPackage ;
    rdfs:range xsd:date .

awp:hasEndDate a owl:DatatypeProperty ;
    rdfs:domain awp:InstallationWorkPackage ;
    rdfs:range xsd:date .

awp:hasConstraintStatus a owl:DatatypeProperty ;
    rdfs:domain awp:InstallationWorkPackage ;
    rdfs:range xsd:string .
    # AllCleared | PendingMaterial | PendingApproval | PendingPredecessor

awp:dependsOn a owl:ObjectProperty ;
    rdfs:domain awp:InstallationWorkPackage ;
    rdfs:range awp:InstallationWorkPackage .

# ===== Equipment Ontology =====

bim:ConstructionEquipment a owl:Class ;
    rdfs:label "Construction Equipment" .

bim:hasEquipmentWidth a owl:DatatypeProperty ;
    rdfs:domain bim:ConstructionEquipment ;
    rdfs:range xsd:double .

bim:hasEquipmentHeight a owl:DatatypeProperty ;
    rdfs:domain bim:ConstructionEquipment ;
    rdfs:range xsd:double .

bim:hasTurningRadius a owl:DatatypeProperty ;
    rdfs:domain bim:ConstructionEquipment ;
    rdfs:range xsd:double .

bim:hasBoomLength a owl:DatatypeProperty ;
    rdfs:domain bim:ConstructionEquipment ;
    rdfs:range xsd:double .

bim:hasLoadCapacity a owl:DatatypeProperty ;
    rdfs:domain bim:ConstructionEquipment ;
    rdfs:range xsd:double .

bim:canAccessZone a owl:ObjectProperty ;
    rdfs:domain bim:ConstructionEquipment ;
    rdfs:range awp:ConstructionWorkArea .
```

### Task 16-6: Schema Manager 확장 - date/dateTime 타입 지원

**수정 파일**: `src/ontology/schema_manager.py`

```python
XSD_MAP = {
    "string": XSD.string,
    "double": XSD.double,
    "integer": XSD.integer,
    "boolean": XSD.boolean,
    "date": XSD.date,           # 추가
    "dateTime": XSD.dateTime,   # 추가
    "duration": XSD.duration,   # 추가
}
```

### Task 16-7: Lean Layer SHACL Shapes 정의

**수정 파일**: `data/ontology/shapes.ttl` 에 추가

```turtle
# ConstructionTask: 필수 일정
sched:TaskShape a sh:NodeShape ;
    sh:targetClass sched:ConstructionTask ;
    sh:property [
        sh:path sched:hasPlannedStart ;
        sh:datatype xsd:date ;
        sh:minCount 1 ;
    ] ;
    sh:property [
        sh:path sched:hasPlannedEnd ;
        sh:datatype xsd:date ;
        sh:minCount 1 ;
    ] .

# IWP: 필수 링크
awp:IWPShape a sh:NodeShape ;
    sh:targetClass awp:InstallationWorkPackage ;
    sh:property [
        sh:path awp:belongsToCWP ;
        sh:minCount 1 ;
    ] ;
    sh:property [
        sh:path awp:hasStartDate ;
        sh:datatype xsd:date ;
        sh:minCount 1 ;
    ] .

# Element Status: 유효값 검증
bim:StatusValueShape a sh:NodeShape ;
    sh:targetClass bim:ElementStatus ;
    sh:property [
        sh:path bim:hasStatusValue ;
        sh:in ("Planned" "Designed" "Fabricated" "Shipped" "OnSite" "Installed" "Inspected") ;
    ] .
```

### Deliverables
- `scripts/poc_ifc_inject.py` (방법 A PoC)
- `src/converter/csv_to_rdf.py` (방법 B 구현)
- `scripts/poc_schema_inject.py` (방법 C PoC)
- `data/ontology/lean_schema.ttl` (Lean Layer 전체 스키마)
- `data/test/schedule_sample.csv` (테스트 데이터)
- `docs/PROPERTY-INJECTION-COMPARISON.md` (4가지 방법 비교서)
- `src/ontology/schema_manager.py` (date/dateTime 타입 추가)
- `data/ontology/shapes.ttl` (Lean Layer SHACL 추가)

### 검증 기준
- [  ] 방법 A: IFC에 PropertySet 추가 → RDF 재변환 → SPARQL 조회 성공
- [  ] 방법 B: CSV 주입 → 그래프에 트리플 추가 → SPARQL 조회 성공
- [  ] 방법 C: Schema Manager로 타입/속성 등록 → 그래프 적용 성공
- [  ] lean_schema.ttl이 rdflib로 파싱 가능
- [  ] SHACL shapes가 pyshacl로 검증 가능
- [  ] 4가지 방법 비교 문서 완성

---

## Phase 17: Lean Layer 통합 구현 & 쿼리 엔진

### 목표
Phase 16에서 검증된 방법으로 Lean Layer를 파이프라인에 통합하고, 3가지 컨셉(Semantic EPC / 시공성 검증 / 오늘 할 일)을 위한 SPARQL 쿼리와 추론 규칙을 구현한다.

### Dependencies
Phase 16

### Task 17-1: Lean Layer Injector 통합 모듈

**파일**: `src/converter/lean_layer_injector.py` (신규)

```python
class LeanLayerInjector:
    """Lean Layer 데이터를 RDF 그래프에 주입하는 통합 모듈.

    지원 소스:
    - CSV/Excel (schedule, status, AWP, equipment)
    - IfcOpenShell (IFC PropertySet 확장)
    - Schema Manager (스키마 정의)
    - API (실시간 상태 업데이트)
    """

    def __init__(self, graph: Graph):
        self.graph = graph

    def load_lean_schema(self, schema_path: str):
        """lean_schema.ttl 로딩 및 그래프 병합."""

    def inject_schedule_csv(self, csv_path: str) -> int:
        """일정 CSV → ConstructionTask + 요소 연결."""

    def inject_awp_csv(self, csv_path: str) -> int:
        """AWP CSV → CWA/CWP/IWP 계층 + 요소 연결."""

    def inject_status_csv(self, csv_path: str) -> int:
        """상태 CSV → ElementStatus + 요소 연결."""

    def inject_equipment_csv(self, csv_path: str) -> int:
        """장비 CSV → ConstructionEquipment 인스턴스."""

    def update_element_status(self, global_id: str, status: str, date: str):
        """단일 요소 상태 업데이트 (API용)."""
```

### Task 17-2: 컨셉별 SPARQL 쿼리 템플릿

**수정 파일**: `src/api/queries/templates.py` 에 추가

```python
# 컨셉 1: Semantic EPC - 지연 부재 조회
GET_DELAYED_ELEMENTS = """
SELECT ?element ?name ?category ?plannedDate ?status ?cwp
WHERE {
    ?element a bim:PhysicalElement ;
             bim:hasName ?name ;
             bim:hasCategory ?category .
    ?element sched:assignedToTask ?task .
    ?task sched:hasPlannedStart ?plannedDate .
    ?element bim:hasDeliveryStatus ?status .
    OPTIONAL { ?element awp:assignedToIWP/awp:belongsToCWP ?cwp }
    FILTER (?plannedDate <= NOW() && ?status != "Installed")
}
ORDER BY ?plannedDate
"""

# 컨셉 1: 오늘 Ready 상태 아닌 부재
GET_NOT_READY_TODAY = """
SELECT ?element ?name ?status ?plannedDate
WHERE {
    ?element a bim:PhysicalElement ;
             bim:hasName ?name ;
             bim:hasDeliveryStatus ?status .
    ?element sched:assignedToTask ?task .
    ?task sched:hasPlannedStart ?plannedDate .
    FILTER (?plannedDate <= "$TODAY"^^xsd:date)
    FILTER (?status NOT IN ("OnSite", "Installed"))
}
"""

# 컨셉 2: 장비 진입 가능 구역 (기둥간격 기반)
GET_EQUIPMENT_ACCESS = """
SELECT ?equipment ?zone ?eqWidth ?minSpacing
WHERE {
    ?equipment a bim:ConstructionEquipment ;
               bim:hasEquipmentWidth ?eqWidth .
    ?zone a awp:ConstructionWorkArea .
    ?zone bim:hasMinColumnSpacing ?minSpacing .
    FILTER (?eqWidth <= ?minSpacing)
}
"""

# 컨셉 3: 오늘 할 일 (AWP 기반)
GET_TODAY_WORK = """
SELECT ?iwp ?cwp ?cwa ?element ?name ?category ?status
WHERE {
    ?iwp a awp:InstallationWorkPackage ;
         awp:hasStartDate ?start ;
         awp:hasEndDate ?end ;
         awp:belongsToCWP ?cwp ;
         awp:includesElement ?element .
    ?cwp awp:belongsToCWA ?cwa .
    ?element bim:hasName ?name ;
             bim:hasCategory ?category .
    OPTIONAL { ?element bim:hasDeliveryStatus ?status }
    FILTER (?start <= "$TODAY"^^xsd:date && "$TODAY"^^xsd:date <= ?end)
}
ORDER BY ?cwa ?cwp ?iwp
"""

# 컨셉 3: IWP 제약 조건 확인
GET_IWP_CONSTRAINTS = """
SELECT ?iwp ?constraint ?predecessorIWP ?predStatus
WHERE {
    ?iwp a awp:InstallationWorkPackage ;
         awp:hasConstraintStatus ?constraint .
    OPTIONAL {
        ?iwp awp:dependsOn ?predecessorIWP .
        ?predecessorIWP awp:hasConstraintStatus ?predStatus .
    }
    FILTER (?constraint != "AllCleared")
}
"""
```

### Task 17-3: Lean Layer 추론 규칙 추가

**수정 파일**: `src/inference/reasoner.py`

```python
# Rule 8: 지연 부재 자동 감지
INFER_DELAYED = """
CONSTRUCT { ?elem bim:isDelayed true }
WHERE {
    ?elem sched:assignedToTask ?task .
    ?task sched:hasPlannedStart ?planned .
    ?elem bim:hasDeliveryStatus ?status .
    FILTER (?planned < NOW() && ?status NOT IN ("OnSite", "Installed"))
}
"""

# Rule 9: IWP 제약 자동 판단
INFER_IWP_READY = """
CONSTRUCT { ?iwp awp:isExecutable true }
WHERE {
    ?iwp a awp:InstallationWorkPackage ;
         awp:hasConstraintStatus "AllCleared" .
    FILTER NOT EXISTS {
        ?iwp awp:dependsOn ?pred .
        FILTER NOT EXISTS { ?pred awp:hasConstraintStatus "AllCleared" }
    }
}
"""

# Rule 10: 일일 과부하 감지
INFER_OVERLOADED_DAY = """
CONSTRUCT { ?date bim:isOverloaded true }
WHERE {
    SELECT ?date (COUNT(?task) AS ?taskCount)
    WHERE {
        ?task sched:hasPlannedStart ?date .
    }
    GROUP BY ?date
    HAVING (COUNT(?task) > 20)
}
"""
```

### Task 17-4: Namespace 확장

**수정 파일**: `src/converter/namespace_manager.py`

```python
# Lean Layer 네임스페이스 추가
SCHED = Namespace("http://example.org/bim-ontology/schedule#")
AWP = Namespace("http://example.org/bim-ontology/awp#")
OPM = Namespace("http://www.w3id.org/opm#")

# bind_namespaces()에 추가
graph.bind("sched", SCHED)
graph.bind("awp", AWP)
graph.bind("opm", OPM)
```

### Task 17-5: REST API 엔드포인트 추가

**파일**: `src/api/routes/lean_layer.py` (신규)

```python
# POST /api/lean/inject/schedule - 일정 CSV 주입
# POST /api/lean/inject/awp - AWP CSV 주입
# POST /api/lean/inject/status - 상태 CSV 주입
# POST /api/lean/inject/equipment - 장비 CSV 주입
# PUT  /api/lean/status/{global_id} - 단일 요소 상태 업데이트
# GET  /api/lean/today - 오늘 작업 조회
# GET  /api/lean/delayed - 지연 부재 조회
# GET  /api/lean/iwp/{iwp_id}/constraints - IWP 제약 확인
```

### Task 17-6: Dashboard Lean Layer 탭 추가

**수정 파일**: `src/dashboard/index.html`, `src/dashboard/app.js`

- Lean Layer 탭: CSV 업로드 UI + 주입 결과 표시
- Today's Work 탭: 오늘 작업 목록 + 카테고리별 그룹핑
- Status Monitor 탭: 지연 부재 리스트 + 상태별 통계 차트

### Deliverables
- `src/converter/lean_layer_injector.py` (통합 주입 모듈)
- `src/api/routes/lean_layer.py` (REST API)
- `src/api/queries/templates.py` (컨셉별 SPARQL 추가)
- `src/inference/reasoner.py` (추론 규칙 3개 추가)
- `src/converter/namespace_manager.py` (네임스페이스 확장)
- Dashboard Lean Layer/Today's Work/Status Monitor 탭

### 검증 기준
- [  ] CSV 주입 → SPARQL 조회 → 컨셉 1/2/3 쿼리 결과 정상
- [  ] 추론 규칙 실행 후 `bim:isDelayed`, `awp:isExecutable` 자동 추론
- [  ] REST API 엔드포인트 동작 확인
- [  ] Dashboard에서 오늘 작업 / 지연 부재 / 상태 모니터 시각화
- [  ] SHACL 검증 통과 (필수 속성, 유효값)

---

## Phase 간 의존성

```
Phase 15 (Data Audit)
    ↓ IFC 내 데이터 현황 파악
Phase 16 (PoC + Schema)
    ↓ 주입 방법 결정 + 스키마 확정
Phase 17 (통합 구현)
    ↓ 파이프라인 통합 + 쿼리/추론/API/Dashboard
```

## 기술적 실현 가능성 요약

| 항목 | 판단 | 근거 |
|------|------|------|
| Schema Manager로 Lean Layer 정의 | **가능** | CRUD 이미 구현, date 타입만 추가 |
| CSV → RDF 직접 주입 | **가능** | rdflib로 트리플 추가, GlobalId로 요소 매핑 |
| IFC에 PropertySet 추가 | **가능** | ifcopenshell.api.pset 검증 완료 (연구조사) |
| SHACL로 Lean Layer 검증 | **가능** | pyshacl 이미 통합, shape 추가만 필요 |
| SPARQL로 3가지 컨셉 쿼리 | **가능** | rdflib SPARQL 엔진 + 쿼리 캐시 존재 |
| CONSTRUCT 기반 추론 규칙 | **가능** | reasoner.py에 7개 규칙 이미 동작 중 |
| 기둥 간격/층고 자동 계산 | **제한적** | 기하 데이터 미포함 → 외부 계산 후 RDF 적재 필요 |
