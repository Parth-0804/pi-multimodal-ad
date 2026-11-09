# PHASE 1 — GPU optimization report

Date: 26 October 2026. Written: 2026-10-26T23:02:15+01:00.

**Selected cache-free configuration: four persistent DataLoader workers, two FFmpeg decoder threads per video, pinned memory, prefetch factor two, and exact decoding of only the 16 consumed frames.** It delivered **6.64 actions/sec and 97.9% sustained GPU compute utilization**, with clean worker exits. One action contains 16 RGB frames. The projected 2,966-action epoch is **7.45 minutes**.

**No full experiment was launched. All benchmark processes have finished; the GPU was observed idle with no allocated process memory afterward. Further training waits for the researcher's later prompt.**

## Hardware and allocation

- One visible project GPU: **NVIDIA Tesla T4, 16,384 MiB nominal VRAM**, compute capability 7.5; PyTorch exposes approximately 15,929 MiB. Its UUID matches the GPU in the prior project runtime record. No other visible/allocated GPU was found or accessed.
- Driver **580.167.08**; driver-advertised CUDA **13.0**; PyTorch CUDA runtime **13.0**; PyTorch **2.13.0+cu130**, torchvision **0.28.0+cu130**, cuDNN **9.2**. A standalone `nvcc` executable was not found. Native BF16 is unavailable.
- GPU admission checks found no competing GPU process. CUDA/NVIDIA visibility variables and SLURM allocation variables were unset; inherited visibility was retained. This is the sole visible VM GPU, consistent with the previous project allocation, rather than a scheduler reservation independently verified through SLURM.
- CPU: **16 AMD EPYC-Rome logical cores**, affinity 0–15. No CPU quota or memory ceiling was found in the inspected cgroup hierarchy. Main-process Torch threads remain four; loader Torch threads are one, with separately bounded FFmpeg threads.
- RAM: **62.7 GiB total, about 58.0 GiB available** at the saved audit snapshot; no swap.
- Storage: about **79 GiB free** at the saved audit snapshot. An earlier inspection saw about 13 GiB before separately authorized cache cleanup finished. This audit deleted no files. Its only persistent decoded-pixel cache is a bounded **215 MiB** benchmark subset; checkpoints/traces and all generated bulk are ignored by Git.
- Buffered source-video reads measured **1,439–5,785 MiB/sec**. These page-cache-affected reads are not physical-device bandwidth measurements. `/proc` I/O counters and decoder/loading timings are retained; storage was not the dominant measured warm-input stall.

Full evidence: [hardware](runs/20261026T212550Z-934ad6c7/reports/hardware.json), [buffered I/O](runs/20261026T212550Z-934ad6c7/tables/storage_reads.json).

## Experimental scope and measurement

The audit targets the existing REASSEMBLE `F2-CLEAN-CNN-2x2-MEAN-v1` study. It uses **24 deterministic gradient-training actions from 20 recordings**, selected from the first outer fold's original epoch-zero permutation. Calibration and assessment outcomes were not used for fitting or configuration selection.

The model, original pretrained weights, G-only feature normalizer, class weighting, learning rates, AdamW, clipping, dropout, frame identities and trainable final-stage boundary remain unchanged. **Float32, one action per microbatch, 16 frames batched per CNN call, and eight accumulated actions per optimizer update** are preserved. No full scientific epoch, fold matrix or seed sweep was run.

Every configuration has **two sustained windows of at least 60 seconds**, after two warmup updates. Initialization, numerical checks, model loading, checkpoint writes, worker teardown and short operator profiling are excluded from throughput windows. GPU telemetry is sampled approximately every 0.5 seconds. Epoch times below are **extrapolations for 2,966 actions**, rather than measured complete epochs. Repeating a bounded subset keeps this audit small; it does not establish throughput across all 4,530 actions or cold physical storage.

The existing pixel cache had been evicted before this audit. The cached benchmark regenerates verified 32-frame pixels only inside this folder. The selected live path creates no persistent pixels: each 16-frame result must match a SHA256 derived from its verified original 32-frame parent. Model inputs therefore remain bitwise identical despite removal of unused-frame preprocessing.

## Before/after benchmarks

GPU utilization below means NVIDIA's kernel-busy-time metric. VRAM is separately measured process/device memory usage; neither VRAM occupancy nor memory-controller activity is a substitute for compute utilization. Kernel-busy time also does not measure percent of peak FLOPS or SM occupancy.

| Configuration | GPU compute utilization | Peak VRAM | Actions/sec | Projected epoch |
|---|---:|---:|---:|---:|
| Cached32 support, serial | 41.6% | 4247 MiB | 2.938 | 16.83 min |
| Cached32 support, 2 workers | 99.9% | 4247 MiB | 6.769 | 7.30 min |
| Cached32 support, 4 workers | 99.9% | 4249 MiB | 6.745 | 7.33 min |
| Live32, default decoder, serial [D] | 22.6% | 4247 MiB | 1.704 | 29.01 min |
| Live32, default decoder, 2 workers [D] | 47.1% | 4247 MiB | 3.334 | 14.83 min |
| Live32, 1 decoder thread, serial [D] | 16.7% | 4247 MiB | 1.169 | 42.27 min |
| Live32, 1 decoder thread, 2 workers [D] | 31.2% | 4247 MiB | 2.147 | 23.03 min |
| Live32, 1 decoder thread, 4 workers [D] | 72.8% | 4249 MiB | 4.852 | 10.19 min |
| Exact live16, 2 decoder threads, 2 workers | 49.0% | 4247 MiB | 3.623 | 13.64 min |
| **Exact live16, 2 decoder threads, 4 workers** | 97.9% | 4249 MiB | 6.637 | 7.45 min |

`[D]` denotes preserved **diagnostic results excluded from selection**: the default-decoder run was interrupted for stability repair; the single-thread decoder run later failed during four-worker teardown. Their finite training windows help diagnose input starvation, but are not evidence of a stable configuration. Both gates remain blocked.

The original **18–20%** figure was reported by the researcher; no contemporaneous utilization trace was found to verify that exact number. Reconstructed live-loading baselines measured approximately **16.7–22.6%**, while the verified warm-cache serial baseline measured **41.6%**. These are different input paths and must not be presented as a single matched historical measurement.

Matched cached-input comparison: **2.94 → 6.77 actions/sec (2.30×)**, **41.6% → 99.9%** compute utilization, **16.83 → 7.30 min** projected epoch. Four cached workers gave no meaningful gain over two.

For the current cache-free state, select the exact-live16/four-worker path. Its two windows delivered **6.702 and 6.573 actions/sec**, with **98.1% and 97.6%** compute utilization. Against the bounded single-thread live32 serial diagnostic, its measured speedup is **5.68×** and projected epoch falls from **42.27 to 7.45 minutes**; this comparison includes frame-work removal and decoder/worker tuning.

## Actual bottlenecks and changes

1. **Serial CPU loading and preprocessing starved the GPU.** Cached serial loading took about **195 ms/action**: approximately 119 ms NPZ decompression, 56 ms hashing and 18 ms float conversion, versus only 1.9 ms buffered file reading. CNN forward/backward took approximately **137 ms/action** and host-to-device transfer **7.6 ms/action**. Two cached workers reduced main-process loading wait to approximately **13 ms/action**.
2. **Cache-miss compression was expensive and unnecessary for live training.** The bounded 24-action preparation measured means of **86 ms decoding, 318 ms preprocessing/hash validation, 1,382 ms NPZ compression and 9 ms writing**. The selected path removes compression and disk-cache promotion entirely. It does not repopulate historical caches.
3. **The 16-frame arm processed 32 support frames.** The selected path decodes/preprocesses only the 16 consumed frames, validating their exact original pixel bytes. CNN computation and frame pooling are unchanged.
4. **Decoder threading and teardown needed separate handling.** Default FFmpeg pools produced over **130 OS threads per loader worker**. The final decoder bounds FFmpeg to two threads; observed complete worker thread counts were about **24–25**, including library/helper threads. Merely bounding decoder threads and calling the ordinary shutdown routine did not fix the aborts. Cooperative iteration exhaustion now drains prefetched input, closes video handles, and then joins workers. **All four final benchmark/profiler shutdown records contain only exit code 0.** Drained actions perform no training and are outside timed windows.
5. **Synchronization and transfer overhead were reduced.** Pinned memory, persistent workers, prefetch two, non-blocking transfers, and removal of per-action host scalar checks keep work queued. Finite loss/gradient-norm checks remain at optimizer boundaries; numerical checks inspect individual gradients separately. Effective batch eight is retained through gradient accumulation.

The final CUDA trace provides independent confirmation: the two-worker and four-worker paths execute the **same 3,045 CUDA kernels** for eight actions, taking about **1.12 seconds of kernel time**. Wall time changes from **2.12 to 1.18 seconds**; kernel-busy share rises from **52.8% to 95.5%**. The gain comes from removing idle gaps, without extra GPU computation. Sustained-window telemetry remains the primary utilization measure. CPU, CUDA-event and worker timings overlap and must not be summed as disjoint wall-time components.

Trace evidence: [kernel summary](runs/20261026T215300Z-selected16-e15865ad/tables/kernel_trace_summary.json). Raw operator totals include nested ranges and must not be added together as physical kernel time.

## Numerical correctness and protocol decisions

Both final configurations passed:

- regenerated-input identity checks, including exact selected16 hashes;
- finite, nonzero head and final-stage gradients, with gradients restricted to the intended parameters;
- exact first-update parameter, optimizer and CPU/CUDA RNG parity against the serial reference;
- unchanged earlier CNN parameters and BatchNorm running buffers, with the backbone in evaluation mode;
- **bitwise model/optimizer/RNG checkpoint replay on a fixed training batch**;
- finite sustained-window losses and gradient norms, and clean worker shutdown.

Checkpoint replay here validates component serialization; it does not certify resuming a future scientific runner's sampler/prefetch cursor. Existing scientific checkpoints, source files, configuration and progress were preserved; both successful run preservation checks passed. No historical result was overwritten.

The batch-size sweep is intentionally limited by the existing fixed one-action microbatch and dropout/RNG protocol. VRAM was not a constraint: final Torch peak allocated memory was approximately **2.18 GiB**, while NVIDIA reported approximately **4.15 GiB** in use. Additional batch/precision changes would need separate equivalence validation.

**AMP:** BF16 lacks native T4 support. FP16 was not enabled because float32 is fixed by the current protocol; no mixed-precision correctness claim is made. **`torch.compile`:** considered but not enabled or benchmarked; it would require deterministic numerical/checkpoint validation and a measured throughput benefit. Further input tuning has little immediate value for this measured final path, already near 98% compute busy. Full-cohort variation may change that conclusion.

**Multi-GPU strategy:** DDP is inapplicable to the sole visible GPU. No independent GPU jobs were run concurrently. If additional GPUs are explicitly allocated later, independent folds/seeds are a reasonable first strategy, with CPU/decoder budgets assigned per GPU; DDP requires its own benchmark and preservation of the global batch/protocol.

## Training-time and GPU-hour estimates

The existing plan contains **25 fits per condition**, five epochs each, totalling **287,620 training-action presentations per condition**. It has one seed family; a new multi-seed matrix has not been specified.

| Scope | Estimate / actual |
|---|---:|
| 16-frame adapted training, existing 25 fits, selected live configuration | **12.04 GPU-hours** of steady training |
| Same 16-frame scope with 15–30% runtime contingency | **13.8–15.6 GPU-hours**, before inference/bootstrap work |
| Existing four-condition matrix, training component only | **34.9–36.1 GPU-hours** |
| Four conditions with optimized input/inference integration and overhead | **45–60 GPU-hours per seed family**, provisional |
| Four conditions retaining the old serial inference path | **75–90 GPU-hours per seed family**, provisional |
| Actual full multi-fold/multi-seed experiment GPU-hours this session | **0.000 — not launched** |
| Actual monitored benchmark-window GPU-hours, including failed/interrupted diagnostics | **0.339 GPU-hours** |
| One-GPU audit elapsed budget, first run through final benchmark completion | **0.547 GPU-hours upper bound**, including CPU preparation/idle gaps |

The 32-frame multiplier **1.9–2.0** is a provisional extrapolation, supported only by historical disposable warm timings of approximately 0.140 s/action at 16 frames and 0.267 s/action at 32 frames. Sustained 32-frame throughput was not newly benchmarked. Frozen-head fits historically took about 22–28 seconds each and add roughly 0.3 hours across both frozen conditions, excluding extraction/replay.

The 45–60-hour planning range includes approximately one hour for full-cohort identity bootstrapping, conservative inference cost based on measured training throughput, and checkpoint/I/O/CPU contingency. It assumes a future runner actually uses the optimized input path for inference. Keeping historical serial inference is materially more expensive: the preserved completed 16-frame fit spent 2,171 seconds on 1,460 calibration/prediction actions, projecting about **31.1 hours** across both adapted conditions before other overhead. These are planning scenarios, not completion promises or newly measured full runs.

For a future seed count `S`, multiply seed-dependent fit costs by `S`; shared manifest preparation need not repeat. An exact total cannot be stated until the later training prompt defines its matrix and seed count.

## Gate, validation and next action

The requested performance investigation, multiple configurations, measured selection, numerical/gradient checks and time estimates are recorded. The **16-frame benchmark candidate passes**. **Full training remains locked**, and no process is running.

Before a later full launch: use the researcher's new prompt to freeze the matrix/seeds; integrate the selected loader in a new versioned scientific runner; build whole-cohort selected-frame identities; validate sampler/checkpoint resume; and benchmark sustained 32-frame execution if that arm is requested. The existing historical runner was not changed or restarted.

Validation completed: **14 synthetic tests passed**, repository-environment `pip check` passed, and `git diff --check` passed. Final worker checks and GPU telemetry confirmed clean exit and zero GPU process memory. No dependencies were installed and no commit was created.

All audit additions are under this requested folder: configuration, eight source/launcher files, tests, README, this report, and unique ignored run directories. `git diff --stat` reports **3 tracked files, 22 insertions**, all pre-existing unrelated changes (`README.md`, `REPO_MAP.md`, and `THESIS_EVIDENCE_GAPS.md`); this audit's files are untracked additions and therefore absent from that tracked diff statistic. Separate cache-cleanup artifacts appearing during the session were not modified by this audit.

Completed evidence:

- [Cached comparison](runs/20261026T212550Z-934ad6c7/tables/summary.json)
- [Final cache-free comparison](runs/20261026T215300Z-selected16-e15865ad/tables/summary.json)
- [Final performance gate](runs/20261026T215300Z-selected16-e15865ad/reports/performance_gate.json)
- [Correctness: two workers](runs/20261026T215300Z-selected16-e15865ad/checks/selected16_workers2_pinned_numerical.json)
- [Correctness: four workers](runs/20261026T215300Z-selected16-e15865ad/checks/selected16_workers4_pinned_numerical.json)
- [Historical preservation](runs/20261026T215300Z-selected16-e15865ad/checks/historical_preservation.json)
- [Interrupted diagnostic record](runs/20261026T213457Z-stream-a8efd0e8/reports/streaming_stability_interruption.json)
- [Failed diagnostic gate](runs/20261026T214258Z-stream-ca88704c/reports/performance_gate.json)

Implementation guidance was checked against the official [PyTorch performance tuning guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html); measured behavior and local numerical checks determine the selected configuration.
