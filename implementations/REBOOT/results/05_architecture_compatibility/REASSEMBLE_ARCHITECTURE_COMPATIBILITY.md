# REASSEMBLE/MSM architecture compatibility

Inspected actual sources: `src/reassemble/section1_features.py`, `section1_models.py`, `section1b.py`, `section2_models.py`, `MILLING DATASET/source/msm/{data,models,splits}.py` and `CROSS_DATASET_COMPARISON/src/external_eval/{features,data,models,evaluate}.py`. Their exact hashes are in the run software provenance. None were changed.

| Branch/component | Feasible reuse | Required REBOOT-specific work/gate |
|---|---|---|
| RGB input |16 real640×480 RGB frames from a fixed chosen view | New pinned LeRobot-v3 episode/video offset adapter; CPU AV1 decoder; retain original frame/time mapping. Freeze view and observation window before evaluation. |
| Frozen visual CNN | Existing pinned PekingU/rtdetr_r18vd ResNet R18vd backbone, spatial means of last3 maps→896 and16-frame temporal mean | New fold-fitted standardizer and896→128→1 head after trustworthy labels. No detector transformer or bounding-box head; no CNN executed here. |
| Numerical measurements |14 observed joint/gripper positions | New feedback-only allowlist and unit/clock documentation; mean, population std, RMS, min, max and peak-to-peak would give84 values. This differs from MSM90 and Handover36. Standardization must be fitted within training folds. |
| Commanded actions | Preserved for audit only | `action` must not be passed off as an independent measured sensor. Exclude from primary sensor model; any command-conditioned control needs separate explicit experimental labeling. |
| Sensor baselines | Balanced logistic and fixed strong sensor-only classifier can use verified position statistics | New labels/domain coefficients and train-only scaling; no force/torque, effort or velocity fabrication. Units/angular wrap handling need explicit methodology. |
| Averaging / F2 | Existing two-probability averaging; newly fitted logistic F2 on true group-OOF probabilities | No source fusion coefficients transferred; identity-safe2-inner OOF and3-outer design must first pass actual group/class gates. Currently blocked. |
| Quality-aware fusion | Existing DecisionGate plus explicit new label-free quality adapter could be investigated |14-channel quality context and availability flags differ from previous domains. Requires enough independent OOF support and matched static/augmentation controls; no evidence currently justifies training it. |
| Depth | Four full-release schema columns exist | Not needed for the requested RGB/state baseline; sample has none. Using depth would be a separate new architecture experiment and requires actual value/calibration validation. |

The existing16-frame mean is order-invariant. A visibly dynamic drop does not prove that this representation models temporal order; a separately preregistered temporal ablation may be useful later. Do not silently replace the representation or claim motion understanding.

Position feedback can encode robot phase and human recovery behavior. Diagnostic windows deliberately include recovery context and are not classification-ready inputs. A future detection protocol must define whether it is retrospective event recognition or early warning, freeze the causal time horizon and prevent recovery/future-action leakage. The current task trains no model and transfers no learned weights.
