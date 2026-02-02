# BIM Ontology

IFC(Industry Foundation Classes) 파일을 RDF/OWL 온톨로지로 변환하고 SPARQL로 쿼리하는 파이프라인.

## Overview

건설 산업의 BIM 데이터(IFC 파일)를 시맨틱 웹 기술로 변환하여 의미론적 쿼리를 가능하게 합니다.

```
IFC File → [IFCParser] → [RDFConverter] → [TripleStore] → SPARQL Query
```

## Features

- **IFC 파싱**: ifcopenshell 기반 IFC4/IFC2X3 파일 파싱
- **RDF 변환**: ifcOWL 네임스페이스 기반 RDF 트리플 생성
- **이름 기반 분류**: Navisworks 내보내기로 손실된 타입 정보를 이름 패턴으로 복원
- **SPARQL 쿼리**: rdflib 기반 로컬 트리플 스토어에서 쿼리 실행
- **다중 직렬화**: Turtle, RDF/XML, JSON-LD, N-Triples 지원
- **OWL/RDFS 추론**: owlrl 기반 추론 엔진 (RDFS subClassOf, OWL inverseOf, 커스텀 CONSTRUCT 규칙)
- **쿼리 캐싱**: LRU 인메모리 캐시 (14,800x+ 속도 향상)
- **스트리밍 변환**: 배치 단위 대용량 IFC 파일 처리

## Quick Start

```bash
# 가상환경 생성 및 패키지 설치
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 테스트 실행
pytest tests/ -v
```

## Usage

```python
from src.parser import IFCParser
from src.converter import RDFConverter
from src.storage import TripleStore

# 1. IFC 파일 파싱
parser = IFCParser("references/sample.ifc")
parser.open()

print(f"Schema: {parser.get_schema()}")
print(f"Entities: {parser.get_entity_count()}")

# 2. RDF 변환
converter = RDFConverter(schema=parser.get_schema())
graph = converter.convert_file(parser)

print(f"Triples: {len(graph)}")

# 3. SPARQL 쿼리
store = TripleStore(graph)
results = store.query("""
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    SELECT ?cat (COUNT(?e) AS ?num)
    WHERE {
        ?e bim:hasCategory ?cat .
    }
    GROUP BY ?cat
    ORDER BY DESC(?num)
""")

for row in results:
    print(f"  {row['cat']}: {row['num']}")

# 4. 저장
store.save("output.ttl", fmt="turtle")
```

## API Server

```bash
# 서버 시작 (IFC 파일 자동 변환/캐싱)
uvicorn src.api.server:app --reload

# API 문서: http://localhost:8000/docs
```

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sparql` | SPARQL 쿼리 실행 |
| GET | `/api/buildings` | 건물 목록 |
| GET | `/api/storeys` | 층 목록 |
| GET | `/api/elements?category=Pipe` | 요소 목록 (카테고리 필터) |
| GET | `/api/statistics` | 전체 통계 |
| GET | `/api/hierarchy` | 건물 계층 구조 |

## Python Client

```python
from src.clients.python import BIMOntologyClient

# 로컬 모드 (IFC 파일 직접 사용)
client = BIMOntologyClient.from_ifc("references/sample.ifc")

# 원격 모드 (API 서버 연결)
client = BIMOntologyClient.from_api("http://localhost:8000")

stats = client.get_statistics()
pipes = client.get_elements(category="Pipe", limit=10)
hierarchy = client.get_hierarchy()
```

## Project Structure

```
bim-ontology/
├── src/
│   ├── parser/
│   │   └── ifc_parser.py       # IFC 파싱 모듈
│   ├── converter/
│   │   ├── ifc_to_rdf.py       # RDF 변환 메인
│   │   ├── mapping.py          # IFC → ifcOWL 매핑 룰
│   │   └── namespace_manager.py # 네임스페이스 관리
│   ├── storage/
│   │   └── triple_store.py     # SPARQL 트리플 스토어
│   ├── cache/
│   │   └── query_cache.py      # LRU 쿼리 캐시
│   ├── inference/
│   │   └── reasoner.py         # OWL/RDFS 추론 엔진
│   ├── api/
│   │   ├── server.py           # FastAPI 서버
│   │   ├── routes/             # SPARQL, Buildings, Statistics
│   │   ├── models/             # Pydantic 모델
│   │   └── queries/            # SPARQL 쿼리 템플릿
│   └── clients/
│       └── python/client.py    # Python 클라이언트
├── examples/                   # 사용 예제 5개
├── scripts/                    # 분석/벤치마크 스크립트
├── tests/                      # 90개 테스트
├── data/
│   └── rdf/                    # 변환된 RDF 파일
├── docs/
│   ├── PRD.md                  # 제품 요구사항
│   ├── TECH-SPEC.md            # 기술 설계서
│   ├── PROGRESS.md             # 진행 현황
│   ├── DEVLOG.md               # 개발 일지 및 피드백
│   └── phases/                 # Phase별 상세 문서
├── references/                 # IFC 샘플 파일 및 논문
├── requirements.txt
└── README.md
```

## Test Data

| File | Schema | Size | Entities | Physical Elements |
|------|--------|------|----------|-------------------|
| nwd4op-12.ifc | IFC4 | 224MB | 66,538 | 3,911 (Equipment Systems) |
| nwd23op-12.ifc | IFC2X3 | 828MB | 16,945,319 | 3,980 (Structure Systems) |

## Test Results

- **90/90 tests passed** (100% pass rate)
- **Coverage: 85%** (target: 70%)

| Module | Coverage |
|--------|----------|
| query_cache.py | 100% |
| namespace_manager.py | 100% |
| triple_store.py | 95% |
| api routes | 96~100% |
| streaming_converter.py | 88% |
| reasoner.py | 88% |
| ifc_to_rdf.py | 86% |
| ifc_parser.py | 85% |
| client.py | 82% |

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| IFC4 (224MB) 변환 | 1.3s / 39,237 triples |
| IFC2X3 (828MB) 변환 | 38.1s / 39,237 triples |
| SPARQL 캐시 속도 향상 | 14,869x (65ms -> 0.004ms) |
| OWL 추론 트리플 증가 | +66.7% (39K -> 65K) |

## Known Issues

자세한 내용은 [docs/DEVLOG.md](docs/DEVLOG.md) 참조.

| ID | Issue | Status |
|----|-------|--------|
| F-002 | Navisworks 내보내기로 모든 요소가 IfcBuildingElementProxy로 타입 손실 | 이름 기반 분류로 우회 |
| F-003 | 속성셋 내부 값이 비어 있어 속성 기반 쿼리 제한 | 확인됨 |
| F-004 | GlobalId 없는 비-IfcRoot 엔티티에서 AttributeError | 수정됨 |
| F-005 | 828MB 파일의 1,700만 엔티티 중 95%가 기하 형상 | 기하 제외로 대응 |

## Tech Stack

- **Python 3.12**
- **ifcopenshell** 0.8.4 - IFC 파일 파싱
- **rdflib** 7.5.0 - RDF 그래프 및 SPARQL
- **owlrl** 6.0+ - OWL/RDFS 추론
- **FastAPI** - REST/SPARQL API
- **pytest** - 테스트 프레임워크

## References

- [ifcOWL (buildingSMART)](https://technical.buildingsmart.org/standards/ifc/ifc-formats/ifcowl/)
- [IFC4 ADD2 Schema](https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL)
- Ontology-based BIM-AMS integration in European Highways (2024)
- Multi-ontology fusion and rule development for automated code compliance checking (2022)
