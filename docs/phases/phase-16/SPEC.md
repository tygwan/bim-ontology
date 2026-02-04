# Phase 16: Property Injection PoC & Lean Layer Schema - Specification

## Metadata

- **Phase**: Phase 16
- **Milestone**: M17 - Lean Schema
- **Status**: Pending
- **Dependencies**: Phase 15

---

## Overview

### Goal

4가지 property 주입 방법을 PoC로 검증하고, Lean Layer(Schedule/Status/AWP/Equipment) 온톨로지 스키마를 정의한다.

### Success Criteria

- [ ] 방법 A (IfcOpenShell) PoC: IFC에 PropertySet 추가 → RDF 재변환 → SPARQL 조회
- [ ] 방법 B (CSV→RDF) 구현: CSV 주입 → 그래프 트리플 추가 → SPARQL 조회
- [ ] 방법 C (Schema Manager) PoC: 타입/속성 등록 → 그래프 적용
- [ ] Lean Layer 스키마 정의 (`lean_schema.ttl`)
- [ ] Schema Manager date/dateTime 타입 지원
- [ ] SHACL shapes 정의 (Task, IWP, Status)
- [ ] 4가지 방법 비교 문서

---

## Technical Requirements

### PoC Scripts
- `scripts/poc_ifc_inject.py` - IfcOpenShell PropertySet 주입
- `scripts/poc_schema_inject.py` - Schema Manager API 활용

### CSV→RDF Injector
- `src/converter/csv_to_rdf.py` - GlobalId 기반 매핑

### Lean Schema (`data/ontology/lean_schema.ttl`)
- Schedule: ConstructionTask, WorkSchedule, 일정 속성, 선후행 관계
- Status/OPM: ElementStatus, 상태값, 날짜
- AWP: CWA, CWP, IWP, 계층 관계, 제약 조건
- Equipment: ConstructionEquipment, 제원 속성

### Schema Manager Extension
- XSD_MAP에 date, dateTime, duration 추가

---

## Deliverables

- [ ] `scripts/poc_ifc_inject.py`
- [ ] `src/converter/csv_to_rdf.py`
- [ ] `scripts/poc_schema_inject.py`
- [ ] `data/ontology/lean_schema.ttl`
- [ ] `data/test/schedule_sample.csv`
- [ ] `docs/PROPERTY-INJECTION-COMPARISON.md`
- [ ] `src/ontology/schema_manager.py` (타입 확장)
- [ ] `data/ontology/shapes.ttl` (Lean Layer SHACL)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-04
