#!/usr/bin/env python3
"""RDF 그래프 품질 검증 스크립트.

TTL 파일에 대해 8가지 카테고리의 SPARQL 기반 검증을 수행하고
터미널 리포트를 출력합니다.

사용법:
    python scripts/validate_rdf.py [TTL_PATH]
    python scripts/validate_rdf.py  # 기본값: data/rdf/nwd4op-12.ttl
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.triple_store import TripleStore

# SPARQL 공통 프리픽스
PREFIXES = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX bim:  <http://example.org/bim-ontology/schema#>
PREFIX inst: <http://example.org/bim-ontology/instance#>
PREFIX ifc:  <https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#>
"""


class RDFValidator:
    """RDF 그래프 품질 검증기."""

    # Other 비율 임계값 (15% 이하이면 PASS)
    OTHER_THRESHOLD = 0.15

    def __init__(self, ttl_path: str):
        self.ttl_path = Path(ttl_path)
        self.store = TripleStore()
        self.results: dict[str, dict[str, Any]] = {}
        self._load_time = 0.0

    def load(self):
        """TTL 파일을 로딩한다."""
        start = time.time()
        self.store.load(str(self.ttl_path))
        self._load_time = time.time() - start

    def _query(self, sparql: str) -> list[dict[str, Any]]:
        """프리픽스가 포함된 SPARQL 쿼리를 실행한다."""
        return self.store.query(PREFIXES + sparql)

    def run_all(self) -> dict[str, Any]:
        """모든 검증을 실행하고 결과를 반환한다."""
        self.check_schema()
        self.check_spatial_hierarchy()
        self.check_element_stats()
        self.check_uri_consistency()
        self.check_property_sets()
        self.check_required_properties()
        self.check_classification_quality()
        self.check_relationship_integrity()

        summary = {"pass": 0, "warn": 0, "info": 0, "fail": 0}
        for r in self.results.values():
            summary[r["status"]] += 1

        return {
            "ttl_path": str(self.ttl_path),
            "total_triples": self.store.count(),
            "load_time": round(self._load_time, 2),
            "checks": [
                {"name": name, **data} for name, data in self.results.items()
            ],
            "summary": summary,
        }

    # ---- 1. Schema Completeness ----

    def check_schema(self):
        """스키마(TBox) 완전성을 검증한다."""
        # OWL 클래스 수
        classes = self._query("""
            SELECT ?class WHERE {
                ?class a owl:Class .
                FILTER(STRSTARTS(STR(?class), "http://example.org/bim-ontology/schema#"))
            }
        """)

        # 데이터 프로퍼티 수
        data_props = self._query("""
            SELECT ?prop ?domain ?range WHERE {
                ?prop a owl:DatatypeProperty .
                OPTIONAL { ?prop rdfs:domain ?domain }
                OPTIONAL { ?prop rdfs:range ?range }
            }
        """)

        # 오브젝트 프로퍼티 수
        obj_props = self._query("""
            SELECT ?prop WHERE {
                ?prop a owl:ObjectProperty .
            }
        """)

        class_count = len(classes)
        dprop_count = len(data_props)
        oprop_count = len(obj_props)

        # 최소 필수: 5 공간 클래스 + PhysicalElement + SpatialElement + BIMElement = 8
        status = "pass" if class_count >= 8 and dprop_count >= 6 else "fail"

        self.results["schema_completeness"] = {
            "status": status,
            "details": {
                "owl_classes": class_count,
                "class_names": sorted(
                    r["class"].split("#")[-1] for r in classes
                ),
                "data_properties": dprop_count,
                "object_properties": oprop_count,
            },
        }

    # ---- 2. Spatial Hierarchy ----

    def check_spatial_hierarchy(self):
        """공간 계층 구조(Project→Site→Building→Storey)를 검증한다."""
        # 전체 체인 확인
        chain = self._query("""
            SELECT ?project ?site ?building ?storey WHERE {
                ?project a bim:Project .
                ?project bim:aggregates ?site .
                ?site a bim:Site .
                ?site bim:aggregates ?building .
                ?building a bim:Building .
                ?building bim:aggregates ?storey .
                ?storey a bim:BuildingStorey .
            }
        """)

        # Storey별 요소 수
        storey_elements = self._query("""
            SELECT ?storeyName (COUNT(?elem) AS ?count) WHERE {
                ?storey a bim:BuildingStorey .
                ?storey bim:hasName ?storeyName .
                ?elem bim:isContainedIn ?storey .
            } GROUP BY ?storeyName ORDER BY DESC(?count)
        """)

        # 개별 카운트
        projects = self._query("SELECT (COUNT(?p) AS ?c) WHERE { ?p a bim:Project }")
        sites = self._query("SELECT (COUNT(?s) AS ?c) WHERE { ?s a bim:Site }")
        buildings = self._query("SELECT (COUNT(?b) AS ?c) WHERE { ?b a bim:Building }")
        storeys = self._query("SELECT (COUNT(?s) AS ?c) WHERE { ?s a bim:BuildingStorey }")

        has_chain = len(chain) > 0
        status = "pass" if has_chain else "fail"

        self.results["spatial_hierarchy"] = {
            "status": status,
            "details": {
                "complete_chains": len(chain),
                "projects": projects[0]["c"] if projects else 0,
                "sites": sites[0]["c"] if sites else 0,
                "buildings": buildings[0]["c"] if buildings else 0,
                "storeys": storeys[0]["c"] if storeys else 0,
                "storey_elements": [
                    {"storey": r["storeyName"], "elements": r["count"]}
                    for r in storey_elements
                ],
            },
        }

    # ---- 3. Element Statistics ----

    def check_element_stats(self):
        """요소 통계를 수집한다."""
        # 총 물리적 요소 수
        total = self._query("""
            SELECT (COUNT(?e) AS ?total) WHERE {
                ?e a bim:PhysicalElement .
            }
        """)

        # 카테고리별 분포
        categories = self._query("""
            SELECT ?category (COUNT(?e) AS ?count) WHERE {
                ?e bim:hasCategory ?category .
            } GROUP BY ?category ORDER BY DESC(?count)
        """)

        total_count = total[0]["total"] if total else 0
        cat_count = len(categories)

        self.results["element_statistics"] = {
            "status": "info",
            "details": {
                "total_elements": total_count,
                "category_count": cat_count,
                "categories": [
                    {"name": r["category"], "count": r["count"]}
                    for r in categories
                ],
            },
        }

    # ---- 4. URI Consistency ----

    def check_uri_consistency(self):
        """URI 일관성을 검증한다 (orphan/unlinked 요소 검출)."""
        # isContainedIn 관계는 있지만 타입이 없는 요소 (URI 불일치)
        orphans = self._query("""
            SELECT ?orphan WHERE {
                ?orphan bim:isContainedIn ?storey .
                FILTER NOT EXISTS { ?orphan a bim:PhysicalElement }
            } LIMIT 20
        """)

        # 타입은 있지만 공간 포함관계가 없는 요소
        unlinked = self._query("""
            SELECT ?unlinked WHERE {
                ?unlinked a bim:PhysicalElement .
                FILTER NOT EXISTS { ?unlinked bim:isContainedIn ?any }
            } LIMIT 20
        """)

        orphan_count = len(orphans)
        unlinked_count = len(unlinked)

        if orphan_count == 0 and unlinked_count == 0:
            status = "pass"
        elif orphan_count > 0:
            status = "fail"
        else:
            status = "warn"

        self.results["uri_consistency"] = {
            "status": status,
            "details": {
                "orphan_elements": orphan_count,
                "orphan_samples": [r["orphan"].split("/")[-1] for r in orphans[:5]],
                "unlinked_elements": unlinked_count,
                "unlinked_samples": [r["unlinked"].split("/")[-1] for r in unlinked[:5]],
            },
        }

    # ---- 5. PropertySet Coverage ----

    def check_property_sets(self):
        """PropertySet 존재 및 커버리지를 검증한다."""
        # 전체 PropertySet 수
        pset_total = self._query("""
            SELECT (COUNT(?ps) AS ?total) WHERE { ?ps a bim:PropertySet }
        """)

        # PlantPropertySet (Smart3D) 수
        plant_pset = self._query("""
            SELECT (COUNT(?ps) AS ?total) WHERE { ?ps a bim:PlantPropertySet }
        """)

        # PropertySet가 있는 요소 수 vs 전체 요소 수
        coverage = self._query("""
            SELECT
                (COUNT(DISTINCT ?withPS) AS ?withPSet)
                (COUNT(DISTINCT ?all) AS ?totalElem)
            WHERE {
                ?all a bim:PhysicalElement .
                OPTIONAL {
                    ?withPS a bim:PhysicalElement .
                    ?withPS bim:hasPropertySet ?ps .
                }
            }
        """)

        total_psets = pset_total[0]["total"] if pset_total else 0
        plant_psets = plant_pset[0]["total"] if plant_pset else 0
        with_pset = coverage[0]["withPSet"] if coverage else 0
        total_elem = coverage[0]["totalElem"] if coverage else 0

        ratio = with_pset / total_elem if total_elem > 0 else 0

        if total_psets == 0:
            status = "fail"
        elif ratio < 0.3:
            status = "warn"
        else:
            status = "pass"

        self.results["property_set_coverage"] = {
            "status": status,
            "details": {
                "total_property_sets": total_psets,
                "plant_property_sets": plant_psets,
                "elements_with_pset": with_pset,
                "total_elements": total_elem,
                "coverage_ratio": round(ratio, 3),
            },
        }

    # ---- 6. Required Properties ----

    def check_required_properties(self):
        """필수 속성(GlobalId, Name) 존재를 검증한다."""
        # GlobalId 없는 PhysicalElement
        no_gid = self._query("""
            SELECT (COUNT(?e) AS ?count) WHERE {
                ?e a bim:PhysicalElement .
                FILTER NOT EXISTS { ?e bim:hasGlobalId ?id }
            }
        """)

        # Name 없는 PhysicalElement
        no_name = self._query("""
            SELECT (COUNT(?e) AS ?count) WHERE {
                ?e a bim:PhysicalElement .
                FILTER NOT EXISTS { ?e bim:hasName ?name }
            }
        """)

        missing_gid = no_gid[0]["count"] if no_gid else 0
        missing_name = no_name[0]["count"] if no_name else 0

        status = "pass" if missing_gid == 0 else "fail"

        self.results["required_properties"] = {
            "status": status,
            "details": {
                "missing_global_id": missing_gid,
                "missing_name": missing_name,
            },
        }

    # ---- 7. Classification Quality ----

    def check_classification_quality(self):
        """분류 품질을 검증한다 (Other 비율 확인)."""
        # Other 카테고리 수
        other_count_q = self._query("""
            SELECT (COUNT(?e) AS ?count) WHERE {
                ?e a bim:PhysicalElement .
                ?e bim:hasCategory "Other" .
            }
        """)

        # 전체 카테고리가 있는 요소 수
        total_categorized = self._query("""
            SELECT (COUNT(?e) AS ?count) WHERE {
                ?e bim:hasCategory ?cat .
            }
        """)

        other_count = other_count_q[0]["count"] if other_count_q else 0
        total_cat = total_categorized[0]["count"] if total_categorized else 0

        other_ratio = other_count / total_cat if total_cat > 0 else 0

        if other_ratio <= self.OTHER_THRESHOLD:
            status = "pass"
        elif other_ratio <= 0.30:
            status = "warn"
        else:
            status = "fail"

        self.results["classification_quality"] = {
            "status": status,
            "details": {
                "other_count": other_count,
                "total_categorized": total_cat,
                "other_ratio": round(other_ratio, 4),
                "threshold": self.OTHER_THRESHOLD,
            },
        }

    # ---- 8. Relationship Integrity ----

    def check_relationship_integrity(self):
        """관계 무결성을 검증한다."""
        # aggregates 관계 수
        agg = self._query("""
            SELECT (COUNT(*) AS ?count) WHERE {
                ?parent bim:aggregates ?child .
            }
        """)

        # containsElement 수
        contains = self._query("""
            SELECT (COUNT(*) AS ?count) WHERE {
                ?s bim:containsElement ?e .
            }
        """)

        # isContainedIn 수
        contained_in = self._query("""
            SELECT (COUNT(*) AS ?count) WHERE {
                ?e bim:isContainedIn ?s .
            }
        """)

        # containsElement ↔ isContainedIn 비대칭 검출
        asymmetric = self._query("""
            SELECT (COUNT(?e) AS ?count) WHERE {
                ?e bim:isContainedIn ?s .
                FILTER NOT EXISTS { ?s bim:containsElement ?e }
            }
        """)

        agg_count = agg[0]["count"] if agg else 0
        contains_count = contains[0]["count"] if contains else 0
        contained_count = contained_in[0]["count"] if contained_in else 0
        asym_count = asymmetric[0]["count"] if asymmetric else 0

        symmetric = contains_count == contained_count and asym_count == 0
        status = "pass" if symmetric and contains_count > 0 else "warn"

        self.results["relationship_integrity"] = {
            "status": status,
            "details": {
                "aggregation_pairs": agg_count,
                "contains_element": contains_count,
                "is_contained_in": contained_count,
                "asymmetric_pairs": asym_count,
                "symmetric": symmetric,
            },
        }

    # ---- Report Output ----

    def print_report(self):
        """터미널 리포트를 출력한다."""
        report = self.run_all()

        print()
        print("=" * 60)
        print("  RDF Validation Report")
        print("=" * 60)
        print(f"  TTL: {report['ttl_path']}")
        print(f"  Triples: {report['total_triples']:,}")
        print(f"  Load time: {report['load_time']:.2f}s")
        print("-" * 60)

        status_symbols = {
            "pass": "\033[32mPASS\033[0m",
            "warn": "\033[33mWARN\033[0m",
            "info": "\033[36mINFO\033[0m",
            "fail": "\033[31mFAIL\033[0m",
        }

        check_labels = {
            "schema_completeness": "Schema Completeness",
            "spatial_hierarchy": "Spatial Hierarchy",
            "element_statistics": "Element Statistics",
            "uri_consistency": "URI Consistency",
            "property_set_coverage": "PropertySet Coverage",
            "required_properties": "Required Properties",
            "classification_quality": "Classification Quality",
            "relationship_integrity": "Relationship Integrity",
        }

        for i, check in enumerate(report["checks"], 1):
            name = check["name"]
            status = check["status"]
            label = check_labels.get(name, name)
            symbol = status_symbols.get(status, status.upper())
            detail_str = self._format_detail(name, check["details"])
            dots = "." * (40 - len(label))
            print(f"  [{i}/8] {label} {dots} {symbol}")
            if detail_str:
                print(f"         {detail_str}")

        print("-" * 60)
        s = report["summary"]
        parts = []
        if s["pass"]:
            parts.append(f"\033[32m{s['pass']} PASS\033[0m")
        if s["warn"]:
            parts.append(f"\033[33m{s['warn']} WARN\033[0m")
        if s["info"]:
            parts.append(f"\033[36m{s['info']} INFO\033[0m")
        if s["fail"]:
            parts.append(f"\033[31m{s['fail']} FAIL\033[0m")
        print(f"  Overall: {', '.join(parts)}")
        print("=" * 60)
        print()

        return report

    def _format_detail(self, check_name: str, details: dict) -> str:
        """검증 항목별 요약 문자열을 반환한다."""
        match check_name:
            case "schema_completeness":
                return (
                    f"{details['owl_classes']} classes, "
                    f"{details['data_properties']} data props, "
                    f"{details['object_properties']} obj props"
                )
            case "spatial_hierarchy":
                return (
                    f"Project({details['projects']}) -> "
                    f"Site({details['sites']}) -> "
                    f"Building({details['buildings']}) -> "
                    f"Storey({details['storeys']})"
                )
            case "element_statistics":
                return (
                    f"{details['total_elements']:,} elements, "
                    f"{details['category_count']} categories"
                )
            case "uri_consistency":
                return (
                    f"{details['orphan_elements']} orphans, "
                    f"{details['unlinked_elements']} unlinked"
                )
            case "property_set_coverage":
                return (
                    f"{details['total_property_sets']:,} PSets, "
                    f"{details['elements_with_pset']:,}/{details['total_elements']:,} "
                    f"elements ({details['coverage_ratio']:.1%})"
                )
            case "required_properties":
                return (
                    f"{details['missing_global_id']} missing GlobalId, "
                    f"{details['missing_name']} missing Name"
                )
            case "classification_quality":
                return (
                    f"Other: {details['other_ratio']:.1%} "
                    f"({details['other_count']:,}/{details['total_categorized']:,}), "
                    f"target: <{details['threshold']:.0%}"
                )
            case "relationship_integrity":
                return (
                    f"{details['contains_element']:,} containment pairs, "
                    f"{details['aggregation_pairs']} aggregation pairs, "
                    f"symmetric={details['symmetric']}"
                )
            case _:
                return ""


def main():
    parser = argparse.ArgumentParser(description="RDF 그래프 품질 검증")
    parser.add_argument(
        "ttl_path",
        nargs="?",
        default="data/rdf/nwd4op-12.ttl",
        help="검증 대상 TTL 파일 경로 (기본값: data/rdf/nwd4op-12.ttl)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 형태로 결과 출력",
    )
    args = parser.parse_args()

    ttl = Path(args.ttl_path)
    if not ttl.exists():
        print(f"Error: TTL 파일을 찾을 수 없습니다: {ttl}", file=sys.stderr)
        sys.exit(1)

    validator = RDFValidator(str(ttl))
    if not args.json:
        print(f"Loading {ttl}...", flush=True)
    validator.load()

    if args.json:
        report = validator.run_all()
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        validator.print_report()


if __name__ == "__main__":
    main()
