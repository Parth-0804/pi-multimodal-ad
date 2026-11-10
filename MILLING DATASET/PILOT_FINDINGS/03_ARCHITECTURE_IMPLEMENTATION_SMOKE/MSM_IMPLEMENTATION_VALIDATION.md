# MSM implementation validation

**PASS for the bounded implementation smoke; NOT READY for full evaluation.** The Stage 2 limited cohort supports a traceable coarse-context visual+sensor input contract. All actual Stage 3 training used a deliberately bounded development subset. No smoke metrics are offered as scientific performance evidence, and **zero outer-test predictions** were generated.

Run: `MILLING DATASET/runs/20261027T003527238586Z-stage3`. Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`. Frozen protocol/hash: `config/protocol_lock.json`; exact source/software identities: `provenance.json` plus `manifests/final_software_source_identity.json`. Git revision `94f61529116ebdc966bcf87704a93e4d02fa5e89`; pre-existing dirty tracked/untracked work was preserved. No staging, commit, environment installation, dataset acquisition, or historical output overwrite.

## Tests and real-input checks

**46 tests passed** (20 Stage 3 checks including parametrized cases, plus 26 prior MSM tests). Recorded command output: `validation.json`. The environment's `pip check` passed and `git diff --check` passed. Tests use tiny synthetic data, not copied raw examples.

| Required property | Result / evidence |
| --- | --- |
| Frame-label alignment | Corrected Stage 2 selector reused; all 114 admitted native annotation/frame policies rechecked; actual 24-interval loading rechecks every selected decoded BGR SHA-256 and PTS |
| Sensor-label alignment | Half-open native interval, coverage including edges, finite gate; exact parity of all 90 features for all 24 actual sampled intervals; tests reject NaN/gaps/duplicate clocks/target columns |
| Model forward/output unit | Exactly 16 frames → 896 values → one interval logit; sensor/F2 one score per same interval; wrong frame count or frame-level head tensor rejected |
| Gradients | All new-head parameters have finite nonzero gradients; synthetic update check; actual CPU/CUDA updates pass; frozen CNN has absent gradients by design |
| Group splits | Complete exact OOF coverage; both-class partitions; shared-group split rejected; declared three-outer design fails closed on current two positive groups |
| F2 stacking integrity | All 24 development rows receive one probability pair from models fitted without their experiment group; fitting/selection-group contamination rejected; outer-bank values remain NaN in synthetic outer-fit test |
| Outer-label isolation | Perturbing frozen synthetic outer labels leaves training OOF probabilities, new head and F2 coefficients exactly unchanged |
| Checkpoint save/reload | Branch and F2 prediction maximum absolute differences **0.0** after safe tensor reload |
| Metric calculations | Known synthetic AP 5/6, AUROC 0.75, confusion matrix, balanced accuracy, F1 and Brier validated; undefined one-class metrics rejected |
| Worker stability | Two spawned persistent workers exhausted, both exit codes 0, both reaped; zero/two-worker embeddings bitwise identical |
| Numerical behavior | Finite CNN embeddings/losses/gradients; CPU/CUDA untrained-head max forward difference **8.94e-08**; processor scale roundoff ≤5.96e-8 |
| Preservation | All 41 pilot raw files hash-verified; 41 Stage 1 + 100 Stage 2 protected artifact/source hashes unchanged; raw/cache/checkpoint Git exclusion verified |

Model testing exercised actual imported RT-DETR weights, actual MSM video decoding and new heads; synthetic fixtures do not stand in for the real smoke. MTC-only gaps and missing-video intervals remain excluded. This run does not verify every 640×640 sequence in the full 114-example cohort at runtime: 24 were actually decoded, while all 114 timing/annotation policies were revalidated and Stage 2 remains the visibility audit.

## Allocated GPU and loading measurements

One visible **Tesla T4**, 16,384 MiB nominal, Torch CUDA usable; PyTorch 2.13.0+cu130, torchvision 0.28.0+cu130, transformers 5.14.1. At admission another project process used about 9,184 MiB and the device reported **100%** utilization, leaving about 6,741 MiB free. It was never terminated or modified. GPU visibility was inherited; no separate scheduler reservation was established. Data storage remained about 75 GiB free.

The main smoke used at most about **536 MiB reported process VRAM**, including CUDA context; Torch tensor peak **305.2 MiB allocated / 414.0 MiB reserved**. The allocator was capped at 2 GiB with a 3 GiB free-device reserve admission/runtime check. Device-wide 100% utilization belongs to the shared workload and cannot establish MSM utilization. The previous REASSEMBLE **97.9%** result is not imported here.

Actual MSM live decoding plus frozen-CNN extraction, same four development intervals per setting:

| Workers | Intervals | Measured wall s | Intervals/s | Loader wait s | Peak Torch MiB allocated / reserved | Parent+worker RSS GiB | Worker exit codes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4 | 8.327 | 0.480 | 6.877 | 305.2 / 414.0 | 1.39 | [] |
| 2 | 4 | 4.375 | 0.914 | 2.989 | 305.2 / 414.0 | 3.15 | [0, 0] |

Both use one FFmpeg thread/worker, one Torch CPU thread, prefetch one where applicable, uint8 pinned-memory transfer, FP32 CNN frame microbatch two. Timers start after iterator creation and include first-batch wait; spawn/iterator construction is not fully included. Parent CPU times were 8.28 s (serial) and 1.40 s (two workers); worker lifetime CPU was 19.76 s for two workers and includes startup/import work outside the timed window. Consequently the original telemetry field `cpu_core_equivalents` for that worker setting must not be interpreted as a window-normalized CPU utilization measurement. CPU loading is substantial: the serial 24-example extraction spent 40.05 of 48.53 s waiting for input, with about 39.84 s of source decode work.

The larger 24-interval extraction measured **48.534 s / 0.495 intervals per second**, including live seeks, frame/hash/PTS checks, preprocessing, transfer and CNN pooling. It consumed 384 CNN frames. It was not a full scientific epoch or sustained exclusive resource benchmark. Cache/page-cache state, fixed setting order, only four paired timed examples and GPU contention limit comparisons. Two workers are a useful optimization candidate, not a demonstrated full-corpus optimum; the serial path remains the conservative smoke reference.

An idle process listing briefly motivated an exclusive follow-up, but the admission check saw another GPU job and **refused before any CNN/optimizer work**. There is no exclusive throughput or sustained MSM GPU-utilization result. The optional `msm.benchmark` command requires an idle device and has not completed. Do not wait for or interrupt the unrelated training from this task.

Cached-head device-path check, two updates per device on the same 24 development feature vectors:

| Device | Initialization + two-epoch fit s | Interval presentations/s, including initialization | Peak Torch allocated MiB |
| --- | --- | --- | --- |
| CPU | 0.0111 | 4316.5 | n/a |
| CUDA, shared | 0.4534 | 105.9 | 66.8 |

These very short timings include construction/optimizer startup and are not steady-state head benchmarks or end-to-end CNN throughput. They validate both device paths; CPU is appropriate for the tiny cached-head reference. CNN extraction here is **frozen forward inference**, while optimizer updates affect only the newly initialized head. No CNN-backpropagation throughput is claimed.

## Bounded work completed

Main end-to-end smoke: **24 unique intervals / four folders**, native counts 8 normal + 10 abnormal + 6 stable defective-tool. Two inner branch fits plus a development refit, each two epochs, **six head optimizer updates**, newly fitted sensor models and a new OOF-trained F2. Main elapsed time **80.75 s**. Both F2 and uniform averaging forward paths checked. No prediction metric was calculated from these real development outputs.

Adding the CPU/CUDA head path check gives **10 optimizer updates total** and **528 CNN frame forwards total** (including repeated benchmark/warmup inputs), below frozen caps of 12 / 768. The smoke checkpoint and its fitted F2 coefficients are development artifacts: do not carry them into a full outer evaluation. Exact fit-group provenance is in `manifests/stacking_provenance.json`; checkpoint in ignored `checkpoints/development_only.pt`.

## Full evaluation readiness and requirements

**NOT READY.** Core adapters, fitting composition, tests and inference checkpoints work; the current cohort has only two positive folders and cannot pass the declared three-outer/two-inner group design. Physical tool/session dependence is unresolved. MTC aggregation latency and frequent visual contact occlusion limit conclusions to retrospective coarse-context classification. No claim of visual separability or fusion benefit follows from this smoke.

After researcher review, expand the version-2 laboratory alignment/visibility/sensor audit before generating frozen splits. Stage 1 lists 56 laboratory folders and 2,512 labeled cuts with 458 label-1 intervals in 25 nominal positive groups; these are upper-bound candidates, not eligible examples. Full laboratory minimal video+MTC+alignment-audio/metadata storage was estimated in Stage 2 at **2,640,036,050 bytes total**, **2,533,736,741 additional bytes** beyond the acquired minimal subset. Recompute an exact file plan for the intended microphones/support; no such acquisition occurred here. An ACC-inclusive laboratory alternative is about 35.29 GB total and is a separate architecture contract.

At 2,512 candidate cuts, pooled 896-float visual plus 90-float sensor features occupy about **9.91 MB uncompressed**, before metadata/checkpoints; optional per-frame CNN features about 144 MB. Full decoded 640×640 uint8 frame caching would need about **49.39 GB**, or 197.55 GB float32, so stream and cache pooled features. Existing pretrained files are reused, not downloaded again. The 528-frame smoke took well below the allocated disk reserve.

Purely illustrative extraction time using the two measured short shared-GPU rates is roughly **46–87 minutes for 2,512 intervals**. This is not an exclusive estimate, full-corpus benchmark, label-alignment audit budget or training-time guarantee; actual eligible count, seek lengths, machine clips and loader startup vary. The 27 fixed-head fits reuse this one feature bank and have 10 epochs each; full-matrix timing must be reassessed on the expanded cohort. No multi-day full-CNN budget is implied by this frozen-extractor protocol.

## Reproduction and review boundary

Run from repository root with the repository environment and portable import roots:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 \
PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m pytest -q 'MILLING DATASET/tests'

# Only after separately authorizing a new bounded reproduction; use a NEW run path.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 \
PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.smoke \
  --config 'MILLING DATASET/configs/stage3_protocol.json' --output 'MILLING DATASET/runs/NEW_UNIQUE_STAGE3_RUN'
```

Do not rerun into this preserved run; writers refuse existing outputs. No command launches the full matrix. Source/config/tests are reviewable but remain untracked; existing tracked diff is unchanged (three pre-existing files, 22 insertions). Small reports/manifests are available for review; raw data, numerical caches and checkpoints stay ignored.

**Exact next action: researcher reviews the frozen protocol and adaptation, then decides whether to authorize cohort expansion/dependency audit. Stop here before full evaluation.**
