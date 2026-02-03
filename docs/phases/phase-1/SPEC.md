# Phase 1: IFC 파싱 및 RDF 변환 - Specification

## Metadata

- **Phase**: Phase 1
- **Milestone**: M2 - IFC 파싱 및 RDF 변환 기능 구현
- **Status**: ❌ Not Started
- **Progress**: 0%
- **Start Date**: 2026-02-10 (예정)
- **Target Date**: 2026-02-24
- **Duration**: 14 days
- **Dependencies**: Phase 0 완료
- **Owner**: Dev Team

---

## Overview

### Purpose

IFC4 파일을 파싱하고 ifcOWL 기반 RDF triple로 변환하는 핵심 기능을 구현합니다. 이 Phase는 전체 시스템의 데이터 처리 파이프라인의 기반이 됩니다.

### Goals

1. **IFC 파서 개발**: ifcopenshell 기반 IFC4 파일 파싱 모듈
2. **RDF 변환 개발**: IFC 엔티티를 ifcOWL RDF triple로 변환
3. **Triple Store 연동**: 변환된 RDF를 GraphDB/Neo4j에 저장
4. **단위 테스트**: 파서 및 변환 모듈 테스트 커버리지 > 70%

### Success Criteria

- [ ] IFC4 샘플 파일 파싱 성공
- [ ] 최소 1,000개 이상 RDF triple 생성
- [ ] Triple Store에 저장 및 조회 성공
- [ ] 단위 테스트 커버리지 > 70%
- [ ] 변환 시간 < 30분 (200MB 파일 기준)

---

## Technical Requirements

### Functional Requirements

#### FR-P1-001: IFC 파일 파싱

**Description**: ifcopenshell을 사용하여 IFC4 파일을 로딩하고 엔티티를 추출합니다.

**Requirements**:
- IFC4 스키마 검증
- 주요 엔티티 타입 파싱:
  - IfcWall, IfcColumn, IfcBeam (구조 요소)
  - IfcSpace, IfcBuilding, IfcStorey (공간 정보)
  - IfcMaterial, IfcPropertySet (속성 정보)
- 엔티티 관계 추출 (RelDefinesByProperties, RelContainedInSpatialStructure)
- 오류 처리 및 로깅

**Acceptance Criteria**:
```python
# Test case
ifc_file = IFCParser.open('references/sample.ifc')
assert ifc_file.schema == 'IFC4'
assert len(ifc_file.get_entities('IfcWall')) > 0
assert len(ifc_file.get_entities('IfcSpace')) > 0
```

#### FR-P1-002: RDF 변환

**Description**: IFC 엔티티를 ifcOWL 온톨로지 기반 RDF triple로 변환합니다.

**Requirements**:
- ifcOWL 네임스페이스 정의 (`http://ifcowl.openbimstandards.org/IFC4_ADD2#`)
- IFC 엔티티 → RDF Subject 매핑
- 속성 → RDF Predicate 매핑
- 관계 → RDF Object 매핑
- 데이터 타입 변환 (IfcLabel → xsd:string, IfcReal → xsd:double)

**Mapping Example**:
```turtle
# IFC Entity
#123 = IFCWALL('2A3B...');

# RDF Triple
ex:Wall_2A3B a ifc:IfcWall ;
    ifc:globalId "2A3B..." ;
    rdfs:label "External Wall" .
```

**Acceptance Criteria**:
```python
# Test case
rdf_converter = RDFConverter()
triples = rdf_converter.convert_entity(wall_entity)
assert len(triples) > 0
assert (subject, RDF.type, ifc.IfcWall) in triples
```

#### FR-P1-003: Triple Store 저장

**Description**: 변환된 RDF triple을 GraphDB 또는 Neo4j에 저장합니다.

**Requirements**:
- GraphDB Repository 연결
- SPARQL UPDATE (INSERT DATA) 실행
- 배치 처리 (1,000 triple 단위)
- 트랜잭션 관리 (오류 시 롤백)

**Acceptance Criteria**:
```python
# Test case
triple_store = TripleStore('http://localhost:7200/repositories/test')
triple_store.insert(triples)
result = triple_store.query("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
assert result['count'] > 0
```

---

## Architecture

### Module Structure

```
src/
├── parser/
│   ├── __init__.py
│   ├── ifc_parser.py          # IFC 파싱 모듈
│   ├── entity_extractor.py    # 엔티티 추출
│   └── schema_validator.py    # IFC 스키마 검증
├── converter/
│   ├── __init__.py
│   ├── ifc_to_rdf.py          # RDF 변환 메인
│   ├── mapping.py             # IFC → ifcOWL 매핑 룰
│   ├── namespace_manager.py   # 네임스페이스 관리
│   └── serializer.py          # RDF 직렬화
└── storage/
    ├── __init__.py
    ├── triple_store.py        # Triple Store 연동
    ├── graphdb_client.py      # GraphDB 클라이언트
    └── batch_writer.py        # 배치 처리
```

### Data Flow

```
IFC File
    ↓
[IFC Parser] → ifcopenshell.open()
    ↓
[Entity Extractor] → IfcWall, IfcSpace, ...
    ↓
[RDF Converter] → Subject-Predicate-Object triples
    ↓
[Namespace Manager] → ifc:, ex:, rdfs:, rdf:
    ↓
[Batch Writer] → 1,000 triples/batch
    ↓
[Triple Store] → GraphDB Repository
    ↓
SPARQL Query → Verification
```

---

## Non-Functional Requirements

### NFR-P1-001: 성능

**Requirement**: 대용량 IFC 파일 처리 성능

**Acceptance Criteria**:
- 200MB IFC 파일 변환 < 30분
- 메모리 사용량 < 4GB (파일 크기의 20배 이하)
- Triple 생성 속도 > 1,000 triple/sec

### NFR-P1-002: 확장성

**Requirement**: 다양한 IFC 엔티티 타입 지원

**Acceptance Criteria**:
- 최소 50개 IFC 엔티티 타입 지원
- 새 엔티티 타입 추가 용이 (플러그인 구조)
- 커스텀 속성 처리

### NFR-P1-003: 데이터 품질

**Requirement**: 변환 정확성 및 무결성

**Acceptance Criteria**:
- 엔티티 손실률 < 1%
- 속성 매핑 정확도 > 99%
- 관계 무결성 검증

### NFR-P1-004: 유지보수성

**Requirement**: 코드 품질 및 문서화

**Acceptance Criteria**:
- 단위 테스트 커버리지 > 70%
- 함수 및 클래스 docstring 작성
- 타입 힌팅 (Type Hints) 적용

---

## Implementation Details

### 1. IFC Parser Module

**File**: `src/parser/ifc_parser.py`

**Class**: `IFCParser`

**Methods**:
```python
class IFCParser:
    def __init__(self, file_path: str):
        """IFC 파일 경로로 초기화"""

    def open(self) -> ifcopenshell.file:
        """IFC 파일 로딩"""

    def get_schema(self) -> str:
        """IFC 스키마 버전 반환 (IFC4 확인)"""

    def get_entities(self, entity_type: str) -> List:
        """특정 엔티티 타입 추출"""

    def get_entity_count(self) -> int:
        """총 엔티티 수"""

    def validate(self) -> bool:
        """IFC 파일 유효성 검증"""
```

**Usage Example**:
```python
parser = IFCParser('references/sample.ifc')
ifc_file = parser.open()

walls = parser.get_entities('IfcWall')
print(f"Total Walls: {len(walls)}")

spaces = parser.get_entities('IfcSpace')
print(f"Total Spaces: {len(spaces)}")
```

### 2. RDF Converter Module

**File**: `src/converter/ifc_to_rdf.py`

**Class**: `RDFConverter`

**Methods**:
```python
class RDFConverter:
    def __init__(self):
        """RDF 변환기 초기화 (네임스페이스 설정)"""

    def convert_file(self, ifc_file: ifcopenshell.file) -> Graph:
        """전체 IFC 파일을 RDF Graph로 변환"""

    def convert_entity(self, entity: ifcopenshell.entity_instance) -> List[Tuple]:
        """단일 IFC 엔티티를 RDF triple 리스트로 변환"""

    def map_entity_type(self, ifc_type: str) -> URIRef:
        """IFC 타입 → ifcOWL 클래스 매핑"""

    def map_property(self, prop_name: str, prop_value: Any) -> Tuple:
        """IFC 속성 → RDF Predicate-Object 매핑"""
```

**Usage Example**:
```python
converter = RDFConverter()
graph = converter.convert_file(ifc_file)

# Serialize to Turtle
turtle_output = graph.serialize(format='turtle')
print(turtle_output)
```

### 3. Triple Store Module

**File**: `src/storage/triple_store.py`

**Class**: `TripleStore`

**Methods**:
```python
class TripleStore:
    def __init__(self, endpoint: str):
        """SPARQL 엔드포인트 URL로 초기화"""

    def insert(self, triples: List[Tuple]) -> bool:
        """RDF triple 삽입"""

    def insert_graph(self, graph: Graph) -> bool:
        """RDF Graph 삽입"""

    def query(self, sparql: str) -> Dict:
        """SPARQL SELECT 쿼리 실행"""

    def clear(self) -> bool:
        """Repository 초기화"""
```

**Usage Example**:
```python
store = TripleStore('http://localhost:7200/repositories/bim')
store.insert_graph(graph)

# Verify
result = store.query("""
    SELECT (COUNT(*) as ?count)
    WHERE { ?s a ifc:IfcWall }
""")
print(f"Total IfcWall triples: {result['count']}")
```

---

## Testing Strategy

### Unit Tests

**Coverage Target**: > 70%

**Test Files**:
- `tests/test_ifc_parser.py`
- `tests/test_rdf_converter.py`
- `tests/test_triple_store.py`

**Test Cases**:

```python
# tests/test_ifc_parser.py
def test_open_ifc_file():
    parser = IFCParser('references/sample.ifc')
    ifc_file = parser.open()
    assert ifc_file is not None
    assert parser.get_schema() == 'IFC4'

def test_extract_walls():
    parser = IFCParser('references/sample.ifc')
    parser.open()
    walls = parser.get_entities('IfcWall')
    assert len(walls) > 0

def test_invalid_file():
    parser = IFCParser('invalid.ifc')
    with pytest.raises(FileNotFoundError):
        parser.open()
```

```python
# tests/test_rdf_converter.py
def test_convert_entity():
    converter = RDFConverter()
    # Mock IFC entity
    entity = MockIfcWall()
    triples = converter.convert_entity(entity)
    assert len(triples) > 0

def test_namespace_mapping():
    converter = RDFConverter()
    uri = converter.map_entity_type('IfcWall')
    assert str(uri) == 'http://ifcowl.openbimstandards.org/IFC4_ADD2#IfcWall'
```

### Integration Tests

**Test**: IFC → RDF → Triple Store 전체 플로우

```python
def test_end_to_end_conversion():
    # 1. Parse IFC
    parser = IFCParser('references/sample.ifc')
    ifc_file = parser.open()

    # 2. Convert to RDF
    converter = RDFConverter()
    graph = converter.convert_file(ifc_file)
    assert len(graph) > 1000  # At least 1000 triples

    # 3. Store in Triple Store
    store = TripleStore('http://localhost:7200/repositories/test')
    store.clear()
    success = store.insert_graph(graph)
    assert success

    # 4. Verify with SPARQL
    result = store.query("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
    assert result['count'] == len(graph)
```

---

## Dependencies

### Internal

- Phase 0 완료 (환경 설정, IFC 파일 준비)

### External Libraries

- ifcopenshell (v0.7.0+)
- rdflib (v6.0.0+)
- SPARQLWrapper (v2.0.0+)

### Data Dependencies

- IFC 샘플 파일: `references/*.ifc` (.gitignore)
- ifcOWL 온톨로지: https://www.w3.org/community/lbd/

---

## Risks & Mitigation

### R-P1-001: IFC 파싱 오류

**Risk**: 복잡한 IFC 엔티티 구조로 파싱 실패
**Probability**: 높음
**Impact**: 높음
**Mitigation**:
- ifcopenshell 최신 버전 사용
- 단계별 검증 로직 구현
- 오류 로깅 및 재시도 메커니즘

### R-P1-002: 메모리 부족

**Risk**: 대용량 IFC 파일 로딩 시 메모리 부족
**Probability**: 중간
**Impact**: 높음
**Mitigation**:
- 스트리밍 처리 (Phase 4에서 구현)
- 배치 처리 (1,000 엔티티 단위)
- 메모리 프로파일링

### R-P1-003: ifcOWL 매핑 불일치

**Risk**: IFC 엔티티 타입과 ifcOWL 클래스 매핑 누락
**Probability**: 중간
**Impact**: 중간
**Mitigation**:
- ifcOWL 표준 문서 참조
- 매핑 테이블 작성 및 검증
- 누락된 매핑 자동 감지

---

## Deliverables

### Source Code

- [x] `src/parser/ifc_parser.py`
- [ ] `src/parser/entity_extractor.py`
- [ ] `src/converter/ifc_to_rdf.py`
- [ ] `src/converter/mapping.py`
- [ ] `src/storage/triple_store.py`

### Tests

- [ ] `tests/test_ifc_parser.py`
- [ ] `tests/test_rdf_converter.py`
- [ ] `tests/test_triple_store.py`
- [ ] `tests/test_integration.py`

### Documentation

- [ ] API 문서 (Docstrings)
- [ ] 사용 예제 (`examples/phase1_example.py`)
- [ ] 변환 통계 리포트

---

## Timeline

| Week | Tasks | Deliverables |
|------|-------|--------------|
| Week 1 (2/10-2/16) | IFC Parser 개발, 단위 테스트 | ifc_parser.py, tests |
| Week 2 (2/17-2/24) | RDF Converter 개발, Triple Store 연동, 통합 테스트 | converter, storage, integration tests |

**Target Completion**: 2026-02-24

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
**Status**: ❌ Not Started
**Dependencies**: Phase 0 완료
