# Future ViFailback CNN data-loader optimization

Prepared 2026-11-11 UTC for `matched_cnn_20_100_f2_20261111`.

**Status: isolated implementation prepared; CPU data-contract validation PASS; GPU numerical and performance benchmark PENDING. No faster configuration is recommended yet.** Full100 and its 36 queued Full20 fits retain their original implementation and settings. These candidates are for a separately versioned future study, after the protected queue finishes.

The implementation is in [17_future_dataloader_optimization](17_future_dataloader_optimization/). It is outside the frozen active `src/` and `scripts/` directories. Nothing imports it from the current controller. No active model, optimizer, checkpoint, seed, split, epoch budget, decoder setting or queue was changed. No additional GPU context, training process, frame cache, commit or push was created by this preparation.

## Baseline and reason for this experiment

The [live performance diagnostic](PERFORMANCE_DIAGNOSTIC.md) measured six minutes at two-second intervals: mean GPU kernel-busy utilization **74.76%**, with **24.4%** of samples at zero; mean host CPU busy **9.55%** over 16 CPUs; disk busy **0.974%**, with essentially no physical reads during that warm-cache interval. The trainer and workers could use CPUs 0–15, with no effective cgroup CPU quota. This is evidence of intermittent GPU inactivity and ample resources for a later controlled test, not proof that every GPU gap is a loader stall. CPU-head work, synchronization, transfers and dispatch can also create gaps. Unused CPU percentage does not imply a speedup.

The original source uses the following configuration:

| Setting | Frozen current behavior |
|---|---|
| Loader | Two workers; prefetch one episode per worker; `batch_size=None`; `shuffle=False` |
| Worker lifecycle | Spawn; persistent workers disabled; a new loader for each train/validation phase |
| Delivery and pinning | Ordered episode delivery; `pin_memory=True`; transfers request `non_blocking=True` |
| Training minibatch | Main process collects eight episodes; CNN image chunk size four |
| Pixel tensor | CPU FP32 `(3, 16, 3, 640, 640)`, 225 MiB per episode |
| Cameras | High, left wrist, right wrist, processed sequentially within each episode |
| Frame selection | Original uniform rounded indices; 16 frames per camera, 48 per episode |
| Decode | CPU FFmpeg, `-hwaccel none`, decoder threads one, filter threads one |
| Preprocessing | Original RGB verification, PIL bilinear resize/rescale and tensor assembly |
| Caching | No decoded-frame cache; selected frames decoded on every epoch visit |
| Model work | Pixels reused for the original two CNN passes; CPU head and gradient propagation unchanged |

Source references: [training.py](src/matched_vifailback/training.py), [model_runtime.py](src/matched_vifailback/model_runtime.py), [controller.py](src/matched_vifailback/controller.py), [video.py](../../src/vifailback/video.py), [visual.py](../../src/vifailback/visual.py), and the frozen [protocol](01_protocol_and_source_evidence/protocol.json). Observed FFmpeg processes had more OS threads than the single decoder thread; this does not mean those threads were all decoding in parallel.

The measured first ten epochs averaged **94.231 minutes training + 11.747 minutes validation = 105.979 minutes**, excluding checkpoint commit. Training includes loading, copies and CPU/GPU work; existing telemetry cannot separate them. The two-episode outstanding queue may expose loading when the next eight-episode batch is collected. The experiment tests that hypothesis without changing decoding or model math.

## Isolated configurations

The original `training.episode_loader` remains the independent reference. [loader.py](17_future_dataloader_optimization/future_dataloader/loader.py) reuses its exact `Episodes` dataset, pixel loading and FFmpeg path. [settings.py](17_future_dataloader_optimization/future_dataloader/settings.py) exposes four immutable presets. All retain spawn, ordered delivery, pinned-memory request, no persistent workers, no shuffle, and a private generator seeded 314159, matching the original loader without advancing the main PyTorch RNG.

| Preset | Workers | Prefetch per worker | Maximum outstanding episode tasks | Queued FP32 payload only | Conservative free-RAM admission |
|---|---:|---:|---:|---:|---:|
| `baseline_w2_p1` | 2 | 1 | 2 | 0.439 GiB | 6.834 GiB |
| `w4_p1` | 4 | 1 | 4 | 0.879 GiB | 9.031 GiB |
| `w4_p2` | 4 | 2 | 8 | 1.758 GiB | 10.789 GiB |
| `w2_p4` | 2 | 4 | 8 | 1.758 GiB | 9.471 GiB |

The queue column bounds outstanding tasks, not the number guaranteed ready at a batch boundary. The trainer's eight episodes add 1.758 GiB of payload. Actual memory also includes worker imports, decoded arrays, transformation temporaries, copies and pinning. The admission envelope deliberately budgets these separately; it is an estimate, not measured peak RAM. Required free `/dev/shm` ranges from 1.318 to 3.076 GiB across the presets. GPU admission requires at least 8 GiB free and no compute process; disk admission retains 20 GiB plus a 256 MiB output allowance.

`w4_p1` tests additional episode parallelism. Comparing `w4_p2` with `w2_p4` tests queue depth with different worker counts. Settings reject more than four workers, a queue product above eight, persistent workers or a different multiprocessing context. Persistent-worker reuse, parallel camera decoding, FFmpeg thread changes, alternate image libraries, hardware decode and disk caches are deliberately separate future experiments. Their speed and equivalence have not been established. No whole-cohort frame cache is created; the prior audit estimated 80.91 GiB native RGB or 431.54 GiB FP32 for T+V alone.

## CPU validation performed

The [real-data receipt](17_future_dataloader_optimization/results/cpu_contract_20261111_01/CPU_CONTRACT_VALIDATION.json) records **PASS** at `2026-11-11T22:00:44.484724+00:00`. The new validation process had CUDA hidden before PyTorch import, one PyTorch/BLAS thread, CPU affinity `[0, 1]` and nice level 10. Those limits affected only preparation and its children. The run took **101.056 seconds**, including verification and hashing; this is **not a throughput benchmark or speedup measurement**.

Four proper-training T episodes were selected by frame-count quantiles without consulting labels. Their observed labels are recorded for association checks:

| Episode | Canonical task | Frames per camera | Native failure label |
|---|---:|---:|---:|
| 3962 | 79 | 18 | 1 |
| 3878 | 79 | 188 | 1 |
| 1118 | 30 | 298 | 0 |
| 2348 | 50 | 925 | 0 |

The original loader plus all four presets decoded these same four episodes: **20 episode passes / 60 camera streams**, covering 192 distinct selected camera frames. Validation hashed every byte of each FP32 tensor and every ordered camera/frame tensor, and checked shape, dtype, contiguity, finiteness, delivered episode IDs, labels and main-process RNG state. Every preset matched the original exactly. No pixel arrays or decoded-frame files were saved.

Timestamp verification used historical complete-decode actual PTS, bound to **fresh SHA-256 hashes of all 12 unchanged source video files**. Camera identity, frame count, selected indices and RGB hashes matched the frozen manifest. Maximum selected nominal-versus-actual timestamp difference was **0.0 seconds** (acceptance tolerance `5e-5` seconds). This is source-bound timestamp identity evidence, **not a new PTS decode**.

Native label verification covers all 5,202 source episodes; the frozen 4,382 eligible episodes, 820 exclusions and task-disjoint fitting roles remained intact. Full T ordering was checked through metadata/samplers for seeds **42, 123, 20261023** and zero-based epochs **0, 1, 19, 99**. Each case retained 1,430 episodes, 179 optimizer minibatches and a final six-episode batch. These full-order checks did not decode the entire cohort. Separate synthetic worker tests cover 17 ordered items and minibatches `8 + 8 + 1`.

The automated suites cover loader boundaries/order/RNG, contract drift and the GPU admission/benchmark/export safeguards. **107 CPU-only tests passed**: loader 27, contract nine, admission/comparison 23 and activation 48. The [test summary](17_future_dataloader_optimization/results/test_summary_20261111_01/TEST_RESULTS.json) records commands, durations and expected warnings; final source hashes and checks are in [FINAL_VALIDATION.json](17_future_dataloader_optimization/results/final_validation_20261111_01/FINAL_VALIDATION.json). Repository dependency validation reported `No broken requirements found.`

Actual CUDA pin allocation and all GPU model-update equivalence remain **PENDING**. With CUDA hidden, PyTorch correctly warns that requested pinning is inactive. Four-worker CPU tests also warn about the intentionally restricted two-core affinity. Neither warning is evidence for or against runtime performance.

## Controlled future GPU benchmark

The manual CLI and [benchmark.py](17_future_dataloader_optimization/future_dataloader/benchmark.py) prepare this comparison; they do not schedule it automatically:

1. Require the entire protected **37-fit GPU lane** and **74-fit CPU lane** to be complete, with their controller processes inactive. Verify the completed Full100 and all 36 Full20 receipts, configuration/epoch counts, predictions and checkpoint hashes. A crash, idle sample or Full100 completion alone is insufficient.
2. Require an empty GPU compute-process list and conservative RAM, shared-memory, GPU and disk reserves. Acquire the existing cooperative GPU lock and a separate isolated benchmark lock, then recheck admission before any CUDA/model work. Other compute processes detected between minibatches abort this benchmark. Locks coordinate cooperative processes; they cannot reserve the GPU against unrelated external programs.
3. Require a current PASS CPU receipt bound to the original protocol, sources, split/cohort identities and isolated loader implementation. Build the same original pretrained full-CNN, CPU head, optimizer, clipping and fixed T-only feature moments, using seed 42 and the original Full20 cosine horizon 50. No live checkpoint is loaded. Use one disposable model at a time; write no model checkpoint.
4. Use the first **40 proper-T episodes** of `outer0_inner0`, seed 42, epoch 1. Run a separate untimed equivalence pass through the original loader and every preset. Require actual pinned input tensors and exact input/label, loss/logit, gradient, model, optimizer, scheduler and RNG digests. Check a separate scheduler boundary transition. Any failure prevents timing recommendations. These are prefix checks, not proof of a completed 20- or 100-epoch fit.
5. Run **four balanced cyclic rounds** across the four presets. Every pass starts from identical weights, optimizer and RNG. Eight episodes warm up the loader/model; **32 episodes** are timed. Worker startup/warmup are recorded separately. No numerical tensor hashing is included in the timed inner loop; initial/final state and the scheduler probe must still match the numerical reference. Page caches are not cleared.
6. Record episodes/second, synchronized `next(loader)` host wait with the GPU quiescent, compute wall time, CUDA stream elapsed time, two-second kernel-busy samples, peak allocated/reserved GPU memory and host memory snapshots. Stream elapsed time includes dispatch gaps and is **not kernel-busy time**. Guard queries can give prefetch a head start; their overhead is recorded, so reported waiting is for this guarded benchmark rather than uninstrumented production. Host RSS is a post-pass snapshot, **not a measured peak worker/pinned-memory allocation**. Validation throughput and individual decode/H2D/CPU-head timing are not measured by this harness.
7. Recommend a candidate only if every numerical check passes and its throughput is **at least 5% above baseline in every paired round**. Select the largest median gain among qualifiers. A completed benchmark can validly return `NO_RECOMMENDATION`. The export guard rechecks the measured case evidence and source bindings before exporting a candidate.

All benchmark passes use the same two-thread CPU math environment and unchanged eight-episode optimizer batches. Rotation reduces order bias but cannot eliminate thermal, clock or page-cache effects. Even a passing result supports only the measured T-prefix comparison on this host; it is not an established validation, whole-epoch or entire-fit speedup. Broader use needs a separately versioned study with resource and full-fit monitoring.

**Current benchmark result: PENDING; measured speedup: null; recommended configuration: null.** See the [admission status receipt](17_future_dataloader_optimization/results/gpu_pending_20261111_01/COMMAND_RESULT.json). The GPU controller is alive, the 37 fits are unfinished and the GPU has an active compute process. No GPU benchmark was attempted. At the read-only check on `2026-11-11T22:07:27Z`, PID 29074 retained creation time `1794353606.37`, was the only GPU compute process (5,582 MiB), and Full100 had 12 completed epochs. Its latest progress receipt was epoch 13, 1,200/1,430 episodes at 22:05:17 UTC; this is a saved progress point, not an exact current batch count.

## Exact future activation procedure

Run these commands from the repository root using the repository environment. Each invocation writes a unique result directory and refuses to overwrite an existing run. The commands below are instructions for later; no GPU command was executed during preparation.

```bash
future_loader_dir=VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/17_future_dataloader_optimization

ma_thesis_env/bin/python -B "$future_loader_dir/future_loader.py" benchmark-status
```

Proceed only when the result is `READY_FOR_MANUAL_BENCHMARK` **after all protected fits finish**. Keep the current 36 queued Full20 fits on their original settings even if a configuration appears promising. Do not clear a lock, rewrite a completion receipt or stop a controller to force admission.

The saved CPU receipt can be reused only while its source/data/configuration bindings remain valid. If those bindings change, rerun the small CPU validation under a new run ID and use its receipt instead:

```bash
ma_thesis_env/bin/python -B "$future_loader_dir/future_loader.py" validate-cpu \
  --run-id cpu_contract_future_01
```

With resources exclusively available, run the prepared benchmark explicitly. This default comparison uses all four presets:

```bash
ma_thesis_env/bin/python -B "$future_loader_dir/future_loader.py" benchmark-gpu \
  --cpu-validation "$future_loader_dir/results/cpu_contract_20261111_01/CPU_CONTRACT_VALIDATION.json" \
  --rounds 4 --episodes 32 --warmup-episodes 8 \
  --run-id gpu_comparison_01
```

Inspect `results/gpu_comparison_01/gpu_benchmark/GPU_BENCHMARK.json` and its hashed numerical/timing receipts. A `PENDING`, `FAILED` or `NO_RECOMMENDATION` result means retain the baseline and do not export an optimized setting. Only a qualifying measured result can be exported:

```bash
ma_thesis_env/bin/python -B "$future_loader_dir/future_loader.py" export-config \
  --benchmark-receipt "$future_loader_dir/results/gpu_comparison_01/gpu_benchmark/GPU_BENCHMARK.json" \
  --run-id future_admission_01
```

This produces `results/future_admission_01/FUTURE_LOADER_ADMISSION.json`; it **exports configuration only**, starts no training and modifies no controller. For actual use, create a new versioned future study with its own source freeze, output directories and explicit configuration. In that study's loader construction only, import the isolated package and apply the exported setting:

```python
import json
from pathlib import Path
import sys

loader_root = Path("VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/17_future_dataloader_optimization")
sys.path.insert(0, str(loader_root))
from future_dataloader.loader import build_loader
from future_dataloader.settings import LoaderConfig

admission = json.loads((loader_root / "results/future_admission_01/FUTURE_LOADER_ADMISSION.json").read_text())
assert admission["status"] == "EXPORTED_MEASURED_CANDIDATE_ONLY"
loader_config = LoaderConfig(**admission["loader_config"])
# ctx and ordered_ids are the new study's verified, unchanged native context
# and original epoch sampler output. Its training math stays unchanged.
loader = build_loader(ctx, ordered_ids, loader_config)
```

This is an explicit integration point for future source, not a production training command or an edit to the current `episode_loader`. Do not monkeypatch the running controller, redirect existing queued jobs or resume an old fit under a new loader. Preserve model, optimizer, epochs, seeds, splits, selection/calibration procedure, scheduler and numerical precision. Bind the new study's configuration and source manifest to the exported receipt, benchmark case hashes and loader source. Recheck resource admission at its own launch. Keep an unchanged-loader control; any numerical failure or absent measured gain retains the baseline.

## Provenance and limits

Git HEAD during preparation was `e32ec43aef69cc58adff0ea91e508308041598c5`; pre-existing live-report changes made the working tree dirty. The protected protocol SHA-256 is `71cbb3b01b0adb47d2e055bf79391276f1f2f3a9dd339e5b0f07013932caa9c5`. The CPU contract binding is `48ef5250af15f75a7ef59a55e1ff50e46be4264e7bcf57157d56b8384450a4d3`. Relevant installed versions were PyTorch 2.13.0, NumPy 2.4.6, Transformers 5.14.1 and Pillow 12.3.0. Per-command provenance records Python, other package versions, exact command, timestamp, configuration and protected/isolated source hashes.

The final validation directory records source and output manifests, syntax/dependency/diff checks, automated-test results, protected implementation verification and a final read-only live-status snapshot. Only new report, implementation, synthetic-test and compact evidence files belong to this task. Existing live reports and previous audit artifacts remain preserved. No GPU speedup, GPU waiting-time improvement, actual pin allocation or full-training numerical equivalence is claimed from the CPU results.

**Recommendation: preserve the active Full100 and its complete queued study; benchmark these isolated future loader candidates only after protected GPU work has finished.**
