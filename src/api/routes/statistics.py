"""통계 API."""

from fastapi import APIRouter

from ..models.response import OverallStats, CategoryStat, HierarchyNode
from ..utils.query_executor import execute_sparql, get_store
from ..queries.templates import (
    get_component_statistics,
    get_building_hierarchy,
    get_overall_statistics,
)

router = APIRouter()


@router.get(
    "/statistics",
    response_model=OverallStats,
    summary="전체 통계 조회",
)
async def overall_statistics():
    store = get_store()
    total_triples = store.count()

    # 카테고리별 통계
    cat_results = execute_sparql(get_component_statistics())
    categories = [
        CategoryStat(category=r["category"], count=r["num"])
        for r in cat_results
    ]

    # 전체 통계
    stats_results = execute_sparql(get_overall_statistics())
    if stats_results:
        s = stats_results[0]
        return OverallStats(
            total_triples=total_triples,
            total_elements=s.get("totalElements", 0),
            total_categories=s.get("totalCategories", 0),
            buildings=s.get("buildings", 0),
            storeys=s.get("storeys", 0),
            categories=categories,
        )
    return OverallStats(
        total_triples=total_triples,
        total_elements=0,
        total_categories=0,
        buildings=0,
        storeys=0,
        categories=categories,
    )


@router.get(
    "/statistics/categories",
    response_model=list[CategoryStat],
    summary="카테고리별 통계",
)
async def category_statistics():
    results = execute_sparql(get_component_statistics())
    return [
        CategoryStat(category=r["category"], count=r["num"])
        for r in results
    ]


@router.get(
    "/hierarchy",
    summary="건물 계층 구조 조회",
)
async def building_hierarchy():
    results = execute_sparql(get_building_hierarchy())
    return results
