"""OWL/RDFS 추론 API 라우트."""

import logging

from fastapi import APIRouter, HTTPException

from ..utils.query_executor import get_store
from ...inference.reasoner import OWLReasoner

logger = logging.getLogger(__name__)

router = APIRouter()


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
