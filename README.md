# BIM Ontology

> Navisworks CSV / IFC 파일을 RDF 온톨로지로 변환하고, SPARQL 쿼리 + 계층 탐색 + 속성 집계 + 검증을 제공하는 시맨틱 BIM 파이프라인

## Overview

Navisworks에서 내보낸 CSV(AllHierarchy) 또는 IFC 파일을 RDF 트리플로 변환하여 시맨틱 웹 기술로 건설 데이터를 탐색, 추론, 검증합니다.

```
                          ┌─────────────┐
Navisworks CSV ──────────►│             │
  (AllHierarchy.csv)      │  navis_to_  │──► TTL (RDF)──► SPARQL API ──► Dashboard
                          │  rdf.py     │       │
IFC File ────────────────►│             │       ├──► OWL Reasoning
  (nwd4op-12.ifc)        └─────────────┘       ├──► SHACL Validation
                                                └──► Property Aggregation
```

### Two Data Pipelines

| Pipeline | Source | Output | Features |
|------

## Projects Using cc-initializer

### Community Showcase

| Project | Description |
|---------|-------------|
| [tygwan/bim-ontology](https://github.com/tygwan/bim-ontology) | BIM Ontology - Semantic BIM Pipeline |
| [tygwan/dxtnavis](https://github.com/tygwan/dxtnavis) | DXT Navigator - Real-world example project |

> **Add your project**: Add `uses-cc-initializer` topic to your repo or [submit a PR](PROJECTS.json)

_Last updated: 2026-02-08_

-------|--------|--------|----------|
| **CSV Pipeline** (recommended) | Navisworks AllHierarchy CSV (76MB) | navis-via-csv.ttl (282K triples) | ParentId hierarchy, SP3D properties, PropertyValue reification |
| **IFC Pipeline** | IFC4/IFC2X3 file | nwd4op-12.ttl (39K triples) | Building hierarchy, ifcOWL triples |

CSV Pipeline이 더 풍부한 데이터를 제공합니다 (12,009 objects, 9-level hierarchy, 414K property values).

---

## Getting Started (First-Time Users)

### Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** - Python package manager

```bash
# uv 설치 (아직 없다면)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 1: Clone and Install

```bash
git clone https://github.com/tygwan/bim-ontology.git
cd bim-ontology
uv sync
```

> `uv sync`은 자동으로 `.venv/` 가상환경을 생성하고 의존성을 설치합니다. 이후 모든 명령어는 `uv run`을 통해 실행하면 가상환경이 자동 활성화됩니다. 직접 활성화하려면 `source .venv/bin/activate`를 사용하세요.

### Step 2: Data Files

**Data files are NOT included in git** (too large). You need to obtain them separately.

Place the data files in the following locations:

```
data/rdf/
  ├── navis-via-csv.ttl        # 16MB  - Basic (hierarchy + SP3D)
  ├── navis-via-csv-v3.ttl     # 131MB - Full (+ 414K PropertyValues)
  └── nwd4op-12.ttl            # 2MB   - IFC-based (optional)
references/
  └── AllHierarchy_*.csv       # 76MB  - Source Navisworks CSV (optional)
```

| File | Required? | Description |
|------|-----------|-------------|
| `navis-via-csv.ttl` | **Yes** (minimum) | Navisworks hierarchy + SP3D properties. 282K triples. |
| `navis-via-csv-v3.ttl` | Recommended | Full data with PropertyValue reification. 2.8M triples. |
| `nwd4op-12.ttl` | Optional | IFC-based data for Buildings tab. |
| `AllHierarchy_*.csv` | Optional | Source CSV, only needed if you want to re-convert. |

### Step 3: Start the Server

```bash
# 기본 실행 (default: navis-via-csv-v3.ttl)
uv run uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

다른 데이터 파일을 사용하려면 `BIM_RDF_PATH` 환경변수를 지정합니다:

```bash
# 빠른 시작 (16MB, 282K triples, ~2분)
BIM_RDF_PATH=data/rdf/navis-via-csv.ttl uv run uvicorn src.api.server:app --host 0.0.0.0 --port 8000

# 빠른 테스트 (2MB, 39K triples, ~10초)
BIM_RDF_PATH=data/rdf/nwd4op-12.ttl uv run uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

> **Note**: The server will not respond until the TTL file is fully parsed. Wait for the "Application startup complete" message in the terminal.

### Step 4: Open Dashboard

Open [http://localhost:8000](http://localhost:8000) in your browser.

You should see the **BIM Ontology Dashboard** with "Connected" status and a triple count in the top-right corner.

---

## Dashboard Guide

13-tab dashboard for exploring BIM data.

### Tab Overview

| Tab | Purpose | When to Use |
|-----|---------|-------------|
| **Overview** | Summary stats, category charts, data source selector | First stop - verify data is loaded |
| **Buildings** | IFC building hierarchy (Project > Site > Building > Storey) | IFC data only (nwd4op-12.ttl) |
| **Hierarchy** | System Path tree + **Navisworks Miller Columns drill-down** | **Main explorer** - navigate hierarchy, aggregate properties |
| **Elements** | Filter/search individual BIM elements | Find specific elements by name or category |
| **SPARQL** | Custom SPARQL query editor + templates | Advanced users - custom data analysis |
| **Properties** | PropertySet lookup by GlobalId, property search | Inspect individual element properties |
| **Ontology** | Schema editor - types, relations, classification rules | Modify the ontology schema |
| **Reasoning** | OWL/RDFS inference engine | Infer implicit relationships |
| **Validation** | Quality checks on TTL data | Data quality assurance |
| **Explorer** | Generic RDF node browser with custom columns | Deep exploration of any node type |
| **Lean Layer** | CSV injection (schedule, AWP, status, equipment) | Construction management data |
| **Today's Work** | Daily work package viewer | Schedule-based planning |
| **Status Monitor** | Delayed elements, status tracking | Progress monitoring |

### Recommended First Steps

1. **Overview tab** - Confirm data is loaded (check triple count and stats)
2. **Hierarchy tab** - Click "Load" on the Navisworks Hierarchy Tree
3. Drill down into nodes using the **Miller Columns** (click a node to see children)
4. Select a node to see **Property Summary** (category breakdown, status distribution)
5. Try the **SPARQL tab** with template queries
6. Explore the **Explorer tab** to browse any RDF type

### Hierarchy Tab - Miller Columns

The main feature for exploring the Navisworks hierarchy:

```
[Root Column]  →  [Children]  →  [Grandchildren]  →  ...
┌────────────┐   ┌──────────┐   ┌──────────────┐
│ For Review │ → │ TRAINING │ → │ A1     (640) │
│    (12008) │   │  (11859) │   │ A2    (2334) │
│            │   │ Structure│   │ A3    (2180) │
│            │   │    (134) │   │ ...          │
└────────────┘   └──────────┘   └──────────────┘
```

- Click a node to see its children in the next column
- Breadcrumb navigation at the top
- Numbers in parentheses = total descendants
- **Property Summary** panel shows category/status aggregation of the selected subtree
- **Show Graph** button for canvas visualization

### Data File Switching

You can switch TTL files without restarting the server:
1. **Overview tab** - Use the "Data Source" dropdown and click "Load"
2. **Hierarchy tab** - Use the "RDF Data Source" dropdown and click "Load File"

---

## API Reference

### Core
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web dashboard |
| GET | `/health` | Health check (`{"status":"healthy","triples":282704}`) |
| POST | `/api/sparql` | SPARQL query (`{"query":"SELECT ..."}`) |
| GET | `/api/statistics` | Overall statistics |
| GET | `/api/statistics/metadata` | Max level, total objects, property values |

### Elements & Buildings
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/buildings` | Building list |
| GET | `/api/storeys` | Storey list |
| GET | `/api/elements?category=Pipe` | Elements with filter |
| GET | `/api/hierarchy` | Building hierarchy |

### Properties
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/properties/{global_id}` | Element PropertySets |
| GET | `/api/properties/plant-data` | SP3D data summary |
| GET | `/api/properties/search?key=Weight` | Property search |

### Reasoning & Validation
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/reasoning` | Run OWL/RDFS inference |
| POST | `/api/reasoning/validate` | Run SHACL validation |
| GET | `/api/reasoning/ttl-files` | List available TTL files |
| POST | `/api/reasoning/reload?file_name=x.ttl` | Load a different TTL file |

### Ontology Editor
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/ontology/types` | Object Types CRUD |
| GET/POST | `/api/ontology/links` | Link Types CRUD |
| GET/PUT | `/api/ontology/rules` | Classification rules |
| POST | `/api/ontology/apply` | Apply schema to graph |
| GET/POST | `/api/ontology/export` / `import` | Schema JSON |

---

## RDF Data Model

### Namespaces

| Prefix | URI | Usage |
|--------|-----|-------|
| `navis:` | `http://example.org/bim-ontology/navis#` | Navisworks hierarchy, levels, counts |
| `sp3d:` | `http://example.org/bim-ontology/sp3d#` | Smart Plant 3D properties |
| `bim:` | `http://example.org/bim-ontology/schema#` | BIM categories, classification |
| `prop:` | `http://example.org/bim-ontology/property#` | PropertyValue reification (v3) |
| `inst:` | `http://example.org/bim-ontology/instance#` | Individual node instances |

### Hierarchy Predicates

```turtle
# Navisworks ParentId hierarchy
inst:node_A navis:hasParent inst:node_B .
inst:node_A navis:hasLevel 2 .
inst:node_A navis:hasChildCount 7 .
inst:node_A navis:hasDescendantCount 11859 .

# System Path (logical hierarchy)
inst:node_A sp3d:hasSystemPath "TRAINING\\A1\\Unit01" .
```

### PropertyValue Pattern (v3 only)

```turtle
inst:element_X prop:hasProperty inst:pv_123 .
inst:pv_123 a prop:PropertyValue ;
    prop:propertyName "DryWeight" ;
    prop:rawValue "1250.5" ;
    prop:dataType "Double" ;
    prop:unit "kg" ;
    prop:category "Piping" .
```

---

## Project Structure

```
bim-ontology/
├── src/
│   ├── api/
│   │   ├── server.py                 # FastAPI server (env-based config)
│   │   └── routes/                   # sparql, buildings, statistics,
│   │                                 # reasoning, properties, ontology_editor
│   ├── dashboard/
│   │   ├── index.html                # 13-tab dashboard
│   │   └── app.js                    # Dashboard logic (Miller Columns, etc.)
│   ├── converter/
│   │   ├── navis_to_rdf.py           # CSV → RDF pipeline
│   │   ├── ifc_to_rdf.py             # IFC → RDF pipeline
│   │   ├── namespace_manager.py      # Namespace management
│   │   └── mapping.py                # IFC → ifcOWL mappings
│   ├── parser/ifc_parser.py          # IFC parsing (IFC4/IFC2X3)
│   ├── inference/
│   │   ├── reasoner.py               # OWL/RDFS + custom rules
│   │   └── shacl_validator.py        # SHACL validation
│   ├── ontology/schema_manager.py    # Dynamic schema CRUD
│   └── storage/                      # TripleStore (rdflib / GraphDB)
├── data/
│   ├── rdf/                          # TTL files (.gitignore)
│   └── ontology/                     # SHACL shapes, rules
├── references/                       # CSV, IFC, PDF (.gitignore)
├── docs/
│   └── DASHBOARD-GUIDE.md            # Detailed tab-by-tab guide
├── pyproject.toml                    # Dependencies (uv)
└── uv.lock                          # Lock file
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BIM_RDF_PATH` | `data/rdf/navis-via-csv-v3.ttl` | TTL file to load on startup |
| `BIM_IFC_PATH` | `references/nwd4op-12.ifc` | IFC file for IFC conversion features |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| RDF/SPARQL | rdflib 7.x |
| Web Framework | FastAPI + Uvicorn |
| OWL Reasoning | owlrl |
| IFC Parsing | ifcopenshell (optional) |
| Dashboard | Vanilla JS + Tailwind CSS + Chart.js |
| Package Manager | uv |

## Troubleshooting

### Server won't start
```bash
# Check Python version
python3 --version  # Must be 3.11+

# Reinstall dependencies
uv sync

# Check if port is in use
lsof -i :8000
```

### Page keeps loading / "Connecting..."
The server is still parsing the TTL file. Check the terminal for progress:
- `nwd4op-12.ttl` (2MB): ~10 seconds
- `navis-via-csv.ttl` (16MB): ~2 minutes
- `navis-via-csv-v3.ttl` (131MB): ~5 minutes

Wait for `Application startup complete` message.

### Empty data in dashboard tabs
- Check the **Overview tab** to verify which file is loaded
- CSV-based files (`navis-via-csv*.ttl`) have Navisworks hierarchy data
- IFC-based files (`nwd4op-12.ttl`) have Building hierarchy data
- **Buildings tab** only works with IFC-based files
- **Hierarchy tab Navisworks tree** only works with CSV-based files

### SPARQL query is slow
- Always use `LIMIT` (e.g., `LIMIT 50`)
- Avoid `navis:hasParent*` on large subtrees (>5000 descendants)
- Use specific predicates instead of `?s ?p ?o`

### No PropertyValues in aggregation
- PropertyValues are only in `navis-via-csv-v3.ttl` (131MB file)
- The basic `navis-via-csv.ttl` has hierarchy and SP3D properties but not PropertyValue reification

## References

- [ifcOWL (buildingSMART)](https://technical.buildingsmart.org/standards/ifc/ifc-formats/ifcowl/)
- [IFC4 ADD2 Schema](https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL)
- Ontology-based BIM-AMS integration in European Highways (2024)
- Multi-ontology fusion and rule development for automated code compliance checking (2022)
