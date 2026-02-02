# Phase 0: 프로젝트 초기화 및 문서화 - Checklist

## Metadata

- **Phase**: Phase 0
- **Status**: 🚧 In Progress (40%)
- **Last Updated**: 2026-02-03
- **Target Completion**: 2026-02-10

---

## Completion Criteria

**Phase 0는 다음 조건을 모두 만족할 때 완료됩니다:**

1. ✅ 모든 핵심 문서 작성 완료 (PRD, TECH-SPEC, PROGRESS, CONTEXT)
2. ☐ Phase 0~7 구조 초기화 완료 (24개 문서 생성)
3. ☐ Python 개발 환경 구축 완료
4. ☐ ifcopenshell로 IFC 파일 로딩 성공
5. ☐ Triple Store 설치 및 연결 테스트 성공

---

## 1. 문서화 완료 (Documentation Completion)

### 1.1 핵심 프로젝트 문서 ✅

- [x] PRD.md 작성 완료
  - [ ] 11개 섹션 모두 포함
  - [ ] 18개 기능 요구사항 정의
  - [ ] 8개 사용자 스토리 작성
  - [ ] 8개 마일스톤 정의
  - [ ] 500+ 라인

- [x] TECH-SPEC.md 작성 완료
  - [ ] 시스템 아키텍처 다이어그램
  - [ ] 기술 스택 정의
  - [ ] API 설계 명세
  - [ ] 데이터 모델 정의

- [x] PROGRESS.md 작성 완료
  - [ ] 8개 마일스톤 상태 추적
  - [ ] KPI 및 메트릭 정의
  - [ ] 타임라인 시각화
  - [ ] 리스크 목록

- [x] CONTEXT.md 작성 완료
  - [ ] 프로젝트 한 줄 요약
  - [ ] 핵심 기술 스택
  - [ ] 프로젝트 구조
  - [ ] 토큰 최적화 가이드

### 1.2 Phase 구조 초기화

**Phase 0 문서** ✅
- [x] phase-0/SPEC.md
  - [ ] 목표 및 요구사항 명확히 정의
  - [ ] 성공 기준 5개 이상
  - [ ] 리스크 및 완화 전략
- [x] phase-0/TASKS.md
  - [ ] 작업 목록 20개 이상
  - [ ] 우선순위 및 예상 시간
  - [ ] 의존성 다이어그램
- [x] phase-0/CHECKLIST.md (이 문서)
  - [ ] 완료 기준 명확히 정의
  - [ ] 체크리스트 항목 구조화

**Phase 1 문서**
- [ ] phase-1/SPEC.md
  - [ ] IFC 파싱 요구사항
  - [ ] RDF 변환 명세
  - [ ] 성공 기준
- [ ] phase-1/TASKS.md
  - [ ] 작업 분해 (WBS)
  - [ ] 예상 일정
- [ ] phase-1/CHECKLIST.md
  - [ ] 완료 기준

**Phase 2~7 문서**
- [ ] phase-2/ (SPEC, TASKS, CHECKLIST)
- [ ] phase-3/ (SPEC, TASKS, CHECKLIST)
- [ ] phase-4/ (SPEC, TASKS, CHECKLIST)
- [ ] phase-5/ (SPEC, TASKS, CHECKLIST)
- [ ] phase-6/ (SPEC, TASKS, CHECKLIST)
- [ ] phase-7/ (SPEC, TASKS, CHECKLIST)

**문서 품질 검증**
- [ ] 모든 문서에 메타데이터 포함 (날짜, 버전, 상태)
- [ ] Markdown 포맷 일관성 유지
- [ ] 깨진 링크 없음
- [ ] 코드 블록 및 다이어그램 포함

---

## 2. 환경 설정 완료 (Environment Setup)

### 2.1 Python 환경 ☐

- [ ] **Python 설치 확인**
  - [ ] Python 3.8 이상 설치
  - [ ] 버전 확인: `python --version`
  - [ ] pip 업데이트: `pip install --upgrade pip`

- [ ] **가상환경 생성**
  - [ ] venv 생성: `python -m venv venv`
  - [ ] 활성화 성공 (Linux/Mac: `source venv/bin/activate`)
  - [ ] 가상환경 내 Python 경로 확인

- [ ] **requirements.txt 작성**
  - [ ] 필수 패키지 포함:
    - [ ] ifcopenshell>=0.7.0
    - [ ] rdflib>=6.0.0
    - [ ] SPARQLWrapper>=2.0.0
    - [ ] fastapi>=0.100.0
    - [ ] uvicorn>=0.20.0
    - [ ] pytest>=7.0.0
    - [ ] pytest-cov>=4.0.0
  - [ ] 버전 고정 (보안 및 재현성)

- [ ] **패키지 설치**
  - [ ] `pip install -r requirements.txt` 실행
  - [ ] 모든 패키지 설치 성공
  - [ ] 충돌 없음
  - [ ] import 테스트 성공:
    ```python
    import ifcopenshell
    import rdflib
    from SPARQLWrapper import SPARQLWrapper
    from fastapi import FastAPI
    ```

### 2.2 Java 환경 (선택) ☐

- [ ] **Java 설치 확인**
  - [ ] Java 11 이상 설치
  - [ ] 버전 확인: `java -version`
  - [ ] JAVA_HOME 환경 변수 설정

- [ ] **Apache Jena 설치 (선택)**
  - [ ] Jena 4.0+ 다운로드
  - [ ] 압축 해제 및 PATH 설정
  - [ ] 기본 명령어 테스트 (`sparql --version`)

### 2.3 Docker 환경 (선택) ☐

- [ ] **Docker 설치 확인**
  - [ ] Docker 20.10 이상
  - [ ] Docker Compose 2.0 이상
  - [ ] 버전 확인: `docker --version`, `docker-compose --version`

- [ ] **docker-compose.yml 작성**
  - [ ] GraphDB 서비스 정의
  - [ ] 볼륨 마운트 설정
  - [ ] 포트 매핑 (7200:7200)

---

## 3. 기술 스택 검증 (Technology Validation)

### 3.1 IFC 파싱 검증 ☐

**Test Script**: `scripts/test_ifc_loading.py`

- [ ] **nwd4op-12.ifc (224MB) 로딩**
  - [ ] 파일 경로 확인: `/home/coffin/dev/bim-ontology/references/nwd4op-12.ifc`
  - [ ] ifcopenshell.open() 성공
  - [ ] IFC 스키마 확인 (IFC4)
  - [ ] 총 엔티티 수 출력
  - [ ] 메모리 사용량 < 4GB

- [ ] **nwd23op-12.ifc (311MB) 로딩**
  - [ ] 파일 경로 확인
  - [ ] 로딩 성공
  - [ ] 메모리 사용량 모니터링

- [ ] **엔티티 추출 테스트**
  - [ ] IfcWall 추출 성공 (개수 > 0)
  - [ ] IfcColumn 추출 성공
  - [ ] IfcBeam 추출 성공
  - [ ] IfcSpace 추출 성공

- [ ] **성능 측정**
  - [ ] 로딩 시간 기록 (224MB: ? 초, 311MB: ? 초)
  - [ ] 메모리 피크 기록

**Success Criteria**:
```python
✅ ifc_file.schema == 'IFC4'
✅ len(ifc_file) > 0
✅ len(ifc_file.by_type('IfcWall')) > 0
✅ Loading time < 5 minutes
✅ Memory usage < 4GB
```

### 3.2 RDF 기본 검증 ☐

**Test Script**: `scripts/test_rdf_basic.py`

- [ ] **RDFLib Graph 생성**
  - [ ] Graph() 인스턴스 생성
  - [ ] Namespace 정의 (ifc, ex)

- [ ] **Triple 추가**
  - [ ] Subject-Predicate-Object triple 생성
  - [ ] RDF.type 사용
  - [ ] RDFS.label 사용

- [ ] **Triple 조회**
  - [ ] 전체 triple 순회 (for s, p, o in g)
  - [ ] 특정 triple 쿼리

- [ ] **직렬화 (Serialization)**
  - [ ] Turtle 포맷 출력
  - [ ] RDF/XML 포맷 출력 (선택)
  - [ ] JSON-LD 포맷 출력 (선택)

**Success Criteria**:
```python
✅ len(g) > 0
✅ g.serialize(format='turtle') returns valid Turtle syntax
```

### 3.3 Triple Store 연결 검증 ☐

**Test Script**: `scripts/test_triple_store.py`

- [ ] **GraphDB 설치 (Docker 권장)**
  - [ ] Docker 컨테이너 실행
  - [ ] 컨테이너 상태 확인: `docker ps`
  - [ ] 웹 UI 접속: http://localhost:7200
  - [ ] Repository 생성

- [ ] **SPARQL 연결 테스트**
  - [ ] SPARQLWrapper 사용
  - [ ] 엔드포인트 URL 설정
  - [ ] 기본 SELECT 쿼리 실행
  - [ ] 결과 파싱 (JSON)

- [ ] **Triple 삽입 테스트**
  - [ ] INSERT DATA 쿼리 실행
  - [ ] 삽입된 triple 조회
  - [ ] 삭제 테스트 (CLEAR GRAPH)

**Success Criteria**:
```python
✅ GraphDB 컨테이너 상태: 'running'
✅ Web UI 접속 가능 (HTTP 200)
✅ SPARQL query returns results
✅ Triple insertion successful
```

---

## 4. 설정 파일 작성 (Configuration Files)

### 4.1 필수 파일 ☐

- [ ] **requirements.txt**
  - [ ] 모든 Python 패키지 명시
  - [ ] 버전 고정
  - [ ] 설치 테스트 성공

- [ ] **.gitignore**
  - [ ] venv/ 제외
  - [ ] __pycache__/ 제외
  - [ ] *.pyc 제외
  - [ ] .env 제외
  - [ ] data/ 제외 (생성된 데이터)

- [ ] **README.md 업데이트**
  - [ ] 프로젝트 개요
  - [ ] 설치 가이드
  - [ ] 빠른 시작 (Quick Start)
  - [ ] 문서 링크 (PRD, TECH-SPEC)

### 4.2 선택 파일 ☐

- [ ] **docker-compose.yml**
  - [ ] GraphDB 서비스
  - [ ] 볼륨 마운트
  - [ ] 환경 변수

- [ ] **.env.example**
  - [ ] GRAPHDB_URL
  - [ ] API_PORT
  - [ ] 기타 환경 변수 템플릿

---

## 5. 테스트 및 검증 (Testing & Validation)

### 5.1 단위 테스트 ☐

- [ ] **pytest 설치 확인**
  - [ ] pytest --version
  - [ ] pytest-cov 설치

- [ ] **테스트 디렉토리 구조**
  - [ ] tests/ 폴더 생성
  - [ ] tests/test_ifc_loading.py
  - [ ] tests/test_rdf_basic.py
  - [ ] tests/test_triple_store.py

- [ ] **테스트 실행**
  - [ ] pytest 실행 성공
  - [ ] 모든 테스트 PASS
  - [ ] 커버리지 측정 (선택)

### 5.2 통합 검증 ☐

- [ ] **End-to-End 플로우 확인**
  - [ ] IFC 파일 로딩 → 엔티티 추출 → RDF 생성 → Triple Store 저장
  - [ ] 각 단계 오류 없이 완료
  - [ ] 최종 결과 SPARQL 쿼리로 확인

---

## 6. 문서 검토 및 승인 (Review & Approval)

### 6.1 자체 검토 ☐

- [ ] **문서 일관성 검토**
  - [ ] 모든 문서 날짜 및 버전 일치
  - [ ] 용어 통일 (IFC, RDF, SPARQL)
  - [ ] 링크 유효성 확인

- [ ] **코드 리뷰 (if any)**
  - [ ] 테스트 스크립트 코드 리뷰
  - [ ] PEP8 스타일 가이드 준수 (선택)

### 6.2 Phase 0 완료 선언 ☐

- [ ] **완료 기준 충족 확인**
  - [ ] 위 모든 체크리스트 완료
  - [ ] 블로커 없음
  - [ ] 다음 Phase 준비 완료

- [ ] **PROGRESS.md 업데이트**
  - [ ] Phase 0 상태 → ✅ Completed
  - [ ] Phase 0 Progress → 100%
  - [ ] Actual Completion Date 기록

- [ ] **Phase 1 준비**
  - [ ] phase-1/ 문서 확인
  - [ ] Phase 1 시작 날짜 확정
  - [ ] 초기 작업 할당

---

## Summary Checklist

**Critical Path (필수)**:
- [x] 1.1 핵심 프로젝트 문서 (4/4)
- [x] 1.2.1 Phase 0 문서 (3/3)
- [ ] 1.2.2 Phase 1 문서 (0/3)
- [ ] 1.2.3 Phase 2~7 문서 (0/18)
- [ ] 2.1 Python 환경 (0/4)
- [ ] 3.1 IFC 파싱 검증 (0/5)
- [ ] 3.3 Triple Store 검증 (0/4)
- [ ] 4.1 필수 파일 (0/3)

**Optional Path (선택)**:
- [ ] 2.2 Java 환경 (0/3)
- [ ] 2.3 Docker 환경 (0/2)
- [ ] 3.2 RDF 기본 검증 (0/4)
- [ ] 4.2 선택 파일 (0/2)
- [ ] 5. 테스트 및 검증 (0/6)

**Overall Completion**: 7/57 (12%)
**Critical Path Completion**: 7/22 (32%)

---

## Phase 0 Exit Criteria

**Phase 0는 다음 조건을 모두 만족해야 완료됩니다:**

1. ✅ **Documentation**: 모든 핵심 문서 및 Phase 구조 문서 작성 완료
2. ☐ **Environment**: Python 환경 구축 및 패키지 설치 완료
3. ☐ **Validation**: IFC 파싱 및 Triple Store 연결 테스트 성공
4. ☐ **Configuration**: requirements.txt, .gitignore, README.md 작성
5. ☐ **Readiness**: Phase 1 문서 작성 및 시작 준비 완료

**Target Date**: 2026-02-10
**Current Status**: 🚧 In Progress (32% critical path)

---

## Next Steps After Phase 0

1. ✅ PROGRESS.md 업데이트 (Phase 0 → Completed)
2. Phase 1 시작 (IFC 파싱 및 RDF 변환 개발)
3. 첫 코드 작성: `src/parser/ifc_parser.py`
4. 첫 단위 테스트: `tests/test_ifc_parser.py`

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
**Status**: 🚧 In Progress
**Maintained By**: dev-docs-writer agent
