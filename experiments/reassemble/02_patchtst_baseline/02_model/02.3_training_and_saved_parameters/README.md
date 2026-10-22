# 02.3 — Training and saved parameters

**Evaluation separation:** five outer folds hold out complete recordings; four inner folds select model settings within each outer training set. Segments from the same recording must not cross a train/test boundary. Each cohort row receives one outer-held-out prediction. This is cross-validation evidence, not a separately collected external test set.

For the single-modality neural branches, training uses weighted binary cross-entropy, AdamW (learning rate 0.001, weight decay 0.001), batch size 128, and gradient clipping at 1. The candidate epoch budgets are 5/10 for the visual head and 3/6 for PatchTST. Mean inner-fold average precision chooses the budget. Logistic calibration is fitted to selected inner out-of-fold logits. The threshold maximizes inner-OOF balanced accuracy on 0.01–0.99, with ties nearest 0.5. Thus a probability below 0.5 can still produce a failure decision.

**Saved weights:** each checkpoint stores `state_dict`, model kind, width, config, normalizer mean/std and chosen epochs. The calibration coefficients and decision threshold are in its corresponding prediction JSON, not inside the neural state dictionary. Fold numbers below match the originals (0–4).

| Outer fold | Trained weights | Training selection and calibration |
|---|---|---|
| 0 | [Checkpoint](../../../../../runs/reassemble/20260927T154732Z-section1/checkpoints/patchtst_fold0.pt) | [Fold details](../../../../../runs/reassemble/20260927T154732Z-section1/predictions/patchtst_perm00_fold0.json) |
| 1 | [Checkpoint](../../../../../runs/reassemble/20260927T154732Z-section1/checkpoints/patchtst_fold1.pt) | [Fold details](../../../../../runs/reassemble/20260927T154732Z-section1/predictions/patchtst_perm00_fold1.json) |
| 2 | [Checkpoint](../../../../../runs/reassemble/20260927T154732Z-section1/checkpoints/patchtst_fold2.pt) | [Fold details](../../../../../runs/reassemble/20260927T154732Z-section1/predictions/patchtst_perm00_fold2.json) |
| 3 | [Checkpoint](../../../../../runs/reassemble/20260927T154732Z-section1/checkpoints/patchtst_fold3.pt) | [Fold details](../../../../../runs/reassemble/20260927T154732Z-section1/predictions/patchtst_perm00_fold3.json) |
| 4 | [Checkpoint](../../../../../runs/reassemble/20260927T154732Z-section1/checkpoints/patchtst_fold4.pt) | [Fold details](../../../../../runs/reassemble/20260927T154732Z-section1/predictions/patchtst_perm00_fold4.json) |

[Frozen recording splits](../../../../../runs/reassemble/20260927T154732Z-section1/nested_splits.json) · [Original run provenance](../../../../../runs/reassemble/20260927T154732Z-section1/provenance.json)
