"""PoC: IfcOpenShell로 IFC 파일에 Custom PropertySet을 추가하고 RDF 변환을 검증한다.

Method A: IFC 파일 자체를 수정 → RDF 재변환 → SPARQL 조회
이 방법은 BIM 모델에 속성이 직접 반영되어 round-trip이 보존된다.

Usage:
    python scripts/poc_ifc_inject.py
"""

import sys
import tempfile
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ifcopenshell
import ifcopenshell.api


def inject_schedule_properties(ifc_path: str, output_path: str, max_elements: int = 5):
    """IFC 파일의 요소에 Schedule PropertySet을 추가한다."""
    model = ifcopenshell.open(ifc_path)
    proxies = model.by_type("IfcBuildingElementProxy")

    if not proxies:
        print("ERROR: No IfcBuildingElementProxy found")
        return None

    sample_data = [
        {"PlannedInstallDate": "2026-03-15", "DeliveryStatus": "OnSite",
         "CWP_ID": "CWP-A01-001", "UnitCost": 1250.0},
        {"PlannedInstallDate": "2026-03-20", "DeliveryStatus": "Delayed",
         "CWP_ID": "CWP-A01-002", "UnitCost": 800.0},
        {"PlannedInstallDate": "2026-03-10", "DeliveryStatus": "Installed",
         "CWP_ID": "CWP-A02-001", "UnitCost": 2100.0},
        {"PlannedInstallDate": "2026-03-25", "DeliveryStatus": "Shipped",
         "CWP_ID": "CWP-A01-003", "UnitCost": 950.0},
        {"PlannedInstallDate": "2026-03-18", "DeliveryStatus": "OnSite",
         "CWP_ID": "CWP-A02-002", "UnitCost": 1600.0},
    ]

    injected = []
    for i, element in enumerate(proxies[:max_elements]):
        data = sample_data[i % len(sample_data)]
        pset = ifcopenshell.api.run("pset.add_pset", model,
                                     product=element,
                                     name="EPset_Schedule")
        ifcopenshell.api.run("pset.edit_pset", model, pset=pset,
                             properties=data)
        injected.append({
            "global_id": element.GlobalId,
            "name": element.Name,
            "properties": data,
        })
        print(f"  Injected EPset_Schedule into: {element.Name} ({element.GlobalId})")

    model.write(output_path)
    print(f"\nEnriched IFC saved: {output_path}")
    print(f"Elements modified: {len(injected)}")
    return injected


def verify_rdf_conversion(enriched_ifc_path: str, injected_elements: list):
    """enriched IFC를 RDF로 변환하고 주입된 속성이 추출되는지 검증한다."""
    from src.parser.ifc_parser import IFCParser
    from src.converter.ifc_to_rdf import RDFConverter

    parser = IFCParser(enriched_ifc_path)
    parser.open()

    converter = RDFConverter(schema=parser.get_schema())
    graph = converter.convert_file(parser)

    print(f"\nRDF Conversion: {len(graph)} triples")

    # SPARQL로 주입된 PropertySet 조회
    query = """
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?elem ?elemName ?psetName ?propName ?propValue
    WHERE {
        ?elem bim:hasPropertySet ?pset .
        ?pset bim:hasName ?psetName .
        ?pset bim:hasProperty ?prop .
        ?prop bim:hasName ?propName .
        OPTIONAL { ?prop bim:hasPropertyValue ?propValue }
        OPTIONAL { ?elem bim:hasName ?elemName }
        FILTER(CONTAINS(STR(?psetName), "EPset_Schedule"))
    }
    ORDER BY ?elemName ?propName
    """

    results = list(graph.query(query))
    print(f"\nSPARQL Results for EPset_Schedule: {len(results)} rows")

    if results:
        print("\n--- Injected Properties Found in RDF ---")
        current_elem = None
        for row in results:
            elem_name = str(row.elemName) if row.elemName else "?"
            if elem_name != current_elem:
                current_elem = elem_name
                print(f"\n  Element: {elem_name}")
            prop_name = str(row.propName)
            prop_value = str(row.propValue) if row.propValue else "N/A"
            print(f"    {prop_name}: {prop_value}")
        return True
    else:
        print("\nWARNING: No EPset_Schedule properties found in RDF!")
        # PropertySet이 있는지 별도 확인
        pset_query = """
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        SELECT (COUNT(?pset) AS ?cnt) WHERE {
            ?pset a bim:PropertySet .
        }
        """
        for row in graph.query(pset_query):
            print(f"  Total PropertySets in RDF: {row.cnt}")
        return False


def main():
    ifc_path = "references/nwd4op-12.ifc"
    if not Path(ifc_path).exists():
        print(f"ERROR: IFC file not found: {ifc_path}")
        sys.exit(1)

    # 임시 파일에 enriched IFC 저장
    output_path = "data/test/nwd4op-12_enriched.ifc"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PoC Method A: IfcOpenShell PropertySet Injection")
    print("=" * 60)

    print(f"\n1. Injecting EPset_Schedule into {ifc_path}...")
    injected = inject_schedule_properties(ifc_path, output_path)

    if injected:
        print(f"\n2. Converting enriched IFC to RDF and verifying...")
        success = verify_rdf_conversion(output_path, injected)

        print(f"\n{'=' * 60}")
        print(f"RESULT: {'SUCCESS' if success else 'FAILED'}")
        print(f"{'=' * 60}")
        print(f"  - IFC PropertySet injection: OK")
        print(f"  - RDF conversion of injected properties: {'OK' if success else 'FAILED'}")
        print(f"  - SPARQL queryable: {'OK' if success else 'FAILED'}")


if __name__ == "__main__":
    main()
