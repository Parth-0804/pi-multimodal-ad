# Parameters without systematic tuning evidence

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

No systematic validation-only full-CNN sweep was found for backbone LR, head LR, weight decay, batch/microbatch, dropout, normalization policy, optimizer family, schedule/warmup, frame count or augmentation strength. Twenty versus100 epochs changes budget and checkpoint selection. Historical16/32-frame and final-stage alternatives are exploratory model comparisons rather than a confirmatory optimizer search.

MSM/Handover external LR C, HGB learning rate/depth/regularization, visual-head optimizer/dropout and gate settings are predefined. Vi LR C, head LR/dropout and gate capacity/regularization were not systematically searched; Vi HGB leaf count was. Original F2 C is fixed1: fitting coefficients is not C tuning. Original sensor LR C, gate hidden widths and anchored penalties already have explicit grids.

Absent trials are not evidence of optimality. Omitted framework defaults remain unverified. These are audit findings, not authorization or proposed search ranges/budgets.
