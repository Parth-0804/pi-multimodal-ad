# Boundary-aware visual pooling handoff

**EXPLORATORY — TEMPORAL STRUCTURE HELPS**

## A. Motivation from human review

Aggregate motivation only: 59/64 judgeable, 57/59 agreement among determinate judgements, 5 indeterminate, two disagreements. Ambiguity was more common among recorded failure cases. Human identities/ratings/flags did not enter any fit, fold, feature, threshold or selection. No adjudication or relabeling is implied.

## B. Hypothesis

Whole-segment averaging may dilute signals concentrated early/late. This concerns retrospective completed-action classification, not prediction before failure.

## C. Historical control reproduction

{
  "passed": true,
  "metric_max_abs": 0.0,
  "max_probability_difference": 0.0,
  "historical_metrics": [
    0.6977948286232056,
    0.23065831504271656,
    0.6414118119557979,
    0.515284068299497,
    0.6620825147347741,
    0.18098818474758324,
    0.09429877740531123,
    0.00701712390925374
  ],
  "reproduced_metrics": [
    0.6977948286232056,
    0.23065831504271656,
    0.6414118119557979,
    0.515284068299497,
    0.6620825147347741,
    0.18098818474758324,
    0.09429877740531123,
    0.00701712390925374
  ],
  "probability_tolerance": 1e-05
}

## D. Temporal aggregation variants

| Variant | Definition | Trainable parameters |
| --- | --- | --- |
| V0 | Full-segment mean | 114945 |
| V1 | First half + second half | 115073 |
| V2 | Early + middle + late | 115201 |
| V3 | Last quarter only | 114945 |
| V4 | Early + late | 115073 |
| V5 | Ordered GRU64 + fixed positions | 82433 |


## E. Parameter/training fairness

V0 uses the exact original head/fitter and historical pooled features. V1–V4 use shared 896→128 projection per temporal bin, then concatenate small projected bins; classifier increases by at most 256 weights. All use training-only whole-segment mean moments, weighted BCE, AdamW .001/decay .001, batch128, dropout .1, clipping1. V5 is exactly one GRU64 layer with fixed sinusoidal position, 64-D projection and mean recurrent-output pooling; its inductive bias/capacity differ, so no pure order-causality claim. Fixed epoch grids: V0–V4 [5,10], V5 [5,10,20], mean inner AP selection. Historical single-seed policy retained, with original fold-specific offsets; no three-seed robustness claim. Inner loss histories and AP at candidate budgets, selected/refit checkpoints and predictions are retained under fits/ and branches/.

## F. Main metrics

| Variant | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V0 | 0.6978 [0.6716, 0.7232] | 0.2307 [0.1983, 0.2701] | 0.6414 [0.6175, 0.6658] | 0.5153 [0.4956, 0.5355] | 0.6621 [0.6149, 0.7075] | 0.1810 [0.1617, 0.2013] | 0.0943 [0.0862, 0.1028] | 0.0070 [0.0057, 0.0184] |
| V1 | 0.7119 [0.6874, 0.7374] | 0.2556 [0.2225, 0.2959] | 0.6500 [0.6269, 0.6728] | 0.5162 [0.5001, 0.5338] | 0.6857 [0.6373, 0.7317] | 0.1837 [0.1654, 0.2038] | 0.0930 [0.0850, 0.1014] | 0.0070 [0.0059, 0.0182] |
| V2 | 0.7668 [0.7452, 0.7889] | 0.3080 [0.2729, 0.3493] | 0.6981 [0.6776, 0.7178] | 0.5465 [0.5295, 0.5626] | 0.7583 [0.7201, 0.7963] | 0.2096 [0.1897, 0.2300] | 0.0891 [0.0813, 0.0970] | 0.0093 [0.0074, 0.0206] |
| V3 | 0.7728 [0.7519, 0.7932] | 0.3191 [0.2799, 0.3635] | 0.7005 [0.6799, 0.7200] | 0.5574 [0.5411, 0.5738] | 0.7407 [0.6968, 0.7825] | 0.2163 [0.1944, 0.2388] | 0.0884 [0.0806, 0.0969] | 0.0139 [0.0104, 0.0254] |
| V4 | 0.7547 [0.7364, 0.7733] | 0.2922 [0.2570, 0.3322] | 0.6845 [0.6639, 0.7042] | 0.5229 [0.5063, 0.5397] | 0.7721 [0.7308, 0.8112] | 0.1951 [0.1752, 0.2152] | 0.0905 [0.0827, 0.0985] | 0.0146 [0.0104, 0.0250] |
| V5 | 0.7167 [0.6924, 0.7395] | 0.2250 [0.1991, 0.2578] | 0.6525 [0.6293, 0.6738] | 0.4997 [0.4828, 0.5159] | 0.7328 [0.6869, 0.7743] | 0.1782 [0.1605, 0.1964] | 0.0940 [0.0858, 0.1026] | 0.0130 [0.0085, 0.0232] |


## G. Paired comparisons

| Variant − V0 | Δ AUROC (95%) | Δ AUPRC (95%) | AP simultaneous lower |
| --- | --- | --- | --- |
| V1 | 0.0141 [-0.0040, 0.0329] | 0.0249 [-0.0045, 0.0499] | -0.0118 |
| V2 | 0.0690 [0.0471, 0.0906] | 0.0774 [0.0415, 0.1106] | 0.0306 |
| V3 | 0.0750 [0.0518, 0.0972] | 0.0885 [0.0424, 0.1293] | 0.0301 |
| V4 | 0.0569 [0.0351, 0.0785] | 0.0616 [0.0272, 0.0943] | 0.0177 |
| V5 | 0.0189 [-0.0012, 0.0387] | -0.0056 [-0.0345, 0.0212] | -0.0425 |

Bonferroni percentile intervals for five AP contrasts, quantiles .005/.995; AUROC noninferiority uses marginal 95% lower > -0.01. Same-cohort exploratory selection remains.
Fold-level and historical-single-seed results are in fold_metrics.csv and seed_metrics.csv. Intervals condition on fits and do not include refitting or independent-site uncertainty.

## H. Action-level analysis

| Variant | Action | n | Failures | AUROC | AUPRC |
| --- | --- | --- | --- | --- | --- |
| V0 | pick | 1190 | 98 | 0.5973 | 0.1181 |
| V0 | insert | 1156 | 243 | 0.6082 | 0.3107 |
| V0 | remove | 1096 | 146 | 0.5959 | 0.1790 |
| V0 | place | 1088 | 22 | 0.7423 | 0.2453 |
| V3 | pick | 1190 | 98 | 0.8178 | 0.3595 |
| V3 | insert | 1156 | 243 | 0.6355 | 0.3464 |
| V3 | remove | 1096 | 146 | 0.6915 | 0.2880 |
| V3 | place | 1088 | 22 | 0.8014 | 0.2788 |

V0 and the highest pooled-AP temporal variant only; descriptive, not action-specific model selection.

## I. Failure-side rescue analysis

{
  "variant": "V3",
  "V0_false_negatives": 172,
  "variant_false_negatives": 132,
  "rescued_failures": 93,
  "lost_failures": 53,
  "recordings_with_rescue": 62,
  "recordings_with_loss": 36
}
Per-recording counts are in failure_rescue_by_recording.csv. No cross-reference to human-reviewed IDs. Failure recall/precision for all variants appear in main metrics.

## J. Selective-prediction diagnostic

All six models: selective_metrics.csv. Nominal coverage100/90/80%; confidence=|p−0.5|. Cutoffs use outer-training calibrated selected inner-OOF predictions; ties retained. Actual outer coverage can differ. Calibrator/selection uses those training rows, so inner coverage estimates are not unbiased. AUROC/AP and failure recall are reported on retained rows; additional overall failure recall counts abstentions as misses. Abstention is a computational decision, not a human uncertainty label. No claim that it detects the human-reviewed ambiguous clips.

## K. Fusion follow-up, if triggered

Exactly one static Section1B stacker follow-up triggered for V3. Sensor calibrated probabilities and exact original nested partitions are reused with verified identity. Visual sub-inner selection/refits exclude meta-assessment recordings. Original F2 parity checked before comparing.
| Metric | New − original F2 |
| --- | --- |
| AUROC | 0.0403 [0.0291, 0.0522] |
| AUPRC | 0.0461 [0.0260, 0.0632] |


## L. Failed variants

Every variant is retained above, including deterioration and unresolved differences. Runtime failures retained: none. No budgets expanded, architectures added or losing result hidden.

## M. Interpretation

TEMPORAL STRUCTURE HELPS. Class A uses multiplicity-adjusted positive AP lower bound and marginal AUROC lower >−.01. Sole qualifying last-quarter improvement is class C. B includes gains unresolved after multiplicity. These are bounded operational classifications, not universal architecture statements.

## N. Exact thesis-safe claim

In this separate exploratory study on the same 4,530 segments and recording-disjoint folds, the predeclared temporal-aggregation comparison was classified as TEMPORAL STRUCTURE HELPS. The highest pooled AUPRC point estimate among temporal variants was V3; this descriptive selection is not independent confirmation.

## O. Claims not supported

No prospective warning, physical-event timing accuracy, corrected labels, independently confirmed winner, universal temporal superiority, generalization to unseen objects/sites, validation from reviewer IDs, adaptive gate improvement or audio claim.

## P. Limitations

Same cohort already examined in completed studies and additional improvements; hypothesis/variants declared before this follow-up’s outcomes, but this is not an independent prospective validation set. The human review is a small balanced qualitative sample. One historical seed; shared scene/day dependence may remain beyond recording groups. More bins preserve both temporal location and extra information, and V5 changes the head family; no causal mechanism attribution. Limited budgets may underfit. GPU-compatible runtime must reproduce historical control. Additional trainable projections introduce a small documented capacity difference.

## Q. Provenance

Run: `runs/reassemble/additional_improvements_executed/20260929T162710Z/boundary_aware_visual`. Exact request: REQUEST.md; config.json; protocol.md; source_signature.json; source/; runtime.json; cache_preflight.json; cohort_identity.csv; control_*parity.json; preservation_before/after.json; output_manifest.json. Historical evidence/source config identities in registration.json. Historical V0 uses frozen mean values (CUDA temporal reduction); cached sequence NumPy re-averaging is checked at existing feature tolerance5e−5, avoiding an unannounced floating-point change to the control. No re-extraction. Raw preservation verifies size/mtime and known audited hashes/timestamps, not a new full HDF5 payload hash. Existing additional-run snapshot begins only after Task4 completes, so its authorized ongoing progress is not mistaken for our modification.

## R. Recommended thesis placement

Place in an explicitly exploratory follow-up subsection after the frozen core findings and human-review limitations. Keep the completed core results unchanged. Describe the single conditional static-fusion comparison with the same-cohort selection caveat.
