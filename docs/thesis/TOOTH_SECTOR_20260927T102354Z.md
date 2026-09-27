# TOOTH-SECTOR — removing the 28× dilution

**L1 is NEGATIVE in EXP-F under per-tooth-sector aggregation. Stop condition
triggered; no fourth feature family was tried.**

## Outcome

The 28× dilution was real and is now removed: the TSA was cut into 28 tooth
sectors and aggregated as an upper order statistic (top-1, top-3 mean,
concentration, spread), matching the label's own construction — the mean of
the 3 worst of 24 teeth. **It changes nothing.** EXP-F goes from
16/11 (p = 0.223) revolution-averaged to 26/17 (**p = 0.223**) per-sector:
more features clear the threshold, and the null rises by exactly as much.

Every survivor that is sign-consistent and strong in all three experiments is
**backwards**, and the run-order confound behind that is demonstrated directly
in §5. **Correctly-signed survivors: zero.**

The dilution was therefore **not the binding constraint**. That is the result.

## 1. Segmentation and boundary handling

The task's "4096/28 = 146" does not tile: 28 × 146 = 4088, eight samples short
of the revolution. Boundaries are placed at **round(k · 4096 / 28)** for
k = 0…28, giving **20 sectors of 146 samples and 8 of 147**, summing to exactly
4096 with **no gap and no overlap** (verified programmatically). Sector widths
are equal to within one sample, 0.7 % of a sector.

**Rotation invariance.** The 28 sector values are sorted descending before any
statistic is taken, so no keyphasor and no absolute tooth registration is
assumed. This is not merely a convenience — §2 shows the TSA phase origin
genuinely differs from file to file, so absolute registration is *impossible*
here and sorting is the only sound choice. Sector *k* is not physical tooth *k*.

Per sector: residual RMS, kurtosis, peak-to-peak, crest factor, and sector
energy as a fraction of the revolution total. Per indicator, the sorted
28-vector yields **top-1**, **top-3 mean**, **concentration** (top-3 ÷
all-sector mean) and **spread** (SD of the sorted vector), with the
**revolution mean** kept alongside as the direct comparison arm — same signal,
same files, same TSA, only the aggregation differs.

### On reuse

RAW-VIB persisted only scalar indicators, so the averaged revolutions
themselves were gone and had to be recomputed. The file list was taken from
RAW-VIB's own output table (the same 472 steady files, not re-selected) and
the TSA was produced by importing RAW-VIB's own `angular_resample` and
`residual_of`. It is the same TSA, not a second differently-parameterised
extraction. Archives were read in memory; nothing was extracted in place.

## 2. Port cross-check against the DAQ's own Transforms — **strong agreement**

`Transforms/{TSA, residual, difference, e_op}` exist in all 472 files and had
never been used. Comparing our Accel-2 TSA with the DAQ's:

| | |
|---|---|
| best circular correlation | **median 0.997**, mean 0.997, min 0.985, max 0.999 |
| files above r = 0.9 | **472 / 472** |
| amplitude (RMS) | ours 2.9304 vs DAQ 2.9459 — **0.5 % apart** |
| correlation at **zero** shift | +0.015 |
| control: our **Accel 1** vs DAQ TSA | median 0.819 |

Two things follow. First, **the port is independently validated**: an
implementation written from the raw waveform reproduces the vendor's own
transform to r = 0.997 in amplitude and shape. Second, the Accel-1 control is
markedly worse than the Accel-2 match, exactly as the DAQ's
`acc_channel: 'Accel 2'` attribute states — a second, independent confirmation
that the channel mapping is right.

The near-zero correlation at zero shift, against 0.997 at the best shift,
shows the two TSAs differ only by a **rotational phase offset**: the DAQ
triggers on a falling edge at reference level 180°, while our resampling has
no keyphasor. This is what makes absolute tooth registration impossible and
sorting mandatory (§1).

## 3. The screen — all rows

Protocol identical to D1 and RAW-VIB throughout: run-level mean, target
`raw_top3_mean_pct`, |rho| ≥ 0.5, permutation null of 300 draws (seed
20260912). The DAQ summary row is **recomputed every time as the protocol
check** and again reproduces its established figures exactly.

| feature set | EXP-A | EXP-B | **EXP-F** | sign-consistent |
|---|---|---|---|---|
| DAQ summaries (72) | 47/22 p 0.11 | 34/17 p 0.02 | **7/14 p 0.87** | 14/67 (chance 17) |
| physics, revolution-averaged (50) | 45/16 p 0.11 | 38/12 p 0.00 | **16/11 p 0.22** | 16/50 (chance 12) |
| **physics, per-sector top-3 (80)** | 70/20 p 0.20 | 52/21 p 0.00 | **26/17 p 0.22** | 24/80 (chance 20) |
| DAQ Transforms, revolution-avg (20) | 16/6 p 0.20 | 8/4 p 0.15 | **9/3 p 0.18** | 2/17 (chance 4) |
| DAQ Transforms, per-sector (80) | 65/23 p 0.20 | 51/19 p 0.00 | **35/15 p 0.09** | 25/80 (chance 20) |

*(observed / null median, and P(null ≥ observed))*

**The comparison that matters — EXP-F, row 3 against row 2:**

| aggregation | observed | null median | null p95 | p |
|---|---|---|---|---|
| revolution-averaged | 16 / 50 | 11 | 23 | **0.223** |
| per-sector top-3 | 26 / 80 | 17 | 34 | **0.223** |

Per-sector aggregation raises the observed count from 16 to 26 — but raises
the null from 11 to 17 by the same factor. **The p-value is unchanged to three
decimals.** Order-statistic aggregation buys more threshold-clearing features
and exactly as much extra opportunity for chance to supply them. This is the
cleanest possible demonstration that the dilution was not what was limiting
the result.

EXP-A remains unreadable as a positive: at n = 5 its null 95th percentile is
20–78 depending on the family, so 45/50 and 70/80 are what chance looks like
with five points. EXP-B is significant in every physics row, but it was
already significant for the DAQ summaries (p = 0.02), so it does not separate
the arms.

## 4. Sign discipline — applied before any claim

Every indicator here is an energy, spread or impulsiveness measure of the TSA
residual. Localised tooth damage should **raise** all of them, so **the
physically expected sign is POSITIVE for every feature without exception**.

| row | survivors | correct sign | **backwards** |
|---|---|---|---|
| physics, revolution-averaged | 2 | 1 (`a2_env_h2`) | 1 (`a1_res_rms`) |
| **physics, per-sector** | **3** | **0** | **3** |
| DAQ Transforms, per-sector | 8 | 0 | 8 |

The three per-sector survivors:

| feature | EXP-A | EXP-B | EXP-F | expected | observed |
|---|---|---|---|---|---|
| `a2res_rms_spread` | −0.67 | −0.46 | −0.62 | + | **−** |
| `a2res_p2p_spread` | −0.67 | −0.61 | −0.52 | + | **−** |
| `a2res_efrac_spread` | −0.67 | −0.64 | −0.57 | + | **−** |

All three say the same physically inverted thing: *the more damaged the gear,
the more EVENLY residual energy is spread across the 28 sectors.* Localised
spall predicts the opposite. **None counts toward L1.**

The DAQ's own Transforms give eight survivors — the strongest correlations
anywhere in this study, up to |rho| = 0.905 — and **all eight are negative
too**, the `daqeop_*` concentration and spread family. Strength is not the
problem; direction is.

## 5. The confound, demonstrated rather than asserted

A wrong-signed survivor is supposed to indicate run-order confounding. That is
testable directly, and it holds:

| quantity, vs run index | EXP-A | EXP-B | EXP-F |
|---|---|---|---|
| **the label** (`raw_top3_mean_pct`) | **+0.900** | **+0.679** | **+0.643** |
| `a2res_rms_spread` | −0.667 | −0.464 | −0.619 |
| `a2res_p2p_spread` | −0.667 | −0.607 | −0.524 |
| `a2res_efrac_spread` | −0.667 | −0.643 | −0.571 |
| `daqeop_rms_spread` | −0.667 | −0.643 | −0.643 |
| `daqeop_efrac_conc` | −0.667 | −0.429 | −0.738 |

The label climbs with run index in all three experiments; every backwards
survivor falls with run index in all three. Their strong negative correlation
**with the label** is fully accounted for by both quantities drifting
monotonically with run order, in opposite directions. No mechanical
explanation is needed and none should be offered.

## 6. Accelerometer agreement — an independent strike

A real mechanical effect must appear on both accelerometers. Across the 40
paired per-sector features:

| experiment | sign agreement | rho(rho_a1, rho_a2) |
|---|---|---|
| EXP-A | 82 % of 40 pairs | +0.075 |
| EXP-B | 50 % of 40 pairs | +0.467 |
| **EXP-F** | **30 % of 40 pairs** | **−0.478** |

**In EXP-F the two accelerometers actively disagree** — 30 % sign agreement is
*below* the 50 % expected from coin flips, and the correlation between their
per-feature rho values is negative. Two sensors on the same gearbox, measuring
the same 28 teeth over the same revolutions, do not merely fail to confirm
each other; they point opposite ways. This is independent of the permutation
test and points the same way.

## 7. The known caveat, flagged not corrected

The gear has 28 teeth; the v3 label uses 24, with teeth 1–4 dropped. The worst
vibration sector may therefore belong to a tooth the label excludes. As
instructed this is flagged, not corrected for. The mitigating evidence stands
(teeth 1–4 ranked bottom-half in all 8 EXP-F runs, so they are unlikely to be
the worst sectors), and it is weakened further by the sorting: since sector
identity is discarded, there is no way to tell which physical tooth any
top-ranked sector belongs to. The caveat cannot be resolved within this
rotation-invariant design — it would need a keyphasor, which the data does not
provide.

## 8. Verdict

**L1 NEGATIVE in EXP-F.** Per-sector top-3 is at chance (p = 0.223, identical
to revolution-averaged), and zero survivors carry the physically correct sign.
The stop condition applies: no fourth feature family was attempted, and L2/L3
were not run.

**The closing argument.** Five representations of the same modality have now
been screened under one protocol against one label:

1. vendor low-rate summaries (`/Context/`, `/CI/`) — below chance in EXP-F
2. vendor transforms, revolution-averaged — p = 0.18
3. vendor transforms, per-tooth-sector — p = 0.09, all survivors backwards
4. physics from raw waveform, revolution-averaged — p = 0.22
5. **physics from raw waveform, per-tooth-sector order statistics — p = 0.22**

None clears chance in EXP-F. The two most promising by raw correlation
strength are driven by run order and point the wrong way. The one arm that
looked strongest overall (DAQ Transforms per-sector, |rho| up to 0.905) is
the one whose survivors are *most* uniformly inverted.

The three candidate explanations for the original negative have now each been
tested and eliminated: **the DAQ did not throw the signal away** in
summarisation (RAW-VIB read the raw waveform and got the same answer), **the
port is not broken** (our TSA matches the vendor's at r = 0.997), and **the
28× dilution was not the binding constraint** (removing it leaves the p-value
unchanged). This should be reported as the closing result for the vibration
modality.

## 9. What this still does not test

Stated so the negative is not overread. The features remain **run-level
aggregates over 13–26 sampled minutes**, not within-run trajectories; the
sampling is ~30 of ~370 files per run; and sorting makes the analysis
rotation-invariant at the cost of any per-tooth *correspondence* between
vibration sector and labelled tooth. A keyphasor-registered, tooth-matched
analysis is not possible with this data, and its absence is a property of the
recording, not of this study.

## 10. Assumptions not specified

1. **Sector boundaries** at `round(k·4096/28)`, widths 146/147 (§1); the
   task's uniform 146 would have left 8 samples unassigned.
2. **TSA recomputed**, since RAW-VIB stored only scalars — same file list,
   same imported functions (§1).
3. **DAQ `Transforms` averaged over the file's 60 one-second rows** to match
   our per-file TSA granularity.
4. **Expected sign taken as positive for every indicator** (§4). Defensible
   for energy/spread/impulsiveness measures, and stated so it can be
   challenged.
5. **Per-sector kurtosis over 146 samples** is a noisier estimator than the
   revolution-level version; no correction applied.
6. **"Top-3 mean" mirrors the label's construction** but over 28 sectors where
   the label uses 24 teeth (§7).
7. The task's context line gives **"560 revolutions per file"**; the measured
   value is **~1,400** (RAW-VIB Step 0, unchanged here). Nothing depends on it.

## 11. Artifacts

| file | contents |
|---|---|
| `scripts/rawvib/save_tsa.py` | persists the TSA arrays RAW-VIB discarded, same file list |
| `scripts/rawvib/sector_features.py` | 28-sector segmentation and order statistics |
| `scripts/rawvib/sector_screen.py` | three-row screen, sign audit, accel agreement |
| `data/rawvib/tsa_arrays.npz` | 472 × 4096 averaged revolutions, 8 signals (gitignored) |
| `data/rawvib/sector_screen.json` | full screen output |

Nothing under `gtc-data-experiment/**` was written, moved or modified.
