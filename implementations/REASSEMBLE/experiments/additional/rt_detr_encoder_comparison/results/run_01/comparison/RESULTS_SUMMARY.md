# Completed findings

The hybrid-encoder representation reduced pooled visual AP by 0.049729 and F2 AP by 0.015785 relative to CNN-only on 4,530 actions, 509 failures and 148 recordings. The paired recording-bootstrap 95% interval for the F2 difference is [-0.024804, -0.005800]; all 2,000 replicates were valid. This supports CNN-only under this fixed protocol, without establishing that attention or transformers are generally unhelpful.

| Condition | Visual AP | Sensor AP | F2 AP | Paired folds | Heads new / reused |
|---|---:|---:|---:|---:|---:|
| cnn_only | 0.221644 | 0.420926 | 0.440764 | 5 | 20 / 5 |
| cnn_plus_encoder | 0.171915 | 0.420926 | 0.424979 | 5 | 25 / 0 |

All five matched folds completed. The 16 input frames were identical across conditions. Extractor weights and buffers stayed frozen; runtime traces show encoder projections, attention, FPN and PAN executing only on the encoder path. Guards excluded detector, proposal and decoder execution. Ten outer-condition saved-model replay checks passed on three identified actions each, using live pixels and cached sensor statistics. Cached-head probabilities were also replayed from saved components. This is not a claim that all actions were decoded a second time.

New encoder extraction took 71.00 minutes including decoding; its recorded compute time was 883.14 seconds. Training-only extractor benchmarks were 0.121970 seconds/action for CNN-only and 0.192610 seconds/action with the encoder, excluding decoding. Active frozen parameters were 11,190,112 versus 16,155,232; head parameters were 114,945 versus 98,561. This compares complete representations with different feature widths and compute, not isolated attention or matched capacity. New head fitting totalled 675.26 seconds. See `comparison/costs.csv`, `comparison/execution_cost.json`, and the resource observations for details.

Reuse: all compatible CNN feature rows and five CNN heads; five sensor fits were reused, with 20 sensor fits newly fitted. Forty-five visual heads and ten F2 stackers were newly fitted. No extractor fine-tuning occurred. No scientific extraction/fitting failure remains unresolved. Earlier resource-wait records are historical; the user later explicitly authorized checkpoint-pausing the separate visual study.

Uncertainty: the intervals condition on one fitted seed family and this exposed cohort. Secondary contrasts are exploratory; no external validation, temporal modelling, or robustness conclusion follows from this encoder comparison. The separately authorized noise study makes its own pre-noise choice on the fixed eligible common coverage.

Recommended next decision: require complete matched coverage and independent validation before adopting a different visual representation.

# Encoder comparison — COMPLETE

| Condition | Visual AP | Sensor AP | F2 AP | Paired folds | Fit status |
|---|---:|---:|---:|---:|---|
| cnn_only | 0.221644 | 0.420926 | 0.440764 | 5 | NEW+REUSED+NEW |
| cnn_plus_encoder | 0.171915 | 0.420926 | 0.424979 | 5 | NEW |

Pooled AP is computed from identical directly keyed outer rows, separately from fold APs. The paired intervals are conditional on this exposed dataset and one fitted seed family; secondary contrasts are exploratory and unadjusted.

Failure is positive (1), success negative (0); AP uses sklearn average_precision_score, not trapezoidal PR area. Threshold is fixed .5. Only identically completed paired folds enter these tables. One fold is an incomplete pilot.

## Evidence and interpretation

Real training-only extraction/preflight evidence is in checks/real_extractor_preflight.json; each completed outer fit includes a full saved-model replay.

Source inspection, synthetic tests, original-weight CPU path checks, real extraction/training, replay and statistical conclusions are distinct evidence levels. Inspect checks for which actually ran. Reference-only inherited tables, if available, are under `data/reference_only`; their origin hashes and cached CPU replay are in `checks/reference_cached_CPU_replay.json`. They are not paired comparison outputs and do not establish encoder performance. The source calls backbone -> encoder projections -> hybrid encoder final PAN maps, ending before decoder projections or proposals. The two heads share the 128-unit family but can differ in parameter count due to feature width. This tests the complete hybrid representation pipeline, not attention alone, full detection, temporal modelling, robustness or real-time operation.

## Review and independent recalculation

`comparison/identified_outer_predictions_cnn_only.csv` and `comparison/identified_outer_predictions_cnn_plus_encoder.csv` are emitted only when paired folds actually complete; absence means NOT_RUN. Recalculate with `ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py evaluate`. Per-fit inner predictions and the assembled OOF probabilities are under each condition's fold folder. `data/memberships` records direct G/C/T and prediction keys plus E recording IDs.

Reliability uses 10 fixed equal-width bins (last includes 1), plotting mean prediction versus empirical failure frequency. Changed predictions are outcome-selected log-loss illustrations, tied by sample keys, not independent explanatory evidence.

## Walkthrough

Input: exact same 16 hand-camera images per action. Image representation: frozen independent-image CNN or CNN/projections/hybrid encoder, per-scale spatial means then frame mean. Partition-specific head: G-only standardization and training, C-only branch calibration. Two branch probabilities: calibrated visual and identical sensor reference. F2: outer-training held-inner probabilities fit a static C=1 logistic stacker. Held-out evaluation: apply the separately calibrated outer branches and stacker to E. Bounded conclusion: only this fixed completed-action protocol is tested.

## Incomplete work / limits

Current stage: COMPLETE. Blocker: None. No queued job or background continuation exists. Deadline includes waiting, all stages, and reporting; the resume command cannot renew it. No unsupported metric is substituted from historical anonymous results.

Evidence checked: see actual test and runtime records. Still uncertain: seed-to-seed variability, unseen recordings and external generalization. Defensible conclusion: interpret only the paired completed rows under the stated protocol.


Requested visual-study continuation: the existing supervisor was launched after both studies and their ZIPs completed. Worker 106854 stopped with `COMPLETE_OUTER_CYCLE_NOT_ADMITTED` (exit 75): estimated remaining outer-cycle cost 68,884.2 s (19.13 h), versus 53,835.7 s (14.95 h) before the original reporting reserve. The paused checkpoint is unchanged (453 updates, 3,621 rows seen); no new training updates ran. The visual study is **not running**. Its original training cutoff remains 2026-10-21 20:16:52 UTC and final deadline 23:16:52 UTC. No restart is scheduled. See `provenance/visual_resume_receipt.json` (relative to this run root). Continuing requires a separately approved budget/protocol amendment; neither completed study was changed.
