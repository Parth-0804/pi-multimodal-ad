"""Minimal package forwarding; canonical leaf modules retain object identity."""

from importlib import import_module
from types import ModuleType
from ._mapping import IMPORT_MAP


def forward_package(namespace, canonical_name):
    """Keep the legacy package search path and forward its exported attributes."""
    canonical = import_module(canonical_name)
    legacy_name = namespace["__name__"]
    exports = list(getattr(canonical, "__all__", [
        name for name, value in vars(canonical).items()
        if not name.startswith("_") and not isinstance(value, ModuleType)
    ]))

    def get_attribute(name):
        legacy_child = legacy_name + "." + name
        if legacy_child in IMPORT_MAP:
            return import_module(legacy_child)
        return getattr(canonical, name)

    for name in exports:
        namespace[name] = get_attribute(name)
    namespace["__all__"] = exports
    namespace["__getattr__"] = get_attribute
    namespace["__dir__"] = lambda: sorted(set(namespace) | set(dir(canonical)))
