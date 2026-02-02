# Phase 2: SPARQL 쿼리 엔드포인트 - Specification

## Metadata

- **Phase**: Phase 2
- **Milestone**: M3 - SPARQL 쿼리 엔드포인트 구축
- **Status**: ❌ Not Started
- **Progress**: 0%
- **Start Date**: 2026-02-24 (예정)
- **Target Date**: 2026-03-10
- **Duration**: 14 days
- **Dependencies**: Phase 1 완료
- **Owner**: Dev Team

---

## Overview

### Purpose

RESTful API 서버를 구축하고 SPARQL 쿼리 엔드포인트를 제공하여 클라이언트가 건물 정보를 쿼리할 수 있도록 합니다.

### Goals

1. **SPARQL 쿼리 엔진 통합**: GraphDB SPARQL 엔드포인트 연동
2. **RESTful API 서버 구현**: FastAPI 기반 API 서버
3. **표준 쿼리 템플릿**: 건물 구성요소, 공간, 자재 조회 쿼리 10개
4. **API 문서화**: OpenAPI 3.0 자동 생성

### Success Criteria

- [ ] SPARQL 엔드포인트 동작 (GET/POST)
- [ ] 표준 쿼리 10개 실행 성공
- [ ] API 응답 시간 < 2초
- [ ] OpenAPI 3.0 문서 생성

---

## Functional Requirements

### FR-P2-001: SPARQL 쿼리 엔드포인트

**Description**: HTTP 요청으로 SPARQL 쿼리를 받아 Triple Store에서 실행하고 결과를 JSON으로 반환합니다.

**API Endpoint**:
```
POST /api/sparql
Content-Type: application/json

{
  "query": "SELECT ?wall WHERE { ?wall a ifc:IfcWall } LIMIT 10"
}

Response:
{
  "status": "success",
  "results": [
    { "wall": "http://example.org/Wall001" },
    ...
  ],
  "count": 10
}
```

### FR-P2-002: 표준 쿼리 템플릿

**Description**: 자주 사용되는 쿼리를 템플릿화하여 제공합니다.

**Templates**:
1. 모든 벽 조회 (get_all_walls)
2. 특정 층의 공간 조회 (get_spaces_by_storey)
3. 건물 구성요소 통계 (get_component_statistics)
4. 자재 정보 조회 (get_materials)
5. 속성 정보 조회 (get_properties)
6. 건물 계층 구조 조회 (get_building_hierarchy)
7. 특정 타입 엔티티 조회 (get_entities_by_type)
8. 관계 정보 조회 (get_relationships)
9. 면적 정보 조회 (get_area_information)
10. 전체 통계 (get_overall_statistics)

### FR-P2-003: RESTful API

**Description**: SPARQL 외에 REST 스타일 엔드포인트 제공

**Endpoints**:
- `GET /api/buildings` - 모든 건물 조회
- `GET /api/buildings/{id}` - 특정 건물 조회
- `GET /api/buildings/{id}/spaces` - 건물의 공간 조회
- `GET /api/walls` - 모든 벽 조회
- `GET /api/materials` - 모든 자재 조회
- `GET /api/statistics` - 통계 정보

---

## Architecture

### API Server Structure

```
src/api/
├── __init__.py
├── server.py              # FastAPI 애플리케이션
├── routes/
│   ├── __init__.py
│   ├── sparql.py          # SPARQL 엔드포인트
│   ├── buildings.py       # 건물 관련 API
│   ├── components.py      # 구성요소 API
│   └── statistics.py      # 통계 API
├── models/
│   ├── __init__.py
│   ├── request.py         # 요청 모델 (Pydantic)
│   └── response.py        # 응답 모델
├── queries/
│   ├── __init__.py
│   └── templates.py       # 쿼리 템플릿
└── utils/
    ├── __init__.py
    ├── query_executor.py  # SPARQL 쿼리 실행
    └── response_formatter.py  # 응답 포맷팅
```

---

## Implementation Details

### FastAPI Server

**File**: `src/api/server.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import sparql, buildings, components, statistics

app = FastAPI(
    title="IFC to Ontology DB API",
    description="SPARQL query endpoint for BIM data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sparql.router, prefix="/api", tags=["SPARQL"])
app.include_router(buildings.router, prefix="/api", tags=["Buildings"])
app.include_router(components.router, prefix="/api", tags=["Components"])
app.include_router(statistics.router, prefix="/api", tags=["Statistics"])

@app.get("/")
async def root():
    return {"message": "IFC to Ontology DB API", "version": "1.0.0"}
```

### SPARQL Endpoint

**File**: `src/api/routes/sparql.py`

```python
from fastapi import APIRouter, HTTPException
from ..models.request import SPARQLRequest
from ..models.response import SPARQLResponse
from ..utils.query_executor import execute_sparql_query

router = APIRouter()

@router.post("/sparql", response_model=SPARQLResponse)
async def execute_sparql(request: SPARQLRequest):
    try:
        results = execute_sparql_query(request.query)
        return SPARQLResponse(
            status="success",
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing Strategy

### API Tests

**File**: `tests/test_api.py`

```python
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_sparql_endpoint():
    response = client.post("/api/sparql", json={
        "query": "SELECT ?s WHERE { ?s a ifc:IfcWall } LIMIT 10"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_buildings():
    response = client.get("/api/buildings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

## Deliverables

- [ ] `src/api/server.py`
- [ ] `src/api/routes/sparql.py`
- [ ] `src/api/queries/templates.py`
- [ ] `tests/test_api.py`
- [ ] OpenAPI 문서 (자동 생성: `/docs`)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
