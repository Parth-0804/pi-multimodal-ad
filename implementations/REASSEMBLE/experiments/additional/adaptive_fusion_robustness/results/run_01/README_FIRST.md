# Completed one-fold pilot — inconclusive

All **753 actions × 34 realizations** completed with zero failed cases. Quality-interaction fusion had primary AP **0.257009**, versus **0.253996** for augmentation-matched static fusion: **+0.003012**, paired 95% interval **[-0.026711,+0.032165]**. No reliable primary improvement was demonstrated.

Observed image-fault AP improved, while sensor-fault AP worsened. Clean AP was slightly higher, but clean-loss uncertainty remains. Additive quality alone reduced AP; interaction benefit versus additive quality is also uncertain. This is a development-exposed one-fold pilot; the other four folds remain untested.

**Decision: retain historical F2 as the working baseline.** No further experiment was launched.

[Full results and comparison](RESULTS_SUMMARY.md) · [Data audit](DATA_AUDIT.md) · [Locked protocol](PROTOCOL.md) · [All prediction paths and hashes](comparison/coverage_and_prediction_index.csv) · [Clean prediction table](predictions/fold_01/clean/clean/repeat_00/predictions.csv) · [Review package](REVIEW_PACKAGE.zip) · [ZIP checksum and verification](checks/package_verification.json)

Automated results finished at **12:06 Berlin time on 22 October 2026**; final independent review and repackaging followed within the unchanged 24-hour budget. Fourteen tests, 196 independent AP recalculations and 70,029 probability replays passed. Previous protected artifacts remain unchanged. See provenance/final_runtime.json for actual runtime, interruption and resource accounting.
