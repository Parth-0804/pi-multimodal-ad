# PHM RT-DETR feasibility fallback

This experiment is permitted only when the exact pinned T2.1 audit is
`BLOCKED_REQUIRES_PROFESSOR_OR_PROVIDER_DECISION`. It runs bounded standard
pretrained RT-DETR inference; it does not train a PHM model or report PHM
damage-prediction performance.

```bash
ma_thesis_env/bin/python -B scripts/training/run_rtdetr_feasibility.py --dry-run
ma_thesis_env/bin/python -B scripts/training/run_rtdetr_feasibility.py
```

Generated evidence belongs under the ignored, non-overwriting
`runs/phm2026_rtdetr_feasibility/<run-id>/` root.
