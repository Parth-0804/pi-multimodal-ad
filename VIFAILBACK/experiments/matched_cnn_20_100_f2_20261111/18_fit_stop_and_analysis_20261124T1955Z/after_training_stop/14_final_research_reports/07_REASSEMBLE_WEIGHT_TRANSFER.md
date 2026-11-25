# REASSEMBLE CNN donor

Source Full100 executed 100 epochs and selected epoch 47, seed 42. Donor SHA `5700e8912cf360c845087923e4b417631a886daf928e1655b1031c9ac27c8ce0`. Only 115 CNN tensor keys transfer; no source classifier, visual/sensor scaler, calibrator or F2 transfers.

DONOR20 and DONOR100 freeze the learned source CNN and fit new target heads under the corresponding matched target budgets. No separate donor target-domain CNN fine-tuning condition was declared.

DONOR20: seed 42, fold 0: delta -0.024263, 95% [-0.083623, +0.026911]; inconclusive; not equivalence; seed 42, fold 1: delta -0.010907, 95% [-0.039810, +0.018839]; inconclusive; not equivalence; seed 42, fold 2: delta -0.019905, 95% [-0.056637, +0.022343]; inconclusive; not equivalence; seed 123, fold 0: delta -0.004086, 95% [-0.024444, +0.036454]; inconclusive; not equivalence; seed 123, fold 1: delta -0.009456, 95% [-0.036981, +0.020411]; inconclusive; not equivalence; seed 123, fold 2: delta -0.005619, 95% [-0.047814, +0.037791]; inconclusive; not equivalence; seed 20261023, fold 0: delta -0.016995, 95% [-0.048555, +0.016889]; inconclusive; not equivalence; seed 20261023, fold 1: delta +0.002145, 95% [-0.036688, +0.053587]; inconclusive; not equivalence; seed 20261023, fold 2: delta +0.026008, 95% [-0.032273, +0.088120]; inconclusive; not equivalence; seed 42, fold pooled3: delta -0.016497, 95% [-0.032908, +0.001339]; inconclusive; not equivalence; seed 123, fold pooled3: delta -0.006219, 95% [-0.025260, +0.012160]; inconclusive; not equivalence; seed 20261023, fold pooled3: delta +0.004573, 95% [-0.021106, +0.035886]; inconclusive; not equivalence.

DONOR100: seed 42, fold 0: delta +0.020453, 95% [-0.015122, +0.051843]; inconclusive; not equivalence.

A valid learned-state load establishes mechanical transfer, not predictive benefit. The historical 25-epoch source validator was not weakened; this donor completed 100 epochs.
