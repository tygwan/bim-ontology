"""동적 온톨로지 스키마 관리자.

Palantir Foundry 스타일의 런타임 온톨로지 편집 기능을 제공합니다.
Object Type, Property Type, Link Type, Classification Rules를 CRUD합니다.
"""

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from rdflib import Graph, Literal, URIRef, RDF, RDFS, OWL, XSD

from ..converter.namespace_manager import BIM

logger = logging.getLogger(__name__)

RULES_FILE = Path("data/ontology/classification_rules.json")
SCHEMA_FILE = Path("data/ontology/custom_schema.json")


@dataclass
class ObjectTypeInfo:
    name: str
    parent_class: str
    label: str
    description: str = ""


@dataclass
class PropertyTypeInfo:
    name: str
    domain: str
    range_type: str  # "string", "double", "integer", "boolean", "uri"
    label: str = ""


@dataclass
class LinkTypeInfo:
    name: str
    domain: str
    range_class: str
    inverse_name: str = ""
    label: str = ""


class OntologySchemaManager:
    """OWL 온톨로지 스키마를 동적으로 관리한다."""

    def __init__(self, graph: Optional[Graph] = None):
        self._graph = graph or Graph()
        self._custom_types: dict[str, ObjectTypeInfo] = {}
        self._custom_properties: dict[str, PropertyTypeInfo] = {}
        self._custom_links: dict[str, LinkTypeInfo] = {}
        self._classification_rules: dict[str, list[str]] = {}
        self._load_persisted_data()

    def _load_persisted_data(self):
        """파일에서 저장된 스키마/규칙을 로딩한다."""
        if RULES_FILE.exists():
            try:
                self._classification_rules = json.loads(RULES_FILE.read_text())
                logger.info("분류 규칙 로딩: %d개", len(self._classification_rules))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("분류 규칙 파일 로딩 실패: %s", e)

        if SCHEMA_FILE.exists():
            try:
                data = json.loads(SCHEMA_FILE.read_text())
                for t in data.get("types", []):
                    self._custom_types[t["name"]] = ObjectTypeInfo(**t)
                for p in data.get("properties", []):
                    self._custom_properties[p["name"]] = PropertyTypeInfo(**p)
                for lnk in data.get("links", []):
                    self._custom_links[lnk["name"]] = LinkTypeInfo(**lnk)
                logger.info(
                    "커스텀 스키마 로딩: %d types, %d props, %d links",
                    len(self._custom_types),
                    len(self._custom_properties),
                    len(self._custom_links),
                )
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("커스텀 스키마 파일 로딩 실패: %s", e)

    def _save_schema(self):
        """커스텀 스키마를 파일에 저장한다."""
        SCHEMA_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "types": [asdict(t) for t in self._custom_types.values()],
            "properties": [asdict(p) for p in self._custom_properties.values()],
            "links": [asdict(lnk) for lnk in self._custom_links.values()],
        }
        SCHEMA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def _save_rules(self):
        """분류 규칙을 파일에 저장한다."""
        RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
        RULES_FILE.write_text(json.dumps(self._classification_rules, indent=2, ensure_ascii=False))

    # ---------- Object Types (OWL Classes) ----------

    def list_object_types(self) -> list[ObjectTypeInfo]:
        """등록된 모든 Object Type을 반환한다."""
        builtin: list[ObjectTypeInfo] = []
        for s in self._graph.subjects(RDF.type, OWL.Class):
            if str(s).startswith(str(BIM)):
                name = str(s).replace(str(BIM), "")
                label_objs = list(self._graph.objects(s, RDFS.label))
                label = str(label_objs[0]) if label_objs else name
                parent_objs = list(self._graph.objects(s, RDFS.subClassOf))
                parent = str(parent_objs[0]).replace(str(BIM), "") if parent_objs else ""
                builtin.append(ObjectTypeInfo(name=name, parent_class=parent, label=label))

        custom = list(self._custom_types.values())
        return builtin + custom

    def create_object_type(
        self, name: str, parent_class: str = "BIMElement", label: str = "", description: str = ""
    ) -> ObjectTypeInfo:
        """새 Object Type(OWL Class)을 생성한다."""
        info = ObjectTypeInfo(
            name=name,
            parent_class=parent_class,
            label=label or name,
            description=description,
        )
        self._custom_types[name] = info
        self._save_schema()
        return info

    def update_object_type(self, name: str, **kwargs) -> ObjectTypeInfo:
        """기존 Object Type을 수정한다."""
        if name not in self._custom_types:
            raise KeyError(f"Object Type '{name}' not found in custom types")
        info = self._custom_types[name]
        for k, v in kwargs.items():
            if hasattr(info, k):
                setattr(info, k, v)
        self._custom_types[name] = info
        self._save_schema()
        return info

    def delete_object_type(self, name: str) -> bool:
        """Object Type을 삭제한다."""
        if name in self._custom_types:
            del self._custom_types[name]
            self._save_schema()
            return True
        return False

    # ---------- Property Types (OWL Properties) ----------

    def list_property_types(self) -> list[PropertyTypeInfo]:
        """등록된 모든 Property Type을 반환한다."""
        builtin: list[PropertyTypeInfo] = []
        for s in self._graph.subjects(RDF.type, OWL.DatatypeProperty):
            if str(s).startswith(str(BIM)):
                name = str(s).replace(str(BIM), "")
                domain_objs = list(self._graph.objects(s, RDFS.domain))
                domain = str(domain_objs[0]).replace(str(BIM), "") if domain_objs else ""
                range_objs = list(self._graph.objects(s, RDFS.range))
                range_type = str(range_objs[0]).split("#")[-1] if range_objs else "string"
                builtin.append(PropertyTypeInfo(name=name, domain=domain, range_type=range_type))

        custom = list(self._custom_properties.values())
        return builtin + custom

    def create_property_type(
        self, name: str, domain: str = "BIMElement", range_type: str = "string", label: str = ""
    ) -> PropertyTypeInfo:
        """새 Property Type을 생성한다."""
        info = PropertyTypeInfo(name=name, domain=domain, range_type=range_type, label=label or name)
        self._custom_properties[name] = info
        self._save_schema()
        return info

    # ---------- Link Types (OWL ObjectProperties) ----------

    def list_link_types(self) -> list[LinkTypeInfo]:
        """등록된 모든 Link Type을 반환한다."""
        builtin: list[LinkTypeInfo] = []
        for s in self._graph.subjects(RDF.type, OWL.ObjectProperty):
            if str(s).startswith(str(BIM)):
                name = str(s).replace(str(BIM), "")
                domain_objs = list(self._graph.objects(s, RDFS.domain))
                domain = str(domain_objs[0]).replace(str(BIM), "") if domain_objs else ""
                range_objs = list(self._graph.objects(s, RDFS.range))
                range_cls = str(range_objs[0]).replace(str(BIM), "") if range_objs else ""
                inverse_objs = list(self._graph.objects(s, OWL.inverseOf))
                inverse = str(inverse_objs[0]).replace(str(BIM), "") if inverse_objs else ""
                builtin.append(LinkTypeInfo(name=name, domain=domain, range_class=range_cls, inverse_name=inverse))

        custom = list(self._custom_links.values())
        return builtin + custom

    def create_link_type(
        self, name: str, domain: str, range_class: str, inverse_name: str = "", label: str = ""
    ) -> LinkTypeInfo:
        """새 Link Type을 생성한다."""
        info = LinkTypeInfo(
            name=name, domain=domain, range_class=range_class,
            inverse_name=inverse_name, label=label or name,
        )
        self._custom_links[name] = info
        self._save_schema()
        return info

    # ---------- Classification Rules ----------

    def list_classification_rules(self) -> dict[str, list[str]]:
        """현재 분류 규칙을 반환한다."""
        return dict(self._classification_rules)

    def update_classification_rules(self, rules: dict[str, list[str]]) -> None:
        """분류 규칙을 업데이트한다."""
        self._classification_rules = rules
        self._save_rules()

    # ---------- Schema Operations ----------

    XSD_MAP = {
        "string": XSD.string,
        "double": XSD.double,
        "integer": XSD.integer,
        "boolean": XSD.boolean,
        "date": XSD.date,
        "dateTime": XSD.dateTime,
        "duration": XSD.duration,
    }

    def apply_schema_to_graph(self, graph: Graph) -> int:
        """커스텀 스키마를 그래프에 적용한다. 추가된 트리플 수를 반환한다."""
        before = len(graph)

        for t in self._custom_types.values():
            cls_uri = BIM[t.name]
            graph.add((cls_uri, RDF.type, OWL.Class))
            parent_uri = BIM[t.parent_class] if t.parent_class else BIM.BIMElement
            graph.add((cls_uri, RDFS.subClassOf, parent_uri))
            graph.add((cls_uri, RDFS.label, Literal(t.label)))
            if t.description:
                graph.add((cls_uri, RDFS.comment, Literal(t.description)))

        for p in self._custom_properties.values():
            prop_uri = BIM[p.name]
            graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            graph.add((prop_uri, RDFS.domain, BIM[p.domain]))
            range_uri = self.XSD_MAP.get(p.range_type, XSD.string)
            graph.add((prop_uri, RDFS.range, range_uri))

        for lnk in self._custom_links.values():
            link_uri = BIM[lnk.name]
            graph.add((link_uri, RDF.type, OWL.ObjectProperty))
            graph.add((link_uri, RDFS.domain, BIM[lnk.domain]))
            graph.add((link_uri, RDFS.range, BIM[lnk.range_class]))
            if lnk.inverse_name:
                inv_uri = BIM[lnk.inverse_name]
                graph.add((inv_uri, RDF.type, OWL.ObjectProperty))
                graph.add((inv_uri, OWL.inverseOf, link_uri))

        return len(graph) - before

    def export_schema(self, fmt: str = "json") -> str:
        """스키마를 JSON으로 내보낸다."""
        data = {
            "types": [asdict(t) for t in self._custom_types.values()],
            "properties": [asdict(p) for p in self._custom_properties.values()],
            "links": [asdict(lnk) for lnk in self._custom_links.values()],
            "classification_rules": self._classification_rules,
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def import_schema(self, data: str, fmt: str = "json") -> None:
        """JSON에서 스키마를 가져온다."""
        parsed = json.loads(data)
        for t in parsed.get("types", []):
            self._custom_types[t["name"]] = ObjectTypeInfo(**t)
        for p in parsed.get("properties", []):
            self._custom_properties[p["name"]] = PropertyTypeInfo(**p)
        for lnk in parsed.get("links", []):
            self._custom_links[lnk["name"]] = LinkTypeInfo(**lnk)
        if "classification_rules" in parsed:
            self._classification_rules = parsed["classification_rules"]
            self._save_rules()
        self._save_schema()
