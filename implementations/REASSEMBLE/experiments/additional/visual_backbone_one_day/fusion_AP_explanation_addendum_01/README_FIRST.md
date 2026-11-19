# Visual AP versus fusion AP: diagnostic addendum

Most requested analysis already existed and was reused. This packet fills the missing error-overlap, label-aware loss, rank-example and uncertainty checks.

Fine-tuning improves image predictions overall, but its gains on sensor mistakes are inconsistent. Many improved image rankings do carry into fusion; deterioration on other examples offsets them. At 32 frames, fusion improves slightly when averaging fold APs but worsens slightly when pooling all predictions. Those summaries measure different things.

All requested difference intervals include zero. The newly added fine-tuned32 versus frozen32 fusion interval is **[-0.009295, +0.009400]**. The small observed difference could reflect sampling variability. Calibration, incomplete optimisation and seed variation remain hypotheses; the mechanism is unresolved.

Read [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md), [WORK_INVENTORY.md](WORK_INVENTORY.md), and [REVIEW_PACKAGE.zip](REVIEW_PACKAGE.zip). The ZIP contains the report, supporting tables, selected unchanged prior evidence, analysis scripts and saved numerical inputs.

No training, inference, refitting or threshold tuning ran. Review is a self-review. No further experiment is launched.
