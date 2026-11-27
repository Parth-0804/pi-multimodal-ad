# PHM compact result selection

27 November 2026. Preparation only; no result edits, ignore changes, staging, commit, upload, or experiment execution was performed by this selection task.

Selected **472 exact files** (18.70 MiB), including all 73 original Chapter 5 audit candidates. Of these, **247 are not currently tracked** (14.37 MiB). Every included file is at most 10 MiB. `phm_selection.json` supplies exact paths and decisions.

Scope: 14 model/target/result run families supporting the audited studies; target v1 under superseded; `docs/studies`; the final RT-DETR baseline and frequency PatchTST tutorial studies; and the two compact raw-vibration screen JSON summaries. Preserve all run IDs and original locations. Target versions, initial misnamed fusion, superseded runs, failed/partial detector attempts, negative screening outcomes, and historical limitations remain distinct.

New CSVs were screened by header and first record; JSON objects by schema/report role; report/configuration text by bounded excerpts. This establishes file role, not independent metric accuracy. The earlier audit supplies its separate accuracy checks. Original audit inspection flags are retained where no new content screening was performed. Historical reports may contain claims narrowed by the current thesis; selection does not strengthen them.

Includes compact metrics, predictions, target/run/tooth tables, numeric plot sources, split/availability summaries, configuration/scaler parameters, provenance/input/output manifests, training-history metrics, reports and execution-status receipts. Source/group/member IDs and provisional labels remain explicit derived metadata. Manifests may refer to excluded media; including a manifest does not include or grant redistribution of that media.

Exclusions: all newly encountered photographs/raster/vector figures; copied per-image YOLO labels and full COCO/per-component annotation corpora; review queues; raw/normalized sensor traces and per-example photometric feature values; Parquet/NPZ/NPY binary duplicates/features/caches; checkpoints; console logs; and additional unaudited code. The original audited thesis schematic is retained. No raw tree or protected initial EDA was traversed or read. The generic PHM EDA, dataset-description, model-dataset and sensor-feature run families were outside this scope.

Excluded binary/media payloads were classified by pathname, extension and size only. The JSON retains exact excluded non-media candidates and representative media/label examples; bulk excluded files are summarized here, not individually enumerated:

- image or figure payload: 5268 files, 2306.62 MiB (metadata only).
- per-image training label materialization: 995 files, 1.58 MiB (metadata only).

## Ignore constraints

No nested `.gitignore` exists in the selected run/tutorial/study roots. The relevant root rules observed with `git check-ignore --no-index -v` are:

- `.gitignore:15` → `*.csv` (247 selected paths; a leading `!` is an existing exception).
- `.gitignore:619` → `!/implementations/REASSEMBLE/results/artifacts/reports/CROSS_STUDY_SYNTHESIS_HANDOFF.md` (1 selected paths; a leading `!` is an existing exception).
- `.gitignore:712` → `!/implementations/PHM2026/results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv` (1 selected paths; a leading `!` is an existing exception).
- `.gitignore:713` → `!/implementations/PHM2026/results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_summary.csv` (1 selected paths; a leading `!` is an existing exception).
- `.gitignore:714` → `!/implementations/PHM2026/results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/tables/run_damage_targets.csv` (1 selected paths; a leading `!` is an existing exception).
- `.gitignore:715` → `!/implementations/PHM2026/results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/tables/per_tooth_damage.csv` (1 selected paths; a leading `!` is an existing exception).
- `.gitignore:716` → `!/implementations/PHM2026/results/processed/raw_vibration/l1_screen.json` (1 selected paths; a leading `!` is an existing exception).
- `.gitignore:717` → `!/implementations/PHM2026/results/processed/raw_vibration/sector_screen.json` (1 selected paths; a leading `!` is an existing exception).

`implementations/PHM2026/docs/tutorials/rtdetr_storybook/.gitignore` was inspected: it excludes `/demo_data/`, `/raw_demo_data/` and `/outputs/`; that teaching workspace and its media remain outside this selection. Two nested `.gitignore` files inside `results/runs/phm2026/*-dataset-eda/` were located by filename but are outside the selected families and were not used to authorize anything. Root exact-path rules are sufficient for this selection; do not unignore entire directories.

Tracking and any later publication are separate operations owned by the parent task. The requested preparation does not authorize publication of third-party imagery or a scientific rerun.
