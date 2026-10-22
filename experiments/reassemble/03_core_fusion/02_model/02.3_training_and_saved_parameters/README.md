# 02.3 — Training and saved parameters

**Evaluation separation:** five outer folds hold out complete recordings; four inner folds select model settings within each outer training set. Segments from the same recording must not cross a train/test boundary. Each cohort row receives one outer-held-out prediction. This is cross-validation evidence, not a separately collected external test set.

For the single-modality neural branches, training uses weighted binary cross-entropy, AdamW (learning rate 0.001, weight decay 0.001), batch size 128, and gradient clipping at 1. The candidate epoch budgets are 5/10 for the visual head and 3/6 for PatchTST. Mean inner-fold average precision chooses the budget. Logistic calibration is fitted to selected inner out-of-fold logits. The threshold maximizes inner-OOF balanced accuracy on 0.01–0.99, with ties nearest 0.5. Thus a probability below 0.5 can still produce a failure decision.

**Fusion fitting:** the statistics classifier selects C from 0.1, 1 and 10. Training the stacker requires additional branch cross-fitting inside the outer training set; `section1b.py` builds these probabilities without using each validation recording for fitting its own branch. Meta cross-fitting chooses the fusion decision threshold. The outer test set is used for the final evaluation. Merely fitting a stacker to all globally saved OOF rows would not reproduce this nested protocol.

The learned stacker coefficients, intercepts and thresholds are saved as JSON, rather than a single fusion `.pt` checkpoint. These coefficients alone do not reconstruct the complete branch predictors.

[Five fitted stackers](../../../../../runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json)

- [Outer fold 0: branch choices, calibrators and stacker](../../../../../runs/reassemble/20260927T175336Z-section1b/stacking/outer0.json)
- [Outer fold 1: branch choices, calibrators and stacker](../../../../../runs/reassemble/20260927T175336Z-section1b/stacking/outer1.json)
- [Outer fold 2: branch choices, calibrators and stacker](../../../../../runs/reassemble/20260927T175336Z-section1b/stacking/outer2.json)
- [Outer fold 3: branch choices, calibrators and stacker](../../../../../runs/reassemble/20260927T175336Z-section1b/stacking/outer3.json)
- [Outer fold 4: branch choices, calibrators and stacker](../../../../../runs/reassemble/20260927T175336Z-section1b/stacking/outer4.json)

[Frozen recording splits](../../../../../runs/reassemble/20260927T154732Z-section1/nested_splits.json) · [Original run provenance](../../../../../runs/reassemble/20260927T175336Z-section1b/provenance.json)
