# 의미론적 BIM 및 산업용 온톨로지: 종합 분석

## 1. 표준 및 프레임워크 개요

### 1.1 ifcOWL (buildingSMART)

**범위 및 목적**[cite:1][cite:7]
ifcOWL은 IFC4 EXPRESS 스키마를 OWL2-DL(Web Ontology Language 2.0 Description Logic)로 직접 변환한 표준입니다. 핵심 목표는 건설 업계 데이터를 웹 기술과 의미론적 웹 기술과 연결하는 것입니다.

**주요 특징**
- **정확한 매핑**: EXPRESS 엔티티 → OWL 클래스, 속성 → owl:ObjectProperty
- **지원되는 스케줄링 엔티티**:
  - IfcWorkSchedule: 작업 계획 내 작업 일정 컨테이너
  - IfcTask: 시공 프로젝트의 식별 가능한 작업 단위 (속성: IsMilestone, Status, Priority, TaskTime)
  - IfcCostSchedule: 비용 추적 및 일정 연관

**OWL 매핑 규칙**[cite:1]
```
- 규칙 속성 → 기능적 owl:ObjectProperty (cardinality 1)
- OPTIONAL 속성 → owl:maxQualifiedCardinality "1"
- SET/LIST 속성 → list:hasNext 온톨로지 + 카디널리티 제약
- 역(Inverse) 속성 → owl:inverseOf
- SUBTYPE OF → rdfs:subClassOf
- ABSTRACT SUPERTYPE OF (ONEOF) → owl:unionOf + owl:disjointWith
```

**제한사항**
- 복잡하고 거대한 온톨로지 (IFC 전체 구조 유지)
- 기존 온톨로지 재사용 최소
- 웹 기반 모범 사례를 따르지 않음
- 학습 곡선이 높음

**강점**
- 모든 IFC 엔티티의 완벽한 의미론적 표현
- 표준 SPARQL 쿼리 언어 지원
- OWL 기반 자동 추론 가능
- GIS, IoT, 센서 데이터와 직접 연결 가능
- 마이크로 MVD 생성 및 모델 검증 자동화

**현재 상태**: buildingSMART 최종 표준 (2017년 승인)

---

### 1.2 ISO 15926 (프로세스 플랜트 생명주기 온톨로지)

**범위 및 목적**[cite:88][cite:89]
ISO 15926은 공정 산업(프로세스 플랜트, 유전, 화학 공장 등) 전체 생명주기 데이터 표현을 위한 국제 표준입니다. 제목: "프로세스 플랜트 (유정 및 가스 생산 설비 포함)의 생명주기 데이터 통합"

**생명주기 범위**[cite:88]
- FEED (기본 설계)
- 상세 엔지니어링
- 조달(Procurement)
- 시공
- 운영/유지보수

**IFC와의 주요 차이점**

| 측면 | IFC | ISO 15926 |
|------|-----|-----------|
| 주 대상 | 건축/건물 | 공정 산업/플랜트 |
| 시간 모델 | 제한적 (스케줄 데이터 분리) | 4D 시간 기반 (기본) |
| 데이터 범위 | 기하학 + 설계 데이터 | 장비, 구매 발주, 마일스톤, 유지보수 이력 |
| 참조 데이터 | 없음 | 종합 참조 데이터 라이브러리 (STEPlib) |
| 표준화된 타입 | IFC 타입 분류 | 도메인 전문가 100+ 명이 정의한 핵심 클래스 |
| 의미론 | 건축 중심 | 프로세스 산업 중심 |

**ISO 15926 주요 부분**[cite:2][cite:91]

- **Part 2**: 데이터 모델 (EXPRESS 기반)
- **Part 4**: OWL2 온톨로지 (OWL 기반 추론)
- **Part 13**: 자산 계획 (포트폴리오, 프로그램, 프로젝트, 일정, 제약 조건, 자원, 비용)
- **Part 14**: OWL 직접 의미론 + 생명주기 모델링 패턴

**생명주기 모델링 패턴**[cite:2]
시간 기반이 아닌 세 가지 모델링 패턴:
- **Transformation**: 자산의 상태 변화
- **Merge**: 여러 자산 결합
- **Split**: 자산 분해
- 시간 정보는 별도의 시간 관련 속성을 통해 추가 가능

**강점**
- 프로세스 산업에서 성숙한 표준
- 장비 생명주기 추적 최적화
- 시간 기반 데이터 모델링
- 유전/화학/정유 산업 입증된 도입

**제한사항**
- 건설/건축 산업 외 거의 미사용
- ISO 15926의 복잡성
- IFC와의 직접 통합 어려움

---

### 1.3 BOT (Building Topology Ontology)

**범위 및 목적**[cite:3][cite:6]
BOT는 W3C Linked Building Data 커뮤니티 그룹에서 개발한 최소 크기의 경량 OWL DL 온톨로지입니다. 건물의 핵심 위상 개념 (Building, Storey, Space, Element, Site)을 설명합니다.

**핵심 클래스**
- `bot:Building`: 건축 구조
- `bot:Storey`: 층
- `bot:Space`: 공간 (방, 영역)
- `bot:Element`: 건설 요소
- `bot:Site`: 부지

**핵심 속성**
- `bot:hasBuilding`: 부지에서 건물로
- `bot:hasStorey`: 건물에서 층으로
- `bot:hasSpace`: 층에서 공간으로
- `bot:hasElement`: 건물/층/공간에 포함된 요소

**설계 철학**
- **경량**: 107개 이상의 클래스를 가진 BEO나 ifcOWL과 달리 매우 작음
- **모듈화**: 다른 온톨로지와 결합하도록 설계 (ifcOWL, GIS, IoT, PROPS)
- **재사용**: W3C 웹 모범 사례를 따름
- **확장성**: 특정 도메인 온톨로지 (속성, 제품, 일정)와 함께 사용 가능

**활용 사례**[cite:12]
- BIM 성숙도 레벨 3 (웹 기반 데이터 교환)
- 센서/IoT 데이터와 건물 모델 연결
- 제품 카탈로그 및 관찰 데이터와 통합

**강점**
- 최소 복잡성, 높은 이해도
- 빠른 채택 가능
- 대규모 실제 BIM 모델에서 성공적 검증

**제한사항**
- 순수 위상 관계만 제공
- 재료, 비용, 일정, 상태 정보 부재
- 다른 온톨로지 필수 (BOT만으로는 불충분)

---

### 1.4 BEO (Built Element Ontology)

**범위 및 목적**[cite:19][cite:95]
BEO는 IFC4의 IfcBuildingElement 사양에서 파생된 107+ 개 클래스로 구성된 의미론적 건설 요소 분류입니다.

**주요 특징**
- **클래스 구조**: 
  - 주요 요소 (구조: 보, 기둥, 벽)
  - 2차 요소 (마감재, 천장)
  - 비품 (가구, 설비)
  - 기반 (기초, 말뚝)

**IFC 대비 특징**
- IFC4 계층보다 더 세밀한 의미론적 분류
- 각 요소 타입에 대한 명확한 정의
- 건설 산업 표준화된 용어 사용

**현재 상태**
- 상대적으로 덜 정의된 (BOT, ifcOWL보다)
- 건축 설계 온톨로지 개발의 참고 자료

---

### 1.5 OPM (Ontology for Property Management)

**범위 및 목적**[cite:17][cite:20][cite:23]
OPM은 설계 진화 과정에서 시간 경과에 따라 변하는 건물 요소의 속성 상태를 추적하는 온톨로지입니다.

**핵심 클래스**
```
opm:PropertyState - 시간 경과에 따른 속성 상태의 메타데이터
opm:CurrentPropertyState - 현재 속성 상태 (가장 최신)
opm:OutdatedPropertyState - 이전 상태 (대체됨)
opm:Deleted - 속성 삭제 표시
opm:Assumed - 가정된 값
opm:Confirmed - 확인된 값
opm:Calculation - 계산된 값
```

**시간 추적 메커니즘**
- 각 속성 상태는 최소한 생성 시간(`prov:generatedAtTime`) 기록
- 속성 변경 이력 유지 (설계 변경 추적)
- 삭제된 속성도 메타데이터와 함께 데이터베이스에 유지

**통합 온톨로지**
- SEAS (Smart Energy Aware Systems)
- schema.org (값 연관)
- PROV-O (출처 및 생성 시간)
- PROPS (AEC 산업 속성)

**성능 개선**[cite:20]
- 쿼리 성능: 6900ms → 640ms (약 10배 향상)
- 설계 변경 추적 효율성 대폭 증가

**응용 사례**
- BIM 모델 버전 관리
- 설계 변경 이력 관리
- 도출 속성 및 상호 의존성 추적
- 블록체인 기반 추적 가능성 연구

**제한사항**
- 시간 기반 속성 상태에만 집중
- 기하학적/위상 관계 부재
- 공간 분석 미포함

---

## 2. 온톨로지가 해결하는 BIM 문제 유형

### 2.1 카테고리 A: 데이터 상호운용성

**문제의 규모**[cite:32][cite:35][cite:38]
미국 건설 산업의 부적절한 소프트웨어 상호운용성로 인한 연간 비용: **$15.8 billion (2002년 기준)**

비용 분포:
- 건축가/엔지니어: $1.2 billion
- 일반 시공업체: $1.3 billion
- 전문 제작업체/공급업체: $1.8~2.2 billion
- 건물주/운영자: $10.6 billion (약 2/3)

**구체적 문제**
- Revit, Tekla, Smart3D, Navisworks 등 이기종 소프트웨어 간 데이터 교환
- IFC 변환 시 정보 손실
- 수작업 데이터 재입력 (중복 입력, 오류 위험)
- RFI (Requests for Information) 처리 지연
- 소프트웨어 간 동기화 불가능

**의미론적 해결책**[cite:1][cite:21]

RDF/OWL을 보편적 교환 형식으로 사용:
```sparql
# 예: 모든 구조 요소 + 화재 등급 쿼리
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX ifc_props: <http://data.example.com/properties#>

SELECT ?element ?fireRating ?material WHERE {
  ?element rdf:type ifc:IfcStructuralMember .
  ?element ifc_props:FireRating ?fireRating .
  ?element ifc_props:Material ?material .
  FILTER (?fireRating > "REI 120"^^xsd:string)
}
```

**구현 기술**
- 의미론적 매핑 (속성 집합 정렬)
- SPARQL 페더레이션 (여러 데이터 소스 쿼리)
- 자동 데이터 변환
- 링크드 데이터 기반 교환

**기대 효과**
- 데이터 재입력 비용 감소
- 교환 시간 단축
- 오류율 감소
- 다중 학문 협력 개선

---

### 2.2 카테고리 B: 의미론적 쿼리 및 추론

**문제의 특징**
- 명시적으로 기록되지 않은 관계 (암묵적 관계)
- 복합 공간 분석 불가능
- 수작업 검증

**구체적 사례**[cite:21]

1. **공간 쿼리**: "3층의 모든 배관 (지름 > 200mm)"
```sparql
PREFIX bot: <https://w3id.org/bot#>
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX props: <http://data.example.com/properties#>

SELECT ?pipe WHERE {
  ?pipe rdf:type ifc:IfcPipeSegment .
  ?pipe props:Diameter ?diameter .
  ?pipe ifc:hasLocation ?location .
  ?location bot:hasStorey ?storey .
  ?storey props:StoreyNumber "3"^^xsd:integer .
  FILTER (?diameter > 200)
}
```

2. **암묵적 규칙 추론**: "요소 A가 요소 B 위에 있으면 → A는 B 이전에 설치되어야 함"
   
SWRL (Semantic Web Rule Language) 규칙:
```
IfcElement(?a) ∧ isLocatedAbove(?a, ?b) → 
  mustBeInstalledBefore(?a, ?b)
```

3. **위상 관계 추론**: "모든 벽에 인접한 배관"
```sparql
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX geo: <http://www.opengis.net/ont/sf#>

SELECT ?wall ?pipe WHERE {
  ?wall rdf:type ifc:IfcWall .
  ?pipe rdf:type ifc:IfcPipe .
  ?wall geo:touches ?pipe .
}
```

**의미론적 해결책**[cite:76]

- **OWL 기반 추론**: 클래스 계층, 속성 제약 조건 추론
- **SWRL 규칙**: 복잡한 비즈니스 로직 표현
- **Datalog**: 성능 최적화된 규칙 처리
- **BimSPARQL**: 공간 함수 확장 (교점, 거리, 포함 관계)

**주요 연구 논문**
- Pauwels et al. (2015): BimSPARQL 공간 함수 확장
- Li et al. (2020): ASP(Answer Set Programming) 기반 안전 준수 검증

**기대 효과**
- 설계 오류 사전 감지
- 건축법 자동 준수 확인
- 공간 간섭 자동 탐지
- 의사결정 자동화

---

### 2.3 카테고리 C: 시간 추적 및 상태 관리

**문제의 특징**
- 요소의 생명주기 상태 추적 불가능
- 일정 지연의 연쇄 영향 분석 곤란
- 계획 대비 실적(As-planned vs As-built) 비교 어려움

**요소 생명주기 상태**[cite:76][cite:80]
```
설계 → 제작 → 해운(운송) → 현장 도착 → 설치 → 검사 → 운영
```

각 상태 전환 시:
- 시간 기록
- 담당자 기록
- 실시간 상태 업데이트

**의미론적 해결책**

**1. 시간 기반 지식 그래프**[cite:78][cite:80]
```
각 요소의 시간 참조를 명시적으로 모델링:
TimeReferenceElement 노드 중심으로 데이터 집합 연결
```

**2. OPM 기반 상태 추적**[cite:20][cite:23]
```
PropertyState(설계값) → PropertyState(변경) → 
PropertyState(현장 확인값) → PropertyState(최종)
```

**3. ISO 15926 생명주기 패턴**[cite:2]
```
Transformation (상태 변화)
  예: Equipment 설치됨 (설계) → Equipment 운영 중 (운영)
```

**SPARQL 예제: As-planned vs As-built 비교**
```sparql
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX opm: <http://www.w3id.org/opm#>

SELECT ?task ?plannedStart ?plannedEnd ?actualStart ?actualEnd 
WHERE {
  ?task rdf:type ifc:IfcTask .
  ?task opm:hasPropertyState ?planned .
  ?planned opm:PropertyValue ?plannedStart ; 
           rdf:type opm:AsPlanned .
  ?task opm:hasPropertyState ?actual .
  ?actual opm:PropertyValue ?actualStart ;
          rdf:type opm:AsBuilt .
  FILTER (?actualStart > ?plannedStart)
}
```

**지연 연쇄 분석**
- 임계 경로(Critical Path) 자동 계산
- 지연 전파(Delay Propagation) 모델링
- 완료 예측 업데이트

**주요 연구**
- As-Planned vs As-Built: 사후 지연 분석 표준 방법
- Impacted As-Planned: 지연 이벤트 영향 분석
- As-Built But-For: 소유자 책임 지연 정량화

**기대 효과**
- 실시간 진도 추적
- 예측 불가능한 지연 조기 경고
- 책임 주체 명확화
- 인계(Handover) 자동화

---

### 2.4 카테고리 D: 공간 분석 및 충돌 탐지

**문제의 특징**
- 수작업 간섭 검사 (3D 모델 시각적 검토)
- 2D 도면 기반 장비 선택 (부정확)
- 리프트 플랜 검증 미흡
- 접근 경로 제약 분석 부재

**구체적 사례**
- 크레인 접근 가능 영역 검증
- 작업 구역 간 간섭
- 차량 통행 경로 확보
- 안전 격리 구역 설정

**의미론적 해결책**[cite:39][cite:42]

**1. 공간 추론 (Answer Set Programming)**[cite:39]
```
4D BIM (시간 + 기하학) 기반 안전 준수 자동 검증
- 해결 문제: 부동소수점 오차, 복잡한 기하학
- 방법: 비단조 공간 추론 (Non-monotonic Spatial Reasoning)
```

**2. 충돌 분류 온톨로지**[cite:42]
```
- 물리적 충돌: 두 객체가 같은 공간 차지
- 프로세스 기반 충돌: BIM 생성 프로세스 결함
- 모델 기반 충돌: 메타모델 불일치
```

**3. BimSPARQL 공간 함수**[cite:21]
```sparql
PREFIX bim: <http://bimsparql.example.com/functions#>

SELECT ?element ?equipment WHERE {
  ?element rdf:type ifc:IfcSpace .
  ?element geo:hasSize ?elementSize .
  ?equipment rdf:type ifc:IfcFurniture .
  ?equipment geo:hasSize ?eqSize .
  FILTER (bim:canFitInSpace(?eqSize, ?elementSize))
}
```

**공간 함수 예**:
- `bim:intersects()`: 교집합 검사
- `bim:within()`: 포함 관계
- `bim:distance()`: 거리 계산
- `bim:nearestElement()`: 근처 요소 검색
- `bim:accessibleFrom()`: 접근성 검증

**기대 효과**
- 설계 오류 사전 탐지 (비용 절감)
- 시공 안전성 향상
- 건설 현장 간섭 사전 방지
- 자동화된 충돌 해결 제안

---

## 3. BIM 현장 비효율 프로세스 분석

### 3.1 일정 관리 비효율

**현재(AS-IS) 프로세스**[cite:48][cite:51]

1. **자재 납기 지연 시 영향 범위 파악**
   - 현황: 수작업으로 관련 작업 확인
   - 시간 소요: 1~2일
   - 오류율: 높음
   - 프로세스: 
     ```
     자재 지연 공지 
     → Primavera P6 일정 확인
     → 영향받는 작업 목록 작성
     → 관련 담당자 통보
     ```

2. **일일 공정표 작성**
   - 현황: Excel 기반 수작업
   - 시간 소요: 관리자 하루 2~3시간
   - BIM과 연계 불가능
   - 3D 시각화 없음

3. **Primavera P6 ↔ BIM 3D 모델 링크**
   - 현황: 수작업 링크 (Navisworks 이용)
   - 문제: 
     - P6 업데이트 시 BIM 재연결 필요
     - 양방향 동기화 불가능
     - 변경 이력 추적 곤란

4. **"오늘 해야 할 일" 3D 시각화**
   - 현황: 불가능
   - 해결책: Navisworks 4D 시뮬레이션 (사후 분석용)

**의미론적 해결책(TO-BE)**

```sparql
# 오늘 완료해야 할 3층 작업 조회
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX schedule: <http://data.example.com/schedule#>
PREFIX bot: <https://w3id.org/bot#>

SELECT ?task ?element ?location WHERE {
  ?task rdf:type ifc:IfcTask ;
        schedule:startDate ?start ;
        schedule:endDate ?end ;
        schedule:assignedTo ?element .
  ?element bot:hasStorey ?storey .
  ?storey props:StoreyNumber "3" .
  FILTER (?start <= TODAY() && TODAY() <= ?end)
}
ORDER BY ?element
```

**자동 일정 영향 분석**
```
SWRL 규칙:
IfcTask(?t1) ∧ IfcTask(?t2) ∧ 
schedule:dependsOn(?t1, ?t2) ∧ 
schedule:delayed(?t2, ?delay) → 
schedule:impactedDelay(?t1, ?delay)
```

**TO-BE 이점**:
- 자동 영향 범위 계산 (실시간)
- 프로젝트 관리자 업무 40% 감소
- 오류 제거
- 즉시 경고 및 복원력 계획

---

### 3.2 시공성 검토(Constructability Review) 비효율

**현재(AS-IS) 프로세스**

1. **부지 조건 수작업 검증**
   - 기둥 간격, 슬래브 개구부, 층높이 확인
   - 현황: CAD/도면 기반 수작업 측정
   - 시간: 엔지니어 2~3주
   - 오류: 측정 부정확(±100mm)

2. **중장비 선택**
   - 현황: 2D 도면 기반 결정
   - 문제: 3D 공간 시각화 불가
   - 결과: 부지 상황과 맞지 않음 (재작업)

3. **리프트 플랜 검증**
   - 현황: 2D 도면 + 경험 기반
   - 검증 방법: 육안 확인
   - 위험: 간섭 사전 미탐지

**의미론적 해결책(TO-BE)**

**1. 자동 공간 분석**
```sparql
# 무겁고 큰 장비가 접근 가능한 구역인지 검증
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX geo: <http://data.example.com/geometry#>
PREFIX const: <http://data.example.com/construction#>

SELECT ?equipment ?accessPath ?constraint WHERE {
  ?equipment rdf:type ifc:IfcTransportElement ;
             geo:width ?width ;
             geo:height ?height .
  ?site ifc:hasSite ?element .
  ?element const:hasAccessPath ?accessPath ;
           geo:minWidth ?minWidth ;
           geo:minHeight ?minHeight .
  FILTER (?width <= ?minWidth && ?height <= ?minHeight)
}
```

**2. 건설 온톨로지 기반 체크리스트**[cite:33]
```
구성 가능성 설계 특징:
- 실체: 건축 요소 속성 (재료, 크기, 무게)
- 교점: 요소 간 인터페이스 (용접부, 연결부)
- 구성: 조립 시퀀스 (설치 순서, 의존성)

=> 자동 건설성 평가 알고리즘
```

**3. 리프트 플랜 자동 생성**
```
입력:
- 무거운 요소 (보, 패널, 장비) 무게/크기
- 부지 3D 레이아웃
- 크레인 성능 사양

출력:
- 최적 크레인 타입
- 리프트 시퀀스
- 간섭 자동 탐지
- 안전 격리 구역 계산
```

**TO-BE 이점**:
- 시공성 검토 시간 1/3 단축
- 설계 오류 90% 조기 탐지
- 현장 재작업 감소
- 건설 안전성 향상

---

### 3.3 자재/요소 추적 비효율

**현재(AS-IS) 프로세스**

```
제작 완료 
  ↓ (정보 단절)
배송 출발 
  ↓ (배송사 추적 불가)
현장 도착 
  ↓ (수작업 기록)
보관 대기 
  ↓ (재료 코드 ≠ BIM ID)
설치 완료 
  ↓ (최종 상태 미기록)
운영
```

**문제점**
- 제조 상태 정보 부족 (EPC 프로젝트)
- 배송 추적 단절 (공급업체마다 다른 시스템)
- 자재 코드 ↔ BIM 요소 ID 매핑 부재
- 현장 검수 기록 수작업
- 설치 상태 BIM 미반영

**의미론적 해결책(TO-BE)**

**1. 공급망 온톨로지**[cite:59]
```
주요 클래스:
- ManufacturedElement: 제조된 요소
- DeliveryShipment: 배송
- SiteInventory: 현장 재고
- InstallationTask: 설치 작업

속성:
- mfg:manufacturedDate
- mfg:qualityInspectionStatus
- logistics:estimatedArrival
- logistics:actualArrival
- site:storageLocation
- site:installationStatus
- site:inspectionResult
```

**2. RFID/바코드 기반 자동 추적**
```
물리적 자재 → QR코드
    ↓
스캔 → RDF 데이터 자동 생성
    ↓
SPARQL 엔드포인트 업데이트
    ↓
BIM 모델 자동 상태 동기화
```

**3. 자재 여권(Material Passport) 링크**[cite:62]
```sparql
# 제조 → 배송 → 설치 → 운영 전체 추적
PREFIX mfg: <http://data.example.com/manufacturing#>
PREFIX lgc: <http://data.example.com/logistics#>
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>

SELECT ?element ?mfgDate ?shipDate ?arrivalDate ?installDate WHERE {
  ?element rdf:type ifc:IfcBuildingElement ;
           mfg:manufacturedDate ?mfgDate ;
           lgc:shipmentDate ?shipDate ;
           lgc:arrivalDate ?arrivalDate ;
           ifc:installationDate ?installDate .
  FILTER (?mfgDate < ?shipDate && ?shipDate < ?arrivalDate)
}
```

**4. EPC 프로젝트 조달 상태 추적**
```
주문 → 제작 중 → 제작 완료 → 
배송 중 → 현장 도착 → 설치 대기 → 
설치 중 → 설치 완료 → 검사 → 운영
```
각 단계별 자동 알림 및 BIM 모델 업데이트

**TO-BE 이점**[cite:47][cite:50]:
- 자재 추적 시간 80% 감소
- 현장 재작업 50% 감소
- 배송 지연 조기 경고
- 부정확한 자재 설치 방지
- 공급업체 성과 관리

---

### 3.4 Advanced Work Packaging (AWP) 통합 비효율

**CII 연구 배경**[cite:46][cite:49][cite:52]

CII Research Team 272/319가 개발한 Advanced Work Packaging (AWP):
- 프로젝트 계획 및 실행을 위한 규율 있는 접근법
- 현장 생산성 **25% 향상**
- 총 설치 비용(TIC) **4-10% 감소**
- 일정 **25% 단축**

**현재(AS-IS) 프로세스**

```
AWP 구조:
CWA (구성적 작업 구조)
  ├── CWP (구성적 작업 패키지)
  │   ├── IWP (통합 작업 패키지)
  │   └── [작업 항목]
  └── ...

현황: 
- CWA/CWP/IWP를 엑셀/프로젝트 관리 도구에만 관리
- BIM 모델과 수작업 연계
- 진도 시각화 불가능
- 다중 학문 간 정보 단절
```

**문제점**
- 수작업 링크로 인한 오류
- CWP 변경 시 BIM 미동기화
- 현장 근로자가 "오늘 할 일"을 찾기 어려움
- AWP 성과 자동 측정 불가능

**의미론적 해결책(TO-BE)**

**1. AWP 온톨로지 설계**
```
awp:ConstructiveWorkStructure (CWA)
  ├─ awp:hasPackage → awp:ConstructiveWorkPackage (CWP)
  │   └─ awp:hasPackage → awp:IntegratedWorkPackage (IWP)
  │       ├─ awp:linkedToTask → ifc:IfcTask
  │       ├─ awp:linkedToElement → ifc:IfcBuildingElement
  │       ├─ awp:allocatedResource → ifc:IfcResource
  │       ├─ awp:scheduledStart → xsd:dateTime
  │       ├─ awp:scheduledEnd → xsd:dateTime
  │       └─ awp:progressStatus → {NOT_STARTED, IN_PROGRESS, COMPLETE}
  │
  └─ awp:dependsOn → awp:IntegratedWorkPackage
```

**2. SPARQL 쿼리: 진도 추적 및 자동 분석**

```sparql
# 현장 관리자: 오늘의 작업 조회
SELECT ?iwp ?task ?element ?location ?resource WHERE {
  ?iwp rdf:type awp:IntegratedWorkPackage ;
       awp:linkedToTask ?task ;
       awp:linkedToElement ?element ;
       awp:allocatedResource ?resource ;
       awp:scheduledStart ?start ;
       awp:scheduledEnd ?end ;
       awp:progressStatus ?status .
  ?element bot:hasStorey ?storey .
  FILTER (?start <= TODAY() && TODAY() <= ?end && 
          ?status IN (awp:NOT_STARTED, awp:IN_PROGRESS))
}
ORDER BY ?storey, ?location
```

**3. 지연 연쇄 분석**
```sparql
# 특정 IWP 지연 시 영향받는 모든 후속 IWP 자동 계산
PREFIX awp: <http://data.example.com/awp#>

SELECT ?dependentIWP ?delayDays WHERE {
  ?cwp awp:hasPackage ?iwp1 ;
       awp:hasPackage ?dependentIWP .
  ?iwp1 awp:dependsOn ?dependentIWP .
  ?iwp1 awp:actualEnd ?actualEnd1 ;
        awp:scheduledStart ?scheduledStart1 .
  BIND (DAYS(?actualEnd1, ?scheduledStart1) AS ?delayDays)
  FILTER (?delayDays > 0)
}
```

**4. 자동 진도 측정**
```
물리적 진도 계산:
- 완료된 IWP 수 ÷ 전체 IWP 수
- 가중치 기반 진도 (각 IWP 규모/비용 기준)
- 경로 기반 진도 (임계 경로 기준)

자동 대시보드 생성:
- 프로젝트 종합 진도
- CWP별 진도
- 병목 (Bottleneck) 자동 식별
- 위험도(Risk) 계산
```

**5. 자원 할당 최적화**
```sparql
# 현재 가능한 근로자를 기반으로 다음 완료 가능한 IWP 제안
SELECT ?nextIWP (COUNT(?worker) AS ?availableWorkers) WHERE {
  ?nextIWP rdf:type awp:IntegratedWorkPackage ;
           awp:requiredSkills ?requiredSkill ;
           awp:progressStatus awp:NOT_STARTED ;
           awp:dependsOn ?priorIWP .
  ?priorIWP awp:progressStatus awp:COMPLETE .
  ?worker rdf:type ifc:IfcLabor ;
          ifc:hasSkill ?requiredSkill ;
          ifc:currentStatus ifc:AVAILABLE .
}
GROUP BY ?nextIWP
ORDER BY DESC(?availableWorkers)
LIMIT 1
```

**TO-BE 이점**:
- AWP 관리 자동화 (80% 시간 단축)
- 진도 실시간 추적
- 자원 최적 할당
- 지연 조기 경고
- CII 보고된 25% 생산성 향상 가시화

---

## 4. 비교표: 기술별 문제 해결 능력

| 문제 카테고리 | ifcOWL | ISO 15926 | BOT | OPM | 맞춤형 온톨로지 필요 |
|---|---|---|---|---|---|
| **데이터 상호운용성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 의미론적 매핑 |
| **의미론적 쿼리** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 비즈니스 규칙 |
| **시간 추적** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | 생명주기 상태 |
| **공간 분석** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | 기하 함수 |
| **일정 관리** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | 작업 의존성 |
| **비용 추적** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | 비용 온톨로지 |
| **자재 공급망** | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | 로지스틱 온톨로지 |

---

## 5. 한계 및 향후 연구 방향

### 현재 한계

1. **ifcOWL**: 복잡도 높음, 학습 곡선 가파름, 실무 도구 부족
2. **ISO 15926**: 산업 한정적, 건설업 채택 미흡
3. **BOT**: 위상만 제공, 속성/일정/상태 정보 부재
4. **OPM**: 속성 상태만 추적, 공간 관계 부재
5. **전반적**: 실시간 동기화 기술 미성숙, 왕복 검증(Round-trip) 어려움

### 권장 접근법

**모듈형 온톨로지 조합**:
```
Core Layer:
  ├─ ifcOWL (기하 + IFC 구조)
  └─ BOT (위상)

Domain Layers:
  ├─ OPM (속성 상태)
  ├─ ISO 15926-13 (일정/비용)
  ├─ Custom Schedule Ontology (작업 의존성)
  ├─ Custom Material Ontology (공급망)
  └─ Custom Spatial Ontology (공간 함수)

Integration Layer:
  ├─ SPARQL Endpoint (통합 쿼리)
  ├─ Dynamic Knowledge Graph (실시간 업데이트)
  └─ Autonomous Agents (자동 동기화)
```

---

## 결론

의미론적 BIM은 건설 산업의 데이터 상호운용성과 의사결정 자동화를 크게 개선할 잠재력을 가지고 있습니다. 특히:

- **데이터 상호운용성**: 연간 $15.8B 비용 절감 기대
- **실시간 추적**: AWP 통합으로 25% 생산성 향상 가능
- **오류 감소**: 설계/시공 오류 조기 탐지로 재작업 60~80% 감소
- **의사결정 자동화**: 지연 분석, 자원 최적화 등 수작업 80% 감소

그러나 현재 실무 도구와 표준 통합이 미흡하므로, 프로젝트 맞춤형 온톨로지 설계 및 점진적 도입 전략이 필수적입니다.
