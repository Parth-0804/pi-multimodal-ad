# Pre-training corrections

No real model was trained before these corrections; configuration, candidate variants, folds, budgets and tolerances are unchanged.

1. The new synthetic branch-fitting test failed because `atomic_npz(p, **arrays)` collided with the `p` probability-array keyword. Renamed the destination argument to `path`. The same test then passed, including invariance when only outer-test labels change.
2. Strengthened incomplete-write recovery: an already published equal NPZ is reused without modifying bytes/mtime; changed arrays are rejected. A synthetic preservation regression test passed.
3. Added explicit blocked reports for dependency/parity/runtime failures. A blocked run cannot claim COMPLETE or a scientific result class.

All eight synthetic tests passed after the prediction-writer correction, including pooled windows, trainable capacity, one-layer order sensitivity, multiplicity/classification, recording leakage rejection, outer-label invariance, immutable prediction reuse, and clustered-metric equivalence. The blocked-report addition was syntax checked. There is no claimed real GPU training/control parity result yet; that gate is deferred until Task4 completes.

Initial source signatures/snapshot remain in source_signature.initial.json (when different) and source/. Active signed implementation is captured in source_revision1/.
