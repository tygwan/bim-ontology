"""Lean/ObjectId 기반 주입 로직 테스트."""

from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

from src.converter.lean_layer_injector import LeanLayerInjector
from src.converter.navis_to_rdf import NavisToRDFConverter
from src.converter.namespace_manager import BIM, SCHED


NAVIS = Namespace("http://example.org/bim-ontology/navis#")


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(row))
    path.write_text("\n".join(lines), encoding="utf-8")


def test_lean_schedule_injection_matches_by_object_id(tmp_path: Path):
    graph = Graph()
    elem = URIRef("http://example.org/bim-ontology/instance#elem_1")
    graph.add((elem, RDF.type, BIM.PhysicalElement))
    graph.add((elem, NAVIS.hasObjectId, Literal("obj-1")))

    csv_path = tmp_path / "schedule.csv"
    _write_csv(
        csv_path,
        [
            "ObjectId",
            "TaskName",
            "PlannedStart",
            "PlannedEnd",
            "PlannedDuration",
            "ActualDuration",
            "Cost",
        ],
        [
            ["obj-1", "Task A", "2026-02-01", "2026-02-10", "9", "8", "1500.5"],
        ],
    )

    injector = LeanLayerInjector(graph)
    result = injector.inject_schedule_csv(str(csv_path))

    assert result["elements_matched"] == 1
    assert result["tasks_created"] == 1

    task_uri = next(graph.subjects(RDF.type, SCHED.ConstructionTask))
    assert (task_uri, SCHED.hasPlannedDuration, Literal(9, datatype=XSD.integer)) in graph
    assert (task_uri, SCHED.hasActualDuration, Literal(8, datatype=XSD.integer)) in graph
    assert (task_uri, SCHED.hasDuration, Literal("9", datatype=XSD.string)) in graph

    assert (elem, BIM.hasUnitCost, Literal(1500.5, datatype=XSD.double)) in graph
    assert (elem, BIM.hasConsumeDuration, Literal(8, datatype=XSD.integer)) in graph


def test_lean_status_injection_matches_by_sync_id(tmp_path: Path):
    graph = Graph()
    elem = URIRef("http://example.org/bim-ontology/instance#elem_2")
    graph.add((elem, RDF.type, BIM.PhysicalElement))
    graph.add((elem, NAVIS.hasObjectId, Literal("sync-xyz")))

    csv_path = tmp_path / "status.csv"
    _write_csv(
        csv_path,
        ["SyncID", "StatusValue", "StatusDate", "DeliveryStatus"],
        [["sync-xyz", "Installed", "2026-02-05T10:00:00Z", "Installed"]],
    )

    injector = LeanLayerInjector(graph)
    result = injector.inject_status_csv(str(csv_path))

    assert result["elements_matched"] == 1
    assert result["elements_not_found"] == []
    assert (elem, BIM.hasDeliveryStatus, Literal("Installed")) in graph

    status_nodes = list(graph.objects(elem, BIM.hasStatus))
    assert len(status_nodes) == 1
    status_uri = status_nodes[0]
    assert (status_uri, BIM.hasStatusValue, Literal("Installed")) in graph


def test_navis_schedule_csv_supports_cost_and_duration(tmp_path: Path):
    hierarchy_csv = tmp_path / "hierarchy.csv"
    _write_csv(
        hierarchy_csv,
        [
            "ObjectId",
            "ParentId",
            "Level",
            "DisplayName",
            "Category",
            "PropertyName",
            "RawValue",
            "DataType",
            "Unit",
        ],
        [
            [
                "obj-99",
                "00000000-0000-0000-0000-000000000000",
                "0",
                "Pipe-001",
                "항목",
                "내부 유형",
                "SP3D Entity",
                "String",
                "",
            ],
        ],
    )

    schedule_csv = tmp_path / "schedule.csv"
    _write_csv(
        schedule_csv,
        [
            "SyncID",
            "TaskName",
            "PlannedStart",
            "PlannedEnd",
            "TaskType",
            "ParentSet",
            "Progress",
            "PlannedDuration",
            "ActualDuration",
            "Cost",
        ],
        [
            ["obj-99", "Install Pipe", "2026-02-01", "2026-02-05", "Construct", "Area-A", "25", "4", "5", "2500"],
        ],
    )

    converter = NavisToRDFConverter()
    converter.convert_hierarchy_csv(str(hierarchy_csv))
    stats = converter.convert_schedule_csv(str(schedule_csv))

    assert stats["total_tasks"] == 1
    assert stats["matched_elements"] == 1
    assert stats["tasks_with_cost"] == 1
    assert stats["tasks_with_duration"] == 1

    graph = converter.get_graph()
    task_uri = next(graph.subjects(RDF.type, SCHED.ConstructionTask))
    elem_uri = next(graph.subjects(NAVIS.hasObjectId, Literal("obj-99")))

    assert (task_uri, SCHED.hasPlannedDuration, Literal(4, datatype=XSD.integer)) in graph
    assert (task_uri, SCHED.hasActualDuration, Literal(5, datatype=XSD.integer)) in graph
    assert (task_uri, SCHED.hasCost, Literal(2500.0, datatype=XSD.double)) in graph
    assert (elem_uri, BIM.hasUnitCost, Literal(2500.0, datatype=XSD.double)) in graph
    assert (elem_uri, BIM.hasConsumeDuration, Literal(5, datatype=XSD.integer)) in graph


def test_lean_stats_kpi_with_duration_fallback_priority(tmp_path: Path):
    graph = Graph()
    elem1 = URIRef("http://example.org/bim-ontology/instance#elem_10")
    elem2 = URIRef("http://example.org/bim-ontology/instance#elem_11")
    graph.add((elem1, RDF.type, BIM.PhysicalElement))
    graph.add((elem2, RDF.type, BIM.PhysicalElement))
    graph.add((elem1, NAVIS.hasObjectId, Literal("sync-10")))
    graph.add((elem2, NAVIS.hasObjectId, Literal("sync-11")))

    csv_path = tmp_path / "schedule_kpi.csv"
    _write_csv(
        csv_path,
        [
            "SyncID",
            "TaskName",
            "PlannedStart",
            "PlannedEnd",
            "PlannedDuration",
            "ActualDuration",
            "Duration",
            "Cost",
        ],
        [
            ["sync-10", "Task 10", "2026-02-01", "2026-02-10", "10", "8", "", "1000"],
            ["sync-11", "Task 11", "2026-02-01", "2026-02-10", "", "", "6", "500"],
        ],
    )

    injector = LeanLayerInjector(graph)
    injector.inject_schedule_csv(str(csv_path))
    stats = injector.get_lean_layer_stats()

    assert stats["tasks"] == 2
    assert stats["with_unit_cost"] == 2
    # Task 10(Actual/Planned) + Task 11(legacy Duration -> PlannedDuration 변환)
    assert stats["tasks_with_typed_duration"] == 2
    assert stats["tasks_with_legacy_duration"] == 2  # Task 10(legacy from planned) + Task 11(legacy)
    assert stats["total_unit_cost"] == 1500.0
    assert stats["avg_consume_duration"] == 7.0  # (8 + 6) / 2
    assert stats["avg_task_duration_effective"] == 7.0  # Actual 8 우선, legacy 6 사용
