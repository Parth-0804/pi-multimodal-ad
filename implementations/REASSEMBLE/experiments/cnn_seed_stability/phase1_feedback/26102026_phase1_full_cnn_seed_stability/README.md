# 26 October 2026 — Phase 1 full CNN and seed stability

This is the independently versioned experiment authorized by the supplied
Phase 1 master prompt. The earlier report-only hold was superseded by that
explicit execution request. Historical results, raw datasets, the earlier GPU
audit and unrelated working-tree edits are preserved.

The measured full-CNN pilot runs at about 1.925 actions/s and 94% GPU kernel-busy
utilization. The full 150-fit matrix is planned at approximately **25–58 days**
on the single allocated T4, with exclusive availability. This is an estimate;
completion is indicated only by `PHASE1_ALL_COMPLETE.json` and the final metrics.

## Reports and fixed inputs

- [Historical audit](26102026_reports/PHASE1_HISTORICAL_AUDIT.md)
- [Frozen protocol](26102026_reports/PHASE1_EXPERIMENT_PROTOCOL.md)
- [GPU integration and measured full-CNN pilot](26102026_reports/PHASE1_GPU_INTEGRATION.md)
- [Training results and learning-curve diagnostics](26102026_reports/PHASE1_TRAINING_RESULTS.md)
- [Fusion results](26102026_reports/PHASE1_FUSION_RESULTS.md)
- [Live executive review](26102026_reports/PHASE1_EXECUTIVE_REVIEW.md)
- [Supplementary short-reference interpretation](26102026_reports/PHASE1_INTERPRETATION_LIMITATIONS.md)
- [Configuration](26102026_configuration/PHASE1_CONFIG.json)
- [Recording-disjoint fit plan](26102026_evidence/PHASE1_FIT_PLAN.json)
- [Full-cohort input verification](26102026_evidence/PHASE1_INPUT_VERIFICATION_STATUS.json)
- [Full-backbone numerical/performance gate](26102026_evidence/PHASE1_FULL_CNN_GATE.json)

Result reports stay partial until all required fits and held-out analyses
finish. Historical AP values are context, never substituted for missing results.
The primary comparison is long frozen B versus full-CNN C. A is immutable
historical context; A_r is a separately identified short-horizon reconstruction.

## Live execution and recovery

Ignored execution artifacts live in
`26102026_execution/26102026_main_run_01/`. Key files are:

- `PHASE1_CONTROLLER_STATUS.json`: active child, stage, estimated remaining time,
  host resources and controller PID, refreshed about every 30 seconds.
- `PHASE1_PROGRESS.json`: current arm/seed/fold/epoch and incomplete-epoch action
  count, refreshed every 25 optimizer updates. It can lag during validation.
- `PHASE1_COMPLETED_FIT_INDEX.json`: completed B/C fit coverage.
- `PHASE1_PROCESS_ATTEMPTS.json`: child logs, wall-time accounting and retries.
- `26102026_logs/`: controller and fit logs.
- Per-fit folders: selected weights, two alternating complete-epoch recovery
  generations, keyed held-out probabilities, calibrators, all learning-curve
  JSON and PNG files, GPU telemetry, host resources and worker-shutdown checks.

The controller uses a single-writer lock and starts one GPU child at a time.
If another GPU process is present it waits; if one appears during training the
fit rolls back the incomplete epoch and waits before retrying. Another prompt
can still consume CPU, RAM or disk. Keep active source, configuration, input
manifests and shared reference caches unchanged. Source/input drift requests a
stop at the completed boundary. Unrelated reports can be edited separately.

The implementation resumes complete-epoch boundaries, including model,
optimizer, scheduler, RNG, exact order, selected weights and history. A crash
after an uncommitted best-model replacement restores the earlier committed
selection. An interrupted epoch is replayed, never silently counted as an
extra completed scientific epoch. Selected weights and resumable generations
are retained within the new run; historical checkpoints are never pruned.

To resume after a controller/host interruption, use the same environment and
command from the repository root. The single-writer lock prevents duplicate
controllers. Resume is automatic for already completed fits/epochs, but process
restart after a host reboot is manual; no system service was installed.

```bash
env PYTHONDONTWRITEBYTECODE=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 \
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
  ma_thesis_env/bin/python -B \
  26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_controller.py
```

A new `STOP_AFTER_EPOCH.json` in this study root requests a stop after saving a
complete epoch. The runner never creates such a request for elapsed GPU hours;
it can create one if frozen source/input identity changes. Numerical errors,
insufficient disk and integrity failures stop the affected work with explicit
evidence. No Phase 2/3 experiments, commit, push or raw-data mutation occurs.

## Validation

The new synthetic regressions and reused audit suite pass 26 tests. Full-cohort
identity and real-CNN gradient/update/reload/epoch-replay gates are separate
measured checks. The source snapshot, configuration, pretrained identity,
software versions and Git working-tree provenance are frozen before controlled
training. See `26102026_evidence/PHASE1_SOFTWARE_VALIDATION.json` for commands.

## Active scope amendment — C only,20 epochs

The user superseded the earlier B/C25–50 schedule with [Model C only,20 epochs](26102026_c_only_20epoch_revision_01/README.md). The current CNN resumed from completed epoch9. Pending B fits are removed; original configurations and prior results remain preserved. Use the linked revision for current status and reports.
