# Phase 11: Dynamic Ontology Schema Manager - Specification

## Metadata

- **Phase**: Phase 11
- **Milestone**: M12 - Runtime Ontology Editing
- **Status**: Completed
- **Completed**: 2026-02-03
- **Dependencies**: Phase 10

---

## Overview

### Concept

Palantir Foundry Ontology 패턴에서 영감을 받은 동적 스키마 편집 시스템. REST API를 통해 Object Type, Property Type, Link Type을 런타임에 CRUD하고, 분류 규칙을 JSON 파일로 관리.

### Concept Mapping

| Palantir Foundry | BIM Ontology Equivalent |
|---|---|
| Object Type | OWL Class in BIM namespace |
| Property Type | OWL DatatypeProperty |
| Link Type | OWL ObjectProperty with domain/range |
| Action | SPARQL CONSTRUCT rule |

### Success Criteria

- [x] OntologySchemaManager 클래스 구현 (CRUD + apply/export/import)
- [x] 13개 REST API 엔드포인트
- [x] JSON 파일 기반 분류 규칙 관리
- [x] 스키마 export/import 라운드트립

---

## Technical Requirements

### OntologySchemaManager (schema_manager.py)

**Data Classes:**
- `ObjectTypeInfo` - name, parent_class, label, description
- `PropertyTypeInfo` - name, domain, range_type
- `LinkTypeInfo` - name, domain, range_class, inverse_name

**Core Methods:**

| Category | Methods |
|----------|---------|
| Object Types | `list_object_types()`, `create_object_type()`, `update_object_type()`, `delete_object_type()` |
| Property Types | `list_property_types()`, `create_property_type()` |
| Link Types | `list_link_types()`, `create_link_type()` |
| Rules | `list_classification_rules()`, `update_classification_rules()` |
| Schema Ops | `apply_schema_to_graph()`, `export_schema()`, `import_schema()` |

### REST API (ontology_editor.py)

| Method | Path | Handler |
|--------|------|---------|
| GET | `/api/ontology/types` | list_types() |
| POST | `/api/ontology/types` | create_type() |
| PUT | `/api/ontology/types/{name}` | update_type() |
| DELETE | `/api/ontology/types/{name}` | delete_type() |
| GET | `/api/ontology/properties` | list_properties() |
| POST | `/api/ontology/properties` | create_property() |
| GET | `/api/ontology/links` | list_links() |
| POST | `/api/ontology/links` | create_link() |
| GET | `/api/ontology/rules` | get_rules() |
| PUT | `/api/ontology/rules` | update_rules() |
| POST | `/api/ontology/apply` | apply_schema() |
| GET | `/api/ontology/export` | export_schema() |
| POST | `/api/ontology/import` | import_schema() |

### Persistence

- `data/ontology/classification_rules.json` - 29개 분류 규칙 (JSON)
- `data/ontology/custom_schema.json` - 사용자 정의 types/properties/links

---

## Deliverables

- [x] `src/ontology/__init__.py`
- [x] `src/ontology/schema_manager.py` (284 lines)
- [x] `src/api/routes/ontology_editor.py` (171 lines)
- [x] `data/ontology/classification_rules.json`
- [x] `data/ontology/custom_schema.json`

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
