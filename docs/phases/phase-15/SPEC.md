# Phase 15: IFC/RDF Data Audit & Property Extraction Enhancement - Specification

## Metadata

- **Phase**: Phase 15
- **Milestone**: M16 - Data Audit
- **Status**: In Progress
- **Dependencies**: Phase 14

---

## Overview

### Goal

현재 IFC에서 추출 가능한 모든 데이터를 파악하고, 누락된 Quantity/Material/Classification 추출을 구현한다. 사용자의 실제 IFC 모델 객체 정보와 RDF 데이터의 일치 여부를 검증한다.

### Success Criteria

- [ ] IFC 전수 조사 스크립트 구현 및 실행
- [ ] RDF 감사 SPARQL 쿼리 5종 구현
- [ ] Quantity 추출 (IfcQuantityArea/Length/Volume/Weight)
- [ ] Material 추출 (IfcMaterial/IfcMaterialLayer)
- [ ] Classification 추출 (IfcClassification/Reference)
- [ ] SHACL Shape 추가 (Quantity, Material)

---

## Technical Requirements

### IFC Audit Script (scripts/audit_ifc.py)

ifcopenshell로 IFC 파일을 열어 모든 엔티티 타입, PropertySet 이름, Quantity 존재 여부, Material, Classification, Schedule/Cost 엔티티 유무를 리포트한다.

조사 대상:
| 엔티티 | 타입 | 목적 |
|--------|------|------|
| PropertySets | IfcPropertySet | Pset 이름 + 속성 목록 |
| Quantities | IfcElementQuantity | 수량 (면적/길이/체적/중량) |
| Materials | IfcMaterial | 재료 정보 |
| MaterialLayers | IfcMaterialLayerSetUsage | 레이어 구성 |
| Classifications | IfcClassification | 분류 체계 |
| Schedules | IfcWorkSchedule | 일정 (존재 여부) |
| Tasks | IfcTask | 작업 (존재 여부) |
| CostSchedules | IfcCostSchedule | 비용 (존재 여부) |
| RelAssignsToProcess | IfcRelAssignsToProcess | 작업-요소 연결 |

### RDF Audit Queries (src/api/queries/audit_queries.py)

5종 SPARQL: 전체 요약, 카테고리별 통계, PropertySet 목록, 속성 완성도, 공간 계층 구조

### Property Extraction Enhancement (src/converter/ifc_to_rdf.py)

추가 Data Properties:
- `bim:hasArea` (PhysicalElement → xsd:double)
- `bim:hasLength` (PhysicalElement → xsd:double)
- `bim:hasVolume` (PhysicalElement → xsd:double)
- `bim:hasWeight` (PhysicalElement → xsd:double)
- `bim:hasMaterial` (PhysicalElement → Material, ObjectProperty)
- `bim:hasMaterialName` (Material → xsd:string)
- `bim:hasClassification` (PhysicalElement → ClassificationReference, ObjectProperty)
- `bim:hasClassificationName` (ClassificationReference → xsd:string)
- `bim:hasClassificationSystem` (ClassificationReference → xsd:string)

---

## Deliverables

- [ ] `scripts/audit_ifc.py`
- [ ] `src/api/queries/audit_queries.py`
- [ ] `src/converter/ifc_to_rdf.py` (Quantity/Material/Classification 추출)
- [ ] `data/audit/ifc_audit_report.json`
- [ ] `data/ontology/shapes.ttl` (Shape 추가)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-04
