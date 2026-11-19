# Full CNN training results — PARTIAL

Updated 2026-11-02T22:24:14.633024+00:00. 22/75 C fits complete. Each executes exactly20 epochs. Pending B fits:0.

| Seed | Fit | Executed | Selected | Training hours | Mean GPU compute |
|---|---:|---:|---:|---:|---:|
| 42 | 0 | 20 | 19 | 4.8230 | 99.32% |
| 42 | 1 | 20 | 16 | 5.1773 | 99.65% |
| 42 | 2 | 20 | 19 | 4.8120 | 99.63% |
| 42 | 3 | 20 | 17 | 5.1043 | 99.50% |
| 42 | 4 | 20 | 19 | 6.5715 | 99.55% |
| 42 | 5 | 20 | 19 | 4.7832 | 99.59% |
| 42 | 6 | 20 | 19 | 4.7925 | 99.61% |
| 42 | 7 | 20 | 20 | 4.6625 | 99.41% |
| 42 | 8 | 20 | 2 | 4.5438 | 99.59% |
| 42 | 9 | 20 | 20 | 6.0796 | 99.66% |
| 42 | 10 | 20 | 5 | 4.5587 | 99.54% |
| 42 | 11 | 20 | 19 | 4.5523 | 99.60% |
| 42 | 12 | 20 | 6 | 4.4629 | 99.61% |
| 42 | 13 | 20 | 8 | 4.4707 | 99.62% |
| 42 | 14 | 20 | 19 | 6.0727 | 99.68% |
| 42 | 15 | 20 | 17 | 4.6095 | 99.62% |
| 42 | 16 | 20 | 1 | 4.4530 | 99.61% |
| 42 | 17 | 20 | 20 | 5.0944 | 99.65% |
| 42 | 18 | 20 | 7 | 4.8744 | 99.65% |
| 42 | 19 | 20 | 20 | 6.2074 | 99.68% |
| 42 | 20 | 20 | 9 | 4.5850 | 97.61% |
| 42 | 21 | 20 | 6 | 4.9003 | 99.63% |

The original per-fit folders retain every epoch loss, validation AP/AUROC, LR, time, VRAM, CPU memory, sampler hash, GPU telemetry, best model and two recovery generations. Checkpoint selection may precede20 even though20 epochs execute. Learning-curve JSON and PNG are retained per completed fit. Decreasing training loss with worsening validation AP is compatible with overfitting; an earlier selected checkpoint does not demonstrate a benefit from extra exposure.
