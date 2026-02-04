"""OWL/RDFS 추론 및 SHACL 검증 API 라우트."""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from ..utils.query_executor import get_store
from ...inference.reasoner import OWLReasoner
from ...inference.shacl_validator import validate as shacl_validate
from ...storage.triple_store import TripleStore

logger = logging.getLogger(__name__)

router = APIRouter()

# SPARQL 공통 프리픽스
_PREFIXES = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX bim:  <http://example.org/bim-ontology/schema#>
PREFIX inst: <http://example.org/bim-ontology/instance#>
PREFIX ifc:  <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
"""


@router.post("/reasoning")
async def run_reasoning():
    """OWL/RDFS 추론을 실행하고 결과를 반환한다."""
    try:
        store = get_store()
        reasoner = OWLReasoner(store.graph)
        result = reasoner.run_all()
        return result
    except Exception as e:
        logger.error("추론 실행 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reasoning/validate")
async def run_shacl_validation():
    """SHACL 형상 검증을 실행하고 결과를 반환한다."""
    try:
        store = get_store()
        result = shacl_validate(store.graph)
        return result
    except Exception as e:
        logger.error("SHACL 검증 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


def _run_query(store, sparql: str) -> list[dict[str, Any]]:
    """프리픽스가 포함된 SPARQL 쿼리를 실행한다."""
    return store.query(_PREFIXES + sparql)


def _run_validation_checks(store) -> list[dict[str, Any]]:
    """모든 검증 항목을 실행하고 결과 리스트를 반환한다."""
    checks = []

    # 1. Schema Completeness
    classes = _run_query(store, """
        SELECT ?class WHERE {
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), "http://example.org/bim-ontology/schema#"))
        }
    """)
    data_props = _run_query(store, """
        SELECT ?prop WHERE { ?prop a owl:DatatypeProperty }
    """)
    obj_props = _run_query(store, """
        SELECT ?prop WHERE { ?prop a owl:ObjectProperty }
    """)
    checks.append({
        "name": "schema_completeness",
        "status": "pass" if len(classes) >= 8 and len(data_props) >= 6 else "fail",
        "details": {
            "owl_classes": len(classes),
            "data_properties": len(data_props),
            "object_properties": len(obj_props),
        },
    })

    # 2. Spatial Hierarchy
    chain = _run_query(store, """
        SELECT ?project ?site ?building ?storey WHERE {
            ?project a bim:Project .
            ?project bim:aggregates ?site .
            ?site a bim:Site .
            ?site bim:aggregates ?building .
            ?building a bim:Building .
            ?building bim:aggregates ?storey .
            ?storey a bim:BuildingStorey .
        }
    """)
    storeys = _run_query(store, """
        SELECT (COUNT(?s) AS ?c) WHERE { ?s a bim:BuildingStorey }
    """)
    checks.append({
        "name": "spatial_hierarchy",
        "status": "pass" if len(chain) > 0 else "fail",
        "details": {
            "complete_chains": len(chain),
            "storeys": storeys[0]["c"] if storeys else 0,
        },
    })

    # 3. Element Statistics
    total = _run_query(store, """
        SELECT (COUNT(?e) AS ?total) WHERE { ?e a bim:PhysicalElement }
    """)
    categories = _run_query(store, """
        SELECT ?category (COUNT(?e) AS ?count) WHERE {
            ?e bim:hasCategory ?category
        } GROUP BY ?category ORDER BY DESC(?count)
    """)
    total_elem = total[0]["total"] if total else 0
    checks.append({
        "name": "element_statistics",
        "status": "info",
        "details": {
            "total_elements": total_elem,
            "category_count": len(categories),
            "categories": [
                {"name": r["category"], "count": r["count"]}
                for r in categories
            ],
        },
    })

    # 4. URI Consistency
    orphans = _run_query(store, """
        SELECT (COUNT(?o) AS ?count) WHERE {
            ?o bim:isContainedIn ?s .
            FILTER NOT EXISTS { ?o a bim:PhysicalElement }
        }
    """)
    unlinked = _run_query(store, """
        SELECT (COUNT(?u) AS ?count) WHERE {
            ?u a bim:PhysicalElement .
            FILTER NOT EXISTS { ?u bim:isContainedIn ?any }
        }
    """)
    orphan_count = orphans[0]["count"] if orphans else 0
    unlinked_count = unlinked[0]["count"] if unlinked else 0
    uri_status = "pass" if orphan_count == 0 and unlinked_count == 0 else (
        "fail" if orphan_count > 0 else "warn"
    )
    checks.append({
        "name": "uri_consistency",
        "status": uri_status,
        "details": {
            "orphan_elements": orphan_count,
            "unlinked_elements": unlinked_count,
        },
    })

    # 5. PropertySet Coverage
    psets = _run_query(store, """
        SELECT (COUNT(?ps) AS ?total) WHERE { ?ps a bim:PropertySet }
    """)
    plant_psets = _run_query(store, """
        SELECT (COUNT(?ps) AS ?total) WHERE { ?ps a bim:PlantPropertySet }
    """)
    coverage = _run_query(store, """
        SELECT (COUNT(DISTINCT ?wp) AS ?withPSet) WHERE {
            ?wp a bim:PhysicalElement .
            ?wp bim:hasPropertySet ?ps .
        }
    """)
    total_psets = psets[0]["total"] if psets else 0
    with_pset = coverage[0]["withPSet"] if coverage else 0
    cov_ratio = with_pset / total_elem if total_elem > 0 else 0
    pset_status = "fail" if total_psets == 0 else ("warn" if cov_ratio < 0.3 else "pass")
    checks.append({
        "name": "property_set_coverage",
        "status": pset_status,
        "details": {
            "total_property_sets": total_psets,
            "plant_property_sets": plant_psets[0]["total"] if plant_psets else 0,
            "elements_with_pset": with_pset,
            "total_elements": total_elem,
            "coverage_ratio": round(cov_ratio, 3),
        },
    })

    # 6. Required Properties
    no_gid = _run_query(store, """
        SELECT (COUNT(?e) AS ?count) WHERE {
            ?e a bim:PhysicalElement .
            FILTER NOT EXISTS { ?e bim:hasGlobalId ?id }
        }
    """)
    missing_gid = no_gid[0]["count"] if no_gid else 0
    checks.append({
        "name": "required_properties",
        "status": "pass" if missing_gid == 0 else "fail",
        "details": {"missing_global_id": missing_gid},
    })

    # 7. Classification Quality
    other_q = _run_query(store, """
        SELECT (COUNT(?e) AS ?count) WHERE {
            ?e a bim:PhysicalElement .
            ?e bim:hasCategory "Other" .
        }
    """)
    total_cat = _run_query(store, """
        SELECT (COUNT(?e) AS ?count) WHERE { ?e bim:hasCategory ?c }
    """)
    other_count = other_q[0]["count"] if other_q else 0
    total_categorized = total_cat[0]["count"] if total_cat else 0
    other_ratio = other_count / total_categorized if total_categorized > 0 else 0
    cls_status = "pass" if other_ratio <= 0.15 else ("warn" if other_ratio <= 0.30 else "fail")
    checks.append({
        "name": "classification_quality",
        "status": cls_status,
        "details": {
            "other_count": other_count,
            "total_categorized": total_categorized,
            "other_ratio": round(other_ratio, 4),
        },
    })

    # 8. Relationship Integrity
    contains = _run_query(store, """
        SELECT (COUNT(*) AS ?c) WHERE { ?s bim:containsElement ?e }
    """)
    contained_in = _run_query(store, """
        SELECT (COUNT(*) AS ?c) WHERE { ?e bim:isContainedIn ?s }
    """)
    asymmetric = _run_query(store, """
        SELECT (COUNT(?e) AS ?c) WHERE {
            ?e bim:isContainedIn ?s .
            FILTER NOT EXISTS { ?s bim:containsElement ?e }
        }
    """)
    contains_n = contains[0]["c"] if contains else 0
    contained_n = contained_in[0]["c"] if contained_in else 0
    asym_n = asymmetric[0]["c"] if asymmetric else 0
    symmetric = contains_n == contained_n and asym_n == 0
    checks.append({
        "name": "relationship_integrity",
        "status": "pass" if symmetric and contains_n > 0 else "warn",
        "details": {
            "contains_element": contains_n,
            "is_contained_in": contained_n,
            "asymmetric_pairs": asym_n,
            "symmetric": symmetric,
        },
    })

    return checks


# ── URI prefix 축약 ──

_PREFIX_MAP = {
    "http://example.org/bim-ontology/schema#": "bim:",
    "http://example.org/bim-ontology/instance#": "inst:",
    "http://www.w3.org/2002/07/owl#": "owl:",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:",
    "https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#": "ifc:",
    "http://www.w3.org/2001/XMLSchema#": "xsd:",
}


def _shorten_uri(uri: str) -> str:
    """URI를 짧은 prefix 형태로 축약한다."""
    uri = str(uri)
    for long, short in _PREFIX_MAP.items():
        if uri.startswith(long):
            return short + uri[len(long):]
    return uri


def _expand_uri(short: str) -> str:
    """축약된 prefix URI를 전체 URI로 확장한다."""
    for long, prefix in _PREFIX_MAP.items():
        if short.startswith(prefix):
            return long + short[len(prefix):]
    return short


def _get_store_for_file(ttl_file: str | None):
    """ttl_file이 지정되면 해당 파일을 로드한 스토어를, 아니면 전역 스토어를 반환."""
    if ttl_file:
        filepath = _RDF_DIR / ttl_file
        if not filepath.is_file():
            raise HTTPException(status_code=404, detail=f"파일 없음: {ttl_file}")
        store = TripleStore()
        store.load(str(filepath))
        return store
    return get_store()


_RDF_DIR = Path("data/rdf")


@router.get("/reasoning/ttl-files")
async def list_ttl_files():
    """data/rdf/ 디렉토리 내 사용 가능한 TTL 파일 목록을 반환한다."""
    try:
        files = []
        for p in sorted(_RDF_DIR.glob("*.ttl*")):
            if p.is_file():
                stat = p.stat()
                files.append({
                    "name": p.name,
                    "size_kb": round(stat.st_size / 1024),
                    "modified": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                })

        # current = 첫 번째 .ttl 파일 (bak 제외)
        current = next((f["name"] for f in files if f["name"].endswith(".ttl")), None)
        return {"files": files, "current": current}
    except Exception as e:
        logger.error("TTL 파일 목록 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning/validation-report")
async def get_validation_report(ttl_file: str | None = None):
    """RDF 그래프 품질 검증 리포트를 반환한다.

    8개 카테고리의 SPARQL 기반 검증을 실행하고 JSON 리포트를 반환합니다.

    Args:
        ttl_file: 검증할 TTL 파일명. None이면 현재 로딩된 스토어 사용.
    """
    try:
        if ttl_file:
            filepath = _RDF_DIR / ttl_file
            if not filepath.is_file():
                raise HTTPException(status_code=404, detail=f"파일 없음: {ttl_file}")
            store = TripleStore()
            store.load(str(filepath))
        else:
            store = get_store()

        start = time.time()
        checks = _run_validation_checks(store)
        elapsed = time.time() - start

        summary = {"pass": 0, "warn": 0, "info": 0, "fail": 0}
        for c in checks:
            summary[c["status"]] += 1

        return {
            "ttl_file": ttl_file,
            "total_triples": store.count(),
            "validation_time": round(elapsed, 2),
            "checks": checks,
            "summary": summary,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("검증 리포트 생성 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning/other-elements")
async def get_other_elements(
    ttl_file: str | None = None,
    limit: int = 100,
    offset: int = 0,
    name_pattern: str | None = None,
):
    """Other로 분류된 요소들의 상세 정보를 반환한다."""
    import re as _re
    try:
        if ttl_file:
            filepath = _RDF_DIR / ttl_file
            if not filepath.is_file():
                raise HTTPException(status_code=404, detail=f"파일 없음: {ttl_file}")
            store = TripleStore()
            store.load(str(filepath))
        else:
            store = get_store()

        filter_clause = ""
        if name_pattern:
            safe = name_pattern.replace('"', '\\"')
            filter_clause = f'FILTER(CONTAINS(LCASE(STR(?name)), LCASE("{safe}")))'

        elements_q = _run_query(store, f"""
            SELECT ?name ?type ?gid ?storey_name WHERE {{
                ?e a bim:PhysicalElement .
                ?e bim:hasCategory "Other" .
                ?e bim:hasName ?name .
                ?e bim:hasOriginalType ?type .
                OPTIONAL {{ ?e bim:hasGlobalId ?gid }}
                OPTIONAL {{
                    ?e bim:isContainedIn ?storey .
                    ?storey bim:hasName ?storey_name .
                }}
                {filter_clause}
            }} ORDER BY ?name
        """)

        total = len(elements_q)
        page = elements_q[offset:offset + limit]

        groups = {
            "Pipe Fittings": {"patterns": [r"degree direction change", r"weldolet", r"sockolet", r"eccentric.*size", r"concentric.*size", r"nipple", r"^90e-", r"^45"], "suggested": "PipeFitting", "count": 0, "examples": []},
            "Support Hardware": {"patterns": [r"^anvil_", r"^hgr", r"^assy_", r"hex.?nut"], "suggested": "Hanger", "count": 0, "examples": []},
            "Nozzle/Connection": {"patterns": [r"^[a-z][0-9]?$", r"^n[0-9]+$"], "suggested": "Nozzle", "count": 0, "examples": []},
            "Process Equipment": {"patterns": [r"distillation", r"recovery unit"], "suggested": "Equipment", "count": 0, "examples": []},
            "Equipment Tags": {"patterns": [r"^[a-z]-\d{3}$"], "suggested": "Equipment", "count": 0, "examples": []},
            "Pump Connections": {"patterns": [r"^suction$", r"^discharge$"], "suggested": "Pump", "count": 0, "examples": []},
        }

        for elem in elements_q:
            name = str(elem.get("name", ""))
            matched = False
            for gname, ginfo in groups.items():
                for pat in ginfo["patterns"]:
                    if _re.search(pat, name, _re.IGNORECASE):
                        ginfo["count"] += 1
                        if len(ginfo["examples"]) < 3 and name not in ginfo["examples"]:
                            ginfo["examples"].append(name)
                        matched = True
                        break
                if matched:
                    break

        name_groups = []
        for gname, ginfo in groups.items():
            if ginfo["count"] > 0:
                name_groups.append({
                    "pattern": gname,
                    "count": ginfo["count"],
                    "examples": ginfo["examples"],
                    "suggested_category": ginfo["suggested"],
                })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "elements": [
                {
                    "name": str(e.get("name", "")),
                    "original_type": str(e.get("type", "")),
                    "global_id": str(e.get("gid", "")),
                    "storey": str(e.get("storey_name", "")),
                }
                for e in page
            ],
            "name_groups": name_groups,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Other 요소 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Node Explorer API ──


@router.get("/reasoning/node-types")
async def get_node_types(ttl_file: str | None = None):
    """TTL 내 모든 고유 rdf:type 값과 인스턴스 수를 반환한다."""
    try:
        store = _get_store_for_file(ttl_file)
        rows = _run_query(store, """
            SELECT ?type (COUNT(?s) AS ?count) WHERE {
                ?s a ?type .
            } GROUP BY ?type ORDER BY DESC(?count)
        """)
        types = []
        for r in rows:
            uri = str(r.get("type", ""))
            types.append({
                "uri": uri,
                "short": _shorten_uri(uri),
                "count": int(r.get("count", 0)),
            })
        return {"types": types}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("노드 타입 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning/node-predicates")
async def get_node_predicates(ttl_file: str | None = None):
    """TTL 내 모든 고유 predicate와 사용 횟수를 반환한다."""
    try:
        store = _get_store_for_file(ttl_file)
        rows = _run_query(store, """
            SELECT ?pred (COUNT(*) AS ?count) WHERE {
                ?s ?pred ?o .
            } GROUP BY ?pred ORDER BY DESC(?count)
        """)
        predicates = []
        for r in rows:
            uri = str(r.get("pred", ""))
            predicates.append({
                "uri": uri,
                "short": _shorten_uri(uri),
                "count": int(r.get("count", 0)),
            })
        return {"predicates": predicates}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("노드 predicate 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning/nodes")
async def browse_nodes(
    ttl_file: str | None = None,
    type_filter: str | None = None,
    columns: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """노드 타입 필터 + 선택한 predicate 컬럼으로 노드 테이블 데이터를 반환한다."""
    try:
        store = _get_store_for_file(ttl_file)

        col_list = [c.strip() for c in columns.split(",") if c.strip()] if columns else []

        # 타입 필터 조건
        type_clause = ""
        if type_filter:
            expanded = _expand_uri(type_filter)
            type_clause = f"?subject a <{expanded}> ."

        # 검색 조건
        search_clause = ""
        if search:
            safe = search.replace('"', '\\"')
            search_clause = f'FILTER(CONTAINS(LCASE(STR(?subject)), LCASE("{safe}")))'
            # hasName이 컬럼에 있으면 이름으로도 검색
            if col_list:
                search_clause = (
                    f'FILTER(CONTAINS(LCASE(STR(?subject)), LCASE("{safe}"))'
                    f' || CONTAINS(LCASE(STR(?col0)), LCASE("{safe}")))'
                )

        # OPTIONAL 컬럼 패턴 생성
        optional_clauses = []
        select_vars = ["?subject"]
        for i, col in enumerate(col_list):
            var = f"?col{i}"
            select_vars.append(var)
            expanded_col = _expand_uri(col)
            optional_clauses.append(f"OPTIONAL {{ ?subject <{expanded_col}> {var} }}")

        # 노드 조회 쿼리
        sparql = f"""
            SELECT {" ".join(select_vars)} WHERE {{
                {type_clause}
                {chr(10).join(optional_clauses)}
                {search_clause}
            }} ORDER BY ?subject LIMIT {limit} OFFSET {offset}
        """
        rows = _run_query(store, sparql)

        # total count 별도 쿼리
        count_sparql = f"""
            SELECT (COUNT(DISTINCT ?subject) AS ?total) WHERE {{
                {type_clause}
                {search_clause if not col_list else ""}
            }}
        """
        # 검색이 컬럼 값에도 걸리는 경우 count에도 반영
        if search and col_list:
            col0_expanded = _expand_uri(col_list[0])
            safe = search.replace('"', '\\"')
            count_sparql = f"""
                SELECT (COUNT(DISTINCT ?subject) AS ?total) WHERE {{
                    {type_clause}
                    OPTIONAL {{ ?subject <{col0_expanded}> ?col0 }}
                    FILTER(CONTAINS(LCASE(STR(?subject)), LCASE("{safe}"))
                     || CONTAINS(LCASE(STR(?col0)), LCASE("{safe}")))
                }}
            """
        count_rows = _run_query(store, count_sparql)
        total = int(count_rows[0]["total"]) if count_rows else 0

        # 결과 포맷
        result_rows = []
        for r in rows:
            subj = str(r.get("subject", ""))
            values = []
            for i in range(len(col_list)):
                val = r.get(f"col{i}")
                values.append(str(val) if val is not None else "")
            result_rows.append({
                "subject": _shorten_uri(subj),
                "subject_uri": subj,
                "values": values,
            })

        return {
            "total": total,
            "columns": [_shorten_uri(c) if ":" not in c or c.startswith("http") else c for c in col_list],
            "rows": result_rows,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("노드 탐색 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning/node-detail")
async def get_node_detail(
    subject: str,
    ttl_file: str | None = None,
):
    """특정 subject의 모든 (predicate, object) 쌍을 반환한다."""
    try:
        store = _get_store_for_file(ttl_file)
        expanded = _expand_uri(subject)
        rows = _run_query(store, f"""
            SELECT ?pred ?obj WHERE {{
                <{expanded}> ?pred ?obj .
            }} ORDER BY ?pred
        """)
        triples = []
        for r in rows:
            triples.append({
                "predicate": _shorten_uri(str(r.get("pred", ""))),
                "object": _shorten_uri(str(r.get("obj", ""))),
            })
        return {"subject": subject, "triples": triples}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("노드 상세 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
