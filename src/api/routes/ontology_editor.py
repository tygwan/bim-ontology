"""온톨로지 스키마 편집 API 라우트.

Object Type, Property Type, Link Type, Classification Rules CRUD를 제공합니다.
"""

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..utils.query_executor import get_store
from ...ontology.schema_manager import OntologySchemaManager

logger = logging.getLogger(__name__)

router = APIRouter()

# 싱글톤 스키마 매니저
_manager: OntologySchemaManager | None = None


def _get_manager() -> OntologySchemaManager:
    global _manager
    if _manager is None:
        store = get_store()
        _manager = OntologySchemaManager(graph=store.graph)
    return _manager


# ---------- Request Models ----------

class CreateTypeRequest(BaseModel):
    name: str
    parent_class: str = "BIMElement"
    label: str = ""
    description: str = ""


class UpdateTypeRequest(BaseModel):
    parent_class: str | None = None
    label: str | None = None
    description: str | None = None


class CreatePropertyRequest(BaseModel):
    name: str
    domain: str = "BIMElement"
    range_type: str = "string"
    label: str = ""


class CreateLinkRequest(BaseModel):
    name: str
    domain: str
    range_class: str
    inverse_name: str = ""
    label: str = ""


class UpdateRulesRequest(BaseModel):
    rules: dict[str, list[str]]


# ---------- Object Types ----------

@router.get("/ontology/types")
async def list_types():
    mgr = _get_manager()
    types = mgr.list_object_types()
    return [{"name": t.name, "parent_class": t.parent_class, "label": t.label, "description": t.description} for t in types]


@router.post("/ontology/types")
async def create_type(req: CreateTypeRequest):
    mgr = _get_manager()
    info = mgr.create_object_type(req.name, req.parent_class, req.label, req.description)
    return {"name": info.name, "parent_class": info.parent_class, "label": info.label}


@router.put("/ontology/types/{name}")
async def update_type(name: str, req: UpdateTypeRequest):
    mgr = _get_manager()
    try:
        kwargs = {k: v for k, v in req.model_dump().items() if v is not None}
        info = mgr.update_object_type(name, **kwargs)
        return {"name": info.name, "parent_class": info.parent_class, "label": info.label}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Type '{name}' not found")


@router.delete("/ontology/types/{name}")
async def delete_type(name: str):
    mgr = _get_manager()
    if mgr.delete_object_type(name):
        return {"deleted": True, "name": name}
    raise HTTPException(status_code=404, detail=f"Type '{name}' not found")


# ---------- Property Types ----------

@router.get("/ontology/properties")
async def list_properties():
    mgr = _get_manager()
    props = mgr.list_property_types()
    return [{"name": p.name, "domain": p.domain, "range_type": p.range_type, "label": p.label} for p in props]


@router.post("/ontology/properties")
async def create_property(req: CreatePropertyRequest):
    mgr = _get_manager()
    info = mgr.create_property_type(req.name, req.domain, req.range_type, req.label)
    return {"name": info.name, "domain": info.domain, "range_type": info.range_type}


# ---------- Link Types ----------

@router.get("/ontology/links")
async def list_links():
    mgr = _get_manager()
    links = mgr.list_link_types()
    return [{"name": l.name, "domain": l.domain, "range_class": l.range_class, "inverse_name": l.inverse_name} for l in links]


@router.post("/ontology/links")
async def create_link(req: CreateLinkRequest):
    mgr = _get_manager()
    info = mgr.create_link_type(req.name, req.domain, req.range_class, req.inverse_name, req.label)
    return {"name": info.name, "domain": info.domain, "range_class": info.range_class}


# ---------- Classification Rules ----------

@router.get("/ontology/rules")
async def get_rules():
    mgr = _get_manager()
    return mgr.list_classification_rules()


@router.put("/ontology/rules")
async def update_rules(req: UpdateRulesRequest):
    mgr = _get_manager()
    mgr.update_classification_rules(req.rules)
    return {"updated": True, "rule_count": len(req.rules)}


# ---------- Schema Operations ----------

@router.post("/ontology/apply")
async def apply_schema():
    mgr = _get_manager()
    store = get_store()
    added = mgr.apply_schema_to_graph(store.graph)
    return {"triples_added": added, "total_triples": len(store)}


@router.get("/ontology/export")
async def export_schema():
    mgr = _get_manager()
    return {"schema": mgr.export_schema()}


@router.post("/ontology/import")
async def import_schema(request: Request):
    body = await request.json()
    schema_data = body.get("schema", "")
    if not schema_data:
        raise HTTPException(status_code=400, detail="schema field required")
    mgr = _get_manager()
    mgr.import_schema(schema_data if isinstance(schema_data, str) else json.dumps(schema_data))
    return {"imported": True}
