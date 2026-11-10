# Final scientific conclusion

**Completed exploratory single-split study. No superiority, novelty or independent confirmation is assumed.**

| Model | AP | AUROC | Precision | Recall | F1 | Brier | Log loss | ECE15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Static sensor only | 0.327705 | 0.723680 | 0.666667 | 0.155844 | 0.252632 | 0.081479 | 0.292795 | 0.036268 |
| Frozen CNN + F2 | 0.334977 | 0.728675 | 0.615385 | 0.103896 | 0.177778 | 0.080453 | 0.289894 | 0.026295 |
| Fine-tuned CNN + F2 | 0.349094 | 0.740298 | 0.615385 | 0.103896 | 0.177778 | 0.080157 | 0.288338 | 0.028557 |

## Q1 — Does fine-tuning improve visual-only prediction?

+0.018809 [95% CI -0.036995, +0.095910]. The interval includes zero; an improvement is not established.

## Q2 — Does frozen CNN F2 improve over sensors?

+0.007273 [95% CI -0.003151, +0.015377]. The interval includes zero; an improvement is not established.

## Q3 — Does fine-tuned CNN F2 improve over sensors?

+0.021390 [95% CI -0.000345, +0.036358]. The interval includes zero; an improvement is not established.

## Q4 — Does fine-tuned F2 outperform frozen F2?

+0.014117 [95% CI -0.000773, +0.029089]. The interval includes zero; an improvement is not established.

## Q5 — Does F2 outperform simple averaging?

Frozen: -0.013029 [95% CI -0.033067, +0.003665]. The interval includes zero; an improvement is not established.

Fine-tuned: -0.009439 [95% CI -0.051172, +0.021666]. The interval includes zero; an improvement is not established.

## Q6 — Does better visual AP translate into better fusion?

Visual AP increased by +0.018809; fine-tuning also has a higher fusion AP point estimate. The paired fusion result is +0.014117 [95% CI -0.000773, +0.029089]. The interval includes zero; an improvement is not established. A visual-only gain does not guarantee complementary information beyond sensors.

## Q7 — How strong is the evidence?

All intervals are conditional on one selected fold and seed 42, with 77 failures across 26 assessment recordings. The outer set was already inspected and original fit 3 was post-selected from earlier validation. F2 training covers one genuinely held-out inner bank rather than all historical nested OOF folds. Sensor and visual final training sizes differ as documented; the M4/M5 sensor column and every comparison setting are held fixed. This does not justify a broader seed/fold, unseen recording-source, cross-dataset or deployment claim. The ongoing75-fit20-epoch study remains separate and was neither interrupted nor mixed into these results.

## Q8 — What happens when branches disagree?

7 unique real held-out cases are saved with predefined selection/support rules, actual native labels, probabilities from every fixed model,16 model-input frames, original frame/time mappings and source identities. The gallery includes correct and incorrect predictions where the corresponding category exists. F2 response follows the saved coefficient formula, not an oracle modality switch. [Open the disagreement gallery](../08_visual_diagnostics/HELDOUT_DISAGREEMENTS.html). These examples explain model behavior after fitting; they did not influence coefficients, calibration or model choice.

| Sample ID | Native failure | Fine-tuned visual p | Sensor p | Fine-tuned F2 p |
|---|---:|---:|---:|---:|
| 078658a8e5dc01dbee3d95ef | 1 | 0.147185 | 0.831071 | 0.783141 |
| 1dace0c0e2137e1f96f0e0ec | 1 | 0.105791 | 0.501833 | 0.393230 |
| 221874d13c9b26c8b37a1301 | 0 | 0.063554 | 0.530936 | 0.417285 |
| 8c931a578e30415438a0c2c6 | 1 | 0.180041 | 0.789772 | 0.752448 |
| dab16299508458550630e2c4 | 0 | 0.618485 | 0.055897 | 0.107571 |
| dba477e8fcfd70e655841f61 | 1 | 0.588149 | 0.073984 | 0.113208 |
| dbe71bb8aae5b4e7a4bbca2d | 0 | 0.065614 | 0.838305 | 0.773525 |

The sensor coefficient is about5.075 versus1.133 for the fine-tuned visual probability; these are probability-space coefficients, not normalized importance weights. In failure `dba477e8fcfd70e655841f61`, fine-tuned vision gives0.588149, the sensor0.073984 and fusion0.113208. Vision flags the failure at0.5, but fusion remains below its training-selected0.14 native threshold and misses it. In normal action `dab16299508458550630e2c4`, vision gives0.618485 (a false positive), the sensor0.055897 and fusion0.107571, below0.14, so fusion rejects the visual false alarm. Normal action `dbe71bb8aae5b4e7a4bbca2d` has a high sensor score0.838305 and fused score0.773525 despite a low visual score0.065614, retaining the false alarm. Thus the fitted model can suppress visual errors and useful visual exceptions; it does not always choose the correct branch. Common0.5 and original native-threshold decisions are both shown in the gallery. No mechanical cause is inferred from these probabilities or images.

## What was executed and independently checked

The two original100-epoch selected checkpoints were loaded and hash-verified. Canonical original static-sensor states were reconstructed and verified against the original saved probability banks/calibrators, which were reused for evaluation. Missing base-held-out CNN predictions were generated on CPU using the original 16 frames and pixel hashes. Two original-formulation logistic F2 models and group meta-crossfit diagnostics were fitted. Seven models were evaluated on identical753 IDs; historical M8 was reproduced separately. NumPy/rank implementations independently reproduced AP, AUROC, precision, recall, F1, Brier and log loss. The original fitter was also checked against a separate sklearn logistic construction. Paired recording-bootstrap results, all metrics, probability rows and report/figure source hashes are retained. No new CNN fit or test-label fitting was used.
