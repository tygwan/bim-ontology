# BIM Ontology Dashboard - User Guide

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Start the server (use the data file you want)
BIM_RDF_PATH=data/rdf/navis-via-csv.ttl uv run uvicorn src.api.server:app --host 0.0.0.0 --port 8000

# 3. Open browser
http://localhost:8000
```

### Data Files

| File | Size | Triples | Description |
|------|------|---------|-------------|
| `navis-via-csv.ttl` | 16MB | 282,704 | Navisworks CSV export (hierarchy + SP3D properties) |
| `navis-via-csv-v3.ttl` | 131MB | 2,800,000+ | Full version with 414K PropertyValue reified data |
| `nwd4op-12.ttl` | 2MB | ~25,000 | IFC-based export (small, fast loading) |
| `navis-via-ifc.ttl` | 2MB | ~25,000 | IFC via Navisworks (legacy) |

> **Note**: `navis-via-csv-v3.ttl` takes 2-3 minutes to load but contains the richest data including all PropertyValues. Start with `navis-via-csv.ttl` for faster iteration.

---

## Tab Guide

### 1. Overview

**Purpose**: Dashboard home. Shows summary statistics and category distribution charts.

**How to use**:
1. The **Data Source** selector at the top lets you switch between TTL files
2. Click **Load** to reload the graph from a different file (this affects ALL tabs)
3. Stats cards show:
   - **Total Triples**: Raw count of all RDF statements
   - **Objects**: BIM elements (physical objects like pipes, structures)
   - **Property Values**: Literal values from PropertySets (v3 file only)
   - **Categories**: Distinct bim:hasCategory labels (e.g., Structure, PipeFitting, Valve)
   - **Max Depth**: Deepest hierarchy level from Navisworks CSV
4. **Category Distribution** (pie chart) and **Top Categories** (bar chart) show element breakdown

**When to use**: Start here to verify which data file is loaded and get a quick overview.

---

### 2. Buildings

**Purpose**: Browse IFC building hierarchy (Project > Site > Building > Storey > Space).

**How to use**:
1. Click nodes in the **Building Hierarchy** tree on the left
2. The **Storeys & Elements** panel on the right shows element counts per storey

**When to use**: Only useful when an IFC-based TTL file is loaded (e.g., `nwd4op-12.ttl`). With CSV-based files, this tab will show limited data since the IFC building structure is not present.

---

### 3. Hierarchy

**Purpose**: Explore the BIM hierarchy from two perspectives: System Path (logical) and Navisworks ParentId (physical).

**Components**:

#### RDF Data Source (top)
- Switch between TTL files and click **Load File** to reload

#### Data Comparison (top-left)
- Shows type counts: Projects, Areas, Units, Systems, Elements
- Compares Navisworks data vs IFC export

#### CSV Level Distribution (top-center)
- Bar chart showing how many elements exist at each original CSV hierarchy depth
- Helps understand the data distribution

#### System Path Tree (top-right)
- Collapsible tree view of `sp3d:hasSystemPath` hierarchy
- Click **Load** to build the tree (select depth first)
- Click a node to expand/collapse and see its children
- Click any node to view its **Hierarchy Details** (bottom panel)

#### Navisworks Hierarchy Tree (Miller Columns)
- **This is the main hierarchy explorer**
- Uses `navis:hasParent` relationships (ParentId from CSV)
- **Miller Columns UI**: click a node to see its children in the next column
- Breadcrumb at top shows your current path
- Buttons:
  - **Reset**: Go back to root
  - **Show Graph**: Toggle canvas-based graph visualization
  - **Depth selector + Load**: Set max depth and load the tree

**How to drill down**:
1. Click **Load** to load the hierarchy
2. Click a root node (e.g., "For Review.nwd") - children appear in the next column
3. Click a child (e.g., "TRAINING") - its children appear in the next column
4. Continue drilling deeper - columns scroll horizontally
5. Each selection shows **Property Summary** (aggregation panel below) and **Hierarchy Details** (bottom)

#### Property Summary (appears when a node is selected)
- **Subtree Breakdown**: Category distribution of all descendant elements
- **Status Distribution**: Status values (Working, Approved, etc.)
- **Property Values**: (v3 file only) Reified PropertyValue aggregation by category
- Click **Refresh** to re-query

#### Graph View
- Canvas-based graph showing selected node and its direct children
- Useful for visualizing the parent-child structure

#### Hierarchy Details (bottom)
- Shows children table with Name, Level, Category, Direct children count, Total descendants
- Helps understand what's inside a selected hierarchy node

**When to use**: This is the primary exploration tab. Use it to understand the BIM hierarchy structure, find areas/units/systems, and aggregate property values per region.

---

### 4. Elements

**Purpose**: Browse individual BIM elements with filtering.

**How to use**:
1. Select a **category** from the dropdown to filter (e.g., Structure, PipeFitting)
2. Type a **name** in the search box
3. Click **Search** to apply filters
4. Use **Prev/Next** to paginate through results (50 per page)

**Columns**: Name, Category, Original Type, Global ID

**When to use**: When you need to find specific elements by name or category.

---

### 5. SPARQL

**Purpose**: Run custom SPARQL queries against the loaded RDF graph.

**How to use**:
1. Write or edit a SPARQL query in the editor (prefixes are pre-filled)
2. Click **Execute** to run
3. Results appear as a table below
4. Use **Query Templates** on the right panel for quick-start queries

**Tips**:
- Always use `LIMIT` for large result sets
- Use `OPTIONAL` for predicates that may not exist on all nodes
- Common prefixes: `bim:`, `navis:`, `sp3d:`, `prop:`, `rdfs:`

**When to use**: When you need custom data analysis beyond what other tabs provide.

---

### 6. Properties

**Purpose**: Look up PropertySets for individual elements.

**How to use**:
1. **Property Lookup**: Enter a GlobalId and click **Lookup** to see all PropertySets
2. **Property Search**: Enter a property key name (e.g., "Weight", "DryWeight") and click **Search** to find elements containing that property
3. **Smart3D Plant Data Summary**: Automatic summary of SP3D-specific properties

**When to use**: When investigating properties of a specific element, or searching for elements by property values.

---

### 7. Ontology

**Purpose**: Manage the ontology schema - create types, relations, and classification rules.

**How to use**:
1. **Object Types**: View existing classes. Click **+ New Type** to create
2. **Link Types**: View existing relations. Click **+ New Link** to create
3. **Classification Rules**: Edit JSON-based rules for auto-categorization
4. **Schema Import/Export**: Save or load schema as JSON. Click **Apply to Graph** to update the RDF graph

**When to use**: When extending the ontology with new types or relationships.

---

### 8. Reasoning

**Purpose**: Run OWL/RDFS inference and custom SPARQL CONSTRUCT rules.

**How to use**:
1. Click **Run Reasoning** to apply inference rules
2. Results show before/after triple counts (how many new triples were inferred)

**When to use**: After loading new data or modifying the ontology, to infer implicit relationships.

---

### 9. Validation

**Purpose**: Quality check the loaded RDF data.

**How to use**:
1. Select a **TTL File** (or use the currently loaded graph)
2. Click **Run Validation**
3. Summary cards show PASS/WARN/FAIL counts
4. Use **filter chips** to show/hide check categories
5. Click any check card to expand and see details
6. **Other Category Explorer** (bottom): Investigate IfcBuildingElementProxy elements

**When to use**: After data conversion to verify quality, or when investigating data issues.

---

### 10. Explorer

**Purpose**: Generic RDF node browser - explore ANY node type with custom column selection.

**How to use**:
1. Select a **TTL File** to explore (or use current)
2. Browse **Node Types** on the left (e.g., navis:SP3DEntity, navis:Area, prop:PropertyValue)
3. Click a type to see available **predicates** (columns)
4. Check the predicates you want as columns
5. Optionally type a search term
6. Click **Load** to see results
7. Click any row to see **full triples** for that node

**When to use**: When you want to explore data that doesn't fit other tabs - especially useful for investigating new data or debugging.

---

### 11. Lean Layer

**Purpose**: Inject schedule/AWP/status/equipment CSV data into the graph.

**How to use**:
1. Select **Injection Type**: Schedule, AWP, Status, or Equipment
2. Choose a **CSV file** from your computer
3. Click **Inject CSV** to load the data into the RDF graph
4. Stats cards update: Tasks, IWPs, Statuses, Equipment
5. **Lean Layer Summary** shows the injected data summary

**When to use**: When you have additional CSV data (schedules, work packages, status updates) to integrate with the BIM data.

---

### 12. Today's Work

**Purpose**: View work packages and elements scheduled for a specific date.

**How to use**:
1. Select a **Target Date** using the date picker
2. Click **Load**
3. Summary shows Active IWPs, Total Elements, Executable count
4. Table lists work packages for that day

**Prerequisite**: Lean Layer data (schedule) must be injected first.

**When to use**: Daily work planning - see what's scheduled for today or any date.

---

### 13. Status Monitor

**Purpose**: Track delayed elements and update element statuses.

**How to use**:
1. **Delayed Elements**: Select a reference date and click **Check** to find elements with past-due planned dates
2. **Delivery Status Distribution**: See the current status breakdown chart
3. **Element Status Update**: Enter a GlobalId and select a new status to update

**Prerequisite**: Status data must be in the graph (via Lean Layer or original data).

**When to use**: Monitoring construction progress and tracking delays.

---

## Common Workflows

### Workflow 1: First-time Data Exploration
1. **Overview** - Load `navis-via-csv.ttl`, check stats
2. **Hierarchy** - Load the Navisworks tree, drill down to understand the structure
3. **Elements** - Browse by category
4. **Explorer** - Deep-dive into specific node types

### Workflow 2: Property Investigation
1. **Hierarchy** - Navigate to a specific area/unit
2. Check the **Property Summary** aggregation panel
3. **Properties** tab - Lookup specific elements by GlobalId
4. **SPARQL** - Write custom queries for specific property patterns

### Workflow 3: Quality Assurance
1. **Validation** - Run checks on the TTL file
2. Review WARN and FAIL items
3. **Explorer** - Investigate problematic nodes
4. **Ontology** - Update classification rules if needed

### Workflow 4: Construction Management (requires Lean Layer data)
1. **Lean Layer** - Inject schedule and status CSVs
2. **Today's Work** - Check daily work packages
3. **Status Monitor** - Track delays and update statuses

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server won't start | Check `uv sync` completed, port 8000 is free |
| Page keeps loading | The TTL file is large; wait for server to finish parsing |
| Empty data in tabs | Verify the correct TTL file is loaded (check Overview tab) |
| Hierarchy tree empty | Select appropriate depth and click Load |
| No PropertyValues | Use `navis-via-csv-v3.ttl` (131MB file with full property data) |
| SPARQL timeout | Add `LIMIT`, avoid `hasParent*` on large subtrees |
| Buildings tab empty | Only works with IFC-based TTL files, not CSV-based |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BIM_RDF_PATH` | `data/rdf/navis-via-csv-v3.ttl` | TTL file to load on startup |
| `BIM_IFC_PATH` | `references/nwd4op-12.ifc` | IFC file for conversion |
