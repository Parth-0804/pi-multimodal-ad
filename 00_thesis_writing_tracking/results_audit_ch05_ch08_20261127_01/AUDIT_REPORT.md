# Chapters 5–8: results and GitHub evidence audit

27 November 2026. The starting point was the current working tree, including uncommitted thesis edits, at HEAD `2ae0c76e3d377a0fae3361c00f2e7d65f704545a`.

**No numerical mismatch was found in the inspected chapter results.** Fresh calculations support the principal PHM, REASSEMBLE and MSM results. ViFailback's printed results match retained summaries, but its missing per-fit artifacts prevent fresh prediction-level verification. There are evidence-pointer, historical-protocol and wording issues to resolve before presenting the supporting material as a complete reproducibility package.

This was the authorized read-only audit and upload inventory. No thesis text, hyperlink, figure, experiment source or historical result was changed. Nothing was staged, committed or uploaded. No fitting, training, inference or raw-data processing ran. A LaTeX rebuild was unnecessary because the manuscript was unchanged.

## Active files and coverage

The active build is [`../Thesis/LaTeX_Project/main.tex`](../Thesis/LaTeX_Project/main.tex), using the following files under its `chapters/` directory. Each detailed review covers the current chapter section by section and identifies which checks were new arithmetic, source/report correspondence, or attributed earlier work.

| Chapter | What was checked | Result and main limit |
| --- | --- | --- |
| [5 — PHM](reviews/chapter05.md) | Principal 20-run LOEO MAE/RMSE/Spearman and 10,000-draw run bootstrap; target-version constants; visual image/run MAEs; Ridge/HF and supplementary seed aggregates; current qualifications and supporting records | Printed values agree. The fixed-fusion confidence interval remains report-level evidence. A plan/execution seed discrepancy, prior EXP-F development exposure and overly broad reproducibility wording need explicit treatment. |
| [6 — REASSEMBLE](reviews/chapter06.md) | All eight core models' five metrics; strongest-corruption/fallback table; F2 visual-term arithmetic; 38 saved neural permutation arrays; follow-up result correspondence; C20 prediction scores and compute receipts; Appendix D | Printed values agree. Four historical handoff pointers are missing. Appendix D's dated original-visual-file availability statement needs a current-status update: that file now exists and exactly matches the reused scores. Several follow-up intervals were checked against reports, not newly resampled. |
| [7 — MSM](reviews/chapter07.md) | All four tables; AP/Brier/F1 over 792 saved metric rows; 54 prediction-file hashes; two paired date-cluster bootstrap intervals; cohort/support counts; scope and limitations | No discrepancy found. Original label validity, physical independence, alignment estimation and training were not revalidated. Five date clusters and fixed-model uncertainty remain material limits. |
| [8 — ViFailback](reviews/chapter08.md) | All six tables and numerical prose against compact reports; macro-AP arithmetic; 79/111 fit coverage; saved split disjointness; final result-summary identity; calibration/transfer scope | Summary correspondence passes. Per-fit artifacts referenced for all 79 completed fits are absent locally; AP/AUROC/calibration/F2 replay and bootstrap reconstruction could not be repeated. Two historical evidence pointers need resolution. |

These findings do not certify training reproduction, physical label validity, independent holdout selection, scientific-paper accuracy or generalization. Every result retains its own target, cohort, positive-class convention, fitting history and uncertainty limits. HANDOVER is in Appendix H, rather than these four result chapters; a new HANDOVER audit was outside this pass.

## Issues to carry into a later correction/publication pass

No replacement numerical result is proposed. The following distinguish manuscript clarifications from source-retention gaps.

| Location | Finding | Concrete next action |
| --- | --- | --- |
| Chapter 5, lines 281–287; fixed-fusion supporting records | The plan specifies seed `20260912`; executed configuration/provenance record `20260814`. The chapter does not assert the seed or full plan compliance. No explaining amendment was located. | Disclose this supporting-record discrepancy. Preserve both original records; do not silently edit history. |
| Chapter 5, protocol/limitations at lines 263–278 and 315–330 | Earlier EXP-F analysis informed development. The chapter avoids claiming a pristine holdout but does not make that prior exposure explicit near the principal comparison. | Add a bounded historical-exposure sentence in a later writing pass. |
| Chapter 5, lines 202–204 | “Reproducible implementation” exceeds the saved-output arithmetic and inspectability established here; exact dirty-tree source is incomplete for some historical runs. | Narrow the wording or supply an actually executed reproduction record. |
| Chapter 5, lines 284–285 | Fixed-fusion interval `[-0.548,+0.414]` agrees with the report, but its per-run test inputs were not located. | Keep the interval attributed to the report unless its inputs are recovered. The principal LOEO interval was independently recomputed. |
| Chapter 6 follow-up/resource citations E057–E060 | Four files in the old `docs/thesis_review_handoff/REASSEMBLE_FINETUNING_CURRENT_STATUS_20261110_02/` package are absent. Current C20/C100 records support the main scores and resource sums, but do not establish the exact old validator-error/cache-retirement narrative. | Use the identified current evidence for claims it supports; recover or qualify the remaining historical claims. Exact missing paths and replacements are in the Chapter 6 review/inventory. |
| Appendix D, lines 105–110 | Its 25 November audit said the original visual prediction file was unavailable. `implementations/REASSEMBLE/results/runs/unimodal_baselines_visual_sensor/predictions/rtdetr_perm00.npz` is now present and has exact probability parity with reused U2. | Preserve the historical audit's date/scope and append the new availability/parity finding. |
| Chapter 8, E095 | The cited live `CURRENT_RESULTS.json` path is absent; the final snapshot is retained and its SHA-256 matches the prior verification record. | Point future support navigation to the exact `18_fit_stop_and_analysis_20261124T1955Z/final_evidence/11_metrics_and_statistics/CURRENT_RESULTS.json` snapshot listed in the inventory. |
| Appendix D, E108 | `thesis_manuscript/evidence/external_dataset_results.json` was not found. Current domain reports support the ViFailback summary, but are not established as identical replacements for that missing inventory. | Cite the actual domain evidence for the supported claims; retain the missing historical pointer as unresolved until recovered or superseded explicitly. |
| ViFailback retained evidence | Completion rows name absent per-fit predictions, receipts, configurations and histories. Compact summaries/protocols remain available; they cannot replace numerical inputs for a fresh replay. | Record this limitation in the public evidence index. Recover derived artifacts before claiming independent prediction-level reproducibility; this audit does not authorize a rerun. |

The reviews also preserve what was already correct: PHM's photographic proxy and sensor-only inference boundaries; REASSEMBLE's F2 diagnostic limits and inconclusive adaptive results; MSM's weaker-vision and five-cluster qualifications; ViFailback's partial adaptation, reused development evidence, single donor and unexecuted robustness work.

## Supporting files and GitHub status

See the [upload plan](GITHUB_UPLOAD_PLAN.md), [complete exact-file inventory](supporting_file_inventory.csv), and [core files still absent on main](core_files_to_add.csv). The JSON version additionally preserves hashes, inspection flags and detailed notes.

Read-only remote checks resolved `main` to `40f3f7ecea292c13fd1b2906b64e2654c281071b` and the current review branch to `2ae0c76e3d377a0fae3361c00f2e7d65f704545a`. All 342 selected existing files were compared by Git blob identity against complete relevant subtrees of that pinned `main`. The initial repository-wide recursive response was truncated, so it was not used to infer absence; complete subtree/parent metadata were retained under `checks/`.

- **167 files already on main have identical bytes.** No re-upload is needed for them.
- **21 core files are absent on main**, seven each for PHM, REASSEMBLE and MSM; together about 1.75 MiB.
- **22 additional supporting files are absent**, about 5.67 MiB. Together with the core files, these are 43 identified additions of about 7.42 MiB.
- **132 optional audit-input files are absent**, about 146.27 MiB, chiefly retained predictions and associated receipts. These are separately listed, not part of the essential report/metric bundle.
- ViFailback's 48 selected existing files are already on main. Its missing per-fit artifacts cannot be uploaded from this checkout and are not hidden among the existing-file counts.

All 21 core additions are currently ignored by Git. Publication would require exact-path tracking rules consistent with the repository output policy. No ignore rule was changed. The inventory identifies derived IDs/labels and source-level publication review separately; a file's numerical utility does not establish permission to redistribute dataset content. Raw media, sensor payloads, caches, environments and checkpoints are not proposed for this bundle.

## Verification receipts and limits

The audit's [starting manuscript manifest](manuscript_start_manifest.json), per-chapter reviews, [MSM arithmetic receipt](checks/msm_recomputation.json), [MSM interval receipt](checks/msm_uncertainty_recomputation.json), remote tree metadata and [final preservation/check receipt](checks/final_checks.json) document the actual scope. The Python scripts under `checks/` perform bounded calculations from saved predictions; they do not run models.

Final checks found all 29 snapshotted manuscript files byte-identical to the starting copies, no Git-status changes outside this audit directory, and no missing or changed bytes among the 342 inventoried files. Every core candidate was inspected. Local report links resolve. Standard `git diff --check` flags the existing CRLF lines in the dirty working tree; the same check with `core.whitespace=cr-at-eol` passes. New audit Markdown/Python files have no trailing whitespace. No dependency installation was needed.

The `before/` snapshots and large remote metadata files are local audit records, not proposed bulk uploads. Historical reports and frozen configurations retain their original paths/commands. A source file's existence was never treated as proof of execution, and previous investigators' checks were not relabeled as new checks.
