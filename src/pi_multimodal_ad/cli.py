"""DEPRECATED compatibility forwarding only.

Canonical implementation: phm2026.cli.
Retained for external/historical callers; no automatic removal date.
Do not add scientific implementation here.
"""

if __name__ == "__main__":
    import runpy as _runpy
    _runpy.run_module('phm2026.cli', run_name="__main__", alter_sys=True)
else:
    import importlib as _importlib
    import sys as _sys
    _sys.modules[__name__] = _importlib.import_module('phm2026.cli')
