"""공유 테스트 픽스처 및 마커 정의.

IFC 파일 의존성을 분리하여 CI에서 IFC 없이도 테스트를 실행할 수 있게 합니다.
"""

import pytest
from pathlib import Path

IFC_PATH = Path("references/nwd4op-12.ifc")
RDF_PATH = Path("data/rdf/nwd4op-12.ttl")

requires_ifc = pytest.mark.skipif(
    not IFC_PATH.exists(),
    reason="IFC test data not available (references/nwd4op-12.ifc)",
)


@pytest.fixture
def rdf_store():
    """RDF 파일만으로 TripleStore를 생성하는 fixture (IFC 불필요)."""
    from src.storage import TripleStore

    store = TripleStore()
    if RDF_PATH.exists():
        store.load(str(RDF_PATH))
    return store
