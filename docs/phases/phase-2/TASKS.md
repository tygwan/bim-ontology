# Phase 2: SPARQL 쿼리 엔드포인트 - Tasks

## Task Overview

| Category | Total |
|----------|-------|
| API 서버 개발 | 8 |
| 쿼리 템플릿 작성 | 10 |
| 테스트 | 5 |
| 문서화 | 2 |
| **Total** | **25** |

---

## Tasks

### API 서버 개발
- [ ] T-P2-001: FastAPI 서버 기본 구조 (`src/api/server.py`)
- [ ] T-P2-002: SPARQL 엔드포인트 구현 (`src/api/routes/sparql.py`)
- [ ] T-P2-003: Buildings API 구현 (`src/api/routes/buildings.py`)
- [ ] T-P2-004: Components API 구현 (`src/api/routes/components.py`)
- [ ] T-P2-005: Statistics API 구현 (`src/api/routes/statistics.py`)
- [ ] T-P2-006: 요청/응답 모델 작성 (Pydantic models)
- [ ] T-P2-007: 쿼리 실행 유틸리티 (`src/api/utils/query_executor.py`)
- [ ] T-P2-008: CORS 및 미들웨어 설정

### 쿼리 템플릿 작성
- [ ] T-P2-009: get_all_walls 쿼리
- [ ] T-P2-010: get_spaces_by_storey 쿼리
- [ ] T-P2-011: get_component_statistics 쿼리
- [ ] T-P2-012: get_materials 쿼리
- [ ] T-P2-013: get_properties 쿼리
- [ ] T-P2-014: get_building_hierarchy 쿼리
- [ ] T-P2-015: get_entities_by_type 쿼리
- [ ] T-P2-016: get_relationships 쿼리
- [ ] T-P2-017: get_area_information 쿼리
- [ ] T-P2-018: get_overall_statistics 쿼리

### 테스트
- [ ] T-P2-019: API 단위 테스트 (`tests/test_api.py`)
- [ ] T-P2-020: 쿼리 템플릿 테스트
- [ ] T-P2-021: 통합 테스트 (API + Triple Store)
- [ ] T-P2-022: 성능 테스트 (응답 시간 < 2초)
- [ ] T-P2-023: 부하 테스트 (동시 요청)

### 문서화
- [ ] T-P2-024: OpenAPI 문서 검증 및 보완
- [ ] T-P2-025: API 사용 예제 작성 (`examples/phase2_example.py`)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
