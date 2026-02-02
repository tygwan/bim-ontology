"""예제 4: 건물 계층 구조 조회."""

import sys
sys.path.insert(0, ".")

from src.clients.python import BIMOntologyClient

client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")

# 건물 계층 구조
print("=== 건물 계층 구조 ===")
hierarchy = client.get_hierarchy()
for row in hierarchy:
    parent_type = row.get("parentType", "").split("#")[-1]
    child_type = row.get("childType", "").split("#")[-1]
    parent_name = row.get("parentName", "(이름 없음)")
    child_name = row.get("childName", "(이름 없음)")
    print(f"  {parent_type}({parent_name}) → {child_type}({child_name})")
