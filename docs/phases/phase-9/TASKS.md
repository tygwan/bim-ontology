# Phase 9: Smart3D Plant Classification Expansion - Tasks

## Tasks

### 분류 패턴 확장
- [x] T-P9-001: Smart3D Plant 패턴 10개 추가 (MemberSystem, Hanger, PipeFitting, Flange, ProcessUnit, Conduit, Assembly, Brace, GroutPad, Nozzle)
- [x] T-P9-002: 패턴 우선순위 정렬 (PipeFitting → Pipe, Hanger → Support)
- [x] T-P9-003: `classify_element_name()` 함수에서 ordered dict 순서 검증

### 추론 규칙
- [x] T-P9-004: `infer_plant_support_element` SPARQL CONSTRUCT 규칙 작성
- [x] T-P9-005: `infer_piping_element` SPARQL CONSTRUCT 규칙 작성
- [x] T-P9-006: `PlantSupportElement`, `PipingElement` OWL 클래스 스키마 추가
- [x] T-P9-007: `_create_schema_classes()`에 신규 클래스 등록

### 검증
- [x] T-P9-008: 분류 결과 분석 - "Other" 비율 확인
- [x] T-P9-009: 추론 실행 후 PlantSupportElement/PipingElement 요소 수 확인

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
