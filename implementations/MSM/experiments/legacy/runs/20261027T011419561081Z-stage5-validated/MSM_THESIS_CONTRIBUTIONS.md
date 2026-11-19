# MSM thesis contributions

**Position MSM as a bounded research-engineering feasibility case and an explicit limit on external validation.** Its contribution is not a new fusion algorithm, successful learned-weight transfer or proven anomaly-detection performance. The principal predictive evidence remains the separately qualified REASSEMBLE studies.

## Defensible contribution statements

| Contribution | Evidence | Thesis wording that the evidence supports |
| --- | --- | --- |
| Traceable dataset acquisition and label interpretation | Official version-2 identity, 481-file inventory, all 69 annotation files, independently recounted 2,575 intervals; preserved raw files | “A version-pinned external milling dataset was audited before model adaptation, with source identities and native class semantics retained.” |
| Verified multimodal construction contract | Validated Stage 2 acoustic timing, native frame PTS/hash and visibility/coverage checks; 114 common-MTC examples; corrected partial-overlap alignment issue retained | “A filtered laboratory subset supports 16-frame coarse milling-context sequences paired with numerical machine statistics under documented alignment bounds.” |
| Small reusable domain adapters | Native interval/frame/sensor/statistics/label/group adapters; reused existing CNN/head/standardization composition; configured 15-channel sensor schema | “The software interfaces were adapted to milling without duplicating the full framework or imposing robot sensor identities.” |
| New classifier/fusion plumbing verified on a bounded smoke | New visual head, sensor model and OOF F2; root-seed42 development fitting; finite gradients/checkpoint checks reported; current ID/provenance/arithmetic audit | “A bounded development smoke verifies construction and execution, not independent predictive performance.” |
| Scientific admission gates and honest unavailable results | Two positive folders block three-outer/two-inner evaluation; no completed full-CNN source; empty Stage 4 prediction/checkpoint/curve artifacts | “The evaluation was stopped when its group-support and source-model prerequisites were not met, with the missing conclusions explicitly recorded.” |
| Quantitative evidence consolidation | 1,654 saved metric checks; 196 additional pilot AP checks; exact head arithmetic; selected recording-bootstrap intervals; raw MSM label/statistic reconstruction | “Native-data calculations and saved-result consistency were checked separately; historical training was not independently reproduced.” |

These are implemented and auditable engineering/methodology outcomes. Standard CNN reuse, statistical features, logistic regression, probability stacking, group cross-validation and bootstrapping are established methods; do not present their use as algorithmic novelty. Discovery/correction of an invalid exploratory offset is quality control, not proof that the overall approach was originally guaranteed correct.

## How MSM complements the thesis without replacing its main question

The [original nine-page exposé](<../../../MA_Exposé_Ravaliya_Parth.pdf>) organizes architecture design/evaluation through SQ1–SQ4. MSM adds practical evidence about eligibility, clocks, modality schema and grouped support. It does not replace the main question with an external-validation or robustness hypothesis.

- **SQ1:** show the reusable frozen R18vd CNN, its limits, 16-frame pooling and MSM-specific sensor statistics; state that the retained core executes a CNN, not RT-DETR's Transformer/detector. Audio is used as an alignment reference, not an evaluated predictive branch.
- **SQ2:** explain why visual, sensor and F2 components require fresh task-specific fitting. Use REASSEMBLE's verified F2 contrast for actual fusion value; report MSM's value as unmeasured.
- **SQ3:** retain the named REASSEMBLE fault studies and unsuccessful/inconclusive adaptive comparisons. MSM does not contribute a corrupted/missing-modality result.
- **SQ4:** foreground native targets, grouping, honest sample units, class prevalence, source provenance, conditional uncertainty and operational/cost limits. The blocked evaluation is a documented boundary, not an accuracy negative.

## Architecture components: reuse and fitting

| Component | Reused | New MSM work / status |
| --- | --- | --- |
| CNN representation | Local original pretrained R18vd CNN architecture/weights, 896-value spatial pooling | Frozen; verified source identity. No completed REASSEMBLE-trained CNN transferred |
| Frame aggregation | Mean of exactly 16 frame representations | Native interval clocks, guarded selection, frame identities and 640×640 display geometry adapted |
| Visual classifier | Existing small 128-unit constructor | Fresh milling weights/scaler smoke-fitted; full evaluation not run |
| Sensors/statistics | General statistical-interval interface | 15 actual MTC channels × six statistics = 90; new scaler/balanced logistic classifier; robot channel identity/220-statistic contract not reused |
| Static F2 | Two-probability L2 logistic stacking design | Fresh three-parameter smoke F2 from group-held-out predictions; neither source F2 nor smoke weights used for outer evaluation |
| Split/target adapters | General group-separation/OOF requirements | Native label1 vs stable0/2 and folder grouping; exclude-2 sensitivity declared; actual nested evaluation blocked |

The learned-head smoke establishes software operation. It does not demonstrate that full training would improve performance. The independent audit checks its saved provenance and arithmetic, not a historical training rerun. Architecture portability and learned-CNN transfer must occupy separate claim rows.

## What belongs in the thesis

1. **Methods/data:** why native milling labels and video/sensor availability motivated selection; exact official handle/version and license/provenance; acquisition limits; class2 interpretation; alignment correction and quality contract.
2. **Architecture:** a compact diagram of reused frozen CNN plus new domain adapters, head, sensor classifier and F2. State input/output units and that full cut boundaries are known. Distinguish the intended R initialization from the unavailable executed condition.
3. **MSM results:** a cohort/availability table, frame/timeline diagnostics, engineering-smoke scope and explicit Stage 4 status. Mark predictive metrics **not available**, not zero. Do not plot synthetic or empty learning curves as results.
4. **REASSEMBLE results:** protocol-specific AP/AUROC/calibration tables, F2-minus-sensor clustered interval, unsuccessful gates/encoders, mixed fine-tuning effects and bounded positive temporal/anchored findings. Keep visual and fusion gains separate.
5. **Discussion/limitations:** physical grouping, low anomalous-experiment support, native target differences, MTC aggregation latency, visual occlusion, repeated development exposure, conditional uncertainty and missing audio/robustness scope.
6. **Appendix/reproducibility:** exact configuration/source/input manifests, selected epochs/seeds, original/matched budget differences, preservation of failed exploratory/audit attempts and assurance-level ledger. Core software/test evidence belongs here; it is not a substitute for held-out predictive validation.

Suggested concise abstract sentence: **“An additional milling-dataset feasibility audit verified a filtered visual–sensor input contract and modular software adaptation; independent transfer evaluation remained inconclusive because grouped class support and a validated source checkpoint were unavailable.”**

Avoid: “MSM independently validates the architecture”; “REASSEMBLE weights generalize to milling”; “F2 improves MSM”; “the system is robust to missing/corrupted industrial sensors”; “CNN compatibility proves transferred knowledge.” Those claims require evidence not produced.

## Relevant successful, unsuccessful and inconclusive outcomes

Core REASSEMBLE F2 improves AP over its sensor reference by **0.017907 [0.008603,0.028284]** on the retained protocol; this is a bounded positive empirical result, not an MSM contribution or a universal superiority finding. Later anchored clean adaptation also has a positive AP contrast under its own procedure, so “every adaptive model failed” is incorrect. Longer PatchTST improves over matched short training yet still trails statistics. Original clean gates do not meet their criteria; the quality-aware robustness pilot remains inconclusive.

For MSM, aligned data construction and the development pipeline are supported. Held-out accuracy, F2 gain, learned-CNN transfer and seed/robustness claims remain unanswered. Keeping that distinction is central to a credible thesis, even if no further experiment is undertaken. No model was trained in this consolidation.
