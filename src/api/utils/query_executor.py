"""SPARQL 쿼리 실행 유틸리티.

TripleStore에 대한 쿼리 실행과 결과 포맷팅을 담당합니다.
"""

import logging
from typing import Any

from ...storage import TripleStore

logger = logging.getLogger(__name__)

# 전역 스토어 인스턴스 (서버 시작 시 초기화)
_store: TripleStore | None = None


def get_store() -> TripleStore:
    """현재 TripleStore 인스턴스를 반환한다."""
    if _store is None:
        raise RuntimeError("TripleStore가 초기화되지 않았습니다. init_store()를 호출하세요.")
    return _store


def init_store(store: TripleStore):
    """전역 TripleStore를 설정한다."""
    global _store
    _store = store
    logger.info("TripleStore 초기화 완료: %d 트리플", len(store))


def execute_sparql(query: str) -> list[dict[str, Any]]:
    """SPARQL 쿼리를 실행하고 결과를 반환한다."""
    store = get_store()
    return store.query(query)


def reload_store(ttl_path: str) -> int:
    """새로운 TTL 파일로 스토어를 다시 로드한다.

    Args:
        ttl_path: 로드할 TTL 파일의 절대 경로

    Returns:
        로드된 트리플 수
    """
    global _store
    new_store = TripleStore()
    new_store.load(ttl_path)
    _store = new_store
    logger.info("TripleStore 재로드 완료: %s (%d 트리플)", ttl_path, len(new_store))
    return len(new_store)
