# PHM walkthrough review and validation

Scope: one numbered PHM experiment, RT-DETR Model 1 scalar regression, plus its start page and end-to-end sample trace. Historical source, raw data, configuration, checkpoints and outputs were not changed.

**Unresolved scientific finding:** the stored regression head uses 769 inputs: 768 image features plus `feature_latency_ms`, selected by the `feature_` prefix. The saved scaler and parameter count confirm this. The walkthrough describes the actual model and records the historical architecture discrepancy in [KNOWN_IMPLEMENTATION_ISSUES.md](01_rtdetr_scalar_regression/KNOWN_IMPLEMENTATION_ISSUES.md). Removing timing and measuring the effect require a separate scientific correction and approval for retraining. Target review also remains necessary.

| Check | Result |
|---|---|
| Sample, feature and prediction identity | 995 unique sample IDs agree; image, experiment, run, tooth, split and targets match |
| Partition separation | EXP-B train 448; EXP-A validation 323; EXP-F test 224; no experiment/run spans splits |
| Actual feature order | Exactly feature_0000…feature_0767, followed by feature_latency_ms |
| Actual head width | 769 scaler entries; 98,689 reported head parameters consistent with 769→128→1 |
| Saved performance | All eight metrics plus sample count match all 12 recorded metric rows to absolute tolerance 1e-12 |
| Aggregation | Saved tooth view-max and raw run top-three means agree with the retained image predictions |
| Example target | Saved pixel counts reproduce 2.555843714% for EXP-F / Run 1 / Tooth 01 |
| Relative shortcuts | All ten resolve to their intended originals |
| Original preservation | All 33 initially referenced originals retain SHA256, size and mtime |
| Guide links | All local Markdown links in the new guides resolve |
| Environment | pip check: No broken requirements found |
| Formatting | git diff --check passed; no trailing whitespace in new guides |

Validation reads saved tables and recalculates evaluation/aggregation only. No raw media were opened, no models or checkpoints executed, no training or inference run, no packages installed, and no historical reports regenerated. Metric agreement is not evidence that the intended architecture was implemented correctly; the latency-input discrepancy remains open.

Files added: 12 Markdown files (including this report), one navigation manifest and ten relative shortcuts under `experiments/phm2026/`. `REPO_MAP.md` receives two lines for PHM, preserving the earlier two-line REASSEMBLE addition. Two CSV shortcut names remain ignored under the existing bulk-output rules; guides and the manifest identify their canonical paths.

At this phase boundary, `git diff --stat -- REPO_MAP.md` shows four insertions relative to HEAD: two from the earlier REASSEMBLE phase and two from this PHM phase. Untracked new files are not included in that statistic. Pre-existing presentation-image deletions, the missing `src/shared/README.md`, and other untracked work were left untouched.

Next action: read the [sample trace](01_rtdetr_scalar_regression/SAMPLE_WALKTHROUGH.md) and the confirmed implementation issue. A further experiment walkthrough or scientific correction is a separate phase. No correction or retraining is included in this phase.
