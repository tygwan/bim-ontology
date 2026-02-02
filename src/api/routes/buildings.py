"""건물 관련 REST API."""

from fastapi import APIRouter, HTTPException, Query

from ..models.response import BuildingInfo, StoreyInfo, ElementInfo
from ..utils.query_executor import execute_sparql
from ..queries.templates import (
    get_all_buildings,
    get_spaces_by_storey,
    get_all_elements_by_category,
)

router = APIRouter()


@router.get(
    "/buildings",
    response_model=list[BuildingInfo],
    summary="모든 건물 조회",
)
async def list_buildings():
    results = execute_sparql(get_all_buildings())
    return [
        BuildingInfo(
            uri=r.get("uri", ""),
            global_id=r.get("globalId"),
            name=r.get("name"),
        )
        for r in results
    ]


@router.get(
    "/buildings/{global_id}",
    response_model=BuildingInfo,
    summary="특정 건물 조회",
)
async def get_building(global_id: str):
    query = f"""
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    SELECT ?uri ?name
    WHERE {{
        ?uri bim:hasGlobalId "{global_id}" .
        ?uri a bim:Building .
        OPTIONAL {{ ?uri bim:hasName ?name }}
    }}
    """
    results = execute_sparql(query)
    if not results:
        raise HTTPException(status_code=404, detail=f"Building {global_id} not found")
    r = results[0]
    return BuildingInfo(uri=r["uri"], global_id=global_id, name=r.get("name"))


@router.get(
    "/storeys",
    response_model=list[StoreyInfo],
    summary="모든 층 조회",
)
async def list_storeys():
    query = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?uri ?name ?globalId ?elevation (COUNT(?elem) AS ?num)
    WHERE {
        ?uri rdf:type bim:BuildingStorey .
        OPTIONAL { ?uri bim:hasName ?name }
        OPTIONAL { ?uri bim:hasGlobalId ?globalId }
        OPTIONAL { ?uri bim:hasElevation ?elevation }
        OPTIONAL { ?uri bim:containsElement ?elem }
    }
    GROUP BY ?uri ?name ?globalId ?elevation
    """
    results = execute_sparql(query)
    return [
        StoreyInfo(
            uri=r.get("uri", ""),
            global_id=r.get("globalId"),
            name=r.get("name"),
            elevation=r.get("elevation"),
            element_count=r.get("num", 0),
        )
        for r in results
    ]


@router.get(
    "/elements",
    response_model=list[ElementInfo],
    summary="카테고리별 요소 조회",
)
async def list_elements(
    category: str | None = Query(None, description="BIM 카테고리 (Pipe, Beam, Slab 등)"),
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    if category:
        query = get_all_elements_by_category(category, limit, offset)
    else:
        query = f"""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        SELECT ?uri ?name ?category ?originalType
        WHERE {{
            ?uri a bim:PhysicalElement .
            OPTIONAL {{ ?uri bim:hasName ?name }}
            OPTIONAL {{ ?uri bim:hasCategory ?category }}
            OPTIONAL {{ ?uri bim:hasOriginalType ?originalType }}
        }}
        ORDER BY ?category ?name
        LIMIT {limit}
        OFFSET {offset}
        """
    results = execute_sparql(query)
    return [
        ElementInfo(
            uri=r.get("uri", ""),
            name=r.get("name"),
            category=r.get("category"),
            original_type=r.get("originalType"),
        )
        for r in results
    ]
