# BIM Ontology

> IFC(Industry Foundation Classes) 파일을 RDF/OWL 온톨로지로 변환하고, SPARQL 쿼리 + 동적 스키마 편집 + SHACL 검증을 제공하는 시맨틱 BIM 파이프라인

**[Documentation Site](https://tygwan.github.io/bim-ontology/)** | **[Dashboard Guide](https://tygwan.github.io/bim-ontology/guide/)** | **[API Reference](https://tygwan.github.io/bim-ontology/api/)**

IFC 파일(Navisworks/Smart Plant 3D 내보내기 포함)을 ifcOWL 기반 RDF 트리플로 변환하여 시맨틱 웹 기술로 건설 데이터를 탐색, 추론, 검증합니다.

```
IFC File → [IFCParser] → [RDFConverter] → [TripleStore] → SPARQL / REST API / Dashboard
                                               ↓
                                    [OWLReasoner] → Inferred triples
                                    [SHACLValidator] → Validation report
                                    [OntologySchemaManager] → Dynamic schema editing
```

## Features

### Core Pipeline
- **IFC Parsing** - ifcopenshell 기반 IFC4/IFC2X3 파일 파싱
- **RDF Conversion** - ifcOWL 네임스페이스 기반 RDF 트리플 생성
- **Name-based Classification** - Navisworks 내보내기로 손실된 타입을 29개 카테고리로 복원
- **SPARQL Queries** - rdflib 기반 로컬 트리플 스토어
- **Streaming Conversion** - 배치 단위 대용량 IFC 파일 처리

### Smart3D Plant Support
- **10 Plant-specific Patterns** - MemberSystem, Hanger, PipeFitting, Flange, Nozzle 등
- **SP3D PropertySet Detection** - Smart Plant 3D 속성 자동 태깅
- **Property API** - 요소별 속성 조회 및 검색

### Ontology Management (Palantir Foundry-inspired)
- **Dynamic Schema Editing** - REST API로 Object Type, Property Type, Link Type CRUD
- **Mutable Classification Rules** - JSON 파일 기반 분류 규칙 런타임 변경
- **Schema Import/Export** - JSON 형식 스키마 내보내기/가져오기

### Inference & Validation
- **OWL/RDFS Reasoning** - owlrl 기반 (StructuralElement, MEPElement, PipingElement, PlantSupportElement 등)
- **SHACL Validation** - pyshacl 기반 형상 제약조건 검증
- **Query Caching** - LRU 인메모리 캐시 (14,800x+ 속도 향상)

### Infrastructure
- **Web Dashboard** - 7탭 대시보드 (Overview, Buildings, Elements, SPARQL, Properties, Ontology, Reasoning)
- **GraphDB Integration** - 외부 트리플스토어 어댑터 (SPARQLWrapper)
- **Docker Support** - API + GraphDB (optional) 컨테이너
- **CI/CD** - GitHub Actions (IFC 비의존 테스트 분리)

## Quick Start

```bash
# 1. 가상환경 생성 및 패키지 설치
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 서버 시작
uvicorn src.api.server:app --reload

# 3. 브라우저에서 대시보드 열기
open http://localhost:8000

# 4. 테스트 실행
pytest tests/ -v
```

### Docker

```bash
# API만 실행
docker compose up --build

# GraphDB 포함 실행
docker compose --profile graphdb up --build

# http://localhost:8000 (API + Dashboard)
# http://localhost:7200 (GraphDB Workbench)
```

## Usage

### Python API

```python
from src.parser import IFCParser
from src.converter import RDFConverter
from src.storage import TripleStore

# 1. IFC 파싱
parser = IFCParser("references/sample.ifc")
parser.open()

# 2. RDF 변환
converter = RDFConverter(schema=parser.get_schema())
graph = converter.convert_file(parser)

# 3. SPARQL 쿼리
store = TripleStore(graph)
results = store.query("""
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    SELECT ?cat (COUNT(?e) AS ?num)
    WHERE { ?e bim:hasCategory ?cat }
    GROUP BY ?cat ORDER BY DESC(?num)
""")

# 4. OWL 추론
from src.inference.reasoner import OWLReasoner
reasoner = OWLReasoner(store.graph)
result = reasoner.run_all()  # StructuralElement, MEPElement, PipingElement 등 추론

# 5. SHACL 검증
from src.inference.shacl_validator import validate
report = validate(store.graph)
print(f"Conforms: {report['conforms']}, Violations: {report['violations_count']}")
```

### Python Client

```python
from src.clients.python import BIMOntologyClient

# 로컬 모드
client = BIMOntologyClient.from_ifc("references/sample.ifc")

# 원격 모드
client = BIMOntologyClient.from_api("http://localhost:8000")

stats = client.get_statistics()
pipes = client.get_elements(category="Pipe", limit=10)
hierarchy = client.get_hierarchy()
```

## API Endpoints

### Core API
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web dashboard |
| GET | `/health` | Health check |
| POST | `/api/sparql` | SPARQL query execution |
| GET | `/api/buildings` | Building list |
| GET | `/api/storeys` | Storey list |
| GET | `/api/elements?category=Pipe` | Element list (category filter) |
| GET | `/api/statistics` | Overall statistics |
| GET | `/api/hierarchy` | Building hierarchy |

### Reasoning & Validation
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/reasoning` | Run OWL/RDFS inference |
| POST | `/api/reasoning/validate` | Run SHACL validation |

### Properties (Smart3D Plant)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/properties/{global_id}` | Element PropertySets |
| GET | `/api/properties/plant-data` | SP3D data summary |
| GET | `/api/properties/search?key=Weight` | Property search |

### Ontology Editor
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/ontology/types` | Object Types CRUD |
| PUT/DELETE | `/api/ontology/types/{name}` | Update/delete type |
| GET/POST | `/api/ontology/properties` | Property Types CRUD |
| GET/POST | `/api/ontology/links` | Link Types CRUD |
| GET/PUT | `/api/ontology/rules` | Classification rules |
| POST | `/api/ontology/apply` | Apply schema to graph |
| GET | `/api/ontology/export` | Export schema (JSON) |
| POST | `/api/ontology/import` | Import schema (JSON) |

## Architecture

```
bim-ontology/
├── src/
│   ├── parser/ifc_parser.py          # IFC parsing (IFC4/IFC2X3)
│   ├── converter/
│   │   ├── ifc_to_rdf.py             # RDF conversion + SP3D detection
│   │   ├── streaming_converter.py    # Large file streaming
│   │   ├── mapping.py                # IFC → ifcOWL mappings
│   │   └── namespace_manager.py      # BIM/SP3D/BOT namespaces
│   ├── storage/
│   │   ├── base_store.py             # ABC interface
│   │   ├── triple_store.py           # rdflib local store
│   │   └── graphdb_store.py          # GraphDB adapter
│   ├── inference/
│   │   ├── reasoner.py               # OWL/RDFS + 7 custom rules
│   │   └── shacl_validator.py        # SHACL shape validation
│   ├── ontology/
│   │   └── schema_manager.py         # Dynamic schema CRUD
│   ├── cache/query_cache.py          # LRU query cache
│   ├── api/
│   │   ├── server.py                 # FastAPI server
│   │   └── routes/                   # sparql, buildings, statistics,
│   │                                 # reasoning, properties, ontology_editor
│   ├── dashboard/
│   │   ├── index.html                # 7-tab dashboard
│   │   └── app.js                    # Dashboard logic
│   └── clients/python/client.py      # Python client
├── data/
│   ├── rdf/                           # Converted RDF cache (.gitignore)
│   └── ontology/                     # SHACL shapes, rules, custom schema
├── tests/                            # 91 tests (requires_ifc marker)
├── docker-compose.yml                # API + GraphDB (optional)
└── requirements.txt                  # Python dependencies
```

## Dashboard Guide

7탭 대시보드(`http://localhost:8000`)로 BIM 데이터를 시각적으로 탐색하고 관리합니다.

| Tab | Features |
|-----|----------|
| **Overview** | 4개 통계 카드 (Triples, Elements, Categories, Buildings), 카테고리 도넛 차트, Top 10 바 차트 |
| **Buildings** | 건물 계층 트리 (Project → Site → Building → Storey), 노드 클릭 시 상세 정보 |
| **Elements** | 카테고리 필터 드롭다운, 이름 검색, 50개 단위 페이지네이션 |
| **SPARQL** | 쿼리 에디터 + Execute 버튼, 6개 프리셋 템플릿, 결과 테이블 (행 수, 실행 시간) |
| **Properties** | GlobalId로 PropertySet 조회, 속성 키 검색, Smart3D Plant(SP3D) 데이터 요약 |
| **Ontology** | Object Type/Link Type CRUD, 분류 규칙 JSON 에디터, 스키마 Import/Export/Apply |
| **Reasoning** | OWL/RDFS 추론 실행, Before/After 트리플 비교, 추론된 타입별 요소 수, SHACL 검증 |

상세 가이드: [tygwan.github.io/bim-ontology/guide](https://tygwan.github.io/bim-ontology/guide/)

## Classification System

29 BIM element categories (order-sensitive, specific before generic):

| Group | Categories |
|-------|-----------|
| **Smart3D Plant** | MemberSystem, Hanger, PipeFitting, Flange, ProcessUnit, Conduit, Assembly, Brace, GroutPad, Nozzle |
| **Structural** | Slab, Wall, Column, Beam, Foundation, Structural |
| **MEP** | Pipe, Duct, CableTray, Insulation, Valve, Pump, Equipment |
| **Access** | Railing, Stair |
| **Other** | Support, MemberPart, Aspect, Geometry |

## Reasoning Rules

| Rule | Description |
|------|-------------|
| `infer_structural_element` | Beam, Column, Slab, Wall, Foundation -> StructuralElement |
| `infer_mep_element` | Pipe, Duct, CableTray, Valve, Pump, Insulation, Equipment -> MEPElement |
| `infer_access_element` | Stair, Railing -> AccessElement |
| `infer_plant_support_element` | Hanger, Brace, MemberSystem, Support -> PlantSupportElement |
| `infer_piping_element` | PipeFitting, Flange, Nozzle, Valve, Pipe -> PipingElement |
| `infer_storey_has_elements` | Storey with elements -> hasElements=true |
| `infer_element_in_building` | Element in storey -> isInBuilding (transitive) |

## Performance

| Metric | Value |
|--------|-------|
| IFC4 conversion | ~1.3s / ~39K triples |
| IFC2X3 conversion (streaming) | ~38s / ~39K triples |
| SPARQL cache speedup | 14,869x (65ms -> 0.004ms) |
| OWL reasoning triple increase | +66.7% (39K -> 65K) |
| Test coverage | 85% (91 tests) |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| IFC Parsing | ifcopenshell 0.8.4 |
| RDF/SPARQL | rdflib 7.5.0 |
| OWL/RDFS Reasoning | owlrl 6.0+ |
| SHACL Validation | pyshacl 0.26+ |
| Web Framework | FastAPI |
| External Triplestore | GraphDB 10.6 (optional) |
| Testing | pytest 7.0+ |
| Container | Docker + Docker Compose |

## References

- [ifcOWL (buildingSMART)](https://technical.buildingsmart.org/standards/ifc/ifc-formats/ifcowl/)
- [IFC4 ADD2 Schema](https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL)
- Ontology-based BIM-AMS integration in European Highways (2024)
- Multi-ontology fusion and rule development for automated code compliance checking (2022)
