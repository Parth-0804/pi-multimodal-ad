# Dataset storage breakdown

Audit `20261028T114917Z` · 2026-10-28T12:49:17+01:00. Read-only assessment; no cleanup or downloads. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

| Dataset/evidence root | Allocated | Role and dependency | Retention |
| --- | --- | --- | --- |
| data/Full Dataset | 26.877 GB (25.031 GiB) | Intel Welding authoritative raw data; foundation audit NO-GO does not make raw inputs disposable | RED immutable |
| MILLING DATASET/data/raw/msm/versions/2 | 3.732 GB (3.476 GiB) | MSM native labels, videos, machine measurements and audio; source for final MSM evaluation | RED authoritative |
| MILLING DATASET (whole) | 4.359 GB (4.059 GiB) | Includes the above raw root, hard-linked staging and protected Stage 1–5/visual-review evidence | Parent total: do not add to raw subtotal |
| MSM (whole) | 1.434 GB (1.336 GiB) | Completed grouped evaluation; raw symlink target not recounted | Preserve predictions/models/splits; feature arrays conditional |
| HANDOVER/01_raw_dataset | 16.848 GB (15.691 GiB) | Official archives, selectively extracted inputs, native labels and acquisition evidence | RED authoritative |
| HANDOVER/01_raw_dataset/official_dataset/archives | 13.012 GB (12.118 GiB) | Completed train/validation/test archives and hard-linked .part aliases | Included in Handover raw total; extra names free zero |
| HANDOVER/01_raw_dataset/official_dataset/data | 3.697 GB (3.443 GiB) | Required extracted video, wrench and timestamps | Included above; distinct representation, not byte duplicate |
| HANDOVER/experiments/common_support_v2 | 0.474 GB (0.442 GiB) | Current completed evaluation; root-stage records are older protected audits | Keep evidence; feature-cache subset conditional |
| ../datasets/REASSEMBLE | 330.622 GB (307.916 GiB) | EXTERNAL sibling on same filesystem, not part of project du total | RED authoritative and active dependencies |
| ../datasets/REASSEMBLE/downloads | 58.881 GB (54.838 GiB) | Original release archives/README; data.zip logical size 58,881,334,586 bytes | RED preserve official originals |
| ../datasets/REASSEMBLE/raw | 263.985 GB (245.855 GiB) | Extracted recordings/poses; 149 data.zip member names and sizes matched existing raw files | RED preserve; no full content equivalence claimed |
| ../datasets/REASSEMBLE/cache/encoded_media | 7.609 GB (7.087 GiB) | Encoded hand videos; live training worker file descriptors read these paths | RED active input despite cache name |
| gtc-data-experiment | Absent | PHM A1–5/B1–7/F1–8 raw archives retired under a separate historical authorization | 0 current recoverable; retain recovery manifests/tooling |
| REBOOT | 0.025 GB (0.023 GiB) | Existing pinned public cards/file trees and metadata; measured before any future payload acquisition | Preserve native metadata and feasibility provenance |
| data/paderborn | 0.004 GB (0.003 GiB) | Supplementary historical transfer inputs | Preserve until dependency/retention review |
| data/rawvib | 0.058 GB (0.054 GiB) | Supplementary PHM raw-vibration evidence/inputs | Preserve; original PHM source currently absent |

Rows include nested subtotals and are not additive. Navigation symlinks under `DATASET_RESEARCH` and MSM do not duplicate data. Acquisition staging contains many hard links to authoritative inputs; its apparent size is not additional physical capacity.

## Scientific dependency chain

REASSEMBLE raw recordings → encoded media/cohort and splits → CNN/sensor features → model/checkpoints → saved predictions → per-condition metrics → thesis synthesis. Live October CNN work reads encoded hand videos. Completed Section 1/1B/2/3 and retained additional-improvement Tasks 2–4 still need their manifests, model identities, predictions and conclusions. Task 1 was discontinued on September 30; that does not authorize deleting its partial evidence or restarting it.

MSM native Milling inputs → admitted interval/label/alignment manifests → per-frame clean/corrupted CNN features and sensor statistics → fixed-seed group fits/OOF → predictions/robustness → final MSM and cross-dataset reports. Handover official archives → extracted RGB/wrench/timestamps/native outcomes → common-support v2 manifests/features → official-split fits/predictions → final report; missing participant mapping still blocks participant-safe OOF fusion. The independent review package is a curated snapshot with unique derived exports, not simply a duplicate dataset directory.

Intel Welding is currently a foundation-stage NO-GO for modelling; it retains unique authoritative raw inputs and audit findings. PHM raw retirement recovered 355.283 GiB in September, but those absent bytes are not recoverable again; preserve frozen file hashes, recovery specifications, historical targets, checkpoints and reported results. EXP-A Run 2’s reported 311 overlaps remain unverified and non-destructive. Run/lifecycle identity is not a ground-truth damage label.

Evidence: `README.md`, `REPO_MAP.md`, `docs/data_boundaries.md`, `docs/phm2026/RAW_DATA_RECOVERY.md`, `artifacts/phm2026/PHM_RAW_RETIREMENT_REPORT.md`, `docs/intel_welding/RESULTS_REVIEW.md`, `docs/thesis/FINAL_THESIS_REPRODUCIBILITY.md`, `MSM/README.md`, `HANDOVER/README.md`, both `09_final_reports/REPRODUCIBILITY.md` files, and `CROSS_DATASET_COMPARISON/configs/{execution_plan,frozen_core}.json`. Some root/dated guidance is stale; later dated result/retention records take precedence for actual status.
