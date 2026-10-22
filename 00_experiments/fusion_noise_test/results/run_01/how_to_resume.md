# Supported resume

From the repository root:

```bash
ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/run_experiment.py resume --wait-seconds 600
```

This runs through eligible selection, clean replay, selected-only raw-input inference and evaluation automatically. If upstream work remains active, it safely returns WAITING_FOR_PREVIOUS_RESULTS after the foreground wait. Total waiting across resumptions is capped at60minutes; polls are at least60seconds apart. Nothing is queued.

Original task start:21October2026 01:01 Europe/Berlin (20October23:01UTC), including interruptions. Deadline:22October2026 01:01 Europe/Berlin (21October23:01UTC), with15minutes reserved for reporting. Repeated instructions/resume do not reset this deadline. No training of this or predecessor studies is authorized.
