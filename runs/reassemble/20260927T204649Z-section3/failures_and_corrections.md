# Section 3 execution log of corrections

Initial serial extractors were interrupted with SIGINT to improve runtime after
measured GPU utilization of 39% exposed CPU/decoding bottlenecks. All completed
recording NPZ/JSON pairs passed SHA256 checks; no completed output was changed.
The initial logs remain visual_execution.log and sensor_execution.log, including
expected KeyboardInterrupt traces.

Runtime-only correction: three independent visual workers (same 16-frame batches,
2 CPU threads each), four sensor workers, nonblocking exclusive per-recording
file locks. Exact corruption seeds, formulas, models and parity guards unchanged.
No robustness outcomes had been computed or inspected.
