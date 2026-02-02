# Phase 2: SPARQL 쿼리 엔드포인트 - Checklist

## Completion Criteria

- ☐ FastAPI 서버 구현 완료
- ☐ SPARQL 엔드포인트 동작 (GET/POST)
- ☐ 표준 쿼리 템플릿 10개 작성
- ☐ API 응답 시간 < 2초
- ☐ OpenAPI 3.0 문서 생성

---

## Checklist

### API 서버
- [ ] FastAPI 애플리케이션 구현
- [ ] SPARQL 엔드포인트 (`POST /api/sparql`)
- [ ] RESTful API 엔드포인트 (buildings, components, statistics)
- [ ] Pydantic 모델 (요청/응답)
- [ ] CORS 설정

### 쿼리 템플릿
- [ ] get_all_walls
- [ ] get_spaces_by_storey
- [ ] get_component_statistics
- [ ] get_materials
- [ ] get_properties
- [ ] get_building_hierarchy
- [ ] get_entities_by_type
- [ ] get_relationships
- [ ] get_area_information
- [ ] get_overall_statistics

### 테스트
- [ ] API 단위 테스트
- [ ] 쿼리 템플릿 테스트
- [ ] 통합 테스트
- [ ] 성능 테스트 (응답 시간 < 2초)

### 문서화
- [ ] OpenAPI 문서 (Swagger UI: /docs)
- [ ] API 사용 예제
- [ ] Postman 컬렉션 (선택)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
