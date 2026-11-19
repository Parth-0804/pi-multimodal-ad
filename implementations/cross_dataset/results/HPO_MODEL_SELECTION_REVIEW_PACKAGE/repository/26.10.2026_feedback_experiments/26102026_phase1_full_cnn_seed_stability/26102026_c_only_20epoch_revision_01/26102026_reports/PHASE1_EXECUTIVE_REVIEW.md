# C-only executive review — PARTIAL

Updated 2026-11-02T22:24:14.739534+00:00. User requested C only and explicitly selected20 epochs per fit.
The schedule is **3 seeds ×5 outer folds ×(4 inner fits +1 outer fit)=75 full-CNN fits**.
Pending B training and F2-B comparisons are removed. The one completed B fit is
preserved as prior work and excluded from this revised study.

Completed C fits: **22/75**. Current stage: C_ONLY_TRAINING_PREPARATION.
Measured completed-fit training GPU-hours: 110.191.
Recorded C child-process wall-hours, including retained/retried work: 124.513.
Remaining planning range: **13.87–16.18 days**, assuming continuous
single-T4 availability. This uses measured full-CNN speed and20–40% overhead;
other GPU workloads add calendar time. Removing inexpensive cached-head fits
does not halve the original CNN-dominated runtime.

Initialization, labels, exact live16 input, FP32, effective batch8, optimizer,
fixed normalization running moments, trainable CNN affine/convolution weights,
group partitions and training-only selection/calibration remain unchanged.
The cosine learning-rate horizon remains50 for all fits so the completed
prefix of the active CNN can resume exactly. The execution cap is20, with
checkpoint candidates1–20 and no patience stop before20.

| Task | Status |
|---|---|
| Historical/input/GPU and gradient audit | completed; original evidence reused |
| C training | partial; 22/75 |
| Three-seed stability | pending |
| F2-C,15 stackers with25 reused sensors | pending |
| B training/comparison | removed by user; completed artifacts preserved |
| Phase2/3 | outside this execution scope |

Scientific verdict: full-backbone trainability/input identity/recovery are supported by existing gates. New visual accuracy, fusion benefit and seed stability remain unknown until all held-out analyses complete. No superiority conclusion is drawn from GPU utilization.

Artifacts remain in the original Phase1 execution directory; C-only execution receipts, status and final metrics are under this revision. Original configurations and selected/checkpointed weights are preserved.
