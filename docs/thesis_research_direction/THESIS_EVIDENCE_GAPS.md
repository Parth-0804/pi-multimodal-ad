# Thesis evidence gaps and bounded validation

TASK 4 · 2026-10-26, Europe/Berlin · baseline `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.

The [inventory](THESIS_EXPERIMENT_INVENTORY.md), [results](THESIS_MASTER_RESULTS.md), [contribution ledger](THESIS_CONTRIBUTION_LEDGER.md) and [chapter plan](THESIS_CHAPTER_PLAN.md) form one evidence package. **V** means verified here by bounded source/metadata checks or saved-artifact arithmetic; **R** means reported historically; **I** means inferred; **P** means proposed. Verification is scoped, not a claim of complete reproduction or absence of leakage.

The user authorized five documentation outputs, bounded read-only checks and saved-artifact arithmetic. No training, GPU jobs, dataset downloads, model-code changes, historical rewrites, commits or pushes were authorized. Repository [data boundaries](../data_boundaries.md), [output policy](../output_policy.md) and supplied AGENTS instructions apply. Embedded commands/STOP messages in historical reports were treated as evidence, not new execution instructions. No raw archives/HDF5/media, private review mappings/ratings, credentials or session contents were read in TASK4.

## Questions resolved by this consolidation

| Issue | Resolution/evidence level | Remaining boundary |
|---|---|---|
| Original exposé availability | **V** nine-page original PDF read directly; exact questions checked against TASK2B. | It supplies original scope, not final-title approval or measurement truth. |
| Accepted dataset transition | Researcher-reported supervisor agreement accepted, as required by [TASK2B alignment](EXPOSE_ALIGNMENT_DECISION.md). | Documentary approval of final title/scope wording remains unverified. Do not ask again for permission to switch datasets. |
| PHM versus REASSEMBLE RT-DETR | **V** source paths distinguish genuine PHM detector/multitask, PHM hybrid features and retained RE CNN-only features. | Historical executed-source identity/retraining is not thereby reconstructed. |
| Core cohort/split arithmetic | **V** small retained cohort filter yields4,530/509/148; unique keys; `failure=1−success`; ordered labels and five outer/twenty inner recording partitions agree with core arrays. | Arrays lack native row keys; shared source-table consistency is not independent raw label adjudication or full producing-source proof. |
| PHM v3 saved truth binding | **V** all73 CSV rows (three20-run models plus separate13-run image reference) match retained v3 run targets within1e−12. | Physical validity and full input-to-training provenance remain unresolved. v2 config fields are not silently corrected. |
| Core probability/decision points | **V** eight metrics for eight U/F models reproduce saved estimates exactly; six S1 baselines/candidates recomputed. F1/F2 combination arithmetic matches exactly. | Historical intervals/tests/refits remain R; numerical equality does not demonstrate independent confirmation. |
| Original corruption and dropout execution | **V**22 original condition arrays (130 available model-condition sets) and11 dropout arrays checked; AP/AUROC/Brier/ECE match reported points. | No new fault inference, bootstrap or training; original single-realization/selection limits remain. |
| October quality pilot coverage/arithmetic | **V**34 table hashes,753 matched keys each,77 failures/26 recordings;196 finite AP/AUROC/Brier sets;3,777 training parents/11,331 weighted rows; assessment recordings absent from training; q-normalizer moments agree. | This is selected artifact consistency, not a complete audit of every producing inner branch fit or native corruption. |
| Original dropout/audio/object/efficiency studies | **V** completed source/report evidence located; **R** execution/cost/feasibility conclusions retained in inventory R09/R10. | Corrects incomplete coverage in abbreviated summaries, not the historical files. No audio/OOD model result is invented. |

## Material claim gaps and the minimum evidence for a stronger claim

“No further experiment needed” below means the bounded thesis can disclose the gap and weaken its claim. A stronger research claim changes the necessary evidence. No proposed validation below was started.

| Gap | Evidence now / thesis-safe disposition | Minimum evidence only if the stronger claim is retained | Authorization status |
|---|---|---|---|
| **G01: F2 discrimination superiority over F1** | V ΔAP+.001556/ΔAUROC−.000093; R post-hoc intervals span zero. Retain F2 as static reference with its probability-score advantage, not reliable AP superiority. | A genuinely justified precision/confirmation design would require a declared effect size, groups and protected assessment; another post-hoc test on the same scores cannot manufacture the conclusion. | No extra experiment required for narrowed wording. No new inferential claim/test authorized. |
| **G02: unique visual complementarity versus sensor-only recalibration** | Combined-pipeline gain and descriptive error overlap are supported; F2 adds fitting/calibration flexibility. A fold-specific calibrator can alter pooled rankings. | Match the same meta-fitting/calibration procedure using sensor-only probability/logit inputs, original nested training rows and assessment groups; compare to the visual–sensor stacker, without tuning on exposed outcomes. | New logistic fits are training and need explicit approval. Optional if claiming predictive increment only. |
| **G03: adaptation explains original gate/static differences** | V links/constraints/intercepts/losses/calibration/ensembling differ. No isolated adaptation effect. | Static versus contextual models with identical combination domain, intercept/calibration, fitting objective and controlled capacity/regularization; lock protocol before new outcomes. | New fitting/experiment requires approval. Not necessary for a practical-family comparison. |
| **G04: q measures reliability rather than target content** | U; original context sensitivities and October A/B/C do not identify this. C has direct q and p×q pathways; parameter counts differ3/11/27. | From verified saved OOF inputs, predeclare q-only and interaction-only controls, conditional held-out branch-loss associations given probability/action/duration, and paired q-neutral/shuffled controls. Keep diagnostic association distinct from causal trust. | Optional small-head fitting still requires approval; see [TASK3 candidate B](TASK3_EXPERIMENT_DECISIONS.md). No mandatory new model if reliability wording is removed. |
| **G05: reliable quality-aware robustness/clean preservation** | V C−A primary+.003012; R interval permits harm/benefit and clean interval permits loss. No superiority, equivalence or zero-cost result. | Lock primary mixture, meaningful-effect/clean-loss margins, groups and full coverage before additional fits/inference. Broader exposed folds can measure heterogeneity/precision, not pristine confirmation. New independent acquisition needed for a truly protected confirmation claim. | New fits/native inference require approval. September's .01 margin is not approval of an October margin. |
| **G06: learned temporal order caused the pooling gain** | R last-quarter/bin effects; V3 is fixed location averaging, GRU result unresolved and changes capacity. | Matched frame multiset, head family/capacity/budget and order/permutation/position controls, with appropriate grouped assessment. | Optional new experiment requires approval; current location/aggregation claim needs none. |
| **G07: PHM physical-damage truth** | V proxy definition and saved-target consistency; R selected human calls/photometric diagnostics. No validated quantitative damage area. | Independent blinded expert measurement/annotation across relevant runs/acquisition conditions, suitable area/ordinal endpoints, adjudication and uncertainty. More pseudo-label fitting cannot validate the measurement. | Human/data-access plan requires researcher/supervisor judgment and separately authorized work. Existing feasibility chapter can remain provisional. |
| **G08: PHM PatchTST batch/padding concern** | V patch grid derives from padded tensor length, patch validity is any real sample. Static source concern; U output or historical-score impact. | Tiny CPU fixed-weight, eval-mode check of the same short sequence alone versus longer padded batch with identical valid prefix; inspect tokens/masks and set numerical tolerance. If outputs change, locate affected historical evaluations before any score reinterpretation. | **Not executed.** A neural forward diagnostic is outside this task's saved-artifact arithmetic; obtain explicit approval. Any code correction and retraining would be a separate scientific change with regression tests. |
| **G09: effective PHM historical configuration/producing source** | V current runner consumes pinned v3 targets while YAML target label remains v2 and device defaults differ. Older dirty provenance conflated tracked changes with untracked outputs. No inference that every historical dirty flag proves changed code. | Reconcile exact saved command, source hashes/diff, runtime device, effective consumed inputs/config and model state for the selected run. If unrecoverable, retain explicit provenance limits; do not reconstruct certainty from current source alone. | Further small-artifact reads may be bounded if separately scoped; model replay/refit needs approval. No old config/result edits here. |
| **G10: grouping and adaptive assessment exposure** | V recording partitions agree; R same-day/scene effects and extensive sequential assessment. PHM has only three experiments. | Document known session/operator/object/tool dependencies and development decisions; new protected acquisitions if unseen-domain claims are required. Existing folds/seeds/fault realizations are not new independent units. | No new experiment required for restricted grouping/exposure statements; new validation campaign requires approval. |
| **G11: raw-to-cache-to-prediction provenance** | Selected hashes, saved keys/labels/metadata and scalar arithmetic agree. R upstream replay/native audits exist. The complete raw-to-fit chain was not rerun. | Claim-specific manifest/source binding for selected headline rows; if needed, a separately approved bounded native replay. A full clean-environment reproduction is a distinct, potentially expensive activity. | Raw scans/extraction, model replay or reproduction require additional scope/approval. Do not call this package fully reproduced or leakage-free. |
| **G12: native clock misalignment** | U; existing time-block dropout/pooling preserve timestamps and do not test clock offsets. Exposé §5.6 did name temporal shifts. | Establish native clocks/units/coverage, define signed shifts/edge behavior, zero-shift replay and matched frozen-model offset assessment. Saved scalar probabilities alone cannot create this intervention. | New native access/inference needs approval. Supervisor may accept explicit exclusion instead. |
| **G13: audio and literal tri-modal scope** | R completed audio gate found zero verified annotation-to-waveform mappings; no AST trained. Public/nominal audio availability is different from qualified local alignment. | Only if required: independently validate segment clock mapping and usable mechanical-audio information, excluding spoken outcome leakage, before predictive work. | No download, decoding, new audit or fitting authorized. Gate exclusion is a valid feasibility result, not model ineffectiveness. |
| **G14: literal shared-embedding gate and process awareness** | RE original gates are scalar-logit adaptation; PHM has a separate sensor embedding gate. Context changes allocation but not demonstrably useful process awareness. | Supervisor acceptance of scope adaptation, or a specifically justified matched representation-gate experiment. No need to implement a paper model solely for its name. | Scope decision belongs to researcher/supervisor; new model requires approval. |
| **G15: physical-instance/unseen-site/OOD validity** | R categories connect148 recordings in one graph; physical instance IDs not verified. No qualifying object/site OOD model result. | Valid physical grouping and independent acquisition support before fitting/evaluation; do not treat category strings as instance IDs. | Separate feasibility/design approval required; no new OOD experiment here. |
| **G16: online warning/practical usability** | Whole known completed intervals, end-of-action frames, warm component timings. No causal prospective prediction or plant alarm-cost study. | Prospective observation cutoff, acquisition/processing timing, preselected decision costs/false alarms and actual user evaluation if those claims are required. | New research scope; not necessary for honest offline evaluation. No operator contact or deployment authorized. |
| **G17: external MSM validation** | U; no qualifying project pairing, target/group audit or trained result. PHM and REASSEMBLE are different tasks, not a fitted-model transfer test. | Separate feasibility audit of native modality pairing/clocks, labels/tool/workpiece/operation groups, access/licence and protected assessment; then declared dataset-specific training if justified. | Optional only. No dataset download, inference or training authorized; not an automatic thesis requirement. |
| **G18: “no signal”, equivalent predictors or universal failure** | Not beating a reference, marginal intervals or flat ablations do not establish absence/equivalence. Selected diagnostics are small and assumption-dependent. | A defensible equivalence/usefulness design would need prespecified margins and adequate groups; universal absence is not established by another limited experiment. | Narrow wording now. No automatic rescue/expansion. |
| **G19: novelty/strict replication** | Established stacking/gating/augmentation/conditional modulation precedents; local objectives/protocols differ. No exact paper-benchmark replication or algorithmic priority established. | A claim-specific comprehensive prior-art/derivation and controlled contribution study if algorithmic novelty is required. | No novelty claim in present thesis foundation; supervisor judgment on contribution expectations. |
| **G20: historical monotonic metric interpretation** | V code fits isotonic prediction-to-target mapping on the scored assessment set; R null diagnostics do not establish useful rank generalization. Exact official challenge rules were not independently verified. | If discussing the organizer metric, verify its primary specification and label this retrospective estimand explicitly; deployable calibration requires training-side fitting. | Existing historical diagnostic may be described with these limits. No new fitting/resampling or official-metric certification here. |

## Corrections and qualifications carried forward without rewriting history

1. **Different human-review samples:** PHM selected42 images/38 determinate calls belong to AnomalyDINO/target-semantics diagnostics. REASSEMBLE64 clips/59 determinate judgments/57 agreements belong to the separate action-label review. TASK3 claim C16 mentions the64-clip review within a PHM target-validity row; that evidence must not be used as PHM validation. The TASK3 file is preserved; this package supplies the explicit attribution correction. Neither sample establishes population label accuracy, physical area accuracy or second-rater reliability.
2. **Completed original work:** modality-dropout, audio/object feasibility and efficiency have dedicated completion artifacts. A short Section3/TASK3 summary's omission is not evidence that they were unrun. Conversely, cancelled September Task1's partial artifacts are not a completed result; later pooling and October tuning are separate studies.
3. **PHM report language:** historical “no signal,” “effectively constant,” “clean null” and universal “dilution not binding” statements exceed the shown evidence. Keep reported numbers; narrow conclusions. Overlapping model intervals do not establish equality, and synthetic controls do not eliminate every implementation defect.
4. **Gear-indicator method fidelity:** source names alone do not certify original formulas. Local residual/variance choices are material adaptations; see inventory P12. The [primary NASA gear study](https://ntrs.nasa.gov/api/citations/20090039501/downloads/20090039501.pdf), pp.4–5 and Appendix A, also reports that FM4 may decrease as pitting progresses. Thus a globally positive damage association is an expectation to justify per indicator, not a universal physical law. Formula audit/physical interpretation must precede claims that negative signs prove impossibility. No old feature formula/result was changed.
5. **Sector rotation:** sorting removes sector-index dependence; arbitrary angular phase changes can move content across fixed sector boundaries. Do not claim mathematically exact rotation invariance from sorting alone. This I qualification does not recompute the reported screen.
6. **Repeatability scale:** PHM's reported .796pp within-tooth repeat-photo SD is not the same estimand as run top-three prediction MAE or a paired model-difference standard error. It is evidence of measurement variability, not proof that every smaller model contrast is scientifically undetectable.
7. **Within-stage holdout versus global exposure:** August “one F test pass” can be true for that run, while the global F dataset was repeatedly assessed later. LOEO/fresh seeds do not erase that development history. The same qualification applies to later REASSEMBLE studies predeclared after earlier outer results.
8. **New literature boundary:** TASK4's targeted primary check of gear diagnostics/RankNet/logarithmic pooling is a method-fidelity check, not a new systematic review. The [2026 Song extended abstract](https://www.papers.phmsociety.org/index.php/phmconf/article/view/5263) was also identified as relevant PHM prior art; its existence further argues against claiming gear-indicator insensitivity as a first discovery. No task-matched result, complete technical appraisal or numerical comparison is inferred from that screen.
9. **PHM frozen-image extraction versus feature use:** the inspected P01 extractor calls full Ultralytics `model.predict` while hooking intermediate maps. It does not bypass the detector decoder as the separate REASSEMBLE prefix does. The scalar head consumes hybrid-map features, not detections; that narrower representation path must not be confused with the full extraction execution/cost. This distinction qualifies shorter “frozen encoder” descriptions without changing any result.
10. **Monotonic score mapping:** historical in-sample isotonic rescoring uses assessment truth to fit the score transform. Its numerical value is a retrospective shape-agreement diagnostic, not held-out probability calibration or a deployable prediction score. Citing the local implementation as the “official challenge metric” additionally requires its primary specification; no such new verification is claimed. Target cumulative maxima and sorted output profiles implement different operators.

## Validation performed in TASK4

### Scope and method

Standalone Python `-B` scripts used NumPy/Pandas/scikit-learn/SciPy and standard-library hashes. **No project module, Torch model, checkpoint or GPU runtime was imported/executed.** PDF extraction used already installed pypdf. Selected saved artifacts were each guarded to be under20MB. No full archive hash/CRC/extraction, raw HDF5/media scan, feature regeneration, bootstrap or new metric-optimized fitting occurred. Temporary audit scripts/results were written under `/tmp`; the durable input identity manifest is included below.

The numerical procedure was:

1. Load retained cohort Parquet, apply the exact source filter, check unique recording/segment keys, label mapping, ordered core labels and nested partition membership. Check complete outer/inner coverage and disjoint recording sets. This uses retained metadata, not fresh native annotation reading.
2. Load core OOF NPZ and six S1 observed NPZ files with `allow_pickle=False`. Compute sklearn AP/AUROC, empirical Brier, fixed15-bin ECE and confusion-derived balanced accuracy/macroF1/recall/precision. Compare the eight core metrics against the saved Section2 point estimates at1e−12; maximum discrepancy **0**. Do not resample scores.
3. Check F1 exact probability mean; evaluate F2's saved three-coefficient arithmetic foldwise against saved branch probabilities and threshold decisions; maximum difference **0**. Inspect original gate bounds using clipped branch probabilities; largest apparent violation **1.124e−8**, within the declared2e−7 float32-scale diagnostic tolerance. This is scalar saved-artifact arithmetic, not neural inference or proof of a causal mechanism.
4. Read22 original corruption arrays and11 dropout arrays, check common labels/folds, recompute AP/AUROC/Brier/ECE. All corresponding saved points match within1e−12 (observed maximum0 for original suite). Unavailable models remain unavailable. No interval re-estimation.
5. Recompute PHM CSV MAEs and direct differences on unique experiment/run keys; check all corresponding truth values against the retained v3 target table. Read historical intervals from their JSON; explicitly preserve bootstrap-mean versus empirical-point distinction.
6. Verify SHA256 of34 pilot tables against their index. Check identical sorted sample/recording/segment/label coverage,753 actions/77 failures/26 recordings. Recompute196 available AP/AUROC/Brier sets and compare to saved per-condition rows; maximum discrepancy **5.56e−17**. Average repeats, then severities, then the two Gaussian families equally; reproduce the primary contrast. Both-absent rows are counted, not silently removed failures.
7. Read only the6.15MB saved pilot OOF table and small completion/components JSON. Check11,331 rows/3,777 parents, three variants/parent, label consistency, weights .5/.25/.25 summing1, role/component IDs, no assessment sample/recording overlap and weighted q means/SD. Normalizer maximum discrepancy **0**. This closes the previously header-only check for these properties, not the entire native inner-fit lineage.
8. Preserve the original PDF/review PDF and ten existing TASK2B/TASK3 documents by SHA256. Check compact cited source/evidence files against a separate snapshot. Validate links/Markdown/numeric transcriptions, dependency consistency and Git status/whitespace. Final outcomes are recorded below after validation.

Software used for numeric arithmetic: Python3.12.3, NumPy2.4.6, Pandas2.3.3, scikit-learn1.7.2. These describe the **audit** environment, not every historical training environment. No package was installed/updated.

### Evidence identities and reproducible arithmetic example

The107-entry input-path/SHA256 dictionary for the numerical audit, serialized as sorted-key compact JSON, has SHA256:

`802624895055427c24c6922d34b4e7f9ec4564f20e07feb97e417fcfc1631e90`.

The full relative-path dictionary is below. Inexpensive input hashes identify the inspected artifacts; they do not establish the truth of their labels or the historical source that produced them. Documents/costs/intervals labelled R were read from their linked sources, not regenerated. The separately preserved historical-document hashes and final validation outcomes follow the numerical manifest.

An illustrative read-only reconstruction of the two main point comparisons, from the repository root (does not retrain/re-estimate uncertainty):

```python
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

root = Path.cwd()
with np.load(root / "runs/reassemble/20260927T192852Z-section2/predictions/oof.npz",
             allow_pickle=False) as z:
    y = z["y"]
    assert len(y) == 4530 and y.sum() == 509
    for m in ("U1", "U2", "F1", "F2", "F3", "F4", "F5", "F6"):
        print(m, average_precision_score(y, z[m + "_p"]),
              roc_auc_score(y, z[m + "_p"]))
    print("F2-U1 AP", average_precision_score(y, z["F2_p"])
          - average_precision_score(y, z["U1_p"]))
t = pd.read_csv(root / "runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv",
                float_precision="round_trip")
for name, group in t.groupby("model"):
    print(name, len(group), (group.y_true - group.y_pred).abs().mean())
```

The full TASK4 audit additionally made the bounded identity, corruption/dropout and pilot checks described above. This compact example is not misrepresented as all of those checks.

<details>
<summary>107 numerical-audit input identities (repository-relative paths)</summary>

| Input artifact | SHA256 |
|---|---|
| `00_experiments/adaptive_fusion_robustness/results/run_01/comparison/coverage_and_prediction_index.csv` | `6e145c452b1622eee36f7b5dda94f927722ea29708ba7b0ba805f824583f9e4f` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/comparison/per_condition_metrics.csv` | `4c7594b4b836814621531a6066942fe3907bf70915985d0cd4f8c9a427ed7d57` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/fusion_fits/fold_01/complete.json` | `0c6b23f2424bcd8dd594af1b0d13d4ca6ba2c96d7073abb03a5ad71cabc20d39` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/fusion_fits/fold_01/components.json` | `40fa849f9056d6bda21b18ca96c7bec4df02f9e5e5329f8feaf2316fbaa93652` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/fusion_fits/fold_01/identified_OOF_training_inputs.csv` | `b6f6b4385824ce18a05a7e249c402b1f6e2153b58e99a66c79c102a9b516db4c` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/clean/clean/repeat_00/predictions.csv` | `774bbfdc39291b6de6d1d6a4b32bbac57f28d0c3cfb99b7cffbdbc75f7305e53` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_blur/medium/repeat_00/predictions.csv` | `4de9ab4940539f1519f4f19c8c0070b331a4d493ea96991ba26a63cca53797df` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_blur/mild/repeat_00/predictions.csv` | `0a247f0caff8717c803c006a7448e05acba96dbe70ed820fe35b68829731c6ef` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_blur/strong/repeat_00/predictions.csv` | `e13fe0b0580e8603b47579df701c025ed721384cf464587921b4b6dcb35da2c0` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/medium/repeat_01/predictions.csv` | `f486d74ab31c4270a6a3dc5e278798a87a183c7b2bad637d1cfcdafbd595cb88` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/medium/repeat_02/predictions.csv` | `c9fca774b329f4b74873c012467d35f87b551981ec49c63420aa5f13f7d74e2b` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/medium/repeat_03/predictions.csv` | `23bb3a79e5dea1dfc517cb81d2c0838e1b5c01f1bd7560e762ad2cefbc084ada` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/mild/repeat_01/predictions.csv` | `487969961ea470de66bef6169fc2bf50db7ee239195c890e62ae8a67935c659b` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/mild/repeat_02/predictions.csv` | `1a949ee248a6edaf2121821480667bf8aae4b3cf3ef4b257268a1dbde7cc1422` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/mild/repeat_03/predictions.csv` | `c0f64863664034cfe3e27015ff6236bd3cdf88f0e005cb3f0e81605e188cca54` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/strong/repeat_01/predictions.csv` | `a437d633661be2a8d28ce3b5151b9de4e4ee3f5b27d070130417552f44f29f67` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/strong/repeat_02/predictions.csv` | `2fbda98a680062f9899e9ea5fd1c9e819e2a3178d15921616c35725e971c4757` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/image_noise/strong/repeat_03/predictions.csv` | `b8d0f319650bc8e020fc9502d3746c0acd738ace3ec0b7f34f027e1be20057ff` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/missing_modality/both_absent/repeat_00/predictions.csv` | `2adb33047e73d1a0c2d6217d3d5ebee63b7e2ed2e5db24a5a13a87b298ebe358` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/missing_modality/image_absent/repeat_00/predictions.csv` | `9d32217aa7af212a8e72a05bad53a3f702a6ea12520624be95fee28885f99ce8` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/missing_modality/sensor_absent/repeat_00/predictions.csv` | `cc9d00ad59ae39f5e95c3677522c9e020f49d3273c1f8c68f8c39defadc0ea32` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/medium/repeat_01/predictions.csv` | `eda149d5c44ba2fbff217b299e6c36da62fcd109e5de85734bf8d0110a23f62e` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/medium/repeat_02/predictions.csv` | `14877225559300c24db2b094c2f2e7202f04c611359b39d9530285e64d667f96` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/medium/repeat_03/predictions.csv` | `2f23b3c7de7fdc6cee37941a056ae088587335a3ab0f6018d7c4c57519e7e869` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/mild/repeat_01/predictions.csv` | `3db4478cffbd8c73baca79d2368e45061ed7953b86b2f5375ee3b24971bb6b5c` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/mild/repeat_02/predictions.csv` | `44edcf383ad6faf47fbcf706be3cb5080475edba9f34708a238b87a2dd198e4e` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/mild/repeat_03/predictions.csv` | `d448692e1e78731a82a3172e837fdce947c5afc1312885fb7b4d342ef9e5a41d` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/strong/repeat_01/predictions.csv` | `0d096c3c722907d8b28fef822ab7bfc6c605f14e670dc120d03fb53f3f9166f4` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/strong/repeat_02/predictions.csv` | `fc5df4125642080e0b857f0a9762c7a75b3be64f37c405fb346a2c9c49ea0746` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_noise/strong/repeat_03/predictions.csv` | `73ab63e22aa2d6959d740376b969952da3118a7bc686995ef04ba28e622ccfe5` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/medium/repeat_01/predictions.csv` | `4d1728db1fc40d082bbe5d1f0e3493eaf07dc3e30c2adfde8b205a3f891a0592` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/medium/repeat_02/predictions.csv` | `af6dab567cc3d117cdc4ec00bc5dff33bcb91673db094622615351b23477e432` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/medium/repeat_03/predictions.csv` | `ec6e19aca15800afe0c3fde579294e4759a9a5221058cbe2ab186bbbcebf1ae8` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/mild/repeat_01/predictions.csv` | `54697c63ee3392450ba3af9692b1e5402340c745583e1f3d20160459fd1d27f7` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/mild/repeat_02/predictions.csv` | `a49bc3903e7cb526d34e5966c7a1f0b586688eb03a0a884ecafda6a88d9fe5b3` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/mild/repeat_03/predictions.csv` | `3f5ac101429d6489a8cd1a888e657f1cc7a0e101881aabf08dbac91c716a098a` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/strong/repeat_01/predictions.csv` | `0336737c57ac98128f972825f56e2b1e801976944a8386209772c93d7801c370` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/strong/repeat_02/predictions.csv` | `f307ddafb89a8e017404b003b7e78b5d629f644710c908dc7496d6d2ce7336ab` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/predictions/fold_01/sensor_time_loss/strong/repeat_03/predictions.csv` | `58f1d4f852bc243ca3e51d636b3a83a0dd0d5f6546dfda17a429c75ec9c15bd4` |
| `artifacts/reassemble/audits/nested_splits.json` | `56dd1f32282a5771e16f780180e3cf62aa2684ae8e855ffd441418f91f14a668` |
| `runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/tables/run_damage_targets.parquet` | `e5e098e01822307791138b83c015307ae74a5b2fdaf80957e413170a343e92f1` |
| `runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv` | `b455864466c0aed759756c674d373d30c9f70905cdbb55e7c00ab53b565b72f4` |
| `runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort.parquet` | `1e4b971d9ce97c12d79f8fc43a44f7cf97de57ad3f475d18e925a916b23f22b2` |
| `runs/reassemble/20260927T154732Z-section1/predictions/action_only_perm00.npz` | `9495987043470386899d8b0e90fdb390f5aada5326ff11e8242cad51c6b80214` |
| `runs/reassemble/20260927T154732Z-section1/predictions/majority_perm00.npz` | `13eacda35610b96ac9697e138be37ce7f1ce0b1994b0daca397ab978f5fccb28` |
| `runs/reassemble/20260927T154732Z-section1/predictions/patchtst_perm00.npz` | `2ff53f7ae05e2221dee164bb26726b3a6e85a92dd65e79d198a685c6f0de46da` |
| `runs/reassemble/20260927T154732Z-section1/predictions/prior_perm00.npz` | `be3f0e54a5b7b8541dbcf1fbcaf06e72dbf6ea0250eab383221a48cccfdab72b` |
| `runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00.npz` | `5a8c656571b44e35ecdba5dbc24cc96291e4183a6c750bc53745719838b769d8` |
| `runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00_fold0.json` | `39215e1bb6a257d043aea1421ec28531248bcca6462de476c4a33032b8a96b21` |
| `runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00_fold1.json` | `219ae266f790ed977410f0b7148764c2799498c919ea13fca7f907b30ffb665f` |
| `runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00_fold2.json` | `1c12bd9d32c6f1f15a11ba35bc92010d2be0d990abe750658d727bfb3f50aa42` |
| `runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00_fold3.json` | `e11e523e56927124fa56d48035511b4174acef7e5aa4ae6a8abb4c00c5f89b23` |
| `runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00_fold4.json` | `9ef85ce53eae03c66b319e64ed0d9d3007623c0b7bc1d7bfe273bd1f4b8b1329` |
| `runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00.npz` | `7113f40880df7b839dd3d1fb7522cb712f7dfcae74d6c1be182f982cf1bf5e1e` |
| `runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00_fold0.json` | `b141775f8d709d988ad5dce6e5bed879760329a5fa753e0db4cad35a67886014` |
| `runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00_fold1.json` | `f728fb40f13af1afa872460d5c7492682a8b6a7636e1007f9e97777220a2aa67` |
| `runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00_fold2.json` | `e4b615a8dc635006d7b2dba094ab8c023823e80c18a1b1e3199793f12ae4d1c1` |
| `runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00_fold3.json` | `f69e0804ebb771e009623aadb933540041336157615deddb03a669b9ff0960c4` |
| `runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00_fold4.json` | `5e1608cdcc57e0dedcc2a9ce3fc39dc7ae6c2ebff66b3bdcaf205498041f8877` |
| `runs/reassemble/20260927T175336Z-section1b/stacking/outer0.json` | `365decd18283c0ba3f6012f96f7dceed6156dd2d7c4d1227b3bd848ffdf94a7a` |
| `runs/reassemble/20260927T175336Z-section1b/stacking/outer1.json` | `042c19a4e356f729d8b1143be23a2c7db10dff620ad1772a140e94f2adb7068a` |
| `runs/reassemble/20260927T175336Z-section1b/stacking/outer2.json` | `8f0d374837ed92340fb41ea6b87774bd07e4f5847092684603cbb3b9352dc2d9` |
| `runs/reassemble/20260927T175336Z-section1b/stacking/outer3.json` | `bda1c5a224389692d459b8f9cefad358e7edacb3500980d36fc417450a345bd9` |
| `runs/reassemble/20260927T175336Z-section1b/stacking/outer4.json` | `ef2ba03990fdc20094be68b3543f403dfc7fc4bbde21814bc3938062cf28688d` |
| `runs/reassemble/20260927T192852Z-section2/assessment/results.json` | `991aaf33708a8c795a9f0d7ee3e9665788dd98c347752e1a87affdf3746956c6` |
| `runs/reassemble/20260927T192852Z-section2/assessment/review_comparisons.json` | `4919188b54af6d82bdc7e022007e4f4b3080399862164ab4595b27b3caf0ab8a` |
| `runs/reassemble/20260927T192852Z-section2/predictions/oof.npz` | `e2ca736b2dccdb33a1dfc0cf33c2001a3b69cdb2d8ef82d5241c4f34b740995a` |
| `runs/reassemble/20260927T192852Z-section2/predictions/outer0.json` | `2e499ddb4f59881901fd92a3b71d2a3ad068be5a8549c790b4b82e7533f531ae` |
| `runs/reassemble/20260927T192852Z-section2/predictions/outer1.json` | `ac9844820893b2626bfc52c828cdf3bc3a3aee4fe407e1a7ccd958c3aa45752c` |
| `runs/reassemble/20260927T192852Z-section2/predictions/outer2.json` | `4b2ee7f9e69dfadce09656c68a57d8b40a09dd9b9988f0eb19f4948c33f5e2a1` |
| `runs/reassemble/20260927T192852Z-section2/predictions/outer3.json` | `96d8c34c201391664c586608d2a4755a594db437594f412af493cd2c6cbf080f` |
| `runs/reassemble/20260927T192852Z-section2/predictions/outer4.json` | `d0b70802c43cc0b88f8df991d41fef6b250730c2a4c2395a95b7061d94fb810f` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/S1_0.1.npz` | `6d76c0bf44586e1bf9aa04546448988640e32e69a1359b8860645534d714f22a` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/S1_0.5.npz` | `aa69ead8c490fb991879d84c0f372c98026d14f8a2e02caccfadb58e16d62ce8` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/S1_1.0.npz` | `bff292177cdd85275992f5233b2e18befb1333f16eae4631732804b2eb1954e7` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/S2_0.3.npz` | `c7d5c9777dfd8636b53ba59c45f4d19239c13bbd2e9e0eb9396660bf36e53a34` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/S5.npz` | `112d3aaecc5158540d23e4f001170b8c00f2950886606a4b6552fa4048a8df12` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/V1_0.02.npz` | `a2baf68f4c2656796fad7f54e25a16b88d041519755a6660c6b9cde719456399` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/V1_0.05.npz` | `f3010f665077114b8dcd349c2d2fbfa9bb4d63e5b6dbc21570dc564de8a67202` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/V1_0.1.npz` | `ad28ea03b8b04472c9e58032c1ccad5ac41d610b83c05b2dff08ca89bb3d5c17` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/V2_2.0.npz` | `72065fad7f19e7028d960a6e0edf79aeef4d3eb2dc8d2af0fd83383d76c755b6` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/V4.npz` | `bbe14be41bc8545fac3c93ee274c2dbc84dbe553f5acbe3bd1d202daf25fe464` |
| `runs/reassemble/20260927T204649Z-modality-dropout/predictions/clean.npz` | `b152aff34ec1f860ac2301996949c493a5fb500b86de681667b92fc14df629f7` |
| `runs/reassemble/20260927T204649Z-modality-dropout/results.json` | `c42197224322ac76662acb8acfae64de1440b723a37c2af4170a8c657540c9fb` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S1_0.1.npz` | `729eddc340162f62145b5e4ad0097802542f8b5c5281269b27aff96d50d4fbe9` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S1_0.5.npz` | `5874b7efb0c3264f2f4d35a07111e69c33912c87bd07c3a8d08b964d3be7c467` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S1_1.0.npz` | `c140d083d9293b7bd4a0dbbbb447cf4a08e8930decd58545863f6a2a29c68671` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S2_0.1.npz` | `0d1d229967331792e46299b71f9bb21763d6c84ef830a46fe6d6c26a024b2111` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S2_0.3.npz` | `7f0d014df72e88967408b09726aa25713551fc08b01645567fa763452a1ba890` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S2_0.5.npz` | `91d1b58af0f40476ef22b2d55193b4a5fc0869c2197fc114b920bf147dd4d257` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S3_0.1.npz` | `b7156f092c5ebb7be7723894340a7930d0fb19150fbfafca46f8959e6aaa0be5` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S3_0.3.npz` | `af40b61ab3b0be9bd23ce5815d594d8e31caa9f39e4343bcbe0e7fec2ef80455` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S3_0.5.npz` | `8224195685fd347c44ebbdcce955eb083f848a1f21448867d0ca67d1644c2f2a` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S4.npz` | `ee31012c257ff88d5b3debeb10cccaca107b56eeb4ee9f938ccaa003e198fa5f` |
| `runs/reassemble/20260927T204649Z-section3/predictions/S5.npz` | `2ca2c33fec1d825a263c8016866619862f0a57ac28db8184d8d2ed884ac7058f` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V1_0.02.npz` | `524c6072ee86ef74d2863b7958e56ed73101030cf3b663440afc0e5e14ccb6b8` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V1_0.05.npz` | `d70d87efacf82c580d0ed2e169f1a4f4225af61a6d8ef54589f18ea294a267b6` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V1_0.1.npz` | `01c2c7bc8b1b29e0fb4729f8fe152dbd350288bbf071c4729508206b9d897740` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V2_1.0.npz` | `d92ee7168f4137ceee9164a1fa99b7927daf3c2f0da1ad69b1cc960c42190597` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V2_2.0.npz` | `195e0dea0537e7ec92811b2cea3cc5ec02d3d4721c0aa00f5a9ce3afe8a8cf21` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V2_4.0.npz` | `f76ef8304396ee765953b618816c744abd5f27f8ad68326912dfa3e9376f62dd` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V3_0.1.npz` | `b71aa2d464424e303dc48317387d79f77600f5aa9821ba26ff9fd0a84fbe22b6` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V3_0.3.npz` | `1e41d55d777a669eadb57924b26a4c6eaf534cd3ca8ba4f7b63a19c5a0a09665` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V3_0.5.npz` | `b5b828368b41edbc65cac95bfe52de7b17f6cd27eff8107ca46158b31525b780` |
| `runs/reassemble/20260927T204649Z-section3/predictions/V4.npz` | `bff87bf9b20b332cbbf9cc5f732dd04d38b8b96af435f7c57b154da6da338b80` |
| `runs/reassemble/20260927T204649Z-section3/predictions/clean.npz` | `e47acac99a5f7ebd82d61f5b35fa7634b6379a30a65f97555379d2021e5177c8` |
| `runs/reassemble/20260927T204649Z-section3/results.json` | `4e2e94cbc258ee4bc554321edb7e8b73cccaeb2d7599b8bff39d2c3d36c4d76d` |

</details>

### Preserved original documents

All twelve entry hashes remain the preservation reference; final equality is checked separately.

| Original document | SHA256 |
|---|---|
| `MA_Exposé_Ravaliya_Parth.pdf` | `9f7e1c09db5678fe268a39eb8af823cb965153cc69a8922c129117fd815fb6e6` |
| `critical_literature_review.pdf` | `11d1d56cb63550a1f548298e905755a4136fdeafc928f515b23cfed5c416bce7` |
| `docs/thesis_research_direction/EXECUTIVE_REVIEW.md` | `9c1255f87a5ac56c9aa76312ae29af2afcc8880093874bcbc8ef1056f272c549` |
| `docs/thesis_research_direction/EXISTING_EVIDENCE_MAP.md` | `38ff5bc5c4d032c0cf65213213a970f109b1af3083b72ec96183851a14748e54` |
| `docs/thesis_research_direction/EXPOSE_ALIGNMENT_DECISION.md` | `91fb8a2d8700007d1fecb1a09b0ac2f2af94282f4da703d3b22c8052f9ae44f7` |
| `docs/thesis_research_direction/LITERATURE_POSITIONING.md` | `f2062917b7ba3ff0dcdda6270d04a51dbe91a2bfaf4fef034df2c11bd85e0747` |
| `docs/thesis_research_direction/OPEN_RESEARCH_DECISIONS.md` | `233eca3532e37cf2582c25c8d275c28ca1bbee73833042b5b60054a354fa20c2` |
| `docs/thesis_research_direction/RESEARCH_CHARTER.md` | `985a9f4ec1681b244990ff7b2b452be8ec98f3bc84ec6d5b36446200a223fbd4` |
| `docs/thesis_research_direction/TASK3_CLAIM_AUDIT.md` | `b47e0ff71d02ce651a659363588f698ea3300328e82b4ca2ec20e0ea8385e3fe` |
| `docs/thesis_research_direction/TASK3_EXECUTIVE_HANDOFF.md` | `6fa3bfa1e8947b2bb6bf53562c4a7bc720cee464724ec2ecf0920881323a2f65` |
| `docs/thesis_research_direction/TASK3_EXPERIMENT_DECISIONS.md` | `108e1c8be3c5dedf42a474bf9683f86425f628f0b45455e53571548499afbbba` |
| `docs/thesis_research_direction/TASK3_LITERATURE_EXPERIMENT_MATRIX.md` | `b75c247e933beeef3009374293ff1549bc9f3c4271d0ac7053453dd2b3d91b73` |

### Final validation outcome

**PASS — documentation and bounded checks completed on2026-10-26.**

- Five requested new Markdown files exist; original Main/SQ1–SQ4 wording matches the PDF after normalizing extraction whitespace/hyphenation. Six results families A–F and the six contribution categories are present.
- 204 local document links resolve; 27 distinct external source URLs were inventoried. This is not a claim that every publisher link was fetched anew or that every paper received full-text review; TASK3's access limits remain in force.
- All12 entry-protected PDFs/TASK2B/TASK3 files retain their exact SHA256. All216 selected compact source/evidence files match their preservation snapshot; the107 numerical-audit input identities match the embedded dictionary. No full raw-content or whole-workspace preservation scan is claimed.
- Core, original corruption/dropout, PHM point checks and October pilot arithmetic/metadata checks passed as described above. Every interval remains attributed historical evidence; no new bootstrap, model fit or model forward was run.
- `git diff --check` passed; `git diff --stat` is empty because there are no tracked-file changes. Git status adds only the five requested documents beyond the pre-existing untracked PDFs/TASK2B/TASK3 files. The new documentation remains untracked; nothing was staged, committed or pushed.
- `ma_thesis_env/bin/python -B -m pip check` returned **No broken requirements found.** Separate content checks found no broken local links, unbalanced code fences or trailing whitespace in the new files. Project/model tests were not invoked: this task changes documentation and saved arithmetic only.
- Initial sandbox command startup failed before execution (`bwrap` network-namespace setup); permitted bounded operations then used the reviewed execution route. Temporary audit/schema lookups were corrected before successful validation; they did not alter historical artifacts or trigger training.

No validation step requiring additional approval was attempted. Neural padding diagnostics, new meta-head fits, native inference/replays, raw scans and independent validation are explicitly left unexecuted in G02–G17. They are optional/claim-dependent work, not silently completed checks.


## Does the thesis need another experiment?

**P:** not by default. The present evidence supports the original architecture-comparison question with bounded positive, negative and inconclusive answers. Another experiment becomes necessary only if the final agreed claim requires evidence currently absent, such as validated reliability, isolated adaptation causality, physical gear damage or prospective/external performance. Narrowing those claims is scientifically preferable to presenting a new run as an automatic repair.

A targeted PHM padding diagnostic or saved-artifact quality/content control may be small, but each goes beyond the current task's permission (neural forward or new fitted heads). No dependent validation requiring that approval was performed. Existing documentation/arithmetic work is complete; no required background job remains running.

**ONE recommended next activity:** researcher–supervisor evidence and final-scope review using this package, with the concrete decisions in the [chapter plan](THESIS_CHAPTER_PLAN.md). Decide final title/task wording and original-question coverage, accept/disallow precise contribution claims, and determine whether any gap truly warrants a separately approved experiment. Do not reopen the accepted dataset switch. **STOP after this handoff.**
