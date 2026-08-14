# PHM project state

`context_version: 3.0.0`
`updated: 2026-08-14`
`Git baseline: d3ce4808abfa on main...origin/main; dirty (pre-existing modified .gitignore and untracked in-progress PHM foundation, documentation, scripts, source, and tests); no staged changes observed before this document.`

## Current objective and corrected formulation

The official challenge page, accessed 2026-08-14, supersedes the earlier missing-label assumption: participants derive an image-based damage trajectory from the 28 post-run tooth images, then later train a sensor-only estimator. The current task is end-of-run current-state estimation. Six hours is the typical run, inspection, and output cadence (with 1–3-hour exceptions), not automatically a forecast horizon. Verified experiment + run + tooth identity is the non-temporal association; image UTC remains unverified but is unnecessary for authoritative post-run membership.

T2.1–T2.3, frozen-encoder RT-DETR regression, R4 pseudo-box construction, a genuine detector, and a genuine multitask detector/scalar baseline are complete. The immediate gate is expert review of target version `phm2026_image_damage_v2` and its pseudo-boxes. PatchTST, sensor features, fusion, leaderboard work, and official test modelling have not begun.

## Completed work and primary evidence

- **T2.1:** provisional image target run `20260814T012054997053Z-e195f6d9` (1,311 images, 560 tooth observations, 20 run targets); see `T2_1_CHECKPOINT.md`.
- **T2.2:** manifests/splits run `20260814T013357354377Z-6b068cab` (995 image samples; EXP-B/A/F train/validation/test; zero leakage violations); see `T2_2_CHECKPOINT.md`.
- **T2.3:** naive baseline run `20260814T015914190145Z-4423f1fa`; see `T2_3_CHECKPOINT.md`.
- **R3 RT-DETR:** frozen-encoder provisional regression run `20260814T020338751021Z-d0f225c8` and professor result package `20260814T021150456003Z-d15163e7`; see `R3_RTDETR_CHECKPOINT.md`.
- **R4 pseudo-boxes:** 995 images / 30,628 connected-component pseudo-boxes in run `20260814T040854991567Z-3fa0f794`; see `R4_PSEUDO_BOX_CHECKPOINT.md`.
- **R4 genuine detector:** run `20260814T043751107678Z-7f1e13af`; execution valid but pseudo-box agreement effectively failed; see `R4_RTDETR_DETECTION_CHECKPOINT.md`.
- **R4 multitask RT-DETR:** run `20260814T050026535618Z-9b00f099`; professor package `20260814T051127631836Z-18a96ee3`; see `R4_RTDETR_MULTITASK_CHECKPOINT.md`.
- **F0.1–F0.3:** repository map, dataset-neutral contracts, PHM adapter,
  configuration validation, deterministic IDs/seeding, run manifests,
  provenance, and synthetic-fixture test infrastructure. See the
  [implementation map](PHM_IMPLEMENTATION_MAP.md) and
  [PHM configuration](../../configs/datasets/phm2026.yaml).
- **D1.1 inventory:** complete ZIP central-directory inventory run
  [`20260813T202043619114Z-ad7f9832`](../../runs/phm2026_dataset_description/20260813T202043619114Z-ad7f9832/reports/summary.md).
- **D1.2 sensors:** bounded representative metadata run
  [`20260813T212734652736Z-f7c665fd`](../../runs/phm2026_dataset_description/20260813T212734652736Z-f7c665fd/reports/sensor_summary.md);
  deterministic sampled-statistics companion
  `20260813T212817486478Z-f7c665fd`. See the
  [D1.2 checkpoint](D1_2_CHECKPOINT.md).
- **D1.3 images:** complete header run
  [`20260813T215718624432Z-bd9395ad`](../../runs/phm2026_dataset_description/20260813T215718624432Z-bd9395ad/reports/image_summary.md)
  and bounded sampled-quality run
  [`20260813T215756728445Z-bd9395ad`](../../runs/phm2026_dataset_description/20260813T215756728445Z-bd9395ad/reports/image_summary.md).
  See the [D1.3 checkpoint](D1_3_CHECKPOINT.md).
- **D1.4 alignment feasibility audit:** completed with status
  `PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN`; it created
  no image–sensor join, target, or sample. Read the
  [alignment report](../../runs/phm2026_dataset_description/20260813T223944047252Z-d6474ff4/reports/alignment_summary.md)
  and [blocker record](../../runs/phm2026_dataset_description/20260813T223944047252Z-d6474ff4/reports/alignment_blockers.json).
- **D1.5 professor dataset description:** generated from hash-pinned D1.1–D1.4
  artifacts in run
  [`20260813T225147672972Z-7d2070cf`](../../runs/phm2026_dataset_description/20260813T225147672972Z-7d2070cf/reports/professor_dataset_description.md).

The exact input run IDs and artifact hashes for downstream D1 work are pinned
in [`configs/experiments/phm2026_dataset_description.yaml`](../../configs/experiments/phm2026_dataset_description.yaml).
Never substitute “latest run.”

## Verified dataset findings

- Active scope is EXP-A Runs 1–5, EXP-B Runs 1–7, and EXP-F Runs 1–8.
  Run/lifecycle identity is not a health or damage label. EXP-A Run 2 stays in
  scope with its reported, unverified 311-file overlap warning.
- D1.1 found 52 readable ZIP archives, 8,512 central-directory members, and
  40 nested ZIP members; 13 warnings; no missing expected asset and no
  unreadable archive. Its 622 CRC32-plus-size candidate rows are not duplicate
  proof; zero exact central-directory metadata duplicate rows were found.
- D1.2 representative coverage inspected 745 HDF5 members / 27,165 datasets,
  all readable, with 13 file-schema variants and 12 exact shape families. It
  observed float32/float64/uint16 and evidenced rates from 0.25 Hz to about
  102,400 Hz. It retained 446 internal run-token conflicts as warnings.
- D1.3 covered all 1,311 image headers (EXP-A 455, EXP-B 576, EXP-F 280):
  1440 × 2560 × 3 RGB `uint8`, 8-bit JPEG. The 104-image quality subset found
  no exact SHA-256 group and 127 dHash candidate pairs; neither result is a
  dataset-wide semantic duplicate claim. No annotation sidecar was discovered
  in the bounded archive listing.
- D1.4 found 0 verified image UTC timestamps, 640 local-naive timezone-unknown
  filename timestamps, and 671 missing image timestamps. Sensor UTC evidence
  exists where explicitly recorded, but clocks are not comparable.
- R4 materialized only the frozen 995-image modelling set in one bounded cache and retained 30,628 mask-derived candidate boxes. All 995 images were positive under the heuristic. This is complete pseudo-label replay, not expert annotation.

## Evidence boundaries

| Status | What is supported | What it does not support |
|---|---|---|
| Complete | D1.1 ZIP central directories; D1.3 headers for 1,311 JPGs; R4 replay/cache/box validation for 995 model views | Full raw-payload integrity, expert labels, physical target validity |
| Representative | D1.2 EXP-A Run-1-oriented sensor structure across one selected source per sensor modality | Exhaustive schema/rate/channel coverage over all EXP-A/B/F archives |
| Sampled | D1.2 one-HF-member value statistics; D1.3 104 image pixel/quality/hash results | Whole-signal statistics or dataset-wide image quality/duplicates |
| Provisional | 560 tooth values, 20 run targets, 30,628 pseudo-boxes, and RT-DETR pseudo-label metrics | Organizer ground truth or physical-spall accuracy |
| Blocked/unknown | Expert mask/box validity, image UTC clock, compact all-run sensor features | Validated physical-spall claims, PatchTST, sensor-model or fusion claims |

## Scientific gates and blockers

1. Challenge target semantics, six-hour cadence and run-level pairing are resolved from the official source.
2. The implemented dark/horizontal candidate mask is a provisional pseudo-label; 560 tooth reviews are pending and A/B-versus-F imaging protocol bias is unresolved.
3. Exact image UTC remains unverified, but run-level post-inspection association uses verified experiment/run membership and does not need temporal coercion.
4. No verified spall boxes/classes exist. R4 detection metrics measure heuristic-mask agreement only. Model A had zero retained EXP-F detections at confidence 0.60; Model B had F1 0.002604 and mAP@0.50 0.000054 at confidence 0.01.
5. Compact minute sensor features were not fabricated or extracted; T2.2 records 7,124 one-minute sources and 20 run windows, and a later streaming job is required.
6. The multitask scalar head reached EXP-F view MAE 0.732990 pp (N=224), but raw run-top-3 MAE 1.627254 pp (N=8), worse than the frozen model's 1.347448 pp. Results remain engineering evidence only.

## Repository map

| Area | Canonical location and treatment |
|---|---|
| Immutable PHM input | `gtc-data-experiment/` — read-only archives; never extract in place or edit |
| Excluded Intel input | `data/Full Dataset/` — never scan from PHM work |
| PHM configuration | `configs/datasets/phm2026.yaml`; versioned `configs/experiments/phm2026_*.yaml` |
| Thin CLI scripts | `scripts/profile_dataset.py`, `profile_sensors.py`, `profile_images.py`, `audit_alignment.py`, `describe_dataset.py` |
| Reusable implementation | `src/pi_multimodal_ad/{data_contracts,datasets,profiling,targets,evaluation,models,utils}/` |
| Tests and safe data | `tests/unit/`; tiny synthetic-only `tests/fixtures/synthetic_multimodal/` |
| Generated evidence | ignored `runs/phm2026_*/<run-id>/` with manifests, reports, tables, figures, provenance; R4 canonical IDs are listed above |
| Protected historical study | `experiments/exp_a_initial_eda_r1_r3_r5/` — preserve unchanged, evidence/regression only |
| New study definition | `experiments/phm2026_dataset_description/` — commands and study guidance, not generated bulk |

## Hard prohibitions

- Never touch, rename, move, deduplicate, recompress, or modify PHM raw data.
- Never access the Intel data for PHM tasks.
- Never invent timestamps, organizer labels, physical masks, units, or clock conversions. Self-defined image pseudo-targets must be versioned and visibly provisional until human review.
- Never treat archive members as model samples; a sample needs an approved
  target, cutoff, source references, and grouping/split keys.
- Never create random, leakage-prone splits of nearby windows/images or split
  internally in a loader/trainer.
- Never modify `.gitignore` incidentally; preserve protected historical outputs
  and unrelated files.

## Reusable infrastructure to extend, not replace

- Target/evaluation/model code: `targets/`, `evaluation/`, and `models/` provide the v2 pseudo-target, pseudo-box construction, persisted splits, metrics/baselines, frozen regression, genuine detection evaluation, and a differentiable multitask wrapper.
- Contracts: `AssetRecord`, `ImageRecord`, `SensorRecord`, `TargetRecord`,
  `SampleRecord`, stable IDs, and validation in `data_contracts/`.
- Adapter boundary: `datasets/base.py` and PHM-only parsing/rules in
  `datasets/phm2026.py`.
- Safe profiling: central-directory inventory, one-at-a-time archive I/O,
  HDF5/sensor profiling, image profiling, clock-domain-gated alignment, and
  dataset-description generation in `profiling/`.
- Reproducibility: validated relative YAML loading, deterministic seeding,
  versioned non-overwriting runs, input/output manifests, and provenance in
  `utils/`.
- Tests exercise contracts, adapter rules, archive cleanup, profilers, pinned
  artifacts, alignment blocking, and deterministic report generation.

## Standard validation commands

Run focused checks for files changed; do not launch expensive PHM scans or a
full payload mode without explicit authorization.

```bash
ma_thesis_env/bin/python -B -m pytest -q tests/unit/test_<affected_area>.py
ma_thesis_env/bin/python -B -m black --check src/pi_multimodal_ad scripts tests
ma_thesis_env/bin/python -B -m py_compile <changed_python_files>
ma_thesis_env/bin/python -B -m pip check
git diff --check
git status --short --branch --untracked-files=all
```

Use the script `--dry-run` before a PHM command; require exact pinned artifact
hashes when a downstream task consumes D1 outputs.

## Update protocol

After each completed authorized task, update this file in the same change:
record task status, generated run ID(s), primary report links, coverage level,
new/removed blockers, validation evidence, and the next gate. Keep it concise;
link machine-readable tables and detailed reports rather than duplicating them.
Do not mark a blocked scientific decision as complete.
