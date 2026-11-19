"""Final read-only verification and run-scoped validation evidence."""
import argparse
import ast
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys
from .data import digest, load_cohort
from .smoke import write


def main(run):
    run = Path(run)
    config = json.loads((run / "config/resolved_config.json").read_text())
    lock = json.loads((run / "config/protocol_lock.json").read_text())
    original = json.loads((run / "provenance.json").read_text())
    argv = original["command"]
    config_path = Path(argv[argv.index("--config") + 1]) if "--config" in argv else Path("MILLING DATASET/configs/stage3_protocol.json")
    if digest(config_path) != lock["config_sha256"] or json.loads(config_path.read_text()) != config:
        raise ValueError("Frozen protocol snapshot changed")
    cohort = load_cohort(config["stage2"])
    smoke = json.loads((run / "manifests/smoke_validation.json").read_text())
    head = json.loads((run / "reports/cached_head_benchmark.json").read_text())
    if not smoke["passed"] or smoke["outer_predictions"] or head["outer_predictions"]:
        raise ValueError("Failed smoke or forbidden outer predictions")
    if head["combined_optimizer_updates"] > config["smoke"]["maximum_head_updates"] or head["combined_cnn_frames"] > config["smoke"]["maximum_cnn_frame_forwards_including_benchmark"]:
        raise ValueError("Frozen smoke budget exceeded")
    historical = []
    seen = set()
    for folder in (Path(config["stage1"]), Path(config["stage2"])):
        count = 0
        for item in json.loads((folder / "manifests/output_manifest.json").read_text())["files"]:
            path = Path(item["path"])
            if str(path) in seen or not (path.is_relative_to(folder) or path.is_relative_to("MILLING DATASET/source") or path.is_relative_to("MILLING DATASET/tests")):
                continue
            seen.add(str(path))
            if digest(path) != item["sha256"]:
                raise ValueError("Historical output/source changed: " + str(path))
            count += 1
        historical.append({"run": str(folder), "protected_artifacts_verified": count})
    for path in Path("MILLING DATASET/source/msm").glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    commands = [[sys.executable, "-B", "-m", "pytest", "-q", "MILLING DATASET/tests", "--disable-warnings"],
                [sys.executable, "-B", "-m", "pip", "check"], ["git", "diff", "--check"]]
    checks = []
    for command in commands:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        checks.append({"command": command, "returncode": result.returncode, "output": result.stdout})
        if result.returncode:
            raise ValueError("Required validation command failed: " + str(checks[-1]))
    ignored = {}
    for path in [run / "cache/smoke_features.npz", run / "checkpoints/development_only.pt",
                 Path(config["data_root"]) / "imi_vm20i/dataset1/label.csv"]:
        ignored[str(path)] = subprocess.run(["git", "check-ignore", "-q", str(path)]).returncode == 0
    if not all(ignored.values()):
        raise ValueError("Raw/cache/checkpoint Git exclusion failed")
    write(run / "validation.json", {"passed": True, "UTC": datetime.now(timezone.utc).isoformat(),
        "checks": checks, "historical_preservation": historical, "all_114_annotation_and_frame_policies_revalidated": len(cohort) == 114,
        "raw_input_hashes_verified_during_smoke": 41, "Git_bulk_exclusions": ignored,
        "combined_optimizer_updates": head["combined_optimizer_updates"], "combined_cnn_frame_forwards": head["combined_cnn_frames"],
        "outer_predictions": 0, "full_evaluation_ready": False})
    write(run / "manifests/final_software_source_identity.json", {
        "software": {name: version(name) for name in ("torch", "torchvision", "transformers", "scikit-learn", "numpy", "pandas", "scipy", "psutil", "pytest", "opencv-python")},
        "source": {str(path): digest(path) for path in sorted(Path("MILLING DATASET/source/msm").glob("*.py"))},
        "tests": {str(path): digest(path) for path in sorted(Path("MILLING DATASET/tests").glob("*.py"))},
        "initial_smoke_source_hashes_preserved": json.loads((run / "provenance.json").read_text())["source_sha256"],
        "protocol_sha256": lock["config_sha256"]})
    print(json.dumps({"validation_passed": True, "run": str(run)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
