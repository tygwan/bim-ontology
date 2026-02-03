# Phase 1: IFC 파싱 및 RDF 변환 - Tasks

## Metadata

- **Phase**: Phase 1
- **Status**: ❌ Not Started
- **Progress**: 0%
- **Start Date**: 2026-02-10 (예정)
- **Target Date**: 2026-02-24
- **Duration**: 14 days

---

## Task Overview

| Category | Total | Completed | Pending |
|----------|-------|-----------|---------|
| IFC 파서 개발 | 5 | 0 | 5 |
| RDF 변환 개발 | 6 | 0 | 6 |
| Triple Store 연동 | 4 | 0 | 4 |
| 테스트 작성 | 5 | 0 | 5 |
| **Total** | **20** | **0** | **20** |

---

## 1. IFC 파서 개발

- [ ] **T-P1-001**: IFCParser 클래스 기본 구조 작성
  - Priority: P0
  - Effort: 2h
  - Deliverable: `src/parser/ifc_parser.py`

- [ ] **T-P1-002**: IFC 파일 로딩 기능 구현 (ifcopenshell 활용)
  - Priority: P0
  - Effort: 3h
  - Dependencies: T-P1-001

- [ ] **T-P1-003**: 엔티티 추출 기능 구현 (get_entities)
  - Priority: P0
  - Effort: 4h
  - Dependencies: T-P1-002

- [ ] **T-P1-004**: IFC 스키마 검증 기능 구현
  - Priority: P1
  - Effort: 2h
  - Dependencies: T-P1-002

- [ ] **T-P1-005**: 오류 처리 및 로깅 추가
  - Priority: P1
  - Effort: 2h
  - Dependencies: T-P1-003

---

## 2. RDF 변환 개발

- [ ] **T-P1-006**: RDFConverter 클래스 기본 구조 작성
  - Priority: P0
  - Effort: 2h
  - Deliverable: `src/converter/ifc_to_rdf.py`

- [ ] **T-P1-007**: 네임스페이스 관리 모듈 구현
  - Priority: P0
  - Effort: 2h
  - Deliverable: `src/converter/namespace_manager.py`

- [ ] **T-P1-008**: IFC 엔티티 → RDF Subject 매핑
  - Priority: P0
  - Effort: 4h
  - Dependencies: T-P1-006, T-P1-007

- [ ] **T-P1-009**: IFC 속성 → RDF Predicate-Object 매핑
  - Priority: P0
  - Effort: 4h
  - Dependencies: T-P1-008

- [ ] **T-P1-010**: ifcOWL 매핑 룰 작성 (mapping.py)
  - Priority: P0
  - Effort: 6h
  - Deliverable: `src/converter/mapping.py`
  - Notes: 최소 50개 IFC 엔티티 타입 매핑

- [ ] **T-P1-011**: RDF 직렬화 기능 (Turtle, RDF/XML)
  - Priority: P1
  - Effort: 2h
  - Deliverable: `src/converter/serializer.py`

---

## 3. Triple Store 연동

- [ ] **T-P1-012**: TripleStore 클래스 기본 구조 작성
  - Priority: P0
  - Effort: 2h
  - Deliverable: `src/storage/triple_store.py`

- [ ] **T-P1-013**: SPARQL INSERT 기능 구현
  - Priority: P0
  - Effort: 3h
  - Dependencies: T-P1-012

- [ ] **T-P1-014**: 배치 처리 기능 구현 (1,000 triple 단위)
  - Priority: P0
  - Effort: 4h
  - Deliverable: `src/storage/batch_writer.py`

- [ ] **T-P1-015**: GraphDB 클라이언트 연동
  - Priority: P0
  - Effort: 3h
  - Deliverable: `src/storage/graphdb_client.py`
  - Dependencies: T-P1-013

---

## 4. 테스트 작성

- [ ] **T-P1-016**: IFCParser 단위 테스트 작성
  - Priority: P0
  - Effort: 3h
  - Deliverable: `tests/test_ifc_parser.py`
  - Coverage Target: > 80%

- [ ] **T-P1-017**: RDFConverter 단위 테스트 작성
  - Priority: P0
  - Effort: 3h
  - Deliverable: `tests/test_rdf_converter.py`
  - Coverage Target: > 80%

- [ ] **T-P1-018**: TripleStore 단위 테스트 작성
  - Priority: P0
  - Effort: 2h
  - Deliverable: `tests/test_triple_store.py`

- [ ] **T-P1-019**: End-to-End 통합 테스트 작성
  - Priority: P0
  - Effort: 4h
  - Deliverable: `tests/test_integration.py`
  - Test: IFC → RDF → Triple Store

- [ ] **T-P1-020**: 테스트 커버리지 측정 및 리포트
  - Priority: P1
  - Effort: 1h
  - Command: `pytest --cov=src tests/`
  - Target: > 70%

---

## Daily Task Breakdown

### Week 1: IFC 파서 및 RDF 변환 (2026-02-10 ~ 02-16)

**Day 1 (02/10)**
- [ ] T-P1-001: IFCParser 클래스 구조
- [ ] T-P1-002: IFC 파일 로딩 기능
- [ ] T-P1-006: RDFConverter 클래스 구조

**Day 2 (02/11)**
- [ ] T-P1-003: 엔티티 추출 기능
- [ ] T-P1-007: 네임스페이스 관리

**Day 3 (02/12)**
- [ ] T-P1-004: IFC 스키마 검증
- [ ] T-P1-005: 오류 처리 및 로깅
- [ ] T-P1-008: IFC 엔티티 → RDF Subject 매핑

**Day 4-5 (02/13-14)**
- [ ] T-P1-009: IFC 속성 매핑
- [ ] T-P1-010: ifcOWL 매핑 룰 작성

**Day 6 (02/15)**
- [ ] T-P1-011: RDF 직렬화 기능
- [ ] T-P1-016: IFCParser 단위 테스트

**Day 7 (02/16)**
- [ ] T-P1-017: RDFConverter 단위 테스트

### Week 2: Triple Store 연동 및 통합 테스트 (2026-02-17 ~ 02-24)

**Day 8 (02/17)**
- [ ] T-P1-012: TripleStore 클래스 구조
- [ ] T-P1-013: SPARQL INSERT 기능

**Day 9 (02/18)**
- [ ] T-P1-014: 배치 처리 기능
- [ ] T-P1-015: GraphDB 클라이언트 연동

**Day 10 (02/19)**
- [ ] T-P1-018: TripleStore 단위 테스트
- [ ] T-P1-019: End-to-End 통합 테스트 (Part 1)

**Day 11 (02/20)**
- [ ] T-P1-019: End-to-End 통합 테스트 (Part 2)
- [ ] T-P1-020: 테스트 커버리지 측정

**Day 12-13 (02/21-22)**
- [ ] 전체 코드 리뷰 및 리팩토링
- [ ] 성능 테스트 (대용량 IFC 파일)
- [ ] 버그 수정

**Day 14 (02/24)**
- [ ] 문서화 (API docstring, 사용 예제)
- [ ] Phase 1 완료 검증
- [ ] Phase 2 준비

---

## Effort Summary

| Category | Estimated Hours |
|----------|----------------|
| IFC 파서 개발 | 13h |
| RDF 변환 개발 | 20h |
| Triple Store 연동 | 12h |
| 테스트 작성 | 13h |
| 코드 리뷰 및 버그 수정 | 10h |
| 문서화 | 4h |
| **Total** | **72h** |

**Working Days**: 14 days (2 weeks)
**Daily Average**: 5-6 hours

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
**Status**: ❌ Not Started
