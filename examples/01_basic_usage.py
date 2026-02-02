"""예제 1: 기본 사용법 - IFC 파일에서 BIM 데이터 쿼리하기."""

import sys
sys.path.insert(0, ".")

from src.clients.python import BIMOntologyClient

# IFC 파일에서 직접 클라이언트 생성
client = BIMOntologyClient.from_ifc("references/nwd4op-12.ifc")

# 건물 목록 조회
print("=== 건물 목록 ===")
for b in client.get_buildings():
    print(f"  {b.get('name', '(이름 없음)')} - {b.get('globalId', '')}")

# 층 목록 조회
print("\n=== 층 목록 ===")
for s in client.get_storeys():
    print(f"  {s.get('name', '(이름 없음)')}")

# 카테고리 목록
print("\n=== 카테고리 목록 ===")
for cat in client.get_categories():
    print(f"  {cat}")

# 총 트리플 수
print(f"\n총 트리플 수: {client.count_triples():,}")
