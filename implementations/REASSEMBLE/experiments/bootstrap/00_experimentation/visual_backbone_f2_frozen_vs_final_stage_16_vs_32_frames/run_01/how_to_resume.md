# Inspect, stop or resume this fixed study

The current scientific process is actively fitting. Do not start a second writer. Inspect live progress without launching a model:

```bash
bash parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/study.sh status
```

Training uses an exclusive study lock. Existing complete fits are reused only when input/configuration/source/fit identities and their prediction/model hashes match. Partial fits retain compact model, normalizer, optimizer, CPU/CUDA RNG, Python RNG, epoch, next effective batch, deterministic NumPy order seed/policy and precision. Successful five-epoch fits retain compact prediction-producing models/calibrators and replay evidence; their unnecessary optimizer copies are released with a SHA/size receipt.

If the active worker is interrupted, inspect the recorded blocker and resolve it without changing scientific settings. Once no writer is active and no explicit STOP request remains:

```bash
bash parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/study.sh resume
```

`stop` records an owned-study stop request; training checkpoints at its next safe optimizer boundary. Preserve that request in provenance before intentionally clearing it for resume. Do not stop unrelated jobs. `evaluate` and then `package` operate on the genuinely completed paired folds; they do not authorize extra fits or a different model. No continuation is scheduled.

The latest launch has no hour ceiling, but retains100 planned/110 maximum full visual fit starts,20 disposable optimizer updates,30GiB new disk storage,10GiB free reserve, one available T4 worker, four-CPU affinity and monitored32GiB process RSS. HistoricalTask4, UI, robustness and external datasets remain excluded. No downloads, installations or resource purchases.
