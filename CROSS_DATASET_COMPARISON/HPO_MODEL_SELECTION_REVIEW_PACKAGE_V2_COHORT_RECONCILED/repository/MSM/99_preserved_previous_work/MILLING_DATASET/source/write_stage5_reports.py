#!/usr/bin/env python3
"""Synthesize bounded thesis claims from the completed no-training audit."""
import argparse
import ast
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from msm.data import digest
from msm.smoke import write


def main(run):
    run = Path(run)
    c = json.loads((run / "config/resolved_config.json").read_text())
    audit = json.loads((run / "validation.json").read_text())
    msm = json.loads((run / "manifests/MSM_audit.json").read_text())
    core = json.loads((run / "manifests/REASSEMBLE_core_audit.json").read_text())
    extensions = json.loads((run / "manifests/REASSEMBLE_extensions_audit.json").read_text())
    quality = json.loads((run / "manifests/quality_pilot_audit.json").read_text())
    protocols = json.loads((run / "manifests/protocol_checkpoint_audit.json").read_text())
    later = json.loads((run / "manifests/later_sensor_fusion_audit.json").read_text())
    if not audit["passed"] or audit["new_model_fits"] or audit["CUDA_context_created"]:
        raise ValueError("Unexpected audit status")

    def link(path, label):
        return f"[{label}](<{os.path.relpath(path, run)}>)"

    s1 = link(c["stage1"] + "/MSM_LABEL_AUDIT.md", "MSM native-label audit")
    s2 = link(c["stage2"] + "/MSM_VIDEO_ALIGNMENT_REPORT.md", "validated MSM alignment")
    s3 = link(c["stage3"] + "/MSM_STAGE3_EXPERIMENT_PROTOCOL.md", "frozen MSM protocol")
    s4 = link(c["stage4"] + "/MSM_STAGE4_MODEL_RESULTS.md", "MSM Stage 4 status")
    r1 = link(c["reassemble_section1"] + "/assessment/results.json", "REASSEMBLE unimodal metrics")
    r2 = link(c["reassemble_section1b"] + "/assessment/results.json", "REASSEMBLE static-fusion metrics")
    r3 = link(c["reassemble_section2"] + "/assessment/results.json", "REASSEMBLE clean-fusion comparison")
    r4 = link(c["reassemble_section3"] + "/results.json", "REASSEMBLE corruption results")
    rq = link(c["quality_pilot"] + "/comparison/paired_intervals.csv", "quality-pilot contrasts")
    e8 = link(c["controlled32"] + "/results/comparison/fusion_results.csv", "controlled two-epoch 32-frame results")
    ex = link(c["original_expose"], "original nine-page exposé")
    old = link(c["prior_audit_attempt"], "preserved first Stage 5 audit attempt")
    paired = core["selected_F2_sensor_CIs_recalculated"]
    prevalence_reassemble = 509 / 4530
    prevalence_msm = 10 / 114

    def report(name, body):
        with (run / name).open("x") as stream:
            stream.write(body.strip() + "\n")

    matrix = """| Research question | REASSEMBLE evidence | MSM evidence | Defensible conclusion | Remaining limitation |
| --- | --- | --- | --- | --- |
| SQ1: Representations | Recalculated core AP: statistics 0.429392, frozen CNN 0.230658, short PatchTST 0.241591. Longer PatchTST 0.285311 still trails statistics; separate hybrid visual encoder loses its fixed comparison. Boundary pooling is a separate positive exploratory visual result. | 16 aligned frames plus 90 statistics are feasible for 114 intervals; new-head/sensor/F2 smoke works. No held-experiment performance; no audio classifier. | Tested representations can be implemented and compared, and simpler representations can be competitive under specific budgets. MSM adds engineering feasibility, not external predictive validation. | The retained RT-DETR path is a ResNet CNN, not its Transformer/detector. Audio/AST and literal trimodal scope remain untested; richer candidates, budgets and causal explanations are incomplete. |
| SQ2: Fusion strategies | Core F2 AP 0.447299 versus sensor 0.429392; paired gain +0.017907 [0.008603,0.028284]. Original gates do not meet their clean incremental criteria. Later anchored adaptation improves clean AP under its separate protocol. | Fresh static F2 is implemented and smoke-fitted from group-OOF branch probabilities; Stage 4 has zero held-out predictions. No MSM adaptive gate comparison. | Small learned late fusion adds bounded value in REASSEMBLE; visual gains and fusion gains must be measured separately. No MSM F2-value conclusion is available. | Repeated same-cohort development; different protocols must not be pooled. Original scalar-logit gates materially adapt the exposé's projected-representation proposal. No universal static/adaptive ranking. |
| SQ3: Robustness | Original F5/F6 satisfy neither joint mechanism/outcome criterion across all tested highest-severity family comparisons (0/12 successes). Exact missing-branch fallback is imposed. Later augmentation-matched quality pilot: +0.003012 AP, CI [-0.026711,0.032165], inconclusive. | No missing/degraded/corrupted-modality experiment; an independent dataset and valid clock mapping do not test adaptive reliability. | Robustness is partially investigated on REASSEMBLE under named synthetic faults; MSM contributes no adaptive-robustness evidence. | Synthetic faults, exposed data, limited realizations, and untested cross-modal clock shifts/field failures. No clean noninferiority or universal reliability awareness. |
| SQ4: Evaluation | Recording-group folds, OOF stacking, calibration/threshold metrics, cost records and modularity are auditable. Selected metrics/intervals reproduce from saved predictions. | Version pinning, native labels, timing/visibility gates, raw statistics, strict split/source admission and explicit unavailable results prevent unsupported external claims. | Strong contribution in traceable evaluation and research software; operational assurance is a distinct unresolved question. | Recording/folder separation does not prove physical-session independence. Gate weights are not causal explanations; warm/shared GPU timings do not certify deployment or prospective warning. |"""

    report("MSM_FINAL_EVIDENCE_REVIEW.md", f"""
# MSM final evidence review

**Scientific verdict:** MSM supports a versioned, alignment-audited engineering feasibility case for a coarse visual-plus-sensor interval classifier. It does **not** currently establish independent predictive adaptation, REASSEMBLE-trained CNN transfer, F2 benefit on MSM, seed stability or modality robustness. REASSEMBLE separately retains bounded representation/fusion evidence. These conclusions are different and must remain separate in the thesis.

Review UTC: **{audit['UTC']}**. Run `{run}`. No model was trained, no optimizer update ran, no raw CNN inference was performed and no CUDA context was created. Frozen MSM dataset: **`manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`**, Kaggle ID 8392825, [dataset DOI](https://doi.org/10.34740/kaggle/ds/8392825); [publication](https://www.nature.com/articles/s41597-026-07255-7). Stage 1 established official identity and version; this consolidation checks the retained pinned evidence, not a new live download.

## 1. Sources, chronology and evidence language

Primary question wording was read directly from {ex}, pp.2–3; PDF SHA-256 **{protocols['original_expose_sha256']}**. The repository's October 25 alignment record accurately recovers those questions. Its historical statement that MSM was unexecuted is superseded by October 27 Stages 1–4 for acquisition/implementation, **not** by a successful MSM accuracy evaluation. Earlier original-question proxy statements are not treated as newer authority than the PDF.

Reviewed MSM evidence: {s1}; {s2}; {s3}; {s4}; their acquisition, architecture, implementation, transfer/generalization, validation, manifest and checkpoint artifacts. Relevant REASSEMBLE evidence: {r1}, {r2}, {r3}, {r4}, temporal pooling, encoder comparison, matched 32-frame fine-tuning, longer sensor training, anchored clean adaptation, quality-aware robustness pilot and the live Phase 1 completed-fit receipts.

Use these evidence levels throughout:

| Level | What it means here | What it does not mean |
| --- | --- | --- |
| Independently recalculated from native MSM inputs | Re-read 69 actual label files; recounted classes/groups/durations; recomputed 114 × 90 cut statistics directly from actual MTC rows using independent NumPy formulas | Independent expert label adjudication, physical sensor synchronization or model retraining |
| Recalculated from saved predictions | Recomputed point metrics, exact coefficient arithmetic and two selected 2,000-draw bootstrap comparisons | Raw-input-to-trained-model replication or fresh external confirmation |
| Saved-artifact consistency/provenance checked | Hashes, row IDs, group memberships, budgets, checkpoints, selected epochs and stated execution status agree | Proof that every producing code path executed exactly as reported or every physical group is independent |
| Retained historical execution evidence | Reports/receipts document prior decode, gradients, recovery and throughput checks | Those operations were rerun in Stage 5 |
| Unperformed / unresolved | Required data/source/evaluation or experiment is absent | A zero accuracy result, negative transfer, equivalence or universal methodological failure |

## 2. Why MSM was selected and what preceded implementation

MSM provides a second industrial process and native cutting-interval annotations, laboratory process video/audio and numerical machine signals. That made it a plausible test of whether modular visual/sensor interfaces can be adapted beyond robotic assembly. Selection was based on those testable data properties, not known MSM outer-test superiority. It is an independent dataset, not automatically an independent *evaluation* or robustness test. This distinction follows the actual staged work, rather than retrospectively describing every failed prerequisite as a planned contribution.

Stage 1 resolved the exact official handle and pinned version, inspected 481 listed files totaling 40,412,136,430 bytes, verified the 37/19/13 machine-folder counts and acquired all 69 labels. Native annotations yield **2,575 candidate cuts**, labels **0=1,933; 1=465; 2=177**, with label 1 in 30 nominal folders. Duration min/median/max: **0.533 / 3.008 / 408.529 s**. Candidate labeled cuts are not all paired visual examples. Stage 5 independently reproduced the native totals and checked all **104 acquired source files** against their hashes.

Stage 2 selectively acquired 35 pilot modality/metadata files (about 1.196 GB), not the 40.4 GB archive. It verified actual schemas, audio/video durations, non-square video pixels, label-blind acoustic alignment, native frame identities, sensor coverage and camera visibility. Its final **114 common-MTC examples** have native counts **93/10/11**. The separate 39-example raw-ACC contract overlaps the MTC cohort and must not be added to it. VF10 industry has no video.

The exploratory VMX30Ui/dataset9 offset near +16.04 s was rejected after an inappropriate whole-record overlap rule excluded the correct offset. Corrected calibration/held-out acoustic evidence fixes **+49.73 s ±0.10 s**. Exploratory counts/frames were superseded by the validated Stage 2 revision. Stage 5 checked the corrected saved-PTS/guard and native-annotation association, **not** new acoustic fitting or video decoding. Coolant often hides the actual interface; accepted frames show milling context, not necessarily visible anomaly/tool damage.

Stage 3 reviewed those constraints before adapting the verified model primitives. Its bounded smoke checked forward/gradient paths, prediction units, OOF group provenance and checkpoint serialization. Current audit independently reconstructed all MTC statistics: maximum absolute difference **{msm['independent_raw_MTC_statistics_max_abs_difference']:.8g}** in native feature units, within the declared numerical tolerance. That arithmetic agreement does not resolve unknown MTC aggregation-window latency.

## 3. Architecture portability versus learned-weight transfer

Reused: existing REASSEMBLE local pretrained **R18vd ResNet CNN** (11,190,112 parameters), spatial mean pooling of the final three maps to 896 values, temporal mean over 16 frames, the existing 128-unit head constructor/standardizer and the static two-probability stacking pattern. The detector, hybrid encoder/Transformer and learned temporal attention are not executed in the retained core. Calling the reused CNN a visual Transformer would be inaccurate.

MSM-specific work: immutable native interval/label adapter, corrected frame/clock selection, SAR-preserving 640×640 letterboxing, MTC loading/coverage, six statistics over 15 configured numerical channels, stable-cutting label mapping and experiment groups. REASSEMBLE's robot sensor identities, 512-position sequence and 220-statistic vector were not imposed on MSM. Group/timestamp/tool/remark/label-sheet metadata does not enter the predictor arrays.

Components requiring new fitting: visual classifier **896→128→1**, sensor logistic classifier and scalers, and **three-parameter static F2** from group-held-out branch probabilities. The Stage 3 development smoke fitted these components for its small plumbing test; **full held-experiment fitting never ran**. No REASSEMBLE failure-classification head, source-domain scaler, calibrator or F2 coefficient was reused. Original pretrained CNN reuse across tasks is distinct from transferring CNN weights learned on REASSEMBLE.

Stage 4's R condition required a completed, validation-selected full-backbone Phase 1 C checkpoint. No such admissible source existed then; at this audit there are **{protocols['current_completed_C_fits']} completed C fits**, and the fixed canonical R role's completion receipt exists: **{protocols['canonical_R_completion_receipt_exists_now']}**. One completed B fit only trains a head while keeping the original CNN frozen. Active C files and full-CNN preflight weights cannot substitute for a completed source model.

Stage 4 found all **115 diagnostic CNN tensors structurally compatible**, excluding the four source head tensors and `mean/std`. Normalization affine values retain state-dict names despite source Parameter promotion, so they can map into the frozen target's buffers. This is serialization compatibility. Diagnostic tensors were never used as R on MSM, and Stage 5 only checks that saved compatibility/provenance evidence and unchanged file identities. **Learned-weight transfer success or failure is unmeasured.**

## 4. Tasks and class prevalence are different

| Property | REASSEMBLE primary study | MSM |
| --- | --- | --- |
| Prediction unit | Completed high-level action segment | Completed annotated cutting interval |
| Native positive | `failure = 1 - success`, four assembly action types | Native label 1: abnormal cutting warranting intervention |
| Other native classes | Success | Label 0 stable normal; label 2 defective tool during stable cutting |
| Retained binary target | Failure vs success | Label 1 vs stable cutting labels 0/2; exclude-2 sensitivity declared separately |
| Counts / prevalence | 509/4,530 = **{100*prevalence_reassemble:.4f}%** failure; 148 recordings | Full labels: 465/2,575 = **{100*465/2575:.4f}%**; eligible pilot: 10/114 = **{100*prevalence_msm:.4f}%**, five folders |
| Actual learning-test status | Saved recording-disjoint held-out predictions exist; repeatedly exposed exploratory sequence | Only a 24-example development smoke; zero held-out Stage 4 predictions |
| Main limits | Recording grouping is not independent session/site/object evidence; full action boundaries known | Only two positive folders, unclear physical dependencies, coarse visual/MTC timing contract |

The smoke deliberately used ten positives in 24 samples (41.67%); it is not an estimate of deployment prevalence. The 103-example exclude-label-2 sensitivity still has only two positive groups and cannot rescue evaluation. AUROC/AP from different tasks are not a cross-domain ranking; AP also depends on prevalence and cohort composition. Neither offline complete-segment task demonstrates prospective early warning. Label 2 is not silently recoded as abnormal.

## 5. Verified REASSEMBLE discrimination and fusion evidence

Stage 5 independently recalculated **{audit['metric_values_recalculated']} saved point metric values**, including core folds/seeds, named corruption conditions, temporal/encoder/controlled-32 and later sensor/anchored comparisons; maximum absolute difference **{audit['maximum_metric_absolute_error']:.3g}**. Audit table: `manifests/metric_recalculation_checks.csv`. This is fixed-prediction reproducibility, not retraining.

| Core model | AP | AUROC | Interpretation |
| --- | ---: | ---: | --- |
| Sensor statistics | 0.429392 | 0.779325 | Strongest tested original unimodal sensor reference |
| Frozen CNN | 0.230658 | 0.697795 | Standalone prediction weaker; incremental complementary information possible |
| Short PatchTST | 0.241591 | 0.705351 | Does not beat statistics at its tested budget |
| Static F2 | 0.447299 | 0.794968 | Bounded improvement over original sensor reference |

Reconstructed 2,000 paired recording-cluster draws give **F2 minus sensor AP +{paired['AUPRC']['estimate']:.6f} [{paired['AUPRC']['lower_95']:.6f}, {paired['AUPRC']['upper_95']:.6f}]**, AUROC **+{paired['AUROC']['estimate']:.6f} [{paired['AUROC']['lower_95']:.6f}, {paired['AUROC']['upper_95']:.6f}]**. Brier improves by **{paired['Brier']['estimate']:.6f} [{paired['Brier']['lower_95']:.6f}, {paired['Brier']['upper_95']:.6f}]**. Exact saved F2 coefficient arithmetic reproduces with maximum error **0.0**. Source {r2}; recalculation `manifests/REASSEMBLE_core_audit.json`.

The branches are unchanged when static F2 is added; this is fusion complementarity, not an improved CNN. Core F2 is reused exactly in later core sections, so repeated appearances of AP 0.447299 are **not independent replications**. Original F4/F5/F6 do not meet their clean incremental-AP/AUROC criteria. That bounded result is not universal adaptive-fusion failure.

Later results prevent blanket summaries: longer PatchTST reaches **0.285311 AP**, improving its matched short reference **0.255658**, but still below statistics; same-sensor hybrid AP **0.440347** is not image/sensor fusion. Separately anchored clean adaptation reaches **0.468312 AP** versus A0 **0.447299**; saved ΔAP interval **[0.0015,0.0419]** supports that bounded clean comparison, while its AUROC gain remains unresolved. Those later point metrics were recalculated; their historical contrast intervals were read and identified, not regenerated here. They use different selection/threshold rules and cannot be merged into a new best-model tournament.

## 6. Visual improvement is not automatically fusion improvement

The controlled 32-frame follow-up used matching two-epoch action budgets per recipe, two fixed seeds and identical sensor scores. New calculation from its saved assessment tables:

| Seed | Visual AP, frozen → final-stage tuned | F2 AP, frozen → final-stage tuned |
| --- | --- | --- |
| 42 | 0.222708 → 0.230609 | 0.439363 → 0.438566 |
| 20261023 | 0.216799 → 0.200517 | 0.435202 → 0.432380 |

At seed 42, the visual point gain coexists with a lower F2 point score; at the second seed visual improvement itself disappears. Saved F2-difference intervals span zero for both seeds. No causal explanation or equivalence is established. All **100 fit receipts/checkpoint hashes** match their index and all report two epochs; 25 fits were reused rather than independently repeated. Equal action/epoch budgets do not imply equal compute. Source {e8}.

There is also a different positive exploratory representation result: last-quarter pooling increases visual AP **0.230658→0.319146**, and its newly fitted F2 reaches **0.493437**. This retains pretrained CNN weights, changes retrospective temporal aggregation, and selects on repeatedly studied data under a single base-seed policy. It is not evidence of full-CNN learned-weight transfer or three-seed robustness, nor a reason to silently replace MSM's fixed whole-cut frame policy. The frozen hybrid-encoder comparison is a separate negative: visual AP **0.221644→0.171915**, fused AP **0.440764→0.424979**, with a shared sensor reference. Different head widths/costs prevent an attention-only causal conclusion.

## 7. Robustness evidence stays domain- and protocol-specific

All point metrics across the original **22 REASSEMBLE clean/fault conditions** were recalculated from saved predictions. Original F5/F6 have **0/12** joint adaptation/smaller-degradation criterion successes at the highest tested family severities. This does not erase condition-specific results or prove every adaptive method fails. Complete absence uses an explicit surviving-branch policy; mask-enforced weight changes are not learned reliability or recovered information. Source {r4}.

The later augmentation-matched quality-interaction pilot has **34 hash-verified tables**, **196 AP values** exactly reproduced and **70,029 probabilities** reconstructed from saved coefficients (maximum error **{quality['probability_max_error']:.3g}**). Its exact original multinomial draws reproduce mean AP C−A **+{quality['primary_mean_AP_difference']:.6f}**, 95% **[{quality['primary_95_interval'][0]:.6f}, {quality['primary_95_interval'][1]:.6f}]**. It remains inconclusive on one exposed fold/26 recordings; clean noninferiority is not demonstrated. Source {rq}.

**MSM has no corrupted/missing-modality evaluation, no adaptive-gate evaluation and no learned-weight transfer result. Merely being an independent dataset answers none of those robustness questions.** Acoustic timing validation is also not a test of model robustness to cross-modal misalignment. Synthetic REASSEMBLE faults do not establish field-failure distributions or MSM resilience.

## 8. Grouping, leakage, budgets and selected epochs

Checked core REASSEMBLE cohort identities, five whole-recording outer folds, **20 inner partitions** and **80 sub-inner partitions** used for F2 branch selection/calibration exclusion. Saved predictions match cohort labels and group/fold assignments. This checks the declared group separation, not the original raw annotation binding or physical-session independence. F2 threshold cross-fitting conditions on an already-constructed branch OOF matrix; its internal threshold scores are not unbiased independent validation. That disclosed training-side dependence is not a newly demonstrated outer-test leak. Repeated adaptive use of the same outer outcomes also limits confirmatory claims.

MSM's five nominal folders collapse to three machine/reference-date clusters; only two positive clusters exist and physical tool/session identities remain unclear. Three outer tests cannot each contain positives from two positive folders. Holding one positive folder out leaves one positive training folder, insufficient for two-fold group-held-out F2 construction. Both laboratory machine-held-out directions fail that same inner support check. Industry cannot supply a matched visual cohort. No fallback split or sensor-only substitution was executed.

| Study | Budget / seeds / selection verified or source-inspected |
| --- | --- |
| REASSEMBLE core CNN | Epoch candidates 5/10; selected outer epochs **5,5,10,10,5**; original base seed 20260927 with recorded fold/refit offsets, not a three-seed stability experiment |
| Core PatchTST / statistics | Epoch candidates 3/6; selected **6,6,6,6,6**; sensor C grid 0.1/1/10 selects **1,0.1,10,0.1,0.1** |
| Core fusion/gates | Seeds **20260927,20260928,20260929**; declared finite inner-selected head grids; seed metrics checked; static F2 has no neural epoch budget |
| Controlled 32-frame follow-up | Exactly **two epochs**, both recipes, seeds **42,20261023**; 100 indexed receipts/weights checked; not full-backbone Phase 1 |
| Full-backbone Phase 1 | Fixed seeds **42,123,20261023**, 25–50 epochs with training-side validation selection. At audit only completed B seed42/job0: **25 executed, epoch9 selected**. No final C source available; active values are not final selections |
| MSM frozen protocol | Ten fixed head epochs, no search/early stopping, seeds **42,123,20261023**; three outer/two inner intended, never admitted |
| MSM actual Stage 3 smoke | Root seed42; two epochs per development fit, six pipeline head updates plus four CPU/CUDA head-check updates = **10 total**; **528 CNN frame forwards**. Not the intended seed/fold matrix |
| MSM Stage 4 / Stage 5 | **Zero fitted models or optimizer updates**; missing results are explicit, not silently omitted |

## 9. Independent reproduction limits and unsuccessful work

The audit reproduced *from native files* the MSM annotation and statistical-feature calculations. From *saved predictions* it reproduced metric arithmetic, fold/seed values, exact F2/quality-head formulas and two selected conditional cluster intervals. It checked original pretrained identities, completed Phase 1 and controlled-study checkpoint hashes and MSM development checkpoint structure/scaler IDs; independent NumPy forward arithmetic yields finite probabilities, without scoring the development labels.

It did **not** rerun raw CNN/video extraction, acoustic offset fitting, model training, historical optimizer/gradient/recovery events, raw corruption generation, physical-label adjudication, all historical bootstrap intervals or the raw REASSEMBLE target join. In particular, Stage 3's historical save/reload zero-error check is retained execution evidence: the original final-refit probability array was not preserved, so its historical execution comparison cannot be independently replayed from that array. Current saved-checkpoint arithmetic is a narrower check. No new training is essential to the bounded conclusions above, and none was requested or performed.

Retain negative/inconclusive findings: original unimodal gate conditional; tested short/long PatchTST below statistics; hybrid visual encoder loss; original clean scalar gates not qualifying; original synthetic mechanism criterion not met; quality-pilot broad interval; initial fine-tuning budget confound and mixed matched-budget seed effects; rejected MSM exploratory alignment; Stage 4 cohort/source block. A blocked experiment is **not** a failed model-accuracy or negative-transfer result. Non-significance is not equivalence.

The {old} is preserved because its first quality-bootstrap replay used the same bootstrap law but a different RNG method (`integers` rather than the original `multinomial`). The guard correctly rejected deterministic parity. The validated run restores the original draw sequence, SHA-256 **{quality['bootstrap_draw_counts_sha256']}**. No historical evidence, target, fitted model or conclusion was changed to obtain agreement.

## 10. Mapping to the four original exposé subquestions

The original main question centers architecture design/evaluation. SQ1 asks about suitable lightweight/pretrained representations; SQ2 compares unimodal, concatenation, late and process-aware gated fusion; SQ3 asks about missing/degraded/unreliable modalities; SQ4 asks about evaluation beyond accuracy. The original PDF's wording, original welding case study and later task/domain changes should be stated explicitly; no final-title approval is inferred from this audit.

{matrix}

## 11. Thesis disposition

Use REASSEMBLE for the protocol-labeled representation/fusion and bounded synthetic robustness results. Include MSM as an external feasibility/portability and evaluation-boundary case, with official provenance, corrected alignment, native labels, actual cohort size, new adapters and explicit blocked Stage 4. Do not place fabricated MSM AP values in a comparative accuracy table or title MSM as successful external validation/weight transfer.

The companion contribution, limitations and presentation reports provide admissible wording. Sources and audit inputs are hashed in `manifests/input_manifest.json`; reproducibility scope is in `validation.json`. Raw data, original reports/checkpoints and active training remain unchanged. No novelty, universal superiority, out-of-domain predictive generalization or deployment-robustness conclusion follows beyond the named evidence.
""")

    report("MSM_THESIS_CONTRIBUTIONS.md", f"""
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

The {ex} organizes architecture design/evaluation through SQ1–SQ4. MSM adds practical evidence about eligibility, clocks, modality schema and grouped support. It does not replace the main question with an external-validation or robustness hypothesis.

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
""")

    report("MSM_LIMITATIONS_AND_OPEN_QUESTIONS.md", f"""
# MSM limitations and open questions

**The current evidence cannot support an external predictive validation or learned-weight-transfer claim.** This is a boundary on inference, not evidence that the architecture cannot learn milling. Full quantitative checks and source links are in `MSM_FINAL_EVIDENCE_REVIEW.md`.

## 1. Material limitations and their effect

| Limitation | Verified evidence / scope | Consequence |
| --- | --- | --- |
| Positive experiment support | 114 paired examples, ten positives in two nominal folders; removing label2 still leaves two positive folders | Frozen three-outer/two-inner validation cannot run. Intervals/seeds cannot substitute for independent positive groups |
| Physical independence unresolved | Five folders collapse to three machine/reference-date clusters, two positive clusters; tool/session identity incomplete | Folder-disjoint does not imply independent tools, days, scenes or physical experiments |
| Native task semantics | REASSEMBLE failure is completed-action outcome; MSM label1 is intervention-worthy cutting abnormality; label2 is stable defective-tool operation | No unified physical “damage/failure” target or direct cross-task score ranking |
| Prevalence and selection | REASSEMBLE 11.2362%; full MSM annotations 18.0583%; eligible MSM 8.7719%; selected smoke 41.6667% | AP/precision/calibration and difficulty are not directly comparable; smoke is not a prevalence estimate |
| Visual visibility | Accepted frames show spindle/workpiece/milling context, often with coolant/window occlusion | Data construction does not show that the abnormality itself is visually observable |
| Smartphone timing | Corrected acoustic mapping and empirical support/bounds; no external optical fiducial; original transcode history incompletely observable | Strong shared-audio evidence is not proof of zero systematic AV/annotation error or robustness to alignment shifts |
| MTC aggregation | Row-level coverage passes, but values are held/pre-aggregated with unknown internal windows/latency | Statistics represent coarse controller context, not guaranteed fresh high-rate within-cut measurements |
| Contract heterogeneity | Common-MTC and raw-ACC cohorts differ; only 39 separate paired ACC examples, overlapping MTC | Do not add cohort counts or concatenate differing feature contracts without a new declared design |
| Industry lacks video | All 13 industrial folders have no listed video; CT/MTC schema and material/machine conditions differ | An industrial sensor-only experiment cannot establish generalization of the visual-plus-sensor architecture |
| Source R unavailable | No completed canonical full-backbone Phase 1 C checkpoint; preflight/active/B-head files are inadmissible | No conclusion that learned REASSEMBLE CNN initialization helps, hurts or transfers |
| Development exposure | Same REASSEMBLE cohort supports many follow-ups; some fits/branches/predictions reused | Later comparisons remain exploratory; repetition of the same F2 score is not independent confirmation |
| Unequal/limited budgets | Initial fine-tuning recipes had five frozen vs two tuned epochs; matched follow-up has only two epochs/two seeds | Initial attribution is confounded; later recipe is bounded, not converged/universal or a source-seed distribution |
| Gate mechanism differences | Core scalar-logit convex gates, static-anchored adaptation and quality interactions are distinct models/objectives | Do not merge their claims. Weight changes/quality terms are not causal reliability explanations |
| Missing robustness trials on MSM | No corruption, missing-modality, misalignment or adaptive-gate comparison | Independent dataset status provides no adaptive-robustness evidence |
| Cost evidence | Stage 3 short shared-T4 loading benchmark, startup effects; Stage 4 zero training; Stage 5 CPU arithmetic only | No full-MSM training cost, sustained GPU utilization or production-latency certification |

The VM20i source XML's `S_Axis_Load` type/units inconsistency remains flagged and uncorrected; source numerical identity is preserved, but physical interpretation needs care. Labels and raw data have not been rewritten to improve coverage.

## 2. Leakage protections and residual qualification

Current audit verified REASSEMBLE whole-recording fold separation (5 outer, 20 inner, 80 sub-inner), saved label/fold identity and F2 coefficient replay. It does not prove the raw labels or physical-session independence. Core F2 threshold cross-fitting uses a prebuilt global branch-OOF bank within outer training, so those internal threshold scores are dependent; no outer-test leakage was newly found, and no redesigned fitting procedure was silently substituted.

MSM excludes target-containing metadata from feature vectors: native labels, Tool/Workpiece, label-sheet process parameters, remarks, filenames, NC/program/outcome fields, timestamps, duration and IDs do not become ordinary predictors. Group/time metadata still governs alignment, quality control and partitioning. Measured speed/feed channels can encode operating-regime confounding despite being legitimate signals. Scalers/class weights/parameters must fit training partitions only.

Temporal averaging over 16 frames is order-insensitive pooling, not temporal attention. Complete annotated boundaries and late process information are legitimate for the retrospective task, but cannot be described as online warning before a failure/cut ends. Correct frame-label association is necessary, not sufficient, for transferable class information.

## 3. Reproduction and provenance limits

**Recalculated now:** native MSM labels/counts/durations and independent MTC formulas; saved REASSEMBLE point metrics/folds/seeds for the audited families; exact saved F2/quality-head arithmetic; core F2-minus-sensor and quality-pilot primary recording-bootstrap intervals. The quality-pilot draw hash exactly matches its source receipt. No new model fit was involved.

**Consistency checked now:** previous MSM output/input hashes, current checkpoint IDs/weight hashes, source/budget selections, Stage 4 empty prediction/curve tables, current development checkpoint ID/scaler/finite-output arithmetic, and completed Phase 1 receipts. These checks rely on preserved artifacts and are not full execution replay.

**Not independently reproduced now:** raw REASSEMBLE annotation-to-array binding, raw video/CNN extraction, phone/audio offset estimation, expert labels, corruption generation, historical optimizer/gradient/recovery traces, all reported intervals, complete training/evaluation or field behavior. The Stage 3 historical reload comparison lacks a saved original final-refit probability vector; its zero-error claim remains a retained execution receipt, supplemented by narrower current checkpoint-arithmetic checks.

The initial Stage 5 bootstrap replay failed because the audit used a different RNG call sequence. Its source/evidence remain preserved; the validated audit uses the original multinomial draw generator. This was an audit reproduction issue, not evidence of a historical model or interval defect. No source result was edited.

## 4. Unsuccessful and inconclusive experiments to retain

- Stage 2's exploratory periodic-lag alias was invalid and corrected before the validated cohort. Report the correction, not the superseded mapping/count as a competing model result.
- Original REASSEMBLE unimodal gates were conditional; engineered statistics outperform the tested short/long PatchTST, even though longer training helps the latter. This is a bounded representation result, not universal Transformer inferiority.
- Hybrid encoder visual/fused scores are lower in the fixed comparison; different widths/costs prevent attention-only causation.
- Original clean scalar gates do not meet their incremental criteria, and original high-severity joint mechanism/outcome successes are 0/12. A later clean anchored AP gain prevents universal “adaptive fusion never helps” wording.
- Quality-pilot primary difference **+0.003012 [-0.026711,0.032165]** is inconclusive; clean noninferiority remains unresolved.
- Matched 32-frame fine-tuning has opposite visual point directions across seeds and no resolved F2 gain. Earlier unequal budgets and prior exposure remain documented.
- MSM Stage 4 was **not admitted**, not a failed classifier. Its 54 blocked result slots contain no AP/AUROC values, zero prediction rows and zero selected models.

Non-significance does not show equivalence. A missing experiment does not show absence of signal. A model/head being trainable does not establish useful learning or generalization. A lower Brier score under one protocol does not establish calibrated deployment risk on another dataset.

## 5. Open questions and proportional future evidence

| Question | Evidence needed before answering | Present status |
| --- | --- | --- |
| Does the adapted architecture predict MSM abnormal cuts? | Larger alignment/visibility/sensor-audited cohort; defensible dependency groups; valid frozen nested folds; all models/metrics under identical roles | Unanswered |
| Do REASSEMBLE-learned CNN parameters help? | Completed provenance-verified canonical source; same frozen/fine-tuning rule for P/R; new head/scalers; matched frames/roles/budgets/seeds | Unanswered; structural compatibility only |
| Does F2 add value on MSM? | Separate complete P/R training-side group-OOF probabilities, new stackers and untouched outer predictions; paired group uncertainty | Unanswered |
| Is an effect stable? | Report all predeclared seeds/folds, enough genuinely independent positive groups; distinguish MSM fit-seed variation from source checkpoint variation | Unanswered on MSM; source data cannot be multiplied by seed count |
| Can video contact or high-rate sensors improve the evidence? | Expert visibility review, known aggregation/latency or a separately declared ACC contract; no automatic cohort mixing | Engineering possibility, not a measured benefit |
| Can adaptive quality help under realistic failure? | A separately frozen matched-augmentation/gate comparison with sufficient groups and named missing/degraded conditions, including clock shifts if claimed | No MSM evidence; REASSEMBLE remains bounded/exploratory |
| Is deployment feasible? | Prospective boundary/latency assumptions, cold/end-to-end resource measurements, calibration under actual prevalence, operational costs and external sessions | Not established |

None of these questions mandates inventing a new experiment or expanding the thesis without review. Stage 5 authorizes consolidation only; no new fitting, threshold tuning, raw feature extraction or robustness campaign was run. The current defensible thesis can transparently report partial answers and explicit external-validation limits.
""")

    report("MSM_SUPERVISOR_PRESENTATION_OUTLINE.md", f"""
# MSM supervisor presentation outline

Working title: **Multimodal architecture evidence: REASSEMBLE findings and MSM feasibility boundaries**. Suggested duration 12–15 minutes plus discussion. This is not approval of a final thesis title or a request to launch additional experiments.

## Slide 1 — Scientific verdict

**Message:** REASSEMBLE supplies bounded predictive/fusion evidence; MSM supplies audited input/software portability evidence. Learned-CNN transfer and independent MSM performance remain unestablished.

Show three status boxes: “REASSEMBLE fixed-prediction results verified”; “MSM 114 construction-valid intervals”; “MSM independent evaluation blocked.” Say explicitly that no Stage 5 training occurred.

## Slide 2 — The original four questions

Use the {ex}, pp.2–3. Preserve SQ1 representations; SQ2 unimodal/concatenation/late/gated comparison; SQ3 missing/degraded/unreliable modalities; SQ4 evaluation beyond accuracy. Explain the move from the original welding case study to actual dataset-specific tasks without changing the question hierarchy. MSM does not turn SQ3 into an external-dataset question.

## Slide 3 — Why MSM and what its labels mean

Show version-pinned official identity; 69 folders/2,575 native cutting intervals. Explain native0 stable normal, native1 abnormal cutting, native2 stable operation with a defective tool. Main MSM target is 1 versus 0/2. Contrast REASSEMBLE completed-action failure, 509/4,530 (11.24%), with the MSM eligible cohort, 10/114 (8.77%). Do not show cross-dataset AP rankings.

## Slide 4 — What was verified before implementation

Timeline: official inventory/labels → selective pilot acquisition → actual media/sensor inspection → label-blind alignment/visibility/coverage → fixed 16-frame contract. Use an existing validated frame-plus-sensor diagnostic from Stage 2. Explain the corrected VMX/dataset9 +49.73 s mapping and the rejected exploratory alias; correction is quality control, not a method novelty claim. Industry has no video.

## Slide 5 — Reused architecture and new MSM work

Diagram: 16 guarded frames → frozen R18vd **CNN** → 896 mean-pooled values → new 128-unit head. Corresponding native MTC cut → 90 statistics → new logistic classifier. Their probabilities → new OOF-trained F2. Highlight reusable code/pretrained CNN versus newly fitted heads/scalers/fusion; no source failure head or F2 coefficient transfers. RT-DETR's Transformer/detector is not executed.

## Slide 6 — What REASSEMBLE actually establishes

Table: statistics AP 0.429392; frozen CNN 0.230658; short PatchTST 0.241591; F2 0.447299. Main contrast F2−sensor **+0.017907 [0.008603,0.028284]**, recording-clustered and conditional on fitted models. Mention calibration improvement with Brier delta −0.002005. Repeated core F2 values are exact reuse, not independent replications. Later anchored clean adaptation is a separate positive result, not evidence every adaptive gate succeeds or fails.

## Slide 7 — Visual gains and fusion gains are distinct

Use the newly generated `figures/controlled32_visual_vs_fusion.png`, with two-epoch seed42/20261023 point effects, and cite {e8}. Seed42 visual AP increases about0.00790 while F2 drops about0.00080; the other seed has lower visual and F2 scores. Explain that this does not identify a causal mechanism. Contrast with exploratory boundary pooling, where both visual and fusion scores rise under a different representation/selection procedure. Neither is learned-CNN transfer to MSM.

## Slide 8 — Robustness: negative and inconclusive evidence

Original F5/F6 joint mechanism/outcome criteria: 0/12 highest-severity successes. Later quality-interaction pilot C−A **+0.003012 [-0.026711,0.032165]**; one fold/26 recordings and no clean noninferiority. Complete modality-loss fallback is a declared policy, not learned recovery. MSM corruption/missing/alignment-shift robustness is untested. Do not generalize synthetic faults to field reliability.

## Slide 9 — Why MSM has no independent accuracy result

Show the five experiment-label counts from Stage 4's cohort chart: only VM20i/d1 and VMX/d9 contain positives. Three outer tests cannot all contain positives; an outer holdout leaves inadequate inner positive support. Show current source status: no completed canonical Phase 1 C checkpoint. “115 compatible tensors” is structural evidence, not learned transfer. Report zero held-out prediction rows rather than assigning a zero AP.

## Slide 10 — What this audit independently reproduced

Assurance ladder: native 69-label/114-MTC recalculation → saved-prediction metrics/selected bootstrap intervals → hash/ID/provenance consistency → historical training receipts. Numbers: **1,654 metric values**, maximum discrepancy about1.1e-16; **196 pilot AP values**, **70,029 coefficient-replayed probabilities**; selected bootstrap draw hash reproduced. No training, raw CNN replay or expert label re-adjudication. A saved-stage result matching itself is not new external confirmation.

## Slide 11 — Four-question evidence matrix

Show the required five-column table from `MSM_FINAL_EVIDENCE_REVIEW.md`. Main messages: SQ1 partial representation coverage; SQ2 bounded fusion comparison with no universal winner; SQ3 partial synthetic investigation and no MSM adaptive evidence; SQ4 substantial traceability/evaluation practice with unresolved deployment/physical-independence limits.

## Slide 12 — Thesis contribution and boundary

Include the audited external feasibility case, modular adapters, native targets/clocks, explicit admission gates and honest missing results. Keep predictive contributions protocol-labeled under REASSEMBLE. Place full manifests, budgets/seeds/selected epochs, failure/correction history and evidence-level table in the appendix. Future cohort expansion/source completion are options requiring a separately considered scope, not unfinished claims to disguise.

Closing sentence: **“The software adapts; independent predictive and learned-weight transfer to milling have not yet been demonstrated.”**

## Likely questions and precise answers

| Supervisor question | Answer |
| --- | --- |
| Why select MSM if no evaluation followed? | Its native cutting intervals and laboratory video/sensors made an external test plausible. Only the actual audit established the restricted usable cohort and missing dependencies. No poor classifier score caused the stop. |
| Did REASSEMBLE-trained CNN weights transfer successfully? | No evaluated transfer exists. The original pretrained CNN was reused; diagnostic serialization is compatible; the required completed learned source is missing. |
| Does F2 help? | Yes, under the retained REASSEMBLE core comparison and its stated conditional interval. On MSM it remains unmeasured. |
| Why not random-split cuts or use two folds? | They would change the frozen design and fail to create independent positive groups for the nested F2 procedure. More intervals or seeds do not repair that. |
| Does the second dataset prove robustness? | No. It tests neither degradation nor missing-modality response, and its predictive evaluation has not run. |
| Was the whole research independently reproduced? | No. Native MSM calculations and saved-result arithmetic/selected intervals were recalculated; historical model fitting/raw CNN/corruption generation were not repeated. |
| Are there negative results? | Yes: several representations/gates do not improve their comparator, the quality pilot is inconclusive and controlled fine-tuning effects vary by seed. MSM Stage 4 is blocked, not a negative accuracy result. |
| What should be claimed as novel? | No algorithmic novelty is established by these checks. Frame contributions as systematic, reproducible engineering and bounded comparative evidence, without priority/superiority claims. |

Presentation sources: the four Stage 5 reports, `validation.json`, all audit manifests and the linked original results. All numerical rounding in slides must preserve the units, source protocol, prediction unit and uncertainty status.
""")

    # A descriptive research figure, not a new fitted result or an inferred CI.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    (run / "figures").mkdir()
    table = pd.DataFrame(extensions["controlled32"])
    delta_visual, delta_f2 = [], []
    for seed in (42, 20261023):
        for branch, values in (("visual", delta_visual), ("F2", delta_f2)):
            selected = table.loc[(table.seed == seed) & (table.branch == branch)].set_index("condition")
            values.append(selected.loc["finetuned32_two_epochs", "AP"] - selected.loc["frozen32_two_epochs", "AP"])
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x = np.arange(2)
    ax.bar(x - .18, delta_visual, .36, color="#4477aa", label="Visual AP change")
    ax.bar(x + .18, delta_f2, .36, color="#cc6677", label="F2 AP change")
    ax.axhline(0, color="black", linewidth=.8)
    ax.set_xticks(x, ["42", "20261023"])
    ax.set_xlabel("REASSEMBLE visual-training seed")
    ax.set_ylabel("AP: final-stage tuned minus frozen")
    ax.set_title("Matched two-epoch 32-frame study: visual and fusion effects differ")
    ax.legend()
    fig.text(.5, .015, "Descriptive saved-prediction point effects; no CI shown. Not MSM transfer results.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, 1))
    fig.savefig(run / "figures/controlled32_visual_vs_fusion.png", dpi=170)
    plt.close(fig)
    with (run / "manifests/SQ_comparison_matrix.md").open("x") as stream:
        stream.write(matrix + "\n")
    write(run / "manifests/review_scope.json", {"reports_written_UTC": datetime.now(timezone.utc).isoformat(),
        "training_performed": False, "predictions_recalculated_from_new_CNN": False,
        "source_report_writer_sha256": digest(__file__), "independent_vs_consistency_boundary_documented": True,
        "superseded_audit_attempt_preserved": c["prior_audit_attempt"]})
    for file in [Path(__file__), Path("MILLING DATASET/source/msm/evidence_audit.py")]:
        ast.parse(file.read_text(), filename=str(file))
    result = subprocess.run(["git", "diff", "--check"], text=True, capture_output=True)
    if result.returncode:
        raise ValueError("Whitespace check failed")
    write(run / "manifests/commands.json", {"commands": [
        f"OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.evidence_audit --config 'MILLING DATASET/configs/stage5_audit.json' --output '{run}'",
        f"PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B 'MILLING DATASET/source/write_stage5_reports.py' --run '{run}'"],
        "no_training_or_training_test_command": True})
    files = [*run.rglob("*"), Path(__file__), Path("MILLING DATASET/source/msm/evidence_audit.py"), Path("MILLING DATASET/configs/stage5_audit.json")]
    entries = [{"path": str(file), "bytes": file.stat().st_size, "sha256": digest(file),
                "git_ignored": subprocess.run(["git", "check-ignore", "-q", str(file)]).returncode == 0}
               for file in sorted(set(files)) if file.is_file()]
    write(run / "manifests/output_manifest.json", {"created_UTC": datetime.now(timezone.utc).isoformat(), "self_excluded": True, "files": entries})
    print(json.dumps({"reports": str(run), "audit_passed": True, "new_training": False}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
