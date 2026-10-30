# Frozen original-architecture replication: measured status

Snapshot: 2026-10-30T16:35:34.542553+00:00. Run `20261029T004900Z`. Read the
[research priority correction](PRIMARY_REPLICATION_PRIORITY.md) first.

The completed frozen branch does **not** currently show a pooled F2 advantage
over the original sensor Logistic Regression. F2 exceeds frozen vision and
has higher pooled macro AP than averaging for each seed, while falling below
original LR for each seed. This is a partial clean-data result; full CNN
fine-tuning and missing/degraded-modality evaluation remain pending.

## Within-ViFailback results first

Each seed covers the same 4,382 held-out episodes exactly once across three
task-disjoint outer folds: 3,753 failures and 629 no-failures (failure prevalence
0.856458, no-failure prevalence 0.143542). The three seeds are repeated
fits on those episodes, not 13,146 independent examples. Pooled AP uses all
outer predictions within a seed; it is not an average of fold APs.

| Model | Seed | AP failure | AP success | Macro AP | AUROC |
|---|---:|---:|---:|---:|---:|
| Original frozen CNN | 42 | 0.853052 | 0.137260 | 0.495156 | 0.479402 |
| Original sensor LR | 42 | 0.954370 | 0.343577 | 0.648974 | 0.784370 |
| Simple averaging | 42 | 0.931760 | 0.289037 | 0.610399 | 0.716501 |
| Original F2 | 42 | 0.945168 | 0.312405 | 0.628787 | 0.752701 |
| Original frozen CNN | 123 | 0.845749 | 0.146991 | 0.496370 | 0.475157 |
| Original sensor LR | 123 | 0.954370 | 0.343577 | 0.648974 | 0.784370 |
| Simple averaging | 123 | 0.933227 | 0.317011 | 0.625119 | 0.731510 |
| Original F2 | 123 | 0.943543 | 0.307257 | 0.625400 | 0.746198 |
| Original frozen CNN | 20261023 | 0.839708 | 0.129067 | 0.484387 | 0.463408 |
| Original sensor LR | 20261023 | 0.954370 | 0.343577 | 0.648974 | 0.784370 |
| Simple averaging | 20261023 | 0.931124 | 0.307745 | 0.619435 | 0.726439 |
| Original F2 | 20261023 | 0.940587 | 0.301547 | 0.621067 | 0.733723 |

| Paired pooled difference | Seed 42 | Seed 123 | Seed 20261023 | Mean across seeds |
|---|---:|---:|---:|---:|
| Original F2 minus Original frozen CNN | +0.133630 | +0.129030 | +0.136680 | +0.133114 |
| Original F2 minus Original sensor LR | -0.020187 | -0.023574 | -0.027907 | -0.023889 |
| Original F2 minus Simple averaging | +0.018388 | +0.000281 | +0.001633 | +0.006767 |
| Simple averaging minus Original sensor LR | -0.038575 | -0.023855 | -0.029539 | -0.030657 |
| Simple averaging minus Original frozen CNN | +0.115242 | +0.128749 | +0.135047 | +0.126346 |

Differences above are absolute macro-AP differences on the 0–1 scale. They
are descriptive; this check does not add bootstrap intervals or establish
statistical significance. The frozen protocol already specifies paired
2,000-resample task-cluster intervals for final reporting. For success-class
AP, F2 minus averaging is positive for seed 42 but negative for seeds 123 and
20261023; a macro-AP improvement must not conceal that difference. Original
LR is deterministic here: its seed tables are identical, not independent
replications of sensor uncertainty.

## All folds retained

| Seed | Outer fold | Episodes | V1 macro AP | Original LR macro AP | Averaging macro AP | F2 macro AP | F2 minus LR |
|---|---:|---:|---:|---:|---:|---:|---:|
| 42 | 0 | 1107 | 0.475731 | 0.707996 | 0.698790 | 0.708218 | +0.000222 |
| 42 | 1 | 1586 | 0.519561 | 0.731945 | 0.726733 | 0.732536 | +0.000591 |
| 42 | 2 | 1689 | 0.519034 | 0.641544 | 0.628145 | 0.641724 | +0.000180 |
| 123 | 0 | 1107 | 0.467893 | 0.707996 | 0.691518 | 0.707284 | -0.000713 |
| 123 | 1 | 1586 | 0.537031 | 0.731945 | 0.732213 | 0.734602 | +0.002657 |
| 123 | 2 | 1689 | 0.503849 | 0.641544 | 0.635750 | 0.641480 | -0.000064 |
| 20261023 | 0 | 1107 | 0.472839 | 0.707996 | 0.693085 | 0.696864 | -0.011132 |
| 20261023 | 1 | 1586 | 0.518977 | 0.731945 | 0.729053 | 0.732512 | +0.000567 |
| 20261023 | 2 | 1689 | 0.492981 | 0.641544 | 0.626422 | 0.642821 | +0.001277 |

Read both these fold results and the pooled results: scores produced by
different outer fits have separate calibrators, so cross-fold ranking can
differ from within-fold ranking. Do not choose pooling, a fold or calibration
after seeing which comparison is favorable. The full class-wise fold APs,
AUROC, input hashes and selected-epoch receipts are in
[the finalized check receipt](SAVED_FROZEN_RESULTS_RECHECK.json). Threshold and
calibration metrics remain in the unchanged per-fit `metrics.json` artifacts
and published reports; they were not independently recomputed by this check.

## What was checked

- All nine V1 outer prediction tables and matched original-LR/F1/F2 tables
  have completion receipts and matching SHA-256 values; episode IDs and native
  targets match the frozen manifest and assessment partitions.
- All 27 inner V1/LR prediction tables match their saved hashes and join
  exactly to the F2 meta-training records. Every inner assessment task is
  excluded from its own T/V/C partitions; meta-training episodes exclude the
  complete outer assessment task set.
- AP for each class, macro AP and AUROC were recomputed with sklearn, separately
  from the project reporting helper; all four saved fold metrics agree within
  1e-12. Pooled seed metrics and paired differences were computed from the
  saved predictions. This reuses the same sklearn metric definitions and is
  a consistency check, not an independent statistical reimplementation.
- F1 predictions were reconstructed as the exact float32 probability mean.
  F2 predictions were reconstructed from its saved probability-logistic
  coefficients, with no coefficient refitting. The original C=1/unweighted
  metadata were checked. Actual source sensor/stacker code was inspected.
- All 36 V1 completion receipts record 100 executed epochs, with each selected
  epoch retained separately. This check did not reload checkpoint payloads or
  independently recount every history; it verifies schedule receipts.
- All 31 frozen implementation/configuration files, five reused source files,
  the cohort/split manifests and 13 hash-protected report publications still
  match their preserved identities. Controller PID and creation time match
  its original receipt. No fitting, training, signal or restart occurred.

The first check receipt is also preserved as `SAVED_FROZEN_RESULTS_CHECK.json`.
The finalized repeat adds the check-script source hash and explicit command
to `SAVED_FROZEN_RESULTS_RECHECK.json`. Both runs gave the same metric values.

Reproduce from repository root, using a new output filename:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 ma_thesis_env/bin/python -B \
  VIFAILBACK/10_final_research_reports/researcher_handoff/20261030_RESEARCH_PRIORITY_CORRECTION/check_saved_frozen_results.py \
  --output /tmp/vifailback_frozen_replication_check_new.json
```

The check refuses to overwrite an existing output. It reads the frozen run
and current publication receipts; it does not invoke training or publishing.

## Current queue and incomplete comparisons

At the check, the original controller PID was 290646 with its original creation time and no active child.
The live stage is `WAITING_REASSEMBLE75_COMPLETE_AND_GPU_IDLE`. Completed
stages include both initial feature banks, 36 V1 fits, 36 supplementary
high-camera-only fits, the sensor baselines and the frozen fusion fits.
The source REASSEMBLE status at 2026-10-30T16:29:35Z recorded 10/75 fits
complete in its separate 20-epoch study. That study is distinct from the
required ViFailback 100-epoch full-CNN schedules. No GPU job was interrupted.
Use the live status files rather than this dated snapshot for later progress.

V2 full CNN100, V3 supplementary donor adaptation, final saved-result
verification and the locked robustness scenarios remain pending. HGB is
already complete and preserved in the sensor-baseline artifacts and
`06a_COMPLETED_CPU_SENSOR_BASELINES.md`; it has not replaced original LR in F2.
No additional HGB work was launched for this correction.

## Cross-dataset interpretation remains open

These ViFailback differences do not yet establish comparable F2 benefits
between datasets. A complete source comparison must identify its own saved
predictions and within-REASSEMBLE deltas, then discuss target prevalence,
grouping, visibility, calibration and budget differences. A validated donor
checkpoint demonstrates checkpoint lineage, not matched cross-dataset fusion
benefits. The ongoing source study must finish without interference. No
cross-dataset superiority, equivalence or robustness claim is made here.
