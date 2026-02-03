# Phase 14: SHACL Validation & Enhanced Reasoning - Specification

## Metadata

- **Phase**: Phase 14
- **Milestone**: M15 - Schema Constraints
- **Status**: Completed
- **Completed**: 2026-02-03
- **Dependencies**: Phase 11, Phase 13

---

## Overview

### Goal

SHACL(Shapes Constraint Language)로 RDF 그래프의 데이터 품질을 검증. pyshacl 라이브러리를 통합하고, 5개 SHACL Shape을 정의하여 필수 속성 존재 여부 및 타입 제약조건을 검사.

### Success Criteria

- [x] 5개 SHACL Shape 정의 (shapes.ttl)
- [x] pyshacl 기반 검증 함수 구현
- [x] REST API 엔드포인트 (`POST /api/reasoning/validate`)
- [x] 검증 결과 JSON 리포트 (conforms, violations, results_text)

---

## Technical Requirements

### SHACL Shapes (shapes.ttl)

| Shape | Target Class | Constraints |
|-------|-------------|-------------|
| `BIMElementShape` | `bim:BIMElement` | `bim:hasGlobalId` 필수 (xsd:string) |
| `PhysicalElementShape` | `bim:PhysicalElement` | `bim:hasOriginalType` 필수 |
| `BuildingStoreyShape` | `bim:BuildingStorey` | `bim:hasElevation` 필수 (xsd:double) |
| `PropertySetShape` | `bim:PropertySet` | `bim:hasProperty` 최소 1개 |
| `PlantPropertySetShape` | `bim:PlantPropertySet` | `bim:hasName` 필수 |

### Validator (shacl_validator.py)

```python
def load_shapes(shapes_path: str) -> Graph:
    """SHACL shapes 파일 로딩."""

def validate(data_graph: Graph, shapes_path: str = None) -> dict:
    """pyshacl로 RDF 그래프 검증.
    Returns: {conforms, violations_count, violations, results_text, error}
    """
```

각 violation 객체:
- `focus_node`: 검증 실패 노드 URI
- `message`: 검증 메시지
- `severity`: 심각도 (Violation, Warning, Info)
- `constraint`: 제약조건 컴포넌트
- `path`: 속성 경로

### REST API (reasoning.py)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/reasoning` | OWL/RDFS 추론 실행 (기존) |
| POST | `/api/reasoning/validate` | SHACL 검증 (신규) |

---

## Deliverables

- [x] `src/inference/shacl_validator.py` (105 lines)
- [x] `data/ontology/shapes.ttl` (58 lines, 5개 Shape)
- [x] `src/api/routes/reasoning.py` - SHACL 엔드포인트 추가
- [x] `requirements.txt` - `pyshacl>=0.26` 추가

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
