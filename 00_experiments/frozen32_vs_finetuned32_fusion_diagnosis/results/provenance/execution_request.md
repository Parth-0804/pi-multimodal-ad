# First commit completed work, then run the Frozen32 vs Fine-tuned32 fusion diagnosis

Work in the existing HFU repository:

`/home/student/Master_Thesis_WS/pi-multimodal-ad`

This is a controlled follow-up study. Do not repeat completed experiments or broad audits.

The scientific question is:

> Why did Fine-tuned32 obtain better standalone visual AP without producing better F2 fusion AP?

The existing study found:

- Frozen32 visual AP: 0.219427
- Fine-tuned32 visual AP: 0.230609
- Frozen32 F2 AP: 0.439584
- Fine-tuned32 F2 AP: 0.438566

The exploratory Fine-tuned32 minus Frozen32 fusion difference was approximately −0.001017 with 95% interval [−0.009295, +0.009400].

Existing diagnostics also found that the 32-frame fine-tuned visual branch was worse in all five inner OOF banks, while outer-assessment visual AP improved in three of five folds. This is currently the most concrete lead, but it is not yet an established cause.

The goal of this experiment is to distinguish four explanations:

1. Training-seed instability.
2. The earlier unequal five-epoch frozen versus two-epoch fine-tuned training budget.
3. Limited complementary information beyond the sensor branch.
4. Interaction between visual calibration / OOF behaviour and F2 fitting.

A fifth valid outcome is:

`CAUSE_NOT_RESOLVED`

Do not force a causal explanation.

---

# PHASE 0 — GROUP AND PUSH THE EXISTING COMPLETED WORK FIRST

Before implementing this experiment, organise the existing uncommitted scientific work into logical Git commits and push those commits to the existing GitHub remote.

## 0.1 Inspect before touching Git

Run and save:

- `git status --short`
- `git branch --show-current`
- `git remote -v`
- `git log --oneline --decorate -n 15`
- `git diff --name-status`
- `git diff --stat`

Inspect applicable repository instructions.

Identify:

- files belonging to the completed encoder comparison;
- files belonging to the selected-model noise study;
- files belonging to the adaptive-fusion study;
- files belonging to the frozen/fine-tuned 16/32-frame study;
- files belonging to the later fusion-AP diagnostic;
- unrelated pre-existing user changes.

Do NOT use `git add -A`, `git add .`, `git reset --hard`, `git clean`, `git stash`, or force-push.

Do not alter unrelated dirty-tree work.

Do not commit:

- raw datasets;
- model-weight blobs that are intentionally excluded from version control;
- huge feature caches;
- generated temporary files;
- credentials;
- local environment files;
- unrelated PowerPoint/assets unless they clearly belong to the requested task and are already intended for version control.

Respect existing `.gitignore`.

If large generated artifacts are already tracked intentionally, preserve existing repository policy rather than inventing a new one.

## 0.2 Create grouped commits by scientific task

Stage files selectively.

Use approximately these logical commit groups, adapting names only when the actual files show that a different grouping is more accurate:

### Commit 1

`reassemble: add frozen CNN vs hybrid encoder study`

Include only the completed RT-DETR encoder-comparison implementation, configuration, compact results/reports and reproducibility metadata appropriate for Git.

Expected task root:

`00_experiments/rt_detr_encoder_comparison/`

### Commit 2

`reassemble: add selected-model robustness study`

Include only the completed input-corruption/noise experiment material suitable for Git.

Expected task root:

`00_experiments/fusion_noise_test/`

### Commit 3

`reassemble: add quality-aware fusion robustness pilot`

Include only the completed adaptive/quality-aware fusion pilot suitable for Git.

Expected task root:

`00_experiments/adaptive_fusion_robustness/`

### Commit 4

`reassemble: add frame-count and backbone fine-tuning study`

Include the completed Frozen16/Fine-tuned16/Frozen32/Fine-tuned32 implementation, compact results, protocol and reproducibility metadata suitable for Git.

Expected root:

`00_experiments/visual_backbone_one_day/`

### Commit 5, only if it is genuinely distinct

`reassemble: add fusion AP diagnostic analysis`

Use this only if the later fusion-diagnostic addendum is sufficiently independent that it should not be included with Commit 4.

Expected material includes:

`fusion_AP_explanation_addendum_01/`

Do not manufacture empty commits.

For each commit:

1. Show staged files before commit.
2. Verify no unrelated files are staged.
3. Run `git diff --cached --check`.
4. Commit only that task.
5. Record the resulting commit hash.

Do not rewrite existing published history.

## 0.3 Push

After all grouped commits succeed:

- verify `git status`;
- push the current branch to its configured GitHub remote;
- if the current branch has no upstream, set an upstream only to the existing intended remote;
- do not force-push.

If the current branch is protected and a normal push is rejected, create a human-readable branch:

`research/reassemble-experiment-results`

only if this can be done without disturbing unrelated local work.

Push that branch normally.

If authentication, remote permissions, or repository policy prevents a safe push:

**STOP before starting the new scientific experiment.**

Report the exact blocker and the local commit hashes. Do not bypass authentication or continue as though the repository were backed up.

Create a concise `GIT_COMMIT_REPORT.md` later containing:

- commit hash;
- message;
- task represented;
- major included paths;
- push branch/remote;
- deliberately excluded files.

---

# PHASE 1 — CREATE THE NEW STUDY

After the completed work has been successfully pushed, create:

`00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/`

Use only clear human-readable paths:

```text
00_experiments/
  frozen32_vs_finetuned32_fusion_diagnosis/
    README_FIRST.md
    PROTOCOL.md
    resolved_config.json
    GIT_COMMIT_REPORT.md
    run_experiment.py
    code/
    tests/
    data_manifests/
    existing_evidence/
    results/
      seed_42/
        frozen32_two_epochs/
        finetuned32_two_epochs/
        uniform_fusion/
        f2_fusion/
      seed_20261023/
        frozen32_two_epochs/
        finetuned32_two_epochs/
        uniform_fusion/
        f2_fusion/
      comparison/
        RESULTS_SUMMARY.md
        seed_stability.csv
        visual_results.csv
        fusion_results.csv
        oof_vs_assessment.csv
        calibration_comparison.csv
        complementarity.csv
        paired_intervals.csv
        plots/
      checks/
      provenance/
      REVIEW_PACKAGE.zip
```

Avoid:

- hash-named directories;
- timestamp-only run names;
- `final_final`;
- `task_1`, `task_2`;
- unexplained abbreviations.

Timestamps and hashes belong in metadata, not folder names.

---

# PHASE 2 — REUSE EXISTING WORK BEFORE COMPUTING ANYTHING

Inspect the existing completed study:

`00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/`

and diagnostic:

`00_experiments/visual_backbone_one_day/fusion_AP_explanation_addendum_01/`

Do not rerun:

- the original four-condition study;
- existing bootstrap analyses;
- existing leakage/replay checks;
- existing AP-contribution diagnostics;
- previous plots;
- encoder comparison;
- robustness study;
- adaptive-fusion study.

Build a small inventory:

| Item | Existing / reusable | New work needed |
|---|---|---|

Reuse exact compatible:

- 32-frame sample cohort;
- 32-frame selections;
- outer folds;
- inner folds;
- calibration memberships;
- sensor predictions;
- sensor calibrators;
- labels;
- recording IDs;
- original Fine-tuned32 seed-42 two-epoch fits where identities match;
- original seed-42 OOF and outer predictions;
- existing bootstrap recording order/draws where appropriate.

Do not assume compatibility based only on filenames.

Verify hashes, configuration, sample keys, split identities and fitting roles.

---

# PHASE 3 — LOCK A FAIR DIAGNOSTIC PROTOCOL

## Primary comparison

Compare only:

- `frozen32_two_epochs`
- `finetuned32_two_epochs`

Do not include 16-frame models.

Do not include hybrid encoder models.

Do not add temporal transformers.

Do not add noise/corruption.

Do not alter the sensor branch.

## Matched training budget

Both visual conditions use exactly:

- 32 frames per completed action;
- same selected frame indices;
- same preprocessing;
- same visual head architecture;
- same training samples;
- same outer/inner/calibration memberships;
- same effective batch policy;
- same precision;
- same head optimizer settings;
- same head learning rate;
- same number of action passes;
- exactly **2 training epochs**.

Frozen32:

- CNN backbone stays fully frozen.
- Only the visual classifier/head trains for 2 epochs.

Fine-tuned32:

- exactly the same final CNN spatial stage as the previous study is trainable;
- visual head is trainable;
- earlier CNN stages remain frozen;
- trainable final-stage LR remains the previously authorised value unless source evidence shows otherwise.

This is an **equal-epoch / equal-data-budget comparison**, not equal compute.

State that explicitly.

Do not claim equal compute because Fine-tuned32 updates more parameters.

## Seeds

Use exactly two seed families:

- existing seed family: `42`
- new seed family: `20261023`

Do not search seeds.

Do not choose a seed after seeing results.

For seed 42:

reuse existing two-epoch Fine-tuned32 results if they exactly match this protocol.

If a compatible Frozen32 epoch-two checkpoint/output already exists, reuse it.

Otherwise retrain only the missing Frozen32 two-epoch fits.

For seed 20261023:

run both Frozen32 and Fine-tuned32 under the locked two-epoch protocol.

This gives one existing and one new seed family without launching a broad multi-seed campaign.

Do not add a third seed automatically.

---

# PHASE 4 — KEEP SENSOR INFORMATION IDENTICAL

The sensor branch must be fixed.

For every corresponding:

- outer fold;
- inner OOF fold;
- calibration role;
- assessment action;

use the exact same sensor model, calibration and probability for Frozen32 and Fine-tuned32.

The sensor branch must also be identical across seed families unless an upstream fitting dependency genuinely requires otherwise.

Prefer reuse of the original completed study's identified sensor predictions.

Verify exact sample-key equality and probability equality.

Do not refit or retune sensors merely because the visual seed changed.

Record the sensor artifact identity in every fit manifest.

---

# PHASE 5 — COMPARE TWO FUSION METHODS

For every seed and outer fold evaluate BOTH:

## A. Uniform fusion

Use:

`p_uniform = 0.5 * p_visual + 0.5 * p_sensor`

using calibrated branch probabilities.

No training.

No threshold tuning.

Its purpose is diagnostic:

> Does Fine-tuned32's better visual representation help when the fusion rule itself cannot adapt its coefficients?

## B. Existing F2 fusion

Use the existing F2 definition:

`p_F2 = sigmoid(intercept + a_visual*p_visual + a_sensor*p_sensor)`

Fit F2 only from valid inner-OOF branch probabilities for that outer fold and seed.

Never fit F2 on outer-assessment rows.

The F2 feature order must remain:

`[p_visual, p_sensor]`

Use the existing F2 solver/C/intercept settings.

Do not introduce extra calibration after F2.

Do not tune F2 based on assessment results.

---

# PHASE 6 — EXPLICITLY TEST THE OOF-VS-ASSESSMENT HYPOTHESIS

This is a primary diagnostic.

For each:

- seed;
- outer fold;
- visual condition;

calculate visual branch metrics separately on:

1. inner OOF predictions used as F2 training inputs;
2. outer-assessment predictions.

Report at minimum:

- AP;
- AUROC;
- Brier;
- log loss;
- fixed-threshold recall/precision;
- probability mean/std;
- positive/negative probability summaries;
- calibration/reliability bins under the existing fixed method.

Do not describe F2 performance on its OOF training rows as independent validation.

The visual OOF predictions are held out from visual-branch fitting/calibration, but they are subsequently used to fit F2.

That distinction must remain explicit.

Create:

`results/comparison/oof_vs_assessment.csv`

with one row per:

seed × fold × visual condition × evaluation role.

Answer:

- Is Fine-tuned32 consistently stronger or weaker than Frozen32 in OOF predictions?
- Is the direction different on outer assessment?
- Is the OOF-to-assessment shift repeatable across the two seeds?
- Does this mismatch align with changes in the fitted F2 visual coefficient?

This analysis may support an OOF/stacker mismatch explanation, but do not call it causal unless the full evidence warrants that wording.

---

# PHASE 7 — TEST COMPLEMENTARITY, NOT JUST VISUAL AP

For each seed and outer fold, use identical assessment actions and fixed sensor predictions.

Calculate:

- visual correct / sensor wrong;
- sensor correct / visual wrong;
- both correct;
- both wrong;

separately for:

- failures;
- successes.

Also calculate continuous true-label:

- Brier change;
- log-loss change;

for:

- sensor-missed failures;
- sensor-detected failures;
- sensor-false-positive successes;
- sensor-correct successes.

Do not use subgroup AP to compare groups with different prevalence unless correctly conditioned and explicitly justified.

The question is:

> Does Fine-tuned32 improve on the actions where additional visual information could actually add something beyond sensors?

If Fine-tuned32 gains mostly where the sensor is already correct, report that as descriptive evidence of limited additional complementarity.

Do not call that sensor dominance.

---

# PHASE 8 — DIAGNOSE THE FUSION INTERACTION

Compare Frozen32 and Fine-tuned32 under:

- visual only;
- sensor only;
- uniform fusion;
- F2 fusion.

This provides a useful diagnostic decision pattern.

## Pattern A

Fine-tuned32 visual improves  
AND uniform fusion improves  
BUT F2 does not improve

Interpretation:

`F2/calibration/OOF interaction becomes a supported candidate explanation.`

Still do not call it proven causal without consistency across folds/seeds.

## Pattern B

Fine-tuned32 visual improves  
BUT neither uniform nor F2 improves

Interpretation:

`Limited complementary information becomes a supported candidate explanation.`

## Pattern C

Fine-tuned32 benefit changes substantially between seed 42 and seed 20261023

Interpretation:

`Training-seed instability becomes a supported candidate explanation.`

## Pattern D

Under equal two-epoch training, Frozen32 changes enough that the earlier visual/fusion discrepancy disappears or reverses

Interpretation:

`The original five-vs-two epoch budget was a material confound.`

## Pattern E

OOF Fine-tuned32 remains consistently worse while outer-assessment Fine-tuned32 is better, and F2 loses or downweights visual influence

Interpretation:

`OOF-to-assessment branch mismatch becomes a supported candidate explanation.`

Multiple patterns may coexist.

If none is stable:

`CAUSE_NOT_RESOLVED`

is the correct outcome.

---

# PHASE 9 — STATISTICS AND UNCERTAINTY

Primary scientific comparisons:

1. Fine-tuned32 − Frozen32 visual AP under the matched 2-epoch protocol.
2. Fine-tuned32 − Frozen32 uniform-fusion AP.
3. Fine-tuned32 − Frozen32 F2 AP.

Report these:

- separately for each seed;
- pooled across folds for each seed;
- with mean-fold AP separately;
- and with a simple two-seed descriptive stability table.

Reuse the original recording-cluster bootstrap design where valid.

Use 2,000 paired recording-cluster bootstrap draws within each seed.

Do not pretend that two seeds give a robust estimate of training-seed uncertainty.

Do not pool the two seeds as independent recordings.

Treat seed-to-seed variation descriptively.

Report:

- effect estimate;
- 95% recording-bootstrap interval;
- fold-level values;
- seed-level values.

Keep:

pooled AP ≠ mean-fold AP.

Do not select whichever aggregation favours a preferred method.

---

# PHASE 10 — COMPUTE AND TIME BUDGET

Use one GPU maximum.

No parallel scientific GPU jobs.

Target total additional execution within 24 hours.

Because seed 42 Fine-tuned32 may be reused, the main expensive new work should be the second Fine-tuned32 seed plus any missing two-epoch Frozen32 fits.

Before starting the new seed:

estimate remaining runtime from the completed 32-frame fine-tuning logs.

Proceed only if the complete matched new-seed comparison plus final reporting reasonably fits the budget.

Reserve at least 2 hours for:

- final evaluation;
- diagnostics;
- packaging;
- safe stopping.

If full five-fold seed 20261023 cannot fit:

do not silently change epochs, folds, samples or architecture.

Stop with:

`PARTIAL_NEW_SEED`

and report exactly what completed.

Do not extend automatically into multi-day execution.

No package installs, data downloads, external compute purchases or new architecture work.

---

# PHASE 11 — IMPLEMENTATION CHECKS

Before real training, verify only the checks relevant to this new study.

Do not repeat the old full validation suite when already covered.

Check:

- same 32-frame action keys;
- same frame selections;
- same target values;
- same recording memberships;
- same sensor probabilities;
- correct two-epoch stop;
- frozen CNN remains unchanged in Frozen32;
- only final CNN stage + head update in Fine-tuned32;
- BatchNorm/running-buffer policy matches the previous study;
- correct random-seed restoration;
- correct OOF/assessment roles;
- uniform fusion arithmetic;
- F2 arithmetic;
- saved checkpoint replay;
- no outer-assessment row enters training/calibration/F2 fitting.

Reuse completed checks where hashes and inputs match.

Do not manufacture a new test count by rerunning old checks.

---

# PHASE 12 — DELIVERABLES

Create:

`README_FIRST.md`

A concise status and final answer.

`PROTOCOL.md`

Locked scientific protocol.

`GIT_COMMIT_REPORT.md`

The earlier grouped commit/push record.

`results/comparison/RESULTS_SUMMARY.md`

Main diagnostic results.

`results/comparison/visual_results.csv`

Frozen32 vs Fine-tuned32 by seed/fold.

`results/comparison/fusion_results.csv`

Visual / sensor / uniform / F2 results.

`results/comparison/oof_vs_assessment.csv`

OOF-versus-assessment visual behaviour.

`results/comparison/complementarity.csv`

Sensor-error complementarity diagnostics.

`results/comparison/calibration_comparison.csv`

Saved calibration/probability diagnostics.

`results/comparison/seed_stability.csv`

Seed-level comparison.

`results/comparison/paired_intervals.csv`

Matched recording-bootstrap intervals.

Also create clear plots:

1. Visual AP by seed and fold.
2. Uniform fusion vs F2 by condition.
3. OOF versus assessment visual AP.
4. Fine-tuned-minus-frozen differences with intervals.
5. Complementarity on sensor-missed failures.

Keep plots factual and editable/source-reproducible.

---

# PHASE 13 — FINAL CAUSE ASSESSMENT

Finish with this table:

| Candidate explanation | Evidence for | Evidence against | Status |
|---|---|---|---|
| Seed instability | ... | ... | Supported / Weak / Not supported / Unresolved |
| Unequal training budget | ... | ... | ... |
| Limited sensor complementarity | ... | ... | ... |
| Calibration/F2 interaction | ... | ... | ... |
| OOF-to-assessment mismatch | ... | ... | ... |

Do not mark a cause “Supported” merely because it is plausible.

Use:

`Supported`

only when the new controlled evidence behaves consistently with the predeclared diagnostic prediction.

Otherwise use:

- `Weak evidence`
- `Not supported`
- `Unresolved`

A valid conclusion may be:

> “The discrepancy is not attributable to a single mechanism from the available evidence.”

---

# PHASE 14 — REVIEW PACKAGE

Create:

`REVIEW_PACKAGE.zip`

Include only:

- new source;
- tests;
- configuration;
- protocol;
- Git commit report;
- small manifests;
- keyed assessment predictions;
- OOF prediction tables necessary to inspect the mechanism;
- metrics;
- intervals;
- plots;
- results summary;
- checks.

Exclude:

- raw videos;
- raw dataset copies;
- huge feature caches;
- full model blobs when existing checked local checkpoints can be referenced;
- credentials;
- unrelated historical outputs.

Create and verify a hash manifest.

Do not upload the ZIP automatically.

---

# FINAL RESPONSE

Return:

1. Git branch and pushed commit hashes.
2. New experiment path.
3. COMPLETE / PARTIAL / BLOCKED.
4. Two-seed visual AP comparison.
5. Uniform-fusion comparison.
6. F2 comparison.
7. OOF-versus-assessment finding.
8. Complementarity finding.
9. Cause-assessment table.
10. Actual runtime.
11. Paths to:
   - `README_FIRST.md`
   - `RESULTS_SUMMARY.md`
   - `REVIEW_PACKAGE.zip`

End with:

**Evidence checked:**  
specific code, fits, predictions and checks actually used.

**Still uncertain:**  
remaining hypotheses and seed/generalization limits.

**Defensible conclusion:**  
the strongest explanation actually supported by this controlled study, or `CAUSE_NOT_RESOLVED`.

Then STOP.

Do not automatically launch another architecture, corruption, external-dataset, or UI experiment.