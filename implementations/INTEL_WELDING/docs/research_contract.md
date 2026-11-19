# Research contract — Intel Robotic Welding multimodal study

**Written before any model development. Committed before model-comparison
experiments. Binding on what counts as evidence.**

Dataset: `IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset` (HF, `gated: manual`),
local copy at `data/Full Dataset/`. Licence in `data/Full Dataset/LICENSE.txt`.
The PHM North America 2026 work elsewhere in this repository is untouched and
remains valid on its own terms; no number from that study may appear in a
table with a number from this one.

## Research questions

**MAIN RQ** — How can a process-aware multimodal AI architecture be designed
and evaluated for robust industrial anomaly detection?

- **SQ1** Which lightweight or pretrained Transformer-based representation
  components are suitable for visual, audio and sensor time-series data?
- **SQ2** How do unimodal baselines, simple concatenation fusion, modular late
  fusion and process-aware gated cross-modal fusion compare in predictive
  performance?
- **SQ3** Can gated cross-modal fusion improve robustness when modalities are
  missing, degraded or unreliable?
- **SQ4** How can performance be evaluated beyond accuracy — robustness,
  interpretability, modularity, calibration, compute, latency, usability?

## Tasks

- **PRIMARY**: binary anomaly detection, `Good` vs `Defect` (any non-Good).
- **SECONDARY**: 12-category intended weld-condition diagnosis.

## Label semantics — binding wording

`CATEGORY` is the **intended weld condition** recorded by the experimenters,
not expert-verified physical ground truth. No output of this study may use the
phrase "ground-truth defect" or "true defect" for this field. Permitted
phrasing: "the intended defect labels provided with the dataset".

## Grouping unit

The unit of generalisation is the **welding session**, operationalised as the
manifest `DIRECTORY` field. Justification recorded in the Phase 1 audit:
`CATEGORY` is constant within every `DIRECTORY`, so a sample-level split would
let a model recover the label from session identity. No sample from one
session may appear in both development and final-test partitions.

## Development / test separation

- ~20% of **sessions** form the FINAL TEST partition, frozen before any
  representation or fusion model is trained, hashed, and stored under
  `artifacts/intel_welding/splits/`.
- The remaining ~80% of sessions form DEVELOPMENT. All model selection,
  tuning, thresholds, calibration and corruption design happen here, using
  `StratifiedGroupKFold` (5 folds, group = session, stratify = binary label).
- The final test set is read **once**, and only after
  `docs/intel_welding/final_evaluation_preregistration.md` is committed and
  `allow_final_test: true` is explicitly set. Default is false and the
  evaluation code refuses to run otherwise.
- The dataset's supplied `SPLIT` column is retained only as a secondary
  literature-comparability protocol **if** it is session-disjoint. The Phase 1
  audit determines this.

## Primary metrics

- Binary: **AUROC** primary; AUPRC, macro-F1, balanced accuracy, precision,
  recall, specificity, Brier, ECE secondary. Thresholds chosen on development
  predictions only.
- Multiclass: **macro-F1** primary; balanced accuracy, per-class P/R/F1,
  confusion matrix, one-vs-rest AUROC where support permits.
- SQ4: parameters, trainable parameters, peak GPU memory, latency/sample,
  throughput, model size, calibration, corruption and missing-modality curves.

Uncertainty is always by **session-clustered bootstrap**; paired model
comparisons use a paired session-cluster bootstrap. Effect size, interval and
direction are reported, never a bare p < 0.05.

## Modalities

Deployable (in-process): **audio** (`.flac`), **video** (`.avi`), **sensor
time series** (`.csv`). Process context from the manifest is an auxiliary
input, never a substitute for a physical modality.

Post-weld images are **privileged/offline only**. They may not enter the
primary deployable fusion comparison. Their availability is a Phase 1 finding.

## Fusion architectures (SQ2)

- **A** unimodal per modality
- **B** embedding concatenation + LayerNorm + MLP
- **C1** uniform late fusion, **C2** learned convex late fusion
- **D** process-aware gated fusion, with ablations D0–D6

## Robustness (SQ3)

Corruption operators and severities are declared **before** any robustness
result is seen: audio noise at 20/10/0 dB, band-limited noise, clipping,
temporal dropout; video blur, brightness shift, frame dropout, temporal
subsampling, occlusion; sensor Gaussian noise scaled by training-fold channel
std, point dropout, channel dropout, stuck-at-constant, block dropout; and all
seven missing-modality combinations. Levels are never chosen after seeing
performance.

## Stopping gates

Each gate halts its dependents on failure; the failed precondition is recorded
rather than worked around.

| gate | requirement |
|---|---|
| 0 data access | raw data readable; no restriction bypassed |
| 1 integrity | enough samples carry audio + video + sensor |
| 2 label support | both binary classes across enough independent sessions |
| 3 leakage | partitions session-disjoint; no duplicate content across them |
| 4 alignment | cross-modal lag small and stable → temporal cross-attention allowed; otherwise sample-level fusion only |
| 5A/5B/5C signal | per-modality OOF performance excludes chance under session-clustered bootstrap; permutation control collapses |
| 6 fusion allowed | **at least two** deployable modalities pass their signal gate |
| 7 gate validity | gate weights demonstrably respond to process and quality inputs |
| 8 SQ3 answerable | clean model uses its modalities, and gating beats simple fusion under degradation |
| 9 final unlock | architecture frozen, preregistration committed, clean git state |

## Interpretation rules, fixed in advance

- A flat degradation curve from an effectively constant model is **not**
  robustness.
- A gate is not interpretable because its weights can be plotted; an
  interpretation must survive controlled ablation (D4/D5/D6).
- A feature or gate behaviour whose sign is opposite to the physically
  expected direction is evidence of confounding, not of detection.
- If context-only performance is high, the finding is reported as dataset
  confounding. The study must then distinguish **recognising the recipe
  intended to produce a defect** from **detecting a physical defect
  signature**, and every multimodal model is compared against modality-only,
  context-only, and modality+context arms.
- Outcomes A–F (including "only one modality carries signal" and "context
  explains the labels") are all acceptable results. None is preferred.

## What counts as evidence

| SQ | evidence FOR | evidence AGAINST |
|---|---|---|
| SQ1 | a representation's OOF performance excludes chance, is stable over ≥3 seeds, and its cost/latency is justified relative to a simpler baseline | pretrained backbone is indistinguishable from the handcrafted baseline, or unstable across seeds |
| SQ2 | a fusion arm beats the strongest unimodal arm with a paired session-clustered interval excluding zero | interval includes zero, or the gain is matched by simple late fusion or explained by context alone |
| SQ3 | gated fusion retains performance better than simple fusion under predeclared corruption, with gate weight moving away from the degraded modality | gate does not reroute, or gating is no better than late fusion under degradation |
| SQ4 | a defensible trade-off table across accuracy, robustness, calibration, compute and modularity | metrics reported without operational interpretation |

## Reproducibility

Every reported model emits config, seed, git commit, dataset-manifest hash,
split hash, environment, checkpoint or reproducible command, and
machine-readable metrics.

## Prohibitions

No test-set access during development. No split-seed search on performance.
No transformation fitted outside the training fold. No class merging to
improve a metric. No architecture chosen for narrative interest. No silent
change of research question after seeing results.
