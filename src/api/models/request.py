"""API 요청 모델."""

from pydantic import BaseModel, Field


class SPARQLRequest(BaseModel):
    query: str = Field(..., description="SPARQL 쿼리 문자열", min_length=1)


class QueryByTypeRequest(BaseModel):
    entity_type: str = Field(..., description="IFC 엔티티 타입 또는 BIM 카테고리명")
    limit: int = Field(100, ge=1, le=10000)
    offset: int = Field(0, ge=0)
