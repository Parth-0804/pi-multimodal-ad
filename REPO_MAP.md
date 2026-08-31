# Repository Map

A one-page index: what each top-level directory is for, whether it's active
or historical/protected, and where to go next. For governance rules (what
you're allowed to touch), see [`AGENTS.md`](AGENTS.md) — this file is just
navigation.

## Top-level directories

| Directory | What it is | Status |
|---|---|---|
| `src/pi_multimodal_ad/` | The installable package: data contracts, dataset adapters, feature extraction, models (PatchTST, RT-DETR variants), evaluation, profiling, reporting, provenance/run utilities. | **Active** — this is the real codebase. |
| `scripts/` | Thin CLI entry points that call into `src/pi_multimodal_ad/`, organized by pipeline stage (see below). | **Active** |
| `configs/` | `datasets/` (data source + scope definitions) and `experiments/` (one YAML per experiment, referenced by the matching `scripts/` entry point). | **Active** |
| `tests/unit/` | Unit tests for the package; `tests/fixtures/synthetic_multimodal/` holds tiny synthetic fixtures (never real data). | **Active** |
| `runs/` | Every pipeline run's output, in versioned, timestamped, non-overwriting directories (`runs/<experiment>/<timestamp>-<hash>/{config,manifests,figures,reports}`). | **Active, append-only.** Never edited or overwritten — new runs, not corrections. |
| `experiments/` | Experiment definitions and a few historical/exploratory studies. | Mixed — see below. |
| `tutorials/` | Self-contained educational/analysis material: the RT-DETR storybook tutorial, the supplementary RT-DETR causal-analysis baseline, the supplementary PatchTST frequency-domain baseline, and built presentation decks. Exempt from the governed run-provenance rules above, but self-labels its own provisional/supplementary status throughout. | **Active**, but explicitly supplementary — not the governed pipeline. |
| `docs/` | Policy docs (`active_scope.md`, `data_boundaries.md`, `output_policy.md`) plus `docs/planning/` — dated checkpoint reports for each implementation task (T2, D1, R3, R4, P4, ...). | **Active reference / historical record.** Checkpoint docs are point-in-time and are not rewritten after the fact. |
| `presentation_assets/` | Generated figures for dated presentation decks (one subfolder per presentation date), produced by `scripts/presentation/generate_professor_presentation.py`. | Generated output, kept for history. |
| `archive/` | Explicitly retired code/config/docs from superseded research directions, per the policy in `archive/README.md`. Currently holds `legacy_intel_welding_dataset/` (see root README). | **Historical, protected.** Never presented as part of the active pipeline. |
| `data/` | A placeholder (`DO_NOT_COMMIT_DATA_HERE.txt`) left over from the pre-pivot project phase. Real PHM2026 raw data lives outside this repository entirely. | Legacy placeholder, harmless. |
| `notebooks/` | *(removed — was a single placeholder notebook with no real content; moved to `archive/legacy_intel_welding_dataset/`.)* | n/a |
| `download.py` (root) | Historical EXP-B high-frequency archive downloader. | Historical — not a current pipeline entry point; left as-is per prior audit. |

## `scripts/` — organized by pipeline stage

```
scripts/
├── dataset/       profiling and description: describe_dataset.py, profile_dataset.py,
│                  profile_images.py, profile_sensors.py, audit_alignment.py,
│                  generate_dataset_evidence.py
├── targets/       provisional target construction: derive_image_targets.py,
│                  audit_target.py, build_rtdetr_pseudo_boxes.py
├── features/      model-ready dataset assembly: build_sensor_features.py,
│                  build_model_dataset.py
├── training/      train_patchtst.py, train_rtdetr_detector.py,
│                  train_rtdetr_regression.py, train_rtdetr_multitask.py,
│                  run_rtdetr_feasibility.py
├── results/       generate_patchtst_results.py, generate_rtdetr_results.py,
│                  generate_rtdetr_r4_results.py, evaluate_naive_baselines.py
├── presentation/  generate_professor_presentation.py
└── ops/           check_disk_space.py
```

Each script under `scripts/<stage>/` is the thin CLI wrapper for the
matching logic in `src/pi_multimodal_ad/`; run it from the repo root exactly
as it appears above (e.g. `scripts/training/train_patchtst.py`, not just
`train_patchtst.py`).

## `runs/` — what's in there

14 experiment families, each a growing set of timestamped run directories.
To find the most recent run for an experiment: sort its subdirectories by
timestamp (the directory name's leading `YYYYMMDDThhmmss...` prefix) and
take the latest. Every run directory has the same shape:
`config/`, `manifests/`, `reports/` (Markdown + JSON summaries), and
`figures/`.

| Experiment | What it produces |
|---|---|
| `phm2026_dataset_description` | Archive inventory, sensor/image structural profiling. |
| `phm2026_target_audit` | Target-formulation candidate audit (pre-decision). |
| `phm2026_image_target` | The provisional `phm2026_image_damage_v2` pseudo-label. |
| `phm2026_model_dataset` | Assembled, leakage-checked train/val/test sample contract. |
| `phm2026_sensor_features` | Per-minute sensor feature tables (governed, 72-feature schema). |
| `phm2026_rtdetr_pseudo_boxes` | The heuristic pseudo-box dataset RT-DETR trains on. |
| `phm2026_rtdetr_regression`, `_detection`, `_multitask`, `_r4_results` | RT-DETR variants (R3 frozen-encoder, R4 genuine detector, R4 multitask) and their evaluation reports. |
| `phm2026_patchtst_baseline`, `_patchtst_results` | The governed PatchTST baseline and its evaluation report. |
| `phm2026_evaluation` | Cross-cutting evaluation contract / real-world validity checklist. |
| `phm2026_rtdetr_results` | The consolidated RT-DETR engineering report. |

For narrative write-ups (not raw run output), see `docs/planning/` below.

## `docs/planning/` — checkpoint reports, roughly in build order

`T2_TARGET_FORMULATION_DECISION` → `T2_1/2/3_CHECKPOINT` (target + dataset
build) → `D1_2/3_CHECKPOINT` (sensor/image profiling) →
`R3_RTDETR_CHECKPOINT` (frozen-encoder baseline) →
`R4_PSEUDO_BOX_CHECKPOINT`, `R4_RTDETR_DETECTION_CHECKPOINT`,
`R4_RTDETR_MULTITASK_CHECKPOINT`, `R4_PRETRAINING_TRACEABILITY_CHECKPOINT`
(genuine detector + multitask variants) → `P4_PATCHTST_BASELINE_CHECKPOINT`
(sensor baseline). `PROJECT_STATE.md` is the running summary;
`PHM_IMPLEMENTATION_MAP.md` and `PHM_CODEX_IMPLEMENTATION_BACKLOG.md` are
broader planning references.

## `tutorials/` — supplementary, self-labeled material

```
tutorials/
├── rtdetr_storybook/        Educational walkthrough of RT-DETR's backbone/
│                            encoder/decoder stages on real photos, for
│                            people new to the architecture.
├── final_baseline_rtdetr/   Supplementary causal analysis of why the
│                            governed RT-DETR baseline scores near zero
│                            (box-scale mismatch, activation heatmaps).
├── patchtst_freq_baseline/  Supplementary from-scratch PatchTST variant
│                            using raw frequency-domain features (MAE 1.220,
│                            distinct from the governed baseline's 1.011 —
│                            do not conflate the two).
└── presentations/           Built .pptx decks presenting both baselines.
```

Each subfolder's own `REPORT.md`/`CHECKPOINT.md` states its provisional
status explicitly — none of this is organizer ground truth.

## Historical / do-not-modify

- `experiments/exp_a_initial_eda_r1_r3_r5/` — preserved until a validated
  replacement reproduces it and the researcher approves migration.
- `runs/**` — append-only; never edit or overwrite a past run.
- `archive/**` — retired by design; see `archive/README.md`.
- Raw data (`gtc-data-experiment/**`, `data/Full Dataset/**`) — immutable,
  and not part of this repository's tracked contents at all.
