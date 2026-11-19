# MSM supervisor presentation outline

Working title: **Multimodal architecture evidence: REASSEMBLE findings and MSM feasibility boundaries**. Suggested duration 12–15 minutes plus discussion. This is not approval of a final thesis title or a request to launch additional experiments.

## Slide 1 — Scientific verdict

**Message:** REASSEMBLE supplies bounded predictive/fusion evidence; MSM supplies audited input/software portability evidence. Learned-CNN transfer and independent MSM performance remain unestablished.

Show three status boxes: “REASSEMBLE fixed-prediction results verified”; “MSM 114 construction-valid intervals”; “MSM independent evaluation blocked.” Say explicitly that no Stage 5 training occurred.

## Slide 2 — The original four questions

Use the [original nine-page exposé](<../../../MA_Exposé_Ravaliya_Parth.pdf>), pp.2–3. Preserve SQ1 representations; SQ2 unimodal/concatenation/late/gated comparison; SQ3 missing/degraded/unreliable modalities; SQ4 evaluation beyond accuracy. Explain the move from the original welding case study to actual dataset-specific tasks without changing the question hierarchy. MSM does not turn SQ3 into an external-dataset question.

## Slide 3 — Why MSM and what its labels mean

Show version-pinned official identity; 69 folders/2,575 native cutting intervals. Explain native0 stable normal, native1 abnormal cutting, native2 stable operation with a defective tool. Main MSM target is 1 versus 0/2. Contrast REASSEMBLE completed-action failure, 509/4,530 (11.24%), with the MSM eligible cohort, 10/114 (8.77%). Do not show cross-dataset AP rankings.

## Slide 4 — What was verified before implementation

Timeline: official inventory/labels → selective pilot acquisition → actual media/sensor inspection → label-blind alignment/visibility/coverage → fixed 16-frame contract. Use an existing validated frame-plus-sensor diagnostic from Stage 2. Explain the corrected VMX/dataset9 +49.73 s mapping and the rejected exploratory alias; correction is quality control, not a method novelty claim. Industry has no video.

## Slide 5 — Reused architecture and new MSM work

Diagram: 16 guarded frames → frozen R18vd **CNN** → 896 mean-pooled values → new 128-unit head. Corresponding native MTC cut → 90 statistics → new logistic classifier. Their probabilities → new OOF-trained F2. Highlight reusable code/pretrained CNN versus newly fitted heads/scalers/fusion; no source failure head or F2 coefficient transfers. RT-DETR's Transformer/detector is not executed.

## Slide 6 — What REASSEMBLE actually establishes

Table: statistics AP 0.429392; frozen CNN 0.230658; short PatchTST 0.241591; F2 0.447299. Main contrast F2−sensor **+0.017907 [0.008603,0.028284]**, recording-clustered and conditional on fitted models. Mention calibration improvement with Brier delta −0.002005. Repeated core F2 values are exact reuse, not independent replications. Later anchored clean adaptation is a separate positive result, not evidence every adaptive gate succeeds or fails.

## Slide 7 — Visual gains and fusion gains are distinct

Use the newly generated `figures/controlled32_visual_vs_fusion.png`, with two-epoch seed42/20261023 point effects, and cite [controlled two-epoch 32-frame results](<../../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/fusion_results.csv>). Seed42 visual AP increases about0.00790 while F2 drops about0.00080; the other seed has lower visual and F2 scores. Explain that this does not identify a causal mechanism. Contrast with exploratory boundary pooling, where both visual and fusion scores rise under a different representation/selection procedure. Neither is learned-CNN transfer to MSM.

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
