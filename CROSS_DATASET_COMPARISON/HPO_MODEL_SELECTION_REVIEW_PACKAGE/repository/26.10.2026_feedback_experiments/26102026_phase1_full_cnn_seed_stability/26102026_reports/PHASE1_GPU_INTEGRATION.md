# Phase 1 GPU integration — verification complete

Updated 2026-10-26T23:04:53.242540+00:00. The fully trainable CNN performance gate passed. This is a
bounded training-side pilot, not a completed full-cohort epoch or experiment.

One allocated NVIDIA Tesla T4, 16 GB nominal VRAM, driver 580.167.08, CUDA driver
13.0, PyTorch 2.13.0+cu130, cuDNN 9.2; 16 available EPYC CPU cores and about
62.7 GiB system RAM. The exact hardware/software snapshots are in
`../26102026_execution/26102026_main_run_01/26102026_full_cnn_preflight_01/PHASE1_PREFLIGHT_PROVENANCE.json`.
GPU compute utilization below is sampled kernel-busy percentage. It measures
neither VRAM occupancy nor percentage of peak FLOPS.

| Measurement | Earlier optimized pilot | New fully trainable CNN pilot |
|---|---:|---:|
| Executed gradient scope | Final CNN stage and head | All executed CNN convolutions, normalization affine parameters, head |
| Precision | FP32 | FP32 |
| Sustained GPU compute utilization | 97.9% | 94.06% |
| Actions/second | 6.637 | 1.9253 |
| Projected 2,966-action training epoch | 7.45 minutes | 25.68 minutes |
| Peak process VRAM | About 4.15 GiB | 8.772 GiB |
| Peak tensor allocation | Different gradient scope | 7.768 GiB |

The columns have different computation and gradient coverage. They are not a
matched speedup comparison. Historical 18–20% utilization reflected input
starvation in the previous workload; the original report isolates decoding,
CPU preprocessing, decoder thread proliferation and loader stalls. Its earlier
serial live32 diagnostic was unstable and is not a valid selected baseline.
The original report and all benchmark evidence remain unchanged.

| Full-CNN window | Seconds | Actions | Actions/s | Updates/s | GPU compute | CPU loading wait | CUDA forward/backward time |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62.06 | 120 | 1.9336 | 0.2417 | 93.77% | 3.650s | 57.569s |
| 2 | 62.59 | 120 | 1.9171 | 0.2396 | 94.36% | 3.751s | 58.017s |

Both windows exclude worker/model initialization and checkpoint writes and
follow two warm-up passes. Their training-side subset contains 24 actions;
full-cohort sustained performance is recorded separately per executed epoch.
About 6% of measured wall time was spent waiting for input, and CUDA work
occupied about 93% of wall time. These components overlap. The new dominant
cost is full forward/backward computation. There is no measured reason to
repeat the previous worker grid, increase effective batch size, or change
precision. Native BF16 is unavailable; FP16 and torch.compile are not enabled
or claimed equivalent. This preserves the validated FP32 scientific protocol.

The selected configuration uses exact whole-action 16-frame decoding, FFmpeg
two threads/video, four persistent workers, prefetch two, pinned memory and
nonblocking device transfer. Sixteen frames are batched in one CNN call per
action; eight actions are accumulated per update. The final partial group is
scaled by its actual number of actions. CPU thread limits prevent oversubscription.
No DDP is configured on the single allocated GPU. Independent fits run
sequentially; the controller waits when another GPU workload is detected.

All 4,530 actions from 148 recordings (509 failure targets) passed exact
selected-frame identity, dimensions, dtype, label/timestamp and recording
association validation. All 16 frames match the intended original FP32 input
reconstruction and uniform whole-action policy; no last-quarter substitution.
See `../26102026_evidence/PHASE1_INPUT_VERIFICATION_STATUS.json` and its manifest.

The real-CNN pilot verifies finite gradients for every intended parameter,
nonzero early/middle/final-stage and head gradients, actual updates in every
CNN stage, fixed running moments, identical resumed model/optimizer/scheduler/
RNG and epoch order, exact sample counts, and saved-model reload predictions.
Frozen normalization affine buffers become trainable parameters while their
forward formula and running moments remain unchanged. No detector decoder,
attention or proposal modules are executed. Cooperative shutdown records show
zero worker exit codes after complete, resumed and short prediction iterations.
Synthetic regressions also cover early exceptions and an interrupted selected-
checkpoint replacement before epoch commit. The latter retains selected
weights inside both resumable generations so recovery cannot select an
uncommitted future checkpoint.

`PHASE1_PREFLIGHT_SOURCE_RECONCILIATION.json` links all eight exact pilot source
files to their recorded hashes and retained copies. Model, loader, metric and
pilot source are unchanged. Subsequent crash-selection recovery, telemetry and
action-association checks are explicit additions covered by the final tests.

Measured full-CNN computation projects 495.3–
990.7 training GPU-hours
for 75 full-CNN fits at 25–50 epochs. A planning allowance for validation,
calibration, loader starts, checkpointing and 75 small frozen-head fits gives
**594–1387 GPU-job hours, approximately 24.8–57.8 days**
of exclusive single-T4 availability. This is a planning range, not measured
total runtime; early stopping, full-cohort locality and competing workloads
change the calendar duration. Actual completed training and GPU-job wall-hours
are updated in the executive report and controller status.

Evidence: `PHASE1_FULL_CNN_BENCHMARK.json`, `PHASE1_FULL_CNN_GATE.json`,
`PHASE1_FULL_CNN_GRADIENT_EVIDENCE.json`, `PHASE1_FULL_CNN_RESUME.json`,
`PHASE1_FULL_CNN_RELOAD.json`, and per-epoch telemetry under the new execution
directory. The old audit gate remains untouched; the new full-CNN gate is
specific to this newly authorized protocol.

## First actual full-cohort training pass

The first C fit (seed42, outer1/inner1) committed epoch1: 1753 actions, 220 optimizer updates, 14.82 training minutes, 1.62 validation minutes, 1.9720 actions/s and 96.67% mean GPU kernel-busy utilization. These whole-pass timings include first loader startup; validation and checkpointing are separate. Total epoch wall time including checkpointing was 16.46 minutes.

All 11,199,968 CNN parameters and 114,945 head parameters are trainable; all 73 intended parameter/state entries changed and running moments stayed fixed. The committed checkpoint hash was verified. See `../26102026_evidence/PHASE1_FIRST_COMPLETE_CNN_EPOCH.json`. This is one epoch of an active fit, not final experimental evidence.
