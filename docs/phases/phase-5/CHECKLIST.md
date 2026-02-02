# Phase 5: 웹 대시보드 및 배포 - Checklist

## Completion Criteria

- [x] 웹 대시보드 구현 완료
- [x] 차트 5종류 이상
- [x] Docker 배포 설정
- [ ] CLI 도구 구현 (보류 - API + 대시보드로 대체)
- [ ] 사용자 가이드 작성

---

## Checklist

### 웹 대시보드
- [x] SPA 애플리케이션 (vanilla JS + Tailwind CSS)
- [x] Overview 탭: 통계 카드 + 카테고리 분포 차트
- [x] Buildings 탭: 건물-층 계층 트리 + 층 상세
- [x] Elements 탭: 필터/검색/페이지네이션 테이블
- [x] SPARQL 탭: 쿼리 에디터 + 6개 템플릿 + 결과 테이블
- [x] Reasoning 탭: 추론 실행 + before/after 통계
- [x] 차트: 도넛(카테고리 분포), 수평 바(Top 카테고리), 트리(계층), 테이블(요소), 에디터(SPARQL)
- [x] API 연동 (모든 REST/SPARQL 엔드포인트)
- [x] 다크 테마 UI

### API 업데이트
- [x] POST /api/reasoning 엔드포인트
- [x] GET / → 대시보드 HTML 서빙
- [x] /static/* 정적 파일 마운트
- [x] test_root 테스트 업데이트
- [x] test_run_reasoning 테스트 추가

### Docker 배포
- [x] Dockerfile (Python 3.12-slim)
- [x] docker-compose.yml (단일 서비스)
- [ ] Docker 실행 검증 (WSL에서 Docker 미설치)

### CLI 도구 (보류)
- [ ] convert 명령어
- [ ] query 명령어
- [ ] validate 명령어

> **결정 (AD-008)**: React 프레임워크 대신 vanilla JS SPA로 구현. 빌드 과정 불필요.
> CLI 도구는 Python 클라이언트(Phase 3)와 SPARQL 에디터(대시보드)로 기능 대체.

### 테스트
- [x] 91/91 테스트 통과
- [x] 커버리지 85%+

### 문서화
- [x] DEVLOG Phase 5 섹션
- [x] README 업데이트 (대시보드, Docker, API 추가)
- [ ] 대시보드 사용 가이드 (별도 문서)

---

**Document Version**: v2.0
**Last Updated**: 2026-02-03
