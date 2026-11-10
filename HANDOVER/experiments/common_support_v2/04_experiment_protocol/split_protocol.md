# Split and leakage protections

Use the original official participant-based train/validation/test archives. Native counts337/101/151 become eligible335/101/151 under the pre-score common-support gate. Train only on the335 eligible training trials. Fixed validation is reported separately and never selects epochs/thresholds; it is not merged into training or test. No native participant IDs or mapping is supplied, so identity-level disjointness cannot be independently verified. Participant-OOF F2/F2_aug/QG_clean/QG_aug are BLOCKED, not replaced by trial-OOF or validation-set stacking. The five independently interpretable official-split baselines continue. No participant CI is fabricated from trial resampling.

All normalization, noise scales and imputations use only the relevant fit partition. Duplicate source video across official partitions is forbidden. No class-dependent frame selection, test-aware source checkpoint selection, target metadata features or in-sample F2 fit is allowed.
