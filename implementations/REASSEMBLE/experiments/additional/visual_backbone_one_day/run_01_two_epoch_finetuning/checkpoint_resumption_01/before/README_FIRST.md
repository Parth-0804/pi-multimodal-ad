# Two-epoch fine-tuning / five-epoch frozen backbone comparison

**PARTIAL**. Common completely assessed outer folds: none. Only this four-condition intersection supplies the primary comparison. Unmatched frozen coverage is listed separately in `comparison/unmatched_coverage.json`. A one-fold result is a pilot; no statement extends to the unobserved folds.

[Results](comparison/RESULTS_SUMMARY.md) · [Protocol amendment](protocol_amendment.md) · [Performance](performance_report.md) · [Progress](progress.json) · [Worker](worker_status.json) · [Focused checks](checks/focused_checks.json).

| Condition | Epochs | Visual AP | Sensor AP | F2 AP | Common folds |
|---|---:|---:|---:|---:|---:|
| frozen_16_frames | 5 | — | — | — | 0/5 |
| fine_tuned_16_frames | 2 | — | — | — | 0/5 |
| frozen_32_frames | 5 | — | — | — | 0/5 |
| fine_tuned_32_frames | 2 | — | — | — | 0/5 |


Fixed start: 2026-10-20T23:16:52+00:00 (2026-10-21T01:16:52+02:00 Berlin). Hard deadline: 2026-10-21T23:16:52+00:00 (2026-10-22T01:16:52+02:00 Berlin). Training cutoff: 2026-10-21T20:16:52+00:00; last three hours reserved for reporting. Time remaining at this document write: 17.95 h. Prior study elapsed is separate, not subtracted from this amendment clock.



Worker status: `STOPPED`; supervisor PID `106847`, worker PID `106854`. See `logs/amended_training.log`. Resume only via `bash 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/study.sh supervise`; it reuses the stable clock and rejects a second writer. No other machine, future schedule or new deadline is created. An existing STOP.json blocks resumption; preserve it as provenance and clear only after the recorded priority dependency has completed. Do not bypass it to run a competing writer.

This is an asymmetric epoch-budget comparison: frozen heads use five epochs, final-stage plus head use exactly two joint epochs. It is not an equal-epoch/equal-compute fine-tuning isolation, convergence study, optimal architecture claim, robustness test or completion of unobserved folds. Recording-cluster bootstrap uncertainty conditions on these fitted models; one observed fold cannot establish variation across unobserved folds. One seed family; previously exposed REASSEMBLE cohort; fixed0.5 threshold. No outer scores select settings, stopping, folds or batching. Historical Task4 remains excluded. Review is self-review; independent review is outstanding.

Single next decision after stopping: Review the checkpoint and remaining-cost evidence before authorizing another bounded continuation of this same amended protocol.
