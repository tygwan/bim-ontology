"""속성 조회 API 라우트.

Smart3D Plant PropertySet을 포함한 요소별 속성 조회를 제공합니다.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..utils.query_executor import get_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/properties/{global_id}")
async def get_element_properties(global_id: str):
    """특정 요소의 모든 PropertySet을 반환한다."""
    store = get_store()
    rows = store.query(f"""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?pset_name ?prop_name ?prop_value
        WHERE {{
            ?elem bim:hasGlobalId "{global_id}" .
            ?elem bim:hasPropertySet ?pset .
            ?pset bim:hasName ?pset_name .
            ?pset bim:hasProperty ?prop .
            ?prop bim:hasName ?prop_name .
            OPTIONAL {{ ?prop bim:hasPropertyValue ?prop_value }}
        }}
        ORDER BY ?pset_name ?prop_name
    """)

    if not rows:
        raise HTTPException(status_code=404, detail=f"Element {global_id} not found or has no properties")

    # PropertySet별로 그룹화
    psets: dict[str, dict] = {}
    for row in rows:
        pset_name = row["pset_name"]
        if pset_name not in psets:
            psets[pset_name] = {"name": pset_name, "properties": {}}
        psets[pset_name]["properties"][row["prop_name"]] = row.get("prop_value")

    return {"global_id": global_id, "property_sets": list(psets.values())}


@router.get("/properties/plant-data")
async def get_plant_data():
    """Smart3D Plant 데이터 요약을 반환한다."""
    store = get_store()

    # PlantPropertySet 통계
    plant_psets = store.query("""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?pset_name (COUNT(?prop) AS ?prop_count)
        WHERE {
            ?pset rdf:type bim:PlantPropertySet .
            ?pset bim:hasName ?pset_name .
            ?pset bim:hasProperty ?prop .
        }
        GROUP BY ?pset_name
        ORDER BY DESC(?prop_count)
    """)

    # 전체 PropertySet 수
    total = store.query("""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(DISTINCT ?pset) AS ?num)
        WHERE { ?pset rdf:type bim:PropertySet }
    """)

    plant_total = store.query("""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(DISTINCT ?pset) AS ?num)
        WHERE { ?pset rdf:type bim:PlantPropertySet }
    """)

    return {
        "total_property_sets": total[0]["num"] if total else 0,
        "plant_property_sets": plant_total[0]["num"] if plant_total else 0,
        "plant_pset_details": plant_psets,
    }


@router.get("/properties/search")
async def search_properties(
    key: str = Query(..., description="Property key to search"),
    value: Optional[str] = Query(None, description="Property value filter"),
    min_val: Optional[float] = Query(None, alias="min", description="Minimum numeric value"),
    max_val: Optional[float] = Query(None, alias="max", description="Maximum numeric value"),
    limit: int = Query(50, ge=1, le=500),
):
    """속성 키/값으로 검색한다."""
    store = get_store()

    filters = [f'?prop bim:hasName "{key}"']
    if value:
        filters.append(f'FILTER(STR(?val) = "{value}")')
    if min_val is not None:
        filters.append(f"FILTER(xsd:double(?val) >= {min_val})")
    if max_val is not None:
        filters.append(f"FILTER(xsd:double(?val) <= {max_val})")

    filter_str = " .\n            ".join(filters)

    rows = store.query(f"""
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?elem_name ?pset_name ?val
        WHERE {{
            ?pset bim:hasProperty ?prop .
            {filter_str} .
            ?prop bim:hasPropertyValue ?val .
            ?pset bim:hasName ?pset_name .
            ?elem bim:hasPropertySet ?pset .
            ?elem bim:hasName ?elem_name .
        }}
        LIMIT {limit}
    """)

    return {"key": key, "count": len(rows), "results": rows}
