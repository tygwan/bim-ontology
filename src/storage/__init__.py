import os

from .base_store import BaseTripleStore
from .triple_store import TripleStore


def create_store(backend: str | None = None) -> BaseTripleStore:
    """백엔드 설정에 따라 적절한 TripleStore를 생성한다.

    Args:
        backend: "local" (기본값) 또는 "graphdb"

    Returns:
        BaseTripleStore 구현체
    """
    backend = backend or os.getenv("TRIPLESTORE_BACKEND", "local")

    if backend == "graphdb":
        from .graphdb_store import GraphDBStore
        return GraphDBStore()

    return TripleStore()


__all__ = ["BaseTripleStore", "TripleStore", "create_store"]
