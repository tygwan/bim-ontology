"""FastAPI 서버 애플리케이션.

IFC → RDF 온톨로지 데이터에 대한 SPARQL 및 REST API를 제공합니다.
웹 대시보드를 포함합니다.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import sparql, buildings, statistics
from .routes import reasoning, properties, ontology_editor, lean_layer
from .utils.query_executor import init_store
from ..storage import TripleStore

# Optional imports for IFC processing (requires ifcopenshell)
try:
    from ..parser import IFCParser
    from ..converter import RDFConverter
    IFC_SUPPORT = True
except ImportError:
    IFCParser = None
    RDFConverter = None
    IFC_SUPPORT = False

logger = logging.getLogger(__name__)

import os

# 기본 파일 경로 (환경변수로 오버라이드 가능)
DEFAULT_IFC_PATH = os.getenv("BIM_IFC_PATH", "references/nwd4op-12.ifc")
DEFAULT_RDF_PATH = os.getenv("BIM_RDF_PATH", "data/rdf/navis-via-csv-v3.ttl")


def load_data(ifc_path: str | None = None, rdf_path: str | None = None) -> TripleStore:
    """IFC 파일 또는 기존 RDF 파일에서 데이터를 로딩한다."""
    store = TripleStore()

    # 기존 RDF 파일이 있으면 직접 로딩 (빠름)
    rdf_file = Path(rdf_path) if rdf_path else Path(DEFAULT_RDF_PATH)
    if rdf_file.exists():
        logger.info("기존 RDF 파일 로딩: %s", rdf_file)
        store.load(str(rdf_file))
        return store

    # IFC 파일에서 변환 (ifcopenshell 필요)
    ifc_file = Path(ifc_path) if ifc_path else Path(DEFAULT_IFC_PATH)
    if ifc_file.exists() and IFC_SUPPORT:
        logger.info("IFC 파일 변환: %s", ifc_file)
        parser = IFCParser(str(ifc_file))
        parser.open()

        converter = RDFConverter(schema=parser.get_schema())
        graph = converter.convert_file(parser)

        store = TripleStore(graph)

        # 변환 결과 캐싱
        rdf_file.parent.mkdir(parents=True, exist_ok=True)
        store.save(str(rdf_file))
        logger.info("RDF 캐시 저장: %s", rdf_file)
        return store
    elif ifc_file.exists() and not IFC_SUPPORT:
        logger.warning("IFC file found but ifcopenshell not installed. Cannot convert.")

    raise FileNotFoundError(
        f"IFC 파일({ifc_file}) 또는 RDF 파일({rdf_file})을 찾을 수 없습니다."
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 데이터 로딩/정리."""
    store = load_data()
    init_store(store)
    logger.info("서버 시작: %d 트리플 로딩됨", len(store))
    yield
    logger.info("서버 종료")


def create_app(store: TripleStore | None = None) -> FastAPI:
    """FastAPI 앱 인스턴스를 생성한다.

    Args:
        store: 테스트 시 주입할 TripleStore. None이면 lifespan에서 자동 로딩.
    """
    if store is not None:
        # 테스트 모드: lifespan 없이 직접 스토어 주입
        app = FastAPI(
            title="BIM Ontology API",
            description="IFC → RDF 온톨로지 SPARQL 쿼리 엔드포인트",
            version="1.0.0",
        )
        init_store(store)
    else:
        app = FastAPI(
            title="BIM Ontology API",
            description="IFC → RDF 온톨로지 SPARQL 쿼리 엔드포인트",
            version="1.0.0",
            lifespan=lifespan,
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(sparql.router, prefix="/api", tags=["SPARQL"])
    app.include_router(buildings.router, prefix="/api", tags=["Buildings"])
    app.include_router(statistics.router, prefix="/api", tags=["Statistics"])
    app.include_router(reasoning.router, prefix="/api", tags=["Reasoning"])
    app.include_router(properties.router, prefix="/api", tags=["Properties"])
    app.include_router(ontology_editor.router, prefix="/api", tags=["Ontology"])
    app.include_router(lean_layer.router, prefix="/api", tags=["Lean Layer"])

    @app.get("/health", tags=["Health"])
    async def health():
        from .utils.query_executor import get_store
        try:
            s = get_store()
            return {"status": "healthy", "triples": len(s)}
        except RuntimeError:
            return {"status": "unhealthy", "triples": 0}

    # 대시보드 정적 파일 서빙
    dashboard_dir = Path(__file__).parent.parent / "dashboard"
    if dashboard_dir.exists():
        app.mount("/static", StaticFiles(directory=str(dashboard_dir)), name="static")

        @app.get("/", tags=["Dashboard"])
        async def dashboard():
            return FileResponse(str(dashboard_dir / "index.html"))
    else:
        @app.get("/", tags=["Health"])
        async def root():
            return {"service": "BIM Ontology API", "version": "2.0.0"}

    return app


# uvicorn 직접 실행용
app = create_app()
