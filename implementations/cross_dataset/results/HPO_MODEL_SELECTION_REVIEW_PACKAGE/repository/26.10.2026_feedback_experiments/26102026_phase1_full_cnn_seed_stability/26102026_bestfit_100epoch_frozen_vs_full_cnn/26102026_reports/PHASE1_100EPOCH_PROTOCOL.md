# Authorized temporary comparison: frozen CNN versus full CNN, 100 epochs

Protocol REASSEMBLE-SINGLEFIT-FROZEN-VS-FULL-CNN-E100-v1, fixed before new assessment results. Authorized by the user's 27 October 2026 instruction to execute this detour and document it. The original three-seed, 75-fit, C-only study remains authorized and resumes automatically afterward.

## Selection and assessment

Snapshot selection considers the three completed C-only fits, each 20 epochs, available when the detour was requested. Select by highest training-side validation AP; ties lower validation weighted BCE, then seed/job index. Winner: original fit 3 (zero-based job 2), seed 42, inner fold 3 of outer fold 1, validation AP 0.2877194859994388, selected checkpoint epoch 19. Other APs: 0.28039409999236303 and 0.2687589468226123. Candidate validation groups differ; their ranking is descriptive and this follow-up is exploratory.

Keep the selected fit's training (1,752 actions), validation (419), calibration and fusion group memberships unchanged. Both arms assess the same 753 outer-fold-1 actions, whose recordings are disjoint from all three candidates' training, validation, calibration and inner-assessment roles. This explicitly replaces the selected inner fit's prediction set for this detour only, preventing other candidates' validation recordings from contaminating assessment through the selection process. Selection did not consult outer assessment labels or metrics. Dataset exposure in earlier research and post-selection limit claims of confirmation.

## Matched two-arm training

Run two fresh independent 100-epoch fits from identical original pretrained CNN initialization and identical seeded classifier initialization (seed 42). Do not extend the winning trained checkpoint, which would give an unequal starting point. No early stopping before 100 epochs except unsafe numerics, resource/integrity failure or explicit user stop. Select the reporting checkpoint by validation AP, ties lower weighted BCE and earlier epoch; retain all 100 epochs and learning curves.

B_frozen100 trains only the head on the verified original FP32 16-frame pooled features. C_full_finetuned16 trains all executed backbone convolution and normalization affine parameters plus the head; normalization running moments remain fixed, as in the approved full-CNN implementation. Spatial pooling, frame averaging, preprocessing, class weighting and train-only standardization remain unchanged. No new fusion/F2 model is trained in this two-fit visual detour.

Both arms use FP32, AdamW, head LR 0.001, weight decay 0.001, gradient clip 1, effective batch 8 actions and the same deterministic epoch permutations. Full CNN backbone LR is 0.00001; microbatch 1 action batches its 16 frames together. A matched cosine multiplier decreases from 1 to 0.1 over 100 epochs in both arms. This horizon is explicitly new for this separate experiment; the paused study retains its original cosine-50 prefix and exact 20-epoch cap. Four persistent pinned-memory workers, prefetching and two decoder threads retain the audited full-CNN throughput configuration.

Calibration uses only the selected C recordings, independently per arm. Report AP, AUROC, Brier, log loss, prevalence, raw-logit AP/AUROC, learning curves and paired C-minus-frozen AP/AUROC. A 2,000-draw recording bootstrap (seed 20261027) gives conditional intervals for this one fitted split, not multi-seed uncertainty.

## Pause, provenance and continuation

The original controller stops cooperatively only after committing a completed epoch and closing data workers. Preserve an additional SHA256-verified copy containing model, optimizer, scheduler, RNG, selected weights, history and next permutation hash. Consume only this detour's uniquely identified stop request. Hold the original single-writer lock during both new fits; never run the two controllers concurrently on the allocated GPU. The new fits use isolated identities and output directories; original training files and configurations stay frozen and are hash checked throughout.

On success, release the writer lock and relaunch the unchanged C-only controller. Verify that it loads the exact paused epoch and next permutation. It skips its three completed fit receipts, finishes the remaining epochs of fit 4, and continues the original 75-fit schedule. No 100-epoch weights enter the original study. An explicit new stop, source drift, numerical failure, low disk or failed checkpoint integrity blocks continuation for inspection. Foreign GPU jobs are never terminated; the runner waits and resumes from its own last completed epoch after resource contention.

A controller process is detached from the interactive session. Host reboot or controller failure requires relaunching the same comparison controller; committed checkpoints are resumable. There is no claim of a system service or reboot scheduler.

## Resources and planning estimate

The project has one allocated Tesla T4 (16 GB); no multi-GPU speedup is available. FP32 is retained after the existing gradient/update/reload audit; no new precision or scientific changes are introduced. Full-CNN audited throughput is about 1.925 actions/s, while recent sustained epochs approach 2.02 actions/s and approximately 99% GPU kernel-busy activity. Kernel-busy utilization is distinct from memory occupation and does not measure the percentage of peak arithmetic throughput.

At 1,752 training actions, 100 epochs require approximately 24–25.3 GPU training hours, plus validation, calibration, decoding startup and checkpoint overhead. Reserve roughly 26–36 GPU job hours (about 1–1.5 days with exclusive availability) for this detour. Frozen cached-feature training is much shorter and will be measured. Actual training and process GPU job hours are recorded separately; queue/pause time is excluded from active job time. Maintain at least 10 GiB free storage. Original data, prior outputs and original checkpoints are preserved.
