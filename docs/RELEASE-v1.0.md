# Release Notes v1.0.0

**Release Date**: 2026-02-03

## Summary

IFC(Industry Foundation Classes) 파일을 RDF/OWL 온톨로지로 변환하고, SPARQL 쿼리 및 웹 대시보드로 BIM 데이터를 탐색할 수 있는 전체 파이프라인 첫 릴리스.

## Features

### Core Pipeline
- **IFC 파싱**: ifcopenshell 기반 IFC4/IFC2X3 듀얼 스키마 지원
- **RDF 변환**: ifcOWL 네임스페이스 기반, 80+ 엔티티 타입 매핑
- **이름 기반 분류**: Navisworks 내보내기로 손실된 타입 정보를 18개 카테고리로 복원
- **TripleStore**: rdflib 인메모리 SPARQL 엔진

### API & Client
- **REST API**: FastAPI 기반 9개 엔드포인트 (Buildings, Elements, Statistics, Hierarchy, SPARQL)
- **추론 API**: OWL/RDFS 추론 엔드포인트 (POST /api/reasoning)
- **Python 클라이언트**: 로컬/원격 듀얼 모드 (BIMOntologyClient)
- **OpenAPI 문서**: Swagger UI (/docs)

### Performance
- **쿼리 캐시**: LRU 인메모리, 14,869x 속도 향상
- **OWL 추론**: 5개 커스텀 규칙 + RDFS, +66.7% 트리플 생성
- **스트리밍 변환**: 배치 단위 대용량 파일 처리

### Dashboard & Deployment
- **웹 대시보드**: 5개 탭 (Overview, Buildings, Elements, SPARQL, Reasoning)
- **Docker**: 단일 컨테이너 배포 (python:3.12-slim)
- **CI**: GitHub Actions 자동 테스트

## Tested Configurations

| Schema | Entities Scale | Triples | Conversion Time |
|--------|---------------|---------|-----------------|
| IFC4 | 수만 | ~39K | ~1.3s |
| IFC2X3 | 수천만 | ~39K | ~38s |

## Quality

- **91 tests**, 100% pass rate
- **85%+ code coverage**
- **0 errors** under 10 concurrent users (부하 테스트)

## Known Limitations

- rdflib 단일 스레드로 동시 10명 부하 시 복잡 쿼리 P95 > 2초
- Navisworks 내보내기로 "Other" 카테고리 44% (원본 모델이면 해결)
- OWL RL 프로파일만 지원 (OWL DL/Full 미지원)
- CLI 도구 미구현 (대시보드/Python 클라이언트로 대체)

## Tech Stack

- Python 3.12, ifcopenshell 0.8.4, rdflib 7.5.0
- owlrl 6.0+, FastAPI, uvicorn
- Chart.js, Tailwind CSS (CDN)
- Docker, GitHub Actions
