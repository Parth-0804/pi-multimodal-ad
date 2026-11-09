# Frozen versus full CNN,100 epochs — COMPLETE

Updated 2026-10-28T22:38:59.346746+00:00. Stage: COMPLETE_MAIN_STUDY_RESUMED.

Selected completed C20 fit: seed 42, original fit 3. Selection used training-side validation AP only.

| Candidate original fit | Seed | Validation AP | Executed epochs |
|---|---:|---:|---:|
| 1 | 42 | 0.280394 | 20 |
| 2 | 42 | 0.268759 | 20 |
| 3 | 42 | 0.287719 | 20 |

Validation sets differ across candidates, so the ranking is descriptive. This is a post-selected single-split follow-up, not independent confirmation. Both new arms start fresh from identical original pretrained CNN initialization/seeded heads.

| Arm | Completed epochs | Selected epoch | Training hours | Status |
|---|---:|---:|---:|---|
| B_frozen100 | 100/100 | 14 | 0.0610 | Complete |
| C_full_finetuned16 | 100/100 | 47 | 23.9642 | Complete |

| Arm | Sustained GPU kernel-busy % | Peak allocated GiB | Training actions/s | Mean training epoch seconds |
|---|---:|---:|---:|---:|
| B_frozen100 | 21.47 | 0.080 | 799.419 | 2.19 |
| C_full_finetuned16 | 99.74 | 7.770 | 2.032 | 862.40 |

Planning estimate:26–36 allocated GPU job hours. Actual active process time so far:25.8937 GPU job hours (includes validation/checkpoints; excludes pause and GPU queue). Per-arm training-only hours are shown above. These are resource occupancy hours, not GPU-utilization-weighted compute hours.

Frozen training reuses exact verified16-frame FP32 pooled features; its small head requires much less computation. Full training uses all CNN convolution/normalization-affine parameters and the classifier, four persistent workers, FFmpeg2, microbatch1 and accumulation8. Normalization running moments remain fixed. GPU kernel-busy activity and VRAM usage are distinct. All epoch curves and telemetry remain in each isolated arm folder.

## Shared outer assessment

| Arm | AP | AUROC | Brier | Log loss | Prevalence |
|---|---:|---:|---:|---:|---:|
| B_frozen100 | 0.193776 | 0.664605 | 0.089570 | 0.319693 | 0.102258 |
| C_full_finetuned16 | 0.212585 | 0.675325 | 0.089255 | 0.317383 | 0.102258 |

Paired C minus frozen differences and conditional recording-bootstrap intervals:

```json
{
  "AP": {
    "estimate": 0.01880892572409615,
    "lower95": -0.03644532724110226,
    "upper95": 0.09692558487958164,
    "valid_draws": 2000,
    "unit": "recording; conditional on selected split and fitted models"
  },
  "AUROC": {
    "estimate": 0.010720049181587643,
    "lower95": -0.03300808278117944,
    "upper95": 0.049021113753410485,
    "valid_draws": 2000,
    "unit": "recording; conditional on selected split and fitted models"
  }
}
```

The753 assessment actions belong to outer-fold1 recordings excluded from every candidate training, selection, calibration and inner-assessment role. Calibration uses only the chosen original C groups. One fold/seed and prior dataset exposure limit generalization; the original75-fit study remains the broader evaluation. No new F2 model was fitted in this two-fit detour.

The paused study retains its original20-epoch cap and cosine50 prefix. On completion, its controller is relaunched with the saved model, optimizer, scheduler, RNG and sampler boundary. No100-epoch weights are copied into that study.
