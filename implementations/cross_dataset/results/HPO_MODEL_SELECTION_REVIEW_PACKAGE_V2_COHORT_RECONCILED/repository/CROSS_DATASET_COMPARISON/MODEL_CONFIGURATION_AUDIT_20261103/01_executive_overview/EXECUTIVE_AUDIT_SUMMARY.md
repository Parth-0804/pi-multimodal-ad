# Version2 cohort qualification

The [verified action/split reconciliation](../../../../COHORT_RECONCILIATION/MATCHED_COMPARISON_SUMMARY.md) governs REASSEMBLE comparisons in this package. The753 actions (26 recordings) are exactly original outer fold0 within4,530 actions (148 recordings). The920-action selected inner assessment is disjoint. C20 outer refit job4 shares the753 held-out actions with CNN100; C20 inner job2 does not. Compare only matching action/label/assessment/observation passports. Training and selection differences remain limitations. A stale prediction_recordings list is documented without altering the original JSON. No training or inference was run.

The original audit text and numerical results follow unchanged; generic pre-reconciliation comparison statements are historical context and are superseded by the revised comparability matrix and passports.

---

# Executive model/configuration/results audit

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

The audit found32 explicitly defined computational families and7,969 reconstructed fit/configuration records. Of these,7,929 are marked COMPLETE:7,755 have individual fit/candidate/log evidence and174 legacy PHM calls are inferred from completed aggregate output plus source control flow. Forty records are REUSED. Counts include nested candidates, negative controls and reconstruction refits; they are not7,929 independent replications.

There are4,920 binary checkpoint/model candidates with4,438 distinct SHA256 identities, including pretrained, disposable, copied and recovery artifacts. JSON fitted states are indexed separately. The extraction retains587,101 numeric metric records and93,278 epoch-history rows. The validation report gives the exact held-out-only count. Repeated metrics at distinct aggregation scopes are preserved rather than silently deduplicated as independent observations.

The approved REASSEMBLE25-fit cap is complete. The100-epoch pair supports a single-fold visual point improvement; its fusion gain remains inconclusive. Handover fusion and Vi full/transfer model training have not executed. Small systematic parameter grids exist, but no broad full-CNN optimizer HPO is demonstrated. No final model is selected.


## TABLE A — ALL IMPLEMENTED MODELS

| Dataset | Model | Architecture | Status | Results available |
| --- | --- | --- | --- | --- |
| All primary | Prevalence constant | Training-side positive prior; no learned neural parameters | Evaluation/diagnostic only | Saved metrics/linked sources; no gradient fit |
| REASSEMBLE | Action-only logistic | One-hot action context → balanced logistic | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| All primary | Static sensor logistic | Training-only standardization → logistic → optional sigmoid calibration; penalty default unverified where absent | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| MSM/HANDOVER/VIFAILBACK | Sensor HGB | Histogram gradient-boosted classification trees | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| All primary | Frozen R18vd mean + MLP | 128+256+512 spatial means → temporal/camera mean896 →128 ReLU dropout0.1 →1 | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Last-stage CNN adaptation | Frozen CNN prefix + final stage trainable + visual head | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Full CNN adaptation | All executed CNN convolutions + promoted FrozenBN affine + fresh head; fixed running moments | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE legacy | CNN + RT-DETR hybrid encoder | CNN → input projections → RTDetrHybridEncoder AIFI/FPN/PAN → pooled head | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Positional temporal Transformer | 896→128, sinusoidal time positions, 1 encoder layer/4 heads/FF256, masked mean →1 | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Temporal Transformer without positions | Same TemporalHead, positions=False; order ablation | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Boundary-bin visual pooling | Shared 896→128 ReLU dropout0.1; selected frame-bin means concatenated →1 | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Temporal GRU | 896→64 ReLU dropout0.1 + positions → GRU64 → mean →1 | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | PatchTST classification | 22 channels×512 progress points, patch32/stride16, d32, 2 layers/4 heads/FF64 →128→1 | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| All primary except blocked Handover | F2 probability logistic | sigmoid(b+wV*pV+wS*pS); signed unconstrained constant coefficients | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| All primary | Probability average | (pV+pS)/2; no fitted fusion coefficients | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Feature concatenation F3 | Visual128 and sensor220 separately→128; concat256 LayerNorm→32/64 ReLU dropout→1 | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE/MSM/VIFAILBACK | Masked softmax logit gate | Context→hidden ReLU→2; masked softmax; sigmoid(sum alpha*logit(p)) | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Anchored constant adjustment | Fixed F2 anchor; two learned tanh-bounded coefficient adjustments | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE | Anchored adaptive adjustment | Context42→16→2 adjusts fixed F2 coefficients per sample | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE legacy | Additive quality logistic | sigmoid(b + w·[pV,pS,z8]) | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| REASSEMBLE legacy | Interaction quality logistic | sigmoid(b + w·[pV,pS,z8,pV*z8,pS*z8]) | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | PatchTST scalar regression | Minute feature channels → PatchTST encoders → scalar damage regression | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | Ridge regression | Per-normalized-minute feature mean/std/min/max/last → Ridge | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | RT-DETR scalar regression | Detector-derived image representation → scalar pseudo-damage head | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | RT-DETR object detection | Ultralytics detector, pseudo-bounding-box target; detection losses | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | RT-DETR multitask | Joint detector loss and scalar regression loss | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | Latent sensor late fusion | One PatchTST per sensor group; pooled embeddings concatenate → scalar head | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | Decision sensor late fusion | Per-group PatchTST+scalar head; learned affine combination of scalars | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy | Process-aware sensor gate | Per-group embeddings project to32; process-context gate softmax; weighted embedding→scalar head | Implemented; completed variants indexed | Per-study/fold/seed result CSVs; missing variants explicit |
| PHM legacy evaluation | DINOv2 change scoring | Frozen DINOv2 patch cosine NN to baseline bank; mean/top fractions/max score | Evaluation/diagnostic only | Saved metrics/linked sources; no gradient fit |
| PHM legacy diagnostic | Sorted profile constant | Mean ordered training tooth profile; top3 scalar diagnostic | Evaluation/diagnostic only | Saved metrics/linked sources; no gradient fit |
| REASSEMBLE | Static/temporal sensor hybrid | Static and temporal SENSOR probability combination; no video branch | PARTIAL aggregate lineage | Per-study/fold/seed result CSVs; missing variants explicit |

## TABLE B — MODEL CONFIGURATIONS

| Model | Optimizer | Head/backbone LR | WD | Batch | Max/executed/selected | Trainable | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OriginalfrozenR18head | AdamW | .001/0 | 0.001000 | 128 | 10 /source5–10 /inner5or10 | 114945 | 20260927+offsets |
| B100 | AdamW | .001/0 | 0.001000 | 8 | 100/100/14 | 114945 | 42 |
| C100 | AdamW | .001/1e-5 | 0.001000 | 8 | 100/100/47 | 11314913 | 42 |
| C20 | AdamW | .001/1e-5 | 0.001000 | 8 | 20/20/Vselected | 11314913 | 42only |
| MSM/Handovervisual | AdamW | .001/0 | 0.001000 | 32 | 10/10/10 | 114945 | 42/123/20261023 |
| Vi frozen | AdamW | .001/0 | 0.001000 | 8 | 100/100/VmacroAP | 114945 | 42/123/20261023 |
| StaticLR/F2 | L2logistic | notapplicable | Csource | allrows | notepochs | d+1 | source-specific |

## TABLE C — MODEL RESULTS

| Dataset | Study/model | Seed | Fold | Held-out N | Prevalence | AP | AUROC | F1 | Brier | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REASSEMBLE | original SECTION1B/sensor_statistics | one original split/offset family | pooled5 | 4530 | 0.112362 | 0.429392 | 0.779325 | 0.622332 | 0.080448 | COMPLETE; exploratory test reuse |
| REASSEMBLE | original SECTION1B/rtdetr | one original split/offset family | pooled5 | 4530 | 0.112362 | 0.230658 | 0.697795 | 0.515284 | 0.094299 | COMPLETE; exploratory test reuse |
| REASSEMBLE | original SECTION1B/minimal_late_fusion | one original split/offset family | pooled5 | 4530 | 0.112362 | 0.447299 | 0.794968 | 0.634000 | 0.078443 | COMPLETE; exploratory test reuse |
| REASSEMBLE | REASSEMBLE_PHASE1_C20/C_full_finetuned16 | 42 | pooled5 | 4530 | 0.112362 | 0.312127 | 0.756386 | 0.130809 | 0.090146 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M1_frozen100 | 42 | 0 | 753 | 0.102258 | 0.193776 | 0.664605 | 0.000000 | 0.089570 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M2_finetuned100 | 42 | 0 | 753 | 0.102258 | 0.212585 | 0.675325 | 0.070588 | 0.089255 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M3_sensor | 42 | 0 | 753 | 0.102258 | 0.327705 | 0.723680 | 0.252632 | 0.081479 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M4_F2_frozen | 42 | 0 | 753 | 0.102258 | 0.334977 | 0.728675 | 0.177778 | 0.080453 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M5_F2_finetuned | 42 | 0 | 753 | 0.102258 | 0.349094 | 0.740298 | 0.177778 | 0.080157 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M6_average_frozen | 42 | 0 | 753 | 0.102258 | 0.348007 | 0.721240 | 0.073171 | 0.081605 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M7_average_finetuned | 42 | 0 | 753 | 0.102258 | 0.358533 | 0.745985 | 0.074074 | 0.080793 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S3 | 123 | pooled3 | 4382 | 0.856458 | 0.954370 | 0.784370 | 0.918168 | 0.107868 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S2 | 123 | pooled3 | 4382 | 0.856458 | 0.970510 | 0.853756 | 0.916996 | 0.109334 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S3 | 20261023 | pooled3 | 4382 | 0.856458 | 0.954370 | 0.784370 | 0.918168 | 0.107868 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S2 | 20261023 | pooled3 | 4382 | 0.856458 | 0.970510 | 0.853756 | 0.916996 | 0.109334 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S3 | 42 | pooled3 | 4382 | 0.856458 | 0.954370 | 0.784370 | 0.918168 | 0.107868 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S2 | 42 | pooled3 | 4382 | 0.856458 | 0.970510 | 0.853756 | 0.916996 | 0.109334 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1 | 123 | pooled3 | 4382 | 0.856458 | 0.845749 | 0.475157 | 0.922680 | 0.125489 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1 | 20261023 | pooled3 | 4382 | 0.856458 | 0.839708 | 0.463408 | 0.922680 | 0.126591 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1 | 42 | pooled3 | 4382 | 0.856458 | 0.853052 | 0.479402 | 0.922680 | 0.129213 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1_high_only | 123 | pooled3 | 4382 | 0.856458 | 0.851883 | 0.456897 | 0.922680 | 0.127796 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1_high_only | 20261023 | pooled3 | 4382 | 0.856458 | 0.849646 | 0.466178 | 0.922680 | 0.128678 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1_high_only | 42 | pooled3 | 4382 | 0.856458 | 0.847815 | 0.459756 | 0.922680 | 0.128452 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F1_average | 123 | pooled3 | 4382 | 0.856458 | 0.933227 | 0.731510 | 0.922680 | 0.111606 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F2 | 123 | pooled3 | 4382 | 0.856458 | 0.943543 | 0.746198 | 0.922129 | 0.113445 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/quality_gate | 123 | pooled3 | 4382 | 0.856458 | 0.948804 | 0.760464 | 0.919315 | 0.110313 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/gate_static | 123 | pooled3 | 4382 | 0.856458 | 0.952706 | 0.773207 | 0.921808 | 0.108946 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F1_average | 20261023 | pooled3 | 4382 | 0.856458 | 0.931124 | 0.726439 | 0.922415 | 0.112168 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F2 | 20261023 | pooled3 | 4382 | 0.856458 | 0.940587 | 0.733723 | 0.922129 | 0.113740 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/quality_gate | 20261023 | pooled3 | 4382 | 0.856458 | 0.950272 | 0.761641 | 0.919712 | 0.110474 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/gate_static | 20261023 | pooled3 | 4382 | 0.856458 | 0.952475 | 0.770848 | 0.921921 | 0.109444 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F1_average | 42 | pooled3 | 4382 | 0.856458 | 0.931760 | 0.716501 | 0.922282 | 0.113196 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F2 | 42 | pooled3 | 4382 | 0.856458 | 0.945168 | 0.752701 | 0.922129 | 0.113107 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/quality_gate | 42 | pooled3 | 4382 | 0.856458 | 0.947321 | 0.756404 | 0.919349 | 0.110529 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/gate_static | 42 | pooled3 | 4382 | 0.856458 | 0.951757 | 0.769223 | 0.921692 | 0.109431 | COMPLETE; scope limited as documented |
| MSM | primary__group_id/F2 | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.756879 | 0.940705 | 0.820887 | 0.056703 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/F2_aug | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.760170 | 0.940401 | 0.818497 | 0.058183 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/QG_aug | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.826521 | 0.926371 | 0.746251 | 0.078043 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/QG_clean | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.837418 | 0.931925 | 0.770069 | 0.070717 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/averaging | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.735594 | 0.921692 | 0.709485 | 0.087269 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/direction_only_DIAGNOSTIC | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.241181 | 0.585006 | 0.356542 | 0.241350 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/prevalence | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.145395 | 0.320038 | 0.000000 | 0.160406 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/sensor_histgradient | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.901299 | 0.974077 | 0.837956 | 0.049034 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/sensor_logistic | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.828616 | 0.929702 | 0.811268 | 0.061724 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/visual | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.298901 | 0.705674 | 0.379833 | 0.205258 | COMPLETE; mean of per-seed pooled AP |
| HANDOVER | official/averaging | mean3 seeds | official test | 151 | 0.728477 | 0.803102 | 0.580118 | 0.728694 | 0.230493 | COMPLETE; mean seeds official test |
| HANDOVER | official/prevalence | mean3 seeds | official test | 151 | 0.728477 | 0.728477 | 0.500000 | 0.842912 | 0.197807 | COMPLETE; mean seeds official test |
| HANDOVER | official/sensor_histgradient | mean3 seeds | official test | 151 | 0.728477 | 0.906319 | 0.746563 | 0.781395 | 0.212665 | COMPLETE; mean seeds official test |
| HANDOVER | official/sensor_logistic | mean3 seeds | official test | 151 | 0.728477 | 0.823624 | 0.582040 | 0.720000 | 0.237479 | COMPLETE; mean seeds official test |
| HANDOVER | official/visual | mean3 seeds | official test | 151 | 0.728477 | 0.771647 | 0.539911 | 0.580126 | 0.264805 | COMPLETE; mean seeds official test |

## TABLE D — FROZEN VS FINETUNED CNN

| Model | Executed epochs | Selected epoch | Training hours | Peak allocated GiB | AP | AUROC | Checkpoint path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B_frozen100 | 100 | 14 | 0.060992 | 0.080301 | 0.193776 | 0.664605 | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_BEST_MODEL.pt |
| C_full_finetuned16 | 100 | 47 | 23.964191 | 7.770030 | 0.212585 | 0.675325 | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_BEST_MODEL.pt |

## TABLE E — FUSION COMPARISON

| Dataset/protocol | VisualAP | SensorAP | AverageAP | F2AP | QualityAP | Comparability |
| --- | --- | --- | --- | --- | --- | --- |
| REASSEMBLEoriginalpooled5 | 0.230658 | 0.429392 | NOT RECORDED | 0.447299 | seecompleteSection2results | same4530;exploratory |
| REASSEMBLE100pilot | 0.212585 | 0.327705 | 0.358533 | 0.349094 | NOT RECORDED | same753;singlefold/seed/postselected |
| MSM mean seed pooled3 | 0.298901 | 0.828616 | 0.735594 | 0.756879 | .837418clean/.826521aug | matchedprimary;HGB.901299 |
| Handovermeanseed | 0.771647 | 0.823624 | 0.803102 | NOT EXECUTED | NOT EXECUTED | official151;participantsunknown |
| Vi pooledseed42 macroAP | 0.495156 | 0.648974 | 0.610399 | 0.628787 | 0.634019 | same4382;HGB.700020;differentmetric |

## TABLE F — HYPERPARAMETER OPTIMIZATION STATUS

| Model | Verdict | Parameters tested | Configurations/trials | Selection | Evidence |
| --- | --- | --- | --- | --- | --- |
| Original REASSEMBLE static/action LR | SYSTEMATICALLY TUNED | C0.1/1/10 | 3 per selection fold | mean inner AP; selected refit | configs/reassemble/section1.json; section1_models.evaluate_model |
| Original visual head / PatchTST | CHECKPOINT SELECTION ONLY | epochs5/10;3/6 | 2 stored epoch candidates each | mean inner AP; same optimizer recipe | configs/reassemble/section1.json |
| F3 | SYSTEMATICALLY TUNED | hidden32/epochs10 vs64/epochs20 | 2 coupled configs | mean inner AP of three-seed mean | configs/reassemble/section2.json; section2.py |
| F4/F5/F6 | SYSTEMATICALLY TUNED | hidden8/16 | 2 per gate family | mean inner AP | src/reassemble/section2.py; section2_models.py |
| Anchored F2 adjustments | SYSTEMATICALLY TUNED | lambda.01/.1/1 | 3 per adjustment family | inner validation AP/robust selection from saved execution | configs/reassemble/additional_improvements/execution.json |
| Boundary V0–V5 / legacy16/32/encoder | LIMITED/MANUAL TUNING | architecture/frame/final-stage alternatives | see variant receipts | outer-score-informed follow-up; exploratory | src/reassemble/boundary_visual/runner.py; legacy receipts |
| C20 and B/C100 | CHECKPOINT SELECTION ONLY | validation epoch; fixed LR/wd/batch | one recipe per arm | V AP; no optimizer search | PHASE1_C_ONLY_CONFIG.json; PHASE1_COMPARISON_CONFIG.json |
| MSM/Handover primary recipe | PREDEFINED CONFIGURATION | no optimizer grid | 1 per family | fixed final epoch; group/sensitivity comparisons | CROSS_DATASET_COMPARISON/configs/frozen_core.json |
| Vi frozen head / F2 / gates / LR | CHECKPOINT SELECTION ONLY / PREDEFINED CONFIGURATION | V epoch only for head | one recipe | V macro AP for head; fixed other fits | VIFAILBACK/src/vifailback/training.py; fusion.py |
| Vi HGB | SYSTEMATICALLY TUNED | max_leaf_nodes7/15/31 | 3×36=108 fitted candidates | V macro AP then C calibration | VIFAILBACK/src/vifailback/baselines.py; S2_SELECTION_AND_CALIBRATION.json |
| PHM Ridge | SYSTEMATICALLY TUNED | alpha.01/.1/1/10/100 | 5×6 saved studies=30 | EXP-A MAE | src/phm2026/models/patchtst/regression.py; ridge_selection.json |
| PHM DINO scoring | LIMITED/MANUAL TUNING | 2backbones×2banks×5aggregations | 20 evaluation configs, no new gradient fits | same38 human calls reused; best biased | docs/thesis/ANOMALYDINO_SWEEP.csv; scripts/phm2026/results/anomalydino_sweep.py |

## TABLE G — REPRODUCIBILITY

| Model/study | Code available | Config available | Checkpoint available | Predictions available | Split available | Overall status |
| --- | --- | --- | --- | --- | --- | --- |
| Phase1 C20/B and B/C100 | Yes,with provenance | Yes | Best + rotating resumable last states | Yes | Yes | COMPLETE saved chain; training replay not performed |
| Original REASSEMBLE branches | Yes | Yes | Selected outer states; many inner states absent | Yes | Yes | PARTIAL |
| Original F2 | Yes | Yes | JSON coefficients | Yes,OOF and held-out | Yes | COMPLETE fitted-state chain |
| 100-epoch F2 | Yes | Yes | Coefficients/calibrators | Yes,M1–M7 | Yes,920 stack and753 assessment | COMPLETE artifacts; limited design |
| MSM/Handover baselines | Yes | Yes | Fitted heads/LR/HGB | Yes | Yes;Handover participants absent | INFERENCE_ONLY / PARTIAL exact resume |
| MSM F2/gates | Yes | Yes | JSON/PT states | Yes,OOF/held-out | Yes | INFERENCE_ONLY |
| Handover F2/gates | Yes | Yes | No | No | Participant OOF unavailable | MISSING_ARTIFACTS; NOT EXECUTED |
| Vi frozen V1/high-only | Yes | Yes | BEST and FINAL_EPOCH100 | Yes | Yes,task groups | COMPLETE saved chain |
| Vi sensors/meta | Yes | Yes | Selected models; discarded HGB candidates absent | Yes | Yes | INFERENCE_ONLY / PARTIAL candidate replay |
| PHM canonical models | Yes,current/recorded revision | Yes | Present; some safe loaders decline | Yes | Yes | PARTIAL; provisional target |
| PHM aggregate fusions | Current source | Yes/source constants | Per-fit states not retained | Aggregate scores only | Source-defined | METRICS_ONLY |

## TABLE H — MISSING EVIDENCE

| Experiment | Missing evidence | Impact | Can it be recovered? | Required next action |
| --- | --- | --- | --- | --- |
| Handover fusion | Official pseudonymous participant mapping | Cannot certify participant OOF or split independence | Publisher metadata may recover it | Obtain mapping; do not infer identities |
| REASSEMBLE original75 | 50 other-seed fits and C20 F2 finalization | One-seed coverage only;fusion result absent | Requires future authorized work | Review scope/cap before any execution |
| 100-epoch pilot | Other seeds/folds,fresh assessment,full nested100-epoch OOF | Cannot generalize visual/fusion gain | Requires separate study | Agree independent comparison design |
| Vi full/transfer | V2/V3 trained head/fusion results | No adaptation/transfer performance claim | Future authorized work only | Resolve75-fit gate versus25-fit cap |
| External R transfer | Completed R runs and accepted canonical donor | 20 epochs fails validator minimum25 | Protocol/validator decision required | Resolve contract; preserve historical evidence |
| Historical states | Inner weights,optimizer/scheduler/RNG,exact epochs | Not every fit is loadable/resumable | Some logs may recover metadata | Keep graded reproducibility status |
| GPU cost | Full allocation/extraction/telemetry history | No exact global GPU-hours total | Scheduler logs if retained | Recover accounting separately |
| Physical independence | Tool/workpiece/session/clock metadata | Nominal groups may not equal physical independence | Publisher evidence may help | Declare actual grouping limits |
| PHM legacy | Per-fit states/epochs and consistent target/scaler lineage | Aggregate-only results and preprocessing defect | Some records may exist;correction is separate work | Review defects without rewriting outputs |
| Future HPO | Agreed endpoint,assessment,selection criteria and budget | No justified final choice yet | Independent research decision | Review audit before authorization |
| Audit coverage | Unlogged/deleted fits or external artifacts | Counts cover discovered evidence,not unknown history | Only with additional records | Supply any missing provenance |

## Explicit scientific answers

### Q1. Did systematic tuning occur?

Yes: small nested REASSEMBLE C/hidden-width/penalty grids, Vi HGB leaf selection and PHM Ridge alpha search. No broad full-CNN optimizer-search framework evidence was found. Checkpoint selection, seed repetition, calibration and fusion coefficient fitting are distinct operations.

### Q2. Original REASSEMBLE visual settings?

Frozen pinned R18vd CNN;16 frames,640 RGB/255, mean896→128 ReLU/dropout0.1→1;training-only standardizer;AdamW LR0.001, weight decay0.001, batch128, clip1;inner AP selects5/10 epochs. Extraction uses FP16 autocast and the head FP32. Original betas/epsilon remain unverified where no state records them.

### Q3. Full-CNN100-epoch settings?

Seed42, fresh original pretrained CNN and head, all convolutions and FrozenBN affine trainable, FP32,16 frames, head LR0.001/backbone1e-5, weight decay0.001, betas(0.9,0.999), epsilon1e-8, clip1, microbatch1/effective8, workers4, cosine100 with floor0.1, no augmentation/early stopping. All100 epochs ran;V AP selected47.

### Q4. Other frozen/fine-tuned differences?

Within B100/C100, seed, head, role IDs, budget, precision and schedule match;C adds backbone optimization and affine promotion, while B trains cached features. Against the original short frozen recipe, batch, budget, schedule, feature precision and fitting/calibration roles also differ.

### Q5. What caused the observed gain?

The matched100-epoch pilot closely isolates the adaptation condition and supports its observed point gain. One preselected fold/seed cannot establish its general effect. Differences from the original short frozen study cannot be uniquely attributed to backbone fine-tuning.

### Q6. Static sensor and original F2 settings?

Sensors:22 channels,512 progress points,220 statistics;fit-local standardization;balanced LR C0.1/1/10, inner AP selection, max_iter2000, random_state0, OOF sigmoid calibration/threshold. F2:sigmoid(b+wV*pV+wS*pS), unweighted C1, lbfgs, max_iter2000, random_state0, nested calibrated OOF inputs, no extra fused calibrator.

### Q7. Were branches and fusion tuned independently?

Original sensor C selection and visual epoch selection are separate. F2 C is fixed while coefficients are estimated. F3/gate widths and anchored penalties have their own grids. External P recipes are predefined. Vi HGB validation selection precedes separate calibration and meta-fusion fitting.

### Q8. Did100-epoch fusion improve?

The completed pilot has frozen F2 AP0.334977351562 and full F2 AP0.349094220121;delta+0.014116868559, paired recording95% interval[-0.00077261755,0.02908933571]. This is a point increase with an inconclusive interval on one reused fold. C20 fusion is absent.

### Q9. Which results have multiple seeds?

MSM, Handover and Vi completed supported models across42,123,20261023. Original Section2 uses three offset seed families. C20, paired100 and100-epoch F2 use only42. Original Section1 has one base/offset family plus permutation controls; controls are not seed replication. Exact historical seed families remain in per-run records.

### Q10. Which reproducibility chains are complete?

Phase1/100 and Vi frozen selected states, histories, predictions and metrics form verified saved-artifact chains. Original F2 coefficients/OOF/output metrics are linked. External baselines/gates support inference chains but not universal exact resume. Many inner weights and PHM aggregate epochs/states are absent. Training reproduction from initialization was not attempted.

### Q11. Which comparisons are legitimate?

Original REASSEMBLE branches/F2 on the common cohort, MSM within the same primary protocol, and Vi on matching4,382 task-held-out episodes. Paired100 and Handover comparisons have explicit limits. Cross-dataset AP ranking, pooled-original versus selected-pilot results, and unexecuted V2/V3 comparisons are not legitimate direct rankings.

### Q12. What must precede defensible HPO?

Agree label/horizon/metric, eligible manifest, independent group unit, training-only nested selection/calibration/OOF and assessment handling after repeated test exposure. Resolve missing participants and75-fit/25-cap/20-versus25-epoch barriers. Preserve provenance and review PHM defects separately before any future authorized correction.

### Q13. Which candidates have evidence for discussion?

Original LR/F2, frozen/full-CNN pilots and C20 visual, MSM branches/HGB/fusions, Handover supported baselines, Vi V1/LR/HGB/meta models and historical temporal/gate variants have graded evidence. Handover fusion and Vi full/transfer classifiers lack trained results. Discussion eligibility is not a final selection.

No final candidate, search range or compute budget is selected. Use the source anchors, cohort contracts and comparability matrix alongside point scores.

## Evidence anchors

- [configs/reassemble/section1.json](../../../configs/reassemble/section1.json) — visual/sensor/logistic_C/selection/calibration.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — actual classifier forwards, neural_fit, logistic_fit.
- [src/reassemble/section1_features.py](../../../src/reassemble/section1_features.py) — frame pooling and normalized-progress sensor resampling.
- [runs/reassemble/20260927T154732Z-section1/training_implementation.json](../../../runs/reassemble/20260927T154732Z-section1/training_implementation.json) — recorded original implementation revision.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json) — effective shared100 horizon; head/backbone LR.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) — all CNN stages, FrozenBN affine promotion; fixed running moments.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py) — training100/checkpoint selection/recovery.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [runs/reassemble/20260927T175336Z-section1b/assessment/results.json](../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json) — metrics, paired recording intervals, complementation.
- [runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json](../../../runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json) — five fitted F2 coefficient states.
- [src/reassemble/section1b.py](../../../src/reassemble/section1b.py) — fit_stacker; nested calibrated probability inputs.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json) — M1–M7 common-threshold metrics.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json) — conditional paired recording intervals.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json) — canonical sensor identities and stacking-bank limitations.
- [MSM/04_experiment_protocol/experiment_config.json](../../../MSM/04_experiment_protocol/experiment_config.json) — fixed P recipe, labels/groups/sensor channels.
- [MSM/03_processed_model_inputs/final_sample_manifest.csv](../../../MSM/03_processed_model_inputs/final_sample_manifest.csv) — 1895 eligible sample IDs/native labels/clock mapping/source hashes.
- [MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json) — 54 completed protocol/fold/seed cases, output hashes.
- [CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py](../../src/external_eval/evaluate.py) — execute_case: train, inner OOF, official validation, held-out scopes.
- [CROSS_DATASET_COMPARISON/src/external_eval/models.py](../../src/external_eval/models.py) — fit_base/fit_fusions/fit_quality/predictions.
- [HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json](../../../HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json) — participant_oof_gate/observation_amendment/validation_use.
- [HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv](../../../HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv) — 587 mapped IDs, native labels, empty participant IDs.
- [HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json) — three seeds complete; fused methods skipped.
- [HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json](../../../HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json) — official dataset record and metadata.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
