# Phase 1: IFC 파싱 및 RDF 변환 - Checklist

## Metadata

- **Phase**: Phase 1
- **Status**: ❌ Not Started
- **Target Completion**: 2026-02-24

---

## Completion Criteria

**Phase 1는 다음 조건을 모두 만족할 때 완료됩니다:**

1. ☐ IFC 파서 모듈 구현 완료 (파싱, 엔티티 추출, 검증)
2. ☐ RDF 변환 모듈 구현 완료 (매핑, 직렬화)
3. ☐ Triple Store 연동 완료 (삽입, 배치 처리)
4. ☐ 단위 테스트 커버리지 > 70%
5. ☐ 224MB IFC 파일 변환 성공 (< 30분)

---

## 1. IFC 파서 모듈 ☐

### 1.1 기본 기능

- [ ] `src/parser/ifc_parser.py` 작성 완료
  - [ ] IFCParser 클래스 구현
  - [ ] `__init__(file_path)` 메서드
  - [ ] `open()` 메서드 (ifcopenshell 활용)
  - [ ] `get_schema()` 메서드 (IFC4 확인)
  - [ ] `get_entities(type)` 메서드
  - [ ] `get_entity_count()` 메서드
  - [ ] `validate()` 메서드

### 1.2 엔티티 추출

- [ ] 주요 엔티티 타입 추출 성공
  - [ ] IfcWall 추출
  - [ ] IfcColumn 추출
  - [ ] IfcBeam 추출
  - [ ] IfcSpace 추출
  - [ ] IfcBuilding 추출
  - [ ] IfcStorey 추출
  - [ ] IfcMaterial 추출
  - [ ] IfcPropertySet 추출

### 1.3 오류 처리

- [ ] 파일 존재 여부 확인
- [ ] IFC 스키마 버전 검증 (IFC4만 허용)
- [ ] 손상된 파일 처리
- [ ] 로깅 구현 (INFO, WARNING, ERROR)

---

## 2. RDF 변환 모듈 ☐

### 2.1 기본 구조

- [ ] `src/converter/ifc_to_rdf.py` 작성 완료
  - [ ] RDFConverter 클래스 구현
  - [ ] `convert_file(ifc_file)` 메서드
  - [ ] `convert_entity(entity)` 메서드
  - [ ] `map_entity_type(ifc_type)` 메서드
  - [ ] `map_property(prop_name, prop_value)` 메서드

### 2.2 네임스페이스 관리

- [ ] `src/converter/namespace_manager.py` 작성
  - [ ] ifc 네임스페이스 정의 (`http://ifcowl.openbimstandards.org/IFC4_ADD2#`)
  - [ ] ex 네임스페이스 정의 (프로젝트용)
  - [ ] rdf, rdfs, xsd 네임스페이스

### 2.3 매핑 룰

- [ ] `src/converter/mapping.py` 작성
  - [ ] 최소 50개 IFC 엔티티 타입 → ifcOWL 클래스 매핑
  - [ ] 데이터 타입 변환 (IfcLabel → xsd:string, IfcReal → xsd:double)
  - [ ] 관계 매핑 (RelDefinesByProperties, RelContainedInSpatialStructure)

### 2.4 직렬화

- [ ] `src/converter/serializer.py` 작성
  - [ ] Turtle 포맷 출력
  - [ ] RDF/XML 포맷 출력 (선택)
  - [ ] JSON-LD 포맷 출력 (선택)

---

## 3. Triple Store 연동 ☐

### 3.1 기본 연동

- [ ] `src/storage/triple_store.py` 작성 완료
  - [ ] TripleStore 클래스 구현
  - [ ] `__init__(endpoint)` 메서드
  - [ ] `insert(triples)` 메서드
  - [ ] `insert_graph(graph)` 메서드
  - [ ] `query(sparql)` 메서드
  - [ ] `clear()` 메서드

### 3.2 배치 처리

- [ ] `src/storage/batch_writer.py` 작성
  - [ ] 1,000 triple 단위 배치 처리
  - [ ] 진행 상황 모니터링
  - [ ] 트랜잭션 관리 (오류 시 롤백)

### 3.3 GraphDB 연동

- [ ] `src/storage/graphdb_client.py` 작성
  - [ ] GraphDB SPARQL 엔드포인트 연결
  - [ ] INSERT DATA 쿼리 실행
  - [ ] Repository 생성 및 관리

---

## 4. 테스트 완료 ☐

### 4.1 단위 테스트

**IFCParser 테스트**
- [ ] `tests/test_ifc_parser.py` 작성
  - [ ] test_open_ifc_file()
  - [ ] test_get_schema()
  - [ ] test_extract_walls()
  - [ ] test_extract_spaces()
  - [ ] test_invalid_file()
  - [ ] test_large_file() (224MB)

**RDFConverter 테스트**
- [ ] `tests/test_rdf_converter.py` 작성
  - [ ] test_convert_entity()
  - [ ] test_namespace_mapping()
  - [ ] test_entity_type_mapping()
  - [ ] test_property_mapping()
  - [ ] test_serialization()

**TripleStore 테스트**
- [ ] `tests/test_triple_store.py` 작성
  - [ ] test_connection()
  - [ ] test_insert_triples()
  - [ ] test_insert_graph()
  - [ ] test_query()
  - [ ] test_clear()

### 4.2 통합 테스트

- [ ] `tests/test_integration.py` 작성
  - [ ] test_end_to_end_conversion()
    - [ ] IFC 파일 로딩
    - [ ] RDF 변환
    - [ ] Triple Store 저장
    - [ ] SPARQL 쿼리로 검증
  - [ ] test_batch_processing()
  - [ ] test_large_file_conversion() (224MB)

### 4.3 커버리지

- [ ] 테스트 커버리지 > 70%
  - [ ] `pytest --cov=src tests/` 실행
  - [ ] 커버리지 리포트 생성
  - [ ] 미커버 영역 확인 및 추가 테스트

---

## 5. 성능 검증 ☐

### 5.1 변환 성능

- [ ] **nwd4op-12.ifc (224MB) 변환 성공**
  - [ ] 파싱 시간 측정
  - [ ] RDF 변환 시간 측정
  - [ ] Triple Store 저장 시간 측정
  - [ ] 총 변환 시간 < 30분
  - [ ] 메모리 사용량 < 4GB

- [ ] **nwd23op-12.ifc (311MB) 변환 시도**
  - [ ] 변환 성공 여부 확인
  - [ ] 성능 지표 기록

### 5.2 데이터 품질

- [ ] **변환 정확성 검증**
  - [ ] 생성된 RDF triple 수 > 1,000
  - [ ] 엔티티 손실률 < 1%
  - [ ] SPARQL 쿼리로 주요 엔티티 조회 성공
    - [ ] IfcWall 조회
    - [ ] IfcSpace 조회
    - [ ] IfcBuilding 조회

---

## 6. 문서화 ☐

### 6.1 코드 문서화

- [ ] 모든 클래스 및 메서드에 docstring 작성
- [ ] 타입 힌팅 (Type Hints) 적용
- [ ] 주요 로직에 주석 추가

### 6.2 사용 예제

- [ ] `examples/phase1_example.py` 작성
  - [ ] IFC 파싱 예제
  - [ ] RDF 변환 예제
  - [ ] Triple Store 저장 예제

### 6.3 API 문서

- [ ] API 참조 문서 생성 (선택)
  - [ ] Sphinx 또는 MkDocs 사용
  - [ ] 클래스 및 메서드 설명

---

## 7. Phase 1 Exit Criteria ☐

**Phase 1는 다음 조건을 모두 만족해야 완료됩니다:**

- [ ] **기능 완성**
  - [ ] IFC 파서 모듈 구현 완료
  - [ ] RDF 변환 모듈 구현 완료
  - [ ] Triple Store 연동 완료

- [ ] **테스트 완료**
  - [ ] 단위 테스트 작성 및 통과
  - [ ] 통합 테스트 통과
  - [ ] 테스트 커버리지 > 70%

- [ ] **성능 검증**
  - [ ] 224MB IFC 파일 변환 성공 (< 30분)
  - [ ] 1,000개 이상 RDF triple 생성
  - [ ] Triple Store에 저장 및 조회 성공

- [ ] **문서화**
  - [ ] 코드 docstring 작성
  - [ ] 사용 예제 작성
  - [ ] Phase 1 완료 리포트

- [ ] **코드 품질**
  - [ ] 코드 리뷰 완료
  - [ ] 주요 버그 수정
  - [ ] PEP8 스타일 가이드 준수 (선택)

---

## Summary Checklist

| Category | Items | Completed |
|----------|-------|-----------|
| IFC 파서 모듈 | 11 | 0 |
| RDF 변환 모듈 | 13 | 0 |
| Triple Store 연동 | 10 | 0 |
| 테스트 | 18 | 0 |
| 성능 검증 | 10 | 0 |
| 문서화 | 7 | 0 |
| **Total** | **69** | **0** |

**Overall Completion**: 0%

---

## Next Steps After Phase 1

1. PROGRESS.md 업데이트 (Phase 1 → Completed)
2. Phase 2 시작 (SPARQL 쿼리 엔드포인트 구축)
3. API 서버 개발 착수

---

**Document Version**: v1.0
**Last Updated**: 2026-02-03
**Status**: ❌ Not Started
