"""Human-readable editorial pass over generated report prose; preserve data tables."""
import re
from pathlib import Path
from audit_common import OUT,csv_write


def existing_tables(name):
    content=(OUT/name).read_text();return '\n\n'.join(re.findall(r'(?m)^\|.*(?:\n\|.*)*',content))


def replace_body(name,body):
    p=OUT/name;old=p.read_text();title=old.splitlines()[0]
    anchors=old.split('\n## Evidence anchors\n',1)
    p.write_text(title+'\n\nAudit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.\n\n'+body.strip()+'\n'+ ('\n## Evidence anchors\n'+anchors[1] if len(anchors)>1 else ''))


def polish_all():
    root='06_dataset_specific/'
    replace_body(root+'REASSEMBLE/MODEL_AND_CONFIGURATION_AUDIT.md',"""
The original primary cohort contains **4,530 actions, 509 native failures and 148 recordings**. Eligibility requires primary actions and complete video/sensors. Recording is the grouping unit. The original protocol uses five outer folds, four inner folds and additional nested branch-selection folds, with base seed20260927 and deterministic fit offsets. Nineteen within-recording/action label-shift controls are negative controls, not independent replications.

The original visual branch is frozen RT-DETR R18vd CNN only:16 uniform frames,896-dimensional mean representation,128-unit ReLU/dropout0.1 head. AdamW uses LR0.001,weight decay0.001,batch128 and gradient clipping1. The inner mean AP selects epoch5 or10. Static sensors supply220 statistics from22 channels; balanced logistic regression selects C0.1,1 or10. PatchTST uses22 channels and512 normalized-progress points with epoch3/6 selection. Each branch has its own training-side selection/calibration. F2 then fits a fixed-C1 probability logistic model using nested OOF predictions. Section2 feature concatenation/gates, temporal/anchored/sensor extensions, boundary variants and legacy final-stage/encoder probes are separately inventoried.

The approved C-only cap is **complete:25/25 fits**, representing **25/75 of the original plan**. All25 ran20 epochs, seed42, covering every outer fold with four inner fits plus one outer refit. Seeds123 and20261023 are deferred. The original cosine50 schedule prefix was retained through epoch20. No active primary training process was found at the audit's initial inspection. C20 F2 finalization has **NOT EXECUTED**; the audit did not fit it.

From the five saved C20 outer prediction banks, the audit recomputed pooled visual AP **0.312127025700** and AUROC **0.756385557356**, using4,530 unique native IDs. This is one-seed, five-outer-fold visual evidence. There is only one retained original long frozen-B receipt before the C-only revision, so a complete matched five-fold B20 comparison is unavailable.

The100-epoch pair is a separate fresh-initialization pilot at seed42, original fit3/job_index2,outer_fold_original0. Both models completed100 epochs; selected epochs are14 frozen and47 full CNN. Their753 assessment actions were already exposed in earlier work. The later static-sensor F2 follow-up is complete but remains a single-fold pilot with a920-row stacking bank, not a full nested100-epoch experiment. See the adjacent detailed reports.

For MSM/Handover transfer, the canonical C20 donor now has a completed receipt and matching selected-state hash, but the validator still requires at least25 executed epochs. No external R transfer training was executed. ViFailback has completed C100 donor feature extraction but no V3 classifier/fusion training, with a separate75-fit scheduling barrier. Feature-bank completion is not model-training completion.

The historical variants are exploratory. Boundary fusion variant choice used exposed outer AP, and later pilots reused the same outer assessment cohort. Correct within-fit separation therefore does not imply an untouched confirmatory research test. No final model is selected.
""")
    replace_body(root+'MSM/MODEL_AND_CONFIGURATION_AUDIT.md',"""
The primary MSM cohort has **1,895 eligible intervals,336 abnormal examples**, with45 nominal groups. Original labels remain recorded, including a separate sensitivity that excludes native label2. The target is the declared abnormal-cut mapping; run/stage numbers are not damage labels. Physical tool/workpiece/session identities are incomplete, and only five date proxies are available.

The protocol uses three outer folds and two inner folds, seeds42,123,20261023. Retain/exclude-label2 crossed with nominal/machine-date/calendar-date grouping produces six protocols and54 completed cases. There are594 fitted model records, including base branches and fusion/gates. The table below is the **mean across three seeds of pooled three-outer-fold AP**, matching the earlier reported results. It is not an unweighted mean of nine fold-level AP values. Seeds reuse the same assessment samples.

Visual training is fixed at10 epochs, batch32, AdamW LR0.001/weight decay0.001,clip1,FP32, frozen CNN plus114,945-parameter head. Sixteen temporal-bin-center RGB frames are letterboxed to640 with sample-aspect-ratio correction. Fifteen actual MTConnect numerical channels produce90 features (six statistics each). Sensor LR is balanced C1,lbfgs,max_iter2000,random_state0. HGB uses learning_rate0.1,max_iter100,max_leaf_nodes15,min_samples_leaf10,l2_regularization1,early_stoppingFalse with balanced sample weights.

Average and F2 use the **LR sensor branch**, not HGB. F2 is unweighted C1 logistic on OOF probabilities. Quality gates use36 quality features plus two availability indicators,hidden16,40 epochs,LR0.003,weight decay0.001,batch128,clip1. Augmented variants use fixed lowest-severity corruption views. These are predefined external recipes, not optimizer HPO.

Saved pooled results reconcile the previously reported AP values: visual0.298901,LR0.828616,HGB0.901299,average0.735594,F20.756879,F2aug0.760170,quality-clean0.837418,quality-aug0.826521. In contrast,mean-fold AP is0.345443 visual,0.837925 LR,0.888524 HGB and0.787849 F2. AP_AGGREGATION_RECONCILIATION.csv preserves both conventions by model. They are different estimands,not conflicting predictions. The pooled prevalence baseline AP0.145395 differs from cohort prevalence0.177309 because each fold uses its own training prior. Conditional paired group intervals use2,000 draws; they do not establish physical-tool independence.

Every completed case's recorded output hashes and clean held-out metrics were checked. All exported prediction rows, including every corruption and role, were joined to native IDs/labels, with disjoint assessment/training IDs. Complete results retain all folds/seeds, sensitivity protocols, corruptions, subgroups and recorded intervals. Nominal grouping and date proxies limit stronger independence claims.

R transfer remains NOT EXECUTED. The canonical donor now exists at20 epochs, but `validated_source` requires at least25. Neither donor nor validator was changed.
"""+'\n'+existing_tables(root+'MSM/MODEL_AND_CONFIGURATION_AUDIT.md'))
    replace_body(root+'HANDOVER/MODEL_AND_CONFIGURATION_AUDIT.md',"""
The native589 trials become **587 aligned examples** in `common_support_v2`:335 official training,101 validation and151 test. The test set contains110 failures and41 successes (failure prevalence0.728477). Two training trials were excluded for nearest wrench/video gaps above0.1 seconds. An earlier full-tail audit flagged92 test tails; the documented common observation-window amendment before fitting superseded that rule and retained all151 test trials. This preprocessing amendment must remain explicit.

The frozen visual head uses16 temporal-bin-center letterboxed RGB frames,10 epochs,AdamW LR0.001/weight decay0.001,batch32,clip1. Six wrench channels produce36 statistical features. LR is balanced C1,lbfgs,max_iter2000,random_state0; HGB uses0.1 learning rate,100 iterations,15 leaves,min_samples_leaf10,l2_regularization1,early_stoppingFalse with balanced sample weights. All three seeds42,123,20261023 completed the supported baselines. Average uses visual plus LR. Official validation rows are descriptive under the fixed recipe; they are not inner OOF predictions.

**F2,F2aug,quality-clean and quality-aug are NOT EXECUTED / BLOCKED.** Official documentation describes a participant-disjoint split, but available metadata and author code identify robot/task/trial rather than participants. The empty `participant_id` fields are preserved. Trial,robot,task or date identifiers cannot substitute for people. Certifiable participant-disjoint inner OOF is therefore unavailable. No fusion was fitted on official validation/test to bypass that limitation, and no participant bootstrap is defensible.

The final manifest preserves clock mappings, selected frames, native wrench indices, source hashes and original labels. HSR wrench is measured while Gen3 wrench is estimated;14 zero-channel traces were retained. These are limitations, not silently repaired data. Three seeds reuse the same151 test trials and do not supply independent participant evidence.

Mean held-out AP is0.771647 visual,0.823624 LR,0.906319 HGB,0.803102 average and0.728477 constant prior. Full per-seed, official-validation, test and robustness metrics remain in COMPLETE_RESULTS.csv. R transfer has not executed: the20-epoch canonical donor fails the validator's25-epoch minimum. Recovering participant groups requires official pseudonymous metadata, not inferred identities.
"""+'\n'+existing_tables(root+'HANDOVER/MODEL_AND_CONFIGURATION_AUDIT.md'))
    replace_body(root+'VIFAILBACK/MODEL_AND_CONFIGURATION_AUDIT.md',"""
The current final core contains **4,382 episodes:3,753 failures,629 successes,99 tasks**. Historical4,384/3,755 figures are superseded. Native totals are5,202 episodes (4,545 failures,657 successes). Camera QC passed13,150 of13,152 videos, followed by two episode exclusions. The sensor cache still contains4,384 rows; models correctly join the final4,382 episode IDs. Task55 quarantine and B02 uncertainty remain documented. Whole-episode outcome classification does not establish failure-time localization or early warning; physical-session independence and hardware-clock alignment are unverified.

Task-disjoint three-outer/three-inner splits use label-blind hash ordering. T/V/C/assessment task sets are disjoint, and each meta-OOF episode is absent from its base fitting, validation and calibration partitions. Seeds are42,123,20261023. Completed work comprises **72 frozen100-epoch heads** (36 three-camera V1,36 high-only),36 LR fits,108 HGB candidate fits across36 jobs, and nine V1 fusion jobs with F2/quality/neutral gates (27 models), totaling243 fitted classifier/candidate/gate records.

**V2 full-CNN training and V3 transfer-classifier training have not executed.** Both original V1 and C100-donor V3 feature banks are complete. A cached donor representation is not a trained transfer head or a transfer fusion result.

Frozen heads use896→128 ReLU/dropout0.1→1,114,945 trainable parameters,100 cosine epochs,batch8,LR0.001,weight decay0.001,clip1,FP32. Selection is the first strict maximum of validation macro AP, followed by separate C calibration. BEST_MODEL and FINAL_EPOCH100 are retained. Sensors are28 state/velocity/gripper-effort channels at25Hz with280 statistics; they are not force/torque channels. S1=S3 is one balanced C1 logistic method,random_state42,max_iter2000. HGB usesLR0.05,max_iter200,min_samples_leaf20,l2_regularization0.1,no early stop; validation macro AP selects leaves7/15/31,then C calibrates. F2 uses training-side OOF probabilities. Quality gates use11 quality plus two availability inputs,hidden16,40 epochs,LR0.001,weight decay0.001,batch64. The neutral gate zeros quality with the same trained capacity.

Every pooled row below uses the same4,382 episodes per seed. Failure prevalence0.856458 makes failure AP alone misleading: both classes and macro AP are reported. Saved sensor predictions are deterministic across seeds. F2 macro AP is below LR macro AP in all three seeds; no new confidence interval is manufactured.

The saved Oct30 PIPELINE_STATUS says WAITING_REASSEMBLE75_COMPLETE_AND_GPU_IDLE and names controller PID290646, which was dead at initial inspection. The source gate requires the75-fit completion marker plus final-metrics hash; the approved25-fit cap does not produce it. V2/V3 are blocked by that scheduling contract, not currently progressing. The audit did not change or restart the controller.
"""+'\n'+existing_tables(root+'VIFAILBACK/MODEL_AND_CONFIGURATION_AUDIT.md'))
    replace_body('07_scientific_validity/LEAKAGE_AND_SELECTION_AUDIT.md',"""
The audit checked disjoint sample roles for25 REASSEMBLE plan jobs and12 ViFailback T/V/C/assessment jobs. Vi task groups are disjoint, and the three inner-OOF pools exactly cover their corresponding outer training pools without assessment overlap. All MSM/Handover saved prediction rows, including all roles and corruptions, were joined to native final manifests; IDs and labels matched. Original case output hashes and763 independent metric/history checks passed. `SPLIT_AND_LABEL_VERIFICATION.csv` records the checks and their limits. A valid nominal-group contract does not certify unknown physical participant/tool/session identities.

Original REASSEMBLE normalization, branch selection, sigmoid calibration and fusion fitting use nested training-side data. Phase1 separates T/V/C/assessment. However, selecting fit3 for a later100-epoch study and choosing boundary variants from exposed outer AP introduces research-level post-selection. Per-fit isolation and an untouched confirmatory test are different properties. The100-epoch follow-up's920-row stacking bank is genuinely base-held-out but is not a full four-inner-fold100-epoch OOF design. Fusion accuracy on its own meta-training rows is training performance.

MSM nominal-group OOF is checked. Date-proxy sensitivities and incomplete tool/workpiece identities limit stronger independence claims. External standardizers, quality moments and corruption scales use fitting rows. Handover trial-disjointness cannot certify participant-disjointness; the participant OOF gate appropriately blocks fused training. The common-window observation amendment remains explicit, and participant identities were not invented.

ViFailback task disjointness is supported; physical-session and hardware-clock independence remain unverified. Seeds reuse the same episodes. The4,384-row feature bank versus4,382-row model cohort is a valid ID-subset join, not automatically leakage. Labels describe episode outcomes, not visible failure times.

**Concrete PHM legacy preprocessing defect:** `scripts/phm2026/results/sq2_sq3_fusion.py::main` fits a single normalizer before LOEO using default `training_split='train'`, which is fixed EXP-B in the source minute table. LOEO instead trains on EXP-F for EXP-A/EXP-B assessments. Consequently, EXP-B held-out measurements enter its normalization; for EXP-A assessment the scaler uses EXP-B validation rather than EXP-F training. The normalizer is training-only for the canonical B/A/F design but not for this changing LOEO design. The aggregate results are preserved with this limitation; no correction was made.

Some PHM late-fusion summaries declare targetv3 while their resolved configuration declaresv2. Both records remain visible; equivalence is not assumed. The20-setting DINO appearance sweep reuses38 human calls for comparison/selection; best-of20 is optimistic development performance.

Missing identity metadata, repeated test exposure and concrete preprocessing-scope mismatches are separately reported. These findings do not imply intentional leakage. The audit did not change labels, formulas, source code, splits or historical results.
""")
    coverage=existing_tables('07_scientific_validity/SEED_AND_FOLD_COVERAGE.md')
    replace_body('07_scientific_validity/SEED_AND_FOLD_COVERAGE.md',coverage+"""

Per-run configurations retain actual seeds, not only seed-family names. Negative-control permutations and reused checkpoints are explicitly labeled. More files do not create independent folds. C20 has complete five-outer-fold coverage for seed42 only. The100-epoch CNN/F2 pilots each have one selected fold and seed. MSM,Handover and ViFailback repeat three seeds on shared assessment identities, so seed variation cannot be treated as independent sample uncertainty.
""")
    replace_body('08_future_hpo_readiness/PARAMETERS_NOT_YET_TUNED.md',"""
No systematic validation-only full-CNN sweep was found for backbone LR,head LR,weight decay,batch/microbatch,dropout,normalization policy,optimizer family,schedule/warmup,frame count or augmentation strength. Twenty versus100 epochs changes budget and checkpoint selection. Historical16/32-frame and final-stage alternatives are exploratory model comparisons rather than a confirmatory optimizer search.

MSM/Handover external LR C,HGB learning rate/depth/regularization,visual-head optimizer/dropout and gate settings are predefined. Vi LR C,head LR/dropout and gate capacity/regularization were not systematically searched; Vi HGB leaf count was. Original F2 C is fixed1: fitting coefficients is not C tuning. Original sensor LR C,gate hidden widths and anchored penalties already have explicit grids.

Absent trials are not evidence of optimality. Omitted framework defaults remain unverified. These are audit findings, not authorization or proposed search ranges/budgets.
""")
    replace_body('08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md',"""
A defensible future study needs a frozen eligibility/label contract, an agreed independent grouping unit, train-only preprocessing, an explicit inner selection/calibration/OOF design, and declared metrics with prevalence/threshold conventions. The assessment must be unexposed or transparently described as exploratory. Pinned source/data/initial weights, selected and resumable states, and resource accounting are separate requirements.

Resolve the absent Handover participant mapping, ViFailback75-fit scheduling requirement versus the25-fit cap, and external transfer20-versus25-epoch validator mismatch before dependent work. Review the PHM normalization defect and target-version conflicts separately from preservation of historical evidence.

Independent review must decide candidate families, selection criteria, acceptable protocol limitations and budget. This audit does not choose a winner, tuning ranges or compute allocation. Negative and unstable results remain part of the evidence.
"""+'\n'+existing_tables('08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md'))
    replace_body('09_reviewer_handoff/RESEARCHER_HANDOFF.md',"""
Start with README and the executive TablesA–H/Q1–Q13. Read CURRENT_EXPERIMENT_STATUS before interpreting stale controller metadata. Architecture inventory and SOURCE_FUNCTION_INDEX identify executed forward paths. EFFECTIVE_CONFIGURATIONS and PARAMETER_PROVENANCE preserve per-fit values and explicit uncertainty about defaults.

Before aggregating results, filter dataset,experiment,evaluation_scope,seed,fold,protocol,corruption,threshold and metric_path. Check the positive class and prevalence. Consult COMPARABILITY_MATRIX before comparing AP. Long metrics include epochs and interval endpoints; summary tables contain all non-epoch records. Predictions, checkpoints and raw inputs remain at their original paths. Hashes and source identities support independent joins and verification without copying giant artifacts.

Interpret the100-epoch pair on its selected753-action cohort and920-row stacking bank, separately from the original4,530-action pooled study. Do not fit missing C20 fusion while reproducing the audit. For Handover, inspect official documentation, empty participant identity fields and the OOF gate; unexecuted fusion is not a failed trained model. For ViFailback, report both classes and distinguish donor feature extraction from V3 model training. PHM legacy results require separate attention to provisional targets and the LOEO normalization defect.

This audit used CPU metadata and saved scores only. It did not change models,labels,raw data,source or results, nor signal/restart jobs. No Git commit or push was made: the existing worktree contains many unrelated changes and the new audit includes large generated tables. Start/end status snapshots and HEAD are preserved. This folder adds review evidence and does not replace historical outputs.

The missing-evidence and HPO-readiness reports separate recoverable records from future scientific decisions. The independent researcher must decide subsequent model selection and study authorization.
""")
    replace_body('01_executive_overview/KEY_FINDINGS_AND_LIMITATIONS.md',"""
1. The primary visual model is R18vd CNN only. The legacy hybrid encoder and PHM detector are separate architectures. Full C trains all executed CNN convolutions and promoted normalization affine parameters while keeping running moments fixed.
2. Small systematic grids did occur. Epoch selection,100-epoch budgets,seed repetition,calibration and coefficient fitting are distinct from broad optimizer HPO. Fit counts include candidates,controls and reconstruction refits.
3. The approved C20 cap is finished:25 fits,seed42,all five outer folds,20 epochs each. Fifty original fits are deferred and C20 F2 has not executed. Vi's75-fit completion gate and external transfer's25-epoch donor validator conflict with the present25-fit/20-epoch endpoint.
4. The100-epoch visual AP change0.193776→0.212585 is real on753 matched actions in one selected fold/seed. F2 AP0.334977→0.349094 is a point increase whose paired interval includes zero; generalized fusion improvement is not established.
5. Original pooled static F2 AP0.447299 and sensor AP0.429392 belong to a different five-outer protocol. MSM HGB and Vi HGB/LR provide essential strong sensor comparisons.
6. Handover participant IDs are absent. The official participant-disjoint claim cannot be independently certified, and fusion remains unexecuted. No identities were invented.
7. Vi's current4,382 episodes supersede the provisional4,384. Three seeds reuse the same assessment IDs. Failure prevalence0.856458 requires both-class metrics. Feature completion is not V2/V3 training completion.
8. PHM legacy LOEO normalization uses fixed EXP-B data outside changing fit folds. Summary/config target versions also conflict. These findings are preserved, not corrected within an audit.
9. C100's99.7% sampled training compute activity and7.77GiB allocated memory measure different things. The25.8937-hour total is paired active-child wall time, not pure C training or global GPU compute-hours.
10. Reproducibility is graded. A saved-state/prediction/metric chain can be complete while optimizer/RNG,full-history cost or independent assessment evidence is missing. No final architecture is selected.
""")
    replace_body('01_executive_overview/CURRENT_EXPERIMENT_STATUS.md',"""
| Study | Current evidence | Completed scope | Outstanding |
|---|---|---|---|
| REASSEMBLE C20 |Approved stop completed Nov3 12:23:30UTC (13:23Berlin) |25/25 cap;25/75 original;seed42;20 epochs each |50 deferred fits;C20 F2 not finalized |
| B/C100 |COMPLETE |Two arms,100 epochs each,selected14/47 |No additional paired folds/seeds |
|100-epoch static F2 |COMPLETE pilot |Two fitted F2 states,M1–M7 metrics |Single920-row stack bank;not four-inner100-epoch OOF |
| MSM P |COMPLETE |54 cases,six protocols,three seeds |R transfer unexecuted;donor20 epochs fails minimum25 |
| Handover P baselines |COMPLETE |Three seeds,official common-support cohort |F2/gates blocked by participant mapping;R unexecuted |
| Vi frozen/sensor/V1 fusion |COMPLETE saved chains |72 heads,36 LR+108 HGB candidates,27 fusion/gates |V2/V3 training0;75-fit scheduling barrier |
| PHM |Historical completed states and aggregate-only evidence |Canonical runs and legacy fusion/scoring studies |Provisional targets,missing per-fit states/epochs,LOEO defect |
| REBOOT/Intel |Feasibility/EDA/source evidence |No trained native classifier found |No performance claim |

No active primary research training was found at initial inspection. Vi's controller PID metadata was stale. Process/resource snapshots are recorded in provenance; a saved status file is not proof of a live or paused process. The audit did not signal,launch,restart or reschedule any job. The25-fit cap is complete, not a failed fit or a75-fit completion. Changes by external processes after the snapshot are outside this audit's control.
""")
    # Preserve executive tables while replacing all compact prose and answers.
    name='01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md';old=(OUT/name).read_text()
    headers=['ALL IMPLEMENTED MODELS','MODEL CONFIGURATIONS','MODEL RESULTS','FROZEN VS FINETUNED CNN','FUSION COMPARISON','HYPERPARAMETER OPTIMIZATION STATUS','REPRODUCIBILITY','MISSING EVIDENCE']
    blocks=[]
    for letter,title in zip('ABCDEFGH',headers):
        start=old.index('## TABLE '+letter+' — ');end=old.find('\n## ',start+4)
        block=old[start:end if end>=0 else len(old)];tabs=re.findall(r'(?m)^\|.*(?:\n\|.*)*',block)
        blocks.append('## TABLE '+letter+' — '+title+'\n\n'+'\n\n'.join(tabs))
    intro="""
The audit found32 explicitly defined computational families and7,969 reconstructed fit/configuration records. Of these,7,929 are marked COMPLETE:7,755 have individual fit/candidate/log evidence and174 legacy PHM calls are inferred from completed aggregate output plus source control flow. Forty records are REUSED. Counts include nested candidates,negative controls and reconstruction refits; they are not7,929 independent replications.

There are4,920 binary checkpoint/model candidates with4,438 distinct SHA256 identities, including pretrained,disposable,copied and recovery artifacts. JSON fitted states are indexed separately. The extraction retains587,101 numeric metric records and93,278 epoch-history rows. The validation report gives the exact held-out-only count. Repeated metrics at distinct aggregation scopes are preserved rather than silently deduplicated as independent observations.

The approved REASSEMBLE25-fit cap is complete. The100-epoch pair supports a single-fold visual point improvement; its fusion gain remains inconclusive. Handover fusion and Vi full/transfer model training have not executed. Small systematic parameter grids exist, but no broad full-CNN optimizer HPO is demonstrated. No final model is selected.
"""
    questions=[
      ('Q1. Did systematic tuning occur?','Yes: small nested REASSEMBLE C/hidden-width/penalty grids,Vi HGB leaf selection and PHM Ridge alpha search. No broad full-CNN optimizer-search framework evidence was found. Checkpoint selection,seed repetition,calibration and fusion coefficient fitting are distinct operations.'),
      ('Q2. Original REASSEMBLE visual settings?','Frozen pinned R18vd CNN;16 frames,640 RGB/255,mean896→128 ReLU/dropout0.1→1;training-only standardizer;AdamW LR0.001,weight decay0.001,batch128,clip1;inner AP selects5/10 epochs. Extraction uses FP16 autocast and the head FP32. Original betas/epsilon remain unverified where no state records them.'),
      ('Q3. Full-CNN100-epoch settings?','Seed42,fresh original pretrained CNN and head,all convolutions and FrozenBN affine trainable,FP32,16 frames,head LR0.001/backbone1e-5,weight decay0.001,betas(0.9,0.999),epsilon1e-8,clip1,microbatch1/effective8,workers4,cosine100 with floor0.1,no augmentation/early stopping. All100 epochs ran;V AP selected47.'),
      ('Q4. Other frozen/fine-tuned differences?','Within B100/C100,seed,head,role IDs,budget,precision and schedule match;C adds backbone optimization and affine promotion,while B trains cached features. Against the original short frozen recipe,batch,budget,schedule,feature precision and fitting/calibration roles also differ.'),
      ('Q5. What caused the observed gain?','The matched100-epoch pilot closely isolates the adaptation condition and supports its observed point gain. One preselected fold/seed cannot establish its general effect. Differences from the original short frozen study cannot be uniquely attributed to backbone fine-tuning.'),
      ('Q6. Static sensor and original F2 settings?','Sensors:22 channels,512 progress points,220 statistics;fit-local standardization;balanced LR C0.1/1/10,inner AP selection,max_iter2000,random_state0,OOF sigmoid calibration/threshold. F2:sigmoid(b+wV*pV+wS*pS),unweighted C1,lbfgs,max_iter2000,random_state0,nested calibrated OOF inputs,no extra fused calibrator.'),
      ('Q7. Were branches and fusion tuned independently?','Original sensor C selection and visual epoch selection are separate. F2 C is fixed while coefficients are estimated. F3/gate widths and anchored penalties have their own grids. External P recipes are predefined. Vi HGB validation selection precedes separate calibration and meta-fusion fitting.'),
      ('Q8. Did100-epoch fusion improve?','The completed pilot has frozen F2 AP0.334977351562 and full F2 AP0.349094220121;delta+0.014116868559,paired recording95% interval[-0.00077261755,0.02908933571]. This is a point increase with an inconclusive interval on one reused fold. C20 fusion is absent.'),
      ('Q9. Which results have multiple seeds?','MSM,Handover and Vi completed supported models across42,123,20261023. Original Section2 uses three offset seed families. C20,paired100 and100-epoch F2 use only42. Original Section1 has one base/offset family plus permutation controls; controls are not seed replication. Exact historical seed families remain in per-run records.'),
      ('Q10. Which reproducibility chains are complete?','Phase1/100 and Vi frozen selected states,histories,predictions and metrics form verified saved-artifact chains. Original F2 coefficients/OOF/output metrics are linked. External baselines/gates support inference chains but not universal exact resume. Many inner weights and PHM aggregate epochs/states are absent. Training reproduction from initialization was not attempted.'),
      ('Q11. Which comparisons are legitimate?','Original REASSEMBLE branches/F2 on the common cohort,MSM within the same primary protocol,and Vi on matching4,382 task-held-out episodes. Paired100 and Handover comparisons have explicit limits. Cross-dataset AP ranking,pooled-original versus selected-pilot results,and unexecuted V2/V3 comparisons are not legitimate direct rankings.'),
      ('Q12. What must precede defensible HPO?','Agree label/horizon/metric,eligible manifest,independent group unit,training-only nested selection/calibration/OOF and assessment handling after repeated test exposure. Resolve missing participants and75-fit/25-cap/20-versus25-epoch barriers. Preserve provenance and review PHM defects separately before any future authorized correction.'),
      ('Q13. Which candidates have evidence for discussion?','Original LR/F2,frozen/full-CNN pilots and C20 visual,MSM branches/HGB/fusions,Handover supported baselines,Vi V1/LR/HGB/meta models and historical temporal/gate variants have graded evidence. Handover fusion and Vi full/transfer classifiers lack trained results. Discussion eligibility is not a final selection.')]
    qtext='\n\n'.join('### '+q+'\n\n'+a for q,a in questions)
    replace_body(name,intro+'\n\n'+'\n\n'.join(blocks)+"""

Complete configuration tables are in `03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md` and the per-run CSV/JSON. All recorded results remain in the complete result tables; TableC is a decision-oriented subset, not a replacement. TableD's checkpoints are each arm's PHASE1_BEST_MODEL.pt; exact full paths and hashes are in the checkpoint inventory. Frozen feature extraction is excluded from its cached-head timing.

## Explicit scientific answers

"""+qtext+'\n\nNo final candidate,search range or compute budget is selected. Use the source anchors,cohort contracts and comparability matrix alongside point scores.')
    replace_body('README.md',"""
This folder contains the requested model/configuration/results audit for REASSEMBLE,ViFailback,MSM and Handover,with separate historical PHM coverage. The original task is preserved in `provenance/USER_AUDIT_REQUEST.txt`. No new training,tuning,feature extraction,model changes or job signaling was performed.

1. Read [executive overview](01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md) for TablesA–H and explicit Q1–Q13 answers.
2. Check [current status](01_executive_overview/CURRENT_EXPERIMENT_STATUS.md) and [key limitations](01_executive_overview/KEY_FINDINGS_AND_LIMITATIONS.md).
3. Inspect [architecture inventory](02_model_architecture/COMPLETE_MODEL_INVENTORY.md),[all model configurations](03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md) and [tuning history](03_hyperparameter_configuration/HYPERPARAMETER_TUNING_HISTORY.md).
4. Use [complete results](05_results/ALL_MODEL_RESULTS_SUMMARY.csv),[long metrics](05_results/ALL_RECORDED_METRICS_LONG.csv),[comparability matrix](05_results/COMPARABILITY_MATRIX.csv) and the dataset reports/plots.
5. Read [missing evidence](07_scientific_validity/MISSING_EVIDENCE.md),[reproducibility](04_training_and_checkpoints/REPRODUCIBILITY_ASSESSMENT.md),[validation](09_reviewer_handoff/AUDIT_VALIDATION_RESULTS.md) and [researcher handoff](09_reviewer_handoff/RESEARCHER_HANDOFF.md).

The taxonomy has32 computational families. There are7,969 per-fit/configuration records:7,929 COMPLETE (7,755 individually corroborated plus174 legacy control-flow-inferred),40 REUSED. Counts include candidates,controls and reconstruction refits,not independent replications. Binary candidates number4,920 with4,438 distinct hashes; additional JSON fitted states are separately indexed. Extraction retains587,101 numeric metric records and93,278 epoch-history rows. The validation report supplies exact held-out-only counts.

Large checkpoints,raw datasets,caches and prediction banks remain at their original paths. This folder is self-contained as an audit of metadata/reports; full inference/data replay requires those original artifacts. Paths in machine-readable tables are relative to the repository root unless an external original path is explicitly recorded. Source SHA256s and output identities are in FILE_AND_SOURCE_MANIFEST.csv and the checkpoint inventory. NOT RECORDED and FRAMEWORK DEFAULT — NOT VERIFIED preserve uncertainty rather than filling absent values.

Audit utilities write only inside this new audit root and inspect saved evidence on CPU. Intermediate working states may be gzip-compressed with round-trip hash receipts; required CSV/JSON data remain unabridged. Start HEAD was `eb3888f5d23310aa097dbb1be14605e931190b4a`. The audit remains uncommitted; nothing was pushed. Existing historical evidence was preserved.
""")
    # Readability in matrix/decision tables: replace dense drafting labels with explicit statements.
    comparisons=[
        ('Original REASSEMBLE branches/F2','DIRECTLY COMPARABLE','Same4530 IDs,labels and outer grouping; original nested protocol; exploratory research history.'),
        ('B100 versus C100','COMPARABLE WITH LIMITATIONS','Same753 IDs,T/V/C,seed and head budget; one previously exposed selected fold;cached-B costs omit extraction.'),
        ('100-epoch F2 versus sensor/visual','COMPARABLE WITH LIMITATIONS','Same753 IDs and canonical sensor;single920-row stacking bank;conditional intervals.'),
        ('Original pooled F2 versus100-epoch pilot','NOT DIRECTLY COMPARABLE','4530 pooled versus753 selected actions;different stacking/selection protocol.'),
        ('Original outer1 F2 versus100-epoch F2','COMPARABLE WITH LIMITATIONS','Same assessment cohort but different meta-fitting banks;not an isolated representation intervention.'),
        ('C20 versus original frozen','COMPARABLE WITH LIMITATIONS','Outer IDs may match;batch,schedule,T/V/C and recipe differ;only seed42.'),
        ('C20 versus C100','NOT DIRECTLY COMPARABLE','Five outer folds versus one selected job;cosine50 prefix20 versus fresh100-epoch run.'),
        ('MSM primary families','DIRECTLY COMPARABLE','Same primary outer IDs and protocol;F2 uses LR sensor,HGB is a separate strong baseline.'),
        ('MSM protocol sensitivities','NOT DIRECTLY COMPARABLE','Grouping unit or label2 eligibility changes;interpret as sensitivity analysis.'),
        ('Handover baseline families','COMPARABLE WITH LIMITATIONS','Same151 official test trials;participant independence unverified;documented observation amendment.'),
        ('Handover F2/gates','INSUFFICIENT EVIDENCE','Not executed because participant-disjoint OOF cannot be certified.'),
        ('Vi V1/sensors/F2/gates','DIRECTLY COMPARABLE','Same4382 task-held-out episodes,labels and seeds;both-class metrics required.'),
        ('Vi high-only versus three-camera','COMPARABLE WITH LIMITATIONS','Same episodes/splits/training recipe;different observational bandwidth.'),
        ('Vi V2/V3 versus V1','INSUFFICIENT EVIDENCE','Full/transfer classifier training has not executed;feature caches alone are insufficient.'),
        ('Cross-dataset AP ranking','NOT DIRECTLY COMPARABLE','Different labels,prevalence,window,group and input contracts.'),
        ('Boundary/legacy follow-ups','COMPARABLE WITH LIMITATIONS','Paired saved predictions exist;outer results informed later architecture choice.'),
        ('PHM versus native-failure studies','NOT DIRECTLY COMPARABLE','Provisional regression targets and LOEO normalization defect;different metric/endpoint.'),
        ('PHM best-of20 DINO claim','NOT DIRECTLY COMPARABLE','Same38 human calls used for scoring/selection;no fresh confirmation.')]
    csv_write(OUT/'05_results/COMPARABILITY_MATRIX.csv',[{'comparison':a,'classification':b,'reason':c} for a,b,c in comparisons])
    from render_reports import table
    replace_body('07_scientific_validity/SCIENTIFIC_COMPARABILITY_VERDICT.md',table(['Comparison','Classification','Reason'],comparisons)+"""

Direct comparability describes matched assessment contracts,not superiority or statistical significance. Conditional intervals retain their original resampling units. Seed variation on shared data is descriptive. No cross-dataset ranking or final model choice is made.
""")
    decision=[['Target and endpoint','Agree native failure definition,observation horizon,primary metric and both-class reporting.','All candidates'],['Comparison design','Agree cohort/split,branch sensor,calibration,threshold and acceptable input differences.','Matched family comparisons'],['Assessment independence','Handle prior outer-test exposure and post-selection transparently.','REASSEMBLE pilots/boundary'],['Identity metadata','Obtain participants or retain blocked fusion;verify tool/session assumptions.','Handover/MSM/Vi'],['Partial scope and gates','Reconcile25-fit cap with75-fit gate,and20-epoch donor with25-epoch minimum.','C20/Vi/R transfer'],['Reproducibility','Resolve unrecorded defaults,source revisions and retained states;review PHM conflicts.','All studies'],['Compute evidence','Agree any future budget after the protocol;full historical GPU-hours are unavailable.','Full CNN and repetitions'],['Selection authority','Independent review must choose candidate families;the audit has not selected one.','Future HPO']]
    replace_body('08_future_hpo_readiness/MODEL_SELECTION_EVIDENCE_TABLE.md',"""
Original static LR/F2 have a complete original-cohort prediction/OOF/coefficient chain. Frozen/full-CNN pilots and C20 visual evidence exist,with one paired100-epoch fold and no C20 fusion finalization. MSM has three-seed/three-outer fixed-recipe branches,HGB and fusion results. Handover supports official baselines but not participant OOF fusion. Vi supports V1,LR,HGB,F2 and gates across three task-held-out seeds;full/transfer classifiers are absent. Historical temporal/quality variants have exploratory selection limits. PHM uses a separate provisional target and carries legacy normalization limitations.

These candidates are documented for discussion,not ranked or selected. The following information is needed before a future choice:

"""+table(['Information','Decision required','Applies to'],decision))
    replace_body('08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md',"""
Before any new authorized HPO,freeze labels/eligibility,independent grouping,train-only preprocessing,inner selection/calibration/OOF design and assessment handling. Preserve pinned source/data/initialization and selected/resumable states. Decide primary metrics with prevalence and threshold conventions.

Resolve Handover participant metadata,Vi's75-fit gate versus the25-fit cap,and the external donor20-versus25-epoch validator. Review PHM normalization/target conflicts separately from preserving historical evidence. Missing records are not assumed defaults.

No winner,search range or budget is chosen here. Independent review and a later explicit experimental prompt determine the next work.

"""+table(['Information','Decision required','Applies to'],decision))
    # General punctuation spacing for prose/tables, leaving URLs, identifiers and decimal values intact.
    # Match only obvious comma-separated English words; scientific numbers/paths are preserved.
    for p in OUT.rglob('*.md'):
        if p.parent.name=='provenance':continue
        s=p.read_text();s=re.sub(r',(?=[A-Za-z])',', ',s)
        p.write_text(s)
    print('REPORT_EDITORIAL_PASS_COMPLETE',flush=True)

if __name__=='__main__':polish_all()
