"""Measure uncached exact video decoding with the same validated audit loop.

No persistent pixel cache is generated. An isolated read-only decoder reproduces
the saved pixel identities. Decoder timings occupy the shared
`decompress_s` field; each run explicitly records that interpretation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import resource
from pathlib import Path
import shlex
import subprocess
import sys
import time
import uuid

import numpy as np
import torch

import gpu_audit as audit
from isolated_decode import IsolatedDecoder


class StreamingDataset(audit.PixelDataset):
    def __init__(self, run, repeats=1):
        super().__init__(run, repeats)
        self.decoder = None

    def __getitem__(self, index):
        if self.decoder is None:
            c = audit.read(self.root / "config/resolved_config.json")
            original = audit.read(audit.REPO / c["study_root"] / "config/resolved_config.json")
            self.decoder = IsolatedDecoder(audit.REPO, original["weights_dir"], original["rescale_factor"])

        row = self.rows[index % len(self.rows)]
        start = time.perf_counter()
        u = self.decoder(row)
        decoded = time.perf_counter()
        assert hashlib.sha256(u.tobytes()).hexdigest() == row["pixel_content_sha256"]
        hashed = time.perf_counter()
        x = torch.from_numpy(u[row["positions16_in32"]].astype("float32") * np.float32(1 / 255))
        return x, torch.tensor([row["failure"]], dtype=torch.float32), {
            "read_s": 0.0, "decompress_s": decoded - start,
            "hash_s": hashed - decoded, "preprocess_s": time.perf_counter() - hashed,
        }


def main():
    # Disposable child failures must not generate large core dumps.
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["run", "worker"])
    parser.add_argument("--parent-run", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--allow-diagnostic-shutdown-repro", action="store_true")
    args = parser.parse_args()
    if args.mode == "worker":
        if args.run is None or not args.run.resolve().is_relative_to(audit.BASE / "runs"):
            parser.error("Worker requires a new audit run")
        audit.PixelDataset = StreamingDataset
        audit.benchmark(args.run.resolve(), args.name)
        from profile_pipeline import profile_pipeline
        profile_pipeline(args.run.resolve(), args.name)
        return
    if not args.allow_diagnostic_shutdown_repro:
        parser.error("Known diagnostic worker-shutdown defect; use selected16_audit.py for the corrected candidate, or explicitly request diagnostic reproduction")
    if args.parent_run is None or not args.parent_run.resolve().is_relative_to(audit.BASE / "runs"):
        parser.error("A completed parent run in the audit folder is required")
    parent = args.parent_run.resolve()
    assert audit.read(parent / "reports/performance_gate.json")["at_least_two_configs"]
    c = audit.read(parent / "config/resolved_config.json")
    c["input_mode"] = "streaming_exact_decode_without_compression_or_persistent_pixels"
    c["decoder_threads_per_open_video"] = 1
    c["stability_revision"] = "ffmpeg_thread_bound_and_explicit_loader_shutdown_v2"
    c["timing_field_interpretation"] = {"decompress_s": "video_decode_and_original_processor_seconds"}
    for s in c["configurations"]:
        s["name"] = "stream_" + s["name"]
    audit.validate_config(c)
    run = audit.BASE / "runs" / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-stream-" + uuid.uuid4().hex[:8])
    run.mkdir(exist_ok=False)
    start = time.monotonic()
    audit.write(run / "config/resolved_config.json", c)
    for name in ("manifests/job.json", "manifests/selected_training.json", "manifests/inputs.json", "reports/hardware.json"):
        audit.write(run / name, audit.read(parent / name))
    audit.write(run / "provenance.json", {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "command": shlex.join(sys.argv), "git_commit": audit.command(["git", "rev-parse", "HEAD"]),
        "git_status": audit.command(["git", "status", "--short", "--untracked-files=all"]),
        "parent_run": str(parent.relative_to(audit.REPO)),
        "source_identities": {p.name: audit.digest(p) for p in (
            Path(__file__), Path(audit.__file__), Path(__file__).with_name("isolated_decode.py"),
            Path(__file__).with_name("profile_pipeline.py"))},
        "configuration_source": str((parent / "config/resolved_config.json").relative_to(audit.REPO)),
        "methodology": "same deterministic training subset and loop, exact live decoding; no persistent pixels",
        "io_limitation": "Encoded videos are OS-page-cache affected; not cold physical storage"})
    study = audit.REPO / c["study_root"]
    before = audit.preserved_files(study)
    audit.write(run / "manifests/historical_before.json", before)
    print("STREAM_RUN", str(run.relative_to(audit.REPO)), flush=True)
    for setting in c["configurations"]:
        cmd = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", "--run", str(run), "--name", setting["name"]]
        with (run / (setting["name"] + ".log")).open("x") as log:
            p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
        print(setting["name"], "exit", p.returncode, flush=True)
        if p.returncode:
            audit.write(run / "reports/performance_gate.json", {"status": "BLOCKED", "failed_configuration": setting["name"], "full_execution_allowed": False})
            raise RuntimeError("Streaming benchmark failed; inspect its new log")
    audit.finalize(run, c, study, before, start)


if __name__ == "__main__":
    main()
