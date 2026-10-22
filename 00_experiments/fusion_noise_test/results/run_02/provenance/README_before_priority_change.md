# Selected-model raw-input robustness study

Everything new stays inside this directory. The two preceding studies, native data and fitted models are read-only. No training or adaptation is performed. Selection stays unlocked while preceding work is active.

From the repository root:

```bash
ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/run_experiment.py prepare
ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/run_experiment.py test
ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/run_experiment.py run --wait-seconds 600
```

`resume` advances the same pipeline with identity checks; `select` performs clean selection only after upstream results are terminal; `evaluate` recalculates actual saved outputs; `status` never launches inference. Waiting is foreground only, at most60minutes total with60second polling, and never resets the original24hour deadline. No scheduled continuation is installed.

[Current status](results/run_01/README_FIRST.md), [selection](results/run_01/model_selection/selection_report.md), [results](results/run_01/comparison/RESULTS_SUMMARY.md).

The guarded prefix is an attributed inference-only snapshot of the encoder study. Native resampling/statistics follow the pinned visual-study source; explicit fault masks prevent interpolation across intentionally removed support. Snapshot code is evidence only and never imported. Full real-data replay is required before any corrupted assessment inference.
