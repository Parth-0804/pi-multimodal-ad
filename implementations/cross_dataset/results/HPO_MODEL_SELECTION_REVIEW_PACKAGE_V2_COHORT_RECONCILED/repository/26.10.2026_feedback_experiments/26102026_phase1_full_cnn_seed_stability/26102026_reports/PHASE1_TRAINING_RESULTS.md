# Phase 1 training results — PARTIAL — training in progress

Updated 2026-10-27T01:41:39.752574+00:00. Completed 1/150 required fits.

| Model | Seed | Outer fold | Role | Executed epochs | Selected epoch | Training hours |
|---|---:|---:|---|---:|---:|---:|
| B_long_frozen16 | 42 | 1 | inner_fold_01 | 25 | 9 | 0.0155 |

## Completed-fit convergence observations

| Model | Seed | Fit | First→last training BCE | Selected→last validation AP | Mean GPU compute | Mean actions/s | Peak allocated GiB |
|---|---:|---:|---|---|---:|---:|---:|
| B_long_frozen16 | 42 | 0 | 1.7306→0.0386 | 0.2365→0.2137 | 21.30% | 790.156 | 0.080 |

Decreasing training loss accompanied by lower final validation AP is evidence compatible with overfitting; it is not proof of its cause. An early selected checkpoint shows that longer execution alone was not beneficial. Reaching50 epochs is a budget boundary, not evidence of convergence or superiority. Numerical failures are reported separately and never counted as valid poor accuracy. Every completed fit has exportable learning-curve PNG and JSON.

Every fit retains loss/AP/AUROC/LR/time/VRAM/utilization curves in PHASE1_LEARNING_CURVE.json and per-epoch telemetry. Selected checkpoints can precede the minimum25 executed epochs. Incomplete epochs are not counted as completed scientific exposure. Numerical failures are not valid negative accuracy results.
