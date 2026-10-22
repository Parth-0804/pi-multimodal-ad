# Other core fusion comparisons

Section 2 compares these on the same recording-held-out cohort:

| Original name | Meaning |
|---|---|
| U1 | Sensor-statistics classifier |
| U2 | RT-DETR visual classifier |
| F1 | Uniform average of branch probabilities |
| F2 | Section 1B static logistic stacker; main walkthrough in this folder |
| F3 | Learned feature concatenation (128 visual embedding + 220 statistics) |
| F4 | Process-conditioned gate |
| F5 | Quality-conditioned gate |
| F6 | Process-and-quality-conditioned gate |

F4–F6 combine branch logits using learned context-dependent weights. They are distinct from F2's regression on two probabilities. Read their configured context and calibration in the linked implementation.

- [Comparison report](../../../../runs/reassemble/20260927T192852Z-section2/assessment/SECTION_2_FUSION_HANDOFF.md)
- [All metrics and paired comparisons](../../../../runs/reassemble/20260927T192852Z-section2/assessment/results.json)
- [Saved predictions for U1/U2/F1–F6](../../../../runs/reassemble/20260927T192852Z-section2/predictions/oof.npz)
- [Selected hyperparameters](../../../../runs/reassemble/20260927T192852Z-section2/assessment/selected_hyperparameters.json)
- [Gate weight summaries](../../../../runs/reassemble/20260927T192852Z-section2/assessment/gate_weights.json)
- [Experiment configuration](../../../../runs/reassemble/20260927T192852Z-section2/config.json)
- [Model definitions](../../../../src/reassemble/section2_models.py)
- [Context and model-input assembly](../../../../src/reassemble/section2_data.py)
- [Nested fitting and prediction orchestration](../../../../src/reassemble/section2.py)

The Section 2 NPZ uses keys such as `F1_p`, `F2_p`, `F3_p`, plus corresponding `_hard` arrays, shared `y` and `fold`. Use these named keys instead of expecting the plain `p` key found in the Section 1B file.
