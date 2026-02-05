"""Lean Layer 통합 주입 모듈.

Backbone RDF 그래프에 Schedule, Status, AWP, Equipment 데이터를
Lean Layer 온톨로지로 주입하는 통합 인터페이스를 제공한다.

Phase 16에서 검증된 Method B (CSV→RDF) + Method C (Schema Manager) 기반.
"""

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rdflib import Graph, Literal, URIRef, RDF, RDFS, XSD, Namespace

from .namespace_manager import BIM, INST, SCHED, AWP

logger = logging.getLogger(__name__)

LEAN_SCHEMA_PATH = Path("data/ontology/lean_schema.ttl")

# GlobalId → 요소 URI 매핑 SPARQL
_FIND_ELEMENT_BY_GLOBALID = """
PREFIX bim: <http://example.org/bim-ontology/schema#>
SELECT ?elem WHERE {{
    ?elem bim:hasGlobalId "{global_id}" .
}}
LIMIT 1
"""

# ObjectId/SyncID → 요소 URI 매핑 SPARQL
_FIND_ELEMENT_BY_OBJECTID = """
PREFIX navis: <http://example.org/bim-ontology/navis#>
SELECT ?elem WHERE {{
    ?elem navis:hasObjectId "{object_id}" .
}}
LIMIT 1
"""

# 값 타입 매핑
_TYPE_MAP = {
    "string": XSD.string,
    "double": XSD.double,
    "integer": XSD.integer,
    "boolean": XSD.boolean,
    "date": XSD.date,
    "dateTime": XSD.dateTime,
}


class LeanLayerInjector:
    """Lean Layer 통합 주입기.

    Backbone RDF 그래프에 Schedule/Status/AWP/Equipment 데이터를 주입한다.
    """

    def __init__(self, graph: Graph):
        self._graph = graph
        self._globalid_cache: dict[str, URIRef] = {}
        self._objectid_cache: dict[str, URIRef] = {}
        self._schema_loaded = False

    def load_lean_schema(self, schema_path: str | None = None) -> int:
        """Lean Layer 온톨로지 스키마를 그래프에 로딩한다.

        Returns:
            추가된 트리플 수
        """
        path = Path(schema_path) if schema_path else LEAN_SCHEMA_PATH
        if not path.exists():
            raise FileNotFoundError(f"Lean schema not found: {path}")

        before = len(self._graph)
        self._graph.parse(str(path), format="turtle")
        added = len(self._graph) - before
        self._schema_loaded = True
        logger.info("Lean Layer 스키마 로딩: +%d triples from %s", added, path.name)
        return added

    def _resolve_element(self, global_id: str = "", object_id: str = "") -> Optional[URIRef]:
        """GlobalId 또는 ObjectId/SyncID로 RDF 그래프에서 요소 URI를 찾는다."""
        if global_id:
            if global_id in self._globalid_cache:
                return self._globalid_cache[global_id]

            query = _FIND_ELEMENT_BY_GLOBALID.format(global_id=global_id)
            results = list(self._graph.query(query))
            if results:
                uri = results[0].elem
                self._globalid_cache[global_id] = uri
                return uri

        if object_id:
            if object_id in self._objectid_cache:
                return self._objectid_cache[object_id]

            query = _FIND_ELEMENT_BY_OBJECTID.format(object_id=object_id)
            results = list(self._graph.query(query))
            if results:
                uri = results[0].elem
                self._objectid_cache[object_id] = uri
                return uri

        return None

    @staticmethod
    def _extract_row_ids(row: dict) -> tuple[str, str]:
        """CSV 행에서 식별자를 추출한다.

        우선순위:
        - GlobalId: IFC 경로 호환
        - ObjectId 또는 SyncID: Navis CSV 경로
        """
        global_id = row.get("GlobalId", "").strip()
        object_id = row.get("ObjectId", "").strip()
        if not object_id:
            object_id = row.get("SyncID", "").strip()
        return global_id, object_id

    @staticmethod
    def _parse_duration_days(value: str) -> Optional[int]:
        """Duration 문자열을 일(day) 정수로 파싱한다.

        숫자 문자열(`7`, `7.0`)만 지원한다.
        """
        text = (value or "").strip()
        if not text:
            return None
        try:
            return int(float(text))
        except ValueError:
            return None

    def _read_csv(self, csv_path: str) -> list[dict]:
        """CSV 파일을 읽어 딕셔너리 리스트로 반환한다."""
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ── Schedule Injection ──

    def inject_schedule_csv(self, csv_path: str) -> dict:
        """일정 CSV를 주입한다. ConstructionTask 인스턴스를 생성하고 요소와 연결한다.

        CSV 컬럼:
        - 식별자: GlobalId | ObjectId | SyncID
        - 일정: TaskName, PlannedStart, PlannedEnd, ActualStart, ActualEnd
        - 기간/비용: Duration, PlannedDuration, ActualDuration, UnitCost, Cost
        """
        rows = self._read_csv(csv_path)
        g = self._graph
        triples_added = 0
        tasks_created: dict[str, URIRef] = {}
        elements_matched = 0
        not_found = []

        for row in rows:
            global_id, object_id = self._extract_row_ids(row)
            task_name = row.get("TaskName", "").strip()
            if not global_id and not object_id:
                continue

            elem_uri = self._resolve_element(global_id=global_id, object_id=object_id)
            if elem_uri is None:
                not_found.append(global_id or object_id)
                continue

            elements_matched += 1
            planned_duration_raw = row.get("PlannedDuration", "").strip() or row.get("Duration", "").strip()
            actual_duration_raw = row.get("ActualDuration", "").strip()
            planned_duration_days = self._parse_duration_days(planned_duration_raw)
            actual_duration_days = self._parse_duration_days(actual_duration_raw)

            # Task 인스턴스 생성 (같은 TaskName은 하나의 Task로)
            if task_name and task_name not in tasks_created:
                task_id = task_name.replace(" ", "_").replace("/", "_")
                task_uri = INST[f"task_{task_id}"]
                g.add((task_uri, RDF.type, SCHED.ConstructionTask))
                g.add((task_uri, RDFS.label, Literal(task_name)))
                triples_added += 2

                for col, prop, dtype in [
                    ("PlannedStart", SCHED.hasPlannedStart, XSD.date),
                    ("PlannedEnd", SCHED.hasPlannedEnd, XSD.date),
                    ("ActualStart", SCHED.hasActualStart, XSD.date),
                    ("ActualEnd", SCHED.hasActualEnd, XSD.date),
                ]:
                    val = row.get(col, "").strip()
                    if val:
                        g.add((task_uri, prop, Literal(val, datatype=dtype)))
                        triples_added += 1

                # Legacy duration (문자열) 유지
                if planned_duration_raw:
                    g.add((task_uri, SCHED.hasDuration, Literal(planned_duration_raw, datatype=XSD.string)))
                    triples_added += 1
                # 타입형 duration 추가
                if planned_duration_days is not None:
                    g.add((task_uri, SCHED.hasPlannedDuration, Literal(planned_duration_days, datatype=XSD.integer)))
                    triples_added += 1
                if actual_duration_days is not None:
                    g.add((task_uri, SCHED.hasActualDuration, Literal(actual_duration_days, datatype=XSD.integer)))
                    triples_added += 1

                tasks_created[task_name] = task_uri

            # 요소 → Task 연결
            if task_name and task_name in tasks_created:
                task_uri = tasks_created[task_name]
                g.add((elem_uri, SCHED.assignedToTask, task_uri))
                g.add((task_uri, SCHED.hasAssignedElement, elem_uri))
                triples_added += 2

            # 요소 직접 속성
            for col, prop, dtype in [
                ("PlannedInstallDate", SCHED.hasPlannedInstallDate, XSD.date),
                ("DeliveryStatus", BIM.hasDeliveryStatus, XSD.string),
                ("CWP_ID", AWP.belongsToCWP_ID, XSD.string),
                ("UnitCost", BIM.hasUnitCost, XSD.double),
                ("Cost", BIM.hasUnitCost, XSD.double),
            ]:
                val = row.get(col, "").strip()
                if val:
                    try:
                        if dtype == XSD.double:
                            val = float(val)
                        g.add((elem_uri, prop, Literal(val, datatype=dtype)))
                        triples_added += 1
                    except ValueError:
                        logger.warning("Invalid numeric value skipped: %s=%s", col, val)

            # ObjectId별 consume duration 저장 (Actual 우선, 없으면 Planned)
            consume_days = actual_duration_days if actual_duration_days is not None else planned_duration_days
            if consume_days is not None:
                g.add((elem_uri, BIM.hasConsumeDuration, Literal(consume_days, datatype=XSD.integer)))
                triples_added += 1

        result = {
            "triples_added": triples_added,
            "tasks_created": len(tasks_created),
            "elements_matched": elements_matched,
            "elements_not_found": not_found,
        }
        logger.info("Schedule 주입 완료: %s", result)
        return result

    # ── AWP Injection ──

    def inject_awp_csv(self, csv_path: str) -> dict:
        """AWP CSV를 주입한다. CWA/CWP/IWP 계층을 구축하고 요소를 연결한다.

        CSV 컬럼:
        - 식별자: GlobalId | ObjectId | SyncID
        - AWP: CWA_ID, CWP_ID, IWP_ID, IWP_StartDate, IWP_EndDate, ConstraintStatus
        """
        rows = self._read_csv(csv_path)
        g = self._graph
        triples_added = 0
        cwa_cache: dict[str, URIRef] = {}
        cwp_cache: dict[str, URIRef] = {}
        iwp_cache: dict[str, URIRef] = {}
        elements_matched = 0

        for row in rows:
            global_id, object_id = self._extract_row_ids(row)
            cwa_id = row.get("CWA_ID", "").strip()
            cwp_id = row.get("CWP_ID", "").strip()
            iwp_id = row.get("IWP_ID", "").strip()

            if not global_id and not object_id:
                continue

            elem_uri = self._resolve_element(global_id=global_id, object_id=object_id)
            if elem_uri is None:
                continue

            elements_matched += 1

            # CWA 인스턴스
            if cwa_id and cwa_id not in cwa_cache:
                cwa_uri = INST[f"cwa_{cwa_id}"]
                g.add((cwa_uri, RDF.type, AWP.ConstructionWorkArea))
                g.add((cwa_uri, RDFS.label, Literal(cwa_id)))
                g.add((cwa_uri, BIM.hasName, Literal(cwa_id)))
                cwa_cache[cwa_id] = cwa_uri
                triples_added += 3

            # CWP 인스턴스
            if cwp_id and cwp_id not in cwp_cache:
                cwp_uri = INST[f"cwp_{cwp_id}"]
                g.add((cwp_uri, RDF.type, AWP.ConstructionWorkPackage))
                g.add((cwp_uri, RDFS.label, Literal(cwp_id)))
                g.add((cwp_uri, BIM.hasName, Literal(cwp_id)))
                if cwa_id and cwa_id in cwa_cache:
                    g.add((cwp_uri, AWP.belongsToCWA, cwa_cache[cwa_id]))
                    triples_added += 1
                cwp_cache[cwp_id] = cwp_uri
                triples_added += 3

            # IWP 인스턴스
            if iwp_id and iwp_id not in iwp_cache:
                iwp_uri = INST[f"iwp_{iwp_id}"]
                g.add((iwp_uri, RDF.type, AWP.InstallationWorkPackage))
                g.add((iwp_uri, RDFS.label, Literal(iwp_id)))
                g.add((iwp_uri, BIM.hasName, Literal(iwp_id)))
                if cwp_id and cwp_id in cwp_cache:
                    g.add((iwp_uri, AWP.belongsToCWP, cwp_cache[cwp_id]))
                    triples_added += 1
                for col, prop in [
                    ("IWP_StartDate", AWP.hasStartDate),
                    ("IWP_EndDate", AWP.hasEndDate),
                ]:
                    val = row.get(col, "").strip()
                    if val:
                        g.add((iwp_uri, prop, Literal(val, datatype=XSD.date)))
                        triples_added += 1
                constraint = row.get("ConstraintStatus", "").strip()
                if constraint:
                    g.add((iwp_uri, AWP.hasConstraintStatus, Literal(constraint)))
                    triples_added += 1
                iwp_cache[iwp_id] = iwp_uri
                triples_added += 3

            # 요소 → IWP 연결
            if iwp_id and iwp_id in iwp_cache:
                g.add((iwp_cache[iwp_id], AWP.includesElement, elem_uri))
                g.add((elem_uri, AWP.assignedToIWP, iwp_cache[iwp_id]))
                triples_added += 2

        result = {
            "triples_added": triples_added,
            "cwa_count": len(cwa_cache),
            "cwp_count": len(cwp_cache),
            "iwp_count": len(iwp_cache),
            "elements_matched": elements_matched,
        }
        logger.info("AWP 주입 완료: %s", result)
        return result

    # ── Status Injection ──

    def inject_status_csv(self, csv_path: str) -> dict:
        """상태 CSV를 주입한다. ElementStatus 인스턴스를 생성한다.

        CSV 컬럼:
        - 식별자: GlobalId | ObjectId | SyncID
        - 상태: StatusValue, StatusDate, DeliveryStatus
        """
        rows = self._read_csv(csv_path)
        g = self._graph
        triples_added = 0
        elements_matched = 0
        not_found = []

        for i, row in enumerate(rows):
            global_id, object_id = self._extract_row_ids(row)
            if not global_id and not object_id:
                continue

            elem_uri = self._resolve_element(global_id=global_id, object_id=object_id)
            if elem_uri is None:
                not_found.append(global_id or object_id)
                continue

            elements_matched += 1

            # ElementStatus 인스턴스
            status_value = row.get("StatusValue", "").strip()
            status_date = row.get("StatusDate", "").strip()
            if status_value:
                status_seed = (global_id or object_id).replace("$", "_").replace("-", "_")
                status_uri = INST[f"status_{status_seed}_{i}"]
                g.add((status_uri, RDF.type, BIM.ElementStatus))
                g.add((status_uri, BIM.hasStatusValue, Literal(status_value)))
                g.add((elem_uri, BIM.hasStatus, status_uri))
                triples_added += 3

                if status_date:
                    g.add((status_uri, BIM.hasStatusDate,
                           Literal(status_date, datatype=XSD.dateTime)))
                    triples_added += 1

            # DeliveryStatus 직접 속성
            delivery = row.get("DeliveryStatus", "").strip()
            if delivery:
                g.add((elem_uri, BIM.hasDeliveryStatus, Literal(delivery)))
                triples_added += 1

        result = {
            "triples_added": triples_added,
            "elements_matched": elements_matched,
            "elements_not_found": not_found,
        }
        logger.info("Status 주입 완료: %s", result)
        return result

    # ── Equipment Injection ──

    def inject_equipment_csv(self, csv_path: str) -> dict:
        """장비 CSV를 주입한다. ConstructionEquipment 인스턴스를 생성한다.

        CSV 컬럼: EquipmentID, Name, Width, Height, TurningRadius,
                  BoomLength, LoadCapacity, AccessZone_CWA_ID
        """
        rows = self._read_csv(csv_path)
        g = self._graph
        triples_added = 0
        equipment_count = 0

        for row in rows:
            eq_id = row.get("EquipmentID", "").strip()
            name = row.get("Name", "").strip()
            if not eq_id:
                continue

            eq_uri = INST[f"equip_{eq_id}"]
            g.add((eq_uri, RDF.type, BIM.ConstructionEquipment))
            g.add((eq_uri, RDFS.label, Literal(name or eq_id)))
            g.add((eq_uri, BIM.hasName, Literal(name or eq_id)))
            triples_added += 3
            equipment_count += 1

            for col, prop in [
                ("Width", BIM.hasEquipmentWidth),
                ("Height", BIM.hasEquipmentHeight),
                ("TurningRadius", BIM.hasTurningRadius),
                ("BoomLength", BIM.hasBoomLength),
                ("LoadCapacity", BIM.hasLoadCapacity),
            ]:
                val = row.get(col, "").strip()
                if val:
                    g.add((eq_uri, prop, Literal(float(val), datatype=XSD.double)))
                    triples_added += 1

            # 접근 가능 CWA 연결
            cwa_id = row.get("AccessZone_CWA_ID", "").strip()
            if cwa_id:
                cwa_uri = INST[f"cwa_{cwa_id}"]
                g.add((eq_uri, BIM.canAccessZone, cwa_uri))
                triples_added += 1

        result = {
            "triples_added": triples_added,
            "equipment_count": equipment_count,
        }
        logger.info("Equipment 주입 완료: %s", result)
        return result

    # ── Single Element Status Update ──

    def update_element_status(
        self, global_id: str, status_value: str, delivery_status: str = ""
    ) -> dict:
        """단일 요소의 상태를 업데이트한다.

        Args:
            global_id: 요소 GlobalId
            status_value: Planned|Designed|Fabricated|Shipped|OnSite|Installed|Inspected
            delivery_status: Ordered|InProduction|Shipped|OnSite|Installed (optional)

        Returns:
            {"success": bool, "triples_added": int}
        """
        elem_uri = self._resolve_element(global_id)
        if elem_uri is None:
            return {"success": False, "error": f"Element not found: {global_id}"}

        g = self._graph
        triples_added = 0
        now_str = datetime.now(timezone.utc).isoformat()

        # ElementStatus 인스턴스 생성
        status_uri = INST[f"status_{global_id.replace('$', '_')}_{now_str[:10]}"]
        g.add((status_uri, RDF.type, BIM.ElementStatus))
        g.add((status_uri, BIM.hasStatusValue, Literal(status_value)))
        g.add((status_uri, BIM.hasStatusDate,
               Literal(now_str, datatype=XSD.dateTime)))
        g.add((elem_uri, BIM.hasStatus, status_uri))
        triples_added += 4

        if delivery_status:
            # 기존 delivery status 제거 후 새로 추가
            g.remove((elem_uri, BIM.hasDeliveryStatus, None))
            g.add((elem_uri, BIM.hasDeliveryStatus, Literal(delivery_status)))
            triples_added += 1

        # isReady 추론: Installed 또는 OnSite → ready
        ready = status_value in ("Installed", "OnSite", "Inspected")
        g.remove((elem_uri, BIM.isReady, None))
        g.add((elem_uri, BIM.isReady, Literal(ready)))
        triples_added += 1

        return {"success": True, "triples_added": triples_added, "global_id": global_id}

    # ── Query Helpers ──

    def get_lean_layer_stats(self) -> dict:
        """Lean Layer 주입 현황 통계를 반환한다."""
        g = self._graph
        queries = {
            "tasks": "SELECT (COUNT(?t) AS ?cnt) WHERE { ?t a sched:ConstructionTask }",
            "iwps": "SELECT (COUNT(?i) AS ?cnt) WHERE { ?i a awp:InstallationWorkPackage }",
            "cwps": "SELECT (COUNT(?c) AS ?cnt) WHERE { ?c a awp:ConstructionWorkPackage }",
            "cwas": "SELECT (COUNT(?c) AS ?cnt) WHERE { ?c a awp:ConstructionWorkArea }",
            "statuses": "SELECT (COUNT(?s) AS ?cnt) WHERE { ?s a bim:ElementStatus }",
            "equipment": "SELECT (COUNT(?e) AS ?cnt) WHERE { ?e a bim:ConstructionEquipment }",
            "with_delivery": "SELECT (COUNT(?e) AS ?cnt) WHERE { ?e bim:hasDeliveryStatus ?s }",
            "with_iwp": "SELECT (COUNT(?e) AS ?cnt) WHERE { ?e awp:assignedToIWP ?i }",
            "with_unit_cost": "SELECT (COUNT(DISTINCT ?e) AS ?cnt) WHERE { ?e bim:hasUnitCost ?c }",
            "with_consume_duration": "SELECT (COUNT(DISTINCT ?e) AS ?cnt) WHERE { ?e bim:hasConsumeDuration ?d }",
            "tasks_with_cost": "SELECT (COUNT(DISTINCT ?t) AS ?cnt) WHERE { ?t a sched:ConstructionTask ; sched:hasCost ?c }",
            "tasks_with_typed_duration": """
                SELECT (COUNT(DISTINCT ?t) AS ?cnt) WHERE {
                    ?t a sched:ConstructionTask .
                    { ?t sched:hasPlannedDuration ?d }
                    UNION
                    { ?t sched:hasActualDuration ?d }
                }
            """,
            "tasks_with_legacy_duration": "SELECT (COUNT(DISTINCT ?t) AS ?cnt) WHERE { ?t a sched:ConstructionTask ; sched:hasDuration ?d }",
            "total_unit_cost": "SELECT (SUM(xsd:double(?c)) AS ?cnt) WHERE { ?e bim:hasUnitCost ?c }",
            "avg_unit_cost": "SELECT (AVG(xsd:double(?c)) AS ?cnt) WHERE { ?e bim:hasUnitCost ?c }",
            "avg_consume_duration": "SELECT (AVG(xsd:double(?d)) AS ?cnt) WHERE { ?e bim:hasConsumeDuration ?d }",
            # 우선순위: ActualDuration > PlannedDuration > legacy Duration(숫자 문자열)
            "avg_task_duration_effective": """
                SELECT (AVG(?effective) AS ?cnt) WHERE {
                    ?t a sched:ConstructionTask .
                    OPTIONAL { ?t sched:hasActualDuration ?actualDur }
                    OPTIONAL { ?t sched:hasPlannedDuration ?plannedDur }
                    OPTIONAL { ?t sched:hasDuration ?legacyDur }
                    BIND(
                        COALESCE(
                            xsd:double(?actualDur),
                            xsd:double(?plannedDur),
                            IF(
                                REGEX(STR(?legacyDur), "^[0-9]+(\\\\.[0-9]+)?$"),
                                xsd:double(?legacyDur),
                                0
                            )
                        ) AS ?effective
                    )
                    FILTER(?effective > 0)
                }
            """,
        }
        prefixes = """
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        PREFIX sched: <http://example.org/bim-ontology/schedule#>
        PREFIX awp: <http://example.org/bim-ontology/awp#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        """
        stats = {}
        float_keys = {"total_unit_cost", "avg_unit_cost", "avg_consume_duration", "avg_task_duration_effective"}
        for key, q in queries.items():
            results = list(g.query(prefixes + q))
            if not results:
                stats[key] = 0.0 if key in float_keys else 0
                continue
            val = results[0].cnt
            if val is None:
                stats[key] = 0.0 if key in float_keys else 0
                continue
            if key in float_keys:
                try:
                    stats[key] = float(val)
                except (TypeError, ValueError):
                    stats[key] = 0.0
            else:
                try:
                    stats[key] = int(val)
                except (TypeError, ValueError):
                    stats[key] = 0
        return stats
