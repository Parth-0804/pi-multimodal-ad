# Section 2 attempts and corrections

Before modelling, one patch invocation failed because the sandbox helper could not
configure its loopback interface. No part of that failed patch was applied. The
same scoped changes were applied through the approved shell execution path.

A preflight read found no pyproject.toml; this repository uses its documented
PYTHONPATH=src test entry point. No package metadata was invented.

The quality loader was hardened before tests to select only the frozen cohort
segments, skipping unrelated invalid annotations. Undefined gripper MAD-outlier
quality (1,562 rows) uses training-only mean imputation; cohort and features unchanged.

No Section 2 model fit has failed or been used to expand the predefined search.

## Final review

Complete computation exited 0 with no model failures or numerical warnings.
The automatic point-AP shortlist (F5) was corrected to F4 in the reviewed report
after paired uncertainty, calibration, seed stability and parameter cost were
considered. Original generated outputs remain intact. Three post-hoc descriptive
paired contrasts support this review; no training or primary criteria changed.
See assessment/review_decision.json and review_comparisons.json.
