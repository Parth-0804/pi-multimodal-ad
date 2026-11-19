# Interpretation of the supplementary short reference

The primary C versus B comparison uses the same checkpoint-selection rule,
candidate epochs, data partitions and exposure bounds. Its scientific target
is full-CNN adaptation versus an extended frozen-head control.

The supplementary A_r reference selects between B's epoch-5 and epoch-10
checkpoints. B selects among every executed epoch. Consequently, B minus A_r
combines an extended execution budget with a larger checkpoint candidate set.
For example, B can select epoch 9 while A_r selects epoch 5 or 10. Such a result
provides no evidence that execution beyond epoch 10 improved the chosen model.
Interpret this contrast as a budget-and-selection comparison. Attribution
specifically to additional exposure requires matching the short-horizon
checkpoint candidate set as well.

Historical A has further differences in feature precision, training partitions,
selection and calibration. Its verified AP values remain descriptive context.

This disclosure preserves the frozen experimental protocol, all model updates,
selected checkpoints and historical artifacts. It was added during the first
C training epoch, after the first B fit, with no new held-out AP or fusion
results used to change training or model selection. Recording-bootstrap
precision cannot remove this interpretation limitation.
