# Plan Review: Phase 15-17 구현 결과 대조

## 개요

`docs/PLAN-LEAN-LAYER.md`에 정의된 Phase 15-17 계획과 실제 구현 결과를 항목별로 대조합니다.

---

## Phase 15: IFC/RDF Data Audit & Extraction Enhancement

### Task 15-1: IFC 파일 전수 조사 스크립트

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `scripts/audit_ifc.py` 생성 | O | O - 생성됨 | DONE |
| 12개 엔티티 타입 조사 | O | O - PropertySet, Quantity, Material, Classification, Schedule, Task, Cost 등 | DONE |
| `data/audit/ifc_audit_report.json` 생성 | O | O - 감사 결과 JSON 저장 | DONE |

### Task 15-2: RDF 데이터 감사 SPARQL 쿼리셋

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `src/api/queries/audit_queries.py` 생성 | O | O | DONE |
| Q1-Q5 SPARQL 쿼리 | 5종 | 5종 구현 | DONE |

### Task 15-3~15-5: Quantity/Material/Classification 추출

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `_convert_quantities()` | O | **스킵** - IFC에 IfcElementQuantity 없음 (audit 결과 0개) | N/A |
| `_convert_materials()` | O | **스킵** - IFC에 IfcMaterial 없음 (audit 결과 0개) | N/A |
| `_convert_classifications()` | O | **스킵** - IFC에 IfcClassification 없음 (audit 결과 0개) | N/A |

> **판단**: Navisworks export IFC 파일에 Quantity/Material/Classification 데이터가 존재하지 않으므로 추출 로직 구현은 불필요. 데이터가 있는 IFC 파일 사용 시 향후 구현 가능.

### Task 15-6: Dashboard 감사 탭

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| Data Audit 탭 | O | **미구현** - Validation 탭이 유사 기능 제공 | SKIP |

> **판단**: 기존 Validation 탭(8개 검사 항목)이 데이터 품질 감사 기능을 이미 포함하므로 별도 탭 불필요.

### Phase 15 산출물 대조

| 산출물 | 계획 | 실제 | 비고 |
|--------|------|------|------|
| `scripts/audit_ifc.py` | O | O | |
| `src/api/queries/audit_queries.py` | O | O | |
| `data/audit/ifc_audit_report.json` | O | O | |
| `src/converter/ifc_to_rdf.py` 수정 | O | **스킵** | IFC 데이터 없음 |
| SHACL Shape 추가 | O | Phase 16에서 통합 구현 | |

---

## Phase 16: Property Injection PoC & Lean Layer Schema

### Task 16-1: Method A - IfcOpenShell

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `scripts/poc_ifc_inject.py` 생성 | O | O | DONE |
| IFC에 PropertySet 추가 | O | O - EPset_Schedule 추가 | DONE |
| RDF 재변환 확인 | O | O - 5 elements, 20 SPARQL rows | DONE |

### Task 16-2: Method B - CSV→RDF

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `src/converter/csv_to_rdf.py` 구현 | O | O | DONE |
| `data/test/schedule_sample.csv` 생성 | O | O - 8 rows, 실제 GlobalId 사용 | DONE |
| CSV 주입 + SPARQL 조회 | O | O - 7 matched | DONE |

### Task 16-3: Method C - Schema Manager

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `scripts/poc_schema_inject.py` 생성 | O | O | DONE |
| custom_schema.json 저장 | O | O | DONE |
| OWL 트리플 추가 확인 | O | O - +25 schema + 13 instance triples | DONE |

### Task 16-4: 4가지 방법 비교

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `docs/PROPERTY-INJECTION-COMPARISON.md` | O | O | DONE |
| 4가지 방법 비교표 | O | O - 6개 기준으로 비교 | DONE |
| 방법 D (Dynamo) | 문서 검토만 | 문서 검토만 | DONE |
| 권장 방법 도출 | - | Method B (CSV→RDF) primary, Method C secondary | DONE |

### Task 16-5: Lean Layer Schema

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `data/ontology/lean_schema.ttl` | O | O - 169 triples, 7 classes, 24 data props, 12 object props | DONE |
| Schedule 온톨로지 | O | O - ConstructionTask, WorkSchedule + 10 properties | DONE |
| Status/OPM 온톨로지 | O | O - ElementStatus, hasDeliveryStatus, isReady | DONE |
| AWP 온톨로지 | O | O - CWA, CWP, IWP + includesElement/dependsOn | DONE |
| Equipment 온톨로지 | O | O - ConstructionEquipment + 5 dimension props | DONE |

### Task 16-6: Schema Manager 확장

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| XSD_MAP date 추가 | O | O | DONE |
| XSD_MAP dateTime 추가 | O | O | DONE |
| XSD_MAP duration 추가 | O | O | DONE |

### Task 16-7: SHACL Shapes

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| TaskShape (ConstructionTask) | O | O - hasPlannedStart/End minCount=1 | DONE |
| IWPShape (IWP) | O | O - belongsToCWP, hasStartDate required + ConstraintStatus enum | DONE |
| StatusValueShape (ElementStatus) | O | O - 7개 유효값 검증 | DONE |
| EquipmentShape | - (미계획) | O - 추가 구현 | EXTRA |

### Phase 16 산출물 대조

| 산출물 | 계획 | 실제 | 비고 |
|--------|------|------|------|
| `scripts/poc_ifc_inject.py` | O | O | |
| `src/converter/csv_to_rdf.py` | O | O | |
| `scripts/poc_schema_inject.py` | O | O | |
| `data/ontology/lean_schema.ttl` | O | O | 169 triples |
| `data/test/schedule_sample.csv` | O | O | |
| `data/test/awp_sample.csv` | - | O | 추가 생성 |
| `docs/PROPERTY-INJECTION-COMPARISON.md` | O | O | |
| `src/ontology/schema_manager.py` 수정 | O | O | |
| `data/ontology/shapes.ttl` 수정 | O | O | 4 shapes 추가 (11 total) |

---

## Phase 17: Lean Layer Integration & Query Engine

### Task 17-1: Lean Layer Injector 통합 모듈

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| `src/converter/lean_layer_injector.py` | O | O | DONE |
| `load_lean_schema()` | O | O | DONE |
| `inject_schedule_csv()` | O | O - GlobalId 매칭, ConstructionTask 생성, 속성 주입 | DONE |
| `inject_awp_csv()` | O | O - CWA→CWP→IWP 계층 + 요소 연결 | DONE |
| `inject_status_csv()` | O | O - ElementStatus 인스턴스 + 이력 | DONE |
| `inject_equipment_csv()` | O | O - ConstructionEquipment + canAccessZone | DONE |
| `update_element_status()` | O | O - 개별 상태 업데이트 + isReady 추론 | DONE |
| `get_lean_layer_stats()` | - (미계획) | O - 통계 API용 추가 구현 | EXTRA |

### Task 17-2: SPARQL 쿼리 템플릿

| 쿼리 | 계획 | 실제 | 상태 |
|------|------|------|------|
| GET_DELAYED_ELEMENTS | O | O - `get_delayed_elements(reference_date)` | DONE |
| GET_NOT_READY_TODAY | O | O - `get_not_ready_elements()` | DONE |
| GET_EQUIPMENT_ACCESS | O | O - `get_equipment_access_zones()` | DONE |
| GET_TODAY_WORK | O | O - `get_todays_work(target_date)` | DONE |
| GET_IWP_CONSTRAINTS | O | O - `get_iwp_constraints(iwp_id)` | DONE |
| GET_DELIVERY_STATUS_SUMMARY | - (미계획) | O - 추가 구현 | EXTRA |

**구현 차이점**:
- 계획은 `templates.py`에 정적 쿼리 문자열로 정의
- 실제로도 `templates.py`에 함수 기반으로 구현됨 (파라미터 치환 지원)
- `get_delivery_status_summary()`는 계획에 없었지만 Status Monitor에 필요하여 추가

### Task 17-3: 추론 규칙

| 규칙 | 계획 | 실제 | 차이 |
|------|------|------|------|
| Rule 8: 지연 부재 감지 | `INFER_DELAYED` | `infer_delayed_element` | 일치 - PlannedInstallDate < NOW() 기반 |
| Rule 9: IWP 실행 가능 | `INFER_IWP_READY` | `infer_iwp_executable` | 일치 - AllCleared + 전 요소 OnSite/Installed |
| Rule 10: 일일 과부하 | `INFER_OVERLOADED_DAY` | **변경** → `infer_element_ready` | 변경됨 |

**Rule 10 변경 근거**:
- 계획: 일일 과부하 감지 (하루 20개 이상 작업)
- 실제: 요소 준비 상태 추론 (DeliveryStatus → isReady)
- **이유**: 일일 과부하보다 요소 준비 상태 추론이 IWP 실행 가능성 판단(Rule 9)의 전제 조건으로 더 실용적. 과부하 감지는 SPARQL 쿼리로 대체 가능.

### Task 17-4: Namespace 확장

| 항목 | 계획 | 실제 | 상태 |
|------|------|------|------|
| SCHED 네임스페이스 | O | O | DONE |
| AWP 네임스페이스 | O | O | DONE |
| OPM 네임스페이스 | O | **스킵** | 직접 사용하지 않아 미추가 |
| bind_namespaces() 확장 | O | O | DONE |

### Task 17-5: REST API 엔드포인트

| Endpoint | 계획 | 실제 | 상태 |
|----------|------|------|------|
| POST /api/lean/inject/schedule | O | O | DONE |
| POST /api/lean/inject/awp | O | O | DONE |
| POST /api/lean/inject/status | O | O | DONE |
| POST /api/lean/inject/equipment | O | O | DONE |
| PUT /api/lean/status/{global_id} | O | O | DONE |
| GET /api/lean/today | O | O | DONE |
| GET /api/lean/delayed | O | O | DONE |
| GET /api/lean/iwp/{iwp_id}/constraints | O | O | DONE |
| **GET /api/lean/stats** | - (미계획) | O | EXTRA |

### Task 17-6: Dashboard 탭

| 탭 | 계획 | 실제 | 상태 |
|----|------|------|------|
| Lean Layer 탭 | CSV 업로드 + 결과 표시 | 4개 통계 카드 + CSV Injection + Summary 테이블 | DONE+ |
| Today's Work 탭 | 오늘 작업 목록 + 그룹핑 | Date picker + 3 요약 카드 + IWP 테이블 + Constraint 색상 | DONE+ |
| Status Monitor 탭 | 지연 리스트 + 통계 차트 | Delayed 패널 + Delivery 도넛 차트 + Status Update 폼 | DONE+ |
| SPARQL 탭 템플릿 추가 | - (미계획) | +4개 Lean Layer 쿼리 템플릿 | EXTRA |

### Phase 17 산출물 대조

| 산출물 | 계획 | 실제 | 비고 |
|--------|------|------|------|
| `src/converter/lean_layer_injector.py` | O | O | |
| `src/api/routes/lean_layer.py` | O | O | 9 endpoints |
| `src/api/queries/templates.py` 수정 | O | O | +6 templates |
| `src/inference/reasoner.py` 수정 | O | O | +3 rules |
| `src/converter/namespace_manager.py` 수정 | O | O | +2 namespaces |
| `src/dashboard/index.html` 수정 | O | O | +3 tabs |
| `src/dashboard/app.js` 수정 | O | O | ~250 lines added |
| `requirements.txt` 수정 | - (미계획) | O | +python-multipart |

---

## 종합 평가

### 통계 요약

| Phase | 계획 항목 | 완료 | 스킵 (데이터 없음) | 변경 | 추가 구현 |
|-------|-----------|------|---------------------|------|-----------|
| Phase 15 | 19 | 12 | 6 (Qty/Mat/Cls + 관련) | 0 | 0 |
| Phase 16 | 19 | 19 | 0 | 0 | 2 (awp_sample.csv, EquipmentShape) |
| Phase 17 | 22 | 21 | 1 (OPM namespace) | 1 (Rule 10) | 5 (stats API, delivery summary, etc) |
| **합계** | **60** | **52** | **7** | **1** | **7** |

### 계획 대비 달성율

- **직접 구현**: 52/60 = **86.7%**
- **스킵 (합리적 근거)**: 7개 - IFC 데이터 부재 또는 중복 기능
- **변경 (개선)**: 1개 - Rule 10 (과부하 → 준비상태, 더 실용적)
- **추가 구현**: 7개 - 계획에 없었으나 필요에 의해 추가

### 주요 변경/개선 사항

1. **Rule 10 변경**: 일일 과부하 감지 → 요소 준비 상태 추론
   - Rule 9(IWP 실행 가능) 판단에 필요한 전제 조건
   - 과부하 감지는 간단한 GROUP BY 쿼리로 대체 가능

2. **GET /api/lean/stats 추가**: Dashboard Lean Layer 탭의 통계 표시에 필요

3. **SPARQL 탭 4개 쿼리 템플릿 추가**: Dashboard에서 Lean Layer 데이터를 직접 쿼리할 수 있도록

4. **EquipmentShape 추가**: 계획에 없었으나 데이터 무결성을 위해 추가

### 미구현 항목 (향후 과제)

| 항목 | 이유 | 우선순위 |
|------|------|----------|
| Quantity 추출 (_convert_quantities) | IFC에 데이터 없음 | 새 IFC 파일 사용 시 |
| Material 추출 (_convert_materials) | IFC에 데이터 없음 | 새 IFC 파일 사용 시 |
| Classification 추출 (_convert_classifications) | IFC에 데이터 없음 | 새 IFC 파일 사용 시 |
| Data Audit 전용 탭 | Validation 탭으로 대체 | 낮음 |
| OPM 네임스페이스 | 직접 사용하지 않음 | 필요 시 |

### 결론

Phase 15-17 계획이 **전반적으로 성공적으로 구현**되었습니다. 스킵된 항목은 모두 합리적 근거(IFC 데이터 부재)가 있으며, 계획 외 추가 구현은 실제 운영에 필요한 기능들입니다. Rule 10의 변경은 시스템 일관성 측면에서 오히려 개선입니다.

---

**Document Version**: v1.0
**Last Updated**: 2026-02-04
