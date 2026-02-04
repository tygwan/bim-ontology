"""Lean Layer REST API 라우트.

Schedule, AWP, Status, Equipment 데이터 주입 및 조회 엔드포인트.
"""

import logging
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from ..utils.query_executor import get_store
from ...converter.lean_layer_injector import LeanLayerInjector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lean")

_PREFIXES = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bim:  <http://example.org/bim-ontology/schema#>
PREFIX sched: <http://example.org/bim-ontology/schedule#>
PREFIX awp:  <http://example.org/bim-ontology/awp#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
"""


def _get_injector() -> LeanLayerInjector:
    store = get_store()
    return LeanLayerInjector(store.graph)


async def _save_upload(upload: UploadFile) -> str:
    """업로드된 파일을 임시 파일로 저장한다."""
    content = await upload.read()
    suffix = Path(upload.filename or "data.csv").suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(content)
    tmp.close()
    return tmp.name


# ── CSV Injection Endpoints ──


@router.post("/inject/schedule")
async def inject_schedule(file: UploadFile = File(...)):
    """일정 CSV를 주입한다.

    CSV 컬럼: GlobalId, TaskName, PlannedStart, PlannedEnd, ActualStart, ActualEnd,
              PlannedInstallDate, DeliveryStatus, CWP_ID, UnitCost
    """
    tmp_path = await _save_upload(file)
    try:
        injector = _get_injector()
        injector.load_lean_schema()
        result = injector.inject_schedule_csv(tmp_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Schedule injection failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/inject/awp")
async def inject_awp(file: UploadFile = File(...)):
    """AWP CSV를 주입한다.

    CSV 컬럼: GlobalId, CWA_ID, CWP_ID, IWP_ID, IWP_StartDate, IWP_EndDate,
              ConstraintStatus
    """
    tmp_path = await _save_upload(file)
    try:
        injector = _get_injector()
        injector.load_lean_schema()
        result = injector.inject_awp_csv(tmp_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("AWP injection failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/inject/status")
async def inject_status(file: UploadFile = File(...)):
    """상태 CSV를 주입한다.

    CSV 컬럼: GlobalId, StatusValue, StatusDate, DeliveryStatus
    """
    tmp_path = await _save_upload(file)
    try:
        injector = _get_injector()
        injector.load_lean_schema()
        result = injector.inject_status_csv(tmp_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Status injection failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/inject/equipment")
async def inject_equipment(file: UploadFile = File(...)):
    """장비 CSV를 주입한다.

    CSV 컬럼: EquipmentID, Name, Width, Height, TurningRadius,
              BoomLength, LoadCapacity, AccessZone_CWA_ID
    """
    tmp_path = await _save_upload(file)
    try:
        injector = _get_injector()
        injector.load_lean_schema()
        result = injector.inject_equipment_csv(tmp_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Equipment injection failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ── Status Update Endpoint ──


class StatusUpdateRequest(BaseModel):
    status_value: str
    delivery_status: str = ""


@router.put("/status/{global_id}")
async def update_status(global_id: str, req: StatusUpdateRequest):
    """단일 요소의 상태를 업데이트한다."""
    valid_statuses = {"Planned", "Designed", "Fabricated", "Shipped",
                      "OnSite", "Installed", "Inspected"}
    if req.status_value not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status_value. Must be one of: {valid_statuses}")

    injector = _get_injector()
    result = injector.update_element_status(
        global_id, req.status_value, req.delivery_status)

    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Unknown error"))
    return result


# ── Query Endpoints ──


@router.get("/today")
async def get_todays_work(target_date: Optional[str] = None):
    """오늘 할 일 (AWP 기반)을 조회한다."""
    if not target_date:
        target_date = date.today().isoformat()

    store = get_store()
    query = _PREFIXES + f"""
    SELECT ?iwp ?iwpName ?cwpName ?cwaName ?startDate ?endDate
           ?constraintStatus ?isExecutable
           (COUNT(DISTINCT ?elem) AS ?elementCount)
    WHERE {{
        ?iwp a awp:InstallationWorkPackage .
        ?iwp awp:hasStartDate ?startDate .
        ?iwp awp:hasEndDate ?endDate .
        FILTER(?startDate <= "{target_date}"^^xsd:date && ?endDate >= "{target_date}"^^xsd:date)
        OPTIONAL {{ ?iwp rdfs:label ?iwpName }}
        OPTIONAL {{ ?iwp awp:hasConstraintStatus ?constraintStatus }}
        OPTIONAL {{ ?iwp awp:isExecutable ?isExecutable }}
        OPTIONAL {{
            ?iwp awp:belongsToCWP ?cwp .
            OPTIONAL {{ ?cwp rdfs:label ?cwpName }}
            OPTIONAL {{
                ?cwp awp:belongsToCWA ?cwa .
                OPTIONAL {{ ?cwa rdfs:label ?cwaName }}
            }}
        }}
        OPTIONAL {{ ?iwp awp:includesElement ?elem }}
    }}
    GROUP BY ?iwp ?iwpName ?cwpName ?cwaName ?startDate ?endDate
             ?constraintStatus ?isExecutable
    ORDER BY ?cwaName ?cwpName ?iwpName
    """
    results = list(store.graph.query(query))
    return {
        "target_date": target_date,
        "iwp_count": len(results),
        "work_packages": [
            {
                "iwp": str(r.iwpName or ""),
                "cwp": str(r.cwpName or ""),
                "cwa": str(r.cwaName or ""),
                "start_date": str(r.startDate or ""),
                "end_date": str(r.endDate or ""),
                "constraint_status": str(r.constraintStatus or ""),
                "is_executable": str(r.isExecutable or ""),
                "element_count": int(r.elementCount),
            }
            for r in results
        ],
    }


@router.get("/delayed")
async def get_delayed_elements(reference_date: Optional[str] = None):
    """지연 부재를 조회한다."""
    if not reference_date:
        reference_date = date.today().isoformat()

    store = get_store()
    query = _PREFIXES + f"""
    SELECT ?elem ?name ?category ?plannedDate ?deliveryStatus ?isDelayed
    WHERE {{
        ?elem a bim:PhysicalElement .
        ?elem sched:hasPlannedInstallDate ?plannedDate .
        OPTIONAL {{ ?elem bim:hasName ?name }}
        OPTIONAL {{ ?elem bim:hasCategory ?category }}
        OPTIONAL {{ ?elem bim:hasDeliveryStatus ?deliveryStatus }}
        OPTIONAL {{ ?elem bim:isDelayed ?isDelayed }}
        FILTER(?deliveryStatus NOT IN ("Installed", "Inspected"))
        FILTER(?plannedDate < "{reference_date}"^^xsd:date)
    }}
    ORDER BY ?plannedDate
    LIMIT 200
    """
    results = list(store.graph.query(query))
    return {
        "reference_date": reference_date,
        "delayed_count": len(results),
        "elements": [
            {
                "name": str(r.name or ""),
                "category": str(r.category or ""),
                "planned_date": str(r.plannedDate or ""),
                "delivery_status": str(r.deliveryStatus or ""),
                "is_delayed": str(r.isDelayed or ""),
            }
            for r in results
        ],
    }


@router.get("/iwp/{iwp_id}/constraints")
async def get_iwp_constraints(iwp_id: str):
    """IWP의 제약 조건 및 포함 요소를 조회한다."""
    store = get_store()
    query = _PREFIXES + f"""
    SELECT ?iwpName ?startDate ?endDate ?constraintStatus ?isExecutable
           ?elem ?elemName ?elemCategory ?deliveryStatus ?isReady
    WHERE {{
        ?iwp rdfs:label "{iwp_id}" .
        ?iwp a awp:InstallationWorkPackage .
        OPTIONAL {{ ?iwp rdfs:label ?iwpName }}
        OPTIONAL {{ ?iwp awp:hasStartDate ?startDate }}
        OPTIONAL {{ ?iwp awp:hasEndDate ?endDate }}
        OPTIONAL {{ ?iwp awp:hasConstraintStatus ?constraintStatus }}
        OPTIONAL {{ ?iwp awp:isExecutable ?isExecutable }}
        OPTIONAL {{
            ?iwp awp:includesElement ?elem .
            OPTIONAL {{ ?elem bim:hasName ?elemName }}
            OPTIONAL {{ ?elem bim:hasCategory ?elemCategory }}
            OPTIONAL {{ ?elem bim:hasDeliveryStatus ?deliveryStatus }}
            OPTIONAL {{ ?elem bim:isReady ?isReady }}
        }}
    }}
    ORDER BY ?elemName
    """
    results = list(store.graph.query(query))
    if not results:
        raise HTTPException(status_code=404, detail=f"IWP not found: {iwp_id}")

    first = results[0]
    elements = [
        {
            "name": str(r.elemName or ""),
            "category": str(r.elemCategory or ""),
            "delivery_status": str(r.deliveryStatus or ""),
            "is_ready": str(r.isReady or ""),
        }
        for r in results if r.elem
    ]
    return {
        "iwp": str(first.iwpName or ""),
        "start_date": str(first.startDate or ""),
        "end_date": str(first.endDate or ""),
        "constraint_status": str(first.constraintStatus or ""),
        "is_executable": str(first.isExecutable or ""),
        "element_count": len(elements),
        "elements": elements,
    }


@router.get("/stats")
async def get_lean_stats():
    """Lean Layer 주입 현황 통계를 반환한다."""
    injector = _get_injector()
    return injector.get_lean_layer_stats()
