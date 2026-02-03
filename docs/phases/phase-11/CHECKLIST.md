# Phase 11: Dynamic Ontology Schema Manager - Checklist

## Metadata

- **Phase**: Phase 11
- **Status**: Completed
- **Completed**: 2026-02-03

---

## Completion Criteria

- [x] OntologySchemaManager 전체 CRUD 동작
- [x] 13개 REST 엔드포인트 정상
- [x] JSON 기반 persistence 동작
- [x] Export/Import 라운드트립 정상

---

## Checklist

### OntologySchemaManager
- [x] `list_object_types()` - BIM 네임스페이스 OWL 클래스 목록
- [x] `create_object_type()` - 새 OWL 클래스 생성
- [x] `update_object_type()` - 라벨/설명 수정
- [x] `delete_object_type()` - OWL 클래스 삭제
- [x] `list_property_types()` / `create_property_type()`
- [x] `list_link_types()` / `create_link_type()`
- [x] `list_classification_rules()` / `update_classification_rules()`
- [x] `apply_schema_to_graph()` - 스키마를 RDF 그래프에 적용
- [x] `export_schema()` - JSON 내보내기
- [x] `import_schema()` - JSON 가져오기

### REST API (13개)
- [x] Types: GET, POST, PUT, DELETE
- [x] Properties: GET, POST
- [x] Links: GET, POST
- [x] Rules: GET, PUT
- [x] Schema: Apply, Export, Import

### Persistence
- [x] `data/ontology/classification_rules.json` - 29개 규칙
- [x] `data/ontology/custom_schema.json` - 빈 템플릿 (types, properties, links)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
