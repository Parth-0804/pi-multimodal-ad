# Actual actions

Located root-missing prompt at parth_ws_bootstrap/00_Experimentaitons/Run_Visual_Backbone_Comparison.md. No matching process or existing output run found. Read prompt/governing data/output rules and targeted original source. nvidia-smi observed one idle16GiB TeslaT4; essential runtime check launched. All writes confined to this new folder under parth_ws_bootstrap/00_experimentation, honoring the latest folder request and prior bootstrap boundary. No old source,config,data,history or AGENTS written.

2026-10-20T15:58:11.072097+00:00 — Preparation full lossless pixel estimate exceeded30GiB,3segments25MB/~38.3GBprojected. Technical repair01 preserves estimate/source/config/log; bounded2GiB lossless cache with exact content-hash re-decoding, no frame/processor/settings/label changes. No fitted models/cohort lock existed. Only own regenerable cache files may evict; historical/raw outputs untouched.

Implementation efficiency before fits: native pixel access during feature extraction/training now uses bounded8GiB RAM and existing2GiB disk cache,exact re-decoding/content hashes on miss,without recompressing every training access. Preparation writer/source remains unchanged. CPU preprocessing/frames/precision/scientific settings unchanged.

## Implementation before cohort/fit lock

CPU affinity of own preparation PID 41639 and extant threads restricted to CPUs 0–3; new stage launcher applies the same four-CPU limit. All new numerical processes use four-thread library settings and zero data-loader workers. No cgroup memory limit was found; fitting monitors RSS against 32 GiB and uses an 8 GiB RAM pixel LRU. Core standardizer floor confirmed from section1_models.Standardizer as 1e-6 and adopted before any fits. Sensor inference retains float32 scaler arithmetic. Final-stage and checkpoint-resume checks are implemented but NOT_YET_EXECUTED. Training-only timings and storage estimates will be written before admitting full fits. Completed optimizer checkpoints will be released only after compact prediction-producing weights/calibrators and replay evidence are saved, preserving their SHA and scalar completion receipt.

Original feature extraction will use the actual 16- and 32-frame batch shapes and Torch float32 spatial/frame reductions, avoiding a NumPy reduction mismatch with live adaptation. Saved-model replay for every complete visual fit will reconstruct the full pixel-to-CNN-to-head-to-calibrator path, including the frozen arms, on the first three held-out sample keys. The 1e-5 probability tolerance is fixed before any scientific fit. Cached-feature head timing and full pixel-path replay timing are saved separately.

## Controlled preparation efficiency handoff

SIGINT sent only to owned preparation PID 41639 and process exited 130; no competing writer. Per-record completed checkpoints and the interrupted log/source/config/progress were preserved. A one-sample measured compression cost of1.582s dominated the ~1.9s preparation rate. New preparation retains the already bounded 2GiB lossless cache without compressing every later row merely to evict it. Exact uncompressed content hashes still bind every selected tensor; later extraction/inference redecodes uncached pixels. No labels, frame selection, statistics or split formulas changed. Non-prepare function AST identities are checked in checks/preparation_runtime_optimization.json. Prior completed cache-only preparation source is explicitly allowlisted, not treated as scientific-fit reuse. No model fit or score existed at this change.

## Pre-fit cache capacity and model-object inspection

Constructing the original local pretrained object on CPU verified RTDetrResNetBackbone, selected stage2/stage3/stage4 and four CNN stages. Final stage has exactly8,388,608 parameters in five convolution-weight tensors; its normalization affine/running quantities are buffers, not additional trainable parameters. Fifty compact adapted states therefore need about1.56GiB plus heads; completed optimizer copies will be released after replay. Reserve4GiB for models/checks/features/metadata and use24GiB disk pixel cap (28GiB projected combined ceiling, below30GiB), with the existing8GiB RAM allowance now storing losslessly compressed bytes in an exclusive RAM/disk LRU. This can retain a full G working set more effectively without changing a pixel, gradient or label. The active preparation loaded its original2GiB write-admission setting and still avoids cache churn. Codec profiling tested exact round trips; standard compressed NPZ was retained for compatibility, and no temporal/horizontal image representation is fed to a model. No optimizer step or model score preceded these runtime choices.

## Completed native preparation

Actual cohort locked4530 samples,509 failures,148 recordings; zero exclusions. All selected16/32 lists checked nested/distinct/in-interval,25 actual G/C/held partitions and100 planned visual fits. Added direct partition sample keys and complete before/after group/class counts before fitting. Previous storage blocker is resolved explicitly in saved state; its failure log/estimate remain preserved. Preparation implementation/config snapshotted before adding total task elapsed time, remaining caps and process-RSS observations to runtime state reporting.

## Actual stage invocation: preflight

From repository root: `bash parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/study.sh preflight > parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/checks/cnn_preflight_and_feature_extraction.log 2>&1`. This foreground stage runs the four-condition disposable gradient/weight/BN/checkpoint replay checks, then original-feature extraction. No scientific fit is reused from preflight. Source/config identities are fixed for extraction; CPU/GPU/offline/cache environment is in the saved launcher.

## Actual preflight outcome

All four real-CNN checks passed, with9/20 disposable optimizer updates and pooled width896. Frozen arms changed no CNN tensors; adapted arms changed final-stage convolution weights only, all normalization buffers unchanged. Compact reload passed and replay of the second update reproduced parameters, optimizer and CPU/CUDA RNG exactly. Original feature extraction is now running. Before any full scientific fits, raw fitting gained only additional evidence/timing outputs: keyed sensor-C calibration logits and CUDA-event model/backward/optimizer intervals excluding pixel-load time, saved in checkpoint scalar state. No training objective, optimizer setting, forward computation or random draw/order changed. Per-batch device-clock elapsed including host gaps is also retained and clearly labeled.

## Pre-fit storage-check overhead and integrity guards

During raw fitting, the exclusive pixel cache still enforces24GiB directly on every spill. Filesystem free reserve is checked each spill, while full-tree study accounting occurs at least once per minute and remains before model/checkpoint writes and every100 updates. This avoids scanning thousands of feature/cache sidecars for every RAM/disk promotion; all controlled non-cache allocations remain below the predeclared4GiB reserve, leaving2GiB ceiling slack. This is monitored/procedural storage control, not an OS filesystem quota. Input/source identity is rechecked before each raw visual/sensor job and fixed config before checkpoints. No pixel, frame selection, forward, loss, optimizer setting or random draw changed. These training-only additions do not modify the active original-feature extraction source or its identity.

## Full scientific training started

Original features completed all4530 rows/896 dimensions. Actual row cost sums: pixel loading/cache/transfer8456.22s,16-frame CNN/pool/transfer653.31s,32-frame1111.92s. Feature array hashes/finite shapes and runtime/input checks passed. An initial inline readiness check omitted the CUBLAS environment and was correctly rejected before any fit; rerunning with the saved deterministic environment passed without source changes. Actual fitting invocation: `bash parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/study.sh train > parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/checks/full_study_training.log 2>&1`. No plan/approval handoff; exactly the authorized paired-fold matrix.

## First real condition checkpoint

Fold1 frozen16 completed all four inner plus final outer raw fits (five total), C calibration, identified OOF pairs, F2 fit and keyed outer predictions with arithmetic/model replay. Five sensor fits complete and shared. No assessment AP scored or condition ranking made. Fine-tuned16 inner1 is now running from original weights. Source/configuration unchanged after the scientific fit lock.
