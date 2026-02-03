# Phase 13: GraphDB External Triplestore - Checklist

## Metadata

- **Phase**: Phase 13
- **Status**: Completed
- **Completed**: 2026-02-03

---

## Completion Criteria

- [x] BaseTripleStore ABC 정의
- [x] GraphDBStore 어댑터 구현
- [x] 팩토리 기반 백엔드 전환
- [x] Docker Compose GraphDB 서비스

---

## Checklist

### Storage Abstraction
- [x] `BaseTripleStore` ABC - 5개 추상 메서드
- [x] `TripleStore` → `BaseTripleStore` 상속
- [x] `__len__()` → `count()` 위임

### GraphDBStore
- [x] `__init__(endpoint_url, repo)` - GraphDB 연결 설정
- [x] `query()` - SPARQLWrapper SELECT
- [x] `insert()` - SPARQL INSERT DATA
- [x] `count()` - SELECT COUNT(*)
- [x] `load()` - 파일 로딩
- [x] `save()` - Turtle 내보내기

### Factory
- [x] `create_store(backend)` - "local" → TripleStore, "graphdb" → GraphDBStore
- [x] `TRIPLESTORE_BACKEND` 환경변수 지원

### Docker
- [x] GraphDB 10.6 서비스 (optional `graphdb` profile)
- [x] Port: `${GRAPHDB_PORT:-7200}:7200`
- [x] Volume: `graphdb_data`
- [x] `GDB_HEAP_SIZE=2g`
- [x] API 서비스 `depends_on` 설정

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
