# Phase 14: SHACL Validation & Enhanced Reasoning - Tasks

## Tasks

### SHACL Shapes
- [x] T-P14-001: `data/ontology/shapes.ttl` 작성 (Turtle 포맷)
- [x] T-P14-002: `BIMElementShape` - hasGlobalId 필수 (xsd:string)
- [x] T-P14-003: `PhysicalElementShape` - hasOriginalType 필수
- [x] T-P14-004: `BuildingStoreyShape` - hasElevation 필수 (xsd:double)
- [x] T-P14-005: `PropertySetShape` - hasProperty 최소 1개 (sh:minCount 1)
- [x] T-P14-006: `PlantPropertySetShape` - hasName 필수

### Validator
- [x] T-P14-007: `load_shapes()` - Turtle 파일에서 shapes graph 로딩
- [x] T-P14-008: `validate()` - pyshacl.validate() 래핑
- [x] T-P14-009: Violation 파싱 (focus_node, message, severity, constraint, path)
- [x] T-P14-010: 에러 핸들링 (shapes 파일 미존재, pyshacl 미설치)

### API
- [x] T-P14-011: `POST /api/reasoning/validate` 엔드포인트 추가
- [x] T-P14-012: SHACL 검증 결과 JSON 응답 형식 정의

### Dependencies
- [x] T-P14-013: `requirements.txt`에 `pyshacl>=0.26` 추가

### Dashboard
- [x] T-P14-014: Reasoning 탭에 SHACL 검증 버튼 추가
- [x] T-P14-015: 검증 결과 (conforms/violations) 렌더링

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
