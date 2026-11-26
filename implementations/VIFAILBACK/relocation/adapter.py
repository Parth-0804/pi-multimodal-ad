"""Explicit import context for unchanged, relocated ViFailback source.

The command line only inspects saved paths and source identities. It never runs
the frozen controllers, fitting, preprocessing, inference or report writers.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path
import sys


MATCHED = "experiments/matched_cnn_20_100_f2_20261111"
MAPPINGS = {
    "DATASET_RESEARCH/VIFAILBACK_VERIFICATION":
        "implementations/VIFAILBACK/02_dataset_verification/independent_verification",
    "VIFAILBACK": "implementations/VIFAILBACK",
    "26.10.2026_feedback_experiments":
        "implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback",
    "parth_ws_bootstrap": "implementations/REASSEMBLE/experiments/bootstrap",
    "MILLING DATASET": "implementations/MSM/experiments/legacy",
}


def repository_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "pyproject.toml").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root not found; pass an explicit repository path")


def source_scopes(repo: Path) -> list[Path]:
    project = repo / "implementations/VIFAILBACK"
    return [
        project / "src",
        project / "scripts",
        project / MATCHED / "src",
        project / MATCHED / "scripts",
        repo / MAPPINGS["parth_ws_bootstrap"],
        repo / MAPPINGS["26.10.2026_feedback_experiments"],
    ]


@contextmanager
def vifailback_context(repo: Path | str | None = None):
    """Activate path compatibility explicitly, before any ViFailback imports.

    The shared loader supplies historical logical paths only inside the listed
    frozen namespaces. Filesystem operations use their mapped physical paths.
    Python's global pathlib and os modules are not patched. Keep all use of the
    imported frozen modules inside this context. This is not run authorization.
    """
    repo = Path(repo).resolve() if repo is not None else repository_root()
    existing = [name for name in sys.modules
                if name in {"vifailback", "matched_vifailback"}
                or name.startswith(("vifailback.", "matched_vifailback."))]
    if existing:
        raise RuntimeError("Activate before importing ViFailback modules: "
                           + ", ".join(sorted(existing)))
    old_path = sys.path[:]
    initial_modules = set(sys.modules)
    project = repo / "implementations/VIFAILBACK"
    sys.path[:0] = [str(repo / "src"), str(project / "src"),
                   str(project / MATCHED / "src")]
    try:
        relocation = importlib.import_module("reassemble.relocation")
        with relocation.relocation_context(repo, MAPPINGS, source_scopes(repo)) as layout:
            yield layout
    finally:
        sys.path[:] = old_path
        for name in set(sys.modules) - initial_modules:
            if name in {"vifailback", "matched_vifailback"} or name.startswith(
                    ("vifailback.", "matched_vifailback.")):
                sys.modules.pop(name, None)


def _comparison(name: str, expected: dict, actual: dict) -> dict:
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(key for key in expected.keys() & actual.keys()
                     if expected[key] != actual[key])
    if missing or extra or changed:
        raise ValueError(json.dumps({"identity": name, "missing": missing,
                                     "extra": extra, "changed": changed}))
    return {"identity": name, "entries": len(expected), "exact_match": True}


def verify_source_identities(repo: Path | str | None = None) -> dict:
    """Hash only bounded source/configuration files; never open model inputs.

    Original dictionaries and digests are compared without dropping entries or
    refreshing receipts. A moved/modified/added source therefore remains visible
    to the existing integrity gate. This does not reproduce an experiment.
    """
    repo = Path(repo).resolve() if repo is not None else repository_root()
    project = repo / "implementations/VIFAILBACK"
    provenance = json.loads((project / "logs/20261029T004900Z/EXECUTION_PROVENANCE.json").read_text())
    freeze = json.loads((project / MATCHED / "13_reproducibility/IMPLEMENTATION_FREEZE.json").read_text())
    # Check the exact modules we will import before executing their definitions.
    # Their inspected originals import standard-library helpers only.
    inspected_imports = [
        ("src/vifailback/__init__.py", provenance["implementation"]),
        ("src/vifailback/common.py", provenance["implementation"]),
        ("src/vifailback/reference.py", provenance["implementation"]),
        (MATCHED + "/src/matched_vifailback/__init__.py", freeze["implementation"]),
        (MATCHED + "/src/matched_vifailback/common.py", freeze["implementation"]),
    ]
    for relative, expected in inspected_imports:
        actual = hashlib.sha256((project / relative).read_bytes()).hexdigest()
        if actual != expected["VIFAILBACK/" + relative]:
            raise ValueError("changed frozen import source: " + relative)
    initial_modules = set(sys.modules)
    with vifailback_context(repo):
        legacy = importlib.import_module("vifailback.common")
        reference = importlib.import_module("vifailback.reference")
        matched = importlib.import_module("matched_vifailback.common")
        checks = [
            _comparison("original_implementation", provenance["implementation"], legacy.code_identity()),
            _comparison("reused_REASSEMBLE_source", provenance["reused_source"], reference.identities()),
            _comparison("matched_implementation", freeze["implementation"], matched.code_identity()),
        ]
        protocol_file = project / MATCHED / "01_protocol_and_source_evidence/protocol.json"
        protocol_sha = hashlib.sha256(protocol_file.read_bytes()).hexdigest()
        if not (protocol_sha == freeze["protocol_sha256"] == matched.PROTOCOL_SHA256):
            raise ValueError("Frozen matched protocol identity changed")
        checks.append({"identity": "matched_protocol", "exact_match": True,
                       "sha256": protocol_sha})
    model_libraries = sorted({name.split(".")[0] for name in set(sys.modules) - initial_modules}
                             & {"torch", "transformers", "numpy", "scipy", "sklearn", "cv2", "PIL"})
    if model_libraries:
        raise RuntimeError("Unexpected model-library import during source inspection")
    return {"checks": checks, "models_imported": False,
            "new_model_library_imports": model_libraries,
            "raw_payloads_or_checkpoints_read": False,
            "experiment_execution": False,
            "scope": "Saved source/configuration identity and relocation checks only"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("identities", help="compare retained source/configuration identities")
    resolve = sub.add_parser("resolve", help="locate a saved path without opening it")
    resolve.add_argument("saved_path")
    args = parser.parse_args(argv)
    repo = args.repo.resolve() if args.repo is not None else repository_root()
    if args.command == "identities":
        result = verify_source_identities(repo)
    else:
        with vifailback_context(repo) as layout:
            result = {"saved_path": args.saved_path,
                      "physical_path": str(layout.physical(repo / args.saved_path))}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
