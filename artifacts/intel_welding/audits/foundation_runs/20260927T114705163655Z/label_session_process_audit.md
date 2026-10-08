# Label, session, process and supplied-SPLIT audit

Evidence directory: `artifacts/intel_welding/audits/foundation_runs/20260927T114705163655Z`. Manifest SHA256: `9c4fb4df70bb137fc851dd858ac22d53eed86ba08c3806d7177e40b300406826`.

CATEGORY describes intended conditions, not expert-verified physical defects.
Every one of the 236 sessions has one category. Session sizes range from 1 to 20
(median 20). DIRECTORY is the documented grouping unit; within-session label
constancy reinforces the need for grouped evaluation.

| CATEGORY | samples | sessions | readable | readable_sessions |
| --- | --- | --- | --- | --- |
| Burnthrough | 320 | 19 | 320 | 19 |
| Crater_Cracks | 161 | 12 | 161 | 12 |
| Excessive_Convexity | 160 | 9 | 160 | 9 |
| Excessive_Penetration | 480 | 25 | 480 | 25 |
| Good | 819 | 55 | 819 | 55 |
| Lack_of_Fusion | 320 | 16 | 320 | 16 |
| Overlap | 160 | 12 | 160 | 12 |
| Porosity | 340 | 17 | 109 | 6 |
| Porosity_w_Excessive_Penetration | 480 | 27 | 167 | 12 |
| Spatter | 320 | 17 | 6 | 1 |
| Undercut | 160 | 9 | 4 | 1 |
| Warping | 320 | 18 | 1 | 1 |

The supplied split has 576 TRAIN, 1,732 VAL and 1,732 TEST samples. A total of
216/236 sessions cross supplied splits; only 20 are confined to one split.
Reject this protocol for the primary and conditional secondary comparisons.
No model was evaluated on it in this pass.

All seven legitimate manifest process fields have complete category crosstabs
(`category_*.csv`). `session_category.csv` retains the full session–category map.
Every category occurs at one thickness: Good uses 7 mm; Burnthrough,
Excessive_Penetration and Porosity_w_Excessive_Penetration use 3 mm; the remaining
conditions use 7 mm. Thickness alone cannot separate all Good/non-Good samples,
but is an obvious recipe shortcut for some categories.

Across the full manifest, 164 of 175 distinct seven-field recipes map to one
category, and 11 map to two. In the complete-present subset, 122 of 125 recipes
map to one category. These are descriptive associations, not validated predictive
performance. No fields were selected or dropped based on model outcomes.

The prior context report contains model scores over the complete-present
population. Its script lacks a development-only filter. Do not reuse those
scores as valid development-only or final-test results. The current deliverable
is the unexecuted context specification in
`docs/intel_welding/context_baseline_specification.md`.
