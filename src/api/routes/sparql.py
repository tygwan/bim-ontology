"""SPARQL 쿼리 엔드포인트."""

from fastapi import APIRouter, HTTPException

from ..models.request import SPARQLRequest
from ..models.response import SPARQLResponse, ErrorResponse
from ..utils.query_executor import execute_sparql

router = APIRouter()


@router.post(
    "/sparql",
    response_model=SPARQLResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="SPARQL 쿼리 실행",
    description="SPARQL SELECT 쿼리를 실행하고 결과를 JSON으로 반환합니다.",
)
async def post_sparql(request: SPARQLRequest):
    try:
        results = execute_sparql(request.query)
        return SPARQLResponse(
            status="success",
            results=results,
            count=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
