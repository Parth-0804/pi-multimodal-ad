# Reproducibility report

Use the repository environment from the project root. No network or new package is required. Existing selected models remain in `26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn`; exact paths and SHA256 are in the run input manifest. Sensor models/scalers/calibrators and both saved sensor banks are included in03; fitted F2 coefficients are in05. Large CNN checkpoints and raw recordings are referenced rather than duplicated.

For a quick independent read-only verification, run `ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/recompute_metrics.py`. It reads only the exported CSV and metric/bootstrap artifacts, uses separate NumPy/rank formulas, prints every model's recalculated metrics and checks the paired intervals to1e-12. It needs no CNN weights or raw dataset and changes no file.

Commands executed:

```bash
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/verify.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/verify_sensor_features.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/verify_sensor_models.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/verify_canonical_sensor.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/benchmark_cpu.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/infer.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/evaluate.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/plots.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/reports.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/validate.py
ma_thesis_env/bin/python -B experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/seal.py
ma_thesis_env/bin/python -B -m pytest -q -p no:cacheprovider experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/tests
```

The listed stage commands record the performed analysis. The CPU completion launcher `src/complete_pipeline.py` orchestrates evaluation, figures, reports and validation after inference and creates the pipeline receipts used by final sealing. A full replay must use a fresh versioned experiment directory with its own ACTIVE_RUN.json pointer and copied locked configuration/source; never direct new writes into this completed run.

The locked scientific protocol is01/LOCKED_PROTOCOL_03.json; earlier pre-analysis drafts and both original-recipe clarifications are preserved. The initial visual/checkpoint verification remains bound to protocol02 because the CNNs and input roles are unchanged. Reproduce into a new versioned directory, preserving this completed run. The original draft is preserved with its documented pre-analysis sensor-role clarification. CPU inference initially used2 threads; a calibration-control throughput benchmark selected8 available CPU threads with identical FP32 control output. An optional fixed-shape FP32 compiler was faster in one control benchmark but failed during full initialization (native exit139), before producing any scientific prediction rows. It was rejected. The active runtime is stable eager FP32 inference with8 threads, CPU_RUNTIME_03.json; attempted/earlier runtime receipts and per-row evidence are preserved. No learned parameter, frame, precision or model choice changed. All six saved-GPU controls were repeated for the active backend. Only this task's resumable CPU process was restarted, never the running GPU study. The16 model-input frames per example match their original pixel hashes. CPU/GPU forward parity, strict checkpoint loading, original calibrator refits and frozen-logit replay are recorded in02.

No outer-test labels or probabilities enter `fit_fusions()`; it reads only the training bank and ID/group audit metadata. The fusion-fit lock was created before new outer metrics and includes the fixed source/configuration/model hashes. A separate recording-group meta-crossfit is diagnostic only. The test table can be recomputed directly from06 without loading a CNN. Independent NumPy/rank-based metric calculations, including tied-score AP and rank AUROC, reproduce the sklearn table to1e-12; tests include tied and boundary probabilities and duplicate-ID rejection.

All commands write exclusively inside this new experiment. Raw data, original source code, existing checkpoints and previous reports are unchanged. Main-study execution receipts are observed only; no checkpoint or controller setting is changed. The final validation receipt and output manifest distinguish checked original source identities, derived artifacts and known scientific limitations. An output manifest is not a claim of independent dataset replication.

For sensor training replay, keep the recorded original16-thread OpenBLAS partitioning; the checker constrains its physical CPU affinity while retaining that numerical reduction configuration. The later-variant sensor replay reproduces its saved weights/probabilities exactly; the canonical original models were reconstructed and verified against their saved OOF/calibrated probabilities. The comparison uses the original canonical saved probabilities, never replacement-refit probabilities. Run the final sealing command after all stage logs and pipeline receipts are closed so their final hashes, rather than intermediate snapshots, enter the output manifest.

Limitations: previously inspected single test fold; selected original fit; one training-side holdout bank; no complete100-epoch4-fold branch OOF reproduction; no additional seed/fold validation; conditional uncertainty; ECE sparse-bin instability. The saved source identity is sufficient to audit the performed analysis but does not erase those limitations.
