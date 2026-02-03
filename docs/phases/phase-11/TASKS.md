# Phase 11: Dynamic Ontology Schema Manager - Tasks

## Tasks

### Core Module
- [x] T-P11-001: `OntologySchemaManager` 클래스 설계
- [x] T-P11-002: `ObjectTypeInfo`, `PropertyTypeInfo`, `LinkTypeInfo` 데이터클래스
- [x] T-P11-003: Object Type CRUD 메서드 구현
- [x] T-P11-004: Property Type 생성 메서드 구현
- [x] T-P11-005: Link Type 생성 메서드 구현
- [x] T-P11-006: Classification Rules JSON 로딩/저장
- [x] T-P11-007: `apply_schema_to_graph()` - OWL 트리플 생성
- [x] T-P11-008: `export_schema()` / `import_schema()` - JSON 라운드트립

### REST API
- [x] T-P11-009: Object Types CRUD 엔드포인트 (GET/POST/PUT/DELETE)
- [x] T-P11-010: Property Types 엔드포인트 (GET/POST)
- [x] T-P11-011: Link Types 엔드포인트 (GET/POST)
- [x] T-P11-012: Classification Rules 엔드포인트 (GET/PUT)
- [x] T-P11-013: Schema Apply/Export/Import 엔드포인트

### Data Files
- [x] T-P11-014: `classification_rules.json` 초기 데이터 (29개 규칙)
- [x] T-P11-015: `custom_schema.json` 빈 템플릿
- [x] T-P11-016: `server.py`에 ontology_editor 라우터 등록

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
