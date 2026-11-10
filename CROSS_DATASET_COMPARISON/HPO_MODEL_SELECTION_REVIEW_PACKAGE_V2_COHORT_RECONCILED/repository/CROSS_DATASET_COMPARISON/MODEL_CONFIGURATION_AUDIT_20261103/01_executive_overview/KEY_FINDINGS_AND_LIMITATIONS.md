# Key findings and limitations

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

1. The primary visual model is R18vd CNN only. The legacy hybrid encoder and PHM detector are separate architectures. Full C trains all executed CNN convolutions and promoted normalization affine parameters while keeping running moments fixed.
2. Small systematic grids did occur. Epoch selection,100-epoch budgets, seed repetition, calibration and coefficient fitting are distinct from broad optimizer HPO. Fit counts include candidates, controls and reconstruction refits.
3. The approved C20 cap is finished:25 fits, seed42, all five outer folds,20 epochs each. Fifty original fits are deferred and C20 F2 has not executed. Vi's75-fit completion gate and external transfer's25-epoch donor validator conflict with the present25-fit/20-epoch endpoint.
4. The100-epoch visual AP change0.193776→0.212585 is real on753 matched actions in one selected fold/seed. F2 AP0.334977→0.349094 is a point increase whose paired interval includes zero; generalized fusion improvement is not established.
5. Original pooled static F2 AP0.447299 and sensor AP0.429392 belong to a different five-outer protocol. MSM HGB and Vi HGB/LR provide essential strong sensor comparisons.
6. Handover participant IDs are absent. The official participant-disjoint claim cannot be independently certified, and fusion remains unexecuted. No identities were invented.
7. Vi's current4,382 episodes supersede the provisional4,384. Three seeds reuse the same assessment IDs. Failure prevalence0.856458 requires both-class metrics. Feature completion is not V2/V3 training completion.
8. PHM legacy LOEO normalization uses fixed EXP-B data outside changing fit folds. Summary/config target versions also conflict. These findings are preserved, not corrected within an audit.
9. C100's99.7% sampled training compute activity and7.77GiB allocated memory measure different things. The25.8937-hour total is paired active-child wall time, not pure C training or global GPU compute-hours.
10. Reproducibility is graded. A saved-state/prediction/metric chain can be complete while optimizer/RNG, full-history cost or independent assessment evidence is missing. No final architecture is selected.
