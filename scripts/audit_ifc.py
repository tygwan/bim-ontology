"""IFC 파일 전수 조사 스크립트.

IFC 파일 내 모든 엔티티 타입, PropertySet, Quantity, Material, Classification,
Schedule/Cost 엔티티를 조사하고 JSON 리포트를 생성한다.

Usage:
    python scripts/audit_ifc.py references/nwd4op-12.ifc
    python scripts/audit_ifc.py references/nwd4op-12.ifc --output data/audit/report.json
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import ifcopenshell


def audit_ifc(file_path: str) -> dict:
    """IFC 파일을 전수 조사하여 리포트를 생성한다."""
    ifc = ifcopenshell.open(file_path)
    report: dict = {
        "file": Path(file_path).name,
        "schema": ifc.schema,
        "total_entities": len(list(ifc)),
    }

    # 1. 전체 엔티티 타입별 카운트
    type_counts = Counter()
    for entity in ifc:
        type_counts[entity.is_a()] += 1
    report["entity_type_counts"] = dict(type_counts.most_common())
    report["unique_types"] = len(type_counts)

    # 2. 공간 구조
    spatial_types = [
        "IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcSpace",
    ]
    spatial = {}
    for st in spatial_types:
        entities = ifc.by_type(st)
        spatial[st] = {
            "count": len(entities),
            "names": [getattr(e, "Name", None) for e in entities[:20]],
        }
    report["spatial_structure"] = spatial

    # 3. 물리적 요소 (IfcProduct 하위)
    product_types = [
        "IfcBuildingElementProxy", "IfcWall", "IfcColumn", "IfcBeam",
        "IfcSlab", "IfcStair", "IfcRailing", "IfcDoor", "IfcWindow",
        "IfcPipeSegment", "IfcPipeFitting", "IfcFlowTerminal",
        "IfcFlowSegment", "IfcDistributionElement", "IfcMember",
        "IfcPlate", "IfcFooting", "IfcCovering",
    ]
    physical = {}
    total_physical = 0
    for pt in product_types:
        try:
            entities = ifc.by_type(pt)
            if entities:
                physical[pt] = len(entities)
                total_physical += len(entities)
        except RuntimeError:
            pass
    report["physical_elements"] = physical
    report["total_physical_elements"] = total_physical

    # 4. PropertySet 조사
    pset_info: dict[str, dict] = {}
    pset_rels = ifc.by_type("IfcRelDefinesByProperties")
    report["propertyset_relation_count"] = len(pset_rels)

    for rel in pset_rels:
        pset = rel.RelatingPropertyDefinition
        pset_type = pset.is_a()
        pset_name = getattr(pset, "Name", "unnamed") or "unnamed"

        if pset_name not in pset_info:
            pset_info[pset_name] = {
                "type": pset_type,
                "property_count": 0,
                "property_names": [],
                "usage_count": 0,
            }

        pset_info[pset_name]["usage_count"] += len(rel.RelatedObjects)

        if hasattr(pset, "HasProperties") and pset.HasProperties:
            props = [p.Name for p in pset.HasProperties]
            if not pset_info[pset_name]["property_names"]:
                pset_info[pset_name]["property_names"] = props
                pset_info[pset_name]["property_count"] = len(props)

    report["property_sets"] = pset_info
    report["property_set_count"] = len(pset_info)

    # 5. IfcElementQuantity 조사
    eq_info: dict[str, dict] = {}
    for rel in pset_rels:
        qset = rel.RelatingPropertyDefinition
        if not qset.is_a("IfcElementQuantity"):
            continue
        qset_name = getattr(qset, "Name", "unnamed") or "unnamed"
        if qset_name not in eq_info:
            quantities = []
            if hasattr(qset, "Quantities") and qset.Quantities:
                for q in qset.Quantities:
                    q_type = q.is_a()
                    q_name = q.Name
                    q_value = None
                    for attr in ["AreaValue", "LengthValue", "VolumeValue",
                                 "WeightValue", "CountValue", "TimeValue"]:
                        v = getattr(q, attr, None)
                        if v is not None:
                            q_value = v
                            break
                    quantities.append({
                        "name": q_name,
                        "type": q_type,
                        "sample_value": q_value,
                    })
            eq_info[qset_name] = {
                "quantity_count": len(quantities),
                "quantities": quantities,
                "usage_count": len(rel.RelatedObjects),
            }
    report["element_quantities"] = eq_info
    report["element_quantity_set_count"] = len(eq_info)

    # 6. Material 조사
    materials = ifc.by_type("IfcMaterial")
    report["materials"] = {
        "count": len(materials),
        "names": [m.Name for m in materials[:30]],
    }

    material_layer_sets = ifc.by_type("IfcMaterialLayerSet")
    report["material_layer_sets"] = {"count": len(material_layer_sets)}

    material_assocs = ifc.by_type("IfcRelAssociatesMaterial")
    report["material_associations"] = {"count": len(material_assocs)}

    # 7. Classification 조사
    classifications = ifc.by_type("IfcClassification")
    report["classifications"] = {
        "count": len(classifications),
        "names": [getattr(c, "Name", None) for c in classifications],
    }

    class_refs = ifc.by_type("IfcClassificationReference")
    report["classification_references"] = {"count": len(class_refs)}

    class_assocs = ifc.by_type("IfcRelAssociatesClassification")
    report["classification_associations"] = {"count": len(class_assocs)}

    # 8. Schedule/Cost 엔티티 (존재 여부 확인)
    schedule_cost = {}
    schedule_types = [
        "IfcWorkSchedule", "IfcWorkPlan", "IfcTask", "IfcTaskTime",
        "IfcRelSequence", "IfcRelAssignsToProcess",
        "IfcCostSchedule", "IfcCostItem", "IfcCostValue",
    ]
    for st in schedule_types:
        try:
            entities = ifc.by_type(st)
            schedule_cost[st] = len(entities)
        except RuntimeError:
            schedule_cost[st] = 0
    report["schedule_cost_entities"] = schedule_cost
    has_schedule = any(
        schedule_cost.get(t, 0) > 0
        for t in ["IfcWorkSchedule", "IfcTask", "IfcRelSequence"]
    )
    has_cost = any(
        schedule_cost.get(t, 0) > 0
        for t in ["IfcCostSchedule", "IfcCostItem"]
    )
    report["has_schedule_data"] = has_schedule
    report["has_cost_data"] = has_cost

    # 9. 관계 엔티티 조사
    rel_types = [
        "IfcRelAggregates", "IfcRelContainedInSpatialStructure",
        "IfcRelDefinesByProperties", "IfcRelDefinesByType",
        "IfcRelAssociatesMaterial", "IfcRelAssociatesClassification",
        "IfcRelConnectsPathElements", "IfcRelFillsElement",
        "IfcRelVoidsElement", "IfcRelSpaceBoundary",
    ]
    relationships = {}
    for rt in rel_types:
        try:
            relationships[rt] = len(ifc.by_type(rt))
        except RuntimeError:
            relationships[rt] = 0
    report["relationships"] = relationships

    # 10. IfcBuildingElementProxy 이름 분류 (상위 20개 패턴)
    proxy_names = Counter()
    for proxy in ifc.by_type("IfcBuildingElementProxy"):
        name = getattr(proxy, "Name", None) or "unnamed"
        # 첫 단어 또는 하이픈 앞 부분으로 그룹핑
        prefix = name.split("-")[0].split("_")[0].strip()
        proxy_names[prefix] += 1
    report["proxy_name_prefixes"] = dict(proxy_names.most_common(30))

    # 11. 요약
    report["summary"] = {
        "has_property_sets": report["property_set_count"] > 0,
        "has_quantities": report["element_quantity_set_count"] > 0,
        "has_materials": report["materials"]["count"] > 0,
        "has_classifications": report["classifications"]["count"] > 0,
        "has_schedule": has_schedule,
        "has_cost": has_cost,
        "data_richness": sum([
            report["property_set_count"] > 0,
            report["element_quantity_set_count"] > 0,
            report["materials"]["count"] > 0,
            report["classifications"]["count"] > 0,
            has_schedule,
            has_cost,
        ]),
    }

    return report


def print_report(report: dict):
    """리포트를 콘솔에 출력한다."""
    print(f"\n{'='*60}")
    print(f"IFC AUDIT REPORT: {report['file']}")
    print(f"{'='*60}")
    print(f"Schema: {report['schema']}")
    print(f"Total Entities: {report['total_entities']:,}")
    print(f"Unique Types: {report['unique_types']}")

    print(f"\n--- Spatial Structure ---")
    for st, info in report["spatial_structure"].items():
        if info["count"] > 0:
            names = ", ".join(str(n) for n in info["names"][:5])
            print(f"  {st}: {info['count']} ({names})")

    print(f"\n--- Physical Elements ({report['total_physical_elements']:,} total) ---")
    for pt, count in sorted(report["physical_elements"].items(), key=lambda x: -x[1]):
        print(f"  {pt}: {count:,}")

    print(f"\n--- PropertySets ({report['property_set_count']}) ---")
    for name, info in list(report["property_sets"].items())[:15]:
        props = ", ".join(info["property_names"][:5])
        more = f" +{len(info['property_names'])-5}" if len(info["property_names"]) > 5 else ""
        print(f"  {name} [{info['type']}] ({info['property_count']} props, used {info['usage_count']}x)")
        if props:
            print(f"    -> {props}{more}")

    print(f"\n--- Element Quantities ({report['element_quantity_set_count']}) ---")
    if report["element_quantities"]:
        for name, info in report["element_quantities"].items():
            print(f"  {name}: {info['quantity_count']} quantities")
            for q in info["quantities"][:5]:
                print(f"    -> {q['name']} ({q['type']}): {q['sample_value']}")
    else:
        print("  (none found)")

    print(f"\n--- Materials ({report['materials']['count']}) ---")
    if report["materials"]["names"]:
        for name in report["materials"]["names"][:10]:
            print(f"  {name}")
    else:
        print("  (none found)")

    print(f"\n--- Classifications ({report['classifications']['count']}) ---")
    if report["classifications"]["names"]:
        for name in report["classifications"]["names"]:
            print(f"  {name}")
    else:
        print("  (none found)")

    print(f"\n--- Schedule/Cost Entities ---")
    for st, count in report["schedule_cost_entities"].items():
        marker = "O" if count > 0 else "X"
        print(f"  [{marker}] {st}: {count}")

    print(f"\n--- Relationships ---")
    for rt, count in report["relationships"].items():
        if count > 0:
            print(f"  {rt}: {count:,}")

    print(f"\n--- Proxy Name Prefixes (top 20) ---")
    for prefix, count in list(report["proxy_name_prefixes"].items())[:20]:
        print(f"  {prefix}: {count:,}")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    s = report["summary"]
    print(f"  PropertySets:    {'YES' if s['has_property_sets'] else 'NO'}")
    print(f"  Quantities:      {'YES' if s['has_quantities'] else 'NO'}")
    print(f"  Materials:       {'YES' if s['has_materials'] else 'NO'}")
    print(f"  Classifications: {'YES' if s['has_classifications'] else 'NO'}")
    print(f"  Schedule Data:   {'YES' if s['has_schedule'] else 'NO'}")
    print(f"  Cost Data:       {'YES' if s['has_cost'] else 'NO'}")
    print(f"  Data Richness:   {s['data_richness']}/6")
    print()


def main():
    parser = argparse.ArgumentParser(description="IFC File Audit Tool")
    parser.add_argument("ifc_file", help="IFC file path")
    parser.add_argument("--output", "-o", default="data/audit/ifc_audit_report.json",
                        help="Output JSON path")
    args = parser.parse_args()

    if not Path(args.ifc_file).exists():
        print(f"Error: File not found: {args.ifc_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Auditing: {args.ifc_file}")
    report = audit_ifc(args.ifc_file)
    print_report(report)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    main()
