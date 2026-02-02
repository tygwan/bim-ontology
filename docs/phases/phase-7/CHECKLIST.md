# Phase 7: MVP 배포 및 검증 - Checklist

## Completion Criteria

- ☐ 프로덕션 배포 완료
- ☐ 2개 IFC 파일 변환 성공
- ☐ PRD Success Criteria 모두 충족
- ☐ 검증 리포트 작성
- ☐ 프로젝트 회고 완료

---

## Checklist

### 배포
- [ ] 프로덕션 환경 설정
- [ ] Docker Compose 배포
- [ ] GraphDB 데이터 마이그레이션
- [ ] API 서버 실행
- [ ] 대시보드 실행

### PRD Success Criteria 검증
- [ ] **SC-001**: nwd4op-12.ifc (224MB) 변환 성공
- [ ] **SC-001**: nwd23op-12.ifc (311MB) 변환 성공
- [ ] **SC-002**: 10개 SPARQL 쿼리 실행 가능
- [ ] **SC-003**: Python 클라이언트 쿼리 성공
- [ ] **SC-004**: 쿼리 응답 시간 < 2초
- [ ] **SC-005**: RESTful API JSON 응답
- [ ] **SC-006**: CLI 변환 및 쿼리 실행
- [ ] **SC-007**: 대시보드 통계 시각화

### 성능 검증
- [ ] 변환 시간: 200MB < 30분
- [ ] 쿼리 응답 시간: 단순 < 2초, 복잡 < 10초
- [ ] Triple 저장 수: > 100만
- [ ] 동시 사용자: 10명 지원

### 문서화
- [ ] 검증 리포트
- [ ] 프로젝트 회고 (Retrospective)
- [ ] README.md 최종 업데이트
- [ ] 릴리스 노트 v1.0

---

**Document Version**: v1.0
