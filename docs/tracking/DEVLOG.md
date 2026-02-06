# Development Log (DEVLOG)

BIM Ontology 프로젝트 개발 과정 기록.

---

## Phase 0: 환경 설정 및 기본 검증 (2026-02-03)

### 목표

- Python 개발 환경 구축
- IFC 파일 로딩 가능 여부 확인
- 기본 RDF 변환 프로토타입 검증

### 수행 내용

1. Python 3.12.3 가상환경 생성 (`venv/`)
2. ifcopenshell 0.8.4, rdflib 7.5.0 등 핵심 패키지 설치
3. 프로젝트 디렉토리 구조 생성 (`src/`, `scripts/`, `tests/`, `data/`)
4. IFC 파일 로딩 테스트 (`scripts/test_ifc_loading.py`)
5. IFC 속성 상세 분석 (`scripts/test_ifc_properties.py`)
6. RDF 변환 프로토타입 (`scripts/test_rdf_conversion.py`)

### 발견된 문제점

#### F-001: IFC 스키마 버전 불일치

- **상태**: 확인됨, 대응 완료
- **내용**: 두 IFC 파일의 스키마 버전이 서로 다름
  - IFC4 샘플 파일 (대용량, 수만 엔티티)
  - IFC2X3 샘플 파일 (초대용량, 수천만 엔티티)
- **영향**: ifcOWL 네임스페이스가 스키마 버전별로 다름. IFC4 ADD2와 IFC2X3 TC1은 엔티티 구조도 차이가 있음.
- **대응**: `namespace_manager.py`에서 스키마별 네임스페이스 매핑 구현. `IFCParser`에서 두 스키마 모두 지원.

#### F-002: Navisworks 내보내기에 의한 타입 손실

- **상태**: 확인됨, 우회 구현
- **내용**: 두 IFC 파일 모두 Navisworks(Xbim.IO.Esent)로 내보내기한 것으로, 모든 건축 요소가 `IfcBuildingElementProxy`로 단일화됨. `IfcWall`, `IfcSlab`, `IfcColumn` 등의 구체적 타입 정보가 완전히 손실됨.
- **영향**: ifcOWL 기반의 정확한 타입 매핑 불가. 의미론적 쿼리의 정확도 저하.
- **대응**: 요소의 `Name` 속성에서 패턴 매칭(`classify_element_name`)으로 원래 타입을 추정하는 분류기 구현. 18개 카테고리(Slab, Wall, Beam, Pipe, Column 등) 분류 성공.

#### F-003: 빈 속성셋

- **상태**: 확인됨
- **내용**: `Pset_BuildingElementProxyCommon`이 3,911개 존재하지만 내부 속성(`HasProperties`)의 `NominalValue`가 모두 비어 있음.
- **영향**: 속성 기반 쿼리(재질, 크기, 용도 등) 불가.
- **대응**: 속성이 존재하는 경우에만 변환하도록 `_convert_property_sets`에서 null 체크 구현.

#### F-004: GlobalId가 없는 IFC 엔티티

- **상태**: Phase 1에서 수정됨
- **내용**: `IfcPresentationLayerAssignment`, `IfcSurfaceStyle`, `IfcColourRgb`, `IfcSIUnit` 등은 `IfcRoot`를 상속하지 않아 `GlobalId` 속성이 없음. 이들을 RDF로 변환 시도하면 `AttributeError` 발생.
- **영향**: 전체 변환 파이프라인이 중단됨.
- **대응**:
  1. `mapping.py`의 `GEOMETRY_TYPES`에 프레젠테이션/스타일/단위 타입 38종 추가하여 변환 스킵
  2. `_entity_uri()`에서 `GlobalId` 없을 시 `entity.id()`로 대체
  3. `_convert_physical_elements()`에서 `GlobalId` 존재 여부 사전 검증

#### F-005: 대용량 파일 처리

- **상태**: 확인됨, 모니터링 중
- **내용**: IFC2X3 샘플 파일은 약 1,700만 엔티티를 포함. 그 중 대부분이 기하 형상 데이터(IfcPolyLoop, IfcFaceBound, IfcFace 각 수백만).
- **영향**: 전체 변환 시 메모리와 시간 소요가 큼. 로딩만 70초.
- **대응**: 기하 형상 엔티티는 GEOMETRY_TYPES로 분류하여 RDF 변환에서 제외. 실제 변환 대상은 약 4,000개 수준.

#### F-006: SPARQL 변수명과 Python 예약어 충돌

- **상태**: 수정됨
- **내용**: rdflib에서 SPARQL 결과에 접근할 때 `row.class`, `row.count` 등의 변수명이 Python의 `class` 키워드 및 `tuple.count()` 메서드와 충돌.
- **대응**: SPARQL 변수명을 `?cls`, `?num` 등으로 변경.

### 데이터 특성 요약

| 파일 | 스키마 | 엔티티 규모 | 로딩 시간 | 물리적 요소 | 비고 |
|------|--------|-------------|-----------|-------------|------|
| IFC4 샘플 | IFC4 | 수만 | ~13초 | ~3,900 | 장비 시스템 |
| IFC2X3 샘플 | IFC2X3 | 수천만 | ~71초 | ~3,900 | 구조 시스템 |

### 이름 기반 분류 결과 (IFC4 샘플)

| 카테고리 | 수 | 비율 |
|----------|-----|------|
| Other | 1,720 | 44.0% |
| MemberPart | 570 | 14.6% |
| Aspect | 516 | 13.2% |
| Beam | 380 | 9.7% |
| Pipe | 244 | 6.2% |
| Insulation | 114 | 2.9% |
| Geometry | 114 | 2.9% |
| Column | 75 | 1.9% |
| Slab | 41 | 1.0% |
| 기타 (8개 분류) | 137 | 3.5% |

---

## Phase 1: IFC 파싱 및 RDF 변환 (2026-02-03)

### 목표

- IFCParser 클래스 모듈화
- RDFConverter 클래스 구현 (ifcOWL 기반)
- TripleStore 로컬 엔진 구현
- 테스트 커버리지 70% 이상

### 수행 내용

1. `src/parser/ifc_parser.py` - IFCParser 클래스 (IFC4/IFC2X3 지원)
2. `src/converter/namespace_manager.py` - ifcOWL 네임스페이스 관리
3. `src/converter/mapping.py` - IFC → ifcOWL 매핑 룰 (80+ 엔티티 타입)
4. `src/converter/ifc_to_rdf.py` - RDFConverter 클래스
5. `src/storage/triple_store.py` - rdflib 기반 로컬 트리플 스토어
6. `tests/test_integration.py` - 28개 테스트 (E2E 포함)

### 테스트 결과

- **28/28 테스트 통과** (100% pass rate)
- **전체 커버리지: 83%** (목표 70% 초과)
  - ifc_to_rdf.py: 86%
  - ifc_parser.py: 85%
  - triple_store.py: 92%
  - namespace_manager.py: 100%

### 아키텍처 결정

#### AD-001: 로컬 TripleStore 먼저 구현

- **결정**: GraphDB 외부 연동 대신 rdflib 기반 인메모리 스토어를 먼저 구현
- **이유**: 개발 초기에 외부 의존성을 최소화하고, SPARQL 쿼리 패턴을 검증한 후 외부 스토어로 확장
- **향후**: GraphDB/Fuseki 클라이언트를 TripleStore 인터페이스 하위에 추가

#### AD-002: 이름 기반 분류 전략

- **결정**: IfcBuildingElementProxy의 Name 속성에서 정규식 패턴 매칭으로 원래 BIM 타입 추정
- **이유**: Navisworks 내보내기에서 타입 정보가 손실되어 ifcOWL 직접 매핑이 불가
- **한계**: "Other" 카테고리가 44%로 높음. 향후 ML 기반 분류 또는 원본 모델 재내보내기가 필요

#### AD-003: 기하 형상 제외

- **결정**: 기하 형상(Geometry), 프레젠테이션(Presentation), 스타일(Style) 엔티티를 RDF 변환에서 제외
- **이유**: 전체 엔티티의 95%+ 가 기하 형상. 온톨로지 목적은 의미론적 관계 쿼리이며, 3D 좌표/메시 데이터는 RDF에 적합하지 않음.
- **향후**: 필요 시 기하 요약 정보(bounding box, centroid)만 추가

### 변환 통계

- **입력**: IFC4 샘플 파일 (수만 엔티티)
- **변환 대상**: 3,915 엔티티 (공간 4 + 물리적 3,911)
- **출력**: 39,217+ RDF 트리플
- **변환 시간**: ~0.7초
- **출력 파일**: 2,057 KB (Turtle 포맷)

---

## 향후 과제

### 완료된 과제

- [x] IFC 파싱 및 RDF 변환 (Phase 1)
- [x] SPARQL 쿼리 API (Phase 2)
- [x] Python 클라이언트 (Phase 3)
- [x] 성능 최적화 및 추론 (Phase 4)
- [x] 웹 대시보드 및 Docker (Phase 5)

### 향후 확장

- [ ] GraphDB/Apache Jena 외부 트리플 스토어 연동
- [ ] ifcOWL 공식 온톨로지 파일 통합
- [ ] "Other" 카테고리 세분화 (ML 기반 분류)
- [ ] 다중 온톨로지 융합 (EurOTL, SSN 등)
- [ ] 규정 자동 검증 (Code Compliance Checking)
- [ ] 3D 뷰어 통합 (IFC.js / Three.js)

---

## Phase 2: SPARQL 쿼리 엔드포인트 (2026-02-03)

### 목표

- FastAPI 기반 REST/SPARQL API 서버 구현
- SPARQL 쿼리 템플릿 10개 작성
- OpenAPI 문서 자동 생성

### 수행 내용

1. `src/api/server.py` - FastAPI 서버 (CORS, lifespan, RDF 자동 로딩/캐싱)
2. `src/api/routes/sparql.py` - SPARQL POST 엔드포인트
3. `src/api/routes/buildings.py` - Buildings/Storeys/Elements REST API
4. `src/api/routes/statistics.py` - 통계/카테고리/계층 구조 API
5. `src/api/models/` - Pydantic 요청/응답 모델
6. `src/api/queries/templates.py` - SPARQL 쿼리 템플릿 10개
7. `tests/test_api.py` - 20개 API 테스트

### 발견된 문제점

#### F-007: RDF 캐싱 전략

- **상태**: 구현됨
- **내용**: 대용량 IFC 파일을 매 서버 시작마다 변환하면 13초+ 소요
- **대응**: `data/rdf/` 디렉토리에 Turtle 파일로 캐싱. 이미 변환된 RDF 파일이 있으면 직접 로딩(~2초). `server.py`의 `load_data()` 함수에서 자동 판별.

#### F-008: TripleStore 전역 상태 관리

- **상태**: 구현됨
- **내용**: FastAPI는 비동기 프레임워크이므로 TripleStore 인스턴스를 안전하게 공유해야 함
- **대응**: `query_executor.py`에서 전역 `_store` 변수로 관리. `create_app(store=)` 으로 테스트 시 직접 주입 가능. 프로덕션에서는 `lifespan` 이벤트에서 초기화.

### 테스트 결과

- **20/20 API 테스트 통과**
- SPARQL 엔드포인트, Buildings API, Statistics API 모두 정상
- 잘못된 SPARQL 쿼리 시 500 에러, 빈 쿼리 시 422 검증 에러 정상 처리

### API 엔드포인트

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | 서비스 정보 |
| GET | `/health` | 헬스 체크 |
| POST | `/api/sparql` | SPARQL 쿼리 실행 |
| GET | `/api/buildings` | 건물 목록 |
| GET | `/api/buildings/{id}` | 건물 상세 |
| GET | `/api/storeys` | 층 목록 |
| GET | `/api/elements` | 요소 목록 (카테고리 필터, 페이지네이션) |
| GET | `/api/statistics` | 전체 통계 |
| GET | `/api/statistics/categories` | 카테고리별 통계 |
| GET | `/api/hierarchy` | 건물 계층 구조 |

---

## Phase 3: Python 클라이언트 라이브러리 (2026-02-03)

### 목표

- BIMOntologyClient 클래스 구현 (로컬/원격 모드)
- 헬퍼 메서드 (건물, 층, 요소, 통계 등)
- 사용 예제 5개

### 수행 내용

1. `src/clients/python/client.py` - BIMOntologyClient 클래스
   - `from_ifc()` - IFC 파일에서 직접 생성
   - `from_rdf()` - RDF 파일에서 생성
   - `from_api()` - 원격 API 서버 연결
2. `tests/test_client.py` - 13개 클라이언트 테스트
3. `examples/01~05_*.py` - 5개 사용 예제

### 아키텍처 결정

#### AD-004: 듀얼 모드 클라이언트

- **결정**: 동일한 API로 로컬(TripleStore 직접) 및 원격(HTTP API) 모드 지원
- **이유**: 개발/테스트 시에는 로컬 모드로 빠르게 반복하고, 배포 시에는 원격 API 서버 사용
- **구현**: `is_local` 속성으로 모드 판별. `query()` 메서드가 내부적으로 분기.

#### AD-005: Java 클라이언트 보류

- **결정**: Phase 3 스펙의 Java/JavaScript 클라이언트는 현 단계에서 보류
- **이유**: 프로젝트의 핵심 파이프라인(IFC→RDF→SPARQL)이 모두 Python으로 동작. REST API가 있으므로 다른 언어는 HTTP 호출로 충분.

### 테스트 결과

- **13/13 클라이언트 테스트 통과**
- 로컬 모드: IFC 로딩 → 변환 → 쿼리 전체 파이프라인 동작 확인

---

## 전체 Phase 0~3 요약 (2026-02-03)

### 테스트 현황

| Phase | 테스트 수 | 통과 | 커버리지 |
|-------|-----------|------|----------|
| Phase 0-1 | 28 | 28 | 83% |
| Phase 2 | 20 | 20 | - |
| Phase 3 | 13 | 13 | - |
| **전체** | **61** | **61** | **83%** |

### 모듈 현황

| 모듈 | 파일 수 | 주요 클래스 |
|------|---------|-------------|
| parser | 1 | IFCParser |
| converter | 3 | RDFConverter, NamespaceManager, Mapping |
| storage | 1 | TripleStore |
| api | 7 | FastAPI server, routes, models |
| clients | 1 | BIMOntologyClient |
| **전체** | **13** | - |

### 발견된 문제점 총 12건

| ID | 요약 | 상태 |
|----|------|------|
| F-001 | IFC 스키마 버전 불일치 (IFC4 vs IFC2X3) | 대응 완료 |
| F-002 | Navisworks 타입 손실 | 이름 기반 분류 |
| F-003 | 빈 속성셋 | 확인됨 |
| F-004 | GlobalId 없는 엔티티 | 수정됨 |
| F-005 | 대용량 기하 형상 | 제외 처리 |
| F-006 | SPARQL 변수명 충돌 | 수정됨 |
| F-007 | RDF 캐싱 전략 | 구현됨 |
| F-008 | TripleStore 전역 상태 | 구현됨 |
| F-009 | 스트리밍 변환기 메모리 이점 제한 | 확인됨 |
| F-010 | QueryCache 공백 정규화 한계 | 확인됨 |
| F-011 | 스트리밍 진행률 콜백 오차 | 확인됨 |

---

## Phase 4: 성능 최적화 및 추론 (2026-02-03)

### 목표

- 대용량 IFC 스트리밍 변환 (StreamingConverter)
- SPARQL 쿼리 결과 캐싱 (QueryCache)
- OWL/RDFS 추론 엔진 (OWLReasoner)
- 성능 벤치마크 리포트

### 수행 내용

1. `src/converter/streaming_converter.py` - StreamingConverter 클래스
   - 배치 단위 처리 (기본 1000개)
   - 진행률 콜백 지원
   - IFC4/IFC2X3 모두 지원
2. `src/cache/query_cache.py` - QueryCache LRU 캐시
   - SHA256 키 해싱, TTL 만료, LRU 제거
   - 공백 정규화로 동일 쿼리 인식
3. `src/inference/reasoner.py` - OWLReasoner 추론 엔진
   - owlrl 라이브러리 통합 (RDFS, OWL RL)
   - 5개 커스텀 SPARQL CONSTRUCT 규칙
   - 스키마 클래스 자동 생성 (StructuralElement, MEPElement, AccessElement)
4. `tests/test_phase4.py` - 29개 테스트
5. `scripts/benchmark_phase4.py` - 성능 벤치마크 스크립트

### 벤치마크 결과

#### 변환 성능

| 파일 | 스키마 | 엔티티 규모 | 로딩 | 일반 변환 | 스트리밍 변환 | 트리플 수 |
|------|--------|-------------|------|-----------|---------------|-----------|
| IFC4 샘플 | IFC4 | 수만 | ~13s | ~1.3s | ~2.9s | ~39K |
| IFC2X3 샘플 | IFC2X3 | 수천만 | ~69s | ~38s | ~40s | ~39K |

#### 쿼리 캐시 성능

| 측정 항목 | 값 |
|-----------|-----|
| Cold 평균 | 65.6ms |
| Hot 평균 | 0.004ms |
| 속도 향상 | **14,869x** |

#### OWL 추론 결과

| 측정 항목 | 값 |
|-----------|-----|
| 추론 전 트리플 | ~39K |
| 추론 후 트리플 | ~65K |
| 새 트리플 (커스텀 규칙) | 4,903 |
| 새 트리플 (RDFS) | 21,254 |
| 총 추론 트리플 | **26,157** (+66.7%) |
| 추론 시간 | 26.3s |

### 발견된 문제점

#### F-009: 스트리밍 변환기 메모리 이점 제한

- **상태**: 확인됨
- **내용**: StreamingConverter가 내부적으로 rdflib Graph에 모든 트리플을 적재하므로, 실제 메모리 피크 절감 효과가 제한적. 17M 엔티티 중 변환 대상이 ~4,000개로 기하 형상 제외 후 실제 부하가 작음.
- **영향**: IFC4 기준 일반 변환(1.3s) 대비 스트리밍(2.9s)이 오히려 느림. IFC2X3 대용량 파일도 차이 미미.
- **향후**: 파일 기반 점진적 직렬화(incremental serialization) 또는 chunked N-Triples 출력으로 개선 가능.

#### F-010: QueryCache 공백 정규화 한계

- **상태**: 확인됨 (Codex 리뷰 발견)
- **내용**: `_key()` 메서드가 `" ".join(query.split())`으로 공백을 정규화하지만, SPARQL 문자열 리터럴 내부의 공백도 변경됨. `WHERE { ?s ?p "hello  world" }` 같은 쿼리에서 잘못된 캐시 히트 가능.
- **영향**: 실제 BIM 쿼리에서는 문자열 리터럴 내 다중 공백이 드물어 실질적 영향 낮음.
- **향후**: 쿼리 파싱 기반 정규화 또는 raw 쿼리 해싱으로 전환 가능.

#### F-011: 스트리밍 진행률 콜백 오차

- **상태**: 확인됨 (Codex 리뷰 발견)
- **내용**: `convertible_types`에 공간 타입이 포함되지만 변환 루프에서 `continue`로 건너뜀. 진행률의 total은 공간 타입 포함, current는 미포함으로 100% 도달이 정확하지 않을 수 있음.
- **향후**: `convertible_types`에서 공간 타입을 사전 제외하여 정확한 진행률 제공.

### 아키텍처 결정

#### AD-006: owlrl 선택 (Apache Jena 대신)

- **결정**: Python 네이티브 owlrl 라이브러리로 OWL/RDFS 추론 구현
- **이유**: 외부 Java 프로세스(Jena) 의존성 제거. rdflib 그래프에 직접 적용 가능. 단, OWL RL 프로파일만 지원.
- **한계**: 대규모 그래프(100K+ 트리플)에서 성능 저하. 향후 Apache Jena Fuseki로 확장 가능.

#### AD-007: 인메모리 LRU 캐시 (Redis 대신)

- **결정**: `collections.OrderedDict` 기반 인메모리 LRU 캐시 구현
- **이유**: 단일 프로세스 환경에서 충분. Redis 외부 의존성 제거. 캐시 히트율 14,000x+ 속도 향상 확인.
- **한계**: 프로세스 재시작 시 캐시 소멸. 다중 워커 환경에서는 Redis 필요.

### 테스트 결과

| Phase | 테스트 수 | 통과 | 커버리지 |
|-------|-----------|------|----------|
| Phase 0-1 | 28 | 28 | - |
| Phase 2 | 20 | 20 | - |
| Phase 3 | 13 | 13 | - |
| Phase 4 | 29 | 29 | - |
| **전체** | **90** | **90** | **85%** |

### 커버리지 상세

| 모듈 | 커버리지 | 비고 |
|------|----------|------|
| query_cache.py | 100% | |
| reasoner.py | 88% | OWL RL 추론 미테스트 |
| streaming_converter.py | 88% | PropertySet 변환 미테스트 |
| namespace_manager.py | 100% | |
| triple_store.py | 95% | |
| ifc_to_rdf.py | 86% | |
| ifc_parser.py | 85% | |

### Codex CLI 교차 리뷰 결과

Phase 4에서 Codex CLI(`codex exec review`)를 활용한 교차 리뷰를 처음 도입. Claude + Codex 듀얼 리뷰 패턴으로 F-010, F-011 문제를 발견함. `codex-reviewer` 에이전트를 `.claude/agents/`에 추가하여 향후 자동 교차 검증 워크플로우 구축.

---

## Phase 5: 웹 대시보드 및 배포 (2026-02-03)

### 목표

- 웹 기반 대시보드로 BIM 온톨로지 데이터 시각적 탐색
- Docker 컨테이너화 및 배포 설정
- API 추론 엔드포인트 추가

### 수행 내용

1. `src/dashboard/index.html` - 웹 대시보드 SPA
   - 다크 테마 (Tailwind CSS CDN)
   - 5개 탭: Overview, Buildings, Elements, SPARQL, Reasoning
2. `src/dashboard/app.js` - 대시보드 로직
   - Chart.js 통합 (도넛 차트, 수평 바 차트)
   - 건물 계층 트리 렌더러
   - 요소 테이블 (카테고리 필터, 검색, 페이지네이션)
   - SPARQL 쿼리 에디터 (6개 템플릿)
   - 추론 실행 UI (before/after 통계)
3. `src/api/routes/reasoning.py` - 추론 API 엔드포인트
   - `POST /api/reasoning` → OWLReasoner.run_all() 실행
4. `src/api/server.py` 업데이트
   - StaticFiles 마운트 (`/static` → dashboard/)
   - `/` 라우트를 대시보드 HTML 서빙으로 변경
5. `Dockerfile` - Python 3.12-slim 기반 컨테이너
6. `docker-compose.yml` - 단일 서비스 구성

### 대시보드 탭 상세

| 탭 | 기능 | 데이터 소스 |
|----|------|-------------|
| Overview | 통계 카드 + 카테고리 분포 차트 | `/api/statistics`, `/api/statistics/categories` |
| Buildings | 건물-층 계층 트리 + 층 상세 | `/api/hierarchy`, `/api/buildings/{id}` |
| Elements | 필터/검색/페이지네이션 테이블 | `/api/elements` |
| SPARQL | 쿼리 에디터 + 결과 테이블 | `/api/sparql` |
| Reasoning | 추론 실행 + 추론 결과 | `/api/reasoning`, `/api/sparql` |

### API 엔드포인트 추가

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/reasoning` | OWL/RDFS 추론 실행 |
| GET | `/` | 웹 대시보드 (HTML) |
| GET | `/static/*` | 대시보드 정적 파일 |

### 아키텍처 결정

#### AD-008: SPA vs 서버 사이드 렌더링

- **결정**: 단일 HTML + vanilla JS로 클라이언트 사이드 SPA 구현
- **이유**: React/Vue 등 프레임워크 빌드 과정 불필요. CDN 기반 Tailwind CSS + Chart.js로 충분. FastAPI의 StaticFiles로 간단히 서빙.
- **한계**: 대규모 데이터셋에서 클라이언트 렌더링 성능 저하 가능. 향후 가상 스크롤링 또는 서버 사이드 페이지네이션 강화 필요.

#### AD-009: Docker 단일 서비스 구성

- **결정**: API + 대시보드를 단일 Docker 컨테이너로 구성
- **이유**: 현 단계에서는 단일 프로세스(uvicorn)로 API와 정적 파일 모두 서빙 가능. 외부 DB 없이 인메모리 TripleStore 사용.
- **향후**: GraphDB/Fuseki 연동 시 multi-container 구성(docker-compose)으로 확장.

### 테스트 결과

| Phase | 테스트 수 | 통과 | 비고 |
|-------|-----------|------|------|
| Phase 0-1 | 28 | 28 | IFC 파싱, RDF 변환 |
| Phase 2 | 21 | 21 | API 테스트 (+1 reasoning) |
| Phase 3 | 13 | 13 | 클라이언트 |
| Phase 4 | 29 | 29 | 캐시, 추론, 스트리밍 |
| **전체** | **91** | **91** | **85%+ 커버리지** |
