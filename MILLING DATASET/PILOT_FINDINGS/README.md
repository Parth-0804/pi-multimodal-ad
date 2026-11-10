# MSM pilot findings

**Current decision: CONDITIONAL GO.** Full laboratory data validation is complete; model evaluation remains unperformed. Read the [research decision](05_FULL_LABORATORY_FEASIBILITY/MSM_RESEARCH_DECISION.md) and [researcher handoff](05_FULL_LABORATORY_FEASIBILITY/REVIEW_HANDOFF.md) first.

MSM was selected as an independent milling domain with native interval annotations, laboratory video and synchronized sensor recordings. It can test portability of the REASSEMBLE architecture and, later, trained CNN weights. Its existence alone provides no evidence of successful transfer, fusion benefit or missing/corrupted-modality robustness.

The official dataset has 69 experiment folders: 37 VM20i, 19 VMX30Ui and 13 industrial VF10. The 56 laboratory folders contain 2,512 native cuts: 1,877 label 0, 458 label 1 and 177 label 2. Label 2 means stable cutting with a defective tool; the primary frozen target is intervention-worthy cutting abnormality (1 versus 0/2), with a separate 1-versus-0 sensitivity. Dataset: `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`.

| Evidence stage | What was established | Scientific status |
| --- | --- | --- |
| [1: dataset and labels](01_DATASET_AND_LABEL_AUDIT/SOURCE_INDEX.md) | Official identity/version, all 69 label files and native meanings | Completed audit |
| [2: alignment and modalities](02_VIDEO_ALIGNMENT_AND_MODALITIES/SOURCE_INDEX.md) | Corrected label-blind audio synchronization; 116 timing/frame-valid and 114 paired pilot intervals | Completed restricted pilot; no predictive result |
| [3: architecture and smoke](03_ARCHITECTURE_IMPLEMENTATION_SMOKE/SOURCE_INDEX.md) | 16-frame CNN and 90-statistic sensor adapters, new heads and leakage-safe F2 pipeline work | Bounded development smoke only; no independent efficacy evidence |
| [4: evaluation and transfer](04_BLOCKED_EVALUATION_AND_TRANSFER/SOURCE_INDEX.md) | Evaluation correctly stopped: two positive pilot groups could not support three outer folds; completed canonical R source was absent | Failed prerequisites; zero held-out results, not a negative ML finding |
| [5: full laboratory feasibility](05_FULL_LABORATORY_FEASIBILITY/SOURCE_INDEX.md) | 204 additional minimal files; 1895 paired technically eligible intervals; date/session and visibility limitations audited | Completed data audit; future model experiments require review |

The current joint technical cohort has **1895 intervals**: 1434 native 0, 336 native 1, 125 native 2; **45 nominal folders**, **17 positive-containing folders**. Technical eligibility is not evidence that an anomaly is optically observable. Independent visibility review remains pending for all these examples; the original pilot has only the previously documented Codex coarse-context review.

The partial-overlap correction is essential: VMX30Ui/dataset9 uses **+49.73 s**, not the rejected exploratory +16.04 s alias. The corrected calibration-template estimator uses independent withheld anchors and support limits. See the preserved [methodology correction](02_VIDEO_ALIGNMENT_AND_MODALITIES/METHODOLOGY_CORRECTION.md). New ambiguous mappings were excluded rather than resolved from class labels.

Machine/experiment folders do not establish independent physical sessions. Date relationships, repeated program hashes and generic tool/material descriptions remain potential dependencies. See the [split gate](05_FULL_LABORATORY_FEASIBILITY/MSM_INDEPENDENCE_AND_SPLIT_GATE.md). Target definition and grouping require researcher approval before final splits are frozen.

Reusable components are the verified CNN extractor/pooling, head constructor and pipeline infrastructure. MSM requires its own visual head, sensor classifier/scalers and OOF-fitted F2 coefficients. No full-cohort CNN extraction, new training, F2 evaluation or source checkpoint inspection occurred in this stage. The ongoing Phase 1 job was not queried or changed. No MSM CNN-transfer result exists.

**Next proposed experiment:** a blinded visual-observability review of the technically eligible 16-frame sequences, sampled across native classes and date/session clusters. Do not launch model evaluation before review and target/group approval.

All originals remain in their authoritative versioned runs. [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json) records exact original paths, SHA-256 hashes and copy/index status. Large tables, videos, audio, checkpoints and caches are referenced rather than duplicated. This folder supersedes no historical result and does not convert smoke checks into test performance.
