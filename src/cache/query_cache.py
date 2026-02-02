"""SPARQL 쿼리 결과 캐싱 모듈.

인메모리 LRU 캐시로 동일 쿼리의 반복 실행을 방지합니다.
"""

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


class QueryCache:
    """LRU 기반 SPARQL 쿼리 결과 캐시.

    Args:
        max_size: 최대 캐시 엔트리 수
        ttl: 캐시 항목 유효 시간(초). 0이면 만료 없음.
    """

    def __init__(self, max_size: int = 256, ttl: int = 300):
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
        self._hits = 0
        self._misses = 0

    def get(self, query: str) -> Any | None:
        """캐시에서 쿼리 결과를 조회한다."""
        key = self._key(query)
        if key in self._cache:
            ts, result = self._cache[key]
            if self._ttl > 0 and (time.time() - ts) > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            # LRU: 최근 사용된 항목을 끝으로 이동
            self._cache.move_to_end(key)
            self._hits += 1
            return result
        self._misses += 1
        return None

    def put(self, query: str, result: Any):
        """쿼리 결과를 캐시에 저장한다."""
        key = self._key(query)
        self._cache[key] = (time.time(), result)
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def invalidate(self):
        """전체 캐시를 초기화한다."""
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        return {
            "size": self.size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.1%}",
        }

    def _key(self, query: str) -> str:
        normalized = " ".join(query.split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
