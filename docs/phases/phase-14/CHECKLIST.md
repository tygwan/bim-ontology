# Phase 14: SHACL Validation & Enhanced Reasoning - Checklist

## Metadata

- **Phase**: Phase 14
- **Status**: Completed
- **Completed**: 2026-02-03

---

## Completion Criteria

- [x] 5개 SHACL Shape 정의 및 검증 동작
- [x] pyshacl 기반 검증 함수 구현
- [x] REST API 엔드포인트 동작
- [x] Dashboard Reasoning 탭에서 SHACL 검증 가능

---

## Checklist

### SHACL Shapes (shapes.ttl)
- [x] `bim:BIMElementShape` → `bim:hasGlobalId` (xsd:string)
- [x] `bim:PhysicalElementShape` → `bim:hasOriginalType`
- [x] `bim:BuildingStoreyShape` → `bim:hasElevation` (xsd:double)
- [x] `bim:PropertySetShape` → `bim:hasProperty` (sh:minCount 1)
- [x] `bim:PlantPropertySetShape` → `bim:hasName`

### Validator
- [x] `load_shapes(shapes_path)` - Graph 로딩
- [x] `validate(data_graph, shapes_path)` - pyshacl 실행
- [x] 결과 구조: conforms, violations_count, violations[], results_text
- [x] Violation 필드: focus_node, message, severity, constraint, path

### API
- [x] `POST /api/reasoning` - OWL/RDFS 추론 (기존)
- [x] `POST /api/reasoning/validate` - SHACL 검증 (신규)
- [x] JSON 응답: conforms, violations_count, results_text

### Dependencies
- [x] `pyshacl>=0.26` in requirements.txt

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
