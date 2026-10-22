# Implementation and study status — targeted clarification

VERIFIED_WITHIN_SCOPE means a source/text/table operation was inspected here. REPORTED refers to historical claims; it does not inherit a report's “verified execution” wording. INFERRED/PROPOSED/UNKNOWN/NOT_RUN are explicit below. The pinned audit is unchanged. Its claim IDs are navigation references, not substitutes for source inspection.

## A. Core visual path

VERIFIED_WITHIN_SCOPE: scripts/reassemble/03_section1_features.py calls section1_features.main; load_visual returns RTDetrForObjectDetection(...).model.backbone.model, sets eval and requires_grad_(False), and extract forwards that returned object to feature_maps. Source: src/reassemble/section1_features.py:43–57,85–103; downstream src/reassemble/section1_models.py:31–35,87–115,123–131; audit C01–C04,C08. The wrapper loads weights; the traced core caller does not forward the full detector hybrid encoder/decoder. The config frozen flag is not consulted there. Head fitting on cached vectors cannot change that backbone.

Sixteen unique sampled frames span the whole annotated interval. Map-wise spatial means are concatenated and temporally averaged. Weight adaptation and input visibility are different decisions. Checkpoint provenance alone proves neither full-detector use nor useful temporal modelling.

VERIFIED_WITHIN_SCOPE target construction: inventory.py:47–60 maps native success to failure=int(not success); sample key is recording_id+segment_id. The current saved cohort check now measures 4530 selected rows / 509 failures / 148 recording IDs and unique keys. This confirms saved-table consistency, not raw annotation correctness or independent collection groups. Complete-interval support is INFERRED completed-action outcome classification; early-warning capability is NOT ESTABLISHED.

## B. Fine-tuning

VERIFIED_WITHIN_SCOPE implemented partial path: additional_improvements/finetune.py:48–59 unfreezes backbone.encoder.stages[3], trains TemporalHead, and overrides train() to retain backbone eval for running statistics. _fit:103–118 uses separate head/stage AdamW rates and training-subset class weighting. main:181–209 supplies nested fits and final prediction output. prefix_cache.py:14–30 caches the immutable prefix while keeping the last stage live. No model/gradient/forward code ran here.

REPORTED historical gradient audit: supported=true,8636033 trainable parameters. This is a retained number, not a dynamic count measured by this session. Source exists for partial fine-tuning; a full-backbone-training or from-scratch comparison was not established in the inspected path. No total-parameter count is invented.

REPORTED chronology: September28 status paused; September30 closure explicitly DISCONTINUED_BY_USER, queue CLOSED. Temporal report says five-fold V-FT incomplete. VERIFIED_WITHIN_SCOPE filesystem: the specific source-defined V-FT_predictions.npz is absent at the recorded expected path; this is not a whole-repository absence claim. Existing V-MEAN/V-TEMP/V-NOPOS artifacts are separately inventoried. No permission to finish discontinued work is inferred.

## C. Two kinds of transformer

Core spatial RT-DETR hybrid encoder/decoder: no invocation on the traced core path; a candidate representation experiment is PROPOSED only. The checkpoint's detector origin is distinct.

Temporal visual alternative: additional_improvements/models.py:8–24 projects frame features to 128, adds sinusoidal positions, uses one TransformerEncoder layer with four heads, then masked mean/classifier. Caller unimodal.py:13–36 -> neural.py:15–37,93–126 is linked in the audit. Current sources/hashes match the selected recorded identities; history reports completed frozen temporal variants, with partial/discontinued fine-tuning. These are not new untouched studies.

PatchTST: section1_models.py:38–45 is a separate sensor-sequence alternative. Retained core Section1B uses sensor statistics, not PatchTST: section1b.py:163–171 deletes the raw sensor sequence and calls stacking. Do not merge these architectures in a thesis diagram.

## D. Fusion, robustness and evidence coverage

VERIFIED_WITHIN_SCOPE formulas: F2 uses a learned logistic link on calibrated branch probabilities (section1b.py:83–94). F4–F6 use softmax context/availability weights on branch logits and sigmoid (section2_models.py:21–46; section2.py:124–139). Changing between those families changes link and adaptivity together. Coefficients are not universal normalized contributions.

VERIFIED_WITHIN_SCOPE separate anchored path: models.py:26–40 and anchored.py:20–38,79–120 implement A0, constant and input-dependent bounded coefficient adjustments under one probability-anchored link. Existing matched controls must be evaluated before advertising a missing control.

Section3 current source/config covers image Gaussian/blur/frame loss, sensor Gaussian/channel/block/stuck faults, and explicit whole-modality absence. section3_evaluate.py:67–110 changes the affected branch/quality, keeps fixed thresholds and applies exact survivor fallback for declared absence. Missingness movement is structurally forced, not learned detection of hidden faults. Config/source history and conditional numerical checks are in the coverage CSV and NUMERICAL_CHECKS.md.

New bounded evidence: four preselected banks have15 AP values agreeing exactly with saved reports. Their y/fold vectors match the current source-defined saved cohort order and nested split; outer recording sets/inner partitions checked disjoint. Banks themselves have no recording/segment/row keys, so producing-run row identity remains unproven. These are CONDITIONAL_ARRAY_ARITHMETIC, not reproduced training/inference or calibrated causal modality shares. No new uncertainty or threshold calculation was made.

Historical Task4 exposure-matched corruption training remains EXCLUDED from execution/repair/extension/restart/equivalent work. Its reported completion cannot unlock it. Reading that coverage may eliminate a proposed study. Historical sensor reports conflict by date: early hybrid pending; later September30 report supplies hybrid results and inventory locates a bank. Both remain intact. Boundary-aware pooling is a separate selected follow-up, not completion of discontinued Task1 or an untouched confirmation.

## E. External dataset identity

UNKNOWN: the earlier “milling/two datasets” pair. A scoped search of README, REPO_MAP, docs/reassemble, docs/thesis and docs/intel_welding did not establish it. Located Paderborn documentation concerns a different vibration/current/context protocol and labels fusion Gate3 unrun; RawVib is PHM waveform work. Neither recovers the pair.

Public shortlist entries are separately labelled: IndustReal and InspecSafe-V1 are NEW candidates for later feasibility, not approved datasets or recovered choices. HA4M action labels, AURSAD numeric channels and Paderborn fault labels cannot be forced into the same image–sensor outcome task. See frozen literature DATASET_SHORTLIST.csv for source/access/version limits.

Evidence checked: current callable source ranges above,124 preflight hashes including exact audit, selected historical text/artifact presence, bounded anonymous NPZ arithmetic and saved cohort/split consistency.
Still uncertain: raw target validity, higher-level independence, complete per-fit producing-source/row chain, complete V-FT artifacts, selection history, original dataset pair.
Defensible conclusion: reuse existing temporal/noise/control work and resolve provenance before choosing any new experiment. Source existence, compatible hashes and arithmetic agreement do not close scientific validity gaps.
