# IFC to Ontology DB Schema - Context Summary

## Quick Reference

**프로젝트 한 줄 요약**
Building Information Modeling (BIM) 표준 포맷인 IFC 파일을 ontology 기반 RDF triple store로 변환하고, SPARQL 쿼리를 통해 건물 정보를 의미론적으로 분석하는 시스템.

**프로젝트 코드**: BIM-ONTOLOGY
**상태**: Phase 0 - 프로젝트 초기화 및 문서화
**마지막 업데이트**: 2026-02-03

---

## Core Technology Stack

### Backend & Processing
- **IFC Parsing**: ifcopenshell (v0.7.0+, Python 3.8+)
- **RDF Processing**: RDFLib (Python), Apache Jena (Java 11+)
- **Triple Store**: GraphDB (Free Edition) 또는 Neo4j (Community Edition)
- **Reasoning Engine**: Apache Jena Inference Engine
- **API Framework**: FastAPI (Python) 또는 Spring Boot (Java)

### Client Libraries
- **Python**: SPARQLWrapper, requests
- **Java**: Apache Jena ARQ
- **JavaScript**: sparql-client (Node.js 14+)

### Frontend & Tools
- **Dashboard**: React 또는 Vue.js
- **CLI**: Python Click/Typer
- **Deployment**: Docker, Docker Compose

### Standards
- **Data Format**: IFC4 (ISO 16739:2013)
- **Ontology**: ifcOWL (OWL 2)
- **Query Language**: SPARQL 1.1
- **Serialization**: RDF/XML, Turtle, JSON-LD

---

## Project Structure

```
bim-ontology/
├── docs/                      # 프로젝트 문서
│   ├── PRD.md                 # 제품 요구사항 정의서
│   ├── TECH-SPEC.md           # 기술 명세서
│   ├── PROGRESS.md            # 진행 상황 추적
│   ├── CONTEXT.md             # 컨텍스트 요약 (이 문서)
│   └── phases/                # Phase별 상세 문서
│       ├── phase-0/           # 프로젝트 초기화
│       ├── phase-1/           # IFC 파싱 및 RDF 변환
│       ├── phase-2/           # SPARQL 쿼리 엔드포인트
│       ├── phase-3/           # 클라이언트 라이브러리
│       ├── phase-4/           # 성능 최적화 및 추론
│       ├── phase-5/           # 대시보드 및 CLI
│       ├── phase-6/           # 통합 테스트
│       └── phase-7/           # MVP 배포
├── src/                       # 소스 코드 (향후 생성)
│   ├── parser/                # IFC 파싱 모듈
│   ├── converter/             # RDF 변환 모듈
│   ├── api/                   # API 서버
│   ├── clients/               # 클라이언트 라이브러리
│   │   ├── python/
│   │   ├── java/
│   │   └── javascript/
│   ├── dashboard/             # 웹 대시보드
│   └── cli/                   # CLI 도구
├── tests/                     # 테스트 코드
├── references/                # 참조 문서 및 샘플 파일
│   ├── *.ifc                  # IFC 샘플 파일 (.gitignore)
│   └── *.pdf                  # 연구 논문
├── scripts/                   # 유틸리티 스크립트
├── docker/                    # Docker 설정
└── README.md                  # 프로젝트 개요
```

---

## Quick Start Guide

### Prerequisites
```bash
# Python 3.8+ 설치 확인
python --version

# Java 11+ 설치 확인 (Apache Jena 사용 시)
java -version

# Docker 설치 확인
docker --version
```

### Installation (향후 구현)
```bash
# 1. Repository 클론
git clone <repository-url>
cd bim-ontology

# 2. Python 가상환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Triple Store 실행 (Docker)
docker-compose up -d graphdb
```

### Basic Usage (향후 구현)
```bash
# IFC 파일 변환
python cli.py convert --input references/sample.ifc --output data/output.ttl

# SPARQL 쿼리 실행
python cli.py query --sparql "SELECT ?wall WHERE { ?wall a ifc:IfcWall }"

# API 서버 시작
python api/server.py --port 8000
```

---

## Architecture Snapshot

### Main Components

**1. IFC Parser Module**
- IFC4 파일 파싱 및 검증
- 엔티티 추출 (geometry, properties, relations)
- ifcopenshell 라이브러리 활용

**2. RDF Converter Module**
- IFC → ifcOWL 매핑
- RDF triple 생성 (Subject-Predicate-Object)
- Namespace 관리 및 최적화

**3. Triple Store**
- GraphDB 또는 Neo4j 저장소
- 100만+ triple 지원
- SPARQL 1.1 쿼리 엔진

**4. API Gateway**
- RESTful API (FastAPI)
- SPARQL 엔드포인트 (GET/POST)
- 인증 및 권한 관리

**5. Inference Engine**
- Apache Jena 추론 엔진
- SHACL/SWRL 규칙 기반 검증
- 파생 지식 추출

**6. Client Libraries**
- Python, Java, JavaScript 지원
- 통일된 API 인터페이스
- 쿼리 및 데이터 접근 추상화

**7. Dashboard & CLI**
- 웹 기반 시각화 대시보드
- CLI 도구 (변환, 쿼리, 검증)

### Entry Points

- **API Server**: `src/api/server.py` (향후 생성)
- **CLI Tool**: `src/cli/main.py` (향후 생성)
- **Converter**: `src/converter/ifc_to_rdf.py` (향후 생성)
- **Parser**: `src/parser/ifc_parser.py` (향후 생성)

### Data Flow

```
IFC File
    ↓
[IFC Parser] → ifcopenshell 파싱
    ↓
[Entity Extraction] → IfcWall, IfcSpace, IfcMaterial 등
    ↓
[RDF Converter] → ifcOWL 매핑, Triple 생성
    ↓
[Triple Store] → GraphDB/Neo4j 저장
    ↓
[SPARQL Query] → 건물 정보 분석
    ↓
[Client/Dashboard] → JSON/CSV/RDF 결과
```

---

## Current Focus

### Active Development Area
**Phase 0: 프로젝트 초기화 및 문서화**

**현재 작업**:
- ✅ PRD.md 작성 완료
- ✅ TECH-SPEC.md 작성 완료
- ✅ CONTEXT.md 생성 완료 (이 문서)
- 🚧 PROGRESS.md 생성 중
- 🚧 Phase 구조 초기화 (phase-0 ~ phase-7)

**다음 단계**:
1. PROGRESS.md 완성
2. Phase 0~7 폴더 및 문서 생성 (SPEC.md, TASKS.md, CHECKLIST.md)
3. 개발 환경 설정 (Python venv, ifcopenshell 설치)
4. IFC 샘플 파일 로딩 테스트

### Recent Changes
- 2026-02-03: 프로젝트 문서화 시작 (PRD, TECH-SPEC, CONTEXT)
- 2026-02-03: Phase 구조 설계 (8개 마일스톤)
- 2026-02-03: 기술 스택 확정 (ifcopenshell, Apache Jena, GraphDB)

---

## Token Optimization

### Essential Files for Context Loading

**최우선 로딩 파일 (P0)**:
- `docs/PRD.md` (요구사항 전체)
- `docs/CONTEXT.md` (이 문서)
- `docs/PROGRESS.md` (현재 진행 상황)

**현재 Phase 관련 파일 (P1)**:
- `docs/phases/phase-0/SPEC.md`
- `docs/phases/phase-0/TASKS.md`

**기술 참조 파일 (P2)**:
- `docs/TECH-SPEC.md` (상세 기술 명세)

**선택적 로딩**:
- 다른 Phase 문서 (작업 시작 시에만)
- 참조 논문 (특정 이슈 발생 시)

### Excludable Paths for Token Savings

**제외 가능 (대용량 파일)**:
- `references/*.ifc` (대용량 IFC 파일 - 필요 시에만)
- `references/*.pdf` (연구 논문 - 요약본만 참조)

**제외 가능 (시스템 파일)**:
- `.git/`, `__pycache__/`, `node_modules/`, `venv/`
- `*.pyc`, `*.log`, `.DS_Store`

**제외 가능 (미래 생성 파일)**:
- `src/` (아직 미생성)
- `tests/` (아직 미생성)
- `docker/` (아직 미생성)

### Context Loading Strategy

**세션 시작 시**:
1. CONTEXT.md 로딩 (프로젝트 전체 개요)
2. PROGRESS.md 로딩 (현재 상태 파악)
3. 현재 Phase SPEC.md + TASKS.md

**작업 중**:
- 관련 소스 코드 파일만 로딩
- 필요 시 PRD.md 또는 TECH-SPEC.md 참조

**Phase 전환 시**:
- 새 Phase의 SPEC.md, TASKS.md, CHECKLIST.md 로딩
- 이전 Phase 문서 언로드

---

## Related Documents

| 문서 | 설명 | 경로 |
|------|------|------|
| PRD | 제품 요구사항 정의서 | `docs/PRD.md` |
| TECH-SPEC | 기술 명세서 | `docs/TECH-SPEC.md` |
| PROGRESS | 진행 상황 추적 | `docs/PROGRESS.md` |
| Phase 0 | 프로젝트 초기화 | `docs/phases/phase-0/` |
| README | 프로젝트 개요 | `README.md` |

---

## Key Metrics

**프로젝트 범위**:
- IFC 파일: 대용량 IFC4/IFC2X3 파일 지원
- 예상 RDF triple 수: 100만~500만
- 지원 클라이언트: Python, Java, JavaScript
- 개발 기간: 3개월 (MVP)

**성능 목표**:
- 변환 속도: 200MB IFC → 30분 이내
- 쿼리 응답 시간: 단순 < 2초, 복잡 < 10초
- 동시 사용자: 최소 10명

**품질 목표**:
- 테스트 커버리지: 80% 이상
- 데이터 정확성: 99% 이상
- API 가동률: 95% 이상

---

## Contact & Resources

**Documentation**:
- PRD: 프로젝트 요구사항 및 사용자 스토리
- TECH-SPEC: 아키텍처 및 기술 상세
- PROGRESS: 마일스톤 및 작업 진행 상황

**Standards & References**:
- IFC4 Standard: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/
- ifcOWL: https://www.w3.org/community/lbd/
- ifcopenshell: https://ifcopenshell.org/
- Apache Jena: https://jena.apache.org/documentation/

**Sample Data**:
- IFC Files: `references/*.ifc` (IFC4/IFC2X3 샘플 - .gitignore)
- Research Papers: `references/*.pdf`

---

**Last Updated**: 2026-02-03
**Document Version**: v1.0
**Maintained By**: dev-docs-writer agent
