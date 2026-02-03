# Phase 9: Smart3D Plant Classification Expansion - Specification

## Metadata

- **Phase**: Phase 9
- **Milestone**: M10 - "Other" Category Reduction
- **Status**: Completed
- **Completed**: 2026-02-03
- **Dependencies**: Phase 8

---

## Overview

### Problem

IFC4 샘플 데이터에서 전체 요소의 44%가 "Other"로 분류됨. Smart Plant 3D / Navisworks 내보내기로 생성된 IFC 파일의 특성상 기존 18개 패턴으로는 Plant-specific 요소를 식별 불가.

### Goals

1. **10개 Plant-specific 패턴 추가**: MemberSystem, Hanger, PipeFitting 등
2. **패턴 우선순위 정렬**: 구체적 패턴이 일반 패턴보다 먼저 매칭
3. **추론 규칙 추가**: PlantSupportElement, PipingElement 상위 분류

### Success Criteria

- [x] "Other" 카테고리 비율 44% → ~10%로 감소
- [x] 29개 분류 카테고리 (기존 18 + 신규 11)
- [x] 추론 규칙 7개 (기존 5 + 신규 2)

---

## Technical Requirements

### CATEGORY_PATTERNS 확장 (ifc_parser.py)

패턴 순서가 중요 (specific before generic):

| Group | Categories | Notes |
|-------|-----------|-------|
| **Smart3D Plant** (신규) | MemberSystem, Hanger, PipeFitting, Flange, ProcessUnit, Conduit, Assembly, Brace, GroutPad, Nozzle | Pipe 이전에 PipeFitting, Support 이전에 Hanger |
| **Structural** | Slab, Wall, Column, Beam | 기존 |
| **MEP** | Pipe, Duct, CableTray, Insulation, Valve, Pump, Equipment | Pipe는 PipeFitting 이후 |
| **Access** | Foundation, Railing, Stair | 기존 |
| **Other** | Support, MemberPart, Structural, Aspect, Geometry | Support는 Hanger 이후 |

### 추론 규칙 추가 (reasoner.py)

```
infer_plant_support_element: Hanger, Brace, MemberSystem, Support → PlantSupportElement
infer_piping_element: PipeFitting, Flange, Nozzle, Valve, Pipe → PipingElement
```

### 스키마 클래스 추가

- `BIM.PlantSupportElement` (rdfs:subClassOf BIM.BIMElement)
- `BIM.PipingElement` (rdfs:subClassOf BIM.BIMElement)

---

## Deliverables

- [x] `src/parser/ifc_parser.py` - 29개 CATEGORY_PATTERNS
- [x] `src/inference/reasoner.py` - 7개 CUSTOM_RULES + 2개 신규 스키마 클래스

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
