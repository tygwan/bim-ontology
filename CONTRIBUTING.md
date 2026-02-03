# Contributing Guide

## 개발 환경 설정

```bash
git clone https://github.com/tygwan/bim-ontology.git
cd bim-ontology
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 코드 스타일

- Python 3.12+ 타입 힌트 사용 (`str | None` 문법)
- docstring은 한국어로 작성
- 함수/클래스에 타입 힌트 필수
- 들여쓰기: 4 spaces

## 브랜치 전략

- `main`: 안정 브랜치
- `feature/*`: 기능 개발
- `fix/*`: 버그 수정

## 커밋 규칙

[Conventional Commits](https://www.conventionalcommits.org/) 형식:

```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add tests
refactor: code restructuring
```

## 테스트

```bash
# 전체 테스트
python -m pytest tests/ -v

# 커버리지
python -m pytest tests/ --cov=src --cov-report=term-missing

# 특정 테스트
python -m pytest tests/test_api.py -v
```

모든 PR은 테스트 통과 필수 (91/91).

## PR 프로세스

1. feature 브랜치 생성
2. 코드 작성 및 테스트 추가
3. `pytest tests/ -v` 전체 통과 확인
4. PR 생성 (main ← feature)
5. 리뷰 후 squash merge

## 프로젝트 구조

```
src/
├── parser/          # IFC 파싱
├── converter/       # RDF 변환
├── storage/         # TripleStore
├── cache/           # 쿼리 캐시
├── inference/       # OWL/RDFS 추론
├── api/             # FastAPI 서버
├── dashboard/       # 웹 대시보드
└── clients/         # Python 클라이언트
```

## 이슈 보고

GitHub Issues에서 다음 정보와 함께 등록:
- 재현 단계
- 예상 동작 vs 실제 동작
- Python 버전, OS 정보
