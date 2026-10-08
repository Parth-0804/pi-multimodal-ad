# Fitting-scope trace

Representative deep trace fixed before outcomes: outer0, inner0, additional sub0. Automated checks cover every available20 inner and80 additional branch-subfold identity manifests.

| Stage | Evidence | Evidence type | Finding |
| --- | --- | --- | --- |
| Cohort/splits | Frozen inventory filter and saved cohort; all5 outer/20 inner partitions; S1 feature row indices | Direct identity and partition inspection | All required assessment recordings separated; branch features are label-independent full-segment measurements |
| Branch scaling/fitting | section1_models.py Standardizer/logistic_fit/neural_fit; section1b.py fit_branch; outer0_inner0.json | Training source hashes and recorded partitions inspected | Normalizers use x[train]; epochs/C selected by subfold assessment confined to current training set |
| Branch calibration | section1b.py fit_branch -> calibrate(oof[selected][train], y[train], raw_test) | Source and saved calibration coefficients inspected | Outer/inner assessment labels absent from calibration arguments; original optimizer execution not independently replayed |
| Meta-training predictions | S1B stacking/outer0_inner0 plus subfold identities; S2 inputs/outer0_inner0_sub0 | Recorded row arrays and disjoint groups independently checked | Each meta row is branch-held-out; additional S2 depth excludes inner assessment from gate-training branch selection/calibration |
| F2 fit/threshold | S1B stacking/outer0.npz train_rows/test_rows and outer0.json stacker; fit_stacker source | Direct saved index/parameter evidence and source inspection | Only outer training branch OOF enters final stacker. Threshold crossfit is conditional on this bank; not independent full-pipeline inner performance |
| F6 normalizer/fitting | S2 F6_outer0_final_s0.json, train_outer and fit_head source | Independent numerical scaler check plus recorded inputs | Quality mean/std equal outer0 training-only metadata; no assessment labels accepted by fit_head |
| F6 selection/threshold | S2 outer0 inner candidates and predictions/outer0.json | Source/manifest trace | Configuration via mean inner AP; threshold via selected inner OOF. No final test selection; adaptivity of the study remains |
| Outer predictions | S1 fold pieces; S1B test_rows; S2 outer0 test_rows; global OOF keyed joins | Independent keyed parity checks | Correct cohort/splits and frozen scores; no GPU or model fitting performed in this trace |


Outer0 final F6 quality-scaler maximum mean/std differences: (0.0, 0.0).

## Provenance limits

- Exact original optimizer-step sample logs not retained; identities are recorded partition/source/provenance evidence, not a replay of every execution.
- Original S1 statistical-sensor scaler/model state not retained at its original fit; subsequent recovery parity is reported separately.
- Deep manual trace samples outer0/inner0/sub0; automated partition checks cover all20 inner and80 extra subfold manifests.
- F2 threshold-only crossfit conditions on the branch OOF bank, as originally declared; not an unbiased end-to-end inner score.

Status: COMPLETED_WITH_PROVENANCE_LIMITATIONS. No required assessment-recording overlap was found in the checked scopes. This does not certify every optimizer operation, historical cohort selection or independent study confirmation. Missing execution-level fit logs are PROVENANCE_GAP, not silently declared fully verified. F2’s conditional threshold crossfit is a declared training-only procedure and does not expose outer-test outcomes.
