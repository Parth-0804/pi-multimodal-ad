"""Consolidate measured within-dataset effects without cross-task score ranking."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

from external_eval.io import write_json,sha,utc
from external_eval.reports import table,text
from external_eval.publication import seal

ROOTS={'MSM':Path('MSM'),'HANDOVER':Path('HANDOVER/experiments/common_support_v2')}


def sentence_difference(pairs,comparison):
    g=pairs[pairs.comparison==comparison]
    if g.empty:return comparison+': unavailable under the scientific gate.'
    v=g.AP_difference.to_numpy(float);sign='positive' if np.all(v>0) else 'negative' if np.all(v<0) else 'mixed/zero'
    return f'{comparison}: mean AP difference {v.mean():+.6f}; three-seed range [{v.min():+.6f}, {v.max():+.6f}] ({sign} across seeds).'


def run():
    dest=Path('CROSS_DATASET_COMPARISON');tables=[];pair_tables=[];robust_tables=[];evidence={};interpretations=[]
    from external_eval.source_evidence import audit as source_audit
    reassemble=source_audit()
    final=dest/'FINAL_RESEARCH_SUMMARY.md'
    for dataset,root in ROOTS.items():
        receipt=Path(dataset)/'09_final_reports/REPORTS_COMPLETE.json'
        if not receipt.exists():raise ValueError('Dataset report not complete: '+dataset)
        evidence[dataset]=json.loads(receipt.read_text())
        for p,h in evidence[dataset]['hashes'].items():
            if sha(p)!=h:raise ValueError('Dataset report no longer matches completion receipt')
        primary='primary__group_id' if dataset=='MSM' else 'official'
        summary=pd.read_csv(root/'06_evaluation_results/metrics/clean_seed_summary.csv');summary=summary[summary.protocol==primary].copy();summary.insert(0,'dataset',dataset);tables.append(summary)
        pairs=pd.read_csv(root/'06_evaluation_results/metrics/paired_seed_differences.csv');pairs=pairs[pairs.protocol==primary].copy();pairs.insert(0,'dataset',dataset);pair_tables.append(pairs)
        robust=pd.read_csv(root/'07_robustness_experiments/robustness_metrics.csv');robust=robust[(robust.protocol==primary)&(robust.role=='test')].copy();robust.insert(0,'dataset',dataset);robust_tables.append(robust)
        for condition,g in pairs.groupby('initialization'):
            lines=[sentence_difference(g,c) for c in ['F2 minus visual','F2 minus sensor_logistic','F2 minus sensor_histgradient','F2 minus averaging','QG_aug minus F2_aug','averaging minus visual','averaging minus sensor_logistic']]
            interpretations.append(f'### {dataset}, {condition}\n\n'+'\n\n'.join(lines))
    combined=pd.concat(tables,ignore_index=True);combined.to_csv(dest/'comparison_tables.csv',index=False)
    pairs=pd.concat(pair_tables,ignore_index=True);pairs.to_csv(dest/'paired_comparison_tables.csv',index=False)
    robust=pd.concat(robust_tables,ignore_index=True)
    means=robust.groupby(['dataset','initialization','model','corruption'])[['AP','absolute_AP_degradation','relative_AP_degradation_percent']].mean().reset_index()
    means.to_csv(dest/'robustness_comparison_tables.csv',index=False)
    gate=json.loads((dest/'provenance/R_source_gate_final.json').read_text());R=gate['R_available']
    controller=json.loads((dest/'provenance/execution_finished.json').read_text());resolutions=[]
    for key,reason in controller['blockers'].items():
        if key=='MSM_P' and 'Owned feature job stopped before completion' in reason:
            marker=Path('MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json')
            complete=json.loads(marker.read_text())
            if not complete['all_predeclared_cases_complete']:raise ValueError('MSM operational race not resolved')
            resolutions.append({'historical_controller_blocker':key,'historical_reason':reason,'resolution':'Completed feature receipt was valid; fixed polling race and executed identical frozen MSM evaluator directly.',
                'actual_complete_matrix':str(marker),'complete_matrix_sha256':sha(marker),'completed_cases':len(complete['cases']),
                'protocol_or_model_settings_changed':False})
    write_json(dest/'provenance/OPERATIONAL_BLOCKER_RESOLUTIONS.json',{'resolutions':resolutions,'scientific_Handover_participant_gate_still_blocked':True,
        'original_controller_receipt_preserved':True})
    source_statement=('The exact completed canonical REASSEMBLE CNN source passed receipt/selection/checkpoint validation and R was evaluated under the same frozen-CNN rules. See the condition-paired tables for its measured benefit or harm.' if R else
        'The exact completed canonical REASSEMBLE source checkpoint remained unavailable. P-only external evaluations use the original generic pretrained CNN. **Transfer of weights learned on REASSEMBLE is unmeasured**, not a failed transfer result; an incomplete/other-fold source was never substituted.')
    architecture='''# Architecture comparison

| Component | MSM | Handover | Reuse versus adaptation |
| --- | --- | --- | --- |
| Prediction unit | One native cutting interval | One completed trial over common recorded support | New native annotation adapters; retrospective tasks |
| Input RGB |16 source-aligned native frames |16 source-clock bin-center native frames | Shared SAR-aware letterbox640, same frozen CNN |
| Visual representation |896 mean-pooled values |896 mean-pooled values | Actual RT-DETR-derived ResNet CNN only; no detector/transformer |
| Visual classifier |896→128→1, ReLU/dropout.1 |Same | Newly fitted domain heads and training-only standardizers |
| Numerical input |15 MTC channels×6stats=90 |6 wrench channels×6stats=36 | New physically meaningful domain adapters; no fabricated shared joints |
| Numerical classifier |Balanced L2 logistic C1 |Same | New coefficients/standardization; stronger HGB control fixed |
| Learned F2 |Unweighted L2 logistic on group-OOF [pv,ps] |BLOCKED: no participant mapping | Actual F2 semantics reused; no source fusion coefficient transfer |
| Nonlearned averaging |Evaluated |Evaluated | Same visual/logistic-sensor branches; no stacking fit |
| Quality fusion |QG_clean, QG_aug; matched F2_aug control |BLOCKED: no participant mapping | Actual DecisionGate reused with explicitly new quality context adapter |
| Main assessment |3 outer×2inner experiment-group folds |Official335train/101val/151test eligible | No label/metadata-derived grouping invented |

All three seeds42,123,20261023 use a fixed10-epoch AdamW visual head (lr.001,wd.001,batch32,clip1,FP32,finalepoch), training-only normalization and identical inputs/splits per model. Gates use40 fixed epochs and fixed augmentation exposure. The CNN is cached once per dataset/preprocessing/weight identity, not refitted per fold. The original REASSEMBLE raw-sequence sensor encoder is **not** claimed to have transferred unchanged: these are the verified statistics-based external adaptations.

Sixteen-frame averaging is permutation invariant. These experiments do not establish temporal-order modeling, object localization or a benefit over a one-frame ablation (not run). Crops and contact sheets are examination derivatives only. F2 is a model name, not F-beta=2 and not a quality-aware gate.
'''
    text(dest/'ARCHITECTURE_COMPARISON.md',architecture+'\n'+source_statement+'\n')
    performance=f'''# Measured performance comparison

Compare paired effects **within each dataset**, not raw AP between tasks. MSM has336/1895 positives (17.73%); Handover's official test has110/151 failures (72.85%). Completed-trial failure and short stable/abnormal cutting are different targets, horizons, cameras and physical systems. High failure prevalence alone raises the Handover AP baseline.

## Primary clean-data scores, every permitted model and all seeds

{table(combined)}
AP_seed_std/range are descriptive head-training variability, not independent-sample uncertainty. No best seed, fold or model is retroactively promoted as independently validated. Diagnostic direction-only results are explicitly separate from main models.

The prevalence predictor uses each outer-training partition's positive fraction. Its constants differ between MSM outer folds, so pooled cross-validation AP need not equal the overall test prevalence. The prevalence column is also the descriptive all-tied AP reference; test prevalence was never used to fit the baseline. Handover has one fixed training partition, so its constant baseline AP equals test prevalence.

{chr(10).join(interpretations)}

MSM paired cluster bootstrap includes nominal-folder and calendar-date-proxy95% intervals,2,000 common draws per paired comparison, averaging seeds without treating them as independent data. Only five calendar dates and unresolved tool/workpiece reuse limit inferential strength. Full interval tables are under MSM/06_evaluation_results/metrics/paired_group_bootstrap_95ci.csv. More positive per-seed deltas do not resolve a group-level interval spanning zero.

Handover has no participant IDs, so no participant CI or leakage-safe F2 estimate is fabricated. Its five official-split baselines provide publisher-partition held-out evidence with unverified participant identity independence. Validation results are separately reported and never chose epochs/thresholds. The binary labels are released outcomes, not observer-assigned camera labels.

MSM repeats the entire fixed model/seed pipeline under two stricter date groupings and label2 exclusion: all six protocols are retained, including weaker or inconsistent outcomes. Machine/direction/native-class and Handover robot/task subgroup tables are descriptive rather than newly selected confirmatory tests. No cross-machine retraining, industrial sensor-only substitution or zero-shot cross-domain classifier test is claimed.

{source_statement}
'''
    text(dest/'PERFORMANCE_COMPARISON.md',performance)
    # Include named high severity and missing conditions without hiding intermediate levels.
    focus=means[means.corruption.isin(['clean','gaussian_blur_3','brightness_contrast_3','partial_occlusion_3','frame_dropout_3','sensor_noise_3','channel_dropout_3','missing_sensor_channels_3','missing_visual','missing_sensor'])&~means.model.str.endswith('DIAGNOSTIC')]
    robustness=f'''# Robustness comparison

Every named severity was fixed before held-out corruption scores. Pixel-level blur/brightness/occlusion were actually passed through the frozen CNN; frame dropout pools the retained native frame embeddings exactly. Sensor noise uses only the respective fit partition's raw measurement SD and recomputed statistics. Explicit missing-channel imputation uses clean training means and a missingness mask. Native labels/groups and assessment identities never change.

## Clean, highest severity and missing-modality results (mean of all three seeds)

{table(focus)}
All intermediate severities, individual seeds and grouping/label sensitivities are retained in each dataset's robustness_metrics.csv and the complete cross-dataset CSV. A negative degradation means measured improvement under that named corruption, not a data correction.

Completely missing vision/sensors invokes the explicitly marked surviving-branch fallback. An unavailable unimodal model has no prediction or metric. Equal F2/gate/averaging fallback results are imposed behavior; they do **not** establish learned adaptive recovery. Compare corrupted vision fusion against the intact numerical branch, and corrupted sensor fusion against intact vision. Improvement over a degraded fused score alone is insufficient.

QG_aug was trained on fixed lowest-severity OOF views, while QG_clean was not. F2_aug is its exposure-matched static control. Higher severities remain assessment-only. See the paired clean-data tables and full degradation tables before attributing any gain to quality adaptation rather than augmentation. No Handover adaptive fusion was fitted without participant-safe OOF. These results are restricted to the named synthetic perturbations and native trace quality; no general hardware-fault or arbitrary-corruption robustness claim follows.
'''
    text(dest/'ROBUSTNESS_COMPARISON.md',robustness)
    msm_summary=combined[(combined.dataset=='MSM')&~combined.model.str.endswith('DIAGNOSTIC')]
    hand_summary=combined[combined.dataset=='HANDOVER']
    source_models=pd.DataFrame(reassemble['models'])
    sq=f'''## Original exposé subquestions

The original REASSEMBLE core saved predictions were rechecked here:4530 completed action examples,509 failures,148 recording groups, five outer folds, failure prevalence11.24%. Point metrics and F2 coefficient arithmetic reproduce; this is saved-result consistency, **not** a new raw-data/model-training replication of REASSEMBLE. Earlier extended/fault findings remain separately protocol-labeled evidence in the preserved Stage5 review.

{table(source_models)}

| Research question | REASSEMBLE evidence | MSM evidence | Defensible conclusion | Remaining limitation |
| --- | --- | --- | --- | --- |
| SQ1: Representations | Core frozen CNN, statistics and short PatchTST saved scores reproduce; statistical sensor reference is stronger than those two core alternatives | Real16-frame CNN plus90 statistics on1895 intervals, all three seeds and group sensitivities | Representations can be ported and compared after fitting new domain heads; see measured within-task differences above | CNN is the ResNet part of RT-DETR, not its Transformer; generic pretraining differs from REASSEMBLE-learned transfer; no new audio/AST result |
| SQ2: Fusion strategies | Core F2 AP0.447299 versus sensor0.429392; saved coefficient replay exact | Actual clean group-OOF F2, averaging, quality adapters and matched augmentation control evaluated | The above seed-paired deltas establish the bounded external fusion result, including negative outcomes; improved vision and improved fusion are distinct | Different targets/budgets and repeated source-cohort development prevent a universal model ranking; Handover learned fusion is blocked |
| SQ3: Robustness | Previous saved-result audit records bounded and unsuccessful adaptive comparisons; no original source corruption was regenerated here | Named real-pixel and actual-sensor perturbations, fixed severities, quality gates and exposure-matched static controls | Only measured named-condition changes and comparisons with unimodal/fallback controls support robustness statements | Independent data alone is not adaptive robustness; missing-branch fallback is imposed; no arbitrary real fault or time-shift robustness |
| SQ4: Evaluation | Five recording-disjoint folds and saved metric/label/coefficient identities checked; not raw annotation rebinding | Raw/native label/alignment reproduction, exact frames/statistics, three grouped policies, OOF provenance, prediction-metric audit and cost records | Traceable evaluation and explicit blocked/negative results are a substantive research-software contribution | Folders/dates do not prove physical tool/session independence; participant identities are unavailable; retrospective tasks are not early warning |

Handover extends the adapter/input comparison to587 RGB/wrench examples and the unchanged151-trial test set, but participant-OOF fusion is not inferred from archive membership. Its72.85% test failure prevalence and MSM's17.73% cut prevalence differ from REASSEMBLE's11.24% action prevalence; absolute AP cannot rank domain difficulty or establish superiority.
'''
    text(final,f'''# Final external-dataset research summary

**MSM: {evidence['MSM']['status']} for the complete permitted architecture evaluation. Handover: PARTIAL because participant-safe learned fusion cannot be certified.** All scientifically permitted P models, all three seeds and the fixed robustness matrix completed; no pilot metric is substituted. {source_statement}

## What the evidence establishes

The software architecture can be adapted to real manufacturing and human–robot interaction inputs using the same frozen16-frame CNN/head and dataset-specific physical sensor statistics. MSM supports the actual leakage-safe F2 composition at the nominal experiment-group level, with stricter date-proxy sensitivities. Handover supports real aligned RGB/wrench baselines on the unchanged official test split; full learned-fusion portability there remains untested because a required grouping field is absent.

Predictive utility is measured by the following within-task scores and paired differences; software execution alone is not evidence of superiority.

### MSM primary comparison

{table(msm_summary)}

### Handover official-test comparison

{table(hand_summary)}

{chr(10).join(interpretations)}

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

{sq}
''')
    text(dest/'REVIEW_HANDOFF.md','''# Researcher review handoff

Start with [FINAL_RESEARCH_SUMMARY.md](FINAL_RESEARCH_SUMMARY.md), then [PERFORMANCE_COMPARISON.md](PERFORMANCE_COMPARISON.md), [ROBUSTNESS_COMPARISON.md](ROBUSTNESS_COMPARISON.md) and [ARCHITECTURE_COMPARISON.md](ARCHITECTURE_COMPARISON.md). Machine-readable comparison_tables.csv contains every primary model/initialization; paired_comparison_tables.csv retains each seed difference.

MSM/09_final_reports and HANDOVER/09_final_reports contain the eight requested reports. Handover's active scientific outputs are versioned under HANDOVER/experiments/common_support_v2; earlier audit versions are preserved. Each dataset's08_visual_examples_and_eda/prediction_examples/index.html provides real16-frame full/context views and synchronized sensor plots, original labels and held-out probabilities. The Handover canonical stage folders include explicit active references.

Review physical grouping, participant identity absence, direction support, source checkpoint gate and the distinction between matched augmentation, quality gating and deterministic missing-modality fallback before making thesis claims. The protocol is frozen; no assessment-dependent tuning or preferred-seed selection was performed. No additional unbounded experiment expansion is needed for this handoff.
''')
    seal()
    print('FINAL DATASET STATUS',json.dumps({d:evidence[d]['status'] for d in evidence}),flush=True)
    print(combined.to_string(index=False),flush=True)
    print('DELIVERY COMPLETE',str(final),flush=True)


if __name__=='__main__':run()
