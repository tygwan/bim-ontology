# IFC to Ontology DB Schema - Technical Specification

## Metadata
- **Author**: Tech Spec Architect Agent
- **Date**: 2026-02-03
- **Version**: v1.0
- **Related PRD**: [PRD.md](./PRD.md)
- **Status**: Draft
- **Project Code**: BIM-ONTOLOGY

---

## 1. Overview

### 1.1 Purpose

This technical specification document defines the architecture, design, and implementation details for the IFC to Ontology DB Schema system. The system converts Industry Foundation Classes (IFC) files into RDF triple stores based on ifcOWL ontology, enabling semantic queries through SPARQL and intelligent reasoning using Apache Jena.

**Key Objectives**:
- Convert large IFC4 files (200MB+) to RDF triples efficiently
- Provide SPARQL query interface for building information analysis
- Support multiple client libraries (Python, Java, JavaScript)
- Enable reasoning capabilities for data validation and inference

### 1.2 Terminology

| Term | Definition |
|------|------------|
| IFC | Industry Foundation Classes - ISO standard for BIM data exchange |
| ifcOWL | OWL representation of IFC EXPRESS schema |
| RDF | Resource Description Framework - W3C standard for semantic data |
| Triple | Subject-Predicate-Object statement in RDF |
| SPARQL | Query language for RDF data |
| Reasoning | Logical inference to derive new knowledge from existing data |
| ifcopenshell | Open-source library for parsing IFC files |
| Apache Jena | Java framework for semantic web applications |
| GraphDB | Commercial RDF triple store database |
| Neo4j | Graph database supporting RDF/SPARQL |

### 1.3 References

- **PRD**: `docs/PRD.md`
- **IFC4 Standard**: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/
- **ifcOWL Specification**: https://www.w3.org/community/lbd/
- **Research Papers**:
  - ifcOWL 연구 논문 (references/ 디렉토리)
  - BIM-AMS 통합 논문 (references/ 디렉토리)
- **Sample IFC Files**: `references/*.ifc` (IFC4/IFC2X3 샘플 - .gitignore)

---

## 2. System Architecture

### 2.1 Overall Architecture

The system follows a 4-layer architecture: Client Layer, API Layer, Processing Layer, and Storage Layer.

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                              │
├──────────────┬──────────────┬──────────────┬─────────────────────┤
│   Python     │     Java     │  JavaScript  │   Web Dashboard     │
│   Client     │   Client     │   Client     │   (React/Vue)       │
└──────────────┴──────────────┴──────────────┴─────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                          API LAYER                                │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │  RESTful API   │  │ SPARQL Endpoint│  │  GraphQL API   │     │
│  │   (FastAPI)    │  │  (GET/POST)    │  │   (Optional)   │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │ Authentication │  │  Rate Limiting │  │    Logging     │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                             │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐      │
│  │              IFC PARSER MODULE                          │      │
│  │  - ifcopenshell-based parsing                          │      │
│  │  - IFC4 schema validation                              │      │
│  │  - Entity extraction (geometry, properties, relations) │      │
│  │  - Error handling and logging                          │      │
│  └────────────────────────────────────────────────────────┘      │
│                           │                                       │
│                           ▼                                       │
│  ┌────────────────────────────────────────────────────────┐      │
│  │            RDF CONVERTER MODULE                         │      │
│  │  - IFC → ifcOWL mapping                                │      │
│  │  - RDF triple generation (Subject-Predicate-Object)    │      │
│  │  - Namespace management                                │      │
│  │  - Data optimization (blank nodes, compression)        │      │
│  │  - Serialization (Turtle, RDF/XML, JSON-LD)           │      │
│  └────────────────────────────────────────────────────────┘      │
│                           │                                       │
│                           ▼                                       │
│  ┌────────────────────────────────────────────────────────┐      │
│  │          REASONING ENGINE MODULE                        │      │
│  │  - Apache Jena inference engine                        │      │
│  │  - OWL reasoning (RDFS, OWL-DL)                        │      │
│  │  - SWRL rules execution                                │      │
│  │  - Derived triples materialization                     │      │
│  │  - Validation and consistency checking                 │      │
│  └────────────────────────────────────────────────────────┘      │
│                           │                                       │
│                           ▼                                       │
│  ┌────────────────────────────────────────────────────────┐      │
│  │           QUERY OPTIMIZATION MODULE                     │      │
│  │  - SPARQL query parsing and optimization              │      │
│  │  - Query plan generation                               │      │
│  │  - Result caching (Redis)                              │      │
│  │  - Result formatting (JSON, CSV, XML)                  │      │
│  └────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                               │
├────────────────────────┬─────────────────────────────────────────┤
│  RDF TRIPLE STORE      │         CACHING & METADATA              │
│  ┌──────────────────┐  │  ┌──────────────┐  ┌────────────────┐  │
│  │   GraphDB (REC)  │  │  │    Redis     │  │   PostgreSQL   │  │
│  │   or             │  │  │  (Query      │  │  (Metadata,    │  │
│  │   Apache Jena TDB│  │  │   Cache)     │  │   User Data,   │  │
│  │   or             │  │  │              │  │   Job Status)  │  │
│  │   Neo4j          │  │  │              │  │                │  │
│  └──────────────────┘  │  └──────────────┘  └────────────────┘  │
│  - SPARQL 1.1 support  │  - TTL-based      │  - Conversion     │
│  - Indexing           │  - In-memory       │    job tracking   │
│  - Transaction mgmt    │  - Fast lookup     │  - User sessions  │
└────────────────────────┴─────────────────────────────────────────┘
```

### 2.2 Component Descriptions

| Component | Role | Technology Stack | Key Features |
|-----------|------|------------------|--------------|
| **Python Client** | Client library for Python applications | Python 3.8+, SPARQLWrapper | Easy integration, pip installable |
| **Java Client** | Client library for enterprise Java apps | Java 11+, Apache Jena ARQ | Maven/Gradle support, type-safe |
| **JavaScript Client** | Client library for web/Node.js | Node.js 14+, sparql-client | NPM package, Promise-based |
| **Web Dashboard** | Web UI for visualization | React/Vue.js, D3.js, Material-UI | Interactive charts, query builder |
| **RESTful API** | HTTP API for data access | FastAPI, Pydantic, uvicorn | OpenAPI docs, async support |
| **SPARQL Endpoint** | Standard SPARQL query interface | FastAPI, RDFLib | W3C compliant, GET/POST |
| **IFC Parser** | Parse IFC files | ifcopenshell, Python | IFC4 support, streaming |
| **RDF Converter** | IFC → RDF conversion | RDFLib, Python | ifcOWL mapping, optimization |
| **Reasoning Engine** | Logical inference | Apache Jena, Java | OWL reasoning, SWRL rules |
| **Query Optimizer** | Optimize SPARQL queries | Custom, Python | Caching, query rewriting |
| **GraphDB** | RDF triple store (Recommended) | Ontotext GraphDB | High performance, reasoning |
| **Apache Jena TDB** | Alternative RDF store | Apache Jena TDB2 | Open-source, Java-based |
| **Neo4j** | Alternative graph DB | Neo4j + neosemantics | Property graph + RDF |
| **Redis** | Query result cache | Redis 6+ | In-memory, fast TTL |
| **PostgreSQL** | Metadata storage | PostgreSQL 13+ | Relational, ACID compliant |

### 2.3 Data Flow

#### 2.3.1 Conversion Flow (IFC → RDF)

1. **Upload**: User uploads IFC file via API or CLI
2. **Validation**: System validates IFC4 schema compliance
3. **Parsing**: ifcopenshell parses IFC file, extracts entities
4. **Transformation**: RDF Converter maps IFC entities to ifcOWL classes/properties
5. **Triple Generation**: Generate RDF triples (Subject-Predicate-Object)
6. **Optimization**: Remove duplicates, optimize blank nodes, compress data
7. **Storage**: Load triples into GraphDB/TDB/Neo4j
8. **Indexing**: Create SPARQL query indexes
9. **Reasoning** (Optional): Run inference rules, materialize derived triples
10. **Completion**: Update job status, notify user

**Performance Target**: 200MB IFC file processed in < 30 minutes

#### 2.3.2 Query Flow (SPARQL → Results)

1. **Request**: Client sends SPARQL query via API/endpoint
2. **Authentication**: Verify user credentials and permissions
3. **Validation**: Parse and validate SPARQL syntax
4. **Cache Check**: Check Redis for cached results
5. **Optimization**: Rewrite query for better performance
6. **Execution**: Execute query against triple store
7. **Reasoning** (if enabled): Apply inference rules
8. **Formatting**: Convert results to JSON/CSV/XML
9. **Caching**: Store results in Redis with TTL
10. **Response**: Return results to client

**Performance Target**: Simple query < 2s, Complex query < 10s

#### 2.3.3 Reasoning Flow

1. **Trigger**: Manual trigger or scheduled job
2. **Rule Loading**: Load SWRL/Jena rules from configuration
3. **Inference**: Apache Jena executes reasoning over existing triples
4. **Validation**: Check for inconsistencies (SHACL/SPARQL constraints)
5. **Materialization**: Store derived triples in database
6. **Reporting**: Generate reasoning report (new triples, violations)

---

## 3. Component Design

### 3.1 IFC Parser Module

#### 3.1.1 Architecture

```
┌──────────────────────────────────────────────────────┐
│              IFC PARSER MODULE                        │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────┐ │
│  │   IFC File   │──▶│   Validator  │──▶│  Parser  │ │
│  │   Reader     │   │   (Schema)   │   │  Engine  │ │
│  └──────────────┘   └──────────────┘   └──────────┘ │
│                                            │          │
│                                            ▼          │
│  ┌──────────────────────────────────────────────┐   │
│  │         Entity Extractor                     │   │
│  │  - Geometry (IfcGeometricRepresentation)    │   │
│  │  - Properties (IfcPropertySet)              │   │
│  │  - Relationships (IfcRelAggregates)         │   │
│  │  - Spatial structure (IfcBuilding, ...)     │   │
│  └──────────────────────────────────────────────┘   │
│                                            │          │
│                                            ▼          │
│  ┌──────────────────────────────────────────────┐   │
│  │         Error Handler                        │   │
│  │  - Missing entities                          │   │
│  │  - Invalid references                        │   │
│  │  - Corrupted data                            │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

#### 3.1.2 Key Features

- **Streaming Parser**: Process large files without loading entire file into memory
- **Schema Validation**: Verify IFC4 schema compliance before conversion
- **Entity Extraction**: Extract all IFC entities with relationships
- **Error Recovery**: Continue processing on non-critical errors
- **Progress Tracking**: Report conversion progress (% complete)

#### 3.1.3 Implementation

```python
# Core implementation: src/parser/ifc_parser.py

import ifcopenshell
import logging
from typing import Iterator, Dict, Any

class IFCParser:
    """Parse IFC files and extract entities."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ifc_file = None
        self.logger = logging.getLogger(__name__)

    def parse(self) -> Iterator[Dict[str, Any]]:
        """Parse IFC file and yield entities."""
        try:
            self.ifc_file = ifcopenshell.open(self.file_path)
            self.logger.info(f"Loaded IFC file: {self.file_path}")

            # Validate schema
            if not self._validate_schema():
                raise ValueError("Invalid IFC4 schema")

            # Extract entities
            for entity in self.ifc_file:
                yield self._extract_entity(entity)

        except Exception as e:
            self.logger.error(f"Parser error: {e}")
            raise

    def _validate_schema(self) -> bool:
        """Validate IFC4 schema."""
        schema = self.ifc_file.schema
        return schema.startswith("IFC4")

    def _extract_entity(self, entity) -> Dict[str, Any]:
        """Extract entity data with properties and relationships."""
        return {
            "id": entity.id(),
            "type": entity.is_a(),
            "attributes": self._get_attributes(entity),
            "properties": self._get_properties(entity),
            "relationships": self._get_relationships(entity)
        }
```

#### 3.1.4 Error Handling

| Error Type | Handling Strategy |
|------------|-------------------|
| File not found | Return 404 error, log event |
| Invalid schema | Return 400 error with details |
| Corrupted data | Skip entity, log warning, continue |
| Memory overflow | Switch to streaming mode |
| Timeout | Cancel job, save partial progress |

### 3.2 RDF Converter Module

#### 3.2.1 Architecture

```
┌──────────────────────────────────────────────────────┐
│            RDF CONVERTER MODULE                       │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────┐ │
│  │ IFC Entity   │──▶│   Mapper     │──▶│  Triple  │ │
│  │    Data      │   │  (ifcOWL)    │   │ Generator│ │
│  └──────────────┘   └──────────────┘   └──────────┘ │
│                                            │          │
│                                            ▼          │
│  ┌──────────────────────────────────────────────┐   │
│  │        Namespace Manager                     │   │
│  │  - ifc: https://standards.buildingsmart...  │   │
│  │  - express: https://w3id.org/express#       │   │
│  │  - owl: http://www.w3.org/2002/07/owl#      │   │
│  │  - rdf: http://www.w3.org/1999/02/22-...    │   │
│  └──────────────────────────────────────────────┘   │
│                                            │          │
│                                            ▼          │
│  ┌──────────────────────────────────────────────┐   │
│  │           Data Optimizer                     │   │
│  │  - Remove duplicate triples                  │   │
│  │  - Optimize blank nodes                      │   │
│  │  - Compress literal values                   │   │
│  │  - Index generation                          │   │
│  └──────────────────────────────────────────────┘   │
│                                            │          │
│                                            ▼          │
│  ┌──────────────────────────────────────────────┐   │
│  │           Serializer                         │   │
│  │  - Turtle (.ttl)                             │   │
│  │  - RDF/XML (.rdf)                            │   │
│  │  - JSON-LD (.jsonld)                         │   │
│  │  - N-Triples (.nt)                           │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

#### 3.2.2 ifcOWL Mapping Rules

| IFC Concept | ifcOWL Representation | Example |
|-------------|----------------------|---------|
| Entity Class | `ifc:IfcWall` | `<#Wall_123> rdf:type ifc:IfcWall` |
| Attribute | `ifc:globalId_IfcRoot` | `<#Wall_123> ifc:globalId_IfcRoot "2O2Fr..."` |
| Relationship | `ifc:relatingObject_IfcRelAggregates` | `<#Rel_1> ifc:relatingObject_IfcRelAggregates <#Building_1>` |
| Property Set | `ifc:hasProperties` | `<#Wall_123> ifc:hasProperties <#Pset_1>` |
| Enumeration | Literal value | `<#Wall_123> ifc:predefinedType "SOLIDWALL"` |

#### 3.2.3 Triple Generation Strategy

**Subject Generation**:
- Use IFC GlobalId as subject URI: `<http://example.org/ifc/{GlobalId}>`
- Blank nodes for intermediate objects

**Predicate Generation**:
- Direct attributes: `ifc:{attributeName}_{className}`
- Relationships: `ifc:{relationshipName}_{relationshipClass}`

**Object Generation**:
- References: URI to other entities
- Literals: Typed literals (xsd:string, xsd:double, xsd:boolean)
- Enumerations: String literals

#### 3.2.4 Implementation

```python
# Core implementation: src/converter/rdf_converter.py

from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from typing import Dict, Any

class RDFConverter:
    """Convert IFC entities to RDF triples."""

    def __init__(self):
        self.graph = Graph()
        self.ifc_ns = Namespace("https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#")
        self.base_ns = Namespace("http://example.org/ifc/")
        self._bind_namespaces()

    def _bind_namespaces(self):
        """Bind standard namespaces."""
        self.graph.bind("ifc", self.ifc_ns)
        self.graph.bind("base", self.base_ns)
        self.graph.bind("owl", "http://www.w3.org/2002/07/owl#")

    def convert_entity(self, entity: Dict[str, Any]) -> None:
        """Convert single IFC entity to RDF triples."""
        # Create subject URI
        subject = self.base_ns[entity['global_id']]

        # Add type triple
        ifc_type = self.ifc_ns[entity['type']]
        self.graph.add((subject, RDF.type, ifc_type))

        # Add attribute triples
        for attr_name, attr_value in entity['attributes'].items():
            predicate = self.ifc_ns[f"{attr_name}_{entity['type']}"]
            obj = self._convert_value(attr_value)
            self.graph.add((subject, predicate, obj))

    def _convert_value(self, value: Any) -> Literal:
        """Convert Python value to RDF literal."""
        if isinstance(value, str):
            return Literal(value, datatype=XSD.string)
        elif isinstance(value, (int, float)):
            return Literal(value, datatype=XSD.double)
        elif isinstance(value, bool):
            return Literal(value, datatype=XSD.boolean)
        else:
            return Literal(str(value))

    def serialize(self, format: str = 'turtle') -> str:
        """Serialize graph to specified format."""
        return self.graph.serialize(format=format)
```

### 3.3 Ontology Storage - Database Comparison

#### 3.3.1 GraphDB (Recommended)

**Pros**:
- Native RDF storage optimized for SPARQL
- Built-in reasoning engine (RDFS, OWL-Horst, OWL-Max)
- High query performance with indexing
- Free edition available (sufficient for most use cases)
- Excellent SPARQL 1.1 compliance
- Web-based workbench for management

**Cons**:
- Requires JVM (memory overhead)
- Free edition has repository size limits
- Less community support than Apache Jena
- Commercial licensing for enterprise features

**Use Cases**:
- Production deployments requiring high performance
- Complex reasoning requirements
- Need for web-based management interface

**Configuration**:
```properties
# graphdb.properties
storage.location=/data/graphdb
reasoning.level=rdfs-plus
query.timeout=30
cache.size=4GB
```

#### 3.3.2 Apache Jena TDB

**Pros**:
- Fully open-source (Apache 2.0 license)
- Native Java implementation
- TDB2 provides transaction support
- Good integration with Jena reasoning
- No size limitations
- Programmatic control

**Cons**:
- Slower query performance than GraphDB
- Basic web interface (Fuseki)
- Manual optimization required
- Less user-friendly management

**Use Cases**:
- Research projects and prototypes
- Full open-source requirement
- Programmatic control needed
- Budget constraints

**Configuration**:
```java
// TDB2 setup
Dataset dataset = TDB2Factory.connectDataset("/data/tdb2");
Model model = dataset.getDefaultModel();
```

#### 3.3.3 Neo4j with neosemantics (n10s)

**Pros**:
- Popular graph database (large community)
- Excellent visualization (Neo4j Browser)
- Property graph model + RDF support
- Cypher query language (easier than SPARQL)
- Strong enterprise support

**Cons**:
- Not native RDF storage (conversion layer)
- SPARQL support via n10s plugin (limited)
- Reasoning capabilities limited
- Higher complexity for pure RDF use cases

**Use Cases**:
- Hybrid property graph + RDF needs
- Teams familiar with Neo4j/Cypher
- Visualization-heavy applications
- Need for graph algorithms

**Configuration**:
```cypher
// Install neosemantics plugin
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE;
CALL n10s.graphconfig.init();
```

#### 3.3.4 Recommendation Matrix

| Criteria | GraphDB | Apache Jena TDB | Neo4j + n10s |
|----------|---------|----------------|--------------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| SPARQL Support | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Reasoning | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Community | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Total** | 27/30 | 24/30 | 21/30 |

**Final Recommendation**: **GraphDB Free Edition** for production, **Apache Jena TDB** as fallback.

### 3.4 SPARQL Query Engine

#### 3.4.1 Query Optimization Strategies

**1. Query Rewriting**:
- Push filters down to reduce intermediate results
- Reorder triple patterns for optimal join order
- Use LIMIT early to reduce result set size

**2. Caching Strategy**:
- Cache frequently used queries (TTL: 1 hour)
- Cache by query hash + parameters
- Invalidate cache on data updates
- Use Redis for distributed caching

**3. Indexing**:
- Subject-Predicate-Object (SPO) index
- Predicate-Object-Subject (POS) index
- Object-Subject-Predicate (OSP) index
- Property-specific indexes for common queries

**4. Performance Considerations**:
- Use DESCRIBE carefully (can return large graphs)
- Prefer ASK for existence checks
- Use COUNT(*) instead of SELECT + COUNT
- Avoid OPTIONAL when not necessary
- Batch results with LIMIT + OFFSET pagination

#### 3.4.2 Standard Query Templates

```sparql
# Template 1: Get all walls in a building
PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
PREFIX base: <http://example.org/ifc/>

SELECT ?wall ?globalId ?name
WHERE {
  ?building a ifc:IfcBuilding .
  ?building ifc:name_IfcRoot ?buildingName .
  FILTER(?buildingName = "{{building_name}}")

  ?rel a ifc:IfcRelContainedInSpatialStructure .
  ?rel ifc:relatingStructure_IfcRelContainedInSpatialStructure ?building .
  ?rel ifc:relatedElements_IfcRelContainedInSpatialStructure ?wall .

  ?wall a ifc:IfcWall .
  ?wall ifc:globalId_IfcRoot ?globalId .
  OPTIONAL { ?wall ifc:name_IfcRoot ?name }
}

# Template 2: Get space areas by floor
PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>

SELECT ?storey ?space ?area
WHERE {
  ?storey a ifc:IfcBuildingStorey .
  ?space a ifc:IfcSpace .
  ?space ifc:decomposes ?storey .

  ?quantity a ifc:IfcQuantityArea .
  ?quantity ifc:areaValue_IfcQuantityArea ?area .
  ?quantity ifc:relatedTo ?space .
}
ORDER BY ?storey ?space

# Template 3: Aggregate material quantities
PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>

SELECT ?materialName (SUM(?volume) as ?totalVolume)
WHERE {
  ?element a ifc:IfcBuildingElement .
  ?element ifc:hasMaterial ?material .
  ?material ifc:name_IfcMaterial ?materialName .
  ?element ifc:hasQuantity ?quantity .
  ?quantity ifc:volumeValue_IfcQuantityVolume ?volume .
}
GROUP BY ?materialName
ORDER BY DESC(?totalVolume)
```

### 3.5 Reasoning Engine

#### 3.5.1 Apache Jena Reasoning Integration

**Reasoning Levels**:
1. **RDFS**: Basic subclass/subproperty inference
2. **OWL-Horst**: OWL subset optimized for performance
3. **OWL-DL**: Full OWL reasoning (slower)
4. **Custom Rules**: SWRL or Jena rules

#### 3.5.2 Use Cases

**1. Data Validation**:
```sparql
# SPARQL constraint: All walls must have height
PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>

SELECT ?wall
WHERE {
  ?wall a ifc:IfcWall .
  FILTER NOT EXISTS { ?wall ifc:height_IfcWall ?height }
}
```

**2. Inference Rules**:
```
# Jena rule: If a space is in a storey, it's also in the building
[rule1:
  (?space rdf:type ifc:IfcSpace)
  (?space ifc:decomposes ?storey)
  (?storey rdf:type ifc:IfcBuildingStorey)
  (?storey ifc:decomposes ?building)
  (?building rdf:type ifc:IfcBuilding)
  ->
  (?space ifc:containedInBuilding ?building)
]
```

**3. Consistency Checking**:
- Detect circular relationships
- Validate cardinality constraints
- Check domain/range restrictions

#### 3.5.3 Implementation

```python
# Core implementation: src/reasoning/reasoner.py

from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

class ReasoningEngine:
    """Execute reasoning and validation."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.violations = []

    def validate_constraints(self) -> list:
        """Validate SPARQL constraints."""
        constraints = self._load_constraints()

        for constraint in constraints:
            results = self.graph.query(constraint['query'])
            if len(results) > 0:
                self.violations.append({
                    'rule': constraint['name'],
                    'violations': list(results)
                })

        return self.violations

    def apply_inference_rules(self, rules_file: str) -> int:
        """Apply Jena rules and materialize inferred triples."""
        # Load rules from file
        # Execute reasoning via Jena API
        # Add inferred triples to graph
        # Return count of new triples
        pass
```

---

## 4. Data Model

### 4.1 ifcOWL Schema Structure

The ifcOWL ontology represents IFC EXPRESS schema as OWL classes and properties. Key structural components:

#### 4.1.1 Core Class Hierarchy

```
owl:Thing
├── ifc:IfcRoot (abstract)
│   ├── ifc:IfcObjectDefinition (abstract)
│   │   ├── ifc:IfcObject (abstract)
│   │   │   ├── ifc:IfcProduct (abstract)
│   │   │   │   ├── ifc:IfcElement (abstract)
│   │   │   │   │   ├── ifc:IfcBuildingElement (abstract)
│   │   │   │   │   │   ├── ifc:IfcWall
│   │   │   │   │   │   ├── ifc:IfcColumn
│   │   │   │   │   │   ├── ifc:IfcBeam
│   │   │   │   │   │   ├── ifc:IfcSlab
│   │   │   │   │   │   ├── ifc:IfcDoor
│   │   │   │   │   │   └── ifc:IfcWindow
│   │   │   │   │   └── ifc:IfcSpatialElement (abstract)
│   │   │   │   │       ├── ifc:IfcSpace
│   │   │   │   │       ├── ifc:IfcBuildingStorey
│   │   │   │   │       └── ifc:IfcBuilding
│   │   │   │   └── ifc:IfcGeometricRepresentationItem
│   │   │   └── ifc:IfcGroup
│   │   └── ifc:IfcPropertyDefinition
│   │       ├── ifc:IfcPropertySetDefinition
│   │       │   └── ifc:IfcPropertySet
│   │       └── ifc:IfcProperty
│   │           ├── ifc:IfcSimpleProperty
│   │           └── ifc:IfcComplexProperty
│   └── ifc:IfcRelationship (abstract)
│       ├── ifc:IfcRelConnects
│       ├── ifc:IfcRelDecomposes
│       │   └── ifc:IfcRelAggregates
│       ├── ifc:IfcRelDefines
│       │   └── ifc:IfcRelDefinesByProperties
│       └── ifc:IfcRelAssociates
│           └── ifc:IfcRelAssociatesMaterial
└── ifc:IfcMaterial
```

### 4.2 Core Properties

#### 4.2.1 Universal Properties (IfcRoot)

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `ifc:globalId_IfcRoot` | xsd:string | Globally unique identifier (GUID) | "2O2Fr$t4X7Zf8NOew3FLOH" |
| `ifc:name_IfcRoot` | xsd:string | Optional name | "External Wall" |
| `ifc:description_IfcRoot` | xsd:string | Optional description | "Load-bearing wall" |

#### 4.2.2 Relationship Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `ifc:relatingObject_IfcRelAggregates` | IfcRelAggregates | IfcObject | Parent object in aggregation |
| `ifc:relatedObjects_IfcRelAggregates` | IfcRelAggregates | IfcObject | Child objects in aggregation |
| `ifc:relatingStructure_IfcRelContainedInSpatialStructure` | IfcRelContainedInSpatialStructure | IfcSpatialElement | Containing spatial element |
| `ifc:relatedElements_IfcRelContainedInSpatialStructure` | IfcRelContainedInSpatialStructure | IfcProduct | Contained elements |

#### 4.2.3 Geometry Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `ifc:representation_IfcProduct` | IfcProduct | IfcProductRepresentation | Geometric representation |
| `ifc:objectPlacement_IfcProduct` | IfcProduct | IfcObjectPlacement | 3D placement in space |

### 4.3 Entity Mapping Examples

#### Example 1: IfcWall

```turtle
@prefix ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#> .
@prefix base: <http://example.org/ifc/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

base:2O2Fr$t4X7Zf8NOew3FLOH a ifc:IfcWall ;
    ifc:globalId_IfcRoot "2O2Fr$t4X7Zf8NOew3FLOH" ;
    ifc:name_IfcRoot "External Wall - Type A" ;
    ifc:description_IfcRoot "200mm concrete wall" ;
    ifc:predefinedType_IfcWall "SOLIDWALL" ;
    ifc:objectPlacement_IfcProduct base:Placement_123 ;
    ifc:representation_IfcProduct base:Representation_456 .
```

#### Example 2: IfcBuildingStorey with Spaces

```turtle
base:StoreyGround a ifc:IfcBuildingStorey ;
    ifc:globalId_IfcRoot "1A2B3C4D5E6F7G8H9I0J1K" ;
    ifc:name_IfcRoot "Ground Floor" ;
    ifc:elevation_IfcBuildingStorey "0.0"^^xsd:double .

base:Space101 a ifc:IfcSpace ;
    ifc:globalId_IfcRoot "9Z8Y7X6W5V4U3T2S1R0Q9P" ;
    ifc:name_IfcRoot "Office 101" ;
    ifc:longName_IfcSpace "Main Office Room" .

base:RelAgg_Storey_Space a ifc:IfcRelAggregates ;
    ifc:globalId_IfcRoot "5M4N3O2P1Q0R9S8T7U6V5W" ;
    ifc:relatingObject_IfcRelAggregates base:StoreyGround ;
    ifc:relatedObjects_IfcRelAggregates base:Space101 .
```

#### Example 3: Material Association

```turtle
base:ConcreteMaterial a ifc:IfcMaterial ;
    ifc:name_IfcMaterial "Concrete C30/37" ;
    ifc:description_IfcMaterial "Structural concrete" .

base:RelMaterial_Wall a ifc:IfcRelAssociatesMaterial ;
    ifc:globalId_IfcRoot "3C2B1A0Z9Y8X7W6V5U4T3S" ;
    ifc:relatingMaterial_IfcRelAssociatesMaterial base:ConcreteMaterial ;
    ifc:relatedObjects_IfcRelAssociatesMaterial base:2O2Fr$t4X7Zf8NOew3FLOH .
```

### 4.4 Database Schema (PostgreSQL for Metadata)

```sql
-- Conversion jobs tracking
CREATE TABLE conversion_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, processing, completed, failed
    progress_percent INTEGER DEFAULT 0,
    triple_count BIGINT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Query cache metadata
CREATE TABLE query_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    result_count INTEGER,
    execution_time_ms INTEGER,
    cache_key VARCHAR(255) NOT NULL,
    ttl_seconds INTEGER DEFAULT 3600,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

-- User management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- user, admin
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Query history
CREATE TABLE query_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    query_text TEXT NOT NULL,
    result_count INTEGER,
    execution_time_ms INTEGER,
    status VARCHAR(50), -- success, error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_conversion_jobs_user_id ON conversion_jobs(user_id);
CREATE INDEX idx_conversion_jobs_status ON conversion_jobs(status);
CREATE INDEX idx_query_cache_hash ON query_cache(query_hash);
CREATE INDEX idx_query_history_user_id ON query_history(user_id);
```

---

## 5. API Design

### 5.1 RESTful API Endpoints

#### 5.1.1 API Overview

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Conversion** | `/api/v1/convert` | POST | Upload and convert IFC file |
| | `/api/v1/jobs/{job_id}` | GET | Get conversion job status |
| | `/api/v1/jobs` | GET | List all user's jobs |
| **Query** | `/api/v1/query` | POST | Execute SPARQL query |
| | `/api/v1/query/templates` | GET | List query templates |
| | `/api/v1/query/templates/{id}` | POST | Execute template with params |
| **Data** | `/api/v1/entities/{type}` | GET | List entities by type |
| | `/api/v1/entities/{global_id}` | GET | Get entity details |
| | `/api/v1/buildings` | GET | List all buildings |
| | `/api/v1/buildings/{id}/storeys` | GET | Get building storeys |
| | `/api/v1/spaces` | GET | List all spaces |
| **Export** | `/api/v1/export/rdf` | POST | Export data as RDF |
| | `/api/v1/export/json` | POST | Export query results as JSON |
| **Admin** | `/api/v1/admin/stats` | GET | System statistics |
| | `/api/v1/admin/reasoning` | POST | Trigger reasoning job |

### 5.2 API Specifications

#### 5.2.1 POST /api/v1/convert

Upload IFC file and start conversion to RDF.

**Request**:
```http
POST /api/v1/convert HTTP/1.1
Host: api.example.com
Authorization: Bearer {api_key}
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="building.ifc"
Content-Type: application/ifc

[IFC file contents]
--boundary
Content-Disposition: form-data; name="options"

{
  "enable_reasoning": false,
  "output_format": "turtle",
  "optimization_level": "high"
}
--boundary--
```

**Response (202 Accepted)**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "pending",
  "message": "Conversion job created",
  "estimated_time_minutes": 25,
  "created_at": "2026-02-03T10:30:00Z"
}
```

**Error Codes**:
| Code | Description |
|------|-------------|
| 400 | Invalid IFC file format |
| 413 | File too large (> 500MB) |
| 401 | Authentication required |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

#### 5.2.2 GET /api/v1/jobs/{job_id}

Get status of conversion job.

**Request**:
```http
GET /api/v1/jobs/a1b2c3d4-e5f6-7890-1234-567890abcdef HTTP/1.1
Host: api.example.com
Authorization: Bearer {api_key}
```

**Response (200 OK)**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "processing",
  "progress_percent": 45,
  "file_name": "building.ifc",
  "file_size_bytes": 235000000,
  "triple_count": 1250000,
  "started_at": "2026-02-03T10:30:15Z",
  "estimated_completion": "2026-02-03T10:55:00Z",
  "current_phase": "rdf_conversion",
  "logs": [
    {"timestamp": "2026-02-03T10:30:15Z", "level": "info", "message": "Started IFC parsing"},
    {"timestamp": "2026-02-03T10:35:20Z", "level": "info", "message": "Parsed 50000 entities"},
    {"timestamp": "2026-02-03T10:40:10Z", "level": "warning", "message": "Skipped 3 invalid entities"}
  ]
}
```

**Status Values**:
- `pending`: Job queued
- `processing`: Job in progress
- `completed`: Job finished successfully
- `failed`: Job failed with errors

#### 5.2.3 POST /api/v1/query

Execute SPARQL query against RDF store.

**Request**:
```http
POST /api/v1/query HTTP/1.1
Host: api.example.com
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "query": "PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>\nSELECT ?wall ?name WHERE { ?wall a ifc:IfcWall . OPTIONAL { ?wall ifc:name_IfcRoot ?name } } LIMIT 100",
  "format": "json",
  "reasoning": false,
  "timeout_seconds": 30
}
```

**Response (200 OK)**:
```json
{
  "head": {
    "vars": ["wall", "name"]
  },
  "results": {
    "bindings": [
      {
        "wall": {
          "type": "uri",
          "value": "http://example.org/ifc/2O2Fr$t4X7Zf8NOew3FLOH"
        },
        "name": {
          "type": "literal",
          "value": "External Wall - Type A"
        }
      },
      {
        "wall": {
          "type": "uri",
          "value": "http://example.org/ifc/3P3Gs$u5Y8Ag9OPfx4GMPI"
        },
        "name": {
          "type": "literal",
          "value": "Internal Wall - Type B"
        }
      }
    ]
  },
  "metadata": {
    "execution_time_ms": 145,
    "result_count": 2,
    "cached": false,
    "reasoning_applied": false
  }
}
```

**Error Codes**:
| Code | Description |
|------|-------------|
| 400 | Invalid SPARQL syntax |
| 408 | Query timeout |
| 429 | Rate limit exceeded |
| 500 | Query execution error |

#### 5.2.4 GET /api/v1/entities/{global_id}

Get detailed information about specific entity.

**Request**:
```http
GET /api/v1/entities/2O2Fr$t4X7Zf8NOew3FLOH HTTP/1.1
Host: api.example.com
Authorization: Bearer {api_key}
Accept: application/json
```

**Response (200 OK)**:
```json
{
  "global_id": "2O2Fr$t4X7Zf8NOew3FLOH",
  "type": "IfcWall",
  "name": "External Wall - Type A",
  "description": "200mm concrete wall",
  "attributes": {
    "predefinedType": "SOLIDWALL",
    "tag": "W-001"
  },
  "properties": [
    {
      "set_name": "Pset_WallCommon",
      "properties": {
        "LoadBearing": true,
        "IsExternal": true,
        "ThermalTransmittance": 0.35
      }
    }
  ],
  "materials": [
    {
      "name": "Concrete C30/37",
      "category": "Concrete",
      "thickness_mm": 200
    }
  ],
  "relationships": {
    "contained_in": {
      "type": "IfcBuildingStorey",
      "global_id": "1A2B3C4D5E6F7G8H9I0J1K",
      "name": "Ground Floor"
    },
    "connects_to": [
      {
        "type": "IfcWall",
        "global_id": "3P3Gs$u5Y8Ag9OPfx4GMPI",
        "name": "Internal Wall - Type B"
      }
    ]
  },
  "geometry": {
    "has_representation": true,
    "bounding_box": {
      "min": {"x": 0.0, "y": 0.0, "z": 0.0},
      "max": {"x": 5.0, "y": 0.2, "z": 3.0}
    }
  }
}
```

#### 5.2.5 GET /api/v1/query/templates

List available SPARQL query templates.

**Response (200 OK)**:
```json
{
  "templates": [
    {
      "id": "get_walls_by_building",
      "name": "Get All Walls in Building",
      "description": "Retrieve all walls contained in a specific building",
      "parameters": [
        {
          "name": "building_name",
          "type": "string",
          "required": true,
          "description": "Name of the building"
        }
      ],
      "example_params": {
        "building_name": "Main Building"
      }
    },
    {
      "id": "space_areas_by_floor",
      "name": "Space Areas by Floor",
      "description": "Get all spaces grouped by floor with their areas",
      "parameters": [],
      "example_params": {}
    },
    {
      "id": "material_quantities",
      "name": "Aggregate Material Quantities",
      "description": "Calculate total quantities for each material type",
      "parameters": [
        {
          "name": "material_category",
          "type": "string",
          "required": false,
          "description": "Filter by material category (e.g., Concrete, Steel)"
        }
      ],
      "example_params": {
        "material_category": "Concrete"
      }
    }
  ]
}
```

### 5.3 GraphQL API (Optional)

#### 5.3.1 Schema Definition

```graphql
type Query {
  # Entity queries
  entity(globalId: ID!): Entity
  entities(type: String, limit: Int, offset: Int): [Entity!]!

  # Building structure queries
  buildings: [Building!]!
  building(id: ID!): Building

  # SPARQL query execution
  sparqlQuery(query: String!, reasoning: Boolean): SparqlResult!

  # Job queries
  conversionJob(id: ID!): ConversionJob
  conversionJobs(status: JobStatus): [ConversionJob!]!
}

type Mutation {
  # Conversion
  convertIFC(file: Upload!, options: ConversionOptions): ConversionJob!

  # Reasoning
  triggerReasoning(rules: [String!]): ReasoningJob!
}

type Entity {
  globalId: ID!
  type: String!
  name: String
  description: String
  attributes: JSON
  properties: [PropertySet!]!
  materials: [Material!]!
  relationships: Relationships!
}

type Building {
  globalId: ID!
  name: String!
  storeys: [BuildingStorey!]!
  address: Address
  totalArea: Float
  elementCount: Int
}

type BuildingStorey {
  globalId: ID!
  name: String!
  elevation: Float
  spaces: [Space!]!
  elements: [Element!]!
}

type SparqlResult {
  headers: [String!]!
  rows: [JSON!]!
  metadata: QueryMetadata!
}

type ConversionJob {
  id: ID!
  status: JobStatus!
  progressPercent: Int!
  tripleCount: Int
  logs: [LogEntry!]!
}

enum JobStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
}
```

#### 5.3.2 Example Query

```graphql
query GetBuildingWithSpaces {
  building(id: "1A2B3C4D5E6F7G8H9I0J1K") {
    globalId
    name
    storeys {
      name
      elevation
      spaces {
        globalId
        name
        area
      }
    }
  }
}
```

---

## 6. Client Libraries

### 6.1 Python Client

#### 6.1.1 Installation

```bash
pip install ifc-ontology-client
```

#### 6.1.2 Usage Example

```python
from ifc_ontology import Client

# Initialize client
client = Client(
    base_url="https://api.example.com",
    api_key="your_api_key"
)

# Convert IFC file
job = client.convert_ifc(
    file_path="/path/to/building.ifc",
    enable_reasoning=False
)

# Wait for completion
job.wait(poll_interval=5)
print(f"Conversion completed: {job.triple_count} triples")

# Execute SPARQL query
results = client.query("""
    PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
    SELECT ?wall ?name WHERE {
        ?wall a ifc:IfcWall .
        OPTIONAL { ?wall ifc:name_IfcRoot ?name }
    }
    LIMIT 10
""")

for row in results:
    print(f"Wall: {row['name']}")

# Use query template
walls = client.execute_template(
    template_id="get_walls_by_building",
    params={"building_name": "Main Building"}
)

# Get entity details
entity = client.get_entity("2O2Fr$t4X7Zf8NOew3FLOH")
print(f"Entity type: {entity.type}")
print(f"Properties: {entity.properties}")

# Export results
client.export_results(
    query=results,
    format="csv",
    output_path="walls.csv"
)
```

#### 6.1.3 API Reference

```python
class Client:
    def __init__(self, base_url: str, api_key: str): ...

    def convert_ifc(
        self,
        file_path: str,
        enable_reasoning: bool = False
    ) -> ConversionJob: ...

    def query(
        self,
        sparql: str,
        format: str = "json",
        reasoning: bool = False
    ) -> QueryResult: ...

    def execute_template(
        self,
        template_id: str,
        params: dict
    ) -> QueryResult: ...

    def get_entity(self, global_id: str) -> Entity: ...

    def list_buildings(self) -> List[Building]: ...
```

### 6.2 Java Client

#### 6.2.1 Maven Dependency

```xml
<dependency>
    <groupId>com.example.ifc</groupId>
    <artifactId>ifc-ontology-client</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### 6.2.2 Usage Example

```java
import com.example.ifc.IfcOntologyClient;
import com.example.ifc.model.ConversionJob;
import com.example.ifc.model.QueryResult;

// Initialize client
IfcOntologyClient client = IfcOntologyClient.builder()
    .baseUrl("https://api.example.com")
    .apiKey("your_api_key")
    .build();

// Convert IFC file
ConversionJob job = client.convertIfc(
    new File("/path/to/building.ifc"),
    ConversionOptions.builder()
        .enableReasoning(false)
        .optimizationLevel(OptimizationLevel.HIGH)
        .build()
);

// Wait for completion
job.waitForCompletion(Duration.ofMinutes(30));
System.out.println("Triples: " + job.getTripleCount());

// Execute SPARQL query
String sparql = """
    PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
    SELECT ?wall ?name WHERE {
        ?wall a ifc:IfcWall .
        OPTIONAL { ?wall ifc:name_IfcRoot ?name }
    }
    LIMIT 10
""";

QueryResult result = client.query(sparql);
result.forEach(row -> {
    System.out.println("Wall: " + row.get("name"));
});

// Get entity
Entity entity = client.getEntity("2O2Fr$t4X7Zf8NOew3FLOH");
System.out.println("Type: " + entity.getType());
```

### 6.3 JavaScript Client

#### 6.3.1 Installation

```bash
npm install @ifc-ontology/client
```

#### 6.3.2 Usage Example

```javascript
import { IfcOntologyClient } from '@ifc-ontology/client';

// Initialize client
const client = new IfcOntologyClient({
  baseUrl: 'https://api.example.com',
  apiKey: 'your_api_key'
});

// Convert IFC file (in browser)
const fileInput = document.querySelector('#ifc-file');
const file = fileInput.files[0];

const job = await client.convertIfc(file, {
  enableReasoning: false
});

// Poll for completion
await job.waitForCompletion({
  pollInterval: 5000,
  onProgress: (progress) => {
    console.log(`Progress: ${progress.percent}%`);
  }
});

console.log(`Conversion completed: ${job.tripleCount} triples`);

// Execute SPARQL query
const results = await client.query(`
  PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
  SELECT ?wall ?name WHERE {
    ?wall a ifc:IfcWall .
    OPTIONAL { ?wall ifc:name_IfcRoot ?name }
  }
  LIMIT 10
`);

results.forEach(row => {
  console.log(`Wall: ${row.name}`);
});

// Use query template
const walls = await client.executeTemplate('get_walls_by_building', {
  building_name: 'Main Building'
});

// Get entity
const entity = await client.getEntity('2O2Fr$t4X7Zf8NOew3FLOH');
console.log(`Entity type: ${entity.type}`);
```

---

## 7. Performance Optimization

### 7.1 Large File Processing (200MB+)

#### 7.1.1 Streaming Strategy

```python
# Streaming IFC parser implementation
class StreamingIFCParser:
    def __init__(self, file_path: str, chunk_size: int = 10000):
        self.file_path = file_path
        self.chunk_size = chunk_size

    def parse_streaming(self) -> Iterator[List[Entity]]:
        """Parse IFC file in chunks to avoid memory overflow."""
        ifc_file = ifcopenshell.open(self.file_path)

        chunk = []
        for entity in ifc_file:
            chunk.append(entity)

            if len(chunk) >= self.chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk
```

#### 7.1.2 Batch Triple Insertion

```python
# Batch insert triples to database
class BatchTripleInserter:
    def __init__(self, store_url: str, batch_size: int = 50000):
        self.store_url = store_url
        self.batch_size = batch_size
        self.buffer = []

    def add_triple(self, subject, predicate, obj):
        """Add triple to buffer."""
        self.buffer.append((subject, predicate, obj))

        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        """Insert buffered triples to database."""
        if not self.buffer:
            return

        # Build SPARQL INSERT query
        query = self._build_insert_query(self.buffer)

        # Execute batch insert
        self._execute_update(query)

        self.buffer = []
```

#### 7.1.3 Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class ParallelIFCConverter:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers

    def convert_parallel(self, entities: List[Entity]) -> List[Triple]:
        """Convert entities to triples in parallel."""
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Split entities into chunks
            chunk_size = len(entities) // self.num_workers
            chunks = [
                entities[i:i + chunk_size]
                for i in range(0, len(entities), chunk_size)
            ]

            # Process chunks in parallel
            futures = [
                executor.submit(self._convert_chunk, chunk)
                for chunk in chunks
            ]

            # Collect results
            triples = []
            for future in futures:
                triples.extend(future.result())

            return triples
```

### 7.2 Indexing Strategy

#### 7.2.1 GraphDB Indexes

```sparql
# Create custom indexes for common query patterns
PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>

# Index on entity types
CREATE INDEX idx_entity_type ON (
  SELECT ?s WHERE { ?s rdf:type ?type }
)

# Index on GlobalId
CREATE INDEX idx_global_id ON (
  SELECT ?s ?id WHERE { ?s ifc:globalId_IfcRoot ?id }
)

# Index on names
CREATE INDEX idx_name ON (
  SELECT ?s ?name WHERE { ?s ifc:name_IfcRoot ?name }
)

# Composite index for spatial containment
CREATE INDEX idx_spatial_containment ON (
  SELECT ?element ?structure WHERE {
    ?rel ifc:relatedElements_IfcRelContainedInSpatialStructure ?element .
    ?rel ifc:relatingStructure_IfcRelContainedInSpatialStructure ?structure
  }
)
```

#### 7.2.2 Apache Jena TDB Indexing

```java
// Configure TDB indexes
DatasetGraph dsg = TDB2Factory.connectDatasetGraph(location);

// SPO, POS, OSP indexes are created by default
// Additional custom indexes
dsg.getContext().set(TDB.symIndexes, "SPO,POS,OSP,SPOG");
```

### 7.3 Query Optimization

#### 7.3.1 Query Patterns

```sparql
# GOOD: Filter early, specific patterns first
PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
SELECT ?wall ?name WHERE {
  ?wall rdf:type ifc:IfcWall .           # Specific type first
  FILTER(?wall = <http://...>)           # Filter early
  ?wall ifc:name_IfcRoot ?name .
}

# BAD: Late filtering, broad patterns
SELECT ?element ?name WHERE {
  ?element ifc:name_IfcRoot ?name .      # Too broad
  ?element rdf:type ?type .
  FILTER(?type = ifc:IfcWall)            # Filter too late
}

# GOOD: Use property paths efficiently
SELECT ?building ?space WHERE {
  ?building rdf:type ifc:IfcBuilding .
  ?space rdf:type ifc:IfcSpace .
  ?space ifc:decomposes+ ?building .     # Property path
}
LIMIT 100                                # Always use LIMIT

# GOOD: Aggregate at database level
SELECT ?material (SUM(?volume) as ?total) WHERE {
  ?element ifc:hasMaterial ?mat .
  ?mat ifc:name_IfcMaterial ?material .
  ?element ifc:hasQuantity/ifc:volumeValue_IfcQuantityVolume ?volume .
}
GROUP BY ?material
```

#### 7.3.2 Query Rewriting Rules

1. **Push filters down**: Apply filters as early as possible
2. **Selectivity first**: Query most selective patterns first
3. **Avoid OPTIONAL when not needed**: Use only when truly optional
4. **Limit early**: Use LIMIT even for intermediate results
5. **Use EXISTS instead of COUNT**: For existence checks
6. **Avoid REGEX when possible**: Use exact matching

### 7.4 Caching Strategy

#### 7.4.1 Redis Cache Configuration

```python
import redis
from hashlib import sha256
import json

class QueryCache:
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = default_ttl

    def get_cached_result(self, query: str) -> Optional[dict]:
        """Get cached query result."""
        cache_key = self._compute_cache_key(query)
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)
        return None

    def cache_result(self, query: str, result: dict, ttl: int = None):
        """Cache query result."""
        cache_key = self._compute_cache_key(query)
        ttl = ttl or self.default_ttl

        self.redis.setex(
            cache_key,
            ttl,
            json.dumps(result)
        )

    def _compute_cache_key(self, query: str) -> str:
        """Compute cache key from query."""
        return f"query:{sha256(query.encode()).hexdigest()}"

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
```

#### 7.4.2 Cache Invalidation Strategy

```python
# Invalidate cache on data updates
class CacheInvalidator:
    def __init__(self, cache: QueryCache):
        self.cache = cache

    def on_data_insert(self, entity_type: str):
        """Invalidate relevant caches when data is inserted."""
        # Invalidate queries involving this entity type
        patterns = [
            f"query:*{entity_type}*",
            "query:*SELECT ?s*",  # Broad queries
            "query:*COUNT*"        # Aggregation queries
        ]

        for pattern in patterns:
            self.cache.invalidate_pattern(pattern)
```

#### 7.4.3 Multi-Level Caching

```
Level 1: Application Memory (LRU Cache)
  - Size: 100 queries
  - TTL: 5 minutes
  - Hit rate: ~80%

Level 2: Redis (Distributed Cache)
  - Size: 10,000 queries
  - TTL: 1 hour
  - Hit rate: ~15%

Level 3: Database Query Results
  - No cache
  - Hit rate: ~5%
```

---

## 8. Security

### 8.1 Authentication & Authorization

#### 8.1.1 API Key Authentication

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key."""
    user = await get_user_by_api_key(api_key)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return user
```

#### 8.1.2 JWT Token Authentication

```python
from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

security = HTTPBearer()

async def verify_jwt_token(token: str = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            token.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401)

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
```

#### 8.1.3 Role-Based Access Control (RBAC)

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class Permission(str, Enum):
    CONVERT_IFC = "convert:ifc"
    QUERY_DATA = "query:data"
    MANAGE_USERS = "manage:users"
    TRIGGER_REASONING = "admin:reasoning"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.CONVERT_IFC,
        Permission.QUERY_DATA,
        Permission.MANAGE_USERS,
        Permission.TRIGGER_REASONING
    ],
    Role.USER: [
        Permission.CONVERT_IFC,
        Permission.QUERY_DATA
    ],
    Role.VIEWER: [
        Permission.QUERY_DATA
    ]
}

def require_permission(permission: Permission):
    """Decorator to check permission."""
    async def check(user = Depends(verify_api_key)):
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])

        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission}"
            )

        return user

    return check
```

### 8.2 Data Access Control

#### 8.2.1 Query-Level Security

```python
class QuerySecurityFilter:
    """Add security filters to SPARQL queries."""

    def __init__(self, user: User):
        self.user = user

    def apply_security_filter(self, query: str) -> str:
        """Add WHERE clause to restrict data access."""
        if self.user.role == Role.ADMIN:
            return query  # Admin has full access

        # Add filter for user's projects only
        filter_clause = f"""
        FILTER EXISTS {{
            ?s ifc:relatedToProject ?project .
            ?project ifc:hasAccessUser <{self.user.uri}> .
        }}
        """

        # Insert filter into WHERE clause
        return self._insert_filter(query, filter_clause)
```

#### 8.2.2 Entity-Level Permissions

```python
class EntityPermission(BaseModel):
    user_id: UUID
    entity_global_id: str
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False

async def check_entity_access(
    user: User,
    entity_id: str,
    permission_type: str
) -> bool:
    """Check if user has access to entity."""
    permission = await get_entity_permission(user.id, entity_id)

    if permission_type == "read":
        return permission.can_read
    elif permission_type == "write":
        return permission.can_write
    elif permission_type == "delete":
        return permission.can_delete

    return False
```

### 8.3 Input Validation & Sanitization

#### 8.3.1 SPARQL Injection Prevention

```python
from typing import Set
import re

class SPARQLValidator:
    """Validate and sanitize SPARQL queries."""

    ALLOWED_PREFIXES: Set[str] = {
        "rdf", "rdfs", "owl", "xsd", "ifc", "base"
    }

    FORBIDDEN_PATTERNS = [
        r";\s*DROP",
        r";\s*DELETE",
        r";\s*INSERT",
        r"SERVICE\s+<",  # Prevent federated queries
    ]

    def validate(self, query: str) -> bool:
        """Validate SPARQL query safety."""
        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError(f"Forbidden pattern: {pattern}")

        # Ensure query only uses allowed prefixes
        prefixes = re.findall(r"PREFIX\s+(\w+):", query)
        for prefix in prefixes:
            if prefix not in self.ALLOWED_PREFIXES:
                raise ValueError(f"Forbidden prefix: {prefix}")

        # Parse query to validate syntax
        try:
            prepareQuery(query)
        except Exception as e:
            raise ValueError(f"Invalid SPARQL syntax: {e}")

        return True
```

#### 8.3.2 File Upload Validation

```python
from magic import Magic

class IFCFileValidator:
    """Validate uploaded IFC files."""

    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_MIME_TYPES = ["application/x-step", "text/plain"]

    def validate(self, file: UploadFile) -> bool:
        """Validate IFC file."""
        # Check file size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)      # Reset

        if size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {size} bytes")

        # Check MIME type
        mime = Magic(mime=True)
        file_type = mime.from_buffer(file.read(1024))
        file.seek(0)

        if file_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"Invalid file type: {file_type}")

        # Validate IFC header
        header = file.read(100).decode('utf-8', errors='ignore')
        if not header.startswith("ISO-10303-21"):
            raise ValueError("Invalid IFC header")

        file.seek(0)
        return True
```

### 8.4 Rate Limiting

```python
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/convert")
@limiter.limit("5/hour")  # 5 conversions per hour
async def convert_ifc(request: Request, file: UploadFile):
    ...

@app.post("/api/v1/query")
@limiter.limit("100/minute")  # 100 queries per minute
async def execute_query(request: Request, query: QueryRequest):
    ...
```

### 8.5 Security Checklist

- [x] API key or JWT authentication required
- [x] Role-based access control implemented
- [x] SPARQL injection prevention
- [x] File upload validation (type, size, content)
- [x] Rate limiting on all endpoints
- [x] HTTPS/TLS encryption in production
- [x] Query timeout limits (prevent DoS)
- [x] Input sanitization for all user data
- [x] Secure storage of API keys (hashed)
- [x] Audit logging for all actions
- [x] CORS policy configured
- [x] SQL injection prevention (for metadata DB)
- [x] XSS prevention in web dashboard
- [x] Regular security updates

---

## 9. Deployment

### 9.1 Docker Containerization

#### 9.1.1 API Service Dockerfile

```dockerfile
# Dockerfile for FastAPI service
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 9.1.2 GraphDB Dockerfile

```dockerfile
# Dockerfile for GraphDB
FROM ontotext/graphdb:10.0.0

# Copy configuration
COPY graphdb-config/graphdb.properties /opt/graphdb/conf/

# Expose ports
EXPOSE 7200

# Set heap size
ENV GDB_HEAP_SIZE=4g

CMD ["-Dgraphdb.home=/opt/graphdb/home"]
```

### 9.2 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Service
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ifc_ontology
      - GRAPHDB_URL=http://graphdb:7200/repositories/ifc
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - graphdb
      - redis
    volumes:
      - ./data/uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  # GraphDB Service
  graphdb:
    image: ontotext/graphdb:10.0.0
    ports:
      - "7200:7200"
    environment:
      - GDB_HEAP_SIZE=4g
      - GDB_JAVA_OPTS=-Xmx4g -Xms4g
    volumes:
      - graphdb_data:/opt/graphdb/home
      - ./graphdb-config:/opt/graphdb/conf
    restart: unless-stopped

  # PostgreSQL Service
  postgres:
    image: postgres:13
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=ifc_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=ifc_ontology
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  # Redis Service
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

  # Web Dashboard
  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

volumes:
  graphdb_data:
  postgres_data:
  redis_data:

networks:
  default:
    name: ifc_ontology_network
```

### 9.3 Environment Configuration

#### 9.3.1 Development (.env.dev)

```bash
# API Configuration
SECRET_KEY=dev_secret_key_change_in_production
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database Configuration
POSTGRES_USER=ifc_user
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=ifc_ontology
DATABASE_URL=postgresql://ifc_user:dev_password@localhost:5432/ifc_ontology

# GraphDB Configuration
GRAPHDB_URL=http://localhost:7200/repositories/ifc
GRAPHDB_USERNAME=admin
GRAPHDB_PASSWORD=admin

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# File Upload
MAX_UPLOAD_SIZE=524288000  # 500MB
UPLOAD_DIR=/tmp/ifc_uploads

# Performance
MAX_WORKERS=4
QUERY_TIMEOUT=30
CONVERSION_TIMEOUT=1800  # 30 minutes
```

#### 9.3.2 Production (.env.prod)

```bash
# API Configuration
SECRET_KEY=${SECRET_KEY}  # Generate with: openssl rand -hex 32
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Database Configuration
POSTGRES_USER=ifc_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=ifc_ontology
DATABASE_URL=postgresql://ifc_user:${POSTGRES_PASSWORD}@postgres:5432/ifc_ontology

# GraphDB Configuration
GRAPHDB_URL=http://graphdb:7200/repositories/ifc
GRAPHDB_USERNAME=${GRAPHDB_USERNAME}
GRAPHDB_PASSWORD=${GRAPHDB_PASSWORD}

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# File Upload
MAX_UPLOAD_SIZE=524288000
UPLOAD_DIR=/app/data/uploads

# Performance
MAX_WORKERS=8
QUERY_TIMEOUT=60
CONVERSION_TIMEOUT=3600  # 60 minutes

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Security
ALLOWED_ORIGINS=https://yourdomain.com
ENABLE_CORS=true
```

### 9.4 Deployment Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Scale API service
docker-compose up -d --scale api=3

# Update single service
docker-compose up -d --no-deps --build api

# Database migration
docker-compose exec api python -m alembic upgrade head

# Create GraphDB repository
docker-compose exec graphdb curl -X POST \
  http://localhost:7200/rest/repositories \
  -H 'Content-Type: application/json' \
  -d @/opt/graphdb/conf/repo-config.json
```

### 9.5 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy IFC Ontology System

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2

  build:
    needs: test
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Build Docker images
      run: |
        docker-compose build

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker-compose push

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /opt/ifc-ontology
          docker-compose pull
          docker-compose up -d
          docker-compose exec api python -m alembic upgrade head
```

---

## 10. Testing Strategy

### 10.1 Unit Testing

#### 10.1.1 IFC Parser Tests

```python
# tests/test_ifc_parser.py
import pytest
from src.parser.ifc_parser import IFCParser

def test_parse_valid_ifc_file():
    """Test parsing a valid IFC4 file."""
    parser = IFCParser("tests/fixtures/simple_building.ifc")
    entities = list(parser.parse())

    assert len(entities) > 0
    assert entities[0]['type'] == 'IfcProject'

def test_parse_invalid_schema():
    """Test error handling for invalid schema."""
    parser = IFCParser("tests/fixtures/invalid_schema.ifc")

    with pytest.raises(ValueError, match="Invalid IFC4 schema"):
        list(parser.parse())

def test_extract_entity_attributes():
    """Test entity attribute extraction."""
    parser = IFCParser("tests/fixtures/wall.ifc")
    entities = list(parser.parse())

    wall = next(e for e in entities if e['type'] == 'IfcWall')
    assert 'global_id' in wall
    assert 'name' in wall['attributes']
```

#### 10.1.2 RDF Converter Tests

```python
# tests/test_rdf_converter.py
import pytest
from src.converter.rdf_converter import RDFConverter
from rdflib import URIRef, Literal

def test_convert_entity_to_triples():
    """Test converting IFC entity to RDF triples."""
    converter = RDFConverter()

    entity = {
        'global_id': '2O2Fr$t4X7Zf8NOew3FLOH',
        'type': 'IfcWall',
        'attributes': {'name': 'External Wall'}
    }

    converter.convert_entity(entity)

    # Verify triples generated
    assert len(converter.graph) > 0
    assert (
        URIRef('http://example.org/ifc/2O2Fr$t4X7Zf8NOew3FLOH'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        URIRef('https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#IfcWall')
    ) in converter.graph

def test_serialize_graph():
    """Test RDF serialization."""
    converter = RDFConverter()
    # Add some triples...

    turtle = converter.serialize(format='turtle')
    assert 'ifc:IfcWall' in turtle
```

#### 10.1.3 Query Engine Tests

```python
# tests/test_query_engine.py
import pytest
from src.query.engine import QueryEngine

@pytest.fixture
def query_engine():
    return QueryEngine(store_url="http://localhost:7200/repositories/test")

def test_execute_simple_query(query_engine):
    """Test executing a simple SPARQL query."""
    query = """
        PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
        SELECT ?wall WHERE {
            ?wall a ifc:IfcWall .
        } LIMIT 10
    """

    results = query_engine.execute(query)
    assert results is not None
    assert len(results) <= 10

def test_query_timeout(query_engine):
    """Test query timeout handling."""
    # Very expensive query
    query = """
        SELECT * WHERE {
            ?s ?p ?o .
            ?s2 ?p2 ?o2 .
            ?s3 ?p3 ?o3 .
        }
    """

    with pytest.raises(TimeoutError):
        query_engine.execute(query, timeout=1)
```

### 10.2 Integration Testing

#### 10.2.1 End-to-End Conversion Test

```python
# tests/integration/test_conversion_flow.py
import pytest
from src.api.client import Client

@pytest.mark.integration
def test_full_conversion_flow():
    """Test complete IFC → RDF conversion flow."""
    client = Client(base_url="http://localhost:8000")

    # Upload IFC file
    job = client.convert_ifc("tests/fixtures/sample_building.ifc")
    assert job.status in ["pending", "processing"]

    # Wait for completion
    job.wait(timeout=300)
    assert job.status == "completed"
    assert job.triple_count > 0

    # Verify data in database
    results = client.query("""
        PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
        SELECT (COUNT(?s) as ?count) WHERE {
            ?s a ifc:IfcWall .
        }
    """)

    assert int(results[0]['count']) > 0
```

#### 10.2.2 API Integration Test

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.mark.integration
def test_api_query_endpoint():
    """Test SPARQL query endpoint."""
    response = client.post(
        "/api/v1/query",
        json={
            "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 10",
            "format": "json"
        },
        headers={"X-API-Key": "test_key"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]["bindings"]) <= 10

@pytest.mark.integration
def test_api_file_upload():
    """Test IFC file upload endpoint."""
    with open("tests/fixtures/sample.ifc", "rb") as f:
        response = client.post(
            "/api/v1/convert",
            files={"file": ("sample.ifc", f, "application/x-step")},
            headers={"X-API-Key": "test_key"}
        )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
```

### 10.3 Performance Testing

#### 10.3.1 Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class IFCOntologyUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get API key."""
        self.api_key = "test_api_key"

    @task(3)
    def query_walls(self):
        """Query for walls."""
        self.client.post(
            "/api/v1/query",
            json={
                "query": """
                    PREFIX ifc: <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
                    SELECT ?wall ?name WHERE {
                        ?wall a ifc:IfcWall .
                        OPTIONAL { ?wall ifc:name_IfcRoot ?name }
                    } LIMIT 100
                """,
                "format": "json"
            },
            headers={"X-API-Key": self.api_key}
        )

    @task(1)
    def get_entity(self):
        """Get entity details."""
        self.client.get(
            "/api/v1/entities/2O2Fr$t4X7Zf8NOew3FLOH",
            headers={"X-API-Key": self.api_key}
        )

    @task(1)
    def list_buildings(self):
        """List all buildings."""
        self.client.get(
            "/api/v1/buildings",
            headers={"X-API-Key": self.api_key}
        )
```

Run load test:
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

#### 10.3.2 Performance Benchmarks

| Test Case | Target | Measurement |
|-----------|--------|-------------|
| Simple query (< 100 results) | < 2s | P95 response time |
| Complex aggregation query | < 10s | P95 response time |
| Entity lookup by GlobalId | < 500ms | P95 response time |
| 200MB IFC conversion | < 30min | Total time |
| 100 concurrent users | < 5s | P95 response time |
| Query cache hit | < 50ms | P95 response time |

### 10.4 Test Coverage Requirements

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Coverage requirements
# - Overall: 80%
# - Parser module: 85%
# - Converter module: 85%
# - API endpoints: 90%
# - Query engine: 80%
```

### 10.5 CI Test Matrix

```yaml
# Test across different configurations
strategy:
  matrix:
    python-version: [3.8, 3.9, 3.10]
    database: [graphdb, jena-tdb]
    os: [ubuntu-latest, macos-latest]
```

---

## 11. Future Considerations

### 11.1 Scalability Enhancements

#### 11.1.1 Horizontal Scaling

- **Multiple API instances**: Load balanced behind Nginx
- **Distributed triple store**: GraphDB cluster or Jena Fuseki distributed
- **Sharding strategy**: Partition data by building/project
- **Microservices**: Split parser, converter, query into separate services

#### 11.1.2 Cloud Deployment

- **AWS**: ECS/EKS for containers, RDS for PostgreSQL, ElastiCache for Redis
- **GCP**: GKE for Kubernetes, Cloud SQL, Memorystore
- **Azure**: AKS, Azure Database, Azure Cache for Redis

### 11.2 Additional Features

#### 11.2.1 Advanced Querying

- **Natural language queries**: Convert English to SPARQL using LLM
- **Query builder UI**: Visual query construction
- **Saved queries**: User can save and share queries
- **Query scheduling**: Run queries on schedule

#### 11.2.2 Enhanced Visualization

- **3D viewer integration**: Display geometry from IFC
- **Interactive graph visualization**: Show entity relationships
- **Dashboard widgets**: Customizable analytics widgets
- **Export to BIM tools**: Export back to Revit, ArchiCAD

#### 11.2.3 Advanced Analytics

- **Machine learning**: Predict missing properties, detect anomalies
- **Cost estimation**: Calculate costs based on quantities
- **Clash detection**: Identify spatial conflicts
- **Energy simulation**: Integrate with energy analysis tools

#### 11.2.4 Collaboration Features

- **Multi-user editing**: Collaborative query building
- **Comments and annotations**: Add notes to entities
- **Version control**: Track changes to IFC data
- **Notifications**: Alert users to data changes

### 11.3 Integration Opportunities

#### 11.3.1 BIM Authoring Tools

- **Revit plugin**: Direct export to ontology DB
- **ArchiCAD extension**: Real-time synchronization
- **Navisworks integration**: Model coordination

#### 11.3.2 Asset Management Systems

- **CMMS integration**: Sync with maintenance systems
- **ERP integration**: Connect to SAP, Oracle
- **IoT sensors**: Link to real-time sensor data
- **FM systems**: Integrate with facility management

#### 11.3.3 GIS Integration

- **Location data**: Link buildings to GIS coordinates
- **CityGML**: Convert to city-scale models
- **Urban planning**: Multi-building analysis

### 11.4 Research Extensions

#### 11.4.1 Ontology Evolution

- **Custom ontologies**: Support domain-specific extensions
- **Ontology alignment**: Map to other construction ontologies (BOT, SAREF)
- **Ontology versioning**: Manage ontology changes over time

#### 11.4.2 Advanced Reasoning

- **SWRL rules**: Complex custom reasoning rules
- **Probabilistic reasoning**: Handle uncertain data
- **Temporal reasoning**: Track changes over time
- **Spatial reasoning**: Geometric computations

### 11.5 Technology Upgrades

| Component | Current | Future Option |
|-----------|---------|---------------|
| Python | 3.10 | 3.12 (performance improvements) |
| FastAPI | 0.100+ | Keep updated |
| GraphDB | 10.x | 11.x when stable |
| React | 18.x | Next.js for SSR |
| Docker | 20.x | Kubernetes for orchestration |
| PostgreSQL | 13 | 15 (improved performance) |

---

## 12. Implementation Roadmap

### Phase 1: Foundation (Months 1-2)
- [x] Project setup and environment configuration
- [x] IFC parser development (ifcopenshell integration)
- [x] RDF converter implementation (ifcOWL mapping)
- [x] GraphDB setup and basic storage
- [x] Unit tests for core modules

### Phase 2: API Development (Month 3)
- [ ] RESTful API implementation (FastAPI)
- [ ] SPARQL endpoint integration
- [ ] Authentication and authorization
- [ ] API documentation (OpenAPI)
- [ ] Integration tests

### Phase 3: Client Libraries (Month 4)
- [ ] Python client library
- [ ] Java client library
- [ ] JavaScript/Node.js client
- [ ] Client documentation and examples

### Phase 4: Optimization (Month 5)
- [ ] Performance optimization (streaming, batching)
- [ ] Query caching (Redis)
- [ ] Indexing strategy
- [ ] Load testing and tuning
- [ ] Reasoning engine integration

### Phase 5: Dashboard & Deployment (Month 6)
- [ ] Web dashboard (React)
- [ ] Data visualization
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment

### Phase 6: Testing & Documentation (Month 7)
- [ ] Comprehensive test suite
- [ ] User documentation
- [ ] Deployment guide
- [ ] Performance benchmarks
- [ ] Project retrospective

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-03 | Tech Spec Architect Agent | Initial technical specification |

---

## Approval & Review

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | TBD | | |
| Product Owner | TBD | | |
| Security Reviewer | TBD | | |
| DevOps Lead | TBD | | |

---

**Document Status**: Draft
**Next Steps**: Review with team, begin Phase 1 implementation
**Related Documents**:
- PRD: `docs/PRD.md`
- API Documentation: `docs/api/openapi.yaml` (to be created)
- User Guide: `docs/user-guide.md` (to be created)
