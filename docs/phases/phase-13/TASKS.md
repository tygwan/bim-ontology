# Phase 13: GraphDB External Triplestore - Tasks

## Tasks

### Storage Abstraction
- [x] T-P13-001: `BaseTripleStore` ABC 정의 (query, insert, count, load, save)
- [x] T-P13-002: `TripleStore`를 `BaseTripleStore` 하위 클래스로 리팩터링
- [x] T-P13-003: `__len__()` 프로토콜 구현

### GraphDB Adapter
- [x] T-P13-004: `GraphDBStore` 클래스 구현
- [x] T-P13-005: `query()` - SPARQLWrapper SELECT 실행
- [x] T-P13-006: `insert()` - SPARQL INSERT DATA
- [x] T-P13-007: `count()` - SELECT COUNT(*)
- [x] T-P13-008: `load()` - GraphDB Import API 또는 SPARQL LOAD
- [x] T-P13-009: `save()` - Turtle 포맷 내보내기

### Factory & Integration
- [x] T-P13-010: `create_store()` 팩토리 함수 (환경변수 기반)
- [x] T-P13-011: `__init__.py` exports 정리 (BaseTripleStore, TripleStore, create_store)
- [x] T-P13-012: `server.py`에서 `create_store()` 사용하도록 수정

### Docker
- [x] T-P13-013: `docker-compose.yml`에 GraphDB 서비스 추가 (optional profile)
- [x] T-P13-014: API 서비스에 GraphDB 환경변수 추가 (TRIPLESTORE_BACKEND, GRAPHDB_URL, GRAPHDB_REPO)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
