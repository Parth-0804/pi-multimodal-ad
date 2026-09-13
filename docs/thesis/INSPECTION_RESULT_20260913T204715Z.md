# Blind inspection result — 20260913T204715Z

Source: FORM 2 (returned zips)
Key: `scratch/blind_inspection/_KEY_DO_NOT_OPEN/key.csv`

```
====================================================================
WITHIN EXPERIMENT — the confound check, read this first
====================================================================
  EXP-A: 10/14 =  71.4%   p = 0.1796
  EXP-B: 9/11 =  81.8%   p = 0.0654
  EXP-F: 11/13 =  84.6%   p = 0.0225

====================================================================
OVERALL
====================================================================
  accuracy (unsure excluded): 30/38 = 78.9%
  two-sided binomial vs 50% : p = 0.0005
  unsure, excluded          : 4
  rank correlation (clean=0, unsure=1, damaged=2) vs score: rho = +0.6007

MISCLASSIFIED (8)
  img_990d6704.jpg  EXP-A run  3 tooth 26  score  1.310  actually  low  called damaged
  img_f4966712.jpg  EXP-A run  5 tooth 27  score  1.457  actually  low  called damaged
  img_d35c9342.jpg  EXP-A run  2 tooth 24  score  1.534  actually  low  called damaged
  img_31b7de6f.jpg  EXP-F run  5 tooth 18  score  5.275  actually high  called clean
  img_c733caf2.jpg  EXP-A run  4 tooth 15  score  5.533  actually high  called clean
  img_f1ecb984.jpg  EXP-B run  4 tooth  8  score  5.600  actually high  called clean
  img_27818e63.jpg  EXP-B run  4 tooth  5  score  5.687  actually high  called clean
  img_01db6e1d.jpg  EXP-F run  5 tooth 22  score  7.420  actually high  called clean

UNSURE (4)
  img_c52e51b0.jpg  EXP-B run  1 tooth 17  score  4.943  actually high
  img_4e05d267.jpg  EXP-B run  4 tooth 18  score  4.995  actually high
  img_45c5738a.jpg  EXP-F run  5 tooth 20  score  5.829  actually high
  img_f3b88a1b.jpg  EXP-B run  5 tooth 15  score  8.793  actually high

====================================================================
VERDICT
====================================================================
  INTERMEDIATE. Above chance but short of convincing. Read the
  misclassified list: errors clustering near the score boundary mean
  a noisy label; errors spread across the range mean a wrong one.

  n = 38 scored, 4 unsure. Treat p-values as indicative.
```

## Asymmetry between the two groups

|                | called damaged | called clean | called unsure |
|----------------|----------------|--------------|---------------|
| actually high  | 12             | 5            | 4             |
| actually low   | 3              | 18           | 0             |

- low group:  18/21 = **85.7%** correctly called clean
- high group: 12/21 = **57.1%** correctly called damaged

The two directions are not equally reliable. Clean teeth are recognised as
clean most of the time; teeth the heuristic scored as heavily damaged are
confirmed as damaged only about half the time, with 5 called clean outright
and 4 more marked unsure. Every one of the 4 unsure images came from the high
group.

The extremes make the point sharpest. If the score tracked visible damage, the
very highest-scoring images should be the easiest to call:

| score | experiment / run / tooth | human call |
|-------|--------------------------|------------|
| 8.793 | EXP-B run 5 tooth 15     | **unsure** |
| 7.420 | EXP-F run 5 tooth 22     | **clean**  |
| 7.233 | EXP-A run 4 tooth 28     | damaged    |
| 7.049 | EXP-A run 4 tooth 25     | damaged    |
| 6.395 | EXP-F run 6 tooth 21     | damaged    |
| 6.033 | EXP-A run 5 tooth 28     | damaged    |

The single highest-scoring image in the entire set could not be called, and
the second highest was called clean.

## Reading

Three of the eight errors are boundary errors in the expected direction: the
false positives scored 1.310, 1.457 and 1.534, which are the top three values
of EXP-A's low group (range 1.199-1.534). Those are the label being noisy near
its own threshold, which is unremarkable.

The false negatives are not all boundary errors. Four sit just inside the
bottom of the high range, but img_01db6e1d at 7.420 is near the TOP of EXP-F's
high range and was still called clean. Combined with the 8.793 image being
unsure, that means the upper end of the score range is not reliably visible
damage.

So the label carries real signal -- rho = +0.60 and p = 0.0005 are not nothing,
and the confound check passes, with every experiment above chance individually
(71.4 / 81.8 / 84.6%). But its high-damage class is much weaker than its
low-damage class, which is consistent with the heuristic responding partly to
dark elongated features that are not spall.

Note the verdict band: 78.9% fell 1.1 points short of the 80% threshold for
"tracks visible damage", a margin of a single image.

## Where does reliability fall off? — descriptive binning

**Short answer: this set cannot show that, and the reason is structural rather
than small-sample.** The selection took the 7 highest and 7 lowest scores per
experiment, so the middle of the score range was never photographed into the
set. There are **zero images between 1.534 and 4.777 pp**. Any apparent
"falloff" between the two clusters is a jump across an unsampled gap, not a
measured transition.

### 1. Bin counts

Fixed bins:

| bin (pp) | n | agreement (unsure excluded) | unsure | group content |
|---|---|---|---|---|
| 0.0 – 2.0 | 21 | 18/21 = **85.7%** | 0 | all low |
| 2.0 – 5.0 | 3 | 1/1 | 2 | all high, all EXP-B |
| 5.0 + | 18 | 11/16 = **68.8%** | 2 | all high |

Quartiles of the observed range (0.285–8.793, width 2.127):

| quartile | n | agreement | unsure |
|---|---|---|---|
| Q1 0.28–2.41 | 21 | 18/21 | 0 |
| **Q2 2.41–4.54** | **0** | — | — |
| Q3 4.54–6.67 | 17 | 10/14 | 3 |
| Q4 6.67–8.79 | 4 | 2/3 | 1 |

One quartile is empty and another holds three images. The bins are too sparse
and too unevenly placed to locate a transition.

### 2. Highest score with high agreement / lowest with falloff

Not answerable as posed. Agreement is 85.7% across the whole low cluster
(0.285–1.534) and 68.8% across the whole high cluster (4.777–8.793), with
nothing in between. The most that can be said is that agreement is higher
below 1.534 than above 4.777.

Within the high cluster, agreement does **not** decline with score. Ordered by
score, with `x` marking a disagreement including unsure:

```
.  x  x  .  .  x  x  .  x  x  .  .  x  .  .  .  .  .  .  x  x
4.78 ------------------------------------------------> 8.79
```

Disagreements sit at the **bottom** of the high range (4.94, 5.00, 5.28, 5.53,
5.60, 5.69, 5.83) and at the **extreme top** (7.42, 8.79), while 5.84–7.23 is
almost entirely correct. That is not a monotone falloff, so the requested
summary sentence of the form "agreement is high below approximately X pp and
falls off above it" **does not apply and is not offered**.

### 3. Do the UNSURE calls cluster?

Partly. The four unsure scores are **4.943, 4.995, 5.829, 8.793**. Two are
adjacent and are the second- and third-lowest scores in the entire high group,
which is consistent with hesitation just inside the damaged class. The other
two are not: one mid-range, and one is the single highest score in the set.

### 4. Do misclassifications cluster by experiment, or by run?

**By run, clearly; by experiment, not at all.**

By experiment, disagreements are almost perfectly flat — EXP-A 4/14,
EXP-B 5/14, EXP-F 3/14. This is the same conclusion the confound check reached
from the other direction: experiment identity is not driving the errors.

By run, they concentrate sharply:

| run | disagreements / images from that run |
|---|---|
| **EXP-B run 4** | **3 of 3** |
| **EXP-F run 5** | **3 of 4** |
| EXP-B run 1 | 1 of 3 |
| EXP-B run 5 | 1 of 2 |
| EXP-A run 4 | 1 of 4 |
| EXP-A runs 2, 3, 5 | 1 each |

Every image drawn from EXP-B run 4 was disputed, and three of four from EXP-F
run 5. Six of the twelve disagreements come from those two runs alone.

That is the most actionable thing in this section. It points at per-run
photographic conditions — a lighting or focus change in one inspection session
— rather than at the score being wrong across the board. It also matches the
limitation recorded for the odd/even split test: that analysis separates
per-photo noise from run-level effects but cannot distinguish run-level damage
from run-level lighting, and this is what a run-level effect looks like.

### What would answer the original question

Images sampled from the **unsampled middle**, roughly 1.5–4.8 pp. Around 20
images spread across that band, blinded the same way, would show whether
agreement declines gradually or breaks at a particular value. Nothing in the
present set can substitute for that.
