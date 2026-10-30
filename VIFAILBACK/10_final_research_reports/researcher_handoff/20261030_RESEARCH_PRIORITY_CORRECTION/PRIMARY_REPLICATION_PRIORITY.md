# Primary research priority: original REASSEMBLE replication on ViFailback

Researcher correction received 2026-10-30. Applies to the interpretation and
presentation of run `20261029T004900Z`.

**Primary question: Does the original REASSEMBLE fusion approach demonstrate
comparable benefits when independently implemented and evaluated on ViFailback?**

This note records the researcher's priorities after the frozen-branch outer
predictions became available. It is a dated reporting clarification, not a new
prospective preregistration. The locked cohort, splits, models, fitting rules,
budgets, seeds and execution sequence remain unchanged. No running process was
interrupted and no completed result was discarded. Historical and automatically
published reports retain their original bytes and publication hashes. Read this
note alongside those reports when interpreting their broader Q1–Q12 framing.

## Primary replication components

| Priority | Component | Locked ViFailback implementation |
|---|---|---|
| 1 | Original pretrained frozen CNN | V1: original RT-DETR-derived ResNet18VD CNN, original pooling and head shape; a new target head trained for 100 epochs |
| 2 | Original static sensor Logistic Regression | S1 = S3: original ten statistics per observed channel, T-only standardization, balanced Logistic Regression C=1, max_iter=2000; separate unweighted sigmoid calibration on C |
| 3 | Fully fine-tuned CNN | V2: original pretrained initialization; all CNN convolution and normalization affine parameters plus the new head train for 100 executed epochs; original FrozenBatchNorm running moments remain fixed |
| 4 | Original probability averaging | F1: equal average of the calibrated visual and original S3 sensor probabilities |
| 5 | Original F2 fusion | Unweighted C=1 Logistic Regression on the two calibrated probabilities, freshly fitted from grouped inner out-of-fold predictions for each visual condition, outer fold and seed |
| 6 | Within-dataset F2 benefits, then cross-dataset consistency | Report ViFailback contrasts and verified REASSEMBLE contrasts separately before comparing their directions, magnitudes and uncertainty |
| 7 | Missing/degraded-modality robustness | Execute the existing fixed, label-blind stress protocol; report clean results first and distinguish programmed fallback from learned reliability adaptation |

The F2 formulation remains
`sigmoid(b + w_visual * p_visual + w_sensor * p_sensor)`.
It operates on probabilities, not concatenated feature vectors or branch logits.
F2 names the original fusion method; it is not the F-beta=2 metric. No source
head, calibration coefficients or F2 coefficients are reused on ViFailback.

The adapter imports the actual original functions through
`VIFAILBACK/src/vifailback/reference.py`. The original sensor, calibrator and
stacker implementations are in
`parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/fusion.py`.
Original statistical features and visual primitives are referenced in that
adapter and hash-pinned in the execution provenance. This is component reuse
with dataset-specific fitting, not an independently invented fusion method.

## Necessary dataset adaptations

- Prediction unit and target: one complete native action episode, failure=1 and
  success/no-failure=0. An outcome is not a frame-level failure annotation.
- Visual input: 16 label-blind, uniformly selected matching indices per camera
  from all three views, hence 48 RGB images at 16 times. Mean pooling across the
  three camera embeddings is an explicit extension of the source input.
  Spatial pooling yields 896 features; the original head shape is
  896 → 128, ReLU, dropout 0.1 → one logit. Weights of the target head are new.
- Numerical input: 14 position fields, 12 nonplaceholder velocity fields and
  two gripper-effort fields. The original ten-statistic routine gives 280
  features. These are not calibrated force/torque measurements. Commands,
  annotations, task IDs and source identities are excluded as ordinary inputs.
- Cohort: the same 4,382 technically eligible episodes for every primary model,
  with 3,753 failures and 629 no-failures across 99 canonical tasks. Existing
  exclusions remain fixed; visual weakness is not retrospectively filtered.
- Grouping: the existing three outer task-disjoint folds and three inner OOF
  partitions replace source-domain group identities. T/V/C/assessment tasks are
  disjoint. Standardization uses T, checkpoint selection uses V, calibration
  uses C, and F2 uses only inner held-out probabilities. All three fixed seeds
  (42, 123, 20261023) and all outer folds remain reported.
- Optimization and memory: the frozen 100-epoch schedules and validation
  selection rule remain intact. Exact frame-chunk recomputation accommodates
  the three-camera CNN input; it does not reduce frames or epochs. Selected
  checkpoints and final executed epochs are reported separately.

These adaptations preserve the original model family and fusion formulation.
They prevent describing the experiment as an exact reproduction of the source
dataset, sensors, acquisition system or evaluation units. Converted-clock
agreement does not establish physical hardware synchronization, and task
disjointness does not establish session/operator independence.

## Reporting order and comparisons

First report the ViFailback clean results, using identical held-out episodes:
V1 and V2 visual-only, S3 sensor-only, their F1 averages, and their F2 models.
Report both class APs, macro AP, prevalence and the locked complementary
discrimination, threshold and calibration metrics. Show every seed and fold.

For each visual condition, show F2 minus visual, F2 minus original S3, and F2
minus averaging. Show averaging against each component. Then show V2 minus V1
and F2(V2) minus F2(V1), keeping visual improvement and fusion improvement
distinct. These are reporting contrasts between existing predictions, not
additional fitting or model-selection rules. Preserve the locked paired
task-cluster bootstrap and its limitations; do not select a favorable seed,
fold, class, threshold, sensor branch or reference after inspecting outer tests.

Next report the corresponding verified **within-REASSEMBLE** differences from
saved source predictions, identifying the exact source run, class target,
prevalence, split units, training budget and checkpoint-selection procedure.
Only then discuss whether the original F2 benefits have similar direction and
size on ViFailback. Raw AP values across different class prevalences and tasks
are not a direct estimate of transferred benefit. Incomplete source studies,
selected single-run checkpoints and mismatched budgets must be disclosed;
they cannot stand in for a complete matched source comparison. No numerical
equivalence margin, pooled cross-dataset significance test or success criterion
is introduced by this correction.

Finally report the prespecified missing/degraded-modality scenarios and costs.
Include class-wise degradation, seed/fold variation, scored coverage and
both-missing abstention. Averaging, F2 and gates share the documented explicit
surviving-branch fallback. That fallback is not evidence of learned adaptation.
Quality-aware gates and their controls remain supplementary analyses of the
locked protocol; they do not replace original F2 as the primary replication.

## Preserved supplementary work and scheduling

HGB (S2) is an additional exploratory sensor baseline. Its completed predictions,
models, selection evidence and measured results remain preserved. HGB is not a
component of the original replication, and original F2 continues to use S3.
The completed HGB stage is not delaying the queue; this correction launches no
additional HGB fits, tuning or reruns. The existing F2-versus-HGB comparison
remains useful supplementary context, not a gate for reporting the replication.

V3 donor-weight transfer, the high-camera-only ablation, quality/static gates
and matched corruption-training controls also retain their existing results
and scheduled work. Their interpretation is supplementary to the primary
replication. The running controller is not reordered or restarted. The ongoing
REASSEMBLE 75-fit study keeps its existing GPU priority; ViFailback's full CNN
experiments wait for its verified completion and GPU availability.

## Evidence and current limits

Read [the frozen replication status](FROZEN_REPLICATION_STATUS.md) for the
currently measured within-ViFailback contrasts and the scope of their saved-
result check. Full CNN 100-epoch and robustness conclusions remain pending. A pipeline
completion flag alone will not answer the primary question, and a positive F2
difference against vision alone will not demonstrate improvement over sensors.

Authoritative unchanged artifacts, relative to repository root:

- `VIFAILBACK/configs/experiment.json`
- `VIFAILBACK/configs/protocol.json`
- `VIFAILBACK/10_final_research_reports/reproducibility/PROTOCOL_FREEZE.json`
- `VIFAILBACK/logs/20261029T004900Z/EXECUTION_PROVENANCE.json`
- `VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json`
- `VIFAILBACK/10_final_research_reports/LATEST_PUBLICATION.json`

Protocol SHA-256:
`497c7b53d360baead6a6654e7e72df9d8c36f83fb9bb93cd1294442405abc91b`.
Experiment configuration SHA-256:
`69f7bc1b6a82441c67bb84a9b83738daaf37b5869e4c90c6aeb482401eddb9c6`.
