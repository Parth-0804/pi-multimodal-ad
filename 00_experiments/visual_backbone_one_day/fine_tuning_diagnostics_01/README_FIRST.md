# Fine-tuning diagnostics: saved predictions and learning curves

**Complete.** This packet analyses the completed four-condition visual-backbone study. It uses saved numerical evidence only. No training, new raw-input inference, feature extraction, corruption experiment or model change was performed.

**Main finding:** fine-tuning slightly improves image-only pooled AP, but those gains do not consistently transfer into fusion. The strongest new clue is that the 32-frame fine-tuned image branch has lower AP in all five inner OOF banks used to train fusion, despite a higher pooled outer-assessment image AP. Learning is less consistent during the first two epochs, and outcomes differ by action and recording. These are diagnostic findings, not proof of one causal explanation.

| Comparison | Image AP change | Fusion AP change |
|---|---:|---:|
| Fine-tuned16 minus frozen16 | +0.002823 | -0.003159 |
| Fine-tuned32 minus frozen32 | +0.011182 | -0.001017 |

Higher AP is better. Both comparisons use the same 4,530 assessment segments, 509 failures and 148 recordings. The original primary fusion16 interval includes zero. At the fixed 0.5 decision threshold, fine-tuned fusion detects three more failures for each frame count; therefore, “no improvement” applies to the primary AP result, not every metric.

Read [FINE_TUNING_DIAGNOSTIC_REPORT.md](FINE_TUNING_DIAGNOSTIC_REPORT.md) for the interpretation, evidence, limitations and proposed next decision. The diagnostic tables and figures are linked there.

- [Findings as JSON](findings.json)
- [Matched OOF/assessment differences](tables/OOF_to_assessment_pair_changes.csv)
- [Failure overlap at fixed ranking budgets](tables/fixed_budget_complementarity.csv)
- [Exact AP accounting by action](tables/action_AP_contributions.csv)
- [Matched first-two-epoch loss summary](tables/learning_curve_summary.csv)
- [Focused synthetic test evidence](checks/synthetic_tests.log)
- [Analysis consistency checks](checks/analysis_checks.json)
- [Separate arithmetic/preservation self-check](checks/final_self_check.json)
- [Input identities](provenance/input_manifest.json) and [output manifest](provenance/output_manifest.json)
- [Execution and software provenance](provenance/execution.json)

The full original study remains at [run_01_two_epoch_finetuning](../run_01_two_epoch_finetuning/README_FIRST.md). Its source, configuration, models, predictions and reports were not edited. This new packet is a sibling folder, so it does not modify the original review archive.

**Recommended next decision:** review this diagnostic evidence and decide whether to authorise a small, pre-specified 16-frame comparison with matched two-epoch budgets, repeated seeds and training-only validation monitoring. It is proposed only; nothing has been launched.

Review status: assistant self-review, including a separately coded arithmetic check. Independent scientific review remains outstanding.
