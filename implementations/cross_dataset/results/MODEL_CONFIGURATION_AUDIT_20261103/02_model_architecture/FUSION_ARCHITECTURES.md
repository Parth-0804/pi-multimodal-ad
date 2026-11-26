# Actual fusion mathematics and fitting scopes

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

Let pV, pS be branch probabilities and l(p)=log(p/(1-p)) after source-defined clipping. Calibration of branches and fitting a fused calibrator are different operations.

| Method | Exact prediction / inputs | Estimation and OOF scope | Missing modalities |
|---|---|---|---|
| Average |(pV+pS)/2 |No fusion fit; branch calibration remains dataset-specific |Explicit surviving-branch fallback where wrapper supplies availability |
| Original F2 |sigmoid(b+wV*pV+wS*pS) |Unweighted C1 L2 logistic, lbfgs, max_iter2000, random_state0, signed unconstrained constant coefficients; calibrated nested training-side OOF, no p/logit transform, no fused calibration |Original complete-modality study; later wrappers explicitly bypass fusion to surviving branch |
| External/Vi F2 |Same probability logistic formula |MSM:2-inner OOF fixed branches; Vi:3-inner OOF with T/V/C task roles; source-specific random_state; no outer labels |Explicit deterministic branch fallback; both absent undefined/abstain |
| F3 |sigmoid(MLP(LayerNorm([proj128(v128), proj128(s220)]))) |Weighted BCE feature-level model; inner grid hidden/epochs32/10 or64/20, three seed-mean predictions; new OOF calibrator |No inherent missing-branch semantics; inspect wrapper/masks |
| F4/F5/F6 |alpha=masked_softmax(MLP(context)); sigmoid(alphaV*l(pV)+alphaS*l(pS)) |Unweighted BCE; action4+availability2 / quality36+availability2 / both42; hidden8or16,40epochs; fit train-side OOF context and branch scores |Mask unavailable branch; surviving branch deterministic; both absent abstain |
| F6 dropout |Same gate |Training availability probabilities V-only.15, S-only.15, both.70 |Fallback is architectural, not proof learned robustness |
| Anchored constant/adaptive |sigmoid(b+sum ai*(1+tanh hi(u))*pi) |Fixed F2 anchor; two parameters or context42→16→2, zero final init; lambda0.01/0.1/1 penalties; training-side validation |Source modality_fallback handles missing inputs |
| Quality additive / interaction LR |sigmoid(b+w·[p, z8]) / sigmoid(b+w·[p, z8, pV*z8, pS*z8]) |C1 unweighted logistic with clean/imageaug/sensoraug sample weights.5/.25/.25; train-only weighted quality moments and clip±10 |Explicit fallback; both absent abstain |
| Vi quality / neutral gate |Masked logit gate,13→16→2 |11quality+2availability; neutral ablation sets quality tozero with identical capacity;40epochs, lr.001, wd.001, batch64; train-side OOF |Availability mask and explicit missing branch behavior |

F2 is **not** a softmax convex mixture and its coefficients need not sum to one or be positive. A quality-aware name alone does not identify a shared model: the legacy quality LR, neural logit gate and anchored probability adjustment are mathematically distinct. Quality dimensionality/meaning is adapted to the dataset; MSM38 input entries differ from Vi13. The original F4 uses action context, not measured signal quality.

Original REASSEMBLE F2 uses5outer×4inner plus nested branch-selection subfolds; its threshold comes from meta-crossfit balanced accuracy. The100e follow-up has one920-row genuinely base-held-out stacking bank, **not four100e inner folds**; fitted coefficients are retained, but its selection history and onefold/one seed limit inference. MSM uses fixed10epoch heads and fixed sensor LR; shared external frozen settings do not reproduce the original REASSEMBLE branch selection/calibration protocol exactly. Handover F2/gates have no fitted results because participant OOF cannot be certified.

OOF correctness requires each meta-training sample to be absent from its base fit, base selection and base calibration groups. Saved split/lineage checks support the intended grouping for REASSEMBLE/MSM/Vi; repeated use of exposed outer scores for later architecture proposals still makes the overall research program exploratory. Neither this audit nor the reports create a missing F2 fit.

PHM latent, scalar-decision and process-aware fusions combine **sensor sub-modalities**, not video plus sensors. Their scalar regression loss/output, provisional damage target and legacy LOEO preprocessing limitations prevent comparison to native-failure F2 AP.

## Evidence anchors

- [runs/reassemble/20260927T175336Z-section1b/assessment/results.json](../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json) — metrics, paired recording intervals, complementation.
- [runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json](../../../runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json) — five fitted F2 coefficient states.
- [src/reassemble/section1b.py](../../../src/reassemble/section1b.py) — fit_stacker; nested calibrated probability inputs.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json) — M1–M7 common-threshold metrics.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json) — conditional paired recording intervals.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json) — canonical sensor identities and stacking-bank limitations.
- [src/reassemble/section2_models.py](../../../src/reassemble/section2_models.py) — actual F3/gate forward.
- [src/reassemble/additional_improvements/models.py](../../../src/reassemble/additional_improvements/models.py) — anchored formula/fallback.
- [00_experiments/adaptive_fusion_robustness/code/quality_fusion.py](../../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py) — additive/interaction design and fitting.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
