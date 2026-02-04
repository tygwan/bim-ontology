# Phase 17: Lean Layer Integration & Query Engine - Checklist

## Metadata

- **Phase**: Phase 17
- **Status**: Complete

---

## Checklist

### LeanLayerInjector
- [x] `src/converter/lean_layer_injector.py` 생성
- [x] `load_lean_schema()` 구현
- [x] `inject_schedule_csv()` 구현
- [x] `inject_awp_csv()` 구현
- [x] `inject_status_csv()` 구현
- [x] `inject_equipment_csv()` 구현
- [x] `update_element_status()` 구현

### SPARQL Templates
- [x] 지연 부재 조회 (`get_delayed_elements`)
- [x] Ready 상태 미달 부재 (`get_not_ready_elements`)
- [x] 장비 진입 가능 구역 (`get_equipment_access_zones`)
- [x] 오늘 할 일 (AWP) (`get_todays_work`)
- [x] IWP 제약 조건 확인 (`get_iwp_constraints`)
- [x] 배송 상태 집계 (`get_delivery_status_summary`)

### Reasoning Rules
- [x] Rule 8: 지연 부재 감지 (`infer_delayed_element`)
- [x] Rule 9: IWP 실행 가능 판단 (`infer_iwp_executable`)
- [x] Rule 10: 요소 준비 상태 추론 (`infer_element_ready`)

### Namespace
- [x] sched, awp 네임스페이스 추가
- [x] bind_namespaces() 확장

### REST API
- [x] POST /api/lean/inject/schedule
- [x] POST /api/lean/inject/awp
- [x] POST /api/lean/inject/status
- [x] POST /api/lean/inject/equipment
- [x] PUT /api/lean/status/{global_id}
- [x] GET /api/lean/today
- [x] GET /api/lean/delayed
- [x] GET /api/lean/iwp/{iwp_id}/constraints
- [x] GET /api/lean/stats

### Dashboard
- [x] Lean Layer 탭 (CSV 업로드 + 통계)
- [x] Today's Work 탭 (날짜별 IWP 조회)
- [x] Status Monitor 탭 (지연/상태 모니터링)
- [x] SPARQL 탭에 Lean Layer 쿼리 템플릿 4개 추가

### Verification
- [x] CSV 주입 → SPARQL 조회 정상 (schedule: 7 matched, awp: 6 IWPs)
- [x] 추론 규칙 실행 후 자동 추론 확인 (+7 inferred triples)
- [x] REST API 라우트 등록 완료
- [x] Dashboard 3개 탭 + 4개 SPARQL 템플릿 추가
- [x] 전체 테스트 91개 통과

---

**Document Version**: v1.1
**Last Updated**: 2026-02-04
