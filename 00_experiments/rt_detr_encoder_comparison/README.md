# Frozen RT-DETR encoder comparison

Completed: five paired folds and 4,530 actions. CNN-only F2 AP was 0.440764;
CNN plus encoder F2 AP was 0.424979. Start with
[README_FIRST.md](results/run_01/README_FIRST.md) for results and directly identified predictions.

This isolated study implements cnn_only versus cnn_plus_encoder under the assignment in Run_Encoder_Comparison.md. All new writes remain in this directory. Prior data, weights, code and scientific outputs are read-only.

Use the repository environment from the repository root:

```bash
ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py prepare
ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py test
ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py run --wait-seconds 0
ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py status
ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py evaluate
```

`resume` uses the same implementation as `run`, checking exact completed-fit identities and resuming incomplete head optimizer checkpoints. Completed fits are never silently retrained. A nonnegative `--wait-seconds` requests a foreground wait with device/process checks once per minute, bounded by the original deadline. No command creates a scheduler or background worker. After the deadline, a new authorization is required; these commands cannot extend it.

See [run status](results/run_01/README_FIRST.md) and [results](results/run_01/comparison/RESULTS_SUMMARY.md). Code is a study-specific implementation; fusion.py is an attributed unchanged snapshot of the priority study's pure logistic helpers, with the original source hashes in provenance. No claims of actual training or GPU path validation arise from tests alone.
