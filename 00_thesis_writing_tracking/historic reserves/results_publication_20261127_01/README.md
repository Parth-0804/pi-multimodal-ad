# Result files prepared for Git tracking

27 November 2026. The researcher requested that the previously identified supporting files be removed from ignore coverage, with additional result files visible alongside their dataset experiments where possible. This pass prepares the current PHM, REASSEMBLE, MSM and ViFailback evidence in its original locations. It does not modify results, insert thesis links, run experiments, commit or push.

**All 43 core/supporting additions from the preceding audit are included.** Broader review selected 3,187 existing files (332.98 MiB): 1,723 were already tracked and 1,464 are new additions (261.86 MiB). Each selected file is smaller than 6 MiB. The new additions and exact ignore changes are staged for review; GitHub will change only after a later commit and push.

| Dataset / ownership | Selected existing files | New files staged | New content, MiB |
| --- | ---: | ---: | ---: |
| PHM2026 | 468 | 247 | 14.37 |
| REASSEMBLE | 694 | 274 | 54.48 |
| MSM | 971 | 942 | 193.00 |
| ViFailback | 1,043 | 0 | 0.00 |
| Shared sources / earlier audit evidence | 11 | 1 | 0.01 |
| Total | 3,187 | 1,464 | 261.86 |

The counts above describe scientific/supporting files, excluding this preparation record and the four edited `.gitignore` files. Selection follows file ownership rather than the reviewing agent's chapter assignment, so sub-review counts can differ slightly. Already tracked files were not restaged merely because they appear in the inventory.

## Exact files and experiment context

- [Selected files — CSV](selected_files.csv) and [JSON](selected_files.json): exact original paths, sizes, SHA-256/Git blob identities, roles, selection reasons, inspection depth, prior audit membership and initial tracking state.
- [Excluded candidates](excluded_files.json): explicit mixed-payload/feature/model/intermediate exclusions and representative excluded media. It is not an exhaustive inventory of raw data or every excluded cache file.
- [PHM selection](reviews/phm_selection.md), [REASSEMBLE selection](reviews/reassemble_selection.md), [MSM/ViFailback selection](reviews/msm_vifailback_selection.md): reviewed experiment boundaries and file-type checks. Their JSON companions retain the individual selection decisions.
- [Validation](VALIDATION.json): selected-byte preservation, ignore-boundary checks, staged-path/identity checks and preservation of pre-existing edits.

The expanded selection includes compact metric tables, score-only predictions, run/target/cohort/split records, fitting and calibration summaries, small fusion coefficients, training curves, execution and timing receipts, warnings/corrections, negative findings and final reports. Related files stay together under their original dataset and run directories. Dated and superseded results remain dated evidence, not a new common leaderboard or a claim that every historical run completed.

PHM coverage follows the audited model/target studies, their associated tutorials, and compact screening summaries. REASSEMBLE covers the audited core and later representation/fusion/robustness studies, with compact C20/C100 evidence. MSM covers the retained final-result study and its sensitivities, including all 54 compressed prediction tables. ViFailback's selected final/dated reports and compact summaries were already tracked; missing per-fit artifacts remain missing.

## Ignore changes

Exact allow rules were added to:

- [Root .gitignore](../../.gitignore)
- [MSM results .gitignore](../../implementations/MSM/results/.gitignore)
- [REASSEMBLE seed-stability .gitignore](../../implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/26102026_phase1_full_cnn_seed_stability/.gitignore)
- [REASSEMBLE C100 .gitignore](../../implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/.gitignore)

The global CSV/array/media/model exclusions remain. Where an ignored ancestor had to be opened, its children remain ignored by default and only selected descendants are allowed. These rules expose the reviewed existing files without automatically publishing every future output in those folders. The compact selection CSV also has an exact exception. No `git add -f`, blanket add, move, renaming or scientific artifact rewriting was used.

## What remains excluded

Raw/source media and sensor payloads, cached/engineered feature matrices, model/optimizer binaries, large intermediates, temporary outputs, mutable locks, bulk logs, full conversation dumps and protected historical EDA were not added. No raw payload scan, model load or scientific rerun occurred. This task does not broaden to HANDOVER, other datasets or unrelated legacy feasibility trees.

Publication preparation found that **49 prediction NPZs from the earlier audit inventory also contain embeddings or quality-feature matrices**. Those files remain excluded; they were not silently repacked. Additional mixed-quality prediction/training CSVs and intermediate stacking banks were similarly excluded. Their compact results and uncertainty summaries remain selected. The selection records identify the exact exclusions. Reading a file for a numerical audit did not automatically establish that its entire payload was appropriate for Git.

The PHM processing JSONL is a 2.78 MiB metadata receipt: its 7,124 records contain identifiers, timing/count/rate metadata and exclusion/error status, without signal or feature arrays. It is retained as provenance. Derived identifiers, labels and small coefficient tables remain explicit in the selected records. No claim is made that making these files trackable reproduces training or resolves dataset redistribution rights for excluded source media.

## Verification and scientific limits

New candidates were inspected by bounded CSV headers/rows, JSON structure/report role, text excerpts or NPZ member headers. Previously audited files retain their recorded inspection limits. This pass checks file suitability, identities and Git visibility; it does not independently validate every newly included historical metric. The prior chapter audit's numerical findings and unresolved PHM/REASSEMBLE/ViFailback evidence qualifications remain unchanged.

Validation confirms that all selected files are visible to Git, all previously ignored explicit exclusions remain ignored, and ordinary/hidden/nested sibling canaries remain ignored in reopened directories. The staged changes are limited to selected additions, the four ignore files and this preparation record. Pre-existing manuscript/document edits and unrelated untracked work remain outside the staged changes.

`git diff --check` on the full existing working tree still encounters pre-existing CRLF formatting. The CRLF-aware check passes. Historical result text is retained byte-for-byte; any staged whitespace warnings from original artifacts are reported in `VALIDATION.json`, rather than corrected by altering those scientific records.
