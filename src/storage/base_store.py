"""Triple Store 추상 베이스 클래스.

로컬(rdflib)과 외부(GraphDB) 스토어의 공통 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTripleStore(ABC):
    """Triple Store 공통 인터페이스."""

    @abstractmethod
    def query(self, sparql: str) -> list[dict[str, Any]]:
        """SPARQL SELECT 쿼리를 실행한다."""
        ...

    @abstractmethod
    def insert(self, triples: list[tuple]) -> int:
        """트리플 리스트를 삽입한다."""
        ...

    @abstractmethod
    def count(self) -> int:
        """전체 트리플 수를 반환한다."""
        ...

    @abstractmethod
    def load(self, filepath: str) -> int:
        """파일에서 트리플을 로딩한다."""
        ...

    @abstractmethod
    def save(self, filepath: str) -> str:
        """그래프를 파일로 저장한다."""
        ...

    def __len__(self) -> int:
        return self.count()
