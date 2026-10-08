# Label and process-confound audit

Manifest rows: 2723 · sessions (DIRECTORY): 169 · categories: 12

## 1. Label structure

### Category counts and session support

| category | samples | sessions | binary |
|---|---|---|---|
| Good | 819 | **55** | Good |
| Excessive_Penetration | 480 | **25** | Defect |
| Burnthrough | 320 | **19** | Defect |
| Lack_of_Fusion | 320 | **16** | Defect |
| Porosity_w_Excessive_Penetration | 183 | **12** | Defect |
| Crater_Cracks | 161 | **12** | Defect |
| Excessive_Convexity | 160 | **9** | Defect |
| Overlap | 160 | **12** | Defect |
| Porosity | 109 | **6** | Defect |
| Spatter | 6 | **1** | Defect |
| Undercut | 4 | **1** | Defect |
| Warping | 1 | **1** | Defect |

Binary: Good 819 samples / 55 sessions; Defect 1904 samples / 114 sessions.

**Categories per session:** 169 of 169 sessions carry exactly one category; 0 carry more than one.

> CATEGORY is **constant within every session**. The label is a session-level property, so any sample-level split lets a model recover the label from session identity. Session-disjoint evaluation is mandatory, not merely preferable.

Session size: min 1, median 20, max 20.

### Supplied SPLIT

Sessions whose samples all share one SPLIT: **20** of 169. Sessions spanning multiple SPLIT values: **149**.

| SPLIT | samples |
|---|---|
| TEST | 1076 |
| VAL | 1071 |
| TRAIN | 576 |

> The supplied SPLIT is **NOT session-disjoint**. Samples from the same session — and therefore the same label — appear in different splits. It cannot serve as the primary protocol, and it is not retained as a secondary comparability protocol either, because results obtained under it are not comparable to session-disjoint results. Recorded as a dataset finding.

### Category against process variables

**WELD_TYPE** — 2 distinct values; 9 of 12 categories occur at exactly one value (Burnthrough, Crater_Cracks, Excessive_Convexity, Lack_of_Fusion, Overlap, Porosity…)
**STEEL_TYPE** — 2 distinct values; 4 of 12 categories occur at exactly one value (Porosity, Spatter, Undercut, Warping)
**THICKNESS_MM** — 2 distinct values; 12 of 12 categories occur at exactly one value (Burnthrough, Crater_Cracks, Excessive_Convexity, Excessive_Penetration, Good, Lack_of_Fusion…)
**CURRENT_A** — 24 distinct values; 3 of 12 categories occur at exactly one value (Spatter, Undercut, Warping)
**VOLTAGE_V** — 15 distinct values; 3 of 12 categories occur at exactly one value (Spatter, Undercut, Warping)
**GAS_BAR** — 12 distinct values; 6 of 12 categories occur at exactly one value (Excessive_Convexity, Overlap, Porosity, Spatter, Undercut, Warping)
**ROBOT_SPEED_CPM** — 4 distinct values; 7 of 12 categories occur at exactly one value (Burnthrough, Crater_Cracks, Overlap, Porosity, Spatter, Undercut…)

Distinct process-setting combinations per category (1 means the category has a single unique recipe):

| category | distinct recipes | sessions |
|---|---|---|
| Burnthrough | 16 | 19 |
| Crater_Cracks | 8 | 12 |
| Excessive_Convexity | 8 | 9 |
| Excessive_Penetration | 24 | 25 |
| Good | 28 | 55 |
| Lack_of_Fusion | 15 | 16 |
| Overlap | 8 | 12 |
| Porosity | 6 | 6 |
| Porosity_w_Excessive_Penetration | 12 | 12 |
| Spatter | 1 | 1 |
| Undercut | 1 | 1 |
| Warping | 1 | 1 |

**Recipe → category:** 125 distinct recipes; 122 map to exactly one category (98%).

## 2. Context-only shortcut classifier

Inputs: WELD_TYPE, STEEL_TYPE, THICKNESS_MM, CURRENT_A, VOLTAGE_V, GAS_BAR, ROBOT_SPEED_CPM. Excluded: CATEGORY, DIRECTORY, SAMPLES, SPLIT, SUBDIRS, is_defect, session.

> Categories excluded from the multiclass CV for having fewer than three independent sessions: **Spatter, Undercut, Warping**. They are NOT merged into other classes; they are reported as unsupported.

### binary Good vs Defect — session-disjoint 5-fold CV

| model | AUROC | macro-F1 | balanced acc | accuracy |
|---|---|---|---|---|
| A prior/majority | 0.411 | 0.411 | 0.500 | 0.699 |
| B logistic regression | 0.996 | 0.965 | 0.965 | 0.971 |
| C decision tree (depth 5) | 0.939 | 0.912 | 0.912 | 0.926 |
| D random forest | 0.958 | 0.948 | 0.948 | 0.956 |


### multiclass diagnosis (9 of 12 categories with >=3 sessions) — session-disjoint 5-fold CV

| model | AUROC(ovr) | macro-F1 | balanced acc | accuracy |
|---|---|---|---|---|
| A prior/majority | 0.367 | 0.052 | 0.111 | 0.302 |
| B logistic regression | 0.991 | 0.957 | 0.962 | 0.941 |
| C decision tree (depth 5) | 0.979 | 0.953 | 0.950 | 0.933 |
| D random forest | 0.989 | 0.942 | 0.939 | 0.926 |

### Permutation importance (random forest, binary, held-out fold)

| variable | mean AUROC drop when permuted | sd |
|---|---|---|
| THICKNESS_MM | +0.2451 | 0.0170 |
| GAS_BAR | +0.1525 | 0.0211 |
| VOLTAGE_V | +0.0445 | 0.0065 |
| ROBOT_SPEED_CPM | +0.0015 | 0.0017 |
| WELD_TYPE | +0.0001 | 0.0027 |
| STEEL_TYPE | -0.0016 | 0.0014 |
| CURRENT_A | -0.0048 | 0.0017 |

### Session-identity probe

How strongly do process settings identify the session? A high value means the recipe is close to a session fingerprint.

Session-ID accuracy from process settings alone: **0.863** over 154 sessions with >=2 samples (chance = 1/154 = 0.0065).

