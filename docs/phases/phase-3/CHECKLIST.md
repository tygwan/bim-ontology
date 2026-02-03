# Phase 3: 클라이언트 라이브러리 - Checklist

## Metadata

- **Phase**: Phase 3
- **Status**: Completed
- **Completed**: 2026-02-03

---

## Completion Criteria

- [x] Python 클라이언트 구현 완료
- [ ] Java 클라이언트 구현 (보류 - AD-005)
- [x] 사용 예제 5개 작성
- [x] 클라이언트 테스트 통과

---

## Checklist

### Python 클라이언트
- [x] `src/clients/python/client.py` - BIMOntologyClient 클래스
  - [x] `from_ifc(path)` - IFC 파일에서 직접 생성
  - [x] `from_rdf(path)` - RDF 파일에서 생성
  - [x] `from_api(url)` - 원격 API 서버 연결
  - [x] `query(sparql)` 메서드 (로컬/원격 자동 분기)
  - [x] `get_buildings()` 헬퍼
  - [x] `get_storeys()` 헬퍼
  - [x] `get_elements(category, limit)` 헬퍼
  - [x] `get_statistics()` 헬퍼
  - [x] `get_categories()` 헬퍼
  - [x] `get_hierarchy()` 헬퍼
  - [x] `count_triples()` 헬퍼
  - [x] `get_element_detail(uri)` 헬퍼

### 사용 예제
- [x] `examples/01_basic_query.py` - 기본 SPARQL 쿼리
- [x] `examples/02_building_analysis.py` - 건물 분석
- [x] `examples/03_element_statistics.py` - 요소 통계
- [x] `examples/04_hierarchy_explorer.py` - 계층 탐색
- [x] `examples/05_custom_sparql.py` - 커스텀 SPARQL

### Java 클라이언트 (보류)
- [ ] Java BIMOntologyClient 클래스
- [ ] pom.xml 작성

> **결정 (AD-005)**: Java/JavaScript 클라이언트는 보류.
> REST API가 있으므로 다른 언어는 HTTP 호출로 충분.

### 테스트
- [x] `tests/test_client.py` - 13개 클라이언트 테스트
  - [x] from_ifc 초기화
  - [x] from_api 원격 모드
  - [x] requires_store_or_url 검증
  - [x] 모든 헬퍼 메서드 테스트
  - [x] 커스텀 쿼리 테스트
- [x] 13/13 테스트 통과

### 아키텍처 결정
- [x] AD-004: 듀얼 모드 클라이언트 (로컬 + 원격)
- [x] AD-005: Java 클라이언트 보류

---

**Document Version**: v2.0
**Last Updated**: 2026-02-03
