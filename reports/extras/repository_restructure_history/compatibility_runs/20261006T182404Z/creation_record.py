# One-time execution record; inspect before rerunning against existing files.
from pathlib import Path
import csv,json,ast
ROOT=Path.cwd();OUT=Path('docs/repository_restructure/compatibility_runs/20261006T182404Z');rows=list(csv.DictReader(Path('docs/repository_restructure/path_mapping.csv').open()))
modules={};scripts={}
def module(path):return path[4:-3].replace('/','.').removesuffix('.__init__')
for r in rows:
 if r['status']=='moved' and r['old_path'].startswith('src/pi_multimodal_ad/'):
  modules[module(r['old_path'])]=module(r['new_path'])
 if r['status']=='moved' and r['old_path'].startswith('scripts/'):
  scripts[r['old_path']]=r['new_path']
assert len(modules)==53 and len(scripts)==39
moves=[json.loads(x) for x in Path('docs/repository_restructure/moves.jsonl').read_text().splitlines()]
assert all(any(x['old']==old and x['new']==new for x in moves) for old,new in scripts.items())
created=[];modified=[]
def create(name,text):
 p=Path(name);assert not p.exists(),name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);created.append(name)
def change(name,text):
 p=Path(name);assert p.exists();p.write_text(text);modified.append(name)
for r in rows:
 if r['status']!='moved' or not r['old_path'].startswith('src/pi_multimodal_ad/'):continue
 old,new=module(r['old_path']),module(r['new_path'])
 header=f'"""DEPRECATED compatibility forwarding only.\n\nCanonical implementation: {new}.\nRetained for external/historical callers; no automatic removal date.\nDo not add scientific implementation here.\n"""\n'
 if Path(r['old_path']).name=='__init__.py':
  body=f'from pi_multimodal_ad._forward import forward_package as _forward_package\n\n_forward_package(globals(), {new!r})\n'
 else:
  body=f'''if __name__ == "__main__":
    import runpy as _runpy
    _runpy.run_module({new!r}, run_name="__main__", alter_sys=True)
else:
    import importlib as _importlib
    import sys as _sys
    _sys.modules[__name__] = _importlib.import_module({new!r})
'''
 create(r['old_path'],header+'\n'+body)
create('src/pi_multimodal_ad/_mapping.py','"""Authoritative forwarding data derived from the frozen migration CSV."""\n\nIMPORT_MAP = '+repr(modules)+'\n')
create('src/pi_multimodal_ad/_forward.py','''"""Minimal package forwarding; canonical leaf modules retain object identity."""

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
''')
for old,new in scripts.items():
 target=Path(new).relative_to('scripts').as_posix()
 create(old,f'''#!/usr/bin/env python3
"""DEPRECATED forwarding wrapper only; canonical script: {new}.

No scientific implementation belongs here. No automatic removal date.
"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / {target!r}
    runpy.run_path(str(target), run_name="__main__")
''')
create('src/phm2026/repository_paths.py','''"""Dependency-free repository location used by PHM configuration and acquisition."""

from pathlib import Path


class RepositoryRootError(ValueError):
    """Repository markers were not found above the supplied starting location."""


def find_repository_root(start: Path | None = None) -> Path:
    """Find the nearest parent containing both .git and AGENTS.md."""
    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".git").exists() and (directory / "AGENTS.md").is_file():
            return directory
    raise RepositoryRootError(f"repository root not found from {candidate}")
''')
p=Path('src/phm2026/utils/config.py');text=p.read_text();start=text.index('def find_repository_root(');end=text.index('\n\ndef _immutable',start)
text=text[:start]+'''def find_repository_root(start: Path | None = None) -> Path:
    """Locate the repository while preserving the public ConfigError contract."""
    try:
        return _locate_repository_root(start)
    except RepositoryRootError as exc:
        raise ConfigError(str(exc)) from exc
'''+text[end:]
text=text.replace('import yaml\n','import yaml\n\nfrom ..repository_paths import RepositoryRootError, find_repository_root as _locate_repository_root\n')
change(str(p),text)
p=Path('src/phm2026/acquisition/phm_download.py');text=p.read_text();assert 'REPO = Path(__file__).resolve().parents[3]' in text
text=text.replace('REPO = Path(__file__).resolve().parents[3]','from ..repository_paths import find_repository_root\n\nREPO = find_repository_root(Path(__file__))');change(str(p),text)
create('pyproject.toml','''[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[project]
name = "pi-multimodal-ad"
version = "0.1.0"
description = "Domain-owned thesis research pipelines and legacy compatibility interfaces"
requires-python = ">=3.10"

[tool.setuptools]
package-dir = {"" = "src"}
include-package-data = false

[tool.setuptools.packages.find]
where = ["src"]
include = ["phm2026*", "intel_welding*", "reassemble*", "pi_multimodal_ad*"]
namespaces = false
''')
create('src/pi_multimodal_ad/README.md','''# Legacy Python compatibility

Canonical scientific implementation lives only in `src/phm2026/`. These files forward the 53 original module/package paths from the migration manifest. Leaf modules alias the canonical module object, including private helpers and mutable module state; package facades preserve legacy child-module discovery and forward canonical exports.

New work should import `phm2026.*`. Old interfaces remain supported for external notebooks, historical serialized references and downstream callers. No automatic deletion is scheduled and no warning noise is added. Contract: `docs/repository_restructure/COMPATIBILITY_CONTRACT.md`; tests: `tests/compatibility/`.
''')
(OUT/'interfaces.json').write_text(json.dumps({'modules':modules,'scripts':scripts},indent=2))
(OUT/'task_manifest.json').write_text(json.dumps({'created_files':created,'modified_files':modified,'planned_remaining':['tests/compatibility/','docs/repository_restructure/COMPATIBILITY_CONTRACT.md','docs/repository_restructure/COMPATIBILITY_VALIDATION.md','docs/repository_restructure/compatibility_matrix.csv','README.md','REPO_MAP.md','docs/repository_restructure/.gitignore'],'canonical_architecture_moves':0,'package_install':'editable; --no-deps --no-build-isolation; no dependency upgrades'},indent=2))
print('Created',len(created),'files; modified',modified)
