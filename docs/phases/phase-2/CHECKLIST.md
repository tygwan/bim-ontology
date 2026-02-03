# Phase 2: SPARQL 쿼리 엔드포인트 - Checklist

## Metadata

- **Phase**: Phase 2
- **Status**: Completed
- **Completed**: 2026-02-03

---

## Completion Criteria

- [x] FastAPI 서버 구현 완료
- [x] SPARQL 엔드포인트 동작 (POST)
- [x] 쿼리 템플릿 10개 작성
- [x] API 응답 시간 < 2초
- [x] OpenAPI 3.0 문서 자동 생성 (/docs)

---

## Checklist

### API 서버
- [x] `src/api/server.py` - FastAPI 애플리케이션
  - [x] CORS 미들웨어 설정
  - [x] lifespan 이벤트 (데이터 자동 로딩/캐싱)
  - [x] 테스트용 store 주입 (`create_app(store=)`)
- [x] `src/api/routes/sparql.py` - SPARQL POST 엔드포인트
- [x] `src/api/routes/buildings.py` - Buildings/Storeys/Elements REST API
- [x] `src/api/routes/statistics.py` - 통계/카테고리/계층 API
- [x] `src/api/models/` - Pydantic 요청/응답 모델
- [x] `src/api/utils/query_executor.py` - 전역 TripleStore 관리

### API 엔드포인트
- [x] POST `/api/sparql` - SPARQL 쿼리 실행
- [x] GET `/api/buildings` - 건물 목록
- [x] GET `/api/buildings/{id}` - 건물 상세
- [x] GET `/api/storeys` - 층 목록
- [x] GET `/api/elements` - 요소 목록 (카테고리 필터, 페이지네이션)
- [x] GET `/api/statistics` - 전체 통계
- [x] GET `/api/statistics/categories` - 카테고리별 통계
- [x] GET `/api/hierarchy` - 건물 계층 구조
- [x] GET `/health` - 헬스 체크

### 쿼리 템플릿
- [x] `src/api/queries/templates.py` - 10개 SPARQL 쿼리 템플릿
  - [x] get_component_statistics
  - [x] get_building_hierarchy
  - [x] get_entities_by_type
  - [x] get_overall_statistics
  - [x] 외 6개 내부 쿼리

### 테스트
- [x] `tests/test_api.py` - 20개 API 테스트
  - [x] SPARQL 엔드포인트 테스트 (SELECT, COUNT, 빈 쿼리, 잘못된 쿼리)
  - [x] Buildings API 테스트 (목록, 상세, 404, 층, 요소, 페이지네이션)
  - [x] Statistics API 테스트 (통계, 카테고리, 계층)
  - [x] 쿼리 템플릿 테스트 4개
- [x] 20/20 테스트 통과

### 문서화
- [x] OpenAPI 문서 자동 생성 (Swagger UI: /docs)
- [x] F-007: RDF 캐싱 전략 구현 (Turtle 파일 캐시)
- [x] F-008: TripleStore 전역 상태 관리 구현

---

**Document Version**: v2.0
**Last Updated**: 2026-02-03
