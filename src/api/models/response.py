"""API 응답 모델."""

from typing import Any
from pydantic import BaseModel, Field


class SPARQLResponse(BaseModel):
    status: str = "success"
    results: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: str | None = None


class BuildingInfo(BaseModel):
    uri: str
    global_id: str | None = None
    name: str | None = None


class StoreyInfo(BaseModel):
    uri: str
    global_id: str | None = None
    name: str | None = None
    elevation: float | None = None
    element_count: int = 0


class ElementInfo(BaseModel):
    uri: str
    name: str | None = None
    category: str | None = None
    original_type: str | None = None


class CategoryStat(BaseModel):
    category: str
    count: int


class OverallStats(BaseModel):
    total_triples: int
    total_elements: int
    total_categories: int
    buildings: int
    storeys: int
    categories: list[CategoryStat]


class HierarchyNode(BaseModel):
    uri: str
    name: str | None = None
    node_type: str
    children: list["HierarchyNode"] = Field(default_factory=list)
