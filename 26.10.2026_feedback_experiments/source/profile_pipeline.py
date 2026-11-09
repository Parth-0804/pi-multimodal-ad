"""Short CPU/CUDA operator trace, deliberately outside throughput windows."""
from pathlib import Path

import torch

import gpu_audit as audit


def profile_pipeline(run, name):
    c = audit.read(run / "config/resolved_config.json")
    setting = next(s for s in c["configurations"] if s["name"] == name)
    study = audit.REPO / c["study_root"]
    job = audit.read(run / "manifests/job.json")
    cohort = audit.read(study / "data_manifests/cohort_and_frames.json")
    positives = sum(cohort[i]["failure"] for i in job["G"])
    weight = torch.tensor((len(job["G"]) - positives) / positives, device="cuda")
    model, opt, _ = audit.create_model(study, job)
    data_loader = audit.loader(run, setting)

    class TraceIterator:
        def __init__(self):
            self.iterator = iter(data_loader)

        def __next__(self):
            with torch.profiler.record_function("input_load_wait"):
                return next(self.iterator)

    iterator = TraceIterator()
    audit.take_update(model, opt, iterator, setting, weight)
    torch.cuda.synchronize()
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
                                           torch.profiler.ProfilerActivity.CUDA]) as prof:
        with torch.profiler.record_function("eight_action_training_update"):
            audit.take_update(model, opt, iterator, setting, weight)
            torch.cuda.synchronize()
    trace = run / "logs" / (name + "_operator_trace.json")
    prof.export_chrome_trace(str(trace))
    operators = [{"name": e.key, "calls": e.count,
                  "self_cpu_ms": e.self_cpu_time_total / 1000,
                  "self_device_ms": e.self_device_time_total / 1000}
                 for e in prof.key_averages()]
    audit.write(run / "tables" / (name + "_operators.json"), {
        "scope": "One warmed disposable eight-action update, excluded from all throughput windows",
        "self_cpu_ms": sum(e["self_cpu_ms"] for e in operators),
        "self_device_ms": sum(e["self_device_ms"] for e in operators),
        "operators": operators,
        "cuda_trace_caveat": "CUDA kernels need CUPTI access; inspect device event count before relying on GPU operator times",
        "trace": str(trace.relative_to(run)), "disposable_optimizer_updates": 2})
    if data_loader._iterator is not None:
        data_loader._iterator._shutdown_workers()
