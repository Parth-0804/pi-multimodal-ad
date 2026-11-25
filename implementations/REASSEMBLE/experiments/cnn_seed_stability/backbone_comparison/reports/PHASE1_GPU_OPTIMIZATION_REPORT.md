# GPU performance evidence for the 100-epoch comparison

This follow-up reuses the completed Phase 1 GPU audit and unchanged numerical training engine. The original audit report and benchmark artifacts are preserved. New 100-epoch utilization, throughput, epoch durations and actual GPU job hours update automatically in [the comparison report](PHASE1_100EPOCH_COMPARISON_REPORT.md).

## Hardware and allocation

One allocated NVIDIA Tesla T4, 16 GB nominal VRAM, driver 580.167.08; the installed PyTorch 2.13 CUDA 13.0 build is recorded in the comparison provenance. The host exposes 16 CPU cores and about 62.7 GiB RAM. Approximately 70.7 GiB disk space remained at launch; the controller requires at least 10 GiB free. There is no second allocated GPU to use. Jobs run sequentially under a shared single-writer lock; other GPU workloads are waited out and never terminated.

## Existing measured performance and bottleneck

The previously reported 18–20% utilization is a user-reported historical figure without a matching original profiler trace. It cannot be presented as a reproduced benchmark. The audit identified serial CPU loading/preprocessing, cache-miss compression and decoding unused support frames as bottlenecks in the earlier path, using separate decoding, loader, transfer and compute measurements. Its optimized final-stage-only measurement is not evidence for full-CNN epoch cost.

| Configuration | GPU kernel-busy activity | VRAM | Training actions/s | Training epoch duration |
|---|---:|---:|---:|---|
| Historical report, uncontrolled | approximately 18–20% reported | Not established | Not established | Not established |
| Audited optimized final-stage-only path | 97.9% | 4.15 GiB | 6.637 | Different training scope; not comparable |
| Audited full-CNN FP32, effective batch 8 | approximately 94% | 7.77 GiB peak allocated (8.34 GB decimal) | approximately 1.925 | Approximately 15.2 minutes for 1,752 actions, excluding validation/checkpoints |
| Recent full-CNN sustained epochs | approximately 99% | Logged per epoch | approximately 2.02 | Approximately 14.5 minutes for 1,752 actions, excluding validation/checkpoints |
| New frozen100 and full100 | Pending / measured live | Measured live | Measured live | Measured live in linked report |

Kernel-busy activity is the fraction of sampled time executing GPU kernels. It is separate from allocated VRAM and does not indicate achieved fraction of peak FLOPs. Full-CNN training is compute-bound at the measured configuration: recent CPU data waits were around one second per approximately 916 seconds of training computation. Increasing CPU workers or performing extra computation to inflate utilization would not improve this workload's throughput.

## Selected configuration and preserved scientific behavior

Use four persistent pinned-memory loader workers with prefetching and two FFmpeg decoder threads. Decode exactly the verified 16 action frames; batch the 16 frames within each action. Full-CNN action microbatch 1 with gradient accumulation 8 preserves effective batch size and fits the T4. Keep FP32 and existing finite-gradient, clipping, parameter-update and checkpoint checks. BF16 is unsupported on this GPU; FP16 and compilation are not introduced without a new numerical/performance justification.

The frozen comparator trains a small head from previously verified exact FP32 frozen features, avoiding repeated unnecessary CNN computation. Its low utilization is expected and scientifically appropriate; its real throughput is the optimization criterion. CNN-feature equivalence was verified across all 4,530 actions during the existing audit. The full comparator trains all executed CNN convolution and normalization-affine parameters, with fixed running moments.

The existing full-CNN gate verifies numerical outputs, finite gradients through all executed trainable CNN parameters, parameter updates, reload equivalence, and optimizer/scheduler/RNG/sampler recovery. The new controls additionally passed four tests, including exact stochastic 37-to-100-epoch checkpoint continuation. Both comparison arms use a documented matched cosine-100 schedule. The original paused study retains its separate cosine-50 prefix and 20-epoch cap.

## Hours and reporting

Estimate 24–25.3 full-CNN training hours for 175,200 training-action presentations, plus validation, calibration, initialization and checkpointing; plan 26–36 allocated GPU job hours total. Frozen-head training is shorter and measured separately. The live comparison report records actual training hours and process GPU job hours, excluding resource queue and pause time. Actual total is pending until execution completes. No final duration or utilization is invented before completion.
