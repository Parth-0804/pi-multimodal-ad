# Final external-dataset research summary

**MSM: PASS for the complete permitted architecture evaluation. Handover: PARTIAL because participant-safe learned fusion cannot be certified.** All scientifically permitted P models, all three seeds and the fixed robustness matrix completed; no pilot metric is substituted. The exact completed canonical REASSEMBLE source checkpoint remained unavailable. P-only external evaluations use the original generic pretrained CNN. **Transfer of weights learned on REASSEMBLE is unmeasured**, not a failed transfer result; an incomplete/other-fold source was never substituted.

## What the evidence establishes

The software architecture can be adapted to real manufacturing and human–robot interaction inputs using the same frozen16-frame CNN/head and dataset-specific physical sensor statistics. MSM supports the actual leakage-safe F2 composition at the nominal experiment-group level, with stricter date-proxy sensitivities. Handover supports real aligned RGB/wrench baselines on the unchanged official test split; full learned-fusion portability there remains untested because a required grouping field is absent.

Predictive utility is measured by the following within-task scores and paired differences; software execution alone is not evidence of superiority.

### MSM primary comparison

| dataset | initialization | protocol | model | AP_mean | AP_seed_std | AP_min | AP_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MSM | P | primary__group_id | F2 | 0.756879 | 0.011082 | 0.746617 | 0.768630 |
| MSM | P | primary__group_id | F2_aug | 0.760170 | 0.009783 | 0.752758 | 0.771258 |
| MSM | P | primary__group_id | QG_aug | 0.826521 | 0.016168 | 0.813794 | 0.844713 |
| MSM | P | primary__group_id | QG_clean | 0.837418 | 0.013389 | 0.823898 | 0.850673 |
| MSM | P | primary__group_id | averaging | 0.735594 | 0.015942 | 0.721772 | 0.753034 |
| MSM | P | primary__group_id | prevalence | 0.145395 | 0.000000 | 0.145395 | 0.145395 |
| MSM | P | primary__group_id | sensor_histgradient | 0.901299 | 0.000000 | 0.901299 | 0.901299 |
| MSM | P | primary__group_id | sensor_logistic | 0.828616 | 0.000000 | 0.828616 | 0.828616 |
| MSM | P | primary__group_id | visual | 0.298901 | 0.010853 | 0.286490 | 0.306606 |


### Handover official-test comparison

| dataset | initialization | protocol | model | AP_mean | AP_seed_std | AP_min | AP_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HANDOVER | P | official | averaging | 0.803102 | 0.013458 | 0.794653 | 0.818621 |
| HANDOVER | P | official | prevalence | 0.728477 | 0.000000 | 0.728477 | 0.728477 |
| HANDOVER | P | official | sensor_histgradient | 0.906319 | 0.000000 | 0.906319 | 0.906319 |
| HANDOVER | P | official | sensor_logistic | 0.823624 | 0.000000 | 0.823624 | 0.823624 |
| HANDOVER | P | official | visual | 0.771647 | 0.006411 | 0.767664 | 0.779042 |


### MSM, P

F2 minus visual: mean AP difference +0.457978; three-seed range [+0.440011, +0.482140] (positive across seeds).

F2 minus sensor_logistic: mean AP difference -0.071737; three-seed range [-0.081999, -0.059986] (negative across seeds).

F2 minus sensor_histgradient: mean AP difference -0.144421; three-seed range [-0.154682, -0.132670] (negative across seeds).

F2 minus averaging: mean AP difference +0.021285; three-seed range [-0.006416, +0.046858] (mixed/zero across seeds).

QG_aug minus F2_aug: mean AP difference +0.066351; three-seed range [+0.049797, +0.088221] (positive across seeds).

averaging minus visual: mean AP difference +0.436693; three-seed range [+0.428370, +0.446427] (positive across seeds).

averaging minus sensor_logistic: mean AP difference -0.093022; three-seed range [-0.106844, -0.075582] (negative across seeds).
### HANDOVER, P

F2 minus visual: unavailable under the scientific gate.

F2 minus sensor_logistic: unavailable under the scientific gate.

F2 minus sensor_histgradient: unavailable under the scientific gate.

F2 minus averaging: unavailable under the scientific gate.

QG_aug minus F2_aug: unavailable under the scientific gate.

averaging minus visual: mean AP difference +0.031455; three-seed range [+0.026418, +0.039579] (positive across seeds).

averaging minus sensor_logistic: mean AP difference -0.020522; three-seed range [-0.028971, -0.005003] (negative across seeds).

Three seed signs describe optimization stability. They do not prove physical-domain generalization; read the group-CI and stricter-split tables before interpreting a small effect. Failure to outperform the stronger sensor model is retained as a negative result even if fusion beats its own logistic-sensor component.

## Data and independence

MSM's native2512 intervals and labels1877/458/177 were independently reproduced. The1895 admitted intervals (1434/336/125) span45 nominal folders,17 positive folders,7 machine/date proxies and5 calendar dates. All six predefined three-outer/two-inner protocols passed class/group gates. Physical tool/workpiece/session independence is unresolved. Label2 is stable defective-tool cutting, a primary negative; the entire pipeline was repeated excluding it. IndustrialVF10 has no camera and was not presented as the same multimodal test.

Handover's589 released labels comprise156 successes and433 failures. Common-support gates retain587 (335training,101validation,151test); two training trials fail the unchanged timing-gap rule. Test has41success/110failure. Participant count17 is a publisher statement; participant identities are absent. Native trial IDs restart by split and were namespace-qualified, not treated as participants. Actual cross-split video-byte duplication is absent. The full-video-tail audit and pre-score common-support amendment are preserved, including its two subtype-count discrepancy with the datasheet and14 all-zero wrench traces.

MSM acoustic alignment is reused with explicit uncertainty, including corrected VMX9+49.73s. Handover sensor arrays exactly match author nearest-time resampling; camera source clocks, encoded PTS and common-support endpoints are distinct and preserved. Neither timing validity nor coolant-heavy imagery establishes that the label is visually identifiable. Full camera views, contextual crops,16-frame sequences, native labels, sensors and measured predictions are available for five negatives/five positives per dataset plus deterministic error examples.

Handover common support can omit unsupported tail evidence, including a potentially relevant action/outcome event. The target remains the released completed-trial outcome; action annotations never choose frames. This is retrospective classification from the shared recorded window, not a claim that every outcome event is visible or that full-video/online failure prediction was evaluated.

## Four separate claims

| Claim | Defensible interpretation | Limitation |
| --- | --- | --- |
| Architecture portability | Real native adapters and newly fitted domain heads work under the stated data contracts; MSM includes actual OOF F2 | Handover learned fusion blocked; original sequence-sensor branch replaced by the verified statistical adaptation |
| Learned-weight transfer | P uses a generic pretrained CNN; R only exists if the exact canonical source gate passed | MissingR cannot demonstrate benefit or harm of REASSEMBLE-learned weights |
| Predictive generalization | Within-dataset held-out group/publisher-split measurements and all seed effects are reported | Domain heads are retrained; unknown physical/participant IDs, high correlations and differing prevalence limit claims |
| Robustness | Named real-pixel/sensor corruptions, fixed severities and explicit fallback were measured | Missing-branch fallback is not adaptive learning; augmentation and gating effects require the matched static control |

## Reproduction, cost and review

One idempotent runner reproduces gates, compact CNN caches, training, OOF fusion, assessment, robustness and reports. Dataset-specific sources, original labels, inputs/hashes, split/config/checkpoint identities, all predictions and actual loss/runtime traces remain separate. Every saved fold metric was independently recalculated from prediction rows to1e-12. Actual CNN extraction and complete permitted fitting ran here; saved-result metric consistency is distinct from a separate stochastic retraining replication. A training-only exact CNN parity check, gradient/reload tests and synthetic outer-composition regressions passed.

The sharedT4 is used for frozen-CNN extraction, with about433MiB actual peak tensor allocation and a2GiB process cap. Small new heads/classifiers fit on CPU. Other active REASSEMBLE work was preserved; device-wide utilization is not attributed to this evaluation. Exact per-dataset extraction, fitting, inference and host-memory records are in06_evaluation_results/runtime_summary.json and the per-case training_and_runtime.json. Caches are shared across all seeds, folds and models within each weight identity.

Read the dataset EXPERIMENT_RESULTS, ROBUSTNESS_RESULTS, DATASET_VALIDATION, MODEL_IMPLEMENTATION and REPRODUCIBILITY reports, then inspect the real example galleries. All historical MSM stages and blocked findings remain intact. The completion receipt/source snapshot/output manifests under provenance permit an independent audit. No PHM/Intel data or active source experiment was modified, and nothing was staged or committed.

For the thesis: report the full paired within-dataset comparison, stronger-sensor control, date/label sensitivities, all seeds, confidence limits and unsuccessful experiments. Present Handover's missing-participant gate and unavailableR as explicit incomplete comparisons. Do not claim online warning, general adaptive robustness, industrial visual transfer, superiority across tasks or learned cross-domain representation transfer without the missing evidence.

## Original exposé subquestions

The original REASSEMBLE core saved predictions were rechecked here:4530 completed action examples,509 failures,148 recording groups, five outer folds, failure prevalence11.24%. Point metrics and F2 coefficient arithmetic reproduce; this is saved-result consistency, **not** a new raw-data/model-training replication of REASSEMBLE. Earlier extended/fault findings remain separately protocol-labeled evidence in the preserved Stage5 review.

| model | AP | AUROC |
| --- | --- | --- |
| sensor_statistics | 0.429392 | 0.779325 |
| rtdetr | 0.230658 | 0.697795 |
| patchtst | 0.241591 | 0.705351 |
| F2 | 0.447299 | 0.794968 |


| Research question | REASSEMBLE evidence | MSM evidence | Defensible conclusion | Remaining limitation |
| --- | --- | --- | --- | --- |
| SQ1: Representations | Core frozen CNN, statistics and short PatchTST saved scores reproduce; statistical sensor reference is stronger than those two core alternatives | Real16-frame CNN plus90 statistics on1895 intervals, all three seeds and group sensitivities | Representations can be ported and compared after fitting new domain heads; see measured within-task differences above | CNN is the ResNet part of RT-DETR, not its Transformer; generic pretraining differs from REASSEMBLE-learned transfer; no new audio/AST result |
| SQ2: Fusion strategies | Core F2 AP0.447299 versus sensor0.429392; saved coefficient replay exact | Actual clean group-OOF F2, averaging, quality adapters and matched augmentation control evaluated | The above seed-paired deltas establish the bounded external fusion result, including negative outcomes; improved vision and improved fusion are distinct | Different targets/budgets and repeated source-cohort development prevent a universal model ranking; Handover learned fusion is blocked |
| SQ3: Robustness | Previous saved-result audit records bounded and unsuccessful adaptive comparisons; no original source corruption was regenerated here | Named real-pixel and actual-sensor perturbations, fixed severities, quality gates and exposure-matched static controls | Only measured named-condition changes and comparisons with unimodal/fallback controls support robustness statements | Independent data alone is not adaptive robustness; missing-branch fallback is imposed; no arbitrary real fault or time-shift robustness |
| SQ4: Evaluation | Five recording-disjoint folds and saved metric/label/coefficient identities checked; not raw annotation rebinding | Raw/native label/alignment reproduction, exact frames/statistics, three grouped policies, OOF provenance, prediction-metric audit and cost records | Traceable evaluation and explicit blocked/negative results are a substantive research-software contribution | Folders/dates do not prove physical tool/session independence; participant identities are unavailable; retrospective tasks are not early warning |

Handover extends the adapter/input comparison to587 RGB/wrench examples and the unchanged151-trial test set, but participant-OOF fusion is not inferred from archive membership. Its72.85% test failure prevalence and MSM's17.73% cut prevalence differ from REASSEMBLE's11.24% action prevalence; absolute AP cannot rank domain difficulty or establish superiority.
