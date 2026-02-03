# Phase 12: Ontology Editor Dashboard - Specification

## Metadata

- **Phase**: Phase 12
- **Milestone**: M13 - Web UI for Schema Editing
- **Status**: Completed
- **Completed**: 2026-02-03
- **Dependencies**: Phase 11

---

## Overview

### Goal

Phase 10-11에서 구현한 Properties API와 Ontology Editor API를 웹 대시보드에 통합. 기존 5탭 대시보드를 7탭으로 확장하여 속성 조회 및 스키마 편집 UI 제공.

### Success Criteria

- [x] 7탭 대시보드 정상 동작 (Overview, Buildings, Elements, SPARQL, Properties, Ontology, Reasoning)
- [x] Properties 탭에서 요소 속성 조회 및 검색
- [x] Ontology 탭에서 타입/링크 CRUD 및 규칙 편집

---

## Technical Requirements

### Dashboard Tabs (7개)

| Tab ID | Tab Name | Features |
|--------|----------|----------|
| `overview` | Overview | 통계 카드 4개, 카테고리 도넛/바 차트 |
| `buildings` | Buildings | 건물 계층 트리, 노드 클릭 상세 |
| `elements` | Elements | 카테고리 필터, 이름 검색, 50개 페이지네이션 |
| `sparql` | SPARQL | 쿼리 에디터, 6개 프리셋, 결과 테이블 |
| `properties` | Properties (신규) | GlobalId 속성 조회, 키 검색, SP3D 요약 |
| `ontology` | Ontology (신규) | Types/Links CRUD, 규칙 JSON 에디터, Import/Export |
| `reasoning` | Reasoning | OWL 추론, Before/After, SHACL 검증 |

### Properties Tab

- GlobalId 입력 → PropertySet 테이블 렌더링
- 속성 키 검색 (텍스트 입력)
- SP3D Plant 데이터 요약 카드

### Ontology Tab

- Object Type 테이블 (이름, 부모, 설명) + Create/Delete 버튼
- Link Type 테이블
- Classification Rules JSON 에디터 (textarea)
- Schema Export 다운로드 / Import 업로드
- Apply Schema 버튼

---

## Deliverables

- [x] `src/dashboard/index.html` - 7탭 구조 (343 lines)
- [x] `src/dashboard/app.js` - Properties/Ontology 패널 로직

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
