# ARCH-VAL-PB — Gate 3 pre-registration

**Written and committed before any Gate 3 model is trained. Contains no results.**

Gate 3 runs only if Gate 2 passes. At the time of writing, Gate 2 has not
returned a verdict, so this document is written blind to it.

## Question

Does pairwise rank distillation from a privileged modality improve a
sensor-only model, on an independent dataset where the privileged modality
demonstrably carries signal?

This validates one mechanism. It is not a Paderborn fault-diagnosis study.

## Mechanism under test

`pairwise_rank_loss` in `scripts/paderborn/common.py` is copied verbatim from
the PHM implementation in `scripts/results/closing_task_c.py` and verified
equal to it on random and degenerate inputs. The mechanism is not re-derived.

Total loss for the distilled arm:

    L = MSE(student(vibration), severity) + w * pairwise_rank_loss(student_out, teacher_out)

The teacher is the same frozen MLP trained on motor-current features on the
training fold; the teacher signal is its predictions on the training rows.
Teacher and student see the same training rows. The teacher is never fitted
on, and never sees, the held-out fold.

## The four arms

| # | arm | features at train | features at inference |
|---|---|---|---|
| 1 | constant | — (training mean) | — |
| 2 | vibration only | vibration | vibration |
| 3 | **vibration + rank distillation** | vibration + current (as teacher only) | **vibration** |
| 4 | oracle | vibration + current | vibration + current |

Row 3 is the architecture. Row 4 is not deployable and exists to quantify what
the privileged modality is worth.

## Frozen hyperparameters

Identical for every arm and every fold. Not tuned at any point, and never
adjusted against a held-out condition.

| | |
|---|---|
| model | MLP, hidden (64, 32), ReLU, dropout 0.1 |
| optimiser | Adam, lr 1e-3, weight decay 1e-4 |
| epochs | 120 |
| batch size | 256 |
| feature scaling | StandardScaler, scale floored at 1e-3, inputs clipped to ±10 |
| seeds | 0, 1, 2 (all arms share them) |

The scale floor and clip are a numerical guard against near-constant context
features inside one operating condition; they are applied identically to all
arms and were fixed before Gate 3.

## Protocol

Leave-one-operating-condition-out **with bearings also held out**: the test
fold is (held-out condition) x (held-out bearings); training is (other three
conditions) x (other bearings). Rationale: severity is constant per bearing,
so condition-only holdout lets a model recognise the bearing and recall its
label. 4 conditions x 4 bearing folds; every row predicted exactly once.

Metric: MAE on fact-sheet severity. Intervals: bearing-clustered bootstrap,
2000 resamples, percentile. Paired comparisons resample bearings and take the
difference on the same rows.

## Distillation weight and the selection rule

Swept over w ∈ {0, 0.1, 0.3, 1.0, 3.0}.

- **w = 0 must reduce row 3 exactly to row 2.** This is asserted numerically
  as a correctness test, not eyeballed. If it does not hold, the run is void.
- **The primary pre-specified weight is w = 1.0.** The headline result is
  row 3 at w = 1.0 versus row 2.
- The rest of the sweep is reported descriptively. Because any best-of-sweep
  value is selected on the held-out data, it is optimistically biased and
  will be labelled as such. It cannot be the headline.

## What counts as the architecture transferring

Decided now, in advance.

- **(a) TRANSFERS** — paired MAE(row 3 at w=1.0) − MAE(row 2), bearing-clustered
  95% CI, lies entirely below zero.
- **(b) MECHANISM-LEVEL NEGATIVE** — that interval includes zero, but the oracle
  gap MAE(row 4) − MAE(row 2) lies entirely below zero. The privileged modality
  carries information this mechanism fails to transfer; the gap quantifies
  what was left on the table.
- **(c) PRIVILEGED MODALITY ADDS LITTLE** — both intervals include zero and the
  oracle gap point estimate is small.
- **(d) UNDERPOWERED** — intervals span zero everywhere and are wide. Report
  widths; do not describe a point estimate as a direction.

All four are reportable outcomes. None is preferred. No arm will be re-run
after its result is seen, no variant added, and no threshold moved.

## Stopping and scope

- If Gate 2 fails, Gate 3 does not run and this document stands unused.
- The artificial-to-real domain shift is a separate, secondary analysis,
  reported separately and never merged with the above.
- No Paderborn number will be placed in a table with a PHM number.

## Citation

Lessmeier, C., Kimotho, J.K., Zimmer, D., Sextro, W. (2016). *Condition
Monitoring of Bearing Damage in Electromechanical Drive Systems by Using Motor
Current Signals of Electric Motors: A Benchmark Data Set for Data-Driven
Classification.* European Conference of the PHM Society, 3(1). CC BY-NC 4.0.
