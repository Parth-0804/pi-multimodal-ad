# Self-review — selected-model robustness pilot

This is an implementation self-review, not an independent reviewer assessment.

## Established evidence

- The actual pinned visual study is terminal BLOCKED, with one completed frozen_16_frames outer fold. The encoder study stopped WAITING_FOR_GPU with zero paired completed folds. No upstream training was resumed or changed by this task.
- Selection followed the fixed terminal partial-coverage rule. The canonical original-representation reference is retained because all four newer variants have zero usable completed folds, not because they were measured as worse. The selection includes exactly fold_01: 753 actions, 26 recordings, 77 failures.
- Saved clean predictions independently recalculate fused AP 0.30792883536861149, visual AP 0.20040089231459993, and sensor AP 0.29053050930334789. These are upstream stored probabilities, not a completed new clean replay.
- Per-fold model/checkpoint/config references and hashes are bound in selected_model.json. The selection lock is unchanged through technical repair 01. The original selected source is archived; the explicitly admitted repair binds both old and new hashes and passing tests.
- Fifteen focused CPU tests pass. The added float32 regression failed before repair and passed after it. Tests include actual local original-weight CPU prefix inference on synthetic inputs, prohibited-path guards, frozen state, deterministic corruption semantics, membership/eligibility rules, and metric arithmetic. This is distinct from scientific assessment inference.
- Actual GPU execution occurred only after the earlier GPU owner stopped. Training-only runtime timing and input invariance checks passed. Initial live clean replay passed 61 rows, then stopped before any corrupted assessment inference.
- The failed row exposed float64 sensor reductions where the original model used float32. After restoring original precision/layout, all 220 saved sensor features and the calibrated sensor probability match exactly for that row. Full repaired clean replay remains required.

## Evidence limitations

The initial implementation accumulated clean prediction rows in memory and failed before committing the fold. Its 61 passing per-frame feature caches remain, and checks/initial_clean_replay_coverage.csv identifies those rows, but their exact runtime probabilities were not persisted. They are not reconstructed from upstream probabilities or claimed as a complete prediction table. The repaired failure path saves partial rows and discrepancy tables if replay fails again.

No damaged-input assessment predictions, raw training noise-scale estimates, robustness metrics, absence-policy measurements, or image-versus-sensor sensitivity findings exist at this stop. There is no defensible robustness conclusion. Empty metric templates are not measurements.

A distinct two-epoch visual training run took the sole allocated GPU after the failed clean replay. Its outputs are not substituted into the locked five-epoch candidate comparison. Its process is neither interrupted nor modified. The bounded foreground wait does not queue a later job.

The study is DEVELOPMENT-EXPOSED and a one-fold pilot. It does not establish the best architecture from a completed comparison, independent generalization, deployment robustness, adaptive fusion benefits, or causal modality importance. Preserved historical/other dirty-tree changes are outside this task.
