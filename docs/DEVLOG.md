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
  - `nwd4op-12.ifc`: **IFC4** (224MB, 66,538 엔티티)
  - `nwd23op-12.ifc`: **IFC2X3** (828MB, 16,945,319 엔티티)
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
- **내용**: `nwd23op-12.ifc` (828MB)는 1,700만 엔티티를 포함. 그 중 대부분이 기하 형상 데이터(IfcPolyLoop 4.6M, IfcFaceBound 4.6M, IfcFace 4.6M).
- **영향**: 전체 변환 시 메모리와 시간 소요가 큼. 로딩만 70초.
- **대응**: 기하 형상 엔티티는 GEOMETRY_TYPES로 분류하여 RDF 변환에서 제외. 실제 변환 대상은 약 4,000개 수준.

#### F-006: SPARQL 변수명과 Python 예약어 충돌

- **상태**: 수정됨
- **내용**: rdflib에서 SPARQL 결과에 접근할 때 `row.class`, `row.count` 등의 변수명이 Python의 `class` 키워드 및 `tuple.count()` 메서드와 충돌.
- **대응**: SPARQL 변수명을 `?cls`, `?num` 등으로 변경.

### 데이터 특성 요약

| 파일 | 스키마 | 크기 | 엔티티 수 | 로딩 시간 | 물리적 요소 | 비고 |
|------|--------|------|-----------|-----------|-------------|------|
| nwd4op-12.ifc | IFC4 | 224MB | 66,538 | 13초 | 3,911 | 장비 시스템 |
| nwd23op-12.ifc | IFC2X3 | 828MB | 16,945,319 | 71초 | 3,980 | 구조 시스템 |

### 이름 기반 분류 결과 (nwd4op-12.ifc)

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

- **입력**: 66,538 IFC 엔티티 (nwd4op-12.ifc)
- **변환 대상**: 3,915 엔티티 (공간 4 + 물리적 3,911)
- **출력**: 39,217+ RDF 트리플
- **변환 시간**: ~0.7초
- **출력 파일**: 2,057 KB (Turtle 포맷)

---

## 향후 과제

### 단기 (Phase 2)

- [ ] ifcOWL 공식 온톨로지 파일 통합
- [ ] "Other" 카테고리 세분화 (추가 패턴 분석)
- [ ] IFC2X3 파일 전체 변환 테스트
- [ ] SPARQL 쿼리 라이브러리 구축

### 중기 (Phase 3-4)

- [ ] GraphDB/Apache Jena 외부 트리플 스토어 연동
- [ ] 온톨로지 추론(reasoning) 적용
- [ ] REST API 구현 (FastAPI)
- [ ] 대용량 파일 스트리밍 처리

### 장기 (Phase 5+)

- [ ] 웹 UI 대시보드
- [ ] 다중 온톨로지 융합 (EurOTL, SSN 등)
- [ ] 규정 자동 검증 (Code Compliance Checking)
