"""예제 3: 특정 카테고리 요소 상세 조회."""

import sys
sys.path.insert(0, ".")

from src.clients.python import BIMOntologyClient

client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")

# Pipe 카테고리 요소 조회
print("=== Pipe 카테고리 (상위 10개) ===")
pipes = client.get_elements(category="Pipe", limit=10)
for p in pipes:
    print(f"  {p.get('name', '(없음)'):<50} {p.get('globalId', '')[:20]}")

# Beam 카테고리 요소 조회
print("\n=== Beam 카테고리 (상위 10개) ===")
beams = client.get_elements(category="Beam", limit=10)
for b in beams:
    print(f"  {b.get('name', '(없음)'):<50} {b.get('globalId', '')[:20]}")

# Column 카테고리
print("\n=== Column 카테고리 (상위 10개) ===")
columns = client.get_elements(category="Column", limit=10)
for c in columns:
    print(f"  {c.get('name', '(없음)'):<50} {c.get('globalId', '')[:20]}")
