# Noise study complete on locked pilot coverage

All 51 prescribed realizations and final checks completed. No noise or encoder continuation is required or scheduled. Metric-only recalculation:

```bash
ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/results/run_02/checks/recalculate_metrics.py
```

The requested restart of the existing visual task was actually attempted with:

```bash
bash 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/study.sh supervise
```

It was rejected by that task's existing whole-outer-cycle admission policy: 19.13 h estimated versus 14.95 h available before the immutable reporting reserve. The worker exited 75 without training updates; its checkpoint is unchanged. Repeating the command cannot resolve the shrinking budget. No extension, policy change, automatic retry or new experiment was made. See provenance/visual_resume_receipt.json. Further training requires an explicitly approved budget/protocol amendment.
