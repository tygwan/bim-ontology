"""IFC 파일 속성 상세 분석 스크립트.

IfcBuildingElementProxy의 속성셋 내용을 상세하게 분석합니다.
"""

import ifcopenshell
import ifcopenshell.util.element as element_util
from collections import Counter
from pathlib import Path


def analyze_properties(filepath: str, max_elements: int = 10):
    """IFC 파일의 속성을 상세 분석한다."""
    path = Path(filepath)
    print(f"\n{'='*60}")
    print(f"속성 분석: {path.name}")
    print(f"{'='*60}")

    ifc_file = ifcopenshell.open(str(path))

    # IfcBuildingElementProxy 샘플 분석
    proxies = ifc_file.by_type('IfcBuildingElementProxy')
    print(f"\nIfcBuildingElementProxy 총 수: {len(proxies):,}")

    # 이름 패턴 분석
    name_counter = Counter()
    for proxy in proxies:
        name = proxy.Name or '(없음)'
        # 이름에서 숫자 부분을 제거하여 패턴 파악
        name_counter[name] += 1

    print(f"\n--- 고유 이름 수: {len(name_counter)} ---")
    print("상위 20개 이름 패턴:")
    for name, count in name_counter.most_common(20):
        print(f"  {name:<50} {count:>6}")

    # 속성셋 상세 분석
    print(f"\n--- 속성셋 상세 (처음 {max_elements}개 요소) ---")

    pset_name_counter = Counter()
    prop_name_counter = Counter()

    for i, proxy in enumerate(proxies[:max_elements]):
        print(f"\n  [{i+1}] {proxy.Name or '(없음)'} (ID: {proxy.GlobalId})")

        # 방법 1: IfcRelDefinesByProperties를 통한 속성 접근
        for rel in ifc_file.by_type('IfcRelDefinesByProperties'):
            if proxy in rel.RelatedObjects:
                pset = rel.RelatingPropertyDefinition
                if hasattr(pset, 'Name'):
                    pset_name_counter[pset.Name] += 1
                    print(f"    속성셋: {pset.Name}")
                    if hasattr(pset, 'HasProperties') and pset.HasProperties:
                        for prop in pset.HasProperties:
                            prop_name_counter[prop.Name] += 1
                            val = getattr(prop, 'NominalValue', None)
                            if val is not None:
                                print(f"      {prop.Name}: {val.wrappedValue} ({val.is_a()})")
                            else:
                                print(f"      {prop.Name}: (값 없음)")

    # 전체 속성 통계
    print(f"\n--- 전체 속성셋 이름 통계 ---")
    all_psets = ifc_file.by_type('IfcPropertySet')
    pset_names = Counter(p.Name for p in all_psets)
    for name, count in pset_names.most_common():
        print(f"  {name:<50} {count:>6}")

    # 전체 속성 이름 통계
    print(f"\n--- 전체 속성 이름 통계 ---")
    all_prop_names = Counter()
    for pset in all_psets:
        if pset.HasProperties:
            for prop in pset.HasProperties:
                all_prop_names[prop.Name] += 1
    for name, count in all_prop_names.most_common(30):
        print(f"  {name:<50} {count:>6}")

    # 타입 정보 확인
    print(f"\n--- 타입 정보 ---")
    type_rels = ifc_file.by_type('IfcRelDefinesByType')
    print(f"IfcRelDefinesByType 수: {len(type_rels)}")
    for rel in type_rels[:10]:
        type_obj = rel.RelatingType
        print(f"  타입: {type_obj.is_a()} - {type_obj.Name or '(없음)'}")
        print(f"    관련 요소 수: {len(rel.RelatedObjects)}")

    # 재질 정보
    print(f"\n--- 재질 정보 ---")
    materials = ifc_file.by_type('IfcMaterial')
    print(f"IfcMaterial 수: {len(materials)}")
    for mat in materials[:10]:
        print(f"  {mat.Name or '(없음)'}")

    # 분류 정보
    print(f"\n--- 분류 참조 ---")
    classifications = ifc_file.by_type('IfcClassification')
    print(f"IfcClassification 수: {len(classifications)}")
    for cls in classifications:
        print(f"  {cls.Name or '(없음)'}")

    class_refs = ifc_file.by_type('IfcClassificationReference')
    print(f"IfcClassificationReference 수: {len(class_refs)}")
    for ref in class_refs[:10]:
        print(f"  {ref.Name or '(없음)'}: {ref.Identification or ''}")


if __name__ == '__main__':
    # 작은 파일(IFC4)만 분석
    analyze_properties(
        'references/nwd4op-12.ifc',
        max_elements=5
    )
