# GPU audit — 26 October 2026

This folder contains a bounded performance audit for the existing REASSEMBLE
16-action-frame, final-stage CNN adaptation protocol. It does not restart an old
study or launch a multi-fold or multi-seed experiment.

Run from the repository root:

```bash
bash 26.10.2026_feedback_experiments/source/run_audit.sh
```

Each invocation creates a unique UTC-stamped `runs/<id>/` directory containing
configuration, hardware, input/output manifests, timing tables, GPU telemetry,
numerical checks, disposable checkpoints, warnings and provenance. Generated
bulk and run directories are ignored by the folder-local `.gitignore`.

The benchmark imports the existing model and standardizer without calling the
historical training or cache writers. It decodes only a deterministic 24-action
subset of the first outer fold's gradient-training partition. Every regenerated
32-frame input must match its saved uncompressed pixel SHA256 before its exact
16-frame subset is used. Calibration and assessment outcomes are not used.

All three configurations retain float32, one action per forward pass, 16 frames
batched together, eight actions per optimizer update, original positive weighting,
normalization, optimizer, learning rates, clipping, dropout and deterministic
settings. Loader RNG is separate from model RNG. The optimized configurations
use two or four single-thread loader workers, pinned memory, persistent workers
and prefetching. Each configuration has two measured 60-second windows after
warmup. Initialization, correctness checks and checkpoint writes are excluded.

The bounded subset repeats for sustained timing. Reported epoch times are
extrapolations, not complete measured epochs. Cold decoding and cache-generation
costs are recorded separately. See `PHASE1_GPU_OPTIMIZATION_REPORT.md` for the
measured comparison, limits and gate decision.

Validation:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 ma_thesis_env/bin/python -B -m pytest 26.10.2026_feedback_experiments/tests -q --import-mode=importlib -p no:cacheprovider
ma_thesis_env/bin/python -B -m pip check
git diff --check
```

The performance options follow the official [PyTorch performance guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html).
Options that change the fixed scientific protocol require a separate documented
decision and numerical validation. The audit runner always keeps full execution
disabled.

To benchmark the optimized live decoder after the first audit finishes, use its
new run path:

```bash
CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 ma_thesis_env/bin/python -B 26.10.2026_feedback_experiments/source/selected16_audit.py run --parent-run 26.10.2026_feedback_experiments/runs/<warm-run-id>
```

This audit creates another unique run and uses the same training actions. It
decodes only the 16 consumed frames with two FFmpeg threads per active video,
asserts their exact pixel identities against verified 32-frame parents, and
creates no persistent pixels. Cooperative exhaustion drains prefetch queues and
releases video handles before worker shutdown; all worker exit codes must be
zero. The inherited `decompress_s` field means decoding plus preprocessing,
recorded explicitly in configuration. Short CPU/CUDA operator traces run outside
sustained timing windows. `trace_summary.py <run>` summarizes actual CUPTI kernels
without adding overlapping operator/range totals.

`streaming_audit.py` retains the 32-frame diagnostic path used to discover worker
teardown failures. It requires `--allow-diagnostic-shutdown-repro` and is excluded
from the selected configuration. Interrupted and failed runs remain preserved.
