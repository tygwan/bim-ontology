# BIM Ontology Dashboard - User Manual

## Overview

BIM Ontology Dashboard는 IFC → RDF 온톨로지 데이터를 시각화하고 관리하는 웹 대시보드입니다.
총 12개의 탭으로 구성되며, 각 탭은 특정 기능을 담당합니다.

- **URL**: `http://localhost:8001/`
- **Theme**: Dark mode (slate/blue)
- **기술**: Vanilla JS + Tailwind CSS + Chart.js

---

## 1. Overview 탭

**목적**: 전체 RDF 데이터 현황을 한눈에 파악합니다.

### 주요 요소
| 항목 | 설명 |
|------|------|
| Total Triples | RDF 그래프에 저장된 총 트리플 수 |
| Physical Elements | `bim:PhysicalElement` 타입 인스턴스 수 |
| Categories | 요소 카테고리 종류 수 (Pipe, Valve 등) |
| Buildings | `bim:Building` 인스턴스 수 |

### 차트
- **Category Distribution**: 도넛 차트 - 카테고리별 요소 비율
- **Top Categories**: 가로 막대 차트 - 상위 10개 카테고리

### 사용법
- 탭 클릭 시 자동 로딩
- 차트는 반응형으로 자동 리사이즈

---

## 2. Buildings 탭

**목적**: IFC 공간 계층 구조(Project → Site → Building → Storey)를 탐색합니다.

### 레이아웃
- **좌측**: Building Hierarchy 트리 (색상 구분: PRJ=보라, SITE=초록, BLD=파랑, STY=노랑)
- **우측**: 선택된 노드의 상세 정보 (층 목록 + 표고)

### 사용법
1. 좌측 트리에서 원하는 Building/Storey를 클릭합니다
2. 우측에 해당 노드 정보와 층별 Elevation이 표시됩니다

---

## 3. Elements 탭

**목적**: 개별 BIM 요소(PhysicalElement)를 검색하고 조회합니다.

### 필터
| 필터 | 설명 |
|------|------|
| Category | 드롭다운 - 전체 또는 특정 카테고리 선택 |
| Search | 이름으로 텍스트 검색 (클라이언트 측) |

### 테이블 컬럼
- Name, Category, Original Type (IFC 타입), Global ID

### 사용법
1. 카테고리 드롭다운에서 원하는 카테고리를 선택합니다
2. 검색란에 이름 키워드를 입력합니다
3. **Search** 버튼을 클릭합니다
4. Prev/Next 버튼으로 페이지를 이동합니다 (50개 단위)

---

## 4. SPARQL 탭

**목적**: RDF 그래프에 직접 SPARQL 쿼리를 실행합니다.

### 레이아웃
- **좌측**: SPARQL 에디터 + 결과 테이블
- **우측**: Query Templates (10개 사전 정의 쿼리)

### 사전 정의 쿼리 템플릿

| # | 이름 | 설명 |
|---|------|------|
| 1 | Category Statistics | 카테고리별 요소 수 |
| 2 | Building Hierarchy | 부모-자식 공간 관계 |
| 3 | Elements by Storey | 층별 요소 수 |
| 4 | Pipe Elements | Pipe 카테고리 요소 목록 |
| 5 | All Properties of Element | 특정 요소의 모든 속성 |
| 6 | Structural Elements | 추론 후 구조 요소 |
| 7 | Delivery Status Summary | 배송 상태별 집계 (Lean Layer) |
| 8 | Today's Work (AWP) | IWP 전체 목록 (Lean Layer) |
| 9 | Delayed Elements | 지연 부재 목록 (Lean Layer) |
| 10 | AWP Hierarchy | CWA > CWP > IWP 계층 (Lean Layer) |

### 사용법
1. 우측 템플릿 버튼을 클릭하면 에디터에 쿼리가 로딩됩니다
2. 필요 시 쿼리를 수정합니다
3. **Execute** 버튼을 클릭합니다
4. 결과가 테이블 형태로 표시됩니다 (행 수 + 실행 시간 포함)

### 참고
- URI는 자동으로 `#` 이후 부분만 표시됩니다
- PREFIX 선언이 필요합니다

---

## 5. Properties 탭

**목적**: 요소의 PropertySet 및 Plant(SP3D) 데이터를 조회합니다.

### 기능

| 기능 | 설명 |
|------|------|
| Property Lookup | GlobalId로 특정 요소의 PropertySet 조회 |
| Property Search | 키워드로 속성 이름 검색 (예: Weight) |
| Plant Data Summary | Smart3D Plant PropertySet 현황 요약 |

### 사용법

**요소 속성 조회:**
1. GlobalId 필드에 요소의 GlobalId를 입력합니다
2. **Lookup** 버튼을 클릭합니다
3. PropertySet별로 속성 이름과 값이 표시됩니다

**속성 검색:**
1. Property Search 필드에 키워드를 입력합니다 (예: `Weight`)
2. **Search** 버튼을 클릭합니다
3. 해당 키워드를 포함하는 모든 속성이 Element/PropertySet/Value로 표시됩니다

---

## 6. Ontology 탭

**목적**: OWL 온톨로지 스키마를 편집하고 관리합니다.

### 기능 영역

| 영역 | 설명 |
|------|------|
| Object Types (Classes) | OWL 클래스 목록 - Name, Parent, Label |
| Link Types (Relations) | ObjectProperty 목록 - Name, Domain, Range, Inverse |
| Classification Rules | JSON 기반 분류 규칙 편집 |
| Schema Import/Export | 스키마 JSON 파일 내보내기/가져오기/그래프 적용 |

### 사용법

**새 타입 생성:**
1. Object Types 패널의 **+ New Type** 버튼을 클릭합니다
2. 팝업에서 타입 이름과 부모 클래스를 입력합니다

**새 링크 생성:**
1. Link Types 패널의 **+ New Link** 버튼을 클릭합니다
2. 팝업에서 링크 이름, Domain, Range 클래스를 입력합니다

**스키마 적용:**
1. **Apply to Graph** 버튼을 클릭하면 custom_schema.json의 정의가 RDF 그래프에 OWL 트리플로 추가됩니다

---

## 7. Reasoning 탭

**목적**: OWL/RDFS 추론 및 커스텀 SPARQL CONSTRUCT 규칙을 실행합니다.

### 추론 규칙 (10개)

**기본 규칙 (1-7)**:
- 구조 요소 분류, MEP 요소 분류, 접근 요소 분류 등

**Lean Layer 규칙 (8-10)**:
| 규칙 | 이름 | 설명 |
|------|------|------|
| Rule 8 | infer_delayed_element | 계획일 < 현재일 && 미설치 → `bim:isDelayed true` |
| Rule 9 | infer_iwp_executable | AllCleared && 전체 요소 OnSite/Installed → `awp:isExecutable true` |
| Rule 10 | infer_element_ready | DeliveryStatus=OnSite/Installed/Inspected → `bim:isReady true` |

### 사용법
1. **Run Reasoning** 버튼을 클릭합니다
2. Before/After 트리플 수와 추론된 트리플 수가 표시됩니다
3. Inferred Types 테이블에 StructuralElement/MEPElement/AccessElement 카운트가 표시됩니다

### 참고
- Lean Layer 데이터가 주입된 후 실행하면 Rule 8-10도 적용됩니다
- 추론은 누적됩니다 (기존 트리플에 추가)

---

## 8. Validation 탭

**목적**: RDF 데이터 품질을 8개 검사 항목으로 검증합니다.

### 검사 항목

| # | 검사 | 설명 | 상태 기준 |
|---|------|------|-----------|
| 1 | Schema Completeness | OWL 클래스/속성 수 | PASS (클래스 > 0) |
| 2 | Spatial Hierarchy | Project→Site→Building→Storey 체인 | PASS (체인 존재) |
| 3 | Element Statistics | 전체 요소 수 + 카테고리 수 + Top 5 | INFO |
| 4 | URI Consistency | 고아 요소 + 미연결 요소 | PASS (0개) |
| 5 | PropertySet Coverage | PropertySet 보유율 | WARN (< 30%) |
| 6 | Required Properties | 필수 속성(GlobalId) 누락 | PASS (0개) |
| 7 | Classification Quality | "Other" 카테고리 비율 | WARN (> 15%) |
| 8 | Relationship Integrity | 양방향 관계 대칭성 | PASS (대칭) |

### 사용법
1. TTL File 드롭다운에서 대상 파일을 선택합니다 (기본: 현재 로딩된 파일)
2. **Run Validation** 버튼을 클릭합니다
3. 4개 요약 카드(Total Triples, PASS, WARN, FAIL)와 8개 검사 카드가 표시됩니다
4. 카드 헤더를 클릭하면 상세 내용을 접을 수 있습니다
5. 상단 필터 체크박스로 특정 검사만 표시할 수 있습니다

### Other Category Explorer
- Classification Quality에서 "Other" 비율이 높을 경우 자동 표시됩니다
- 이름 패턴 기반 카테고리 추천 제공 (PipeFitting, Hanger, Nozzle 등)

---

## 9. Explorer 탭

**목적**: RDF 노드를 타입/술어(predicate) 기준으로 자유롭게 탐색합니다.

### 레이아웃
- **좌측**: Node Types 리스트 (타입별 인스턴스 수)
- **우측 상단**: Columns 선택기 (predicate 체크박스)
- **우측 중단**: 노드 테이블 (선택된 컬럼으로 표시)
- **우측 하단**: Node Detail (클릭한 노드의 모든 트리플)

### 사용법
1. 좌측에서 원하는 Node Type을 클릭합니다 (예: `bim:PhysicalElement`)
2. 우측 Columns에서 보고 싶은 predicate를 체크합니다 (기본: hasName, hasCategory, hasGlobalId, hasOriginalType)
3. **Load** 버튼을 클릭합니다
4. 테이블에서 노드(subject)를 클릭하면 하단에 해당 노드의 모든 트리플이 표시됩니다
5. 검색 필드에 이름을 입력하면 필터링됩니다

### 참고
- TTL File 드롭다운으로 다른 RDF 파일을 탐색할 수 있습니다
- **Refresh** 버튼으로 타입/술어 목록을 새로고침합니다

---

## 10. Lean Layer 탭

**목적**: Lean Layer(Schedule, AWP, Status, Equipment) 데이터를 CSV로 주입하고 현황을 확인합니다.

### 상단 통계 카드
| 카드 | 설명 |
|------|------|
| Tasks | ConstructionTask 인스턴스 수 |
| IWPs | InstallationWorkPackage 인스턴스 수 |
| Statuses | ElementStatus 인스턴스 수 |
| Equipment | ConstructionEquipment 인스턴스 수 |

### CSV Data Injection

**Injection Type 선택:**

| 타입 | CSV 컬럼 | 설명 |
|------|----------|------|
| Schedule | GlobalId or ObjectId or SyncID, TaskName, PlannedStart, PlannedEnd, ActualStart, ActualEnd, Duration/PlannedDuration/ActualDuration, UnitCost/Cost, PlannedInstallDate, DeliveryStatus, CWP_ID | 일정 + 비용/소요일 + 배송 상태 |
| AWP | GlobalId or ObjectId or SyncID, CWA_ID, CWP_ID, IWP_ID, IWP_StartDate, IWP_EndDate, ConstraintStatus | 작업 패키지 계층 |
| Status | GlobalId or ObjectId or SyncID, StatusValue, StatusDate, DeliveryStatus | 요소 상태 이력 |
| Equipment | EquipmentID, Name, Width, Height, TurningRadius, BoomLength, LoadCapacity, AccessZone_CWA_ID | 장비 사양 |

### 사용법
1. **Injection Type** 드롭다운에서 CSV 유형을 선택합니다
2. **CSV File** 에서 파일을 선택합니다
3. **Inject CSV** 버튼을 클릭합니다
4. 결과(추가된 트리플 수, 매칭된 요소 수 등)가 표시됩니다
5. 우측 Summary 테이블이 자동 갱신됩니다

### Lean Layer Summary
- CWA/CWP/IWP 수, 상태 보유 요소 수, IWP 할당 요소 수 등
- Cost/Duration KPI:
  - Elements with Unit Cost, Elements with Consume Duration
  - Tasks with Typed Duration vs Legacy Duration
  - Total/Avg Unit Cost, Avg Consume Duration, Avg Effective Task Duration
- Duration 우선순위(Effective Task Duration):
  - `ActualDuration` → `PlannedDuration` → `Duration(legacy 문자열, 숫자형일 때만)`

### 참고
- GlobalId, ObjectId, SyncID 중 RDF에 존재하는 식별자로 매칭됩니다
- 존재하지 않는 식별자는 무시됩니다
- 주입 시 lean_schema.ttl이 자동 로딩됩니다

---

## 11. Today's Work 탭

**목적**: AWP(Advanced Work Packaging) 기반으로 특정 날짜의 작업 계획을 조회합니다.

### 상단 컨트롤
- **Target Date**: 조회 날짜 선택 (기본: 오늘)
- **Load**: 해당 날짜의 IWP 조회

### 요약 카드
| 카드 | 설명 |
|------|------|
| Active IWPs | 해당 날짜에 활성인 IWP 수 |
| Total Elements | 활성 IWP에 포함된 전체 요소 수 |
| Executable | 제약 조건이 AllCleared인 IWP 수 |

### 테이블 컬럼
| 컬럼 | 설명 |
|------|------|
| IWP | Installation Work Package 이름 |
| CWP | Construction Work Package (상위) |
| CWA | Construction Work Area (최상위) |
| Period | 시작일 ~ 종료일 |
| Elements | 포함 요소 수 |
| Constraint | 제약 상태 (색상 구분) |

### Constraint Status 색상

| 상태 | 색상 | 의미 |
|------|------|------|
| AllCleared | 초록 | 모든 제약 해소 → 실행 가능 |
| PendingMaterial | 노랑 | 자재 미도착 |
| PendingApproval | 주황 | 승인 대기 |
| PendingPredecessor | 빨강 | 선행 작업 미완료 |

### 사용법
1. **Target Date**에서 날짜를 선택합니다
2. **Load** 버튼을 클릭합니다
3. 해당 날짜에 `startDate <= 날짜 <= endDate`인 IWP가 표시됩니다

### 참고
- AWP CSV를 먼저 주입해야 데이터가 표시됩니다 (Lean Layer 탭)
- 추론(Reasoning)을 실행하면 `isExecutable` 필드가 자동 판단됩니다

---

## 12. Status Monitor 탭

**목적**: 부재 지연 현황과 배송 상태를 모니터링하고, 개별 요소 상태를 업데이트합니다.

### 좌측: Delayed Elements

| 항목 | 설명 |
|------|------|
| 기준 날짜 | 지연 판단 기준 날짜 (기본: 오늘) |
| Delayed 카운트 | 지연 부재 총 수 |
| 테이블 | Name, Category, Planned Date, Delivery Status |

**지연 판단 기준**: PlannedInstallDate < 기준 날짜 && DeliveryStatus != Installed/Inspected

### 우측: Delivery Status Distribution

- **도넛 차트**: 배송 상태별 분포 (Ordered/InProduction/Shipped/OnSite/Installed/Inspected)
- **테이블**: 상태별 카운트

### 하단: Element Status Update

| 필드 | 설명 | 유효값 |
|------|------|--------|
| GlobalId | 업데이트할 요소의 GlobalId | 기존 요소의 GlobalId |
| Status Value | 요소 상태 | Planned, Designed, Fabricated, Shipped, OnSite, Installed, Inspected |
| Delivery Status | 배송 상태 (선택) | Ordered, InProduction, Shipped, OnSite, Installed |

### 사용법

**지연 부재 확인:**
1. 기준 날짜를 선택합니다
2. **Check** 버튼을 클릭합니다
3. 지연 부재 목록이 표시됩니다

**상태 업데이트:**
1. GlobalId 필드에 요소 ID를 입력합니다
2. Status Value 드롭다운에서 새 상태를 선택합니다
3. (선택) Delivery Status를 선택합니다
4. **Update** 버튼을 클릭합니다
5. 성공 시 차트가 자동 갱신됩니다

### 참고
- Schedule CSV를 먼저 주입해야 PlannedInstallDate가 존재합니다
- 상태 업데이트 시 `bim:ElementStatus` 인스턴스가 생성되고 `bim:hasStatusDate`에 현재 시간이 기록됩니다
- DeliveryStatus가 OnSite/Installed/Inspected이면 `bim:isReady true`가 자동 설정됩니다

---

## REST API 참조

Dashboard가 사용하는 주요 API 엔드포인트:

### 공통
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 서버 상태 + 트리플 수 |
| GET | `/api/statistics` | 전체 통계 |
| GET | `/api/statistics/categories` | 카테고리별 통계 |
| POST | `/api/sparql` | SPARQL 쿼리 실행 |

### Lean Layer
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/lean/inject/schedule` | 일정 CSV 주입 |
| POST | `/api/lean/inject/awp` | AWP CSV 주입 |
| POST | `/api/lean/inject/status` | 상태 CSV 주입 |
| POST | `/api/lean/inject/equipment` | 장비 CSV 주입 |
| PUT | `/api/lean/status/{global_id}` | 단일 요소 상태 업데이트 |
| GET | `/api/lean/today?target_date=YYYY-MM-DD` | 해당일 작업 조회 |
| GET | `/api/lean/delayed?reference_date=YYYY-MM-DD` | 지연 부재 조회 |
| GET | `/api/lean/iwp/{iwp_id}/constraints` | IWP 제약/요소 조회 |
| GET | `/api/lean/stats` | Lean Layer 현황 통계 |

---

## 빠른 시작 가이드

### 1. 서버 실행
```bash
cd /home/coffin/dev/bim-ontology
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8001
```

### 2. 브라우저 접속
`http://localhost:8001/`

### 3. Lean Layer 데이터 주입 (선택)

**브라우저에서:**
1. Lean Layer 탭으로 이동
2. Schedule CSV 주입
3. AWP CSV 주입

**API로:**
```bash
# 일정 데이터
curl -X POST http://localhost:8001/api/lean/inject/schedule \
  -F "file=@data/test/schedule_sample.csv"

# AWP 데이터
curl -X POST http://localhost:8001/api/lean/inject/awp \
  -F "file=@data/test/awp_sample.csv"
```

### 4. 추론 실행
- Reasoning 탭 → **Run Reasoning** 클릭
- Lean Layer 규칙(지연 감지, IWP 실행 가능성, 요소 준비 상태)이 자동 적용됩니다

### 5. 결과 확인
- Today's Work 탭: AWP 날짜 범위 내 IWP 조회
- Status Monitor 탭: 지연 부재 확인 + 상태 업데이트

---

**Document Version**: v1.0
**Last Updated**: 2026-02-04
