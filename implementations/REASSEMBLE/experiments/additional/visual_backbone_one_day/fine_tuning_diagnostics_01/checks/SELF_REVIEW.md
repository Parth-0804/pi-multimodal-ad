# Diagnostic packet self-review

Status: PASS for the implemented saved-result analysis. This is not independent scientific review.

- Six synthetic tests passed, including AP with ties, exact AP reconciliation over random discrete scores, undefined no-positive AP handling, deterministic label-blind ranking budgets and fusion-logit algebra.
- The analysis reconciled AP, AUROC and Brier for all 72 original condition/branch/scope rows. All 100 keyed fit manifests matched their stored lineage SHA256 identities.
- A separately coded standard-library verifier reproduced all 12 pooled AP/Brier pairs and all eight complementarity rows directly from historical assessment CSVs, without importing the new analysis functions or original model code.
- Exact AP attribution totals reconcile by action and recording; all calibration and F2 arithmetic checks passed.
- 571 consumed inputs passed SHA256 verification. All 1,363 original study files retained their sizes and modification times. Unrelated Git status and tracked diff statistics were unchanged. Large unused historical files were not fully rehashed.
- `git diff --check` passed. Repository-environment `python -B -m pip check` reported no broken requirements.
- Training, model loading, new raw-input inference, feature extraction, corruption experiments, raw payload access and network access: zero.
- Three stopped reader-development attempts are retained. Final reader behaviour uses fit manifests for absent legacy convenience metadata, maps the historical `fused` label to F2, and permits only the measured machine-precision raw sensor-logit difference while requiring exactly identical calibrated sensor probabilities.
- Plots were inspected visually. Reliability plots show only bins with at least 20 segments; the complete bin counts remain in the CSV. All numerical subgroup results remain descriptive.

Scientific review checked that the report does not claim a demonstrated fine-tuning disadvantage, treat coefficient magnitudes as causal modality shares, call calibration data untouched validation, interpret AP accounting as a causal recording ablation, or recommend selecting hyperparameters from outer assessment results. The reported OOF/assessment inconsistency and matched-epoch loss pattern are clues, not established causal mechanisms.

Outstanding: independent scientific review and any separately authorised controlled follow-up. No follow-up was launched or scheduled.
