"""Benchmark decoding only the 16 frames the model consumes.

Every selected-frame hash is derived from a verified 32-frame parent cache.
This removes unused-frame CPU work while preserving exact model inputs.
"""
import argparse
import datetime as dt
import hashlib
import os
from pathlib import Path
import resource
import shlex
import subprocess
import sys
import time
import uuid

import numpy as np
import torch

import gpu_audit as audit
from isolated_decode import IsolatedDecoder


class Selected16Dataset(audit.PixelDataset):
    def __init__(self, run, repeats=1):
        super().__init__(run, repeats)
        self.decoder = None

    def __getitem__(self, index):
        if self.decoder is None:
            c = audit.read(self.root / "config/resolved_config.json")
            original = audit.read(audit.REPO / c["study_root"] / "config/resolved_config.json")
            self.decoder = IsolatedDecoder(audit.REPO, original["weights_dir"], original["rescale_factor"],
                                           decoder_threads=c["decoder_threads_per_open_video"])
        row = self.rows[index % len(self.rows)]
        # The decoder's index-list parameter is named frames32 for historical
        # identity compatibility; here the explicit selected16 list is supplied.
        request = dict(row, frames32=row["frames16"])
        start = time.perf_counter()
        u = self.decoder(request)
        decoded = time.perf_counter()
        assert u.shape[0] == 16
        assert hashlib.sha256(u.tobytes()).hexdigest() == row["selected16_sha256"], "SELECTED16_PIXEL_DRIFT"
        hashed = time.perf_counter()
        x = torch.from_numpy(u.astype("float32") * np.float32(1 / 255))
        return x, torch.tensor([row["failure"]], dtype=torch.float32), {
            "read_s": 0.0, "decompress_s": decoded - start,
            "hash_s": hashed - decoded, "preprocess_s": time.perf_counter() - hashed,
        }


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["run", "worker"])
    parser.add_argument("--parent-run", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--name")
    args = parser.parse_args()
    if args.mode == "worker":
        if args.run is None or not args.run.resolve().is_relative_to(audit.BASE / "runs"):
            parser.error("Worker needs a new audit run")
        audit.PixelDataset = Selected16Dataset
        from managed_loader import loader
        audit.loader = loader
        audit.benchmark(args.run.resolve(), args.name)
        from profile_pipeline import profile_pipeline
        profile_pipeline(args.run.resolve(), args.name)
        return
    if args.parent_run is None or not args.parent_run.resolve().is_relative_to(audit.BASE / "runs"):
        parser.error("A verified warm-cache audit run is required")
    parent = args.parent_run.resolve()
    assert audit.read(parent / "reports/performance_gate.json")["numerical_and_gradient_checks"]
    c = audit.read(parent / "config/resolved_config.json")
    c["input_mode"] = "selected16_exact_live_decode_no_persistent_pixels"
    c["decoder_threads_per_open_video"] = 2
    c["worker_shutdown"] = "cooperative exhaustion and explicit decoder release; require zero exit codes"
    c["timing_field_interpretation"] = {"decompress_s": "16-frame video decode and original processor seconds"}
    c["configurations"] = [dict(s, name="selected16_" + s["name"]) for s in c["configurations"] if s["workers"]]
    c["warnings"] = ["Training-only bounded subset; all selected16 hashes must match their verified 32-frame parents.",
                     "OS page cache affects video I/O; this does not measure cold physical storage.",
                     "32-frame scientific conditions and a new multi-seed matrix remain outside this audit."]
    audit.validate_config(c)
    run = audit.BASE / "runs" / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-selected16-" + uuid.uuid4().hex[:8])
    run.mkdir(exist_ok=False)
    start = time.monotonic()
    audit.write(run / "config/resolved_config.json", c)
    for name in ("manifests/job.json", "manifests/inputs.json", "reports/hardware.json"):
        audit.write(run / name, audit.read(parent / name))
    rows = audit.read(parent / "manifests/selected_training.json")
    for row in rows:
        with np.load(parent / "cache" / (row["sample_id"] + ".npz"), allow_pickle=False) as z:
            u = z["pixels"]
        assert hashlib.sha256(u.tobytes()).hexdigest() == row["pixel_content_sha256"]
        row["selected16_sha256"] = hashlib.sha256(u[row["positions16_in32"]].tobytes()).hexdigest()
    audit.write(run / "manifests/selected_training.json", rows)
    audit.write(run / "provenance.json", {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "command": shlex.join(sys.argv),
        "parent_run": str(parent.relative_to(audit.REPO)),
        "git_commit": audit.command(["git", "rev-parse", "HEAD"]),
        "git_status": audit.command(["git", "status", "--short", "--untracked-files=all"]),
        "source_identities": {p.name: audit.digest(p) for p in (
            Path(__file__), Path(audit.__file__), Path(__file__).with_name("isolated_decode.py"),
            Path(__file__).with_name("profile_pipeline.py"), Path(__file__).with_name("managed_loader.py"))},
        "methodology": "Remove unused-frame decoding only; assert bitwise selected16 identity derived from verified original32 pixels"})
    study = audit.REPO / c["study_root"]
    before = audit.preserved_files(study)
    audit.write(run / "manifests/historical_before.json", before)
    print("SELECTED16_RUN", str(run.relative_to(audit.REPO)), flush=True)
    for setting in c["configurations"]:
        cmd = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", "--run", str(run), "--name", setting["name"]]
        with (run / (setting["name"] + ".log")).open("x") as log:
            p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
        print(setting["name"], "exit", p.returncode, flush=True)
        if p.returncode:
            audit.write(run / "reports/performance_gate.json", {"status": "BLOCKED", "full_execution_allowed": False,
                        "failed_configuration": setting["name"]})
            raise RuntimeError("Selected16 benchmark failed; inspect its preserved log")
    audit.finalize(run, c, study, before, start)


if __name__ == "__main__":
    main()
