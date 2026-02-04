# Phase 16: Property Injection PoC & Lean Layer Schema - Checklist

## Metadata

- **Phase**: Phase 16
- **Status**: Complete

---

## Checklist

### PoC - Method A (IfcOpenShell)
- [x] `scripts/poc_ifc_inject.py` 생성
- [x] IFC에 EPset_Schedule PropertySet 추가
- [x] RDF 재변환 후 PropertySet 추출 확인
- [x] SPARQL 조회 성공

### PoC - Method B (CSV→RDF)
- [x] `src/converter/csv_to_rdf.py` 구현
- [x] `data/test/schedule_sample.csv` 생성
- [x] CSV 주입 후 그래프 트리플 추가 확인
- [x] SPARQL 조회 성공

### PoC - Method C (Schema Manager)
- [x] `scripts/poc_schema_inject.py` 생성
- [x] custom_schema.json에 정의 저장 확인
- [x] apply_schema_to_graph() OWL 트리플 추가 확인

### Lean Schema
- [x] `data/ontology/lean_schema.ttl` 생성
- [x] Schedule 온톨로지 (ConstructionTask, WorkSchedule)
- [x] Status/OPM 온톨로지 (ElementStatus, DeliveryStatus)
- [x] AWP 온톨로지 (CWA, CWP, IWP)
- [x] Equipment 온톨로지 (ConstructionEquipment)
- [x] rdflib 파싱 가능 확인 (169 triples, 7 classes)

### Schema Manager Extension
- [x] XSD_MAP에 date, dateTime, duration 추가

### SHACL
- [x] ConstructionTaskShape 정의
- [x] InstallationWorkPackageShape 정의
- [x] ElementStatusShape 정의
- [x] ConstructionEquipmentShape 정의 (추가)

### Documentation
- [x] `docs/PROPERTY-INJECTION-COMPARISON.md` 작성

### Additional (계획 외)
- [x] `data/test/awp_sample.csv` 테스트 데이터 생성

---

**Document Version**: v1.1
**Last Updated**: 2026-02-04
