# Asymmetric epoch-budget backbone study — RUNNING / INCOMPLETE

Common completely assessed outer folds: none. Only this four-condition intersection supplies the primary comparison. Unmatched frozen coverage is listed separately in `comparison/unmatched_coverage.json`. A one-fold result is a pilot; no statement extends to the unobserved folds.



| Condition | Epochs | Visual AP | Sensor AP | F2 AP | Common folds |
|---|---:|---:|---:|---:|---:|
| frozen_16_frames | 5 | — | — | — | 0/5 |
| fine_tuned_16_frames | 2 | — | — | — | 0/5 |
| frozen_32_frames | 5 | — | — | — | 0/5 |
| fine_tuned_32_frames | 2 | — | — | — | 0/5 |


AP is sklearn average_precision_score on directly keyed outer assessment predictions. Mean-fold AP, AUROC, fixed-threshold metrics and Brier scores are separate numerical tables.

No paired result yet.

Unmatched frozen reference, excluded from the four-condition comparison:

| Condition / fold | Epochs | Segments | Visual AP | Sensor AP | F2 AP |
|---|---:|---:|---:|---:|---:|
| frozen_16_frames / fold_01 | 5 | 753 | 0.200401 | 0.290531 | 0.307929 |


This is an asymmetric epoch-budget comparison: frozen heads use five epochs, final-stage plus head use exactly two joint epochs. It is not an equal-epoch/equal-compute fine-tuning isolation, convergence study, optimal architecture claim, robustness test or completion of unobserved folds. Recording-cluster bootstrap uncertainty conditions on these fitted models; one observed fold cannot establish variation across unobserved folds. One seed family; previously exposed REASSEMBLE cohort; fixed0.5 threshold. No outer scores select settings, stopping, folds or batching. Historical Task4 remains excluded. Review is self-review; independent review is outstanding.

Wall-time limit removed by the user's explicit amendment on 2026-10-21T07:34:32.050891+00:00. There is no training cutoff or hard deadline. Frozen16/32 retain five epochs; fine-tuned16/32 use exactly two joint epochs. Cumulative GPU/CPU/storage/fit/diagnostic limits remain unchanged. The old24h clock/config fields are preserved as historical checkpoint provenance; execution_policy.json records the effective policy.

Next decision: Review the checkpoint and remaining-cost evidence before authorizing another bounded continuation of this same amended protocol.
