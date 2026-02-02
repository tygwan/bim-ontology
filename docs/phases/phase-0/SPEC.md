# Phase 0: 프로젝트 초기화 및 문서화 - Specification

## Metadata

- **Phase**: Phase 0
- **Milestone**: M1 - 프로젝트 초기화 및 환경 설정
- **Status**: 🚧 In Progress
- **Progress**: 40%
- **Start Date**: 2026-02-03
- **Target Date**: 2026-02-10
- **Actual Completion**: -
- **Owner**: Dev Team

---

## Overview

### Purpose

프로젝트의 기반을 구축하고 개발을 시작하기 위한 모든 문서화 및 환경 설정을 완료합니다. 이 Phase는 향후 모든 개발 작업의 기준점이 됩니다.

### Goals

1. **문서화 완성**: PRD, TECH-SPEC, PROGRESS, CONTEXT 문서 작성
2. **Phase 구조 초기화**: Phase 0~7의 폴더 및 문서 생성
3. **개발 환경 설정**: Python, Java, Docker 환경 구축
4. **기술 스택 검증**: ifcopenshell, Apache Jena, GraphDB 설치 및 테스트
5. **IFC 샘플 검증**: 보유 IFC 파일 로딩 및 파싱 테스트

### Success Criteria

- [ ] 모든 프로젝트 문서 작성 완료 (PRD, TECH-SPEC, PROGRESS, CONTEXT)
- [ ] Phase 0~7 폴더 및 문서 생성 (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] Python 3.8+ 개발 환경 구축 (venv, requirements.txt)
- [ ] ifcopenshell로 IFC 파일 로딩 성공
- [ ] GraphDB 또는 Neo4j 설치 및 연결 테스트 성공

---

## Technical Requirements

### Documentation

**Required Documents**:
- ✅ PRD.md (Product Requirements Document)
- ✅ TECH-SPEC.md (Technical Specification)
- ✅ PROGRESS.md (Progress Tracking)
- ✅ CONTEXT.md (Context Summary)

**Phase Structure**:
- ✅ phase-0/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-1/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-2/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-3/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-4/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-5/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-6/ (SPEC.md, TASKS.md, CHECKLIST.md)
- [ ] phase-7/ (SPEC.md, TASKS.md, CHECKLIST.md)

### Development Environment

**Python Environment**:
```bash
# Python 버전
Python 3.8 이상

# 가상환경
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 핵심 패키지
ifcopenshell>=0.7.0
rdflib>=6.0.0
SPARQLWrapper>=2.0.0
fastapi>=0.100.0
pytest>=7.0.0
```

**Java Environment** (Apache Jena용):
```bash
# Java 버전
Java 11 이상 (OpenJDK 권장)

# Apache Jena
Apache Jena 4.0 이상
```

**Docker Environment**:
```bash
# Docker
Docker 20.10 이상
Docker Compose 2.0 이상

# Triple Store 컨테이너
GraphDB Free Edition (또는 Neo4j Community)
```

### Technology Stack Validation

**Priority 0 (필수)**:
- [ ] Python 3.8+ 설치 확인
- [ ] ifcopenshell 설치 및 IFC 파싱 테스트
- [ ] RDFLib 설치 및 RDF 생성 테스트

**Priority 1 (중요)**:
- [ ] Java 11+ 설치 확인
- [ ] Apache Jena 설치
- [ ] GraphDB/Neo4j 설치 및 실행

**Priority 2 (선택)**:
- [ ] Docker 환경 구축
- [ ] IDE 설정 (VSCode, PyCharm, IntelliJ)

---

## Architecture

### Project Structure

```
bim-ontology/
├── docs/                          # 프로젝트 문서
│   ├── PRD.md                     ✅ 완료
│   ├── TECH-SPEC.md               ✅ 완료
│   ├── PROGRESS.md                ✅ 완료
│   ├── CONTEXT.md                 ✅ 완료
│   └── phases/                    # Phase별 문서
│       ├── phase-0/               🚧 진행 중
│       │   ├── SPEC.md
│       │   ├── TASKS.md
│       │   └── CHECKLIST.md
│       ├── phase-1/               ❌ 미생성
│       ├── phase-2/               ❌ 미생성
│       ├── phase-3/               ❌ 미생성
│       ├── phase-4/               ❌ 미생성
│       ├── phase-5/               ❌ 미생성
│       ├── phase-6/               ❌ 미생성
│       └── phase-7/               ❌ 미생성
├── src/                           # 소스 코드 (Phase 1부터 생성)
│   ├── parser/                    ❌ 미생성
│   ├── converter/                 ❌ 미생성
│   ├── api/                       ❌ 미생성
│   ├── clients/                   ❌ 미생성
│   ├── dashboard/                 ❌ 미생성
│   └── cli/                       ❌ 미생성
├── tests/                         # 테스트 코드
├── references/                    # 참조 문서 및 샘플
│   ├── nwd4op-12.ifc              ✅ 존재 (224MB)
│   ├── nwd23op-12.ifc             ✅ 존재 (311MB)
│   └── *.pdf                      ✅ 존재 (연구 논문)
├── scripts/                       # 유틸리티 스크립트
├── docker/                        # Docker 설정
├── README.md                      ✅ 존재
└── requirements.txt               ❌ 미생성
```

---

## Functional Specifications

### FS-P0-001: 프로젝트 문서 작성

**Description**: 프로젝트의 모든 기본 문서를 작성하여 개발 방향성과 요구사항을 명확히 정의합니다.

**Requirements**:
- PRD.md: 제품 요구사항, 사용자 스토리, 성공 기준
- TECH-SPEC.md: 아키텍처, 기술 스택, API 설계
- PROGRESS.md: 마일스톤, 진행 상황, KPI 추적
- CONTEXT.md: 프로젝트 요약, 빠른 참조, 토큰 최적화

**Acceptance Criteria**:
- [x] PRD.md 작성 완료 (500+ 라인)
- [x] TECH-SPEC.md 작성 완료
- [x] PROGRESS.md 작성 완료
- [x] CONTEXT.md 작성 완료

### FS-P0-002: Phase 구조 초기화

**Description**: Phase 0부터 Phase 7까지 8개 Phase의 폴더 구조와 기본 문서를 생성합니다.

**Requirements**:
- 각 Phase 폴더: `docs/phases/phase-{0-7}/`
- 각 Phase 문서: SPEC.md, TASKS.md, CHECKLIST.md

**Acceptance Criteria**:
- [ ] 8개 Phase 폴더 생성
- [ ] 각 Phase별 SPEC.md 작성 (목표, 요구사항, 성공 기준)
- [ ] 각 Phase별 TASKS.md 작성 (작업 목록, 체크리스트)
- [ ] 각 Phase별 CHECKLIST.md 작성 (완료 기준)

### FS-P0-003: Python 개발 환경 설정

**Description**: Python 기반 개발을 위한 가상환경 및 의존성 패키지를 설치합니다.

**Requirements**:
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 패키지 설치
pip install ifcopenshell>=0.7.0
pip install rdflib>=6.0.0
pip install SPARQLWrapper>=2.0.0
pip install fastapi>=0.100.0
pip install pytest>=7.0.0
```

**Acceptance Criteria**:
- [ ] Python 3.8+ 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 작성
- [ ] 핵심 패키지 설치 완료

### FS-P0-004: IFC 파일 로딩 테스트

**Description**: 보유한 IFC 샘플 파일을 ifcopenshell로 로딩하여 기본 파싱 기능을 검증합니다.

**Test Script**:
```python
import ifcopenshell

# IFC 파일 로딩
ifc_file = ifcopenshell.open('/home/coffin/dev/bim-ontology/references/nwd4op-12.ifc')

# 기본 정보 출력
print(f"IFC Schema: {ifc_file.schema}")
print(f"Entities: {len(ifc_file)}")

# 특정 엔티티 조회
walls = ifc_file.by_type('IfcWall')
print(f"Total Walls: {len(walls)}")
```

**Acceptance Criteria**:
- [ ] nwd4op-12.ifc (224MB) 로딩 성공
- [ ] nwd23op-12.ifc (311MB) 로딩 성공
- [ ] IfcWall, IfcColumn 등 엔티티 추출 성공
- [ ] 메모리 사용량 모니터링 (< 4GB)

### FS-P0-005: Triple Store 설치 및 연결

**Description**: GraphDB 또는 Neo4j를 설치하고 기본 연결을 테스트합니다.

**Option 1: GraphDB (Docker)**:
```bash
docker run -d -p 7200:7200 \
  --name graphdb \
  -v graphdb-data:/opt/graphdb/home \
  ontotext/graphdb:10.0.0-free
```

**Option 2: Neo4j (Docker)**:
```bash
docker run -d -p 7474:7474 -p 7687:7687 \
  --name neo4j \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

**Acceptance Criteria**:
- [ ] GraphDB 또는 Neo4j 설치 완료
- [ ] 웹 UI 접속 확인 (GraphDB: http://localhost:7200)
- [ ] Repository 생성 및 기본 triple 삽입 테스트
- [ ] Python에서 SPARQL 쿼리 실행 테스트

---

## Non-Functional Requirements

### NFR-P0-001: 문서 품질

**Requirement**: 모든 문서는 명확하고 구조화되어 있으며, 향후 유지보수가 용이해야 합니다.

**Acceptance Criteria**:
- 문서 구조 일관성 (Markdown 표준 준수)
- 코드 블록 및 다이어그램 포함
- 버전 및 날짜 정보 명시
- 관련 문서 간 링크 연결

### NFR-P0-002: 환경 설정 자동화

**Requirement**: 개발 환경 설정이 스크립트로 자동화되어야 합니다.

**Acceptance Criteria**:
- `scripts/setup_env.sh` 스크립트 작성 (선택)
- requirements.txt 완성
- Docker Compose 파일 작성 (선택)

### NFR-P0-003: 재현 가능성

**Requirement**: 다른 개발자가 동일한 환경을 재현할 수 있어야 합니다.

**Acceptance Criteria**:
- Python 버전 명시 (3.8+)
- 패키지 버전 고정 (requirements.txt)
- OS별 설치 가이드 (Linux, macOS, Windows)

---

## Dependencies

### Internal

- PRD.md: 요구사항 참조
- TECH-SPEC.md: 기술 스택 참조

### External

- ifcopenshell 공식 문서: https://ifcopenshell.org/
- Apache Jena 문서: https://jena.apache.org/documentation/
- GraphDB 문서: https://graphdb.ontotext.com/documentation/
- IFC4 표준: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/

---

## Risks & Mitigation

### R-P0-001: ifcopenshell 설치 실패

**Risk**: ifcopenshell이 일부 OS/Python 버전에서 설치 실패할 수 있음
**Probability**: 중간
**Impact**: 높음
**Mitigation**:
- Python 3.8~3.10 버전 사용 권장
- Conda 환경 사용 (선택)
- 공식 문서 참조하여 troubleshooting

### R-P0-002: 대용량 IFC 파일 메모리 부족

**Risk**: 311MB IFC 파일 로딩 시 메모리 부족 발생 가능
**Probability**: 낮음
**Impact**: 중간
**Mitigation**:
- 최소 8GB RAM 권장
- 메모리 프로파일링 도구 사용
- 스트리밍 파싱 검토 (Phase 1)

### R-P0-003: GraphDB/Neo4j 설치 실패

**Risk**: Docker 환경 또는 로컬 설치 실패
**Probability**: 낮음
**Impact**: 중간
**Mitigation**:
- Docker 사용 권장 (일관된 환경)
- Apache Jena TDB (파일 기반) 대안 고려
- 공식 설치 가이드 참조

---

## Testing Strategy

### TS-P0-001: 문서 검증

**Test**: 모든 문서 링크 및 참조 확인
**Method**: 수동 검토, Markdown linter
**Criteria**: 깨진 링크 없음, 일관된 포맷

### TS-P0-002: 환경 설정 검증

**Test**: 다른 개발자가 requirements.txt로 환경 재현 가능
**Method**: 새 가상환경에서 설치 테스트
**Criteria**: 패키지 충돌 없음, 모든 import 성공

### TS-P0-003: IFC 파싱 검증

**Test**: 샘플 IFC 파일 로딩 및 엔티티 추출
**Method**: Python 스크립트 실행
**Criteria**: 오류 없이 로딩 완료, 엔티티 수 > 0

---

## Deliverables

### Documentation

- [x] PRD.md
- [x] TECH-SPEC.md
- [x] PROGRESS.md
- [x] CONTEXT.md
- [x] phase-0/SPEC.md (이 문서)
- [ ] phase-0/TASKS.md
- [ ] phase-0/CHECKLIST.md
- [ ] phase-1 ~ phase-7 문서

### Configuration Files

- [ ] requirements.txt (Python 패키지)
- [ ] docker-compose.yml (Triple Store) - 선택
- [ ] .gitignore
- [ ] README.md 업데이트

### Test Scripts

- [ ] scripts/test_ifc_loading.py
- [ ] scripts/test_triple_store_connection.py

---

## Timeline

| Task | Duration | Start | End |
|------|----------|-------|-----|
| 문서화 (PRD, TECH-SPEC, etc.) | 2 days | 2026-02-03 | 2026-02-04 |
| Phase 구조 초기화 | 1 day | 2026-02-05 | 2026-02-05 |
| Python 환경 설정 | 1 day | 2026-02-06 | 2026-02-06 |
| ifcopenshell 설치 및 테스트 | 1 day | 2026-02-07 | 2026-02-07 |
| Triple Store 설치 및 테스트 | 2 days | 2026-02-08 | 2026-02-09 |
| Phase 0 검토 및 완료 | 1 day | 2026-02-10 | 2026-02-10 |

**Total Duration**: 8 days
**Target Completion**: 2026-02-10

---

## Notes

- Phase 0는 순수 설정 및 문서화 작업으로, 코딩은 Phase 1부터 시작
- IFC 샘플 파일은 이미 `/home/coffin/dev/bim-ontology/references/`에 존재
- GraphDB vs Neo4j 선택은 Phase 0 완료 전에 결정 (GraphDB 권장)
- 문서화 작업은 dev-docs-writer agent가 담당

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
**Status**: 🚧 In Progress
