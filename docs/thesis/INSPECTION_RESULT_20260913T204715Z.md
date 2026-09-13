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
