# C-only GPU integration

The full-CNN numerical, input, worker and checkpoint gates remain valid because the CNN/input/update computation is unchanged. See the [original GPU integration report](../../26102026_reports/PHASE1_GPU_INTEGRATION.md).

One T4; FP32;16 frames per action; microbatch1; accumulate8; four persistent workers; FFmpeg2; pinned memory; prefetch2.

Measured full-CNN pilot: 1.9253 actions/s. First complete actual C training pass: 1753 actions, 14.82 minutes and 96.67% mean GPU kernel-busy activity. Later per-epoch metrics remain in original C fit folders. GPU compute activity and VRAM occupancy are distinct.

The revised75-fit20-epoch workload initially projected396 full-CNN training hours and475–555 GPU-job hours including20–40% overhead, about20–23 days of exclusive T4 availability. Completed checkpoints reduce the remaining count; live status updates it. B is omitted and its inexpensive cached-head work no longer contributes. Exact completed training hours and recorded C child-process wall-hours appear in the executive review.
