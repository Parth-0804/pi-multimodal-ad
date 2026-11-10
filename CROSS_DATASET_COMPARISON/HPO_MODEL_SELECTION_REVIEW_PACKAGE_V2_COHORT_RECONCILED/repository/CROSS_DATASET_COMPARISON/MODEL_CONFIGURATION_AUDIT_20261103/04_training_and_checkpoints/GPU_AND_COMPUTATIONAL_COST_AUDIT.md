# GPU and computational cost audit

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

Historical100-epoch provenance records **one NVIDIA Tesla T4,16,384MiB,driver580.167.08**. A metadata-only end snapshot again shows that visible device with0MiB allocated and0% compute activity. The audit made zero GPU allocations and did not use any other user's job/device. Visibility alone is not a general proof of allocation entitlement; the historical report records the study's single-T4 allocation.

| Scope | Measured training hours | Measured validation hours | Interpretation |
|---|---|---|---|
|25 C20 fits |126.231610656|9.555842562|Sum of per-fit measured processing times;excludes unrecorded allocation/downtime/extraction |
| B100 cached head |0.060992387|0.001820982|CNN feature extraction excluded |
| C100 full CNN |23.964191181|1.629114685|Separate inference/calibration0.062891223h |
|72 Vi frozen heads |NOT SEPARATELY RECORDED|NOT SEPARATELY RECORDED|Combined training+validation sum0.490804938h;cached feature extraction excluded |

The paired100-epoch active-child process attempts sum to25.89373 wall hours (C-only25.81836h),not pure C training or GPU kernel time. Calendar duration includes gaps and can be longer. A complete historical global GPU-job-hours total is NOT RECORDED; adding overlapping categories or treating all CPU fitting time as GPU-hours would be misleading.

C100 mean sampled TRAINING compute activity is99.713245%,with peak allocated VRAM7.770030499GiB. B100 cached-head training averages21.4613% activity and peak allocated0.080301GiB. Memory fraction and compute activity are different quantities. Per-epoch averaging is not a time-integrated kernel-busy counter; maximum reserved VRAM and exact kernel compute-hours remain NOT RECORDED. This audit ran no utilization benchmark.

TRAINING_DURATION_AND_GPU_USAGE.csv retains every available run-level timing,epoch duration,actions/second,update count,effective batch and memory/activity value. Unknown extraction/resource fields remain explicit. C20/100-epoch repeats across additional seeds/folds would be expensive,but this audit does not select a future compute budget. Reproducibility and assessment design must precede any authorization.

## Evidence anchors

- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_evidence/PHASE1_COMPARISON_PROVENANCE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_evidence/PHASE1_COMPARISON_PROVENANCE.json) — recorded GPU identity.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_reports/PHASE1_GPU_INTEGRATION.md](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_reports/PHASE1_GPU_INTEGRATION.md) — allocated single-T4 report and historical planning estimate.
