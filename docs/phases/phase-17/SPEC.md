# Phase 17: Lean Layer Integration & Query Engine - Specification

## Metadata

- **Phase**: Phase 17
- **Milestone**: M18 - Lean Layer Complete
- **Status**: Pending
- **Dependencies**: Phase 16

---

## Overview

### Goal

Phase 16에서 검증된 방법으로 Lean Layer를 파이프라인에 통합하고, 3가지 컨셉(Semantic EPC / 시공성 검증 / 오늘 할 일)을 위한 SPARQL 쿼리, 추론 규칙, REST API, Dashboard를 구현한다.

### Success Criteria

- [ ] LeanLayerInjector 통합 모듈 구현
- [ ] 컨셉별 SPARQL 쿼리 템플릿 (5종+)
- [ ] 추론 규칙 3개 추가 (지연 감지, IWP 실행 가능, 과부하)
- [ ] Namespace 확장 (sched/awp/opm)
- [ ] REST API 엔드포인트 (8종)
- [ ] Dashboard Lean Layer / Today's Work / Status Monitor 탭

---

## Technical Requirements

### LeanLayerInjector (`src/converter/lean_layer_injector.py`)
- `load_lean_schema()` - lean_schema.ttl 로딩
- `inject_schedule_csv()` - 일정 CSV → ConstructionTask
- `inject_awp_csv()` - AWP CSV → CWA/CWP/IWP
- `inject_status_csv()` - 상태 CSV → ElementStatus
- `inject_equipment_csv()` - 장비 CSV → ConstructionEquipment
- `update_element_status()` - 단일 요소 상태 업데이트

### SPARQL Templates
- 지연 부재 조회 (Semantic EPC)
- Ready 상태 미달 부재 (Semantic EPC)
- 장비 진입 가능 구역 (시공성)
- 오늘 할 일 - AWP 기반 (일일 작업)
- IWP 제약 조건 확인 (일일 작업)

### Reasoning Rules
- Rule 8: 지연 부재 자동 감지 (`bim:isDelayed`)
- Rule 9: IWP 실행 가능 판단 (`awp:isExecutable`)
- Rule 10: 일일 과부하 감지 (`bim:isOverloaded`)

### REST API (`src/api/routes/lean_layer.py`)
- POST /api/lean/inject/schedule
- POST /api/lean/inject/awp
- POST /api/lean/inject/status
- POST /api/lean/inject/equipment
- PUT /api/lean/status/{global_id}
- GET /api/lean/today
- GET /api/lean/delayed
- GET /api/lean/iwp/{iwp_id}/constraints

---

## Deliverables

- [ ] `src/converter/lean_layer_injector.py`
- [ ] `src/api/routes/lean_layer.py`
- [ ] `src/api/queries/templates.py` (SPARQL 추가)
- [ ] `src/inference/reasoner.py` (규칙 추가)
- [ ] `src/converter/namespace_manager.py` (NS 추가)
- [ ] Dashboard 3개 탭 추가

---

**Document Version**: v1.0
**Last Updated**: 2026-02-04
