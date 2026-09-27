# RAW-VIB — recovering the vibration signal the pipeline never used

**Steps 0–3 executed. L1 is NEGATIVE in EXP-F. Steps 4 (L2/L3) were not run,
per the stop condition.**

## Outcome

The 102.4 kHz `Vibration/Accel 1`, `Accel 2` and `Encoder` channels were read
for the first time, order-tracked into the angular domain, and reduced to 50
physics-informed run-level features (TSA, TSA residual, FM4/NA4/M6A/NB4,
sideband energy ratios, envelope-spectrum energy, broadband). Screened by
D1's exact protocol, they do **not** clear permutation chance in EXP-F
(observed 16, null median 11, **P(null ≥ obs) = 0.22**), and the result holds
across three aggregation choices.

**Reported at the three required levels:**

| level | result |
|---|---|
| **L1 FEATURE** | **NEGATIVE in EXP-F.** Positive in EXP-B (p = 0.000); EXP-A is uninformative by construction (see §4). |
| **L2 RANK** | **not run** — gated behind L1 |
| **L3 LEVEL** | **not run** — gated behind L1 |

This is the clean negative the task anticipated: the modality does not carry
recoverable damage information in the largest experiment **even under the
standard gear-diagnostic machinery**, applied to the raw waveform rather than
to the DAQ's summaries. The question is closed properly rather than left open.

One qualification, stated up front so the negative is not overread: the
physics features are **not worse** than the DAQ summaries in EXP-F — they are
better in relative terms (§5). They are simply still not distinguishable from
chance.

## 0. Kinematics — **PASS**, with three of the task's expectations corrected

Measured on a steady-state file, then confirmed identical in all three
experiments.

| quantity | measured | task expected |
|---|---|---|
| shaft frequency | **23.3334 Hz (1400.0 rpm)** | ~3.697 Hz (~222 rpm) |
| mesh frequency | **653.32 Hz** | — |
| **mesh / shaft ratio** | **27.999** | 28 |
| **tooth count** | **28, CONFIRMED** | 28 |
| samples per revolution available | **4,389** | ~28,000 |
| revolutions per file | **~1,400** | ~88 |

Mesh harmonics land at ratios **56.0, 84.0, 112.0**, so the integer relation is
not a coincidence of one peak. Identical in EXP-A (gear 233), EXP-B (gear 303)
and EXP-F (gear 309). **The gate passes: angular analysis is grounded.**

### Where the task's 3.697 Hz came from — and why it would have failed the gate

The expected figures are not arbitrary; they are what **file index 0 of a run**
returns. That file is a **speed ramp**. Measured directly:

| file | mean f_shaft | segment range | speed ratio | steady? |
|---|---|---|---|---|
| index 0 | **3.697 Hz** | 2.749 → 4.586 Hz | 1.67 | **no** |
| index 20 | 23.333 Hz | 23.331 → 23.335 Hz | 1.000 | yes |
| index 39 | 23.334 Hz | 23.332 → 23.334 Hz | 1.000 | yes |

3.697 Hz over 60 s is ~88 revolutions, which is exactly the task's other two
expectations, so all three trace to the same ramp file. **Had 3.697 Hz been
taken as the shaft frequency, the ratio would have been 653.32 / 3.697 =
176.7 — not an integer — and Step 0 would have halted the task.** The gate
worked; it just had to be applied to a steady-state file.

Consequently a **steady-state test is recorded for every file** (shaft rate in
10 segments; steady iff min > 20 Hz and max/min < 1.10) rather than assumed.

### The design consequence: 4,096 samples/rev, not 2^15

Only **4,389** samples/revolution exist at 1400 rpm. The task's target of
2^15 = 32,768 samples/rev was premised on the ~28,000 that a 3.697 Hz shaft
would give. **Resampling to 2^15 would be 7.5x upsampling — manufacturing
detail that is not in the data.** The grid is therefore **4,096 samples/rev
(2^12)**, just under what is available, resolving orders to 2,048 against
order-112 content of interest. The DAQ's own TSA uses M = 4096, which
corroborates the choice.

**Samples/rev achieved: 4,096.**

## 1. Extraction

Per run: 20 evenly spaced files **plus** the last 10 (nearest the photograph
the label comes from), deduplicated. Archives read **in memory**; nothing was
ever extracted in place, and nothing under `gtc-data-experiment/**` was
modified.

| | |
|---|---|
| files queued | 577 across 20 runs (EXP-A 5, EXP-B 7, EXP-F 8) |
| read successfully | 551 |
| too few revolutions (spin-up/down) | 25 |
| unreadable (missing HDF5 component) | 1 |
| **steady-state, used for features** | **472** (13–26 per run) |

79 readable files failed the steady-state test. They are exactly the run-start
ramps and **run-end spin-downs** — note this includes some of the "last 10"
files the task wanted for their proximity to the photograph. A spinning-down
file cannot contribute comparable angular features, so these are excluded and
counted rather than silently averaged in.

Recorded per file: experiment, run, file index, `wf_start_time`, gear ID,
revolutions, shaft frequency, speed stability, steady flag.

## 2. Features

Per file, per accelerometer: order-tracked to 4,096 samples/rev by unwrapping
the encoder's **absolute angle** (it is an absolute angle in degrees, not a
pulse train, so the angle comes from unwrapping rather than edge counting);
TSA over ~1,400 revolutions; residual by removing mesh orders 28/56/84 each
with ±1 shaft-order sidebands; then FM4, NA4, M6A, NB4, energy ratio, residual
kurtosis and crest, sideband energy ratio at mesh ±1,2,3 for three mesh
harmonics, envelope-spectrum energy at tooth-passing harmonics, and broadband
RMS/kurtosis/crest.

**Final count: 50 run-level features** — 23 per accelerometer × 2 = 46, plus 4
(NA4 and a run-normalised NB4 per channel) that require a run-level mean
variance in the denominator and cannot be formed from a single file. Run-level
aggregation is by **mean**, matching D1.

The DAQ's 72 summaries are kept as a **separate comparison arm and are never
merged into the same table**.

## 3. L1 screen — the head-to-head

D1's protocol reproduced exactly: run-level mean, target `raw_top3_mean_pct`,
|rho| ≥ 0.5, permutation null of 300 draws (seed 20260912), sign consistency.
**The DAQ row was recomputed here, not transcribed** — and it reproduces the
task's stated figures exactly, which validates the replication.

| feature set | EXP-A | EXP-B | EXP-F | sign-consistent |
|---|---|---|---|---|
| DAQ summaries (72) | 47/22 | 34/17 | **7/14** | 14/67 (chance 17) |
| physics-informed (50) | 45/16 | 38/12 | **16/11** | 16/50 (chance 12) |

*(observed / null median)*

With p-values:

| feature set | EXP-A | EXP-B | **EXP-F** |
|---|---|---|---|
| DAQ summaries | p = — (see §4) | p = 0.020 | **p = 0.867** |
| physics-informed | p = 0.113 | **p = 0.000** | **p = 0.223** |

**EXP-F, the row that matters: 16 observed against a null median of 11, null
95th percentile 23, P(null ≥ observed) = 0.223.** Above the null median in
point terms, but comfortably inside the null distribution. Not a pass.

### Robustness — the negative survives all three aggregations

Declared before running, all reported, none selected on outcome. (b) exists
because the label comes from a photograph taken at the **end** of a run while
the primary aggregation averages the whole run, which is a genuine
feature/label time mismatch.

| aggregation | EXP-A | EXP-B | **EXP-F** |
|---|---|---|---|
| (a) mean, all steady files *(primary)* | obs 42, p = 0.113 | obs 35, p = 0.000 | obs 16, **p = 0.190** |
| (b) mean, last-10 steady files *(label-matched)* | obs 39, p = 0.203 | obs 32, p = 0.000 | obs 10, **p = 0.487** |
| (c) median, all steady files | obs 44, p = 0.203 | obs 30, p = 0.007 | obs 15, **p = 0.260** |

The negative is not an artifact of the aggregation choice. **The
label-matched variant (b), which I argued beforehand was the most principled,
is the weakest of the three** — which removes the most plausible rescue for
the negative rather than supporting it.

## 4. Why EXP-A cannot be read as positive

EXP-A has **n = 5 runs**. At n = 5, |rho| ≥ 0.5 is nearly free: the
permutation null's 95th percentile is **43–47 of 46–50 features**. An observed
45 sits inside that. EXP-A's apparently spectacular 45/50 is what chance looks
like with five points, which is why the task nominated EXP-F as the row that
matters and why that judgement was correct. EXP-B (n = 7) is genuinely
significant for the physics features (p = 0.000) and was also significant for
the DAQ features (p = 0.020), so it does not separate the two arms.

## 5. What the physics features did buy — stated fairly

The negative should not be read as "the physics features are no better".
Relative to their own nulls, they are clearly better in EXP-F:

| | DAQ summaries | physics-informed |
|---|---|---|
| EXP-F observed vs null median | 7 vs 14 — **below chance** | 16 vs 11 — above the median |
| EXP-F p | 0.867 | 0.223 |
| sign-consistent vs chance | 14 vs 17 — **below chance** | 16 vs 12 — above chance |
| survivors (consistent sign AND strong in all three) | 3 | 2 |

The DAQ summaries in EXP-F were *below* their null on both counts. The physics
features are above it on both. That is a real improvement in the right
direction — it is just not large enough to clear the bar, and the task's bar
is the correct one at these sample sizes.

**The two physics survivors:**

| feature | EXP-A | EXP-B | EXP-F |
|---|---|---|---|
| `a1_res_rms` (TSA residual RMS, Accel 1) | −0.872 | −0.714 | −0.548 |
| `a2_env_h2` (envelope energy at 2× tooth-passing) | +0.564 | +0.571 | +0.548 |

`a1_res_rms` is precisely the physics-motivated quantity — residual energy
after the mesh is removed, where localised tooth damage is supposed to live —
and it is consistently strong across all three experiments. **But its sign is
negative: residual energy DECREASES as the damage label increases.** That is
backwards from the spall hypothesis, which predicts residual energy rising
with localised damage. A consistent, strong, physically-inverted relationship
is more readily explained by run-order confounding (both residual RMS and the
label drift with run index) than by damage mechanics. It should not be
reported as a damage indicator.

## 6. What this does and does not establish

**Does.** D1's null screened the DAQ's low-rate summaries only. That gap is now
closed: the raw 102.4 kHz waveform was read, order-tracked with a verified
encoder, and put through the standard gear-diagnostic indicator set. The
answer in EXP-F is the same. The negative can no longer be attributed to the
DAQ having thrown the signal away in its summarisation.

**Does not.** It does not prove the vibration contains nothing. It shows that
*these* indicators, at run level, over 13–26 sampled minutes per run, against
*this* label, do not clear chance in EXP-F. In particular this does not test:
per-tooth angular localisation (features here are averaged over the whole
revolution, so a single damaged tooth is diluted ~28-fold); within-run
trajectories rather than run-level aggregates; or the full ~370 files per run
rather than the sampled ~30.

**The per-tooth point is the most substantive.** The label is a per-tooth
damage measure and the TSA is a full revolution containing all 28 teeth. A
localised spall on one tooth perturbs 1/28th of the averaged revolution, and
every indicator computed here collapses the revolution to a scalar. Angular
segmentation of the TSA into 28 tooth sectors, scored per tooth against the
per-tooth label, is the natural next test and is a different experiment, not
a tweak to this one.

## 7. Assumptions not specified by the task

1. **Angular grid 4,096 samples/rev**, not the requested 2^15 — forced by the
   measured 4,389 available (§0). The single most consequential deviation.
2. **Steady-state filtering.** Not requested. Without it, ramp and spin-down
   files (79 of 551) would have entered the averages.
3. **"Mesh frequency and its first 3 harmonics"** read as orders 28, 56, 84
   (harmonic indices 1–3), each with ±1 shaft-order sidebands. It could have
   been read as 28/56/84/112.
4. **NA4 and NB4 denominators** use the run-level mean variance, since those
   indicators are defined against a running baseline and cannot be formed per
   file in isolation.
5. **Run-level aggregation by mean**, matching D1 rather than the median used
   elsewhere in the project; both are reported in the robustness table.
6. **Target `raw_top3_mean_pct`**, the column D1 screened against, so the
   head-to-head is like-for-like.
7. **Encoder treated as an absolute angle** in degrees and unwrapped;
   monotonicity enforced with a cumulative maximum, because encoder noise
   produces small backward steps that would break interpolation.
8. **One file was unreadable** (missing HDF5 component) and was dropped rather
   than investigated.
9. **Only Accel 1 and Accel 2** were used. The DAQ's own TSA is computed from
   Accel 2 only (`acc_channel: 'Accel 2'`).
10. **`Transforms/TSA`, `residual`, `difference` and `e_op` already exist in
    every HDF5 file** and were also never used by the pipeline. They were not
    screened here, since the task asked for indicators computed from the raw
    waveform, not the DAQ's versions. Screening them is cheap and unclaimed.

## 8. Artifacts

| file | contents |
|---|---|
| `scripts/rawvib/angular_features.py` | Step 0–2: order tracking, TSA, residual, indicators |
| `scripts/rawvib/l1_screen.py` | Step 3: D1-identical screen, both arms |
| `data/rawvib/file_features.parquet` | 577 rows, per-file features and kinematics (gitignored) |
| `data/rawvib/l1_screen.json` | screen output |

Raw archives were read in memory only. Nothing under `gtc-data-experiment/**`
was written, moved or modified.
