# Section1B runtime correction, before fusion results

The one-thread observed-sensor reproduction selected identical C values in all
five folds, but the C=10 L-BFGS refit used460 iterations versus442 originally.
Maximum probability difference was0.0059373071, exceeding the predeclared1e-5
parity tolerance. AUROC/AP were0.779403/0.429780 versus frozen0.779325/0.429392.
The strict guard stopped the run before any permutation or fusion results.

Restore the original16 OpenBLAS threads. Do not relax parity tolerance, change
features, solver, regularization, model budgets or scientific decision thresholds.
All original attempt files remain in runs/reassemble/20260927T174424Z-section1b.
This runtime correction supersedes only the one-thread execution setting in the
initial protocol. A fresh versioned run is used; the same Section1 evidence is
still immutable. The diagnostic command also had an unnecessary terminal import
without src on sys.path; it failed after printing metadata and wrote no results.
