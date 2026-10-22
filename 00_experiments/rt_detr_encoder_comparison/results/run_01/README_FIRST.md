# COMPLETE — five paired folds

CNN-only performed better on the fixed clean-input comparison: 4,530 actions, 509 failures, 148 recordings, identical 16-frame inputs. Encoder-minus-CNN fused AP was −0.015785 (paired recording-bootstrap 95% interval [−0.024804, −0.005800]; 2,000 valid resamples).

| Condition | Visual AP | Sensor AP | F2 AP | Paired folds | Heads new / reused |
|---|---:|---:|---:|---:|---:|
| cnn_only | 0.221644 | 0.420926 | 0.440764 | 5 | 20 / 5 |
| cnn_plus_encoder | 0.171915 | 0.420926 | 0.424979 | 5 | 25 / 0 |

Extractor weights stayed frozen. Runtime traces verified encoder attention/cross-scale execution and guarded the decoder/proposal paths. All ten outer-condition replay checks passed on three identified actions each. Thirty-six pooled/per-fold AP values were independently recalculated. No scientific stage remains incomplete.

Costs: 71.00 minutes for new encoder extraction including decoding; compatible CNN features were reused. Detailed compute, head capacity, fit reuse and timings are in the results and cost tables.

Review: [Results](comparison/RESULTS_SUMMARY.md), [metrics](comparison/metrics.csv), [paired intervals](comparison/paired_comparisons.csv), [CNN predictions](comparison/identified_outer_predictions_cnn_only.csv), [encoder predictions](comparison/identified_outer_predictions_cnn_plus_encoder.csv), [review package](REVIEW_PACKAGE.zip).

Limits: one fitted seed family, exposed data, unequal feature widths/compute, and no external validation. Recommended next decision: require full matched coverage and independent validation before adopting a different representation.

Evidence checked: real extraction, frozen-state guards, fits, saved-state replay and independently recalculated AP. Still uncertain: generalization and training variability. Defensible conclusion: CNN-only performed better on this fixed clean-input comparison.


Requested visual-study continuation: the existing supervisor was launched after both studies and their ZIPs completed. Worker 106854 stopped with `COMPLETE_OUTER_CYCLE_NOT_ADMITTED` (exit 75): estimated remaining outer-cycle cost 68,884.2 s (19.13 h), versus 53,835.7 s (14.95 h) before the original reporting reserve. The paused checkpoint is unchanged (453 updates, 3,621 rows seen); no new training updates ran. The visual study is **not running**. Its original training cutoff remains 2026-10-21 20:16:52 UTC and final deadline 23:16:52 UTC. No restart is scheduled. See `provenance/visual_resume_receipt.json` (relative to this run root). Continuing requires a separately approved budget/protocol amendment; neither completed study was changed.
