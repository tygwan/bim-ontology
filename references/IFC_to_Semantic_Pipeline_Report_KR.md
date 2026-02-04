# AEC/플랜트 산업 온톨로지 표준 비교 및 Semantic BIM 적용 보고서 (IEEE 스타일)

> 목적: **Plant/Industrial BIM**에서 **IFC → RDF/OWL → SPARQL/추론** 파이프라인을 구축하기 위해, AEC/플랜트 분야에서 사용되는 주요 온톨로지 표준/프레임워크( ifcOWL, ISO 15926/IDO, BOT, BEO, OPM )를 비교하고, Semantic BIM이 해결하는 문제 유형 및 EPC 현장의 비효율 프로세스를 **AS-IS / TO-BE** 관점으로 정리한다.  
> 범위: 요청사항 **1-1 ~ 1-3**을 “보고서 형식”으로 정리. (언급된 업로드 논문 2편 포함)

---

## 1-1. 표준 및 프레임워크 개요

### 1-1-1. 비교 요약표 (스케줄/비용/상태 모델링 관점)

| 구분 | 주 목적(스코프) | “BIM 요소” 표현 | “공간/위상” | “속성/변경이력(시간)” | “일정/작업” | “비용” | Plant/EPC 적합성 | 강점 | 한계 |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| **ifcOWL (buildingSMART)** | IFC(주로 IFC4) EXPRESS를 OWL/RDF로 직역해 Linked Data화 | ◎ | ○ | △(별도 패턴 필요) | **○**(IfcWorkSchedule/IfcTask) | **○**(IfcCostSchedule) | Building/EPC 전반(Plant는 IFC 범위 밖 존재) | IFC 정합성, 표준/재사용 | 그래프 장황 → 질의/룰 복잡 |
| **ISO 15926 / IDO** | 프로세스 플랜트 라이프사이클 데이터 의미 통합(설계~운영) | ○(자산/태그 중심) | △ | **◎** | △(직접 스케줄 스키마라기보다 상태/이력 강점) | △ | **Oil&Gas/EPC 강점** | 태그/사양/문서/이력 통합 | IFC와 모델 철학 상이 → 매핑 비용 |
| **BOT (W3C LBD CG)** | 건물/시설의 최소 위상(Topology) 코어 | △(상세는 외부 연계) | **◎** | △ | × | × | 공간/구역 인덱싱에 매우 유용 | 단순/웹 친화/조합 쉬움 | 제품/공정은 BOT 단독 불충분 |
| **BEO (Built Element Ontology)** | IFC4 기반 “Built Element” 분류(taxonomy) | **○~◎** | △ | △ | × | × | 건축/구조/요소 분류 축에 유용 | 요소 분류/검색 강점 | 일정/비용/상태는 외부 결합 필요 |
| **OPM (Ontology for Property Mgmt)** | 시간에 따라 변하는 속성값·상태·근거(provenance) 표현 | △(요소는 외부) | × | **◎** | △(상태 변화 추적) | △(비용 ‘값’ 변화로 표현 가능) | as-built/검측/상태관리 축에 유용 | 이력/근거/변경추적 표준화 | 공정모델(P6)을 대체하진 않음 |

**표준/사양**: ifcOWL( buildingSMART ), BOT/OPM( W3C LBD CG ), BEO(community), ISO 15926/IDO(PCA RDS).

---

### 1-1-2. ifcOWL (buildingSMART)

#### (1) 스코프
- IFC EXPRESS 스키마를 **OWL로 직접 변환(Direct translation)**하여 RDF/OWL 기반 질의·연계를 가능하게 하는 표준 접근.
- 장점: **원본 IFC와의 정합성(1:1)**, 표준 용어/스키마 재사용, 장기적 상호운용성.

#### (2) IFC4 “스케줄/작업/비용” 엔티티의 OWL 매핑 관점
- ifcOWL은 “직역”이므로 IFC4에 존재하는 작업/일정/비용 엔티티(예: `IfcWorkSchedule`, `IfcTask`, `IfcCostSchedule`)는 **그대로 OWL 클래스/프로퍼티로 노출**되는 것이 핵심.
- 다만 실제 프로젝트에서 “업무 질의/추론”을 위해서는 다음 중 하나가 필요:
  - (A) **원본 ifcOWL을 보존**(정합성 레이어) +  
  - (B) **업무 친화적 재구조화(경량 뷰, materialized triples)** 레이어를 별도로 구축(BOT/BEO/OPM 등 결합)

> 업로드 논문(규정검토/추론 시스템)은 ifcOWL 그래프가 장황하여 **ifcOWL 구조 재조직 + 설계 모델 온톨로지(Designed model ontology) + 룰 기반 추론**을 통해 매핑과 성능을 개선함을 보여준다. (Jiang et al., 2022)

#### (3) 주요 한계
- ifcOWL은 표현력이 크지만, **질의 경로가 길고 복잡**(Pset/Rel 탐색)하여 SPARQL이 장황해지기 쉬움.
- 일정/비용/상태를 모두 얹으면 온톨로지 운영 난이도가 급격히 증가 → 실무에서는 “정합성 레이어 + 업무 레이어” 2층 구조를 추천.

---

### 1-1-3. ISO 15926 / IDO (Industrial Data Ontology)

#### (1) 스코프
- Oil & Gas/EPC에서 프로세스 플랜트 자산의 라이프사이클 데이터(태그, 사양, 문서, 변경이력 등)를 **의미적으로 통합**하기 위한 표준군/온톨로지 접근.
- 최근에는 ISO TR 15926-14 계열을 기반으로 **Industrial Data Ontology(IDO)**로 정리·확장되는 흐름이 존재.

#### (2) IFC와의 관계/차이
- **IFC**: 시설/건축 중심의 객체 모델(형상+속성+관계)로 교환/협업에 강점.
- **ISO15926/IDO**: 플랜트 자산/태그/사양/문서/운영 이력 통합에 강점.
- 결론적으로 Plant/EPC에서는 **IFC(3D/공간/요소)**와 **ISO15926(태그/사양/문서/이력)**가 서로 다른 강점을 가지며, 통합하려면 명시적 매핑 전략이 필요.

#### (3) 일정/비용/상태 모델링
- “일정 스키마” 자체를 제공한다기보다 **상태/변경/이력(temporal identity) 기반 표현**이 강점.
- EPC 현장에선 P6/MSP 같은 스케줄을 그대로 대체하기보단, **작업패키지·자재·검측 상태를 시간축으로 정합**하는 방식이 현실적.

---

### 1-1-4. BOT (Building Topology Ontology, W3C LBD CG)

#### (1) 스코프
- 건물/시설의 위상(Topology)을 표현하는 **최소 코어 온톨로지**.
- 다양한 도메인 온톨로지(제품/센서/운영/공정)와 조합하기 쉬운 “얇은 코어”가 설계 철학.

#### (2) 주요 클래스/관계(대표)
- `bot:Site`, `bot:Building`, `bot:Storey`, `bot:Space`, `bot:Element`
- 공간 포함관계(containsElement 등), 인접/연결 관계(사양 참조)

#### (3) 일정/비용/상태 지원성
- BOT 단독으로 일정/비용을 표현하지 않음.
- 하지만 Plant/EPC에서 **Work Area/Zone/Unit/Level** 기반 인덱싱 코어로 매우 유용:
  - 요소 분류(BEO/ifcOWL), 상태·이력(OPM), 일정(IfcTask 또는 P6 매핑)을 BOT 공간 구조에 걸어 표현.

---

### 1-1-5. BEO (Built Element Ontology)

#### (1) 스코프
- IFC4의 built element 분류(벽/기둥/슬래브/문 등) 기반 “요소 taxonomy” 제공.
- 실무에선 BOT(공간 위상) + BEO(요소 분류) 조합이 흔함.

#### (2) 일정/비용/상태
- BEO 자체는 요소 분류에 집중 → 일정/비용/상태는 외부 온톨로지(Ifctask/P6, OPM 등)와 결합 필요.

---

### 1-1-6. OPM (Ontology for Property Management)

#### (1) 스코프
- **시간에 따라 변하는 속성값**을 일관된 모델로 표현(설계 변경, 시공 상태 변경, 운영/정비 기록 등).
- PROV-O(근거/출처)와 결합해 “누가/언제/어떤 근거로 값이 바뀌었는지”까지 표현 가능.

#### (2) 일정/비용/상태 모델링
- 스케줄 엔티티를 직접 제공하지는 않지만,
  - 설치/검측/인수 등 **상태 변화**
  - 추정비/실적비 등 **값 변화**
  를 “시간을 갖는 속성”으로 체계적으로 관리하는 데 적합.

---

## 1-2. Ontology가 해결하는 BIM 문제 유형 (Semantic BIM)

> 배경(산업 비용): NIST는 미국 capital facilities 산업에서 **상호운용성 결함으로 인한 연간 158억 달러 비용**을 추정(2002년 기준, 보고서 2004 발간). 이후에도 유사한 문제의 구조적 비용이 반복적으로 인용됨.

아래 4개 범주(A~D)로 정리.

---

### A. Data Interoperability (이기종 SW 교환/IFC 변환 손실)

#### (1) AS-IS(전통)
- Revit/Tekla/Smart3D/Navisworks/P6 등 도구별 데이터 모델 차이 → IFC 변환 시 손실/의미 왜곡.
- “중간 엑셀/수기 매핑”과 반복 검증에 시간이 소모.

#### (2) TO-BE(온톨로지)
- IFC/Plant 데이터를 RDF로 통합하고, BOT로 공간 인덱싱, BEO로 요소 분류, ISO15926로 태그/사양/문서 정합을 제공.
- 업로드 논문(2024)은 BIM-AMS(Asset Mgmt System) 연계에서도 온톨로지를 “공유 개념화”로 활용해 상호운용성을 개선하는 방향을 제시.

#### (3) 예시 SPARQL(컨셉)
```sparql
SELECT ?elem ?tag ?doc WHERE {
  ?elem a beo:Pipe .
  ?elem ex:hasTag ?tag .
  ?elem ex:hasDocument ?doc .
}
```

#### (4) 전통 대비
- 전통: 포맷 변환 + 수기 매핑
- 온톨로지: 의미 레이어(공유 개념) + 표준 질의(SPARQL)로 반복 작업 감소

---

### B. Semantic Querying & Reasoning (의미 기반 질의/추론)

#### (1) 실무 예(Plant/EPC)
- “3층/Unit-300 배관 중 직경>200mm + 특정 LineClass + 검사상태 OK”
- “A가 B 위에 있으면 B 선행 설치 필요(선후행 추론)”

#### (2) TO-BE
- BOT로 “층/구역/공간”을 표준화하고, 요소는 BEO/ifcOWL로 연결.
- 룰은 SWRL/Jena/SHACL로 표현(복잡 로직은 외부함수 연계 포함).
- 업로드 논문(2022)은 OWL만으로 부족한 로직을 Jena rule + SPARQL + 외부함수로 해결.

#### (3) 예시 룰(개념)
- `ex:isAbove(A,B) -> ex:mustPrecede(B,A)`

---

### C. Temporal Tracking & State Management (상태/진도/이력, as-planned vs as-built)

#### (1) 실무 예
- 제작→출하→반입→설치→검측→인수 상태가 시스템/엑셀에 분산.
- 지연 발생 시 영향 범위(scope) 파악이 어려움.

#### (2) TO-BE
- OPM으로 상태/속성 변화를 이력화 + PROV로 근거 연결.
- ISO15926/IDO는 플랜트 자산/태그/문서/이력 통합에 강점.
- 일정(P6/IfcTask)은 원천을 유지하고 온톨로지에서 링크·추론.

#### (3) 예시 SPARQL(이력 조회)
```sparql
SELECT ?t ?state WHERE {
  ?ps a opm:PropertyState ;
      opm:propertyOf ex:Elem_123 ;
      opm:hasValue ?state ;
      prov:generatedAtTime ?t .
}
ORDER BY ?t
```

---

### D. Spatial Analysis & Clash Detection (작업공간/장비 접근/양중 간섭)

#### (1) AS-IS
- Navisworks clash 중심 + 작업구역/동선/장비 제약은 회의·수기 판단.

#### (2) TO-BE
- BOT로 작업구역/공간 구조를 표준화하고,
- geometry 분석(IfcOpenShell/3D엔진)은 계산 결과만 RDF로 피드백(위반/통과 트리플 생성).
- “의미 제약 + 수치 결과”를 결합해 사전 위험 탐지 자동화.

---

## 1-3. Plant/EPC에서 BIM 기반 관리의 주요 비효율 (AS-IS / TO-BE)

### 1) Schedule 관리 비효율

#### AS-IS
- 자재 지연 → 영향 범위 파악을 위해 자재코드-요소-액티비티-후속공정 수기 추적.
- Daily Work Plan(DWP) 수기 작성, “3D에서 오늘 할 일”이 직접 보이지 않음.

#### TO-BE(온톨로지)
- (요소 GUID) ↔ (일정 Activity/IfcTask) ↔ (자재/조달 상태) ↔ (작업구역 BOT) ↔ (검측/상태 OPM)을 연결.
- “오늘 가능한 작업”을 SPARQL로 자동 산출(선행완료, 자재 Ready, 접근 가능 등 조건).

---

### 2) Constructability Review 비효율

#### AS-IS
- 장비 접근/개구부/층고/컬럼 간격 등 2D+회의 중심.
- 양중계획 간섭은 사후 검토 경향.

#### TO-BE
- BOT 구역 + 요구조건(폭/높이/회전반경) 룰/제약 모델링.
- geometry 계산은 외부 엔진에서 수행 후 RDF로 결과(제약 위반)만 반영.
- 업로드 논문(2022)처럼, 복잡 로직은 OWL + 룰(Jena) + 외부함수 결합이 현실적.

---

### 3) Material/Element Tracking 비효율

#### AS-IS
- 제작·출하·반입·설치 상태가 분산, 자재코드↔BIM ID 매핑 부재.
- procurement 상태가 BIM에 반영되지 않아 “현장 가능 작업” 판단이 어려움.

#### TO-BE
- ISO15926/IDO로 태그/사양/문서/자산 정합.
- 요소 GUID와 자재/태그를 RDF로 1회 정합 후 지속 운영.
- OPM으로 상태 이력화 + provenance(누가/언제/근거) 연결.

---

### 4) AWP(Advanced Work Packaging) 통합 비효율

#### AS-IS
- CWA/CWP/IWP 구조와 BIM 연결이 수작업.
- 패키지 진도/병목이 3D에서 직관적으로 안 보임.

#### TO-BE
- WorkPackage RDF 스키마(간단) 정의 후, 패키지↔요소집합↔구역(BOT)↔일정(P6/IfcTask)↔상태(OPM) 연결.
- AWP 성과(생산성 향상, TIC 절감)는 업계에서 반복적으로 보고되어 “도입 타당성” 근거로 사용됨(세부 수치/조건은 조직 문서/프로젝트별 확인 필요).

---

## 권장 구현 아키텍처(실행 지향)

1. **IFC 원천 파싱/정리**: IfcOpenShell로 GUID/속성/Pset/geometry 추출  
2. **정합성 레이어**: ifcOWL로 IFC를 RDF로 보존(원본 재현)  
3. **업무 레이어(경량)**: BOT(위상) + BEO(요소 분류) + OPM(이력) + ISO15926/IDO(Plant 태그/사양/문서)  
4. **검증/추론**: SHACL + 룰(Jena/SWRL) + 외부 함수(geometry/집계)  
5. **현장 앱**: “오늘 할 일(작업가능요소)”/“지연 영향범위”/“AWP 진도”를 SPARQL로 자동 질의

---

## 참고문헌(IEEE)

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
[11] L. Jiang et al., “Multi-ontology fusion and rule development to facilitate automated code compliance checking using BIM and rule-based reasoning,” Advanced Engineering Informatics, 2022. (업로드 논문)  
[12] A. Lorvão Antunes et al., “(BIM–AMS linked data exchange / CoDEC 관련),” 2024. (업로드 논문)

---

### 부록: 온라인 리소스 링크(사양/문서)
- ifcOWL(overview): https://technical.buildingsmart.org/standards/ifc/ifc-formats/ifcowl/  
- IFC4 OWL index: https://standards.buildingsmart.org/IFC/DEV/IFC4/FINAL/OWL/index.html  
- BOT spec: https://w3c-lbd-cg.github.io/bot/  
- OPM spec: https://w3c-lbd-cg.github.io/opm/  
- BEO docs: https://cramonell.github.io/beo/actual/index-en.html  
- IDO (PCA RDS): https://rds.posccaesar.org/WD_IDO.pdf  
- NIST GCR 04-867: https://nvlpubs.nist.gov/nistpubs/gcr/2004/nist.gcr.04-867.pdf  
