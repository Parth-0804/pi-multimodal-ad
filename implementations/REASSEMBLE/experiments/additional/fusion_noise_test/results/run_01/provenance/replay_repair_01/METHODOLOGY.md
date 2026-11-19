# Technical replay repair 01

The original selection and corruption locks are preserved byte for byte. No model fitting, model substitution, threshold or tolerance change is made.

The initial clean replay passed 61 rows then stopped. A read-only diagnosis found that reconstructed sensor statistics used float64 reductions, while upstream casts the concatenated resampled signals to float32 before computing statistics. The original implementation and diagnosis are archived here. A regression against the actual upstream pure functions failed before correction and passes afterwards. The failed real row now reproduces every saved sensor feature and its sensor probability exactly. Visual pooling/standardization are also restored to the original Torch arithmetic.

The revision record binds the original source snapshots, original selected-model lock, fixed configuration, repaired source hashes, and passing tests. Resume accepts this one specific technical revision, verifies unchanged components, and must replay the entire selected clean bank again before any corrupted assessment inference. This is repair of reconstruction fidelity, not a new scientific selection. Full replay remains pending until runtime evidence says otherwise.
