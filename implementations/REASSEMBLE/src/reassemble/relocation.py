"""Explicit, import-scoped location compatibility for preserved study sources.

This module does not launch a study, alter a configuration, bypass an identity
check, or modify global pathlib/os functions. Only Python modules underneath the
caller's explicit ``scope_roots`` receive the location-aware imports. Their
original bytes are compiled unchanged. The caller must enter the context before
importing those modules and must separately authorize any scientific execution.
"""
from __future__ import annotations

import builtins
from contextlib import contextmanager
import importlib.machinery
import importlib.util
import json
import os
import pathlib
import sys
import types


class Relocation:
    """Map physical storage while retaining historical path identities.

    ``mappings`` contains repository-relative historical -> current prefixes.
    Mappings must be terminal (no current prefix is another historical prefix).
    More specific prefixes override broader prefixes. A physical prefix must
    have one historical identity, so ambiguous reverse mappings are rejected.
    """

    def __init__(self, repo, mappings, scope_roots=()):
        self.repo = pathlib.Path(repo).resolve()
        pairs = []
        for old, new in mappings.items():
            old, new = pathlib.PurePosixPath(old), pathlib.PurePosixPath(new)
            if (old.is_absolute() or new.is_absolute() or ".." in old.parts
                    or ".." in new.parts or str(old) == "." or str(new) == "."):
                raise ValueError("Mappings must be bounded repository-relative prefixes")
            if old == new:
                continue
            pairs.append((self.repo / old, self.repo / new))
        current = [str(new) for _, new in pairs]
        if len(current) != len(set(current)):
            raise ValueError("Ambiguous historical identities for a physical prefix")
        self._forward = sorted(pairs, key=lambda pair: len(pair[0].parts), reverse=True)
        self._reverse = sorted(((new, old) for old, new in pairs),
                               key=lambda pair: len(pair[0].parts), reverse=True)
        for _, new in pairs:
            if self._replace(new, self._forward) != new:
                raise ValueError("Mapping destination is not terminal")
        self.scope_roots = tuple(self.physical(root if pathlib.Path(root).is_absolute()
                                               else self.repo / root).resolve()
                                 for root in scope_roots)
        relocation = self

        class HistoricalPath(type(pathlib.Path())):
            """Historical components; filesystem-facing strings use current storage."""

            def __init__(self, *segments):
                # pathlib normally consumes a PurePath's internal components,
                # not its __fspath__. Preserve those logical components here.
                parts = [part._logical_name() if isinstance(part, HistoricalPath)
                         else os.fspath(part) for part in segments]
                logical = relocation.logical(pathlib.Path(*parts))
                super().__init__(str(logical))

            def _logical_name(self):
                return pathlib.PurePath.__str__(self)

            def __str__(self):
                logical = pathlib.Path(self._logical_name())
                return str(relocation.physical(logical))

            def relative_to(self, other, *args, **kwargs):
                relative = super().relative_to(other, *args, **kwargs)
                # Provenance keys must not become filesystem-facing translated
                # strings. Return an ordinary relative Path, as distinct from
                # Path('old/prefix') supplied as a filesystem address.
                return pathlib.Path(relative._logical_name())

            def resolve(self, strict=False):
                physical = pathlib.Path(str(self)).resolve(strict=strict)
                return type(self)(relocation.logical(physical))

            def _make_child_relpath(self, name):
                # Python 3.12's implementation caches str(self) as internal
                # components; that would mix physical and historical identities.
                return self / name

        HistoricalPath.__name__ = "HistoricalPath"
        self.Path = HistoricalPath
        self._pathlib = self._proxy(pathlib, Path=HistoricalPath,
                                    PosixPath=HistoricalPath)
        self._os_path = self._proxy(os.path, relpath=self.relpath)
        self._os = self._proxy(os, path=self._os_path)
        self._importlib_util = self._proxy(importlib.util,
                                           spec_from_file_location=self.spec_from_file_location)
        self._importlib = self._proxy(importlib, util=self._importlib_util)
        self.loaded = set()

    @staticmethod
    def _proxy(module, **replacements):
        result = types.ModuleType(module.__name__)
        result.__dict__.update(vars(module))
        result.__dict__.update(replacements)
        return result

    @staticmethod
    def _replace(path, pairs):
        for source, destination in pairs:
            try:
                tail = path.relative_to(source)
            except ValueError:
                continue
            return destination / tail
        return path

    def logical(self, path):
        """Return a plain Path with the historical identity; no filesystem read."""
        if hasattr(path, "_logical_name"):
            return pathlib.Path(path._logical_name())
        path = pathlib.Path(path)
        if path.is_absolute():
            return self._replace(path, self._reverse)
        translated = self._replace(self.repo / path, self._reverse)
        return translated.relative_to(self.repo) if translated != self.repo / path else path

    def physical(self, path):
        """Return a plain Path to current storage; no existence/hash waiver."""
        path = self.logical(path)
        if path.is_absolute():
            return self._replace(path, self._forward)
        translated = self._replace(self.repo / path, self._forward)
        return translated if translated != self.repo / path else path

    def relpath(self, path, start=None):
        # Frozen code sometimes uses os.path.relpath instead of Path.relative_to.
        # Preserve identity keys for both styles; all other os functions remain
        # the real standard-library functions and consume physical __fspath__.
        return os.path.relpath(self.logical(path),
                               self.logical(start) if start is not None else None)

    def in_scope(self, path):
        if not path:
            return False
        path = self.physical(path).resolve()
        return any(path.is_relative_to(root) for root in self.scope_roots)

    def scoped_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        actual = builtins.__import__(name, globals, locals, fromlist, level)
        if level:
            return actual
        if name == "pathlib":
            return self._pathlib
        if name in {"os", "os.path"}:
            return self._os_path if name == "os.path" and fromlist else self._os
        if name == "importlib.util":
            return self._importlib_util if fromlist else self._importlib
        if name == "importlib":
            return self._importlib
        return actual

    def wrap_spec(self, spec):
        if spec and self.in_scope(spec.origin):
            if not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
                raise ImportError(f"Unsupported scoped loader: {spec.origin}")
            spec.loader = _SourceLoader(spec.loader, self)
        return spec

    def spec_from_file_location(self, name, location=None, **kwargs):
        # Preserve historical explicit loaders such as original_api.py without
        # changing importlib globally or weakening their module-name handling.
        location = self.physical(location) if location is not None else None
        return self.wrap_spec(importlib.util.spec_from_file_location(name, location, **kwargs))


class _SourceLoader:
    def __init__(self, original, relocation):
        self.original = original
        self.relocation = relocation

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        filename = self.original.get_filename(module.__name__)
        # Read only the explicitly imported Python source. Compilation neither
        # rewrites it nor substitutes an amended scientific implementation.
        source = self.original.get_data(filename)
        namespace = dict(vars(builtins))
        namespace["__import__"] = self.relocation.scoped_import
        module.__dict__["__builtins__"] = namespace
        self.relocation.loaded.add(module.__name__)
        exec(compile(source, filename, "exec"), module.__dict__)

    def get_source(self, fullname):
        return self.original.get_source(fullname)

    def get_filename(self, fullname):
        return self.original.get_filename(fullname)


class _Finder:
    def __init__(self, relocation):
        self.relocation = relocation

    def find_spec(self, fullname, path=None, target=None):
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec and self.relocation.in_scope(spec.origin):
            return self.relocation.wrap_spec(spec)
        return None


@contextmanager
def relocation_context(repo, mappings, scope_roots):
    """Adapt explicit imports; restore import state on exit.

    Use inside a separately authorized operation. This is not a controller or a
    subprocess bootstrap. Child interpreters need their own explicit context.
    Existing stop and identity checks remain mandatory and unchanged.
    """
    relocation = Relocation(repo, mappings, scope_roots)
    for name, module in tuple(sys.modules.items()):
        if relocation.in_scope(getattr(module, "__file__", None)):
            raise RuntimeError(f"Enter relocation_context before importing {name}")
    finder = _Finder(relocation)
    old_path = list(sys.path)
    old_modules = dict(sys.modules)
    sys.meta_path.insert(0, finder)
    try:
        yield relocation
    finally:
        sys.meta_path.remove(finder)
        sys.path[:] = old_path
        for name in relocation.loaded:
            if name in old_modules:
                sys.modules[name] = old_modules[name]
            else:
                sys.modules.pop(name, None)


def reassemble_layout():
    """Read the reviewed location map only; import no study or model modules."""
    location = pathlib.Path(__file__).resolve().parents[2] / "configs/relocation_paths.json"
    return json.loads(location.read_text())


def reassemble_relocation(repo):
    """Return the explicit context for the preserved REASSEMBLE studies."""
    layout = reassemble_layout()
    return relocation_context(repo, layout["mappings"], layout["scope_roots"])
