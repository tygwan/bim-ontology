# IFC to Ontology DB Schema PRD

## 메타데이터
- **작성자**: PRD Writer Agent
- **작성일**: 2026-02-03
- **버전**: v1.0
- **상태**: Draft
- **프로젝트명**: IFC to Ontology DB Schema
- **프로젝트 코드**: BIM-ONTOLOGY

---

## 1. 개요 (Overview)

Building Information Modeling (BIM) 산업의 표준 데이터 포맷인 IFC (Industry Foundation Classes) 파일을 ontology 기반 데이터베이스 스키마로 변환하고, SPARQL 등의 쿼리 언어를 통해 건물 정보를 효율적으로 분석 및 관리할 수 있는 시스템을 구축합니다.

### 1.1 배경 (Background)

**문제 상황**
- IFC 파일은 건물의 기하학적 정보, 구조, 자재, 시스템 등을 포함하는 복잡한 EXPRESS 스키마 기반 데이터 구조를 가짐
- 대용량 IFC 파일 (수백 MB)의 효율적인 쿼리 및 분석이 어려움
- BIM 데이터와 다른 건설 관리 시스템(예: AMS, FM) 간의 상호운용성 부족
- 전통적인 관계형 데이터베이스로는 건물 정보의 복잡한 관계와 계층 구조를 표현하기 어려움

**왜 Ontology인가?**
- ifcOWL은 IFC EXPRESS 스키마를 OWL (Web Ontology Language)로 표현한 표준
- RDF triple store를 통한 유연한 데이터 모델링 및 쿼리
- 추론 엔진(Apache Jena)을 활용한 지능적 데이터 분석
- SPARQL을 통한 강력한 의미론적 쿼리 지원
- 다양한 프로그래밍 언어 (Python, Java, JavaScript)와의 통합 용이성

**보유 자산**
- IFC4/IFC2X3 대용량 파일 (references/ 디렉토리)
- 참조 논문 2편 (ifcOWL 연구, BIM-AMS 통합)
- IFC4 스키마 표준 문서

### 1.2 목표 (Goals)

- [ ] **G1**: IFC 파일을 ontology 기반 RDF triple store로 변환하는 파이프라인 구축
- [ ] **G2**: 변환된 데이터에 대한 SPARQL 쿼리 인터페이스 제공
- [ ] **G3**: 대용량 IFC 파일 (200MB+) 처리 성능 최적화
- [ ] **G4**: Python/Java/JavaScript 클라이언트 라이브러리 제공
- [ ] **G5**: 건물 구성요소, 공간, 자재 정보에 대한 분석 대시보드 구축

### 1.3 비목표 (Non-Goals)

**이번 범위에서 제외되는 것들**
- IFC2x3 및 IFC4 이전 버전 지원 (IFC4에만 집중)
- 3D 시각화 및 렌더링 기능
- IFC 파일 편집 및 재생성 기능
- 실시간 협업 기능
- 모바일 애플리케이션 개발
- 블록체인 기반 BIM 데이터 관리
- 프로젝트 관리 및 워크플로우 자동화

---

## 2. 요구사항 (Requirements)

### 2.1 기능 요구사항 (Functional Requirements)

| ID | 요구사항 | 우선순위 | 상태 |
|----|---------|---------|------|
| FR-001 | IFC4 파일 파싱 및 검증 (ifcopenshell 기반) | P0 | [ ] |
| FR-002 | IFC 데이터를 RDF triple로 변환 (ifcOWL 스키마 준수) | P0 | [ ] |
| FR-003 | GraphDB 또는 Neo4j에 RDF triple 저장 | P0 | [ ] |
| FR-004 | SPARQL 쿼리 엔드포인트 제공 (GET/POST) | P0 | [ ] |
| FR-005 | 건물 구성요소 조회 쿼리 (IfcWall, IfcColumn, IfcBeam 등) | P0 | [ ] |
| FR-006 | 공간 정보 조회 쿼리 (IfcSpace, IfcBuilding, IfcStorey) | P0 | [ ] |
| FR-007 | 자재 및 속성 정보 조회 (IfcMaterial, IfcPropertySet) | P1 | [ ] |
| FR-008 | Apache Jena 추론 엔진 통합 (규칙 기반 추론) | P1 | [ ] |
| FR-009 | Python 클라이언트 라이브러리 (쿼리 및 데이터 접근) | P1 | [ ] |
| FR-010 | Java 클라이언트 라이브러리 (Enterprise 통합) | P1 | [ ] |
| FR-011 | JavaScript/Node.js 클라이언트 라이브러리 (웹 통합) | P2 | [ ] |
| FR-012 | RESTful API (JSON 응답) | P1 | [ ] |
| FR-013 | 배치 처리 및 대용량 파일 스트리밍 변환 | P0 | [ ] |
| FR-014 | 변환 진행 상황 모니터링 및 로깅 | P1 | [ ] |
| FR-015 | 기본 분석 대시보드 (건물 통계, 자재 집계) | P2 | [ ] |
| FR-016 | 쿼리 결과 내보내기 (CSV, JSON, RDF/XML) | P1 | [ ] |
| FR-017 | 쿼리 템플릿 및 예제 라이브러리 | P1 | [ ] |
| FR-018 | 데이터 검증 및 무결성 체크 | P1 | [ ] |

### 2.2 비기능 요구사항 (Non-Functional Requirements)

| ID | 요구사항 | 기준 |
|----|---------|------|
| NFR-001 | 성능 - 변환 속도 | 200MB IFC 파일을 30분 이내에 변환 |
| NFR-002 | 성능 - 쿼리 응답 시간 | 단순 쿼리 < 2초, 복잡한 집계 쿼리 < 10초 |
| NFR-003 | 확장성 | 최대 500MB IFC 파일 처리 지원 |
| NFR-004 | 확장성 | 최소 100만 개 이상의 triple 저장 및 쿼리 |
| NFR-005 | 가용성 | 시스템 가동률 95% 이상 |
| NFR-006 | 안정성 | 변환 중 오류 발생 시 롤백 및 복구 메커니즘 |
| NFR-007 | 보안 | SPARQL 엔드포인트 인증 및 권한 관리 |
| NFR-008 | 보안 | 민감한 건물 정보에 대한 접근 제어 |
| NFR-009 | 호환성 | IFC4 표준 준수 |
| NFR-010 | 호환성 | Python 3.8+, Java 11+, Node.js 14+ 지원 |
| NFR-011 | 유지보수성 | 코드 커버리지 80% 이상 |
| NFR-012 | 유지보수성 | API 문서화 (OpenAPI 3.0) |
| NFR-013 | 사용성 | CLI 도구 제공 (변환, 쿼리, 검증) |
| NFR-014 | 사용성 | 명확한 에러 메시지 및 로깅 |
| NFR-015 | 이식성 | Docker 컨테이너 지원 |
| NFR-016 | 이식성 | Linux, macOS, Windows 환경 지원 |

---

## 3. 사용자 스토리 (User Stories)

### US-001: IFC 파일 변환
**As a** BIM 엔지니어
**I want to** 대용량 IFC 파일을 ontology 데이터베이스로 변환하고
**So that** 건물 정보를 의미론적으로 쿼리하고 분석할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] IFC4 파일 업로드 및 검증
- [ ] 변환 진행 상황 실시간 모니터링
- [ ] 변환 완료 후 통계 정보 제공 (triple 수, 엔티티 수)
- [ ] 변환 중 발생한 경고 및 오류 로그 확인
- [ ] 변환된 데이터 GraphDB/Neo4j 저장 확인

---

### US-002: 건물 구성요소 조회
**As a** 건축 데이터 분석가
**I want to** 특정 건물의 모든 벽, 기둥, 보 정보를 조회하고
**So that** 구조적 분석 및 자재 견적을 수행할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] SPARQL 쿼리로 IfcWall, IfcColumn, IfcBeam 조회
- [ ] 구성요소별 속성 정보 (치수, 자재, 위치) 포함
- [ ] 쿼리 결과를 JSON 또는 CSV로 내보내기
- [ ] 쿼리 실행 시간 2초 이내
- [ ] Python/Java 클라이언트로 동일한 쿼리 실행 가능

---

### US-003: 공간 정보 분석
**As a** 시설 관리자
**I want to** 건물의 층별 공간 구조와 면적 정보를 조회하고
**So that** 공간 활용도를 분석하고 시설 관리 계획을 수립할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] IfcBuilding, IfcStorey, IfcSpace 계층 구조 조회
- [ ] 각 공간의 면적, 용도, 위치 정보 포함
- [ ] 층별 공간 집계 쿼리 (총 면적, 공간 수)
- [ ] 시각적 대시보드에 공간 통계 표시
- [ ] 쿼리 결과 기반 리포트 생성 (PDF/Excel)

---

### US-004: 자재 정보 및 속성 관리
**As a** 자재 관리자
**I want to** 건물에 사용된 모든 자재 정보와 속성을 추출하고
**So that** 자재 발주 및 재고 관리를 효율화할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] IfcMaterial 및 IfcMaterialLayer 정보 조회
- [ ] IfcPropertySet 및 커스텀 속성 추출
- [ ] 자재별 사용량 집계 (예: 콘크리트 m³, 철근 ton)
- [ ] 자재 정보를 자재 관리 시스템(ERP)에 전송
- [ ] 자재 변경 이력 추적

---

### US-005: 추론 기반 데이터 검증
**As a** 품질 관리자
**I want to** Apache Jena 추론 엔진을 활용하여 건물 데이터의 무결성을 검증하고
**So that** 설계 오류 및 불일치를 조기에 발견할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] IFC 데이터에 대한 SHACL 또는 SWRL 규칙 정의
- [ ] 추론 엔진 실행 및 위반 사항 검출
- [ ] 검증 결과 리포트 생성 (위반 유형, 영향 범위)
- [ ] 자동화된 검증 파이프라인 구축
- [ ] 검증 규칙 커스터마이징 가능

---

### US-006: 다중 언어 클라이언트 통합
**As a** 소프트웨어 개발자
**I want to** Python, Java, JavaScript 클라이언트 라이브러리를 사용하여
**So that** 내 애플리케이션에 BIM 데이터 쿼리 기능을 쉽게 통합할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] 각 언어별 클라이언트 라이브러리 제공
- [ ] 통일된 API 인터페이스 (쿼리, 연결, 결과 처리)
- [ ] 코드 예제 및 튜토리얼 제공
- [ ] 클라이언트 라이브러리 문서화 (API reference)
- [ ] 패키지 관리자 (pip, Maven, npm)를 통한 설치

---

### US-007: 대시보드 기반 시각화
**As a** 프로젝트 관리자
**I want to** 웹 대시보드에서 건물 통계 및 분석 결과를 시각화하고
**So that** 프로젝트 진행 상황을 직관적으로 파악할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] 건물 구성요소 통계 (벽, 기둥, 보 개수)
- [ ] 공간 정보 시각화 (층별 면적 분포)
- [ ] 자재 사용량 차트 (막대 그래프, 파이 차트)
- [ ] 쿼리 성능 모니터링 (응답 시간, 쿼리 빈도)
- [ ] 대시보드 커스터마이징 (위젯 추가/제거)

---

### US-008: 확장성 및 성능 최적화
**As a** 시스템 관리자
**I want to** 대용량 IFC 파일을 처리하고 다수의 동시 쿼리를 처리할 수 있도록
**So that** 엔터프라이즈 환경에서 안정적인 서비스를 제공할 수 있다

**인수 조건 (Acceptance Criteria)**:
- [ ] 500MB IFC 파일 처리 성공
- [ ] 병렬 처리 및 스트리밍 변환 지원
- [ ] 쿼리 캐싱 및 인덱싱 최적화
- [ ] 부하 테스트 (100명 동시 사용자)
- [ ] 수평 확장 가능 (multiple database nodes)

---

## 4. 제약사항 (Constraints)

### 4.1 기술적 제약

**데이터 처리**
- IFC4 스키마 복잡성: 800개 이상의 엔티티 클래스, 복잡한 관계 구조
- 대용량 파일 처리: 메모리 제약 (최대 16GB RAM 환경 가정)
- RDF triple 수: 200MB IFC 파일 → 약 100만~500만 triple 생성

**기술 스택**
- ifcopenshell: Python 3.8+ 필수
- Apache Jena: Java 11+ 필수
- GraphDB: 메모리 요구사항 (최소 4GB)
- Neo4j: 디스크 I/O 성능 의존

**표준 및 호환성**
- ifcOWL 표준 준수 (버전 4.0)
- SPARQL 1.1 쿼리 언어
- RDF/XML, Turtle, JSON-LD 직렬화 포맷

### 4.2 비즈니스 제약

**프로젝트 제약**
- 개발 기간: 3개월 (MVP)
- 예산: 제한된 클라우드 리소스 (1-2 VM)
- 팀 구성: 1-2명 개발자 (풀타임 아님)

**데이터 제약**
- 보유 IFC 샘플 파일: 2개 (다양성 제한)
- 실제 건설 프로젝트 데이터 접근 제한

**운영 제약**
- 초기 단계: 로컬 환경 또는 단일 서버 배포
- 24/7 운영 불가 (초기 버전)
- 전문 DBA 없음

---

## 5. 의존성 (Dependencies)

### 5.1 외부 라이브러리 및 도구

**핵심 의존성 (P0)**
- **ifcopenshell** (v0.7.0+): IFC 파싱 및 데이터 추출
- **Apache Jena** (v4.0+): RDF 처리 및 추론 엔진
- **GraphDB** (Free Edition) 또는 **Neo4j** (Community Edition): RDF triple store
- **RDFLib** (Python): RDF 데이터 조작

**클라이언트 라이브러리 (P1)**
- **SPARQLWrapper** (Python): SPARQL 쿼리 클라이언트
- **Apache Jena ARQ** (Java): SPARQL 쿼리 실행
- **sparql-client** (JavaScript/Node.js): 웹 통합

**웹 프레임워크 및 API (P1)**
- **FastAPI** 또는 **Flask** (Python): RESTful API 서버
- **Spring Boot** (Java): Enterprise API 서버 (선택적)
- **React** 또는 **Vue.js**: 대시보드 프론트엔드

**인프라 및 배포 (P2)**
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션
- **Nginx**: 리버스 프록시 및 로드 밸런싱

### 5.2 데이터 의존성

- **IFC4 스키마 정의**: BuildingSMART 공식 스키마
- **ifcOWL 온톨로지**: W3C LBD CG (Linked Building Data Community Group)
- **참조 논문 및 문서**: ifcOWL 구현 가이드, BIM-AMS 통합 사례

### 5.3 다른 시스템과의 통합

**현재 범위 내 (P1)**
- 자재 관리 시스템 (ERP) 연동 (RESTful API)
- 시설 관리 시스템 (FM/AMS) 데이터 동기화

**향후 확장 (P2)**
- BIM 360, Revit 등 BIM 저작 도구 직접 연동
- GIS (Geographic Information System) 통합
- IoT 센서 데이터 통합

---

## 6. 아키텍처 개요 (Architecture Overview)

### 6.1 시스템 구성요소

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ Python Client│ Java Client  │ JS Client    │ Web Dashboard   │
└──────────────┴──────────────┴──────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
│                  (RESTful API / SPARQL Endpoint)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Processing Layer                         │
├───────────────────────┬─────────────────────────────────────┤
│ IFC Parser            │ RDF Converter                        │
│ (ifcopenshell)        │ (ifcOWL mapping)                     │
│                       │                                      │
│ Data Validator        │ Inference Engine                     │
│                       │ (Apache Jena)                        │
└───────────────────────┴─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Storage Layer                          │
├─────────────────────────┬───────────────────────────────────┤
│ GraphDB / Neo4j         │ Query Cache                        │
│ (RDF Triple Store)      │ (Redis)                            │
└─────────────────────────┴───────────────────────────────────┘
```

### 6.2 데이터 흐름

1. **변환 흐름**: IFC File → ifcopenshell Parser → RDF Converter → Triple Store
2. **쿼리 흐름**: Client → API Gateway → SPARQL Engine → Triple Store → Result
3. **추론 흐름**: Triple Store → Jena Inference Engine → Derived Triples → Triple Store

---

## 7. 성공 기준 (Success Criteria)

### 7.1 MVP (Minimum Viable Product) 기준

- [ ] **SC-001**: 보유한 IFC4/IFC2X3 파일을 성공적으로 변환
- [ ] **SC-002**: 변환된 데이터에 대해 최소 10개의 표준 SPARQL 쿼리 실행 가능
- [ ] **SC-003**: Python 클라이언트 라이브러리로 쿼리 실행 가능
- [ ] **SC-004**: 건물 구성요소 조회 쿼리 응답 시간 < 2초
- [ ] **SC-005**: RESTful API를 통한 JSON 응답 제공
- [ ] **SC-006**: CLI 도구로 변환 및 쿼리 실행 가능
- [ ] **SC-007**: 기본 웹 대시보드에서 건물 통계 시각화

### 7.2 성능 기준

- [ ] **PERF-001**: 200MB IFC 파일 변환 시간 < 30분
- [ ] **PERF-002**: 단순 쿼리 (엔티티 조회) 응답 시간 < 2초
- [ ] **PERF-003**: 복잡한 집계 쿼리 응답 시간 < 10초
- [ ] **PERF-004**: 최소 100만 개 triple 저장 및 쿼리 가능
- [ ] **PERF-005**: 동시 10명 사용자 지원 (평균 응답 시간 유지)

### 7.3 품질 기준

- [ ] **QA-001**: 단위 테스트 커버리지 80% 이상
- [ ] **QA-002**: 통합 테스트 (IFC → RDF → Query) 성공
- [ ] **QA-003**: API 문서화 (OpenAPI 3.0) 완료
- [ ] **QA-004**: 사용자 가이드 및 튜토리얼 제공
- [ ] **QA-005**: 변환 중 데이터 손실 < 1%

### 7.4 비즈니스 기준

- [ ] **BIZ-001**: 건축 데이터 분석가가 기존 방식 대비 50% 시간 절감
- [ ] **BIZ-002**: 자재 관리자가 자재 정보 추출 자동화 (수동 → 자동)
- [ ] **BIZ-003**: 프로젝트 관리자가 실시간 건물 통계 확인 가능

---

## 8. 마일스톤 (Milestones)

| 단계 | 내용 | 예상일 | 담당자 | 상태 |
|------|------|--------|--------|------|
| **M1** | 프로젝트 초기화 및 환경 설정 | 2026-02-10 | Dev Team | [ ] |
| | - 기술 스택 설치 및 검증 | | | |
| | - IFC 샘플 파일 로딩 테스트 | | | |
| | - GraphDB/Neo4j 설치 및 구성 | | | |
| **M2** | IFC 파싱 및 RDF 변환 기능 구현 | 2026-02-24 | Dev Team | [ ] |
| | - ifcopenshell 기반 IFC 파서 개발 | | | |
| | - ifcOWL 기반 RDF 변환 모듈 개발 | | | |
| | - Triple Store 저장 기능 구현 | | | |
| | - 단위 테스트 및 검증 | | | |
| **M3** | SPARQL 쿼리 엔드포인트 구축 | 2026-03-10 | Dev Team | [ ] |
| | - SPARQL 쿼리 엔진 통합 | | | |
| | - RESTful API 서버 구현 (FastAPI) | | | |
| | - 표준 쿼리 템플릿 10개 작성 | | | |
| | - API 문서화 (OpenAPI) | | | |
| **M4** | 클라이언트 라이브러리 개발 | 2026-03-24 | Dev Team | [ ] |
| | - Python 클라이언트 라이브러리 | | | |
| | - Java 클라이언트 라이브러리 | | | |
| | - 코드 예제 및 튜토리얼 작성 | | | |
| **M5** | 성능 최적화 및 추론 기능 | 2026-04-07 | Dev Team | [ ] |
| | - 대용량 파일 스트리밍 처리 | | | |
| | - 쿼리 캐싱 및 인덱싱 최적화 | | | |
| | - Apache Jena 추론 엔진 통합 | | | |
| | - 부하 테스트 및 튜닝 | | | |
| **M6** | 대시보드 및 CLI 도구 개발 | 2026-04-21 | Dev Team | [ ] |
| | - 웹 대시보드 (React 기반) | | | |
| | - CLI 도구 (변환, 쿼리, 검증) | | | |
| | - 데이터 시각화 (차트, 그래프) | | | |
| **M7** | 통합 테스트 및 문서화 | 2026-05-05 | Dev Team | [ ] |
| | - End-to-End 테스트 | | | |
| | - 사용자 가이드 작성 | | | |
| | - 배포 가이드 (Docker) | | | |
| | - 코드 리뷰 및 품질 검증 | | | |
| **M8** | MVP 배포 및 검증 | 2026-05-15 | Dev Team | [ ] |
| | - 프로덕션 환경 배포 | | | |
| | - 실제 데이터로 검증 | | | |
| | - 성능 및 품질 기준 확인 | | | |
| | - 프로젝트 회고 및 문서화 | | | |

### 마일스톤 타임라인 (Gantt)

```
2026년
FEB    MAR    APR    MAY
|──M1──|──M2──|──M3──|──M4──|──M5──|──M6──|──M7──|M8|
Week: 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
```

---

## 9. 위험 관리 (Risk Management)

| 위험 ID | 위험 내용 | 확률 | 영향 | 완화 전략 |
|---------|----------|------|------|----------|
| R-001 | IFC 파싱 복잡성으로 변환 오류 발생 | 높음 | 높음 | - ifcopenshell 최신 버전 사용<br>- 단계별 검증 로직 구현<br>- 샘플 파일로 충분한 테스트 |
| R-002 | 대용량 파일 처리 시 메모리 부족 | 중간 | 높음 | - 스트리밍 처리 구현<br>- 배치 처리 및 청크 분할<br>- 메모리 프로파일링 |
| R-003 | SPARQL 쿼리 성능 저하 | 중간 | 중간 | - 쿼리 최적화 (인덱스, 캐싱)<br>- 쿼리 복잡도 제한<br>- 데이터베이스 튜닝 |
| R-004 | ifcOWL 표준 변경 또는 불일치 | 낮음 | 중간 | - IFC4 최신 표준 참조<br>- 버전 관리 엄격히 수행<br>- 변환 규칙 문서화 |
| R-005 | 기술 스택 학습 곡선 | 중간 | 낮음 | - 참조 논문 및 예제 코드 활용<br>- 단계별 프로토타입 개발 |
| R-006 | 실제 프로젝트 데이터 접근 제한 | 높음 | 낮음 | - 공개 IFC 샘플 추가 확보<br>- 합성 데이터 생성 |
| R-007 | 배포 환경 리소스 부족 | 중간 | 중간 | - Docker 기반 경량화<br>- 클라우드 무료 티어 활용<br>- 수평 확장 설계 |

---

## 10. 측정 지표 (Metrics)

### 10.1 개발 진행 지표

- **코드 커밋 수**: 주간 목표 20+ 커밋
- **이슈 해결율**: 주간 열린 이슈의 80% 해결
- **테스트 커버리지**: 매 스프린트마다 +5% 증가
- **문서화 진행률**: 각 마일스톤 완료 시 100%

### 10.2 시스템 성능 지표

- **변환 처리량**: IFC 파일 크기(MB) / 변환 시간(분)
- **쿼리 응답 시간**: P50, P90, P99
- **데이터베이스 크기**: RDF triple 수, 디스크 사용량
- **시스템 리소스**: CPU, 메모리, I/O 사용률

### 10.3 품질 지표

- **버그 밀도**: 1000 LOC당 버그 수 < 5
- **API 가동률**: 월간 가동률 > 95%
- **쿼리 성공률**: 전체 쿼리의 > 98% 성공
- **데이터 정확성**: 변환 후 데이터 검증 통과율 > 99%

### 10.4 사용자 지표

- **사용자 만족도**: 설문 조사 (5점 척도) 평균 > 4.0
- **기능 사용률**: 핵심 기능 (변환, 쿼리) 사용 빈도
- **문서 접근율**: 사용자 가이드 페이지 뷰

---

## 11. 참조 문서 (References)

### 11.1 표준 및 스펙

- **IFC4 Standard**: [BuildingSMART IFC4 Documentation](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/)
- **ifcOWL**: [W3C LBD Community Group - ifcOWL](https://www.w3.org/community/lbd/)
- **SPARQL 1.1**: [W3C SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- **OWL 2**: [W3C OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/)

### 11.2 참조 논문

1. **ifcOWL 연구** (references/ 디렉토리)
   - IFC EXPRESS를 OWL로 변환하는 방법론
   - 의미론적 쿼리 및 추론 사례

2. **BIM-AMS 통합** (references/ 디렉토리)
   - Ontology 기반 BIM과 Asset Management System 통합
   - 실제 건설 프로젝트 사례 연구

### 11.3 기술 문서

- **ifcopenshell Documentation**: [https://ifcopenshell.org/](https://ifcopenshell.org/)
- **Apache Jena Documentation**: [https://jena.apache.org/documentation/](https://jena.apache.org/documentation/)
- **GraphDB Documentation**: [https://graphdb.ontotext.com/documentation/](https://graphdb.ontotext.com/documentation/)
- **Neo4j Documentation**: [https://neo4j.com/docs/](https://neo4j.com/docs/)

### 11.4 IFC 샘플 파일

- IFC4/IFC2X3 샘플 파일: `references/*.ifc` (.gitignore)

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| v1.0 | 2026-02-03 | PRD Writer Agent | 최초 작성 - 프로젝트 요구사항 정의 완료 |

---

## 승인 및 검토

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| 제품 책임자 | TBD | | |
| 기술 리드 | TBD | | |
| 이해관계자 | TBD | | |

---

**문서 상태**: 초안 (Draft)
**다음 단계**: Technical Specification 문서 작성 (TECH-SPEC.md)
**관련 문서**:
- Discovery Report: `docs/DISCOVERY.md` (생성 예정)
- Technical Specification: `docs/TECH-SPEC.md` (생성 예정)
- Progress Tracker: `docs/PROGRESS.md` (생성 예정)
