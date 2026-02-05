"""CSV → RDF 직접 주입 모듈.

CSV 데이터를 읽어 기존 RDF 그래프에 트리플로 직접 추가한다.
GlobalId를 키로 IFC 요소와 매핑한다.

Method B: IFC를 거치지 않고 RDF 그래프에 직접 주입.
빠르고 유연하지만 BIM 모델에는 반영되지 않는다.
"""

import csv
import logging
from pathlib import Path
from typing import Optional

from rdflib import Graph, Literal, URIRef, RDF, RDFS, XSD, Namespace

logger = logging.getLogger(__name__)

BIM = Namespace("http://example.org/bim-ontology/schema#")
INST = Namespace("http://example.org/bim-ontology/instance#")
SCHED = Namespace("http://example.org/bim-ontology/schedule#")
AWP = Namespace("http://example.org/bim-ontology/awp#")
NAVIS = Namespace("http://example.org/bim-ontology/navis#")


# GlobalId → 요소 URI 매핑을 위한 SPARQL
_FIND_ELEMENT_BY_GLOBALID = """
PREFIX bim: <http://example.org/bim-ontology/schema#>
SELECT ?elem WHERE {{
    ?elem bim:hasGlobalId "{global_id}" .
}}
LIMIT 1
"""

# ObjectId → 요소 URI 매핑을 위한 SPARQL
_FIND_ELEMENT_BY_OBJECTID = """
PREFIX navis: <http://example.org/bim-ontology/navis#>
SELECT ?elem WHERE {{
    ?elem navis:hasObjectId "{object_id}" .
}}
LIMIT 1
"""

# 값 타입 매핑
TYPE_MAP = {
    "string": XSD.string,
    "double": XSD.double,
    "integer": XSD.integer,
    "boolean": XSD.boolean,
    "date": XSD.date,
    "dateTime": XSD.dateTime,
}


class CSVToRDFInjector:
    """CSV 데이터를 RDF 그래프에 직접 주입한다."""

    def __init__(self, graph: Graph):
        self._graph = graph
        self._globalid_cache: dict[str, URIRef] = {}
        self._objectid_cache: dict[str, URIRef] = {}

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
        - GlobalId
        - ObjectId
        - SyncID
        """
        global_id = row.get("GlobalId", "").strip()
        object_id = row.get("ObjectId", "").strip()
        if not object_id:
            object_id = row.get("SyncID", "").strip()
        return global_id, object_id

    def inject_properties(self, csv_path: str, property_mapping: dict[str, tuple[URIRef, str]]) -> dict:
        """범용 CSV 주입: 각 행의 식별자로 요소를 찾아 속성을 추가한다.

        Args:
            csv_path: CSV 파일 경로
            property_mapping: {csv_column: (rdf_property_uri, xsd_type)}
                예: {"PlannedDate": (SCHED.hasPlannedStart, "date"),
                     "Status": (BIM.hasDeliveryStatus, "string")}

        Returns:
            {"triples_added": int, "elements_matched": int, "elements_not_found": list}
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        triples_added = 0
        elements_matched = 0
        not_found = []

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                global_id, object_id = self._extract_row_ids(row)
                if not global_id and not object_id:
                    continue

                elem_uri = self._resolve_element(global_id=global_id, object_id=object_id)
                if elem_uri is None:
                    not_found.append(global_id or object_id)
                    continue

                elements_matched += 1
                for col, (rdf_prop, xsd_type) in property_mapping.items():
                    value = row.get(col, "").strip()
                    if not value:
                        continue

                    datatype = TYPE_MAP.get(xsd_type, XSD.string)
                    if xsd_type == "double":
                        value = float(value)
                    elif xsd_type == "integer":
                        value = int(value)
                    elif xsd_type == "boolean":
                        value = value.lower() in ("true", "1", "yes")

                    self._graph.add((elem_uri, rdf_prop, Literal(value, datatype=datatype)))
                    triples_added += 1

        result = {
            "triples_added": triples_added,
            "elements_matched": elements_matched,
            "elements_not_found": not_found,
        }
        logger.info("CSV 주입 완료: %d triples, %d matched, %d not found",
                     triples_added, elements_matched, len(not_found))
        return result

    def inject_schedule(self, csv_path: str) -> dict:
        """일정 CSV를 주입한다.

        CSV 컬럼: GlobalId|ObjectId|SyncID, PlannedInstallDate, DeliveryStatus, CWP_ID, UnitCost
        """
        mapping = {
            "PlannedInstallDate": (SCHED.hasPlannedInstallDate, "date"),
            "DeliveryStatus": (BIM.hasDeliveryStatus, "string"),
            "CWP_ID": (AWP.belongsToCWP_ID, "string"),
            "UnitCost": (BIM.hasUnitCost, "double"),
        }
        return self.inject_properties(csv_path, mapping)

    def inject_status(self, csv_path: str) -> dict:
        """상태 CSV를 주입한다.

        CSV 컬럼: GlobalId|ObjectId|SyncID, Status, StatusDate
        """
        mapping = {
            "Status": (BIM.hasDeliveryStatus, "string"),
            "StatusDate": (BIM.hasStatusDate, "dateTime"),
        }
        return self.inject_properties(csv_path, mapping)

    def inject_awp(self, csv_path: str) -> dict:
        """AWP CSV를 주입한다. CWA/CWP/IWP 인스턴스를 생성하고 요소를 연결한다.

        CSV 컬럼: GlobalId|ObjectId|SyncID, CWA_ID, CWP_ID, IWP_ID, IWP_StartDate, IWP_EndDate
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        g = self._graph
        triples_added = 0
        cwa_cache: dict[str, URIRef] = {}
        cwp_cache: dict[str, URIRef] = {}
        iwp_cache: dict[str, URIRef] = {}

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                global_id, object_id = self._extract_row_ids(row)
                cwa_id = row.get("CWA_ID", "").strip()
                cwp_id = row.get("CWP_ID", "").strip()
                iwp_id = row.get("IWP_ID", "").strip()

                if not global_id and not object_id:
                    continue

                elem_uri = self._resolve_element(global_id=global_id, object_id=object_id)
                if elem_uri is None:
                    continue

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
                    # 날짜
                    start = row.get("IWP_StartDate", "").strip()
                    end = row.get("IWP_EndDate", "").strip()
                    if start:
                        g.add((iwp_uri, AWP.hasStartDate, Literal(start, datatype=XSD.date)))
                        triples_added += 1
                    if end:
                        g.add((iwp_uri, AWP.hasEndDate, Literal(end, datatype=XSD.date)))
                        triples_added += 1
                    iwp_cache[iwp_id] = iwp_uri
                    triples_added += 3

                # 요소 → IWP 연결
                if iwp_id and iwp_id in iwp_cache:
                    g.add((iwp_cache[iwp_id], AWP.includesElement, elem_uri))
                    g.add((elem_uri, AWP.assignedToIWP, iwp_cache[iwp_id]))
                    triples_added += 2

        return {
            "triples_added": triples_added,
            "cwa_count": len(cwa_cache),
            "cwp_count": len(cwp_cache),
            "iwp_count": len(iwp_cache),
        }
