# Namespace exports (no ifcopenshell required)
from .namespace_manager import (
    IFC4, IFC2X3, BIM, INST, BOT, SCHED, AWP, SP3D,
    get_ifc_namespace, bind_namespaces,
)

# Lazy import for RDFConverter to avoid ifcopenshell requirement at import time
def __getattr__(name):
    if name == "RDFConverter":
        from .ifc_to_rdf import RDFConverter
        return RDFConverter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "RDFConverter",
    "IFC4", "IFC2X3", "BIM", "INST", "BOT", "SCHED", "AWP", "SP3D",
    "get_ifc_namespace", "bind_namespaces",
]
