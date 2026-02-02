"""예제 2: 카테고리별 통계 및 분석."""

import sys
sys.path.insert(0, ".")

from src.clients.python import BIMOntologyClient

client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")

# 카테고리별 통계
print("=== 카테고리별 요소 수 ===")
stats = client.get_statistics()
total = sum(stats.values())

for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
    pct = count / total * 100
    bar = "#" * int(pct / 2)
    print(f"  {cat:<20} {count:>6} ({pct:5.1f}%) {bar}")

print(f"\n  {'총 합계':<20} {total:>6}")
