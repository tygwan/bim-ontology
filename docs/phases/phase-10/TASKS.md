# Phase 10: Smart3D Plant PropertySet API - Tasks

## Tasks

### 네임스페이스
- [x] T-P10-001: SP3D 네임스페이스 정의 (`namespace_manager.py`)
- [x] T-P10-002: `bind_namespaces()`에 SP3D 추가

### RDF 변환
- [x] T-P10-003: `_convert_property_sets()`에 SP3D 감지 로직 추가
- [x] T-P10-004: SP3D PropertySet에 `BIM.PlantPropertySet` 타입 태깅

### API 엔드포인트
- [x] T-P10-005: `GET /api/properties/{global_id}` - SPARQL로 요소 PropertySet 조회
- [x] T-P10-006: `GET /api/properties/plant-data` - PlantPropertySet 통계 집계
- [x] T-P10-007: `GET /api/properties/search` - 키/값 기반 속성 검색
- [x] T-P10-008: `server.py`에 properties 라우터 등록

### Dashboard
- [x] T-P10-009: Properties 탭에서 GlobalId로 속성 조회 UI
- [x] T-P10-010: 속성 키 검색 UI

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
