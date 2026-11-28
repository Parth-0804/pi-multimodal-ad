# Chapter 7 — MSM audit

**Result:** no numerical mismatch found in the current chapter. All four result/support
tables match the retained evidence at printed precision. The main clean and corruption
results were independently recalculated from saved predictions, as were both quoted
calendar-date bootstrap intervals. This does not reproduce training or independently
validate the native labels, optical observability or physical independence.

Source: `00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/07_msm.tex`.
Starting bytes are preserved in `../before/chapters/07_msm.tex`; no manuscript edit
was made. Current external comparison history was not substituted for reading this file.

## Coverage and findings

| Current section / source lines | Check and supporting files under `implementations/MSM/results/` | Result and evidence boundary |
| --- | --- | --- |
| §§7.1–7.2, lines 1–58: role, labels, population | `09_final_reports/DATASET_OVERVIEW.md`, `DATASET_VALIDATION.md`; `02_labels_and_alignment/validated_labels.csv`, `excluded_examples.csv`; `03_processed_model_inputs/final_sample_manifest.csv` | VERIFIED retained-manifest counts: 1,895 admitted + 617 excluded = 2,512; 336 positive, 1,434 label-0, 125 label-2. Excluding label 2 leaves 1,770. The original release's 56 laboratory experiments is REPORTED in the source overview; no raw release scan was performed. Label 1 versus 0/2 and retrospective interval semantics agree with the configuration. |
| §§7.2.1–7.3.3, lines 59–128: visibility, alignment, geometry and sensor contract | `09_final_reports/DATASET_VALIDATION.md`, `04_experiment_protocol/experiment_config.json`, shared `external_eval/features.py` and dataset adapter | VERIFIED document/configuration/source correspondence: +49.73 s convention, rejected +16.04 alias, 16 frames, 640-square letterboxing, 15 channels × six statistics = 90, minimum five finite rows and 0.5 s maximum gap. Original alignment estimation, raw RGB uniqueness and optical visibility were not redone. Chapter keeps those boundaries. |
| §7.3.4 and Table 7.1, lines 130–161 | `04_experiment_protocol/group_split_inventory.csv`, final sample manifest, `02_labels_and_alignment/direction_controlled_feasibility.json`, all 54 saved prediction cases | VERIFIED 45 nominal groups, 17 positive groups, seven machine/date proxies and five dates. Recomputed all 18 assessment-fold positive/total pairs from saved clean visual predictions. DOWN-only/exclude-2 gate remains failed in the retained feasibility record. No split was changed. |
| Figure 7.1, lines 163–176 | `08_visual_examples_and_eda/prediction_examples/primary_10_examples.csv`, final sample manifest | VERIFIED row 5 identifies `imi_vm20i/dataset27/row25`, pair P03, label 0; manifest gives 112.405–113.941 s and 16 selected frames. Raw frames and sensor traces were not scanned or independently re-plotted. Figure assets remain unchanged. |
| §7.4, lines 177–246: architecture, fitting and execution scope | `09_final_reports/MODEL_IMPLEMENTATION.md`, `REPRODUCIBILITY.md`, `04_experiment_protocol/experiment_config.json`, `split_protocol.md`; shared model/feature/evaluation source; `06_evaluation_results/implementation_validation.json`, `P_EVALUATION_COMPLETE.json`, case receipts | VERIFIED source/report correspondence for CNN-only 896 features, 896→128→1 head (114,945 parameters), fresh sensor LR, separate HGB, group-OOF F2, augmented static control and gate. Three seeds × three folds × six protocols = 54 case receipts with prediction files present. Prior zero-reload/F2-refit/cache checks remain attributed to the retained audit; no model fitting/loading or feature extraction was rerun. The unavailable R condition remains unmeasured. |
| §7.5 and Table 7.2, lines 247–280 | Saved predictions; `06_evaluation_results/metrics/clean_seed_summary.csv`, `pooled_heldout_metrics.csv`, `training_diagnostic_AP.csv` | VERIFIED by fresh arithmetic: all eight clean mean AP/sample-SD rows; F2–sensor LR mean −0.0717372562, negative at all three seeds. Visual training diagnostic mean 0.9806715680, range 0.9633836674–0.9993515300 over nine fits, matches text. Training diagnostic aggregation is checked from retained metrics, not training predictions. |
| §7.6 and Table 7.3, lines 281–315 | Saved clean predictions for all six protocols; `clean_seed_summary.csv`, `paired_seed_differences.csv`, `paired_group_bootstrap_95ci.csv` | VERIFIED all 30 AP cells; sensor LR exceeds F2 in every protocol. Primary prevalence and fold prevalences match. Recalculated the two 2,000-draw paired date-cluster intervals: F2−LR [−0.1003564092, −0.0514768379], QG-clean−LR [−0.0970850630, 0.0564264492]. Five-cluster/fixed-fit limitations remain. |
| §7.7 and Table 7.4, lines 317–358 | Primary saved predictions for clean, all severities and absence; `07_robustness_experiments/robustness_metrics.csv`, configuration, shared fallback source | VERIFIED all 44 numeric table cells, including the appropriate intact branch and degraded HGB. Full absence rows use the programmed survivor. Seven families and their strongest configured severities agree. These results do not establish learned absence recovery or natural-fault robustness. |
| §7.8, lines 360–379: trade-offs and conclusion | Primary seed-42 predictions; pooled metrics; `SCIENTIFIC_INTERPRETATION_v2.md` | VERIFIED AP/Brier/F1 recomputation. F2 Brier/F1 0.0561/0.8204, LR 0.0617/0.8113, QG-clean 0.0644/0.7864 at printed precision. Qualified explanations of the visual generalization gap and the distinction between MSM architecture reuse and ViFailback donor transfer are supported; no causal mechanism is claimed. |

## Independent numerical checks performed

- Read the 54 completed saved-prediction files, totaling about 88 MiB compressed,
  and checked each SHA-256 against its case receipt. These are derived score tables,
  not raw sensor/video payloads.
- Retained 1,489,590 relevant rows: clean results for all protocols plus all primary
  corruption conditions. Checked unique assessment IDs within each pooled case.
- Recomputed AP, Brier score and F1 for 792 protocol/seed/model/condition rows;
  maximum absolute difference from the retained metrics was zero for those fields.
- Checked 126 printed numeric cells across the four tables, plus the quoted training
  diagnostic, prevalence, paired effects and seed-42 trade-offs.
- Independently recalculated the two paired calendar-date bootstrap contrasts using
  2,000 common cluster-multiplicity draws and averaged seeds. Cross-checked selected
  weighted AP calculations with scikit-learn. Differences from the retained confidence
  bounds are below 1e-12.

Receipts and reproducible audit-only scripts:
[`msm_recomputation.json`](../checks/msm_recomputation.json),
[`check_msm.py`](../checks/check_msm.py),
[`msm_uncertainty_recomputation.json`](../checks/msm_uncertainty_recomputation.json),
[`check_msm_uncertainty.py`](../checks/check_msm_uncertainty.py).

## Publication preparation

The exact candidate files are in [`chapter07_support.json`](chapter07_support.json).
Reports and compact aggregate CSVs are the core link targets. The final cohort manifest,
source/configuration and prior verification receipts provide supporting context.
All 54 individual prediction files are separately enumerated as optional audit evidence,
subject to a narrowly scoped publication decision for derived labels/identifiers and
their total size. The figure's source-derived frames and signal plots are excluded from
the proposed report/metric upload bundle; source access terms must be reviewed separately.

The retained reports contain historical paths and execution commands. Their existence
does not authorize rerunning the study. The centrally generated inventory distinguishes
current local bytes, Git tracking and remote branch contents; no publication was performed.
