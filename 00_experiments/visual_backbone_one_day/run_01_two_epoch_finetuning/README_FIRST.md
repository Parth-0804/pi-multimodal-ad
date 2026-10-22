# Two-epoch fine-tuning / five-epoch frozen backbone comparison

**COMPLETE**. All five outer folds are completely assessed for every condition, using the same 4,530 held-out segments. All 100 visual fits and 20 condition/fold assessments are complete.

[Results](comparison/RESULTS_SUMMARY.md) · [Findings and limitations](comparison/FINAL_INTERPRETATION.md) · [Verified review ZIP](REVIEW_PACKAGE.zip) · [Protocol amendment](protocol_amendment.md) · [Performance](performance_report.md) · [Progress](progress.json) · [Worker](worker_status.json) · [Focused checks](checks/focused_checks.json).

| Condition | Epochs | Visual AP | Sensor AP | F2 AP | Common folds |
|---|---:|---:|---:|---:|---:|
| frozen_16_frames | 5 | 0.221644 | 0.420803 | 0.440680 | 5/5 |
| fine_tuned_16_frames | 2 | 0.224466 | 0.420803 | 0.437521 | 5/5 |
| frozen_32_frames | 5 | 0.219427 | 0.420803 | 0.439584 | 5/5 |
| fine_tuned_32_frames | 2 | 0.230609 | 0.420803 | 0.438566 | 5/5 |


Wall-time limit removed by the user's explicit amendment on 2026-10-21T07:34:32.050891+00:00. There is no training cutoff or hard deadline. Frozen16/32 retain five epochs; fine-tuned16/32 use exactly two joint epochs. Cumulative GPU/CPU/storage/fit/diagnostic limits remain unchanged. The old24h clock/config fields are preserved as historical checkpoint provenance; execution_policy.json records the effective policy.



Worker status: `STOPPED`; supervisor PID `111461`, worker PID `111468`. See `logs/amended_training.log`. Resume only via `bash 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/study.sh supervise`; it reuses the stable clock and rejects a second writer. No other machine, future schedule or new deadline is created. An existing STOP.json blocks resumption; preserve it as provenance and clear only after the recorded priority dependency has completed. Do not bypass it to run a competing writer.

This is an asymmetric epoch-budget comparison: frozen heads use five epochs, final-stage plus head use exactly two joint epochs. It is not an equal-epoch/equal-compute fine-tuning isolation, convergence study, optimal architecture claim, robustness test or completion of unobserved folds. Recording-cluster bootstrap uncertainty conditions on these fitted models; one observed fold cannot establish variation across unobserved folds. One seed family; previously exposed REASSEMBLE cohort; fixed0.5 threshold. No outer scores select settings, stopping, folds or batching. Historical Task4 remains excluded. Review is self-review; independent review is outstanding.

Single next decision after stopping: Review the completed matched evidence before authorizing any additional scientific change.
