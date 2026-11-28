# Supporting checks completed during remediation

These checks inspect source and saved results. They do not reproduce training or certify historical execution beyond the retained records.

| Check | Evidence and outcome |
|---|---|
| REASSEMBLE PatchTST | `implementations/REASSEMBLE/src/reassemble/section1_models.py:41–45` configures the Hugging Face implementation with internal scaling and input masking disabled. The installed `transformers/models/patchtst/modeling_patchtst.py:301–344,1022–1047,1158–1180` forms 31 patches for context 512, patch 32 and stride 16; the no-scaling path does not use the observed-value mask to suppress attention. The manuscript describes this configured path, without claiming a new training reproduction. |
| PHM PatchTST | `implementations/PHM2026/src/phm2026/models/patchtst/model.py:218–265` zeroes masked inputs, pads the batch sequence to complete its patch grid, marks a patch valid if any constituent position is valid, masks invalid attention keys and excludes invalid patches from mean pooling. The effect of historical batch grids on reported results remains unmeasured. |
| MSM seed 42 | `implementations/MSM/results/06_evaluation_results/metrics/pooled_heldout_metrics.csv:2732`: initialisation P, protocol `primary__group_id`, test, clean, seed 42, F2; AP `0.7553887334374729`, agreeing with the added displayed value `0.7554`. |
| MSM direction | Original paper `s41597-026-07255-7.pdf`, data-record description: UP is up-milling and DOWN is down-milling. DOWN-only is glossed accordingly. VMX9 is described conservatively as an MSM source recording; no undocumented expansion of its identifier is asserted. |
| ViFailback B02 | `implementations/VIFAILBACK/02_dataset_verification/independent_verification/VISUAL_OBSERVABILITY_REVIEW.md:19,26,59` identifies the marker-drawing case: pickup/return visible, drawing stroke uncertain at the fixed samples. `RESEARCHER_HANDOFF.md:5` identifies the screen as AI-assisted, not independent human validation. |
| ViFailback task 55 | `implementations/VIFAILBACK/10_final_research_reports/11_LIMITATIONS_AND_THREATS_TO_VALIDITY.md:7` retains coordinate quarantine and rejects guessed sign transforms. The thesis states unresolved telemetry-coordinate validity, without inventing the correct transformation or excluding additional cases. |
| Runtime forecast | `implementations/VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/18_fit_stop_and_analysis_20261124T1955Z/completed_scope_analysis/RESULT_ANALYSIS.md:125` supports a measured split-weighted central forecast of approximately 43 days, with 47 days including planning overhead. This remains a forecast for unexecuted work. |
| NwfDD | Original P035 PDF, dataset subsection: Nonwoven Fabric Defect Dataset. |
| GPAD | Original P024 PDF, abstract: Geometric Prior-based Anomaly Detection. |
| CFA | Original P023 PDF, abstract: Controlled Fusion Adapter. |
| TC-MAF | Original P026 PDF, title: Train-Calibrated Bounded Multi-Evidence Fusion. |
| GCCF-AD | Original P038 PDF, abstract/introduction: geometry-guided cross-modal consistency fusion for industrial surface anomaly detection. |
| DSE-AD | Original P031 PDF, title/abstract describes the dual-state/differential surface anomaly detector. A descriptive glossary entry is used rather than an invented letter-by-letter expansion. |
| CFM and UCF | Original Costanzino2024Multimodal and Cheng2025Multimodal PDFs: Crossmodal Feature Mapping; Uni-modal and Cross-modal Fusion. |
| GAF-Net | The [original Huang and Tong article](https://www.mdpi.com/2079-9292/15/8/1631), architecture description and Table 6, supports the descriptive “gated attention feedback network” gloss. The existing bibliography key is reused. |
| PHM indicator names | The retained feature descriptions identify FM4, NA4, M6A and ALR as organiser-provided condition-indicator channels. Their exact source labels are retained and explained as such; unsupported expansions or physical units are not invented. |

Original literature PDFs were read from `00_thesis_writing_tracking/historic reserves/Thesis/References/PDFs/`. No bibliography entries were added or changed by this audit. Numeric source strings and SHA-256 identities for the four plots are in `../LaTeX_Project/figures/results_20261128_01/vector/plot_data_and_sources.json`.
