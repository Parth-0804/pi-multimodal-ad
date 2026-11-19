# Phase 1 historical audit

Read-only evidence audit, 26 October 2026. No historical fit was restarted. Original failure-positive task: 4,530 action segments, 509 failures, 148 HDF5 recordings. Target is NOT `segments_info/<id>/success`; high-level actions are pick/insert/remove/place. Uniform16 whole-action timestamp sampling is preserved; last-quarter sampling is a different historical study and is excluded from Phase1.

## Actual architecture

Local pretrained `PekingU/rtdetr_r18vd`, revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`. The historical visual forward executes only its ResNet CNN, spatial means of stage2/3/4 maps, concatenation to896, and mean over independent frames. This does not execute the detector, box heads, hybrid encoder or decoder and does not learn temporal order. The classification head is Linear896→128/ReLU/Dropout0.1/Linear128→1. Original CNN has11,190,112 convolutional parameters; the five trainable final-stage convolution tensors in later partial fine-tuning total8,388,608. Frozen normalization affine values and running moments were stored as buffers. A full-CNN experiment must promote affine values and unfreeze all executed convolutional stages deliberately.

## Historical training budget

Configured candidates are distinct from actual executed/selected epochs. A selected budget is not evidence that longer epochs would improve the model.

| Experiment | Trainable components | Epoch candidates | Actual selected/executed epochs | Seeds | Learning rates | Early stopping | Runtime | Evidence |
|---|---|---|---|---|---|---|---|---|
| Original Frozen16 |128-unit classifier; frozen CNN|5,10|Outer selected [5, 5, 10, 10, 5]; inner candidates executed through10|20260927 family with fold offsets|head1e-3, decay1e-3|None; mean inner AP selects5/10|11.12s nested classifier fitting; extraction separate|`runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00.json`; `src/reassemble/section1_models.py`|
| Original sensor statistics |Balanced logistic coefficients; training-only standardizer|No epochs; C=.1,1,10|Selected C=[1.0, 0.1, 10.0, 0.1, 0.1]|Deterministic solver|Not applicable|Solver convergence/max_iter2000|206.97s nested fitting|`sensor_statistics_perm00.json`; same implementation|
| Original F2 |Unweighted two-probability logistic stacker|No epochs|Fitted per outer fold on correctly nested OOF probabilities|Deterministic reference|C1; no class weights|Solver convergence|max runtime not isolated in assessed summary|`runs/reassemble/20260927T175336Z-section1b/assessment/results.json`; `src/reassemble/section1b.py`|
| CNN versus hybrid encoder |Classifier only; both extractors frozen|Fixed5|All5 folds,45 new heads/5 reused|42 family|head1e-3; no extractor LR|None|675.26s new head fitting; hybrid extraction4260.23s|`00_experiments/rt_detr_encoder_comparison/results/run_01/comparison/execution_cost.json`|
| Later frozen_16_frames |head only|Frozen5; adapted2 under explicit amendment|25 completed fits; epoch counts {5: 25}|42 family|head1e-3; stage1e-5|None; fixed budget|0.164h training only|`00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/frozen_16_frames/**/visual_fit/complete.json`|
| Later fine_tuned_16_frames |head + final CNN stage|Frozen5; adapted2 under explicit amendment|25 completed fits; epoch counts {2: 25}|42 family|head1e-3; stage1e-5|None; fixed budget|9.086h training only|`00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/fine_tuned_16_frames/**/visual_fit/complete.json`|
| Later frozen_32_frames |head only|Frozen5; adapted2 under explicit amendment|25 completed fits; epoch counts {5: 25}|42 family|head1e-3; stage1e-5|None; fixed budget|0.160h training only|`00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/frozen_32_frames/**/visual_fit/complete.json`|
| Later fine_tuned_32_frames |head + final CNN stage|Frozen5; adapted2 under explicit amendment|25 completed fits; epoch counts {2: 25}|42 family|head1e-3; stage1e-5|None; fixed budget|12.456h training only|`00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/fine_tuned_32_frames/**/visual_fit/complete.json`|
| Matched Frozen32 versus FineTuned32 |Head only versus head+final stage|Exactly2|100 fits:75 new,25 reused; all5 folds/2 seeds|42,20261023|head1e-3; stage1e-5; decay1e-3|None|21.845h full task including assessment/reporting|`00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/RESULTS_SUMMARY.md`|
| Boundary-aware temporal pooling |Frozen CNN, alternative temporal heads|V0–V4:5,10; GRU V5:5,10,20|Selected by outer fold: {'V0': [5, 5, 10, 10, 5], 'V1': [10, 5, 10, 10, 5], 'V2': [10, 10, 10, 10, 5], 'V3': [10, 10, 10, 10, 10], 'V4': [10, 10, 10, 5, 10], 'V5': [5, 5, 5, 5, 5]}|Single20260927 family|AdamW1e-3/decay1e-3|Fixed candidate search|Not isolated in compact handoff|`artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md`|
| Earlier partial fine-tuning/temporal extension |Final CNN stage plus temporal head, not full CNN|Configured max20/patience5; temporal max100/min10/patience12|Task1 cancelled/incomplete; never interpret configured maximum as completed|Configured20260927/28/29|CNN1e-5, head1e-4; temporal1e-3|Configured patience; actual partial evidence retained|Incomplete; no completed full-CNN claim|`configs/reassemble/additional_improvements/execution.json`; `src/reassemble/additional_improvements/finetune.py`|

The Oct20 four-arm five-epoch attempt is separately preserved as an interrupted study; its progress reports6 completed visual fits and7 started, not100 completed. The later complete study amended adapted arms to2 epochs while frozen arms remained5. These are different records. No full-backbone or three specified-seed,25–50-epoch experiment exists in these histories.

## Verified historical metrics and comparability

Original Frozen16 AP=0.230658315043, AUROC=0.697794828623. Original sensor AP=0.429391869368. Original static F2 AP=0.447298551440, directly read from the original assessment record; the approximate0.4473 reference is therefore verified to its saved precision. These values are historical context, not promised outcomes.

The original Frozen16 extraction used FP16 autocast with FP32 pooled features. The later matched studies and current GPU audit use FP32 extraction. Original A also selected5/10 epochs through nested inner folds; later models use held-out C calibration and fixed budgets. A versus new B is therefore not a pure duration-only causal comparison. The new protocol explicitly labels a matched short B-trajectory snapshot A_r, while retaining historical A unchanged.

The later one-family four-arm study reports Frozen16/Fine16 visual AP .221644/.224466 and F2 .440680/.437521. Frozen32/Fine32 AP .219427/.230609 and F2 .439584/.438566. Matched32 two-epoch F2 differences were -.000796 (seed42) and -.002822 (seed20261023), with both recording intervals containing zero. The CNN/hybrid comparison reports F2 .440764/.424979. These results do not establish a full-backbone or stable three-seed gain.

## Label, fold and fusion audit

Raw target/interval/whole-action-frame checks are being independently verified in PHASE1_LABEL_FRAME_ALIGNMENT.json and the full-cohort identity manifest. Frame files retain source HDF5 identity, video path, recording/segment IDs and exact frame/timestamp arrays. No IDs, annotations or outcome-derived quality enter the CNN.

Original Section1B explicitly uses sub-inner branch selection/calibration excluding each meta-assessment group. Later four-arm machinery uses fixed25 fit roles, each with recording-disjoint G/C/prediction groups. Four inner-held-out probability banks train each outer F2; independently fitted outer branches predict the outer assessment. Source inspection found a usable leakage-safe structure. The new fit plan adds validation V within G, ensuring checkpoint selection does not use the inner OOF assessment or outer test. The25 deterministic sensor fits are shared across new arms/seeds.

Historical outer results have been repeatedly examined; this is an exploratory follow-up. No claim of untouched confirmation, temporal causal reasoning, robustness or cross-dataset transfer is supported.

## Evidence gaps

Temporal selected epochs have now been aggregated from all30 branch completion records in PHASE1_TEMPORAL_ACTUAL_BUDGETS.json. Original compact metadata retain refit/inner-fit information; no standalone wall-time is invented when absent. Earlier cancelled Task1 is not completion evidence. Historical checkpoint replay generally verifies final model predictions; it does not certify a new runner's sampler or prefetch resume. Those are explicit current preflight requirements.
