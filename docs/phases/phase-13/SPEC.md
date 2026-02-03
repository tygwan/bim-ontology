# Phase 13: GraphDB External Triplestore - Specification

## Metadata

- **Phase**: Phase 13
- **Milestone**: M14 - External SPARQL Store
- **Status**: Completed
- **Completed**: 2026-02-03
- **Dependencies**: Phase 8 (parallel with Phase 11-12)

---

## Overview

### Goal

rdflib 인메모리 스토어 외에 GraphDB 외부 트리플스토어를 연동 가능하도록 스토리지 레이어를 추상화. 환경변수로 백엔드 전환, Docker Compose에 GraphDB 서비스 추가.

### Success Criteria

- [x] `BaseTripleStore` ABC로 스토리지 인터페이스 통일
- [x] `GraphDBStore` 어댑터 구현 (SPARQLWrapper)
- [x] `create_store()` 팩토리 함수로 백엔드 전환
- [x] Docker Compose에 GraphDB 서비스 추가 (optional profile)

---

## Technical Requirements

### BaseTripleStore ABC (base_store.py)

```python
class BaseTripleStore(ABC):
    @abstractmethod
    def query(self, sparql: str) -> list[dict]: ...
    @abstractmethod
    def insert(self, triples: list[tuple]) -> int: ...
    @abstractmethod
    def count(self) -> int: ...
    @abstractmethod
    def load(self, filepath: str) -> int: ...
    @abstractmethod
    def save(self, filepath: str) -> str: ...
    def __len__(self) -> int: return self.count()
```

### GraphDBStore (graphdb_store.py)

SPARQLWrapper를 사용하여 GraphDB REST API와 통신:
- `DEFAULT_GRAPHDB_URL = "http://localhost:7200"`
- `DEFAULT_REPO = "bim-ontology"`
- SPARQL SELECT, INSERT DATA, COUNT, LOAD, EXPORT 지원

### Factory Function (storage/__init__.py)

```python
def create_store(backend: str | None = None) -> BaseTripleStore:
    backend = backend or os.getenv("TRIPLESTORE_BACKEND", "local")
    if backend == "graphdb":
        return GraphDBStore()
    return TripleStore()
```

### Docker Compose

GraphDB를 optional profile로 추가:
```yaml
graphdb:
  image: ontotext/graphdb:10.6
  ports: ["${GRAPHDB_PORT:-7200}:7200"]
  profiles: [graphdb]
  environment: [GDB_HEAP_SIZE=2g]
```

---

## Deliverables

- [x] `src/storage/base_store.py` (40 lines)
- [x] `src/storage/graphdb_store.py` (131 lines)
- [x] `src/storage/__init__.py` - factory + exports (26 lines)
- [x] `src/storage/triple_store.py` - BaseTripleStore 상속
- [x] `docker-compose.yml` - GraphDB 서비스 추가
- [x] `requirements.txt` - SPARQLWrapper>=2.0 추가

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
