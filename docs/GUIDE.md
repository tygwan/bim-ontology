# BIM Ontology 사용자 가이드

## 1. 시작하기

### 요구사항

- Python 3.12+
- IFC 파일 (references/ 디렉토리)

### 설치

```bash
git clone https://github.com/tygwan/bim-ontology.git
cd bim-ontology
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 서버 시작

```bash
uvicorn src.api.server:app --port 8001
```

첫 실행 시 IFC 파일을 RDF로 변환하여 `data/rdf/`에 캐싱합니다 (~13초).
이후 실행에서는 캐시 파일을 로딩하여 빠르게 시작합니다 (~2초).

---

## 2. 웹 대시보드

브라우저에서 `http://localhost:8001` 접속

### Overview 탭

- 전체 통계 카드 (트리플 수, 요소 수, 카테고리 수, 건물 수)
- 카테고리 분포 도넛 차트
- Top 10 카테고리 수평 바 차트

### Buildings 탭

- 건물-층 계층 트리
- 층 이름을 클릭하면 해당 층의 상세 정보 표시
- 노드 색상: Building(파랑), Storey(초록), Element 수(회색)

### Elements 탭

- 전체 요소 테이블 (이름, 카테고리, GlobalId)
- **카테고리 필터**: 드롭다운에서 카테고리 선택
- **검색**: 이름으로 필터링
- **페이지네이션**: 50개씩 표시, 이전/다음 버튼

### SPARQL 탭

쿼리 에디터에서 SPARQL을 직접 작성하고 실행합니다.

**내장 템플릿** (드롭다운에서 선택):
1. 카테고리별 요소 수
2. 건물 계층 구조
3. Beam 요소 목록
4. 전체 통계
5. 속성 조회
6. 모든 관계

**BIM 온톨로지 네임스페이스**:
```sparql
PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX inst: <http://example.org/bim-ontology/instance/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
```

**자주 쓰는 쿼리 예시**:

```sparql
# Pipe 카테고리 요소 이름 조회
PREFIX bim: <http://example.org/bim-ontology/schema#>
SELECT ?name WHERE {
    ?e bim:hasCategory "Pipe" .
    ?e bim:hasName ?name .
} LIMIT 20

# 층별 요소 수
PREFIX bim: <http://example.org/bim-ontology/schema#>
SELECT ?storey (COUNT(?elem) AS ?count) WHERE {
    ?storey a bim:BuildingStorey .
    ?storey bim:containsElement ?elem .
} GROUP BY ?storey
```

### Reasoning 탭

- **Run Reasoning** 버튼: OWL/RDFS 추론 실행
- 추론 전/후 트리플 수 비교
- 적용된 규칙 목록
- 추론으로 새로 생성된 타입(StructuralElement, MEPElement, AccessElement) 조회

---

## 3. REST API

### 기본 엔드포인트

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | 서버 상태 |
| GET | `/api/buildings` | 건물 목록 |
| GET | `/api/buildings/{global_id}` | 건물 상세 |
| GET | `/api/storeys` | 층 목록 |
| GET | `/api/elements?category=Pipe&limit=10&offset=0` | 요소 조회 |
| GET | `/api/statistics` | 전체 통계 |
| GET | `/api/statistics/categories` | 카테고리별 통계 |
| GET | `/api/hierarchy` | 건물 계층 구조 |
| POST | `/api/sparql` | SPARQL 쿼리 실행 |
| POST | `/api/reasoning` | OWL/RDFS 추론 실행 |

### SPARQL 쿼리 요청

```bash
curl -X POST http://localhost:8001/api/sparql \
  -H "Content-Type: application/json" \
  -d '{"query":"PREFIX bim: <http://example.org/bim-ontology/schema#> SELECT ?cat (COUNT(?e) AS ?num) WHERE { ?e bim:hasCategory ?cat } GROUP BY ?cat ORDER BY DESC(?num)"}'
```

**응답 형식**:
```json
{
  "status": "success",
  "results": [{"cat": "Other", "num": 1720}, ...],
  "count": 17
}
```

### Swagger UI

`http://localhost:8001/docs` 에서 모든 엔드포인트를 브라우저에서 테스트 가능

---

## 4. Python 클라이언트

### 로컬 모드

```python
from src.clients.python import BIMOntologyClient

client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")

# 기본 조회
stats = client.get_statistics()
print(f"트리플: {stats['total_triples']}, 요소: {stats['total_elements']}")

buildings = client.get_buildings()
storeys = client.get_storeys()
pipes = client.get_elements(category="Pipe", limit=10)
hierarchy = client.get_hierarchy()
```

### 원격 모드

```python
client = BIMOntologyClient.from_api("http://localhost:8001")

# 동일한 API 사용
stats = client.get_statistics()
elements = client.get_elements(category="Beam")
```

### 커스텀 SPARQL

```python
results = client.query("""
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    SELECT ?name ?cat WHERE {
        ?e bim:hasName ?name .
        ?e bim:hasCategory ?cat .
        FILTER(?cat = "Column")
    }
""")
for row in results:
    print(f"{row['name']} - {row['cat']}")
```

---

## 5. 데이터 카테고리

이름 기반 분류로 18개 카테고리가 생성됩니다:

| 카테고리 | 설명 | 수 (IFC4) |
|----------|------|-----------|
| Other | 미분류 | 1,720 |
| MemberPart | 부재 부품 | 570 |
| Aspect | 외관 요소 | 516 |
| Beam | 보 | 380 |
| Pipe | 배관 | 244 |
| Insulation | 단열재 | 114 |
| Geometry | 형상 관련 | 114 |
| Column | 기둥 | 75 |
| Slab | 슬래브 | 41 |
| Foundation | 기초 | 38 |
| Railing | 난간 | 38 |
| CableTray | 케이블트레이 | 20 |
| Duct | 덕트 | 16 |
| Equipment | 장비 | 13 |
| Stair | 계단 | 10 |
| Pump | 펌프 | 1 |
| Wall | 벽체 | 1 |
