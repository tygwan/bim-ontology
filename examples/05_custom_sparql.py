"""예제 5: 커스텀 SPARQL 쿼리 실행."""

import sys
sys.path.insert(0, ".")

from src.clients.python import BIMOntologyClient

client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")

# 커스텀 SPARQL: 이름에 'Pump' 포함하는 모든 요소
print("=== 이름에 'Pump' 포함하는 요소 ===")
results = client.query("""
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    SELECT ?name ?category
    WHERE {
        ?e bim:hasName ?name .
        ?e bim:hasCategory ?category .
        FILTER(CONTAINS(LCASE(?name), "pump"))
    }
    ORDER BY ?category ?name
""")
for r in results:
    print(f"  [{r['category']}] {r['name']}")

# 커스텀 SPARQL: 공간 구조별 요소 수
print("\n=== 공간 구조별 포함 요소 수 ===")
results = client.query("""
    PREFIX bim: <http://example.org/bim-ontology/schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?structureName ?structureType (COUNT(?elem) AS ?num)
    WHERE {
        ?structure bim:containsElement ?elem .
        ?structure rdf:type ?structureType .
        OPTIONAL { ?structure bim:hasName ?structureName }
        FILTER(?structureType IN (bim:Building, bim:BuildingStorey))
    }
    GROUP BY ?structureName ?structureType
""")
for r in results:
    stype = r.get("structureType", "").split("#")[-1]
    sname = r.get("structureName", "(이름 없음)")
    print(f"  {stype}({sname}): {r['num']}개 요소")
