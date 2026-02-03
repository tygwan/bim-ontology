# Phase 10: Smart3D Plant PropertySet API - Specification

## Metadata

- **Phase**: Phase 10
- **Milestone**: M11 - Plant Property API
- **Status**: Completed
- **Completed**: 2026-02-03
- **Dependencies**: Phase 9

---

## Overview

### Goal

Smart3D Plant IFC 파일에 포함된 커스텀 PropertySet(weight, length, zone, material type)을 REST API로 노출. SP3D/Smart3D 접두사를 가진 PropertySet을 자동 감지하여 태깅.

### Success Criteria

- [x] SP3D PropertySet 자동 감지 및 `BIM.PlantPropertySet` 태깅
- [x] 요소별 속성 조회 API
- [x] 속성 검색 API (키/값 필터)

---

## Technical Requirements

### SP3D 네임스페이스 (namespace_manager.py)

```python
SP3D = Namespace("http://example.org/bim-ontology/sp3d#")
```

### SP3D 감지 로직 (ifc_to_rdf.py)

`_convert_property_sets()`에서 PropertySet 이름이 "SP3D", "SmartPlant", "Smart3D"로 시작하면 `BIM.PlantPropertySet` 타입 추가.

### REST API 엔드포인트 (properties.py)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/properties/{global_id}` | 요소의 전체 PropertySet 조회 |
| GET | `/api/properties/plant-data` | SP3D 데이터 요약 (PlantPropertySet 통계) |
| GET | `/api/properties/search` | 속성 키/값 검색 (min/max 수치 필터) |

---

## Deliverables

- [x] `src/api/routes/properties.py` - 3개 엔드포인트 (132 lines)
- [x] `src/converter/namespace_manager.py` - SP3D 네임스페이스 추가
- [x] `src/converter/ifc_to_rdf.py` - SP3D PropertySet 감지
- [x] `src/api/server.py` - properties 라우터 등록

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
