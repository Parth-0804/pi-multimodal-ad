# Uncertainty and leakage limitations

All predictions concern complete native episodes. Canonical task separation is verified; session/operator independence remains unknown. This is development evidence on previously examined tasks. Intervals resample task clusters conditional on fixed fitted models; they exclude model refitting, seed variability, donor selection and unmeasured session/operator effects. Intervals crossing zero establish neither improvement nor equivalence. Pooled outer scores and mean-fold metrics are distinct; seeds are never pooled as additional examples. HGB remains a separate strong historical sensor baseline; beating LR does not imply beating HGB. No quality gate is introduced.

Paired task-cluster percentile 95% intervals use 2,000 draws and seed 20261111. Models share task draws. Single-class draws are discarded and counted. Per-task macro AP is unavailable when only one native class is present. Multiple comparisons are exploratory without multiplicity adjustment.

Each F2 meta record matches its branch assessment role and is disjoint from that branch T/V/C and outer task groups. Twenty-epoch meta coverage equals the complete outer-training set. Pilot 788 is excluded from visual gradient fitting, selection and calibration. Canonical sensor meta/test refit semantics are documented in report08. Exact meta and outer sensor vectors plus source model identities must match between paired arms.

The cohort manifests already contain native labels. F2 fitting consumes only meta labels and probabilities; outer prediction records are opened only after the persisted coefficient lock. This is procedural protection against outer-result tuning, not a claim that existing dataset labels were inaccessible.
