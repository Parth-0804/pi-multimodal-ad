"""Targeted final preservation checks; no model execution or raw-tree scanning."""
import datetime
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
STUDY = RUN.parent.parent
REPO = STUDY.parent.parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    assert read(RUN / "progress.json")["status"] == "COMPLETE_ON_PILOT_COVERAGE"
    selected = read(RUN / "model_selection/selected_model.json")
    tests = read(RUN / "checks/tests.json")
    assert tests["passed"] and tests["source_identity"] == selected["source_identity"]
    lock = read(RUN / "model_selection/selection_lock.json")
    assert sha(RUN / "model_selection/selected_model.json") == lock["selected_model_sha256"]
    assert sha(STUDY / "config.json") == lock["corruption_config_sha256"]
    for relative, digest in selected["source_identity"].items():
        assert sha(STUDY / relative) == digest, relative
    components = []
    for fold, items in selected["components"].items():
        for role, item in items.items():
            assert sha(REPO / item["path"]) == item["sha256"], item["path"]
            components.append(dict(fold=fold, role=role, **item))
    assert sha(RUN / "data/cohort_and_frames.json") == selected["cohort_sha256"]
    assert sha(RUN / "data/fit_partitions.json") == selected["partitions_sha256"]
    raw = {}
    for sample in read(RUN / "data/cohort_and_frames.json"):
        for prefix in ["source", "video"]:
            relative = sample[prefix + "_path"]
            expected = (sample[prefix + "_bytes"], sample[prefix + "_mtime_ns"])
            assert relative not in raw or raw[relative] == expected
            raw[relative] = expected
    for relative, expected in raw.items():
        stat = (REPO / relative).stat()
        assert (stat.st_size, stat.st_mtime_ns) == expected, relative
    basis = read(RUN / "provenance/versioned_selection_basis.json")
    old = STUDY / basis["old_run"]
    assert sha(old / "model_selection/selected_model.json") == basis["old_selected_model_sha256"]
    assert sha(old / "model_selection/selection_lock.json") == basis["old_selection_lock_sha256"]
    old_manifest = read(old / "provenance/package_manifest.json")
    required = ["README_FIRST.md", "model_selection/selection_report.md", "model_selection/clean_comparison.csv",
                "model_selection/clean_predictions/frozen_16_frames.csv", "comparison/RESULTS_SUMMARY.md"]
    for relative in required:
        key = str((old / relative).relative_to(STUDY))
        assert sha(old / relative) == old_manifest[key]["sha256"], relative
    evidence = dict(passed=True, observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    locked_source_files_verified=len(selected["source_identity"]), selected_components_verified=components,
                    raw_manifest_paths_size_and_mtime_verified=len(raw), raw_scope="Targeted manifest paths; size/mtime checks, not a full content hash of raw data.",
                    selection_and_corruption_config_unchanged=True, old_pilot_locks_and_required_reports_unchanged=True)
    (RUN / "checks/completion_integrity.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Verified {len(components)} selected component references, {len(raw)} raw file metadata records, and preserved pilot locks/reports.")


if __name__ == "__main__":
    main()
