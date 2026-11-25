"""Summarize actual CUPTI kernels without double-counting operator/range totals."""
import argparse
import json
from pathlib import Path

import gpu_audit as audit


def union_microseconds(events):
    intervals = sorted((e["ts"], e["ts"] + e["dur"]) for e in events if e.get("dur", 0) > 0)
    if not intervals:
        return 0.0
    start, end = intervals[0]
    total = 0.0
    for a, b in intervals[1:]:
        if a > end:
            total += end - start
            start, end = a, b
        else:
            end = max(end, b)
    return total + end - start


def summarize(path):
    events = json.loads(path.read_text())["traceEvents"]
    kernels = [e for e in events if e.get("cat") == "kernel"]
    copies = [e for e in events if e.get("cat") == "gpu_memcpy"]
    wall = next(e["dur"] for e in events if e.get("name") == "eight_action_training_update" and e.get("cat") == "user_annotation")
    return {
        "trace": str(path.relative_to(audit.REPO)),
        "kernel_events": len(kernels), "kernel_union_ms": union_microseconds(kernels) / 1000,
        "kernel_sum_ms": sum(e.get("dur", 0) for e in kernels) / 1000,
        "memcpy_events": len(copies), "memcpy_union_ms": union_microseconds(copies) / 1000,
        "profiled_eight_action_wall_ms": wall / 1000,
        "kernel_busy_wall_percent": 100 * union_microseconds(kernels) / wall,
        "input_wait_ms": sum(e.get("dur", 0) for e in events if e.get("name") == "input_load_wait") / 1000,
        "cuda_stream_sync_cpu_ms": sum(e.get("dur", 0) for e in events if e.get("name") == "cudaStreamSynchronize") / 1000,
        "caveat": "One instrumented update; profile overhead and CUDA synchronization affect timing. Sustained nvidia-smi and actions/s remain the comparison metrics. Operator/range device totals must not be summed as kernel time.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    if not run.is_relative_to(audit.BASE / "runs"):
        parser.error("Run must belong to this audit")
    rows = [summarize(p) for p in sorted((run / "logs").glob("*_operator_trace.json"))]
    assert rows and all(r["kernel_events"] > 0 for r in rows)
    audit.write(run / "tables/kernel_trace_summary.json", rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
