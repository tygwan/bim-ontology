# Semantic BIM / Plant(EPC) IFC-to-RDF/OWL 파이프라인 총정리 (확장판)

본 문서는 `references/` 폴더의 4개 리포트를 **“요약”이 아니라 “마스터 리포트” 수준으로 재구성**한 총정리 문서다.  
목표는 **Plant/Industrial(EPC) 환경에서 IFC → RDF/OWL → SPARQL/추론(검증) → 현장 업무 자동화**로 이어지는 전체 그림을, 표준/프레임워크 비교부터 실행 아키텍처/데이터 모델/쿼리 예제/ROI 지표까지 한 번에 볼 수 있게 만드는 것이다.

- 작성 시점: 2026-02-03
- 유의: 본 문서는 4개 원본 리포트의 내용을 최대한 “전부 활용”해 재정리한다. (용어/수치/사례는 원문에 등장하는 범위에서만 사용)

## 0) 기준 문서(원본 리포트)

- `references/IFC_to_Semantic_Pipeline_Report_KR.md` (IEEE 스타일, 표준 비교 + 문제 유형 + EPC 비효율 + 권장 아키텍처)
- `references/semantic-bim-comprehensive-report-kr.md` (카테고리 A~D, SPARQL/SWRL 예제, AWP 온톨로지/쿼리, 기술 비교표, 한계/권장 접근)
- `references/compass_artifact_wf-f8bfc1ad-cc41-4a0e-8da5-155cd268b467_text_markdown.md` (정량 수치/사례, ifcOWL/BOT/BEO/OPM/ISO15926 수치 비교, 센서-BIM 연계, 4D/AWP 성과 지표)
- `references/BIM 시맨틱 파이프라인 구축 조사.md` (한국형 하이브리드 제언, ifcOWL(IfcWorkSchedule/IfcCostSchedule) 구조, 트리플 폭증, SHACL/SWRL 활용, AS-IS/TO-BE KPI 표)

## 1) 결론(Executive Summary) - “한 줄”이 아니라 “실행 가능한 결론”

### 1.1 핵심 결론(공통)

4개 문서가 반복적으로 강조하는 결론은 동일하다:

1. **단일 표준으로 끝내려 하지 말 것.**  
   ifcOWL/ISO15926/BOT/BEO/OPM은 각각 강점이 다르고, 특히 EPC에서 필요한 “업무 기능(일정/비용/자재/상태/AWP)”은 표준만으로 빈 구간이 존재한다.
2. **2층(또는 3층) 구조가 현실적이다.**
   - 정합성(Backbone): 원본 IFC를 최대한 보존(감사/근거/round-trip)
   - 업무(Lean): 현장 질의/대시보드/자동화를 위해 경량 모델로 재구조화(머터리얼라이즈 포함)
   - (선택) 서빙/인덱싱: 자주 쓰는 결과는 사전 계산해 제공
3. **“데이터 연결(링킹) + 검증(SHACL) + 규칙/추론(SWRL/Jena 등) + 외부 함수(기하/집계)”가 한 세트**로 굴러가야 현장에서 의미가 있다.

### 1.2 기대 효과(리포트들에서 반복 인용되는 KPI/효과)

아래 수치들은 원문 리포트에서 등장하는 대표적 기대효과/사례다.

- 상호운용성 비용: NIST GCR 04-867 기반으로 **연 $15.8B(158억 달러)** 문제(2002 기준, 2004 발간)와 비용 분해(발주자/운영자 비중이 가장 큼) 반복 인용
- AWP(Construction Industry Institute, RT-272/319): **생산성 25% 향상**, **TIC 4~10% 절감**, (문서에 따라) **일정 25% 단축** 효과 인용
- 자재/공급망: (보고서들에서) 추적 업무 **시간 80% 감소**, 자재 탐색 **70% 단축**, 재작업 **50% 감소** 등의 KPI/기대효과가 반복 제시
- 시공성/장비계획: (보고서들에서) 검토 시간 **1/3 단축**, 재작업/오류 **50% 감소**, 설계 오류 **90% 조기 탐지** 등
- 운영/상태 추적(OPM): (보고서에서) 쿼리 성능 개선 **6900ms → 640ms(약 10배)** 사례 인용
- 현장/플랫폼 사례(원문에 등장):
  - BNBuilders가 VisiLean과 통합 4D BIM 적용 후 **6주 조기 완공**, **92% PPC** 달성
  - 최적화된 디지털 트윈 기반 계획에서 **크레인 운영 비용 27% 절감** 가능
  - BIM 기반 스풀링 생산성 **일 60매 → 300매+** 증가, 납기 추정 오류 **35% 감소**, 자재 낭비 **30~35% 감소** 등 문서화 사례 언급

## 2) 배경(Why): EPC에서 “시맨틱 파이프라인”이 필요한 이유

### 2.1 EPC 데이터가 깨지는 구조(데이터 사일로)

EPC는 단계/조직/도구가 분리되어 데이터가 파편화되기 쉽다.

- Engineering: 3D 모델(BIM), P&ID/PFD, 상세 스펙, 규정/요건
- Procurement: ERP, PO, Vendor 데이터, 납기/검수
- Construction: P6/MSP, 4D 연계, 현장 작업지시, 검측, 안전/장비 계획
- O&M: 태그 기반 자산 관리, 유지보수 이력, 센서/운영 데이터

### 2.2 IFC만으로 부족한 지점(원문 리포트가 말하는 “핵심 한계”)

- IFC는 “스냅샷” 성격이 강해 **상태 변화/이력(설계 변경, 제작/배송/설치 상태, 검측 기록)**를 자연스럽게 담기 어렵다.
- P&ID(기능/태그), P6(공정), ERP(조달)와 **글로벌 식별자/관계 모델이 분절**되어 있어,
  “요소-태그-문서-작업-자재-상태”를 가로지르는 질의/자동화가 힘들다.

## 3) 표준/프레임워크(What): 각 표준을 어디에 써야 하는가

아래는 4개 문서의 내용을 합쳐, 표준/온톨로지를 “역할” 기준으로 정리한 것이다.

### 3.1 ifcOWL (buildingSMART) - IFC를 RDF/OWL로 “무손실(지향)” 변환하는 백본

#### 3.1.1 목적/성격

- IFC EXPRESS 스키마를 OWL로 **직역(Direct translation)**해 RDF 그래프화
- 강점: IFC 원본 재현/정합성(감사/근거, 표준 재사용, 장기적 상호운용성)

#### 3.1.2 규모/복잡도(원문 인용 수치)

- (보고서에서) IFC4 ADD1 기준 **1,313개 클래스**, **1,580개 오브젝트 프로퍼티**, **13,867개 논리 공리**를 포함한다고 언급
- 결과적으로 “Heavyweight” 온톨로지로 분류

#### 3.1.3 일정/비용 엔티티(IfcWorkSchedule/IfcTask/IfcCostSchedule)

원문 리포트들은 ifcOWL이 다음을 “스키마 차원”에서 제공하지만,
**현장 업무 자동화 수준으로 쓰려면 별도의 업무 레이어가 필요**하다고 강조한다.

- `IfcWorkSchedule`: 프로젝트의 작업 계획 컨테이너(프로젝트 연결, WBS 매핑)
- `IfcTask`: 개별 작업 단위(중첩/자원/상태/우선순위/시간)
- `IfcTaskTime`: ScheduledStart/ScheduledFinish/Duration 등 시간 속성
- `IfcCostSchedule`: 비용 집계/추적(IfcCostItem과 연계)
- 관계 예(원문 리포트 언급):
  - 프로젝트 선언/연결: `IfcRelDeclares`
  - 작업/비용이 Control로 관리/할당: `IfcRelAssignsToControl`, `IfcRelAssignsToProcess`, `IfcRelSequence` 등

#### 3.1.4 OWL 매핑 규칙(원문에 등장한 규칙 요약)

`semantic-bim-comprehensive-report-kr.md`에 제시된 매핑 규칙 예:

```text
- 규칙 속성 → 기능적 owl:ObjectProperty (cardinality 1)
- OPTIONAL 속성 → owl:maxQualifiedCardinality "1"
- SET/LIST 속성 → list:hasNext 온톨로지 + 카디널리티 제약
- 역(Inverse) 속성 → owl:inverseOf
- SUBTYPE OF → rdfs:subClassOf
- ABSTRACT SUPERTYPE OF (ONEOF) → owl:unionOf + owl:disjointWith
```

#### 3.1.5 한계(리포트들이 공통으로 지적)

- EXPRESS “직역” 때문에 그래프가 장황해지고 SPARQL 경로가 길어짐(Pset/Rel 탐색)
- LIST/SET, RULE/FUNCTION 등에서 복잡성이 증가하고, 일부는 OWL2DL로 자연스럽게 변환되지 않음
- Geometry를 포함할 경우 트리플이 급증(“IFC 대비 수십 배” 증가 가능성이 언급됨) → 쿼리 성능 저하
- 결론: **정합성 레이어로는 훌륭하지만, 업무 질의/추론은 경량 업무 레이어가 사실상 필수**

### 3.2 ISO 15926 / IDO - 플랜트 자산(태그/사양/문서/이력) 중심 생애주기 통합

#### 3.2.1 목적/범위

- 프로세스 플랜트(석유/가스/화학 등) 생애주기(설계~운영/정비) 데이터 통합 표준
- IFC가 다루지 않는 P&ID/태그/제어루프/장비 스펙/운영 이력을 포괄
- 리포트에서는 생애주기 범위를 FEED(기본 설계)부터 상세 엔지니어링, 조달, 시공, 운영/유지보수까지로 기술한다.
- (리포트 언급) 참조 데이터 라이브러리(STEPlib) 성격의 “표준화된 타입/클래스 집합”을 장점으로 든다.

#### 3.2.2 IFC와의 차이(리포트 공통 요지)

| 측면 | IFC | ISO 15926 |
|---|---|---|
| 주 대상 | 건축/시설 중심(형상+속성+관계) | 프로세스 플랜트 중심(태그/사양/문서/이력) |
| 시간 모델 | 제한적(스케줄 데이터 분리) | (리포트에서) 4D/시간 기반 접근을 “네이티브”로 설명 |
| 강점 | 3D/공간/요소 교환 | 수십 년 O&M 포함 생애주기 통합 |
| 통합 난점 | - | IFC와 “모델 철학”이 달라 매핑 전략이 필요 |

#### 3.2.3 주요 파트/동향(원문에 언급된 것)

- Part 2: 데이터 모델(EXPRESS)
- Part 4: OWL2 온톨로지(추론 관점)
- Part 7/8: 템플릿 방법론 및 OWL 구현(리포트 언급)
- Part 12: OWL 기반 생애주기 통합 온톨로지(리포트에서 2018 동향으로 언급)
- Part 13: 자산 계획(프로그램/프로젝트/일정/제약/자원/비용 등)
- Part 14: OWL 직접 의미론(Direct Semantics) + 생애주기 모델링 패턴(기능-물리 분리 등)

추가로, 리포트는 DEXPI 프로젝트 등에서 IFC와의 통합 접근이 논의된다고 언급한다.

#### 3.2.4 생애주기 모델링 패턴(원문 예시)

- Transformation: 상태 변화(설치됨 → 운영 중 등)
- Merge/Split: 자산 결합/분해 패턴

#### 3.2.5 EPC 관점 결론

Plant/EPC에서는 흔히:

- **IFC/ifcOWL = 3D/공간/요소**
- **ISO15926/IDO = 태그/사양/문서/이력(O&M 연속성)**

로 역할이 갈리고, 통합하려면 “명시적 매핑(태그↔요소↔문서↔작업)”이 필요하다.

### 3.3 BOT (W3C LBD CG) - 공간/위상 “경량 코어”

#### 3.3.1 성격/규모

- W3C LBD에서 만든 최소 크기 토폴로지 온톨로지(리포트에서 “7개 클래스/14개 오브젝트 프로퍼티” 언급)
- OWL 2 RL 프로파일 채택(규칙 기반 추론 효율 지향)

#### 3.3.2 핵심 개념(리포트들에서 공통으로 등장)

- 클래스: `bot:Site`, `bot:Building`, `bot:Storey`, `bot:Space`, `bot:Element`, `bot:Zone`, `bot:Interface` 등
- 관계:
  - `bot:containsZone`(전이적), `bot:adjacentZone`(대칭적)
  - `bot:containsElement`, `bot:hasSubElement` 등

#### 3.3.3 ifcOWL과의 결합 포인트

리포트에서 제시된 결합 예:

- `ifc:IfcWall rdfs:subClassOf bot:Element` 처럼 ifcOWL 객체를 BOT 상에 얹어,
  **공간 인덱싱/질의의 “짧은 경로”**를 제공

### 3.4 BEO (Built Element Ontology) - 요소 분류(분류체계) 축 제공

#### 3.4.1 범위/규모(리포트 간 차이 포함)

- 한 리포트에서는 IFC 기반 built element 분류를 **107개+ 클래스**로 설명
- 다른 리포트에서는 BEO가 **360개+ 클래스**를 포함한다고 설명

→ 결론: BEO는 “어떤 파생/범위(예: buildingElement vs 더 넓은 범주)”를 포함하느냐에 따라 규모가 달라질 수 있으며,  
실무에서는 “우리가 필요한 클래스 범위”를 명확히 정해 쓰는 것이 중요하다.

#### 3.4.2 예시 범주(리포트에 등장)

- Beam/Column/Wall/Slab/Covering 등
- 토목/인프라 요소(교대/옹벽/포장/레일 등) 언급
- MEP(배관/설비) 범주를 위해 별도 distribution element 계열 온톨로지와 쌍으로 쓰는 접근 언급

#### 3.4.3 한계(리포트 공통)

- 지오메트리/공간 관계/프로퍼티셋/일정/비용은 BEO 단독으로 해결 불가
- BOT/OPM/ifcOWL/외부 기하 온톨로지(또는 엔진) 결합 전제

### 3.5 OPM (Ontology for Property Management) - 상태/이력(시간) 추적의 표준 패턴

#### 3.5.1 핵심 개념(리포트 공통)

- 속성을 “정적 값”이 아니라 **상태(State) 객체**로 취급
- 대표 클래스:
  - `opm:Property`, `opm:PropertyState`
  - `opm:CurrentPropertyState`, `opm:OutdatedPropertyState`
  - `opm:Assumed`, `opm:Confirmed`, `opm:Derived/Calculation` 등(문서별 표기 차이는 있으나 의미는 유사)
- PROV-O와 결합해 “언제/누가/무슨 근거로” 값이 생성/갱신되었는지 기록

#### 3.5.2 상태 추적 예시(리포트에 등장한 시나리오)

- 밸브 V-101 설치 상태:
  - 2025-02-01: “입고 대기”(자재팀)
  - 2025-02-15: “현장 반입”(물류팀)
  - 2025-03-01: “설치 완료”(시공팀)

#### 3.5.3 Turtle 예제(원문에 등장한 패턴)

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

### 3.6 표준 종합 비교표(리포트들 내용 통합)

이 절은 4개 리포트의 비교표를 “한 화면에” 보이도록 합친 것이다.  
수치(클래스 수 등)는 문서/버전/스코프에 따라 달라질 수 있어, **출처 리포트에 따라 병기**한다.

#### 3.6.1 기능/업무 관점 비교(요약)

| 항목 | ifcOWL | ISO 15926/IDO | BOT | BEO | OPM |
|---|---|---|---|---|---|
| 핵심 목적 | IFC를 RDF/OWL로 직역(정합성) | 플랜트 생애주기 데이터 통합 | 공간/위상 최소 코어 | 요소 분류(taxonomy) | 시간에 따른 속성/상태/근거 |
| “요소” 표현 | IFC 엔티티 전반 | 자산/태그 중심 | Element(상세는 외부) | 분류 클래스 제공 | 요소는 외부 연계 |
| 공간/위상 | IFC 관계 기반(복잡) | 제한적/간접 | 강점(코어) | 별도(약함) | 없음 |
| 일정/작업 | 스키마상 지원(IfcTask 등) | Part 13 등에서 다룸(리포트 언급) | 직접 미지원 | 미지원 | 직접 스케줄 아님(상태로 보조) |
| 비용 | 스키마상 지원(IfcCostSchedule 등) | 다룸(리포트 언급) | 미지원 | 미지원 | 값 변화로 “추적” 가능(보조) |
| 상태/이력(시간) | 제한적(별도 패턴 필요) | 강점(생애주기 통합) | 미지원 | 미지원 | 강점(핵심 목적) |
| EPC 적합성 | 3D/요소 백본으로 강함 | 태그/사양/문서/O&M으로 강함 | 구역/공간 인덱싱 코어로 강함 | 요소 검색/필터 축 | 제작~설치~운영 상태 추적 축 |
| 대표 한계 | 트리플/쿼리 복잡, geometry 포함 시 폭증 | 학습/구현 난이도, IFC와 매핑 필요 | 위상 외 정보 부재 | 단독 불가(결합 전제) | 공간/워크플로우 부재(결합 전제) |

#### 3.6.2 규모/복잡도/추론 프로파일(리포트 기반)

| 특성 | ifcOWL | ISO 15926 | BOT | BEO | OPM |
|---|---:|---:|---:|---:|---:|
| 클래스 수(리포트 언급) | 1,313(예시) | ~200(Part2) + 10,000+(Part4) | 7 | 107+ 또는 360+ | 9(예시) |
| 복잡도 | 높음(Heavyweight) | 높음(Complex) | 낮음(Lightweight) | 낮음~중간 | 낮음~중간 |
| 추론 프로파일(리포트 언급) | OWL2 DL | OWL DL + (일부 FOL 언급) | OWL 2 RL | RDFS(또는 경량) | OWL DL |

## 4) 온톨로지가 해결하는 BIM 문제 유형(Problem Types A~D)

아래 A~D는 원문 리포트들이 공통으로 쓰는 “문제 분류”이며,
각 문제는 **AS-IS(현재) → TO-BE(시맨틱 적용)**로 서술된다.

### 4.1 A: Data Interoperability (이기종 SW 교환/IFC 변환 손실)

#### AS-IS

- 문제 규모(리포트 반복 인용): **연 $15.8B(158억 달러)**(2002 기준, 2004 발간)
- 비용 분포(리포트에 등장하는 수치/범위를 요약):
  - 건축가/엔지니어: 약 $1.2B
  - 종합 시공: 약 $1.3B~$1.8B(리포트에 따라 분류/수치 차이)
  - 전문 제작/공급: 약 $1.8B~$2.2B
  - 발주자/운영자: 약 $10.6B(가장 큰 비중)
- Revit/Tekla/Smart3D/Navisworks/PDMS/P6/ERP 등 도구별 데이터 모델 상이
- IFC 변환 시:
  - 지오메트리 왜곡/정렬 불일치
  - 파라메트릭 관계 손실
  - 재료/구조 하중/프로퍼티셋 누락 또는 절단
- 왕복 내보내기에서 손실이 발생한다는 연구 언급(리포트 인용)

#### TO-BE

- RDF/OWL을 “공통 언어(lingua franca)”로 사용해 데이터 소스를 링크드 데이터로 연결
- URI 기반 글로벌 식별자 + Open World Assumption을 활용한 확장 가능한 통합

#### 손실이 발생하는 메커니즘(한국형 리포트의 분해)

리포트에서는 상호운용성 비용이 아래 “업무 형태”로 나타난다고 정리한다.

1. 중복 입력(Redundant Entry): P&ID 데이터를 3D 모델링 툴에 재입력
2. 변환 오류(Translation Error): 포맷 변환 시 속성 누락/기하 깨짐
3. 검증 비용(Validation Cost): 불일치 확인/수정에 엔지니어 수작업 소요

#### 예시 SPARQL(리포트 예시)

```sparql
# (컨셉) 요소-태그-문서 연결 조회
SELECT ?elem ?tag ?doc WHERE {
  ?elem a beo:Pipe .
  ?elem ex:hasTag ?tag .
  ?elem ex:hasDocument ?doc .
}
```

센서/IoT까지 통합하는 예(리포트 예시):

```sparql
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

### 4.2 B: Semantic Querying & Reasoning (의미 기반 질의/추론)

#### AS-IS

- “암묵적 관계(실제로는 존재하지만 데이터에 명시되지 않은 관계)” 때문에 자동화가 막힘
- 복합 조건 검색/검증이 수작업으로 남음(설계 검토, 안전/규정 준수 등)

#### TO-BE

- OWL/규칙으로 암묵 관계를 명시화하고, SPARQL로 복합 조건 질의를 표준화
- 공간 함수(예: BimSPARQL)나 ASP(Answer Set Programming) 등과 결합해 고급 검증 수행

#### OWL/그래프 추론이 제공하는 “기본 효과”(리포트 예시)

리포트에 등장하는 전형적 추론/규칙 기능 예:

1. 자동 분류: `ifc:isExternal true`인 벽 → ExternalWall로 분류
2. 프로퍼티 상속: `bot:Building`이 `bot:Zone`의 프로퍼티를 상속
3. 전이적 관계 추론: Site containsZone Building, Building containsZone Storey → Site containsZone Storey

#### 예시: “3층, 직경 200mm 초과 파이프” (리포트 예시)

```sparql
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

#### 예시: SWRL 규칙(리포트 예시)

```swrl
ifc:IfcBeam(?beam) ∧ ifc:length(?beam, ?len) ∧ swrlb:greaterThan(?len, 12.0)
→ custom:requiresSpecialLifting(?beam, true)
```

또는 설치 선후행을 추론하는 개념 규칙(리포트 요지):

```text
IfcElement(?a) ∧ isLocatedAbove(?a, ?b) → mustBeInstalledBefore(?a, ?b)
```

### 4.3 C: Temporal Tracking & State Management (상태/진도/이력, As-planned vs As-built)

#### AS-IS

- 제작/출하/반입/설치/검측/인수 등 상태가 엑셀/메일/ERP/현장 앱으로 분산
- 지연 발생 시 영향 범위 파악이 늦고(수시간~수일), 근거/책임 추적이 어렵다

#### TO-BE

- OPM으로 상태를 이벤트 기반으로 갱신하며 이력을 유지
- ISO15926/IDO로 태그/사양/문서/이력을 연결
- 일정 데이터(P6/MSP)는 RDF로 변환/링크해 “작업 시작 가능 여부” 등을 자동 판단

#### As-planned vs As-built 비교 SPARQL(리포트 예시)

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

#### 일정 지연 연쇄 분석(리포트 예시)

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

#### 지연/클레임 분석 프레임(리포트에 등장하는 용어)

`semantic-bim-comprehensive-report-kr.md`는 지연 분석을 다음 방식으로 언급한다:

- As-Planned vs As-Built: 계획 대비 실적 비교
- Impacted As-Planned: 지연 이벤트의 영향 분석
- As-Built But-For: 책임 주체 지연 정량화(가정 기반)

### 4.4 D: Spatial Analysis & Clash Detection (공간 분석/간섭/장비 접근)

#### AS-IS

- Navisworks/Solibri 중심의 하드 클래시 + 회의/수기 판단(작업공간/장비/동선/안전)
- 2D 기반 장비 계획, 육안 검토 중심 → 검증 근거가 남기 어렵고 반복 비용이 큼

#### TO-BE

- “기하학” 자체는 외부 엔진이 계산하되, 결과를 RDF로 적재해 의미 규칙과 결합
- Soft clash(허용) vs Hard clash(금지), 유지보수 클리어런스, 안전 구역 등을 규칙화

#### 예시: 작업 구역 점유 + 시간 겹침(리포트 예시)

```sparql
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX task: <http://example.org/task#>
SELECT ?task1 ?task2 ?zone
WHERE {
  ?task1 task:occupiesZone ?zone .
  ?task2 task:occupiesZone ?zone .
  ?task1 time:hasBeginning ?start1 ; time:hasEnd ?end1 .
  ?task2 time:hasBeginning ?start2 ; time:hasEnd ?end2 .
  FILTER (?task1 != ?task2)
  FILTER (?start1 < ?end2 && ?start2 < ?end1)
}
```

#### 충돌(클래시) “분류” 관점(리포트 예시)

`semantic-bim-comprehensive-report-kr.md`는 충돌을 단순 기하 교차 외에도 분류할 수 있다고 정리한다:

- 물리적 충돌: 두 객체가 같은 공간을 점유
- 프로세스 기반 충돌: BIM 생성/관리 프로세스 결함에서 비롯
- 모델 기반 충돌: 메타모델/스키마 불일치에서 비롯

#### ASP(Answer Set Programming) 기반 안전/공간 검증(리포트 요지)

리포트는 4D BIM(시간+기하) 기반 안전 준수 자동 검증에서,
부동소수점/복잡 기하 때문에 비단조(Non-monotonic) 공간 추론이 유용하다고 설명한다.

#### BimSPARQL 함수 예시(리포트 예시)

리포트에 등장하는 공간 함수 예:

- `bim:intersects()` 교집합
- `bim:within()` 포함
- `bim:distance()` 거리
- `bim:nearestElement()` 근접 요소 검색
- `bim:accessibleFrom()` 접근성 검증

## 5) EPC 현장 비효율(AS-IS)과 TO-BE 모델(업무별 상세)

### 5.1 일정(4D) 통합 비효율

#### AS-IS(리포트 공통)

- P6/MSP는 독립 파일, BIM은 별도 툴에서 관리 → Activity ID ↔ BIM 요소 수동 매칭
- 일정 변경 시 4D 재연결, 영향 분석 수작업
- 일일 작업계획(DWP) 엑셀/종이 기반, “오늘 할 일” 3D 자동 시각화 어려움
- (리포트 상세) 일정 활동의 상세도(LOD)와 모델 요소의 상세도가 맞지 않아 4D 애니메이션이 부정확해지기 쉬움
- (리포트 상세) 수천 개 요소-활동 연결을 수동으로 수행 → 연결 비용/오류 증가
- (리포트 상세) 일정 변경이 발생하면 4D 모델 전체 재연결이 필요해 “정적 정보”로 전락
- (리포트 상세) 지연 영향(후속 작업, 작업구역 충돌, 패키지 영향)을 자동 전파할 관계/규칙이 부재

#### TO-BE(리포트 공통)

- P6 데이터를 RDF로 변환:
  - Activity → `IfcTask`
  - WBS → `IfcWorkSchedule`
  - 선후행 관계 → `IfcRelSequence`
- BIM 요소와 작업을 관계로 연결:
  - 요소(BEO/ifcOWL) ↔ 작업(IfcTask) ↔ 구역(BOT) ↔ 상태(OPM)
- 자재/상태 업데이트(OPM) → 작업 시작 가능 여부 판단 → 지연 전파/경고
- (리포트 상세) BIMSO(공유 온톨로지) 접근을 통해 요소/작업/자원을 하나의 지식 그래프로 묶고, 위치/시스템/패키지/자재 기반으로 “자동 연결”을 지향

#### “오늘 해야 할 작업” SPARQL(리포트 예시)

```sparql
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

#### 사례/효과(원문 등장)

- BNBuilders + VisiLean 통합 4D BIM: **6주 조기 완공**, **92% PPC**

### 5.2 시공성(Constructability) 검토 & 장비 계획 비효율

#### AS-IS(리포트 공통)

- 부지 조건(간격/개구부/층고 등) 도면 기반 수동 검증(주 단위 소요)
- 중장비/크레인 선정: 2D 도면 + 엑셀 계산 + 경험 의존
- 리프트 플랜: 육안 확인 → 간섭/안전 위험 누락 가능

#### TO-BE(리포트 공통)

- 장비 온톨로지(크레인):
  - 붐 길이/각도/정격 하중, 아우트리거 규격 등 지식화
  - 규칙 예: “인양물 중량이 정격 하중의 85% 초과 여부”를 SPARQL/SWRL로 체크
- 이동 경로/작업공간 점유를 4D 객체로 모델링하고, 시간대별 간섭을 자동 검사

#### 장비 접근 가능 구역 검증 SPARQL(리포트 예시)

```sparql
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX geo: <http://data.example.com/geometry#>
PREFIX const: <http://data.example.com/construction#>

SELECT ?equipment ?accessPath WHERE {
  ?equipment rdf:type ifc:IfcTransportElement ;
             geo:width ?width ;
             geo:height ?height .
  ?element const:hasAccessPath ?accessPath ;
           geo:minWidth ?minWidth ;
           geo:minHeight ?minHeight .
  FILTER (?width <= ?minWidth && ?height <= ?minHeight)
}
```

#### 효과/사례(원문 등장)

- 최적화된 디지털 트윈 계획 사용 시 **크레인 운영 비용 27% 절감** 가능(연구 기반 언급)

### 5.3 자재/요소 추적(공급망) 비효율

#### AS-IS(리포트 공통)

- 설계-조달-제작-운송-현장-설치 정보가 ERP/엑셀/송장/현장 기록으로 분산
- “스풀 A 도착했나?”를 확인하기 위해 전화/야적장 탐색 등 비효율
- 자재 코드 ↔ BIM 요소 ID 매핑 부재, 설치/검수 상태가 BIM에 반영되지 않음
- (리포트 상세) 초기 MTO를 3D 모델 완성 전 P&ID에서 수동 생성하는 경우가 있고, 2D 도면에서 피팅/플랜지/밸브를 수동 카운팅
- (리포트 상세) 스풀 도면이 설계 모델과 별도로 작성되거나, 스풀/히트 번호가 수동 할당됨
- (리포트 상세) 제작/배송 상태를 종이 기반으로 추적하거나, 배송 추적이 선적 서류 중심으로 수행됨
- (리포트 상세) PO가 BIM과 연결되지 않은 ERP(SAP/Oracle 등)에서 생성되는 구조가 흔함

#### TO-BE(리포트 공통)

- “설계 요소 ↔ MTO ↔ PO 라인 ↔ 제작 스풀 ↔ 설치 컴포넌트”를 지식 그래프로 연결
- RFID/QR 스캔 이벤트를 RDF 트리플로 변환해 OPM 상태 갱신
- BIM 뷰어에서 “시공 가능한(자재 입고 완료) 객체”를 필터/색상으로 가시화

#### 제조→배송→설치→운영 추적 SPARQL(리포트 예시)

```sparql
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

#### 효과/사례(원문 등장)

- 자재 탐색 시간 **70% 단축**, 추적 업무 **80% 감소**, 재작업 **50% 감소**(리포트 KPI/기대효과)
- BIM 기반 스풀링 생산성 **일 60매 → 300매+**, 납기 추정 오류 **35% 감소**, 자재 낭비 **30~35% 감소**(문서화 사례 언급)

### 5.4 AWP(Advanced Work Packaging) 통합 비효율

#### AWP 핵심 개념(리포트 공통)

- CWA(Construction Work Area): 지리적 구역
- CWP(Construction Work Package): 공종/구역 기반 작업 패키지
- IWP(Installation Work Package): 1~2주 단위 실행 가능한 현장 작업 패키지(제약 해제 상태 포함)
- (리포트에 따라) EWP(Engineering Work Package)와의 연계도 중요

#### AS-IS(리포트 공통)

- CWA/CWP/IWP가 엑셀/별도 AWP 도구에 고립
- BIM 요소/일정과 수동 연계 → 변경 시 동기화 실패/오류
- 제약 조건(도면 승인, 자재 입고, 비계, 선행 작업 완료 등) 누락으로 대기시간 발생
- (리포트 상세) CWA/CWP 경계가 2D 도면에 수동 표시되거나, 진행 시각화를 위해 모델을 수동 조작해야 하는 경우가 많음
- (리포트 상세) 작업 패키지 상태가 BIM/일정과 분리된 별도 DB에서 추적되어 “단일 소스”가 되기 어려움

#### TO-BE: AWP 온톨로지 모델(리포트 예시)

```text
CWA contains CWP
CWP decomposed into IWP
IWP includes BIM Elements
IWP linked to Task/Resource/Schedule/Status
IWP dependsOn other IWP (선후행)
Constraint(자재/승인/선행 등) 상태가 모두 Resolved일 때만 IWP Issued
```

#### “현장 관리자: 오늘의 작업 조회” SPARQL(리포트 예시)

```sparql
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
```

#### AWP 효과(원문 반복 인용)

- CII RT-272/319 기반:
  - **생산성 25% 향상**
  - **TIC 4~10% 절감**(문서에 따라 “10%” 표현도 등장)
  - **일정 25% 단축**(리포트에 포함)
- AWP 운영 자동화로 “80% 시간 단축” 등의 기대효과 제시
- O3 Solutions가 엔드투엔드 AWP 플랫폼으로 **92% 고객 만족도** 언급

### 5.5 AS-IS vs TO-BE KPI 표(한국형 리포트의 요약표)

`BIM 시맨틱 파이프라인 구축 조사.md`에서 제시된 형태를 유지해 재정리:

| 관리 항목 | AS-IS | TO-BE(온톨로지 기반) | 개선 효과(KPI) |
|---|---|---|---|
| 공정 관리 | P6↔BIM 수동 매핑, 정적 시뮬레이션 | ifcOWL + OPM 기반 실시간 4D 연동/추론 | 지연 리스크 30% 감소(제시 KPI) |
| 시공성 검토 | 2D/3D 육안, 수기 계산 | 장비 온톨로지 + SWRL 기반 규칙 검증 | 오류/재작업 50% 감소(제시 KPI) |
| 자재 관리 | 문서 분산, 수동 추적, 위치 불명 | IoT 연동 RDF 상태 관리, 실시간 가시화 | 탐색 시간 70% 단축(제시 KPI) |
| AWP 운영 | 엑셀 기반, 제약 누락 | AWP 온톨로지 기반 연계/제약 자동 체크 | Tool Time 25% 향상(제시 KPI) |

## 6) 권장 아키텍처(How): “하이브리드 시맨틱 파이프라인” 상세

### 6.1 레이어드 아키텍처(공통 결론을 구체화)

```text
[Source Layer]
  IFC / P&ID / P6 / ERP(PO,MTO) / IoT(스캔,센서) / 문서

[Backbone / Fidelity Layer]
  ifcOWL (가능한 한 원본 보존, 식별자/관계/근거)

[Lean Domain Layer]
  BOT (공간 인덱싱)
  BEO (요소 분류)
  OPM (상태/이력/근거)
  ISO15926/IDO (태그/사양/문서/운영 이력 - 범위 제한)
  Custom: Schedule/AWP/Material/Cost/Spatial rules

[Validation & Reasoning]
  SHACL (정합성/필수 링크/데이터 타입)
  Rules (SWRL/Jena/Datalog)
  External Functions (Geometry, 집계, 최적화) -> 결과를 RDF로 적재

[Serving]
  SPARQL Endpoint + 대시보드/현장앱(오늘작업/지연영향/자재상태/AWP진도/시공성체크)
```

### 6.2 ifcOWL “복잡한 경로”를 업무 레이어로 단축하는 이유(리포트 근거)

ifcOWL은 Pset/Rel을 따라가야 하는 경우가 많아 SPARQL이 길어지기 쉽다.  
한국형 리포트에는 “파이프 직경 조회 + BOT 층 조인” 예시가 포함되어 있다:

```sparql
PREFIX ifc: <http://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
PREFIX bot: <https://w3id.org/bot#>
PREFIX express: <https://w3id.org/express#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?pipe ?diameter ?storeyName
WHERE {
  ?pipe rdf:type ifc:IfcPipeSegment .

  ?relDefines ifc:relatedObjects_IfcRelDefinesByProperties ?pipe ;
              ifc:relatingPropertyDefinition_IfcRelDefinesByProperties ?pset .
  ?pset ifc:hasProperties_IfcPropertySet ?prop .

  ?prop ifc:name_IfcProperty ?propName .
  ?propName express:hasString "NominalDiameter" .

  ?prop ifc:nominalValue_IfcPropertySingleValue ?val .
  ?val express:hasDouble ?diameter .
  FILTER(?diameter >= 100.0) .

  ?storey rdf:type bot:Storey ;
          bot:hasElement ?pipe ;
          rdfs:label ?storeyName .
}
```

이런 경로를 “업무 레이어”로 평탄화/머터리얼라이즈하면, 현장 쿼리가 훨씬 단순해진다.

### 6.3 지오메트리/간섭 검증의 현실적 처리(리포트 공통)

- “전량 RDF화”는 트리플 폭증과 성능 문제를 유발하기 쉬움(특히 플랜트 대규모 모델)
- 권장 패턴:
  1) 기하 계산/충돌/거리/작업공간 검토는 외부 엔진(IfcOpenShell/전용 3D 엔진 등)에서 계산
  2) 결과만 RDF로 적재(예: `ex:violatesClearance`, `ex:hasHardClashWith`, `ex:accessibleFrom` 등)
  3) 의미 규칙(허용/금지, 작업구역/시간/안전)과 결합해 조치 자동화

## 7) 데이터 모델링 템플릿(“전부 연결”하기 위한 최소 모델)

이 절은 4개 리포트의 핵심 아이디어를 실제 모델링 관점으로 “합쳐” 정리한다.

### 7.1 공통 식별자 전략(필수)

- BIM 요소: IFC GUID(`IfcGloballyUniqueId`)를 코어 키로 유지
- 플랜트 태그: ISO15926/IDO 쪽 Tag ID와 명시 링크
- 일정: P6 Activity ID(또는 MSP UID) ↔ `IfcTask`/커스텀 Task
- 자재/조달: MTO/PO Line/Spool/Heat 등 추적 단위를 정하고 링크
- AWP: CWA/CWP/IWP 식별 체계를 조직 표준으로 고정

### 7.2 “상태”는 OPM으로(이벤트 기반)

리포트의 공통 메시지:

- 상태/진도/검측/인수는 “값 업데이트”가 아니라 “이력”이 중요
- 스캔/IoT/검측 이벤트가 들어올 때마다 `opm:PropertyState`를 생성/갱신

### 7.3 “업무 온톨로지”는 결국 필요(리포트 결론)

- BOT/BEO/OPM/ISO15926만으로 일정/자재/AWP/비용의 업무 로직을 완전히 커버하기 어렵다
- 그래서 리포트들은 다음을 제안한다:
  - 커스텀 Schedule Ontology(작업 의존성/제약/가용성)
  - 커스텀 Material/Supply Ontology(공급망 상태/리드타임)
  - AWP Ontology(패키지 계층 + constraint 상태 + 리소스)
  - Spatial Ontology/함수(클리어런스/접근성/작업공간)

## 8) 쿼리/룰 “레시피”(원문에 나온 예제를 실무용으로 묶기)

아래는 리포트에 실제로 등장한 예제들을 “쿼리북” 형태로 묶은 것이다.

### 8.1 상호운용성: 구조 요소 + 속성 필터(리포트 예시)

```sparql
PREFIX ifc: <http://www.buildingsmart-tech.org/ifcOWL/IFC4#>
PREFIX ifc_props: <http://data.example.com/properties#>

SELECT ?element ?fireRating ?material WHERE {
  ?element rdf:type ifc:IfcStructuralMember .
  ?element ifc_props:FireRating ?fireRating .
  ?element ifc_props:Material ?material .
  FILTER (?fireRating > "REI 120"^^xsd:string)
}
```

### 8.2 OPM 이력 조회(리포트 예시)

```sparql
SELECT ?t ?state WHERE {
  ?ps a opm:PropertyState ;
      opm:propertyOf ex:Elem_123 ;
      opm:hasValue ?state ;
      prov:generatedAtTime ?t .
}
ORDER BY ?t
```

### 8.3 AWP 지연 영향(리포트 예시)

```sparql
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

## 9) 한계/리스크 및 “권장 접근법”(원문 결론 통합)

### 9.1 현재 한계(리포트 공통)

- ifcOWL: 복잡도/학습 곡선/실무 도구 부족 + 트리플/쿼리 성능 이슈
- ISO15926: 도메인(프로세스 산업) 편중, 건설 쪽 채택/툴링 이슈
- BOT/BEO: 경량이지만 단독으로는 업무 정보 부족
- OPM: 상태 이력에는 강하지만 공간/워크플로우는 외부 결합 필요
- 전반: 실시간 동기화/왕복(round-trip)/운영 자동화는 아직 성숙도가 고르지 않음

### 9.2 권장 접근(리포트 공통)

- 모듈형 조합 + 점진 도입
- SHACL로 “정합성/품질”을 먼저 확보하고, 룰은 좁고 명확하게(룰 라이브러리화)
- Geometry는 외부 함수/엔진 중심으로 처리하고 결과를 RDF로 환류
- PoC는 “오늘 작업/지연 영향/자재 상태/AWP 제약” 같이 현장 가치가 큰 작은 범위부터

## 10) 참고문헌/온라인 리소스(원문 리포트에 등장한 핵심 링크)

이 절은 4개 리포트에 등장하는 참고문헌/링크를 “그대로” 최대한 보존해 모아둔 것이다.
중복 항목이 있을 수 있다.

### 10.1 참고문헌(IEEE 스타일) - `IFC_to_Semantic_Pipeline_Report_KR.md` 발췌

[1] buildingSMART, “ifcOWL (IFC EXPRESS to OWL) – Technical resources,” buildingSMART Technical.  
[2] buildingSMART, “ifcOWL ontology documentation (direct translation),” LDWG document (PDF).  
[3] buildingSMART, “IFC4 OWL (ifcOWL) resources,” IFC4 OWL index.  
[4] W3C Linked Building Data Community Group, “BOT: Building Topology Ontology specification.”  
[5] M. H. Rasmussen et al., “BOT: the Building Topology Ontology of the W3C Linked Building Data group,” Semantic Web Journal, 2021.  
[6] C. Ramonell, “BEO: Built Element Ontology documentation.”  
[7] W3C LBD CG, “OPM: Ontology for Property Management specification.”  
[8] M. H. Rasmussen et al., “OPM: An ontology for describing properties that evolve over time,” LDAC Workshop, 2018.  
[9] POSC Caesar Association, “Industrial Data Ontology (IDO) – (related to ISO 15926-14),” 2023.  
[10] NIST, “Cost Analysis of Inadequate Interoperability in the U.S. Capital Facilities Industry (NIST GCR 04-867),” 2004.  
[11] L. Jiang et al., “Multi-ontology fusion and rule development to facilitate automated code compliance checking using BIM and rule-based reasoning,” Advanced Engineering Informatics, 2022.  
[12] A. Lorvao Antunes et al., “(BIM-AMS linked data exchange / CoDEC related),” 2024.  

### 10.2 온라인 리소스 링크(사양/문서) - `IFC_to_Semantic_Pipeline_Report_KR.md` 발췌

- ifcOWL(overview): https://technical.buildingsmart.org/standards/ifc/ifc-formats/ifcowl/
- IFC4 OWL index: https://standards.buildingsmart.org/IFC/DEV/IFC4/FINAL/OWL/index.html
- BOT spec: https://w3c-lbd-cg.github.io/bot/
- OPM spec: https://w3c-lbd-cg.github.io/opm/
- BEO docs: https://cramonell.github.io/beo/actual/index-en.html
- IDO (PCA RDS): https://rds.posccaesar.org/WD_IDO.pdf
- NIST GCR 04-867: https://nvlpubs.nist.gov/nistpubs/gcr/2004/nist.gcr.04-867.pdf

### 10.3 참고 자료(추가 링크 모음) - `BIM 시맨틱 파이프라인 구축 조사.md` 발췌

1. BFO-based ontology enhancement to promote interoperability in ..., https://www.researchgate.net/publication/355763676_BFO-based_ontology_enhancement_to_promote_interoperability_in_BIM  
2. BOT: The building topology ontology of the W3C linked building data ..., https://orbit.dtu.dk/en/publications/bot-the-building-topology-ontology-of-the-w3c-linked-building-dat/  
3. ISO 15926 - Knowledge and References (Taylor & Francis), https://taylorandfrancis.com/knowledge/Engineering_and_technology/Computer_science/ISO_15926/  
4. AEC Software Market Size, Share, Trends, 2031 Report (Mordor Intelligence), https://www.mordorintelligence.com/industry-reports/aec-software-market  
5. Ontology-Based Representation and Reasoning in Building Construction Cost Estimation in China (MDPI), https://www.mdpi.com/1999-5903/8/3/39  
6. An Improved Approach for Effective Describing Geometric Data in ifcOWL through WKT High Order Expressions (SciTePress), https://www.scitepress.org/Papers/2021/105323/105323.pdf  
7. Validating Advanced Work Packaging as a Best Practice: A Game ... (CII), https://www.construction-institute.org/validating-advanced-work-packaging-as-a-best-practice-a-game-changer  
8. Bridging the gap between Information Management and Advanced ... (ITC), https://itc.scix.net/pdfs/w78-2021-paper-086.pdf  
9. IFC 4.3.2 IfcWorkSchedule docs, https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWorkSchedule.htm  
10. IFC 4.3.2 IfcCostSchedule docs, https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCostSchedule.htm  
11. IFC4.3 IfcWorkSchedule (bim-times mirror), http://www.bim-times.com/ifc/IFC4_3/buildingsmart/IfcWorkSchedule.htm  
12. buildingSMART Forum: IfcCostSchedule related to IfcProject?, https://forums.buildingsmart.org/t/how-is-ifccostschedule-related-back-to-ifcproject/3503  
13. Enhancing the ifcOWL ontology with an alternative representation for geometric data (CNR-IRIS), https://iris.cnr.it/retrieve/63503f6b-5082-4aa5-b649-2788a926b70b/Enhancing%20the%20ifcOWL%20ontology%20with%20an%20alternative%20representation%20for%20geometric%20data_preprint.pdf  
14. INTEROPERABILITY IN AECO AND THE OIL ... (ITcon), https://www.itcon.org/papers/2022_16-ITcon-Doe.pdf  
15. ISO 15926-14:2020(E) (READI), https://readi-jip.org/wp-content/uploads/2020/10/ISO_15926-14_2020-09-READI-Deliverable.pdf  
16. BOT publication (TU/e research portal), https://research.tue.nl/en/publications/bot-the-building-topology-ontology-of-the-w3c-linked-building-dat/  
17. BOT paper (ResearchGate), https://www.researchgate.net/publication/342802332_BOT_the_Building_Topology_Ontology_of_the_W3C_Linked_Building_Data_Group  
18. Built Element Ontology docs, https://cramonell.github.io/beo/actual/index-en.html  
19. Building Element Ontology (pi.pauwel.be), https://pi.pauwel.be/voc/buildingelement/  
20. OPM paper (DTU), https://orbit.dtu.dk/en/publications/opm-an-ontology-for-describing-properties-that-evolve-over-time/  
21. Semantic Web Technologies for Indoor Environmental Quality (MDPI), https://www.mdpi.com/2075-5309/12/10/1522  
22. BOT paper (SemanticScholar), https://www.semanticscholar.org/paper/BOT%3A-The-building-topology-ontology-of-the-W3C-data-Rasmussen-Lefran%C3%A7ois/789d0b45f15e364885043fab0a26eef726bd076e  
23. Automatic Scan-to-BIM (MDPI), https://www.mdpi.com/2075-5309/15/7/1126  
24. Bim Consulting Service Market ... (DataHorizzon), https://datahorizzonresearch.com/bim-consulting-service-market-47163  
25. BIM-Based Dynamic Construction Safety Rule Checking ... (MDPI), https://www.mdpi.com/2075-5309/12/5/564  
26. ETSI GR CIM 051 V1.1.1 (2025-02), https://www.etsi.org/deliver/etsi_gr/CIM/001_099/051/01.01.01_60/gr_cim051v010101p.pdf  
27. Automatic SPARQL Generation for BIM Data Extraction (ResearchGate), https://www.researchgate.net/publication/347526754_An_Approach_of_Automatic_SPARQL_Generation_for_BIM_Data_Extraction  
28. Semantic Parsing in Natural Language-based BIM Retrieval (HKU), https://hub.hku.hk/bitstream/10722/356570/1/FullText.pdf  
29. BIM Clash Report Analysis Using ML Algorithms (University of Alberta), https://ualberta.scholaris.ca/bitstreams/10122376-1710-40a5-9a20-a03690181785/download  
30. Automated tower crane planning ... (ResearchGate), https://www.researchgate.net/publication/327371710_Automated_tower_crane_planning_leveraging_4-dimensional_BIM_and_rule-based_checking  
31. Integrating Crane Information Models ... (IAARC), https://www.iaarc.org/publications/fulltext/ISARC2016-Paper192.pdf  
32. Integrating Crane Information Models ... (ResearchGate), https://www.researchgate.net/publication/320167757_Integrating_Crane_Information_Models_in_BIM_for_Checking_the_Compliance_of_Lifting_Plan_Requirements  
33. Transforming the Industry: AWP as a Standard (CII), https://www.construction-institute.org/transforming-the-industry-advanced-work-packaging-as-a-standard-best-practice  
34. Can Advanced Work Packaging Become a Lean Method? (ResearchGate), https://www.researchgate.net/publication/372300505_Can_Advanced_Work_Packaging_Become_a_Lean_Method  
35. Towards a Generalized Value Stream Mapping and Domain Ontology ... (University of Alberta), https://ualberta.scholaris.ca/bitstreams/46c33bb9-a25a-4daf-a4d5-64064db18210/download  
