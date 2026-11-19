# Resume within the existing budget

From the repository root:

```bash
ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py resume --wait-seconds 0
```

This checks the priority process and sole allocated GPU, verifies pinned manifests and source/config identities, and proceeds through real preflight, extraction, matched fitting, replay and reporting only when ready. It returns WAITING_FOR_GPU when the device remains owned. It never queues a job. `--wait-seconds 3600` requests a foreground one-hour maximum wait, still subject to the original 24-hour deadline; no automatic extension.

The deadline is 2026-10-22 00:31 Europe/Berlin (2026-10-21 22:31 UTC), conservatively measured from 2026-10-21 00:31 Europe/Berlin. Fifteen minutes are reserved for reporting. Once expired, resume refuses further scientific work. Preserve this run and seek an explicit new budget decision; do not edit start time to bypass the cap.

If source changes before scientific fits, rerun the focused `test` command. After scientific identity is locked, code/config/input changes fail closed. Interrupted checkpoints remain in their fit folder and restart attempts count toward the caps. Failed commands and logs remain visible. Historical Task4 and further experiments are excluded.
