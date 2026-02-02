"""IFC 파일 로딩 및 기본 분석 테스트 스크립트.

ifcopenshell을 사용하여 IFC4 파일을 파싱하고
엔티티 통계, 스키마 정보, 구조 분석을 수행합니다.
"""

import sys
import time
from pathlib import Path
from collections import Counter

import ifcopenshell


def analyze_ifc(filepath: str) -> dict:
    """IFC 파일을 열고 기본 분석 결과를 반환한다."""
    path = Path(filepath)
    print(f"\n{'='*60}")
    print(f"파일: {path.name}")
    print(f"크기: {path.stat().st_size / (1024*1024):.1f} MB")
    print(f"{'='*60}")

    start = time.time()
    ifc_file = ifcopenshell.open(str(path))
    load_time = time.time() - start
    print(f"로딩 시간: {load_time:.1f}초")

    # 기본 정보
    schema = ifc_file.schema
    total_entities = len(list(ifc_file))
    print(f"\n--- 기본 정보 ---")
    print(f"스키마: {schema}")
    print(f"총 엔티티 수: {total_entities:,}")

    # 엔티티 타입별 카운트
    type_counter = Counter()
    for entity in ifc_file:
        type_counter[entity.is_a()] += 1

    print(f"고유 엔티티 타입 수: {len(type_counter)}")

    # 상위 20개 엔티티 타입
    print(f"\n--- 상위 20 엔티티 타입 ---")
    for etype, count in type_counter.most_common(20):
        print(f"  {etype:<40} {count:>8,}")

    # BIM 주요 요소 분석
    bim_types = [
        'IfcWall', 'IfcWallStandardCase',
        'IfcSlab', 'IfcColumn', 'IfcBeam',
        'IfcDoor', 'IfcWindow',
        'IfcSpace', 'IfcBuildingStorey',
        'IfcBuilding', 'IfcSite', 'IfcProject',
        'IfcPipeSegment', 'IfcDuctSegment',
        'IfcFlowTerminal', 'IfcFlowSegment',
        'IfcPropertySet', 'IfcPropertySingleValue',
        'IfcRelDefinesByProperties',
        'IfcMaterial', 'IfcMaterialLayerSetUsage',
    ]

    print(f"\n--- BIM 주요 요소 ---")
    for btype in bim_types:
        try:
            elements = ifc_file.by_type(btype)
            if elements:
                print(f"  {btype:<40} {len(elements):>8,}")
        except Exception:
            pass

    # 공간 구조 분석
    print(f"\n--- 공간 구조 ---")
    projects = ifc_file.by_type('IfcProject')
    for project in projects:
        print(f"  프로젝트: {project.Name or '(이름 없음)'}")

    sites = ifc_file.by_type('IfcSite')
    for site in sites:
        print(f"  사이트: {site.Name or '(이름 없음)'}")

    buildings = ifc_file.by_type('IfcBuilding')
    for building in buildings:
        print(f"  건물: {building.Name or '(이름 없음)'}")

    storeys = ifc_file.by_type('IfcBuildingStorey')
    print(f"  층 수: {len(storeys)}")
    for storey in storeys[:10]:  # 최대 10개만 출력
        print(f"    - {storey.Name or '(이름 없음)'} (표고: {storey.Elevation})")
    if len(storeys) > 10:
        print(f"    ... 외 {len(storeys) - 10}개")

    # 속성셋 샘플
    print(f"\n--- 속성셋 샘플 (최대 5개) ---")
    psets = ifc_file.by_type('IfcPropertySet')
    for pset in psets[:5]:
        print(f"  [{pset.Name}]")
        if pset.HasProperties:
            for prop in list(pset.HasProperties)[:3]:
                val = getattr(prop, 'NominalValue', None)
                val_str = val.wrappedValue if val else 'N/A'
                print(f"    {prop.Name}: {val_str}")

    return {
        'schema': schema,
        'total_entities': total_entities,
        'unique_types': len(type_counter),
        'type_counts': dict(type_counter),
        'load_time': load_time,
    }


if __name__ == '__main__':
    ifc_dir = Path('/home/coffin/dev/bim-ontology/references')
    ifc_files = sorted(ifc_dir.glob('*.ifc'))

    if not ifc_files:
        print("IFC 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"발견된 IFC 파일: {len(ifc_files)}개")
    for f in ifc_files:
        print(f"  - {f.name} ({f.stat().st_size / (1024*1024):.1f} MB)")

    # 작은 파일부터 분석
    results = {}
    for ifc_path in sorted(ifc_files, key=lambda p: p.stat().st_size):
        try:
            results[ifc_path.name] = analyze_ifc(str(ifc_path))
        except Exception as e:
            print(f"\n오류 ({ifc_path.name}): {e}")

    # 요약
    print(f"\n{'='*60}")
    print("분석 요약")
    print(f"{'='*60}")
    for name, data in results.items():
        print(f"  {name}:")
        print(f"    스키마={data['schema']}, "
              f"엔티티={data['total_entities']:,}, "
              f"타입={data['unique_types']}, "
              f"로딩={data['load_time']:.1f}초")
