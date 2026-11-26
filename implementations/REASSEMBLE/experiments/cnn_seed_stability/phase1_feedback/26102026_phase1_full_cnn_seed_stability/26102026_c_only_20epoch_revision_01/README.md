# Full CNN only,20 epochs — active revision

**Execution scope amended on2 November2026:** the researcher requested a stop
after25 complete fits, covering seed42 and all five outer folds. The active
[capped controller and recovery instructions](02112026_stop_after25fits_01/README.md)
supersede the original75-fit resume command below. Each fit still executes20
epochs; seeds123 and20261023 are deferred. The original plan/configuration
remain preserved, and the live status now records the approved25-fit target.

The user explicitly selected Model C only and20 epochs per fit. The three
seeds and original nested folds remain, giving75 full-CNN fits. No pending B
fits, F2-B or reconstructed A_r fits will run. The existing B result is kept.

Estimated remaining runtime is approximately **20–23 days** of continuous
single-T4 availability. Dropping B saves little GPU time because those cached-
feature head fits were inexpensive. A single C fit is roughly5–8 hours at20
epochs, depending on partition size; the full study trains75 such models.

The active C model transitions at a complete epoch and resumes its model,
optimizer, scheduler, RNG and sampler state. Every fit uses the same original
cosine50 learning-rate prefix through epoch20; the cap changes without
rewriting the completed learning-rate history. The original two-arm training
configuration stays immutable for checkpoint identity, while the separate
revision configuration and completion receipts record the amended scope.

- [Protocol](26102026_reports/PHASE1_EXPERIMENT_PROTOCOL.md)
- [Configuration](26102026_configuration/PHASE1_C_ONLY_CONFIG.json)
- [Live C-only status](26102026_execution/PHASE1_C_ONLY_STATUS.json)
- [Executive review](26102026_reports/PHASE1_EXECUTIVE_REVIEW.md)
- [Training results](26102026_reports/PHASE1_TRAINING_RESULTS.md)
- [Fusion results](26102026_reports/PHASE1_FUSION_RESULTS.md)

Selected weights, learning curves and base prediction files remain in the
original `../26102026_execution/26102026_main_run_01/` per-fit folders. This
revision stores its own source/configuration/provenance, C-only completion
receipts, logs, final metrics and retained transition checkpoint. Original
outputs are preserved. Completion requires `PHASE1_C_ONLY_ALL_COMPLETE.json`;
an active process or partial status is not a finished study.

Resume from the repository root with the same environment:

```bash
env PYTHONDONTWRITEBYTECODE=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 \
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
  ma_thesis_env/bin/python -B \
  26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/26102026_source/c20_controller.py
```

The original study-root `STOP_AFTER_EPOCH.json` remains the graceful stop
control. A single-writer lock prevents competing controllers. Numerical,
identity or storage failures stop the affected work with evidence.
