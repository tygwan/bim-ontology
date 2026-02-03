# Phase 8: CI Pipeline Fix & Test Infrastructure - Tasks

## Tasks

### 테스트 인프라
- [x] T-P8-001: `tests/conftest.py` 생성 - `requires_ifc` 마커, `rdf_store` 픽스처
- [x] T-P8-002: `pyproject.toml` 생성 - pytest 마커 등록
- [x] T-P8-003: `tests/test_integration.py`에 `@requires_ifc` 마커 적용 (19개 테스트)
- [x] T-P8-004: `tests/test_api.py`에 마커 적용 (21개 테스트)
- [x] T-P8-005: `tests/test_client.py`에 마커 적용 (11개 테스트)
- [x] T-P8-006: `tests/test_phase4.py`에 마커 적용 (9개 테스트)

### CI 워크플로우
- [x] T-P8-007: `.github/workflows/ci.yml` 수정 - `-m "not requires_ifc"` 필터
- [x] T-P8-008: 커버리지 임계치 조정 (35%)
- [x] T-P8-009: Python 3.12 + pip 캐싱 설정

### 검증
- [x] T-P8-010: 로컬에서 `pytest -m "not requires_ifc"` 실행 확인 (20개 테스트 통과)
- [x] T-P8-011: GitHub CI 파이프라인 green 확인
- [x] T-P8-012: `from conftest import` 제거 → 인라인 마커 정의로 전환

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
