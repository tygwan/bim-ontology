# Property Injection Methods: PoC Comparison

> Phase 16 결과물 - 2026-02-04

## Executive Summary

IFC/RDF 파이프라인에 Schedule, Status, AWP, Equipment 속성을 주입하기 위한 4가지 방법을 조사하고, 3가지를 PoC로 검증했다. **Method B (CSV to RDF)**를 주력 방법으로, **Method C (Schema Manager API)**를 보조 방법으로 추천한다.

---

## 1. Methods Overview

| Method | 접근 방식 | PoC 결과 | 구현 파일 |
|--------|-----------|----------|-----------|
| **A: IfcOpenShell** | IFC 파일에 PropertySet 직접 추가 -> RDF 재변환 | SUCCESS | `scripts/poc_ifc_inject.py` |
| **B: CSV to RDF** | CSV 데이터를 RDF 그래프에 직접 주입 | SUCCESS | `src/converter/csv_to_rdf.py` |
| **C: Schema Manager** | OWL 스키마를 API로 등록 + 인스턴스 주입 | SUCCESS | `scripts/poc_schema_inject.py` |
| **D: Dynamo** | Revit Dynamo로 IFC에 파라미터 추가 | 미검증 | N/A (Revit 필요) |

---

## 2. Detailed Results

### Method A: IfcOpenShell PropertySet Injection

**원리**: ifcopenshell.api로 IFC 파일의 요소에 `EPset_Schedule` PropertySet을 추가하고, 수정된 IFC를 다시 RDF로 변환한다.

**PoC 결과**:
- 5개 요소에 PropertySet 주입 성공
- PlannedInstallDate, DeliveryStatus, CWP_ID, UnitCost 4개 속성
- 20 SPARQL 결과 (5 요소 x 4 속성)
- round-trip 보존 (IFC -> RDF -> SPARQL 모두 가능)

**장점**:
- IFC 파일 자체에 데이터가 반영되므로 BIM 소프트웨어에서도 확인 가능
- IFC 스키마 규격 준수 (EPset_ prefix)
- round-trip fidelity 보장

**단점**:
- 234MB IFC 파일 전체 로딩/쓰기 필요 (메모리/시간 부담)
- IFC 재변환 필요 (39,375 트리플 재생성)
- 기존 PropertySet 구조에 의존 (Navisworks 내보내기 제한 영향)
- IFC 원본 변경 우려

**적합한 경우**: BIM 소프트웨어 연동이 필수인 경우, 납품용 IFC에 속성 포함 필요 시

---

### Method B: CSV to RDF Direct Injection

**원리**: CSV 파일의 GlobalId를 키로 RDF 그래프에서 기존 요소를 찾아 트리플을 직접 추가한다.

**PoC 결과**:
- Schedule CSV: 7개 요소 매칭, 28 트리플 추가, 1개 미발견 (의도적 테스트)
- AWP CSV: 2 CWA + 6 CWP + 6 IWP 인스턴스 생성, 80 트리플 추가
- 총 108 트리플 추가 (39,264 -> 39,372)
- SPARQL: DeliveryStatus 7개, IWP 6개, Element-IWP 링크 7개 모두 조회 성공

**장점**:
- 가장 빠르고 가벼움 (IFC 로딩 불필요)
- CSV는 비개발자도 Excel로 편집 가능
- GlobalId 기반 매칭으로 기존 요소와 확실히 연결
- AWP 계층 (CWA -> CWP -> IWP -> Element) 자동 구축
- 미발견 요소 리포트 제공

**단점**:
- IFC 원본에는 반영되지 않음 (RDF only)
- GlobalId가 반드시 CSV에 포함되어야 함
- CSV 형식 오류에 민감

**적합한 경우**: 외부 시스템(ERP, P6, SAP)에서 데이터를 가져올 때, 빠른 프로토타이핑

---

### Method C: Schema Manager API Injection

**원리**: OntologySchemaManager API로 OWL 클래스와 프로퍼티를 등록하고, 인스턴스 트리플을 프로그래밍 방식으로 추가한다.

**PoC 결과**:
- 2개 Object Type (ConstructionTask, IWP) 등록
- 5개 Property Type + 1개 Link Type 등록
- 25 schema 트리플 + 13 instance 트리플 추가
- SPARQL: Task 1개, Element 3개 속성 조회 성공
- date XSD 타입 지원 확인

**장점**:
- REST API를 통한 외부 시스템 연동 가능
- 동적 스키마 확장 (런타임에 새 타입/프로퍼티 추가)
- custom_schema.json에 영구 저장
- OWL 규격 준수 (rdfs:subClassOf, rdfs:domain, rdfs:range)

**단점**:
- 인스턴스 주입은 별도 코드 필요 (스키마만 관리)
- BIM 네임스페이스(bim:)에만 제한 (sched:/awp: 별도 처리 필요)
- 소량 데이터에 적합, 대량 주입은 Method B가 효율적

**적합한 경우**: 대시보드에서 사용자가 스키마를 동적으로 수정할 때, API 기반 워크플로우

---

### Method D: Dynamo (미검증)

**원리**: Revit Dynamo 스크립트로 BIM 모델에 직접 파라미터를 추가하고 IFC로 내보낸다.

**예상 장점**: BIM 원본에 직접 반영, 설계자 친화적 UI
**예상 단점**: Revit 라이선스 필수, Navisworks 파일은 직접 지원 불가, 자동화 어려움

---

## 3. Comparison Matrix

| 기준 | Method A | Method B | Method C | Method D |
|------|----------|----------|----------|----------|
| **구현 난이도** | 중 | 하 | 중 | 상 |
| **성능 (대량)** | 하 (IFC 전체 로딩) | 상 (직접 주입) | 중 | 하 |
| **IFC 반영** | O | X | X | O |
| **비개발자 접근** | X | O (CSV/Excel) | X | O (Dynamo) |
| **API 연동** | X | X | O | X |
| **AWP 계층 생성** | X (flat props만) | O (자동) | 가능 (수동) | X |
| **스키마 동적 확장** | X | X | O | X |
| **round-trip** | O | X | X | O |
| **데이터 소스** | IFC 속성 | CSV 파일 | API 호출 | Revit 모델 |
| **의존성** | ifcopenshell | rdflib | rdflib | Revit+Dynamo |

---

## 4. Recommendation

### Primary: Method B (CSV to RDF)

**이유**:
1. 현재 IFC 파일에 Schedule/AWP 데이터가 전혀 없음 -> 외부 주입 필수
2. CSV는 Excel/ERP/P6 등 모든 시스템에서 내보내기 가능
3. AWP 계층(CWA->CWP->IWP) 자동 구축 지원
4. GlobalId 기반 매칭으로 기존 BIM 요소와 정확히 연결
5. 가장 빠르고 메모리 효율적

### Secondary: Method C (Schema Manager API)

**이유**:
1. 대시보드에서 런타임 스키마 수정 지원
2. REST API로 외부 시스템 연동 가능
3. 소량 데이터 동적 주입에 적합

### Hybrid Strategy (Phase 17)

```
외부 데이터 (P6, ERP, Excel)
         |
    CSV Export
         |
    Method B: CSVToRDFInjector
         |
    RDF Graph + Lean Layer Schema (lean_schema.ttl)
         |
    Method C: Schema Manager (런타임 확장)
         |
    SPARQL Query Engine
         |
    Dashboard / API
```

---

## 5. Files Created in Phase 16

| File | Purpose |
|------|---------|
| `data/ontology/lean_schema.ttl` | Lean Layer OWL 온톨로지 (7 classes, 24 data props, 12 object props) |
| `data/ontology/shapes.ttl` | SHACL shapes 확장 (+4 Lean Layer shapes, 총 11개) |
| `src/converter/csv_to_rdf.py` | Method B 구현 (CSVToRDFInjector) |
| `src/ontology/schema_manager.py` | XSD_MAP 확장 (date/dateTime/duration) |
| `scripts/poc_ifc_inject.py` | Method A PoC |
| `scripts/poc_schema_inject.py` | Method C PoC |
| `data/test/schedule_sample.csv` | Schedule 테스트 데이터 (8 rows) |
| `data/test/awp_sample.csv` | AWP 테스트 데이터 (7 rows) |

---

## 6. Test Results Summary

```
Method A (IfcOpenShell):  SUCCESS - 5 elements, 20 properties in SPARQL
Method B (CSV to RDF):    SUCCESS - 7 matched, 108 triples, AWP hierarchy built
Method C (Schema Manager): SUCCESS - 25 schema + 13 instance triples, date XSD OK
All existing tests:       91 passed (no regressions)
```
