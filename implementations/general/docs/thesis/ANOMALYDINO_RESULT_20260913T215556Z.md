# Can a learned change-detection label beat the CV heuristic? — 20260913T215556Z

**Verdict: no. Close the question. The rebuild is not justified.**

Twenty configurations of DINOv2 change detection were scored against the same
38 blind human calls the heuristic was scored against. **None reached the
heuristic's 78.9%.** The best was 76.3%, and that number is best-of-twenty
selected on the same 38 images, so it is optimistically biased and still lost.

This lands in the middle band of the stated decision rule — *"~80% → no better
than what you have; close the question"* — with the caveat, developed in §5,
that the two methods are statistically indistinguishable rather than the new
one being genuinely worse.

## 1. Method

For each of the 42 validated images, the nominal reference is **the same tooth
photographed at baseline** (`break_in` / `test_start` / `pre_run`) in the same
experiment. Every one of the 35 needed (experiment, tooth) pairs has such a
baseline, none missing, so this is genuine **change detection**, not generic
anomaly detection: a benign machining mark present at baseline is nominal for
that tooth and is not flagged.

DINOv2 patch features are extracted over the same ROI the heuristic measures;
each query patch is matched to its nearest baseline patch by cosine distance;
the image score aggregates those distances. Patch nearest-neighbour matching
tolerates the between-session camera misalignment that would defeat pixel
differencing. Banks are never pooled across experiments, so the rig/lighting
confound is not reintroduced through the reference.

**Fair comparison.** The score is converted to a call using the *same*
construction the heuristic's groups came from: within each experiment, rank the
14 validated images, call the top 7 damaged and the bottom 7 clean. Agreement
is against the 38 non-unsure human calls. Neither method gets a threshold fitted
on the humans.

Human calls were reconstructed from `INSPECTION_RESULT_20260913T204715Z.md`,
which records them losslessly (8 misclassified, 4 unsure, remainder correct by
construction). The reconstruction is checksummed against the report's own
30/38 and 4-unsure figures and fails loudly on mismatch.

## 2. The sweep

A single configuration losing would prove little, so bank, aggregation and
backbone were all varied. `docs/thesis/ANOMALYDINO_SWEEP.csv`.

| backbone | bank | aggregation | agreement |
|---|---|---|---|
| base | per-tooth | mean | 29/38 = **76.3%** |
| base | per-exp | mean | 29/38 = **76.3%** |
| small | per-exp | mean | 29/38 = **76.3%** |
| small | per-exp | top10% | 28/38 = 73.7% |
| base | per-exp | top10% | 28/38 = 73.7% |
| small | per-exp | top1% / top5% / max | 26/38 = 68.4% |
| base | per-exp | top1% / top5% | 26/38 = 68.4% |
| small | per-tooth | top10% | 26/38 = 68.4% |
| base | per-exp | max | 25/38 = 65.8% |
| base | per-tooth | top1% / top5% / top10% | 24/38 = 63.2% |
| small | per-tooth | top5% / mean | 24/38 = 63.2% |
| small | per-tooth | top1% / max | 23/38 = 60.5% |
| base | per-tooth | max | 23/38 = 60.5% |

|  |  |
|---|---|
| CV heuristic reference | **30/38 = 78.9%** |
| best configuration | 76.3% |
| median configuration | 68.4% |
| worst configuration | 60.5% |
| **configurations at or above the heuristic** | **0 of 20** |

The **pre-specified** AnomalyDINO configuration — its own published design, the
worst 1% of patches against a strict per-tooth bank — scores **60.5%**. Read
without hindsight, that is the honest single number, and it falls in the
*"<78% → worse"* band.

## 3. The aggregation ordering is backwards, and that is the finding

AnomalyDINO's design intent is that **localized** worst patches indicate
anomaly. Here the ordering is consistently inverted:

```
mean (all patches) > top10% > top5% ~ top1% > max (single worst patch)
```

`mean` wins in every bank/backbone combination and `max` loses in every one.
A whole-image mean distance is not a damage detector; it is a global appearance
difference. That the *least* localized statistic ranks best is direct evidence
that DINOv2 is not finding localized spall in these images — it is measuring
how different the whole tooth face looks from its baseline.

## 4. Confirmation: the winning configuration is largely a brightness measure

Cross-referencing against the photometrics already computed
(`PHOTOMETRICS.csv`), with both quantities ranked **within** experiment so the
between-rig offset cannot drive it:

| score | vs mean intensity | vs RMS contrast | vs Laplacian variance |
|---|---|---|---|
| base / per-tooth / mean (best) | **−0.519** | +0.037 | −0.417 |
| small / per-exp / mean | −0.401 | +0.008 | −0.496 |
| small / per-tooth / top1% (pre-specified) | −0.357 | +0.153 | −0.179 |
| **CV heuristic** | **−0.348** | −0.122 | −0.342 |

The best-performing DINO configuration tracks ROI brightness **more strongly
than the heuristic does** (−0.52 against −0.35). Its competitiveness is
substantially drawn from the same global photometric channel the heuristic was
already criticised for using, not from a cleaner view of damage. It is not an
independent second opinion.

## 5. What the numbers can and cannot resolve

This is the limitation to carry forward, and it constrains every band in the
decision rule.

| method | agreement | 95% CI (Wilson) |
|---|---|---|
| CV heuristic | 30/38 = 78.9% | [63.7%, 88.9%] |
| best DINO config | 29/38 = 76.3% | [60.8%, 87.0%] |
| median DINO config | 26/38 = 68.4% | [52.5%, 80.9%] |
| pre-specified DINO config | 23/38 = 60.5% | [44.7%, 74.4%] |

At n = 38 the binomial standard error near p ≈ 0.8 is about 6.5 pp, so the
78.9% / ~80% / >90% bands are **narrower than this sample can cleanly
resolve**. Concretely:

- **Paired McNemar, heuristic vs best DINO config**: heuristic-only-right 5,
  DINO-only-right 4, exact **p = 1.000**. Indistinguishable.
- **Paired McNemar, heuristic vs pre-specified config**: 10 vs 3, p = 0.092.
  Suggestive of the heuristic being better, not conclusive.
- **Rank correlation with the human call** is if anything marginally *higher*
  for the DINO scores: +0.631 and +0.626 against the heuristic's +0.606. The
  one-image gap in thresholded agreement is noise, not a quality difference.

So the strict reading is **not** "DINO is worse." It is that both methods
extract about the same amount of agreement with human judgement, roughly 60–80%
depending on configuration, and no configuration searched — including ones
chosen with hindsight — beat the incumbent.

**Chance floor.** Under random ranking with the identical top-7/bottom-7
construction (20,000 draws), mean agreement is 19.0/38 = 50.0%, 95% range
13–25. So P(random ≥ 30) = 0.0001 and P(random ≥ 29) = 0.0004: both methods are
comfortably above chance. But P(random ≥ 23) = 0.115, meaning the pre-specified
configuration's 60.5% is **not** itself distinguishable from chance.

## 6. Decision

Against the stated bands:

> \>90% → a better label is clearly achievable; the rebuild is justified.
> ~80% → no better than what you have; close the question.
> <78% → worse; the heuristic is doing more than it looks.

The result is **~80% at best and below 78% as pre-specified**, so the >90% band
is not in play under any configuration and the rebuild is **not justified**.
Both remaining readings point the same way operationally:

1. **Close the question.** A DINOv2 change-detection label is not a cheap
   upgrade path. Twenty configurations, two backbones, two bank definitions,
   five aggregations, and the incumbent was never beaten.
2. **The heuristic is doing about as much as a pretrained foundation model can
   do here**, which is a fair characterisation to carry into the write-up — and
   §4 suggests part of what *both* are doing is measuring brightness.

The binding constraint is not the labelling method. It is that ~20–40% of these
images are genuinely ambiguous to a human observer, and the earlier analysis
already located where: the high-damage class is much weaker than the
low-damage class (85.7% vs 57.1%), and the score range 1.5–4.8 pp was never
sampled. Neither of those is fixed by a better scorer. Both are fixed by
photographing the unsampled middle and by a second human rater — which remains
the only intervention identified that would actually move the label quality.

## Artifacts

| file | contents |
|---|---|
| `scripts/results/anomalydino_validated.py` | single-configuration scorer, call reconstruction, checksum |
| `scripts/results/anomalydino_sweep.py` | the 20-configuration sweep |
| `docs/thesis/ANOMALYDINO_SWEEP.csv` | agreement per configuration |
| `docs/thesis/ANOMALYDINO_SCORES.csv` | per-image scores, all 20 configurations |
| `docs/thesis/ANOMALYDINO_VALIDATED.csv` | per-image detail, pre-specified configuration |

Nothing under `gtc-data-experiment/**` was written, moved or modified; images
were read from the archives in memory. No target definition, config or run
directory was changed.
