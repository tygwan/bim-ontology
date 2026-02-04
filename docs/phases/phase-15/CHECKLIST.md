# Phase 15: IFC/RDF Data Audit & Property Extraction Enhancement - Checklist

## Metadata

- **Phase**: Phase 15
- **Status**: Complete

---

## Checklist

### IFC Audit Script
- [x] `scripts/audit_ifc.py` 생성
- [x] 모든 엔티티 타입 카운트 출력
- [x] PropertySet 이름 + 속성 목록 출력
- [x] Quantity/Material/Classification 존재 여부 확인
- [x] Schedule/Cost 엔티티 존재 여부 확인
- [x] 결과 JSON 저장 (`data/audit/ifc_audit_report.json`)

### RDF Audit SPARQL
- [x] `src/api/queries/audit_queries.py` 생성
- [x] Q1: 전체 데이터 요약
- [x] Q2: 카테고리별 요소 수 + PropertySet 보유 현황
- [x] Q3: PropertySet 이름별 속성 목록
- [x] Q4: 요소별 속성 완성도
- [x] Q5: 공간 계층 구조 전체

### Property Extraction
- [~] `_convert_quantities()` 메서드 구현 → SKIP (IFC에 IfcElementQuantity 없음)
- [~] `_convert_materials()` 메서드 구현 → SKIP (IFC에 IfcMaterial 없음)
- [~] `_convert_classifications()` 메서드 구현 → SKIP (IFC에 IfcClassification 없음)
- [~] `_build_schema()` 에 새 프로퍼티 정의 추가 → SKIP (추출 대상 없음)
- [~] SHACL Shape 추가 → Phase 16에서 Lean Layer Shape로 대체

### Verification
- [x] IFC 감사 리포트에 모든 엔티티 타입 출력됨
- [~] RDF 변환 후 Quantity/Material/Classification 추출 확인 → N/A (IFC 데이터 없음)
- [x] 감사 SPARQL 5종 실행 가능
- [x] 테스트 통과

---

**Document Version**: v1.1
**Last Updated**: 2026-02-04
