# EXP-A Initial Lifecycle EDA — Run-1 / Run-3 / Run-5

## 1. Purpose

This folder preserves the initial exploratory data analysis performed on the
PHM North America 2026 Data Challenge training data for:

- EXP-A Run-1
- EXP-A Run-3
- EXP-A Run-5

The analysis was designed as a lifecycle-stratified investigation:

- Run-1 = early lifecycle
- Run-3 = intermediate lifecycle
- Run-5 = late lifecycle

These are relative experimental stages only. They are **not**
healthy / damaged / failed labels.

### Central scientific question

> Can a physically meaningful degradation trajectory be observed across
> EXP-A Run-1 → Run-3 → Run-5, and can changes in continuous sensor behaviour
> ultimately be aligned with physical gear-tooth damage visible in images?

Working framing:

> **Physics-Aware Multi-Scale / Cross-Modal Degradation Signature Analysis**

---

## 2. Why Run-1 / Run-3 / Run-5?

The high-frequency vibration archives are very large, so the first study used
representative lifecycle stages rather than immediately processing every run.

```text
EXP-A lifecycle

Run-1  ----------------  Run-3  ----------------  Run-5
Early                  Intermediate                Late
```

Reasons:

1. The runs come from the same experiment, reducing cross-experiment variability.
2. They provide early / intermediate / late lifecycle coverage.
3. They keep the initial high-frequency analysis computationally manageable.
4. Run-2 was intentionally excluded from the first HF study because the challenge
   organizers reported substantial Run-1 / Run-2 duplication:
   311 duplicated files, approximately 71.8% overlap.
5. Run-4 was not considered irrelevant. It was initially omitted only for
   computational efficiency and should be included in later full-lifecycle work.

---

## 3. Data modalities used

### 3.1 High-frequency vibration

Selected high-frequency runs:

- Run-1
- Run-3
- Run-5

Confirmed HDF5 mapping:

```text
Axial vibration       /Vibration/Accel 1
Radial vibration      /Vibration/Accel 2

RPM                   /Context/PAU Speed
Torque                /Context/PAU Torque
Temperature           /Context/Temperature
```

Typical vibration sampling rate:

```text
102,400 Hz
```

Typical one-minute vibration array length:

```text
~6,144,000 samples
```

---

### 3.2 Classical condition indicators

The analysis used:

- FM4
- NA4
- M6A
- ALR

These are treated here as classical vibration-based gear condition indicators.

Two CI path conventions were observed:

```text
/CI/FM4
/CI/NA4
/CI/M6A
/CI/ALR
```

and:

```text
/CI_4s/FM4
/CI_4s/NA4
/CI_4s/M6A
/CI_4s/ALR
```

The analysis code therefore needs to support both.

---

### 3.3 Low-frequency archives

Two nested archive groups were inspected:

```text
low-frequency (CIs + Oil + Environment)/
    Exp-A_HDF5_LF.zip

low-frequency (CIs)/
    Exp-A_HDF5_CI.zip
```

Each outer ZIP contains separate run-level ZIP archives.

This was an important structural discovery because the outer archive itself does
not directly expose HDF5 members.

---

### 3.4 Gear-tooth images

EXP-A image stages include:

```text
0 Hours / Test Start
Break-In
Run-1
Run-2
Run-3
Run-4
Run-5
```

The gear contains 28 teeth.

The image modality was used as physical evidence of tooth-surface evolution and
as the future basis for sensor ↔ damage alignment.

---

## 4. Data-ingestion lessons

The dataset required substantial data-engineering work before EDA became reliable.

### Large Synology downloads

The high-frequency archives were downloaded from a Synology File Station share.

The browser download relied on a temporary `sharing_sid` session cookie.

An early downloader appeared to succeed but actually saved very small JSON/HTML
responses instead of the real ZIP archives.

The corrected workflow therefore validated:

- HTTP response type
- expected file size
- binary/ZIP response
- ZIP signature
- final archive size

### Resumable downloads

Incomplete transfers were stored as:

```text
*.zip.part
```

Only after a successful and validated download was the file renamed to:

```text
*.zip
```

### General lesson

> **HTTP 200 does not mean that the expected dataset was downloaded.**

Large industrial datasets should be validated before analysis begins.

---

## 5. EDA methodology

The analysis followed a staged hierarchy.

### P0 — Data integrity

Checked:

- ZIP validity
- HDF5 structure
- missing channels
- NaN / Inf
- sampling rate
- signal length
- run coverage
- duplicate awareness
- photo inventory
- nested archive structure

---

### P1 — Basic EDA

#### Raw vibration

Analysed separately:

- axial / Accel 1
- radial / Accel 2

Views:

- time-domain waveform
- frequency spectrum

#### Operating context

Compared:

- RPM
- torque
- temperature

Purpose:

A vibration difference can be caused by operating conditions rather than degradation.

#### Classical condition indicators

Compared:

- FM4
- NA4
- M6A
- ALR

#### Images

Inspected tooth-surface development across lifecycle stages.

---

### P2 — Feature engineering

#### Time-domain features

- mean
- standard deviation
- RMS
- minimum
- maximum
- peak-to-peak
- skewness
- kurtosis
- crest factor

#### Generic spectral features

- dominant frequency
- spectral centroid
- total spectral energy

#### Physics-aware gear features

For the 28-tooth gear:

```text
shaft frequency = RPM / 60

gear mesh frequency (GMF) = 28 × shaft frequency
```

Energy was evaluated around:

- 1× GMF
- 2× GMF
- 3× GMF

This moved the analysis from generic signal changes toward mechanically
interpretable features.

---

### P3 — Lifecycle distribution analysis

Features were compared across:

```text
R1 vs R3
R3 vs R5
R1 vs R5
```

Analysis included:

- medians
- distribution shifts
- Wasserstein distance
- standardized effect estimates
- boxplots

A later lesson was that conventional standardized effects can be strongly
affected by startup/shutdown observations.

---

### P4 — Within-run trajectories

Features were plotted against normalized run progress:

```text
0.0  ---------------------------------------------  1.0
start                                                end
```

This helped distinguish:

- persistent lifecycle separation
- startup/shutdown behaviour
- isolated outliers
- within-run evolution

Important trajectory features included:

- ALR
- axial 1× GMF energy
- radial 3× GMF energy
- axial skewness
- radial spectral centroid

---

### P5 — PCA / multivariate analysis

Multiple extracted features were combined using PCA.

The exact same PCA space was colored by:

- lifecycle stage
- RPM
- torque
- temperature

Purpose:

> Determine whether feature-space structure is primarily lifecycle-related or
> operating-condition-related.

---

### P6 — Initial cross-modal image analysis

Contact sheets were created for:

- 0 h
- Break-In
- R1
- R2
- R3
- R4
- R5

The first image analysis was qualitative.

It was used to assess whether sensor-side lifecycle hypotheses were plausible
before building a formal image-damage score.

---

## 6. Key findings

These are preliminary EDA findings, not final causal conclusions.

### Finding 1 — Dominant operating conditions are highly comparable

Approximate medians:

| Run | Median RPM | Median Torque | Median Temperature |
|---|---:|---:|---:|
| R1 | ~1399.996 | ~120.002 | ~129.56 |
| R3 | ~1400.004 | ~119.954 | ~131.36 |
| R5 | ~1400.003 | ~120.002 | ~128.12 |

Interpretation:

- RPM and torque are highly comparable in the main operating regime.
- Startup/shutdown observations are still present.
- Lifecycle comparison is feasible, but transient periods must be treated carefully.

---

### Finding 2 — Axial and radial vibration are complementary

Axial and radial accelerometers show visibly different:

- time-domain behaviour
- spectral structure

Interpretation:

Both sensor orientations should be retained because they capture different
components of the gearbox mechanical response.

---

### Finding 3 — Classical CIs show a strong R1 → R3 transition

Median values:

| CI | R1 | R3 | R5 |
|---|---:|---:|---:|
| FM4 | 4.004 | 3.002 | 3.141 |
| NA4 | 3.274 | 2.661 | 2.744 |
| M6A | 29.590 | 14.941 | 17.155 |
| ALR | 1.511 | 0.337 | 0.306 |

Common pattern:

```text
R1  -------- major change -------->  R3  ~  R5
```

Interpretation:

Several classical CIs behave more like transition-sensitive indicators than
strictly monotonic lifecycle indicators in this experiment.

The CI values should not be interpreted as direct damage percentages.

---

### Finding 4 — Axial 1× GMF energy is a strong progressive candidate

The lifecycle distributions and within-run trajectories showed approximately:

```text
R1 < R3 < R5
```

The ordering remained visible across much of steady operation.

Interpretation:

Axial 1× GMF energy is currently one of the strongest physics-aware
candidate degradation signatures.

It remains a candidate until operating-condition control and image-based
physical validation are completed.

---

### Finding 5 — Several features identify an early-to-intermediate transition

Important examples:

- axial skewness
- radial spectral centroid
- radial 3× GMF energy
- ALR

Approximate behaviour:

```text
R1  → large transition →  R3 ≈ R5
```

Interpretation:

Different features may respond to different lifecycle phases.

The gearbox may therefore not be represented by one universal monotonic health index.

---

### Finding 6 — Radial spectral content is redistributed

The radial spectral centroid was substantially higher in R1 and much lower in
R3/R5.

Interpretation:

A strong lifecycle-associated spectral redistribution occurs between the early
and later selected stages.

This should be described as spectral redistribution until physical damage
alignment is completed.

---

### Finding 7 — PCA exposed operating-state confounding

The lifecycle-colored PCA contained:

- a dense main population
- a long secondary tail

When the exact same PCA coordinates were colored by RPM and torque, the long
tail followed low-speed and low-load operation.

Interpretation:

The large PCA tail is strongly associated with startup/shutdown operating state.

Without context variables, this could easily be misinterpreted as extreme
degradation or anomaly behaviour.

---

### Finding 8 — Temperature remains an important contextual variable

RPM and torque largely explain the major transient PCA structure.

Temperature still varies substantially inside the dense steady-state region.

Current interpretation:

```text
RPM + torque
    → useful for operating-regime / steady-state filtering

temperature
    → retain as contextual covariate / normalization variable
```

---

### Finding 9 — Physical image damage becomes localized

Image inspection across:

```text
0 h → Break-In → R1 → R2 → R3 → R4 → R5
```

showed that late-stage images contain strongly localized regions of severe
surface loss / spall-like damage on particular teeth.

Interpretation:

Damage is not uniformly distributed across all 28 teeth.

Future image analysis should therefore preserve tooth-level localization rather
than rely only on a global mean score.

---

## 7. Current working hypothesis

The initial EXP-A analysis suggests that the gearbox does **not** follow one
simple monotonic sensor trajectory.

Two broad response types currently appear.

### Transition-sensitive behaviour

Examples:

```text
ALR
axial skewness
radial spectral centroid
radial 3× GMF energy
```

Approximate behaviour:

```text
R1  → large transition →  R3 ≈ R5
```

### More progressive behaviour

Example:

```text
axial 1× GMF energy
```

Approximate behaviour:

```text
R1 < R3 < R5
```

### Physical-image behaviour

Late-stage images show substantially stronger and highly localized tooth-surface
damage.

### Overall hypothesis

> Different sensor features may respond to different phases of the degradation
> process rather than forming one universally monotonic health indicator.

This still requires controlled full-lifecycle and tooth-level validation.

---

## 8. Important limitations

The current experiment does **not** prove:

- that R1 is healthy
- that R5 is failed
- that every observed feature shift is caused by degradation
- that higher/lower ALR directly maps to a fixed damage severity
- that sensor features are already quantitatively aligned with image damage
- that EXP-A behaviour generalizes to other experiments

Important limitations / confounders:

- startup/shutdown transients
- RPM and torque effects
- temperature effects
- Run-2 duplicate contamination
- nonuniform tooth-level damage
- initial HF lifecycle subsampling
- qualitative rather than quantitative image damage scoring

---

## 9. Main outputs preserved in this experiment folder

### Basic EDA

Stored under:

```text
outputs/basic_eda/
```

Expected content includes:

- dataset inventory
- HDF5 structure information
- raw axial/radial time-domain plots
- axial/radial frequency-domain plots
- RPM / torque / temperature plots
- FM4 / NA4 / M6A / ALR plots
- initial image examples

### Advanced EDA

Stored under:

```text
outputs/advanced_eda/
```

Expected content includes:

- lifecycle feature boxplots
- within-run feature trajectories
- PCA plots
- PCA colored by RPM / torque / temperature
- HF feature tables
- LF / CI canonical tables
- lifecycle distribution-shift statistics
- context-normalization outputs
- image contact sheets
- image inventory
- HDF5 / LF structure reports

---

## 10. Next analytical steps

### 1. Steady-state filtering

Candidate operating window:

```text
1390 ≤ RPM ≤ 1410
115 ≤ Torque ≤ 125
```

Goal:

Remove startup/shutdown contamination and compare lifecycle stages under nearly
identical speed/load conditions.

---

### 2. Robust feature re-ranking

Recalculate lifecycle shifts after steady-state filtering.

Goal:

Determine which candidate features remain strong after operating-context control.

---

### 3. Full EXP-A R1 → R5 high-frequency lifecycle

Now that all EXP-A HF archives are available, extend the analysis to:

```text
R1 → R2 → R3 → R4 → R5
```

Run-2 duplicate handling must be explicit.

Goal:

Determine more precisely where the major state transition occurs.

---

### 4. Deeper GMF / harmonic analysis

Investigate:

- 1× GMF
- 2× GMF
- 3× GMF
- possible order-domain representations
- possible sideband behaviour

Goal:

Strengthen the mechanical interpretation of lifecycle-sensitive spectral changes.

---

### 5. Tooth-level image damage quantification

Move from contact-sheet inspection to numerical tooth-level damage measurement.

Possible later approaches:

- manual annotation
- segmentation
- object detection when spatial localization is appropriate

Goal:

Create a quantitative physical-damage trajectory.

---

### 6. Sensor ↔ image alignment

Align:

```text
sensor features / CIs
        +
tooth-level image damage
```

Goal:

Test whether the strongest sensor-side signatures correspond to actual physical
tooth deterioration.

---

### 7. Replication on EXP-F

After stabilizing the EXP-A methodology, apply it to EXP-F.

Goal:

Determine whether the discovered signatures are EXP-A-specific or reproducible
across another accelerated-life experiment.

---

## 11. Future modelling direction

Potential temporal branch:

```text
CIs / engineered vibration features
        ↓
PatchTST / temporal model
```

Potential image branch:

```text
gear-tooth images
        ↓
RT-DETR / segmentation / visual damage model
```

Potential future multimodal architecture:

```text
Temporal degradation representation
                +
Visual physical-damage representation
                ↓
Cross-modal alignment / multimodal fusion
```

The EDA should determine which information is physically meaningful before the
final model architecture is selected.

---

## 12. Status

### Completed

- [x] EXP-A R1/R3/R5 data inspection
- [x] HDF5 channel mapping
- [x] Basic raw vibration EDA
- [x] Operating-condition analysis
- [x] Classical CI analysis
- [x] HF feature extraction
- [x] Lifecycle distribution analysis
- [x] Physics-aware GMF analysis
- [x] Within-run trajectory analysis
- [x] PCA / operating-context analysis
- [x] Initial gear-tooth image inspection

### Current hypothesis

> EXP-A contains multiple lifecycle-sensitive response patterns rather than one
> universally monotonic sensor health indicator.

### Next validation priority

```text
Steady-state control
        ↓
Full R1–R5 lifecycle
        ↓
Robust feature ranking
        ↓
Quantitative tooth damage
        ↓
Sensor ↔ image alignment
        ↓
Replication on EXP-F
```

---

## 13. Repository note

This directory is an experiment-specific research record.

It intentionally contains:

- one detailed experiment Markdown file
- experiment-specific script snapshots
- experiment-specific configuration snapshots
- experiment-specific outputs

The repository-level `README.md` is intentionally left unchanged and remains the
overall project README.
