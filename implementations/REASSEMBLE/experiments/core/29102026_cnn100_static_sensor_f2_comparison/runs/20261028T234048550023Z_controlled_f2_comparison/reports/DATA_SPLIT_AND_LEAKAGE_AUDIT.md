# Data split and leakage audit

| Role | Actions | Recordings | Failures |
|---|---:|---:|---:|
| CNN gradient T | 1752 | 60 | 198 |
| CNN checkpoint V | 419 | 15 | 44 |
| Visual calibration C | 686 | 19 | 93 |
| F2 base-model holdout | 920 | 28 | 97 |
| Outer assessment E | 753 | 26 | 77 |


These five roles partition all 4,530 eligible actions and148 recordings. Every pair has zero recording overlap. The outer753 IDs are identical across M1–M7 and have no duplicates. Native failure labels, recording IDs and segment IDs match the original cohort exactly.

The selected100-epoch CNNs use T for gradient fitting, V for checkpoint selection and686 C actions for calibration. Their original inner3 assessment bank (920 actions/28 recordings) is excluded from all three roles. The canonical inner sensor fits and calibrates from nested OOF within 2,857 actions that exclude these920 actions. Thus neither base branch uses its F2-bank assessment labels during fitting, selection, scaling or calibration.

For final outer prediction, the original sensor is refitted and OOF-calibrated on all 3,777 outer-training actions, including the F2-bank rows as ordinary outer training. This is the original stacking refit role, not test leakage: all753 test recordings remain excluded. F2 fitting itself opens only the 920 training-side banks and ID/group audit metadata; the complete cohort and outer probability files are opened only after the coefficient lock.

This single held-out bank is not a complete four-fold cross-fitted branch bank. We deliberately report holdout stacking and retain the historical complete-OOF result separately. No additional CNN fit is scientifically required for this fixed-model holdout comparison; reproducing the complete historical nested training design would be a different, larger study. The fixed-model comparison does not borrow predictions from the ongoing20-epoch75-fit visual study.

Four recording-disjoint meta folds within the 920 rows implement the original training-only F2 native-threshold rule and also provide an overfitting diagnostic. Their AP does not select hyperparameters or model weights. The common comparison table remains at0.5, and original native-threshold results are saved separately. Original fit 3 was chosen from previously observed20-epoch training-side validation across differing splits, and the outer fold was already inspected in the100-epoch study. This is an exploratory, post-selected follow-up rather than independent confirmation. Prior dataset exposure and possible selection effects are not removed by conditional bootstrap intervals.

Before fitting, source inspection clarified a stale selected-job `prediction_recordings` field inherited from inner3. Actual outer prediction IDs/recordings were derived from the saved cohort and checked directly. The clarification and sensor-role amendment are preserved in01. The two F2 models and protocol were serialized/hashed in `05_fusion_models/FUSION_FIT_LOCK.json` before calculating any new outer sensor/fusion score. That receipt includes the fitting/evaluation source identity. No test-derived hyperparameter or threshold search was performed.
