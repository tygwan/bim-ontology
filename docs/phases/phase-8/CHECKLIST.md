# Phase 8: CI Pipeline Fix & Test Infrastructure - Checklist

## Metadata

- **Phase**: Phase 8
- **Status**: Completed
- **Completed**: 2026-02-03

---

## Completion Criteria

- [x] CI 파이프라인 green
- [x] IFC 비의존 테스트만 CI에서 실행
- [x] 커버리지 35% 이상 (실제 ~39%)
- [x] 로컬 전체 테스트 영향 없음

---

## Checklist

### 테스트 인프라
- [x] `tests/conftest.py` - `requires_ifc` 마커 정의
- [x] `tests/conftest.py` - `rdf_store()` 픽스처
- [x] `pyproject.toml` - 마커 등록
- [x] 4개 테스트 파일에 인라인 `requires_ifc` 마커 적용

### CI 워크플로우
- [x] `.github/workflows/ci.yml` 수정
  - [x] Python 3.12 + pip 캐싱
  - [x] `-m "not requires_ifc"` 필터
  - [x] `--cov-fail-under=35`
- [x] CI 결과: 20 passed, 71 skipped, 커버리지 ~39%

### 이슈 해결
- [x] `from conftest import requires_ifc` → `ModuleNotFoundError` 해결
- [x] 인라인 마커 정의로 전환 (각 테스트 파일 내)

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
