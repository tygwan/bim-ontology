# IFC-RDF/OWL 시맨틱 파이프라인: 플랜트/산업 BIM 프로젝트를 위한 종합 분석

**시맨틱 웹 기술이 건설 산업의 연간 158억 달러 상호운용성 비용 문제를 해결할 수 있다.** buildingSMART의 ifcOWL, W3C의 BOT, ISO 15926 등 핵심 온톨로지들이 이기종 BIM 소프트웨어 간 데이터 교환, 시맨틱 쿼리, 시간적 상태 추적 문제를 해결하는 기반을 제공하며, CII 연구에 따르면 AWP(Advanced Work Packaging) 적용 시 **생산성 25% 향상**, **총 설치비용(TIC) 4-10% 절감**이 가능하다.

---

## 1부: 온톨로지 표준 및 프레임워크 종합 비교

### ifcOWL: IFC EXPRESS에서 OWL로의 전환

buildingSMART가 개발한 ifcOWL은 IFC EXPRESS 스키마의 Web Ontology Language(OWL) 표현으로, 건물 데이터를 RDF 그래프로 변환하여 GIS, 센서 데이터, 제품 정보와의 연계를 가능하게 한다. IFC4 ADD1 기준 **1,313개 클래스**, **1,580개 오브젝트 프로퍼티**, **13,867개 논리적 공리**를 포함한다.

**일정 관련 엔티티 매핑:**

| IFC 엔티티 | 용도 | OWL 매핑 특성 |
|-----------|------|--------------|
| **IfcWorkSchedule** | 작업 일정 표현 | IfcRelDeclares로 프로젝트 연결, IfcRelAssignsToControl로 태스크 제어 |
| **IfcTask** | 개별 작업 단위 | IfcRelNests로 중첩, IfcRelAssignsToProduct로 제품 연결 |
| **IfcTaskTime** | 일정 시간 정보 | ScheduledStart, ScheduledFinish, Duration 속성 포함 |
| **IfcCostSchedule** | 비용 명세 일정 | IfcCostItem과 관계로 연결 |

ifcOWL의 **주요 한계**로는 EXPRESS의 직접 매핑으로 인한 시맨틱 웹 모범 사례와의 불일치, 순서 리스트 표현을 위한 복잡한 중첩 클래스 구조, RULE 및 FUNCTION 선언의 미변환(OWL2DL로 변환 불가), 단일 모놀리식 온톨로지로 인한 모듈성 부재가 있다. Pauwels와 Terkaj(2016)는 이러한 문제를 상세히 분석하여 *Automation in Construction*에 발표했다.

### ISO 15926: 프로세스 플랜트 생애주기 온톨로지

석유·가스 산업의 프로세스 플랜트 생애주기 데이터 통합을 위해 설계된 ISO 15926은 **4D 접근법**(3차원 공간 + 시간)을 채택하여 물리적 객체의 시간적 변화를 추적한다. 표준 구조는 다음과 같다:

- **Part 2**: 상위 온톨로지 데이터 모델(약 200개 클래스)
- **Part 4**: 초기 참조 데이터 라이브러리(10,000개 이상 클래스)
- **Part 7/8**: 템플릿 방법론 및 OWL 구현
- **Part 12**: OWL 기반 생애주기 통합 온톨로지(2018)

**IFC와의 핵심 차이점:**

| 측면 | ISO 15926 | IFC |
|------|-----------|-----|
| 주 도메인 | 프로세스 플랜트(석유화학) | 건물 및 건설 |
| 초점 | 배관, 계장, 프로세스 장비 | 건물 요소, 공간, 지오메트리 |
| 시간 모델링 | 네이티브 4D 접근법 | 제한적 시간 지원 |
| 수명 주기 | 수십 년 운영/유지보수 | 설계 및 시공 단계 |

ISO 15926은 P&ID(배관계장도), 프로세스 흐름도(PFD), 장비 태그, 제어 루프 등 IFC에서 다루지 않는 프로세스 관련 개념을 포함하며, DEXPI 프로젝트를 통해 IFC와의 통합 접근법이 개발되고 있다.

### BOT: 경량 건물 토폴로지 온톨로지

W3C Linked Building Data Community Group이 개발한 BOT(Building Topology Ontology)는 **7개 클래스**와 **14개 오브젝트 프로퍼티**만으로 건물의 핵심 토폴로지 개념을 표현하는 경량 온톨로지다. OWL 2 RL 프로파일을 채택하여 효율적인 규칙 기반 추론이 가능하다.

**핵심 클래스 구조:**
- `bot:Zone` (기본 클래스) → `bot:Site` → `bot:Building` → `bot:Storey` → `bot:Space`
- `bot:Element`: 기술적 기능을 가진 물리적 건설 객체
- `bot:Interface`: 존 또는 요소 간 경계/연결

**주요 관계 프로퍼티:**
- `bot:containsZone` (전이적): 존이 다른 존을 완전히 포함
- `bot:adjacentZone` (대칭적): 존들이 경계를 공유
- `bot:containsElement`: 요소가 존 범위 내 위치
- `bot:hasSubElement`: 요소가 하위 요소를 호스팅

Rasmussen 등(2021)의 *Semantic Web* 저널 논문에 따르면, BOT는 ifcOWL과 상호보완적으로 작동하여 ifcOWL 클래스들이 BOT 클래스의 하위클래스로 선언될 수 있다(예: `ifc:IfcWall rdfs:subClassOf bot:Element`).

### BEO: 건물 요소 온톨로지

Pieter Pauwels가 2018년 개발한 BEO(Built Element Ontology)는 IFC4_ADD2 스키마의 buildingElement 하위 트리에서 파생된 **약 360개 이상의 클래스**를 포함한다. bSDD(buildingSMART Data Dictionary) 서비스 API의 다국어 레이블로 강화되었다.

**주요 요소 범주:**

| 범주 | 설명 | 예시 하위클래스 |
|------|------|---------------|
| Beam | 수평 구조 부재 | Girder, Lintel, TBeam, HollowcoreBeam |
| Column | 수직 구조 부재 | Pilaster, StandColumn |
| Wall | 수직 공간 분리 요소 | SolidWall, RetainingWall, ShearWall |
| Slab | 수평 판 요소 | FloorSlab, RoofSlab, BaseSlab |
| Covering | 표면 마감 | Ceiling, Cladding, Insulation |

BEO는 별도의 **MEP 온톨로지**(https://pi.pauwel.be/voc/distributionelement#)와 쌍을 이루며, IFC4의 distributionElement 하위 트리를 커버한다. **한계점**으로는 지오메트리 표현 미포함(OMG/FOG 온톨로지 필요), 공간 관계 미포함(BOT 담당), 프로퍼티셋 미포함(OPM/PROPS 필요), 일정/비용 데이터 미지원이 있다.

### OPM: 프로퍼티 관리 온톨로지

Mads Holten Rasmussen 등이 LDAC 2018에서 발표한 OPM(Ontology for Property Management)은 **시간에 따른 프로퍼티 값 변화 추적**을 목적으로 한다. SEAS 온톨로지의 확장으로 개발되었으며, 설계 환경에서 다음을 다룬다:

1. 시간에 따라 변경되는 프로퍼티
2. 다양한 신뢰도를 가진 프로퍼티(가정값 vs 확정값)
3. 다른 프로퍼티에서 파생/계산된 프로퍼티

**핵심 클래스:**

| 클래스 | 용도 |
|--------|------|
| `opm:PropertyState` | 특정 시점의 프로퍼티 상태 평가 |
| `opm:CurrentPropertyState` | 가장 최근 정의된 상태 |
| `opm:OutdatedPropertyState` | 대체된 이전 상태 |
| `opm:Assumed` | 미확인 프로퍼티(낮은 신뢰도) |
| `opm:Confirmed` | 승인된 에이전트가 검증(높은 신뢰도) |
| `opm:Derived` | 다른 프로퍼티에서 추론된 프로퍼티 |

Rasmussen 등(2019)은 *Automation in Construction*에서 이 접근법을 "Managing interrelated project information in AEC Knowledge Graphs"로 확장 발표했다.

### 온톨로지 표준 종합 비교표

| 특성 | ifcOWL | ISO 15926 | BOT | BEO | OPM |
|------|--------|-----------|-----|-----|-----|
| **클래스 수** | 1,313 | ~200(Part2) + 10,000+(Part4) | 7 | ~360 | 9 |
| **복잡도** | 높음 | 높음 | 낮음 | 중간 | 낮음 |
| **일정 지원** | ✓ | ✓(활동 모델링) | ✗ | ✗ | ✗ |
| **비용 지원** | ✓ | ✓ | ✗ | ✗ | ✗ |
| **시간적 추적** | 제한적 | 네이티브 4D | ✗ | ✗ | ✓(핵심 목적) |
| **추론 프로파일** | OWL2 DL | OWL DL + FOL | OWL 2 RL | RDFS | OWL DL |

---

## 2부: 온톨로지가 BIM에서 해결하는 문제 유형

### A. 데이터 상호운용성: 158억 달러의 비효율성 해결

**NIST 연구 핵심 통계(2004):**
Gallaher 등이 수행한 NIST GCR 04-867 연구에 따르면, 미국 자본시설 산업에서 **부적절한 상호운용성으로 인한 연간 비용은 158억 달러**에 달한다:

- 건축가/엔지니어: **12억 달러**(연간 수입의 ~1%)
- 종합건설사: **18억 달러**
- 전문 제작/공급업체: **22억 달러**
- 발주자/운영자: **106억 달러**(가장 큰 부담, 연간 건설가치의 ~3%)

**이기종 소프트웨어 데이터 교환 문제:**
Revit, Tekla, Smart3D, Navisworks, AVEVA, Bentley 등 각 소프트웨어는 고유한 데이터 형식을 사용한다. IFC 변환 시 발생하는 문제:
- 지오메트리 왜곡 및 요소 정렬 불일치
- 파라메트릭 관계 손실
- 재료 속성 및 구조 하중 누락
- 프로퍼티셋 정보 절단

Lai와 Deng(2018)의 연구에 따르면 Revit → IFC → Revit 왕복 내보내기에서 측정 가능한 데이터 손실이 발생한다.

**시맨틱 웹 기술의 해결 방안:**

```sparql
# 크로스 도메인 센서-BIM 통합 쿼리 예시
PREFIX bot: <https://w3id.org/bot#>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
SELECT ?room ?temperature ?time
WHERE {
  ?room a bot:Space .
  ?sensor sosa:isHostedBy ?room .
  ?obs sosa:madeBySensor ?sensor .
  ?obs sosa:hasSimpleResult ?temperature .
  ?obs sosa:resultTime ?time .
}
```

시맨틱 접근법의 장점으로는 Open World Assumption(OWA)을 통한 유연하고 확장 가능한 데이터 통합, URI를 통한 크로스 시스템 글로벌 식별자 제공, 그래프 기반 구조의 자연스러운 관계 표현, 추론 기능을 통한 암시적 관계 채움이 있다.

### B. 시맨틱 쿼리 및 추론: 복잡한 조건 검색

**컴포넌트 선택 쿼리 예시:**

```sparql
# 3층의 직경 200mm 초과 모든 파이프 검색
PREFIX ifc: <http://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
PREFIX bot: <https://w3id.org/bot#>
SELECT ?pipe ?diameter
WHERE {
  ?storey bot:hasSpace ?space .
  ?storey rdfs:label "Floor 3" .
  ?space bot:containsElement ?pipe .
  ?pipe a ifc:IfcPipeSegment .
  ?pipe ifc:nominalDiameter ?diameter .
  FILTER (?diameter > 200)
}
```

**OWL 추론 기능:**

1. **자동 분류**: `ifc:isExternal true` 속성을 가진 벽이 자동으로 `ExternalWall`로 분류
2. **프로퍼티 상속**: `bot:Building`이 `bot:Zone`의 모든 프로퍼티 상속
3. **전이적 프로퍼티 추론**: Site containsZone Building, Building containsZone Storey → Site containsZone Storey (추론)

**SWRL 규칙 예시(Beach 등, 2015):**

```swrl
ifc:IfcBeam(?beam) ∧ ifc:length(?beam, ?len) ∧ swrlb:greaterThan(?len, 12.0) 
→ custom:requiresSpecialLifting(?beam, true)
```

Zhang, Beetz, de Vries(2018)가 *Semantic Web* 저널에 발표한 BimSPARQL은 RDF 건물 데이터 쿼리를 위한 도메인 특화 SPARQL 확장을 제공한다.

### C. 시간적 추적 및 상태 관리: 생애주기 모니터링

OPM 온톨로지를 활용한 **요소 생애주기 상태 모델링:**

```turtle
@prefix opm: <http://www.w3id.org/opm#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

:beam123_state1 a opm:PropertyState, opm:Confirmed ;
  opm:stateValue "designed" ;
  prov:generatedAtTime "2025-03-15"^^xsd:dateTime ;
  prov:wasAttributedTo :structuralEngineer .

:beam123_state2 a opm:CurrentPropertyState ;
  opm:stateValue "fabricated" ;
  prov:generatedAtTime "2025-06-20"^^xsd:dateTime ;
  opm:supersedes :beam123_state1 .
```

**일정 지연 연쇄 분석 쿼리:**

```sparql
PREFIX dicl: <https://w3id.org/digitalconstruction/0.5/Lifecycle#>
PREFIX time: <http://www.w3.org/2006/time#>
SELECT ?predecessorTask ?dependentTask ?cascadeDelay
WHERE {
  ?predecessorTask dicl:precedes ?dependentTask .
  ?predecessorTask dicl:hasDelay ?delay .
  FILTER (?delay > "P0D"^^xsd:duration)
  BIND(?delay AS ?cascadeDelay)
}
```

Boje, Kubicki, Guerriero(2021)는 ICCCBE 2020에서 시맨틱 웹을 위한 4D BIM 시스템 아키텍처를 발표했으며, 4DCollab 온톨로지가 IfcTask와 IfcEvent를 ModelObject와 연결하여 시간적 분석을 지원한다.

### D. 공간 분석 및 간섭 검토: 시맨틱 접근법

**전통적 도구(Navisworks, Solibri) vs 시맨틱 접근법:**

| 측면 | 전통적 접근 | 시맨틱 접근 |
|------|-----------|-----------|
| 간섭 유형 | 기하학적 교차(하드 클래시) | 기능적/워크플로우 충돌 포함 |
| 쿼리 범위 | "이 객체들이 같은 공간을 점유하는가?" | 유지보수 클리어런스, 안전 구역 고려 |
| 분석 통합 | 별도 분석 | 공간 데이터 + 일정 데이터 결합 |

**작업 구역 간섭 분석 쿼리:**

```sparql
PREFIX bot: <https://w3id.org/bot#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX task: <http://example.org/task#>
SELECT ?task1 ?task2 ?zone ?timeOverlap
WHERE {
  ?task1 task:occupiesZone ?zone .
  ?task2 task:occupiesZone ?zone .
  ?task1 time:hasBeginning ?start1 ; time:hasEnd ?end1 .
  ?task2 time:hasBeginning ?start2 ; time:hasEnd ?end2 .
  FILTER (?task1 != ?task2)
  FILTER (?start1 < ?end2 && ?start2 < ?end1)
}
```

---

## 3부: 플랜트/산업(EPC) 프로젝트 BIM 워크플로우 비효율성

### 1. 일정 관리 비효율성

**AS-IS 현행 프로세스:**
- 프로젝트 스케줄러가 Primavera P6 또는 MS Project에서 CPM 일정을 독립 파일로 작성
- BIM 모델러가 별도 애플리케이션(Revit, Navisworks, PDMS)에서 3D 모델 개발
- 일정 활동과 BIM 요소 연결에 Activity ID와 모델 컴포넌트의 **수동 매칭** 필요
- 자재 지연 발생 시 수동으로 일정 로직, 관련 작업 패키지 영향, 타 공종과의 공간 충돌 추적
- 간트 차트 해석 기반으로 Excel/종이로 일일 작업계획(DWP) 작성
- 3D 모델에서 일간/주간 작업 범위의 자동 시각화 불가

**핵심 문제점:**
- **상세도 불일치**: 일정 활동이 너무 많은 물리적 범위를 대표하여 부정확한 4D 애니메이션 초래
- **시간 소모적 연결**: 수천 개 모델 요소와 일정 활동의 수동 연관
- **정적 정보**: 일정 변경 시 4D 모델 전체 재연결 필요
- **빈약한 영향 분석**: 지연 영향 자동 전파를 위한 시맨틱 관계 부재

**TO-BE 시맨틱 기술 솔루션:**

1. **BIM 공유 온톨로지(BIMSO) 접근법**: BIM 요소, 일정 활동, 자원을 연결하는 통합 지식 그래프 생성
2. **자동 일정-BIM 연결**: 온톨로지가 IfcBuildingElement와 일정 Activity 클래스 간 관계 정의, 위치/시스템/작업패키지/재료 기반 자동 연관
3. **지연 영향 분석**: 시맨틱 추론이 일정 변경을 자동 전파, SPARQL 쿼리로 납기 변경 시 영향받는 모든 BIM 요소 식별
4. **동적 일일 시각화**: "오늘 해야 할 작업" 쿼리가 해당 활동의 BIM 요소 반환, 작업 상태 기반 자동 색상 코딩

BNBuilders는 VisiLean과 통합 4D BIM 구현 후 **6주 조기 완공**과 **92% PPC**(Percent Plan Complete)를 달성했다.

### 2. 시공성 검토 비효율성

**AS-IS 현행 프로세스:**
- 엔지니어가 2D 도면을 검토하고 현장 조건을 수동 해석
- 크레인 선정이 수동 양중 중량/반경 계산, 크레인 제조사 2D 하중 차트, 엔지니어 경험과 판단에 의존
- 양중 계획 개발: 2D 평면도에서 크레인 픽/셋 위치 결정, 도면에서 시각적으로 장애물 확인, 공간 검증 없이 양중 경로 계획

**핵심 문제점:**
- "현재 관행은 이동식 크레인 작업 계획에서 엔지니어의 경험에 의존하며, 이는 지루하고 오류가 발생하기 쉬운 프로세스"(EPPM2016 연구)
- 2D CAD 정보가 "실제 건설 과정과 상이"
- 크레인 이동 및 잠재적 충돌의 동적 시뮬레이션 부재

**TO-BE 시맨틱 기술 솔루션:**

1. **크레인 정보 모델(CIM)**: 용량 차트, 치수, 선회 반경을 가진 파라메트릭 크레인 모델
2. **온톨로지 지원 4D 양중 시뮬레이션**: 다중 크레인 양중 애니메이션, BIM 환경 내 동작 제어, 안전 모니터링 및 간섭 검출
3. **자동 시공성 분석**: 크레인 이동과 기존 구조물, 다중 동시 크레인 작업, 임시 시설과 영구 공사 간 공간 충돌 시맨틱 쿼리 식별

연구에 따르면 최적화된 디지털 트윈 계획 사용 시 **크레인 운영 비용 27% 절감**이 가능하다.

### 3. 자재/요소 추적 비효율성

**AS-IS 현행 프로세스:**
- 초기 MTO(Material Take-Off)를 3D 모델 완성 전 P&ID에서 수동 생성
- 2D 도면에서 피팅, 플랜지, 밸브 수동 카운팅
- 스풀 도면이 설계 모델과 별도로 작성
- 스풀 번호 및 히트 번호 수동 할당
- 제작 상태를 종이 기반으로 추적, 배송 추적은 선적 서류(종종 종이)로 수행
- 구매 주문이 BIM과 연결되지 않은 ERP 시스템(SAP, Oracle)에서 생성

**핵심 문제점:**
- "디지털 도구 없이 자재 추적은 물류적 악몽이 될 수 있음"
- 수동 MTO가 오류 발생 가능: "수동 추정은 오류가 발생하기 쉬움"
- 다중 분리 시스템: ERP, BIM, 제작 추적, 현장 설치

**TO-BE 통합 추적 솔루션:**

1. **통합 자재 온톨로지**: MTO 자재 코드를 BIM 요소 ID와 공유 온톨로지로 연결, 조달 부품 번호를 엔지니어링 태그 번호와 매핑
2. **지식 그래프 연결**: 설계 요소 ↔ MTO 항목 ↔ PO 라인 항목 ↔ 제작 스풀 ↔ 설치 컴포넌트
3. **자동 상태 통합**: 스풀 출하 시 → BIM 요소 "운송 중" 표시, 현장 도착 시 → "가용" 표시, 설치 완료 시 → "설치됨" 표시

BIM 기반 스풀링 구현 기업들은 생산성이 **일 60매에서 300매 이상**으로 증가했으며, 머신러닝과 BIM 데이터 사용 시 **납기 추정 오류 35% 감소**, 모델-절단기 통합으로 **자재 낭비 30-35% 감소**가 문서화되었다.

### 4. AWP(Advanced Work Packaging) 통합 비효율성

**AWP 핵심 개념:**
- **CWA(Construction Work Area)**: 다수 CWP를 포함하는 지리적 영역
- **CWP(Construction Work Package)**: 엔지니어링에서 나오는 인도물 지향 패키지
- **IWP(Installation Work Package)**: 현장 작업자를 위한 제약조건 해제된 실행 가능 작업 패키지

**CII RT-272 및 RT-319 연구 결과:**
- 최대 **25% 생산성 향상**
- 최대 **10%(4-10%) 총 설치비용(TIC) 절감**
- 일정 준수율 향상
- 건설 품질 증가
- 프로젝트 예측 가능성 강화
- 안전 성과 개선

RT-319는 20개 사례 연구와 25명의 전문가 인터뷰를 통해 AWP를 **CII Best Practice**로 검증했다(2015년 9월).

**AS-IS 현행 프로세스:**
- 작업 패키지가 스프레드시트 또는 독립 AWP 소프트웨어에서 정의
- BIM 모델 요소와 IWP의 수동 연관
- CWA/CWP 경계가 2D 도면에 수동으로 표시
- 작업 패키지 상태가 별도 데이터베이스에서 추적
- 진행 시각화에 수동 모델 조작 필요

**TO-BE 온톨로지 기반 AWP 통합:**

1. **AWP 온톨로지 개발**: CWA → contains → CWP → decomposed into → IWP → includes → BIM Elements 시맨틱 관계 정의
2. **BIM-AWP 통합**: BIM 모델에 AWP 특화 속성 저장(작업 패키지 할당, 제약 상태, 설치 순서), 범위, 기존 인프라, 계약 패키지 식별 색상 체계 사용
3. **자동 작업 패키지 시각화**: 모든 프로젝트 데이터의 단일 중앙집중식 클라우드 기반 데이터베이스 통합, 현장 작업자용 IWP "모델샷" 생성

O3 Solutions는 500개 이상 프로젝트, 20,000명 이상 사용자를 지원하는 엔드투엔드 AWP 플랫폼으로 **92% 고객 만족도**를 달성하고 있다.

---

## 결론: 시맨틱 기술이 열어가는 미래

본 연구는 ifcOWL, ISO 15926, BOT, BEO, OPM 등 핵심 온톨로지 표준이 **각기 다른 강점과 한계**를 가지며, 실제 프로젝트 적용 시 이들의 조합과 확장이 필요함을 보여준다. 특히 플랜트/산업 EPC 프로젝트에서는 ISO 15926의 프로세스 장비 모델링과 IFC/ifcOWL의 건물 구조 모델링을 통합하는 접근이 요구된다.

**핵심 발견:**

첫째, 현재 온톨로지 표준들은 **일정 및 비용 관리 영역에서 간극**이 존재한다. ifcOWL이 IfcWorkSchedule, IfcCostSchedule을 포함하나 실제 활용도는 낮으며, BOT/BEO/OPM은 이 영역을 다루지 않는다.

둘째, OPM의 **시간적 프로퍼티 상태 추적** 패턴은 설계-제작-설치 생애주기 추적의 기반을 제공하나, 건설 프로젝트 관리를 위한 워크플로우 온톨로지로의 확장이 필요하다.

셋째, CII 연구가 입증한 AWP의 **생산성 25% 향상, TIC 4-10% 절감** 효과는 시맨틱 기술 기반 통합 시 더욱 증폭될 잠재력을 가진다. 현재의 수동 CWA/CWP/IWP-BIM 연결을 온톨로지 기반 자동화로 대체할 경우 상당한 효율성 개선이 기대된다.

**향후 연구 방향:**

플랜트/산업 BIM의 완전한 시맨틱 통합을 위해서는 건설 도메인 온톨로지 네트워크(핵심 BIM, 일정, 자원, AWP 온톨로지), Linked Data 인프라(IFC/P6/조달 데이터의 RDF 변환, 크로스 도메인 쿼리용 SPARQL 엔드포인트), 디지털 트윈 아키텍처(현장의 실시간 상태 통합, 계획-실행 간 양방향 동기화)의 개발과 적용이 필요하다.

McKinsey(2017) 보고서가 지적한 건설 산업의 **연간 1% 생산성 성장률**(전체 경제 2.8%, 제조업 3.6% 대비)을 개선하기 위해, 시맨틱 웹 기술은 **158억 달러 상호운용성 비용**을 획기적으로 절감하고 **50-60% 생산성 향상** 잠재력을 실현하는 핵심 수단이 될 것이다.