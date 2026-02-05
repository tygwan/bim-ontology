# DXTnavis-BimOntology 통합 전략 문서

**작성일**: 2026-02-05
**분석 도구**: Codex gpt-5-codex (high reasoning, 773K tokens)
**대상 프로젝트**: DXTnavis v1.3.0 + bim-ontology

---

## 1. 개요

### 1.1 목적
DXTnavis (Navisworks 플러그인)와 bim-ontology (Python/C# 온톨로지 시스템) 간의
데이터 흐름, 네임스페이스, 식별자 체계를 통일하여 원활한 BIM-Schedule 자동화 파이프라인 구축.

### 1.2 핵심 과제

| 과제 | 현재 상태 | 목표 상태 |
|------|----------|----------|
| **네임스페이스** | `dxt:` vs `bso:` 분리 | `bso:` 통일 |
| **식별자** | InstanceGuid 의존 | Synthetic ID + IFC GUID 이중화 |
| **클래스 매핑** | 개별 관리 | 공유 YAML 설정 |
| **RDF 생성** | HierarchyToRdfConverter (dxt) | BSO 직접 생성 |

---

## 2. 현재 아키텍처 분석

### 2.1 DXTnavis 구조

```
dxtnavis/
├── Services/
│   ├── NavisworksDataExtractor.cs    # 계층 추출 (v1.3.0 Synthetic ID)
│   ├── HierarchyFileWriter.cs        # CSV/JSON Export
│   └── Ontology/
│       ├── HierarchyToRdfConverter.cs  # dxt: 네임스페이스 RDF 생성
│       ├── OntologyService.cs          # dotNetRDF 서비스
│       ├── InferenceEngine.cs          # SPARQL CONSTRUCT 추론
│       └── Neo4jQueryService.cs        # 그래프 DB 연동
└── Models/
    └── HierarchicalPropertyRecord.cs   # 핵심 데이터 모델
```

### 2.2 bim-ontology 구조

```
bim-ontology/
├── ontology/
│   └── bim-schedule.ttl              # BSO/BOT/IFC 통합 스키마
├── python/
│   ├── dxtnavis_loader.py            # DXT CSV → BSO RDF
│   ├── bim_extractor.py              # IFC → BSO RDF
│   ├── schedule_matcher.py           # Fellegi-Sunter 매칭
│   └── cp_scheduler.py               # CP-SAT 스케줄러
└── csharp/
    └── OntologyService.cs            # .NET BSO 서비스
```

### 2.3 데이터 흐름 (현재)

```
┌─────────────────┐     CSV/JSON      ┌─────────────────┐
│  Navisworks     │ ─────────────────▶│  dxtnavis_      │
│  DXTnavis       │                   │  loader.py      │
│  (C#)           │                   │  (Python)       │
└────────┬────────┘                   └────────┬────────┘
         │                                     │
         │ HierarchyToRdfConverter             │ to_rdf_graph()
         ▼                                     ▼
    dxt: namespace                        bso: namespace
    (내부 전용)                            (표준화)
```

**문제점**: 동일 데이터가 두 개의 네임스페이스로 분산 관리됨.

---

## 3. 식별자 전략 (v1.3.0 반영)

### 3.1 Synthetic ID 생성 로직

DXTnavis v1.3.0에서 구현된 `GetStableObjectId()` 메서드:

```
Fallback 순서:
1. InstanceGuid (유효한 경우)
2. Item GUID Property (Item 카테고리의 GUID 속성)
3. Authoring ID (Revit Element ID, AutoCAD Handle, IFC GlobalId)
4. Hierarchy Path Hash (MD5 기반 결정적 GUID)
```

### 3.2 URI 생성 정책

| 출처 | URI 형식 | 예시 |
|------|---------|------|
| **DXTnavis ObjectId** | `bso:element_{SyntheticId}` | `bso:element_a1b2c3d4-...` |
| **IFC GUID** | `bso:ifcGuid` 데이터 속성 | `"2O2Fr$t4X7Zf8NOew3FNr2"` |
| **Parent 관계** | `bot:containsElement` | 표준 BOT 속성 |
| **Level 관계** | `bso:onLevel` | BSO 확장 속성 |

### 3.3 이중 ID 저장

```turtle
bso:element_a1b2c3d4-5678-9abc-def0-123456789012
    a bso:Column ;
    bso:syntheticId "a1b2c3d4-5678-9abc-def0-123456789012" ;
    bso:ifcGuid "2O2Fr$t4X7Zf8NOew3FNr2" ;     # 있는 경우
    bso:revitElementId "1234567" ;              # 있는 경우
    bso:navisworksPath "Project > Building > Level 1 > Column" .
```

---

## 4. 통합 전략

### 4.1 Phase 1: CSV 스키마 표준화

**목표**: `HierarchyFileWriter`와 `dxtnavis_loader` 간 계약 명확화

**작업 항목**:
1. CSV 헤더 JSON Schema 정의
2. 필수/선택 컬럼 구분
3. 데이터 타입 명세

**CSV 스키마 (hierarchy-csv-schema.json)**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["ObjectId", "ParentId", "Level", "DisplayName"],
  "properties": {
    "ObjectId": { "type": "string", "format": "uuid" },
    "ParentId": { "type": "string", "format": "uuid" },
    "Level": { "type": "integer", "minimum": 0 },
    "DisplayName": { "type": "string" },
    "Category": { "type": "string" },
    "PropertyName": { "type": "string" },
    "PropertyValue": { "type": "string" },
    "RawValue": { "type": "string" },
    "DataType": { "type": "string" },
    "Unit": { "type": "string" }
  }
}
```

### 4.2 Phase 2: 클래스 매핑 통일

**목표**: IFC/Navisworks 카테고리 → BSO 클래스 매핑 단일화

**현재 중복**:
- `bim_extractor.py:69` - IFC_CLASS_MAP
- `dxtnavis_loader.py:71` - CATEGORY_MAP

**해결책**: 공유 YAML 설정 파일

**category-to-bso.yaml**:

```yaml
# BIM Category to BSO Class Mapping
# Used by both Python (dxtnavis_loader, bim_extractor) and C# (OntologyService)

version: "1.0"

structural:
  - pattern: ["Column", "기둥", "IfcColumn"]
    bso_class: "bso:Column"
  - pattern: ["Beam", "보", "IfcBeam"]
    bso_class: "bso:Beam"
  - pattern: ["Slab", "슬래브", "IfcSlab", "Floor", "바닥"]
    bso_class: "bso:Slab"
  - pattern: ["Foundation", "기초", "IfcFooting", "IfcPile"]
    bso_class: "bso:Foundation"
  - pattern: ["Wall", "벽", "IfcWall", "IfcWallStandardCase"]
    bso_class: "bso:Wall"

architectural:
  - pattern: ["Door", "문", "IfcDoor"]
    bso_class: "bso:Door"
  - pattern: ["Window", "창문", "IfcWindow"]
    bso_class: "bso:Window"
  - pattern: ["Stair", "계단", "IfcStair"]
    bso_class: "bso:Stair"
  - pattern: ["Railing", "난간", "IfcRailing"]
    bso_class: "bso:Railing"

mep:
  - pattern: ["Pipe", "배관", "IfcPipeSegment", "IfcFlowSegment"]
    bso_class: "bso:Pipe"
  - pattern: ["Duct", "덕트", "IfcDuctSegment"]
    bso_class: "bso:Duct"
  - pattern: ["Cable", "케이블", "IfcCableSegment"]
    bso_class: "bso:CableTray"

default:
  bso_class: "bso:BimElement"
```

### 4.3 Phase 3: 네임스페이스 통일

**옵션 A**: DXTnavis가 BSO 직접 생성 (권장)
- `HierarchyToRdfConverter`를 수정하여 `bso:` 네임스페이스 사용
- 장점: 단일 소스, 일관성
- 단점: DXTnavis 코드 변경 필요

**옵션 B**: dxt: → bso: 변환 레이어
- 별도 변환기 추가
- 장점: 기존 코드 유지
- 단점: 추가 처리 단계

**권장**: 옵션 A (BSO 직접 생성)

**HierarchyToRdfConverter 수정 사항**:

```csharp
// 현재 (dxt:)
private const string DXT = "http://dxtnavis.org/ontology#";

// 변경 후 (bso:)
private const string BSO = "http://bso.construction/ontology#";
private const string BOT = "https://w3id.org/bot#";

// URI 생성
private IUriNode GetOrCreateObjectUri(Guid objectId)
{
    string uri = BSO + "element_" + objectId.ToString();
    return _graph.CreateUriNode(new Uri(uri));
}
```

### 4.4 Phase 4: 추론 엔진 통일

**현재**: `InferenceEngine.cs`가 `dxt:` 네임스페이스에서만 동작

**변경**: BSO SPARQL 규칙으로 마이그레이션

**예시 (same-level precedence)**:

```sparql
# 현재 (dxt:)
PREFIX dxt: <http://dxtnavis.org/ontology#>
CONSTRUCT { ?a dxt:mustPrecede ?b }
WHERE { ?a dxt:onLevel ?level . ?b dxt:onLevel ?level . ... }

# 변경 후 (bso:)
PREFIX bso: <http://bso.construction/ontology#>
CONSTRUCT { ?a bso:mustPrecede ?b }
WHERE { ?a bso:onLevel ?level . ?b bso:onLevel ?level . ... }
```

---

## 5. 데이터 흐름 (통합 후)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Navisworks 2025                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                        DXTnavis v1.3.0+                     │    │
│  │  NavisworksDataExtractor ─────▶ HierarchyFileWriter         │    │
│  │  (Synthetic ID)                 (CSV/JSON)                  │    │
│  │         │                            │                      │    │
│  │         ▼                            │                      │    │
│  │  HierarchyToRdfConverter             │                      │    │
│  │  (BSO namespace)                     │                      │    │
│  │         │                            │                      │    │
│  │         ▼                            ▼                      │    │
│  │     bso:*.ttl              hierarchy_data.csv               │    │
│  └─────────┼────────────────────────────┼──────────────────────┘    │
└────────────┼────────────────────────────┼───────────────────────────┘
             │                            │
             │ (내부 RDF)                 │ (외부 연동)
             │                            │
             ▼                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Python Ontology Engine                            │
│  ┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │ dxtnavis_loader │───▶│ schedule_matcher │───▶│  cp_scheduler  │  │
│  │  (CSV → BSO)    │    │ (F1 ≥ 0.95)      │    │ (CP-SAT)       │  │
│  └─────────────────┘    └──────────────────┘    └────────────────┘  │
│           │                      │                      │            │
│           ▼                      ▼                      ▼            │
│       bso:*.ttl            matches.ttl           schedule.csv       │
└───────────┼──────────────────────┼──────────────────────┼───────────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DXTnavis AWP 4D Automation                        │
│  ┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │  Neo4jQuery     │───▶│  Selection Sets  │───▶│   TimeLiner    │  │
│  │  Service        │    │  (자동 생성)      │    │ (4D 시뮬레이션) │  │
│  └─────────────────┘    └──────────────────┘    └────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. 구현 우선순위

### 6.1 단기 (1-2주)

| 순서 | 작업 | 담당 | 파일 |
|------|------|------|------|
| 1 | CSV Schema JSON 작성 | bim-ontology | `schemas/hierarchy-csv-schema.json` |
| 2 | category-to-bso.yaml 작성 | bim-ontology | `config/category-to-bso.yaml` |
| 3 | dxtnavis_loader.py YAML 로딩 | bim-ontology | `python/dxtnavis_loader.py` |

### 6.2 중기 (2-4주)

| 순서 | 작업 | 담당 | 파일 |
|------|------|------|------|
| 4 | HierarchyToRdfConverter BSO 전환 | dxtnavis | `Services/Ontology/HierarchyToRdfConverter.cs` |
| 5 | InferenceEngine BSO 규칙 | dxtnavis | `Services/Ontology/InferenceEngine.cs` |
| 6 | OntologyService 통합 | both | 공유 NuGet 패키지 |

### 6.3 장기 (1-2개월)

| 순서 | 작업 | 담당 | 비고 |
|------|------|------|------|
| 7 | End-to-End 테스트 | both | 실제 Navisworks 모델 |
| 8 | Neo4j 피드백 루프 | dxtnavis | 매칭 결과 시각화 |
| 9 | 성능 벤치마크 | both | F1 ≥ 0.95 검증 |

---

## 7. 검증 기준

### 7.1 기능 검증

| 테스트 케이스 | 예상 결과 |
|--------------|----------|
| DXT CSV → dxtnavis_loader | 파싱 오류 없음 |
| BSO TTL 유효성 | Turtle Validator 통과 |
| Parent-Child 관계 | bot:containsElement 그래프 연결 |
| Schedule 매칭 | F1 ≥ 0.95 |

### 7.2 ID 검증

| 검증 항목 | 조건 |
|----------|------|
| ObjectId 고유성 | 중복 없음 |
| ParentId 참조 무결성 | 모든 ParentId가 유효한 ObjectId |
| IFC GUID 보존 | 원본 GUID 손실 없음 |

---

## 8. 참고 자료

### 8.1 관련 문서
- [DXTnavis CLAUDE.md](../dxtnavis/CLAUDE.md)
- [bim-schedule.ttl](../ontology/bim-schedule.ttl)
- [DXTnavis CHANGELOG v1.3.0](../dxtnavis/CHANGELOG.md)

### 8.2 코드 참조

| 컴포넌트 | 파일 | 라인 |
|---------|------|------|
| Synthetic ID | `NavisworksDataExtractor.cs` | 35-62 |
| CSV Export | `HierarchyFileWriter.cs` | 36-40 |
| BSO Class Map | `dxtnavis_loader.py` | 71 |
| RDF Converter | `HierarchyToRdfConverter.cs` | 20, 96 |
| Inference Rules | `InferenceEngine.cs` | 67, 213, 282 |

### 8.3 외부 온톨로지
- [BOT (Building Topology Ontology)](https://w3id.org/bot)
- [IFC OWL](https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL)
- [BSO (BIM-Schedule Ontology)](./ontology/bim-schedule.ttl)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-02-05 | 초기 작성 (Codex 분석 기반) |
