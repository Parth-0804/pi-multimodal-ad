# pi-multimodal-ad

Master’s thesis research on visual and numerical sensor representations, multimodal fusion, and condition/failure monitoring. Successful, negative, inconclusive and unfinished investigations retain their separate tasks and evaluation limits.

**Academic review:** [working manuscript](00_thesis_writing_tracking/final_thesis_prep/LaTeX_Project/README.md) · [preserved 26 November review PDF](00_thesis_writing_tracking/review_submissions/2026-11-26/README.md) · [thesis-to-code map](docs/THESIS_CODE_MAP.md). The status recorded on 26 November was that Abstract and Chapters 1–4 had been submitted for review and Chapters 5–8 awaited their chapter-specific writing review. That status predates later source edits; submitted snapshots remain separate from the evolving manuscript.

## Objective and research journey

The [original exposé](implementations/general/docs/thesis/source_documents/MA_Exposé_Ravaliya_Parth.pdf), §3, proposed process-aware multimodal anomaly detection in robotic welding. Its questions concern **SQ1** representation components, **SQ2** unimodal/fusion comparisons, **SQ3** missing/degraded modalities, and **SQ4** evaluation beyond accuracy, including interpretability, modularity and practical use.

The work expanded to gear-condition proxies, robotic action outcomes and milling intervals. Target validity, modality correspondence and evaluation eligibility determined which studies could proceed. The [chronology](00_thesis_writing_tracking/scientific_cross_mapping_20261125/RESEARCH_CHRONOLOGY.md) preserves Intel Welding, PADERBORN and REBOOT investigations with failed or unresolved prerequisites. PHM's supervision and evaluation limitations helped motivate REASSEMBLE; the records do not establish a deliberately designed negative control.

## Methodology

The [literature review](00_thesis_writing_tracking/final_thesis_prep/LaTeX_Project/chapters/02_literature_review.tex) derives **R1** target validity and modality correspondence; **R2** representation suitability under explicit fitting conditions; **R3** incremental fusion value under comparable conditions; **R4** reliability-aware comparison; and **R5** methodological validity and bounded cross-dataset interpretation.

Comparisons cover engineered sensor features, temporal encoders, pretrained visual representations, distinct fine-tuning regimes, conventional references, feature fusion and probability/logit fusion. Study-specific grouped partitions, training-side selection/calibration, mandatory out-of-fold gates, saved predictions and uncertainty bound the evidence. Separately fitting an architecture on several datasets is not zero-shot generalization; completed-action classification is not online early warning.

## Empirical findings

These summaries are REPORTED from the linked study records; independent PHM saved-result checks are identified in its verification document. No universally superior fusion architecture is established.

| Thesis location | Finding and boundary |
|---|---|
| Chapter 5 — [PHM2026](implementations/PHM2026/README.md) | Principal LOEO sensor-group fusion did not establish improvement over the training-mean reference. Photographic targets remain proxies, not validated physical damage. [Traceability and verification](implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md). |
| Chapter 6 — [REASSEMBLE](implementations/REASSEMBLE/README.md) | Core static F2 added value over the sensor reference; tested gates did not establish clean or prescribed reliability-aware superiority. Core, extensions and later CNN studies retain separate protocols. |
| Chapter 7 — [MSM](implementations/MSM/README.md) | The completed primary three-seed comparison reports stronger sensor performance than tested fusion models; the stricter DOWN-only sensitivity failed its support gate. |
| Chapter 8 — [ViFailback](implementations/VIFAILBACK/README.md) | Frozen/donor results and limited full-CNN/pilot assessments are available. Matched full-CNN comparisons remain inconclusive; researcher-stopped fits are unfinished, not negative results. |
| Appendix H — [HANDOVER](implementations/HANDOVER/README.md) | Unimodal/fixed-averaging assessments are available. Missing participant identities blocked mandatory participant-safe OOF fitting for learned fusion. |

## Navigation and access

Follow the [thesis-to-code map](docs/THESIS_CODE_MAP.md) from chapter sections to implementation, configuration, evaluation and results. [Appendix F](00_thesis_writing_tracking/final_thesis_prep/LaTeX_Project/appendices/F_reproducibility.tex) remains the comprehensive evidence register. The [repository map](REPO_MAP.md) locates manuscript history, [scientific verification](00_thesis_writing_tracking/scientific_cross_mapping_20261125/README.md), dataset implementations and cross-study synthesis.

Raw datasets, large checkpoints/caches and copyright-restricted publications are excluded from the proposed review publication; existing tracked assets still require review. [Dataset guides](implementations/README.md) link source/version records, native locations and acquisition requirements; PHM has [recovery instructions](implementations/PHM2026/docs/RAW_DATA_RECOVERY.md). Obtain external resources under their official access terms. Historical paths/endpoints and payload availability require checking. The [consolidation/publication records](00_thesis_writing_tracking/consolidation_20261126/) identify retained hashes, exclusions and pending permissions.

The eleven groups covered by the researcher-approved location exception are now physically consolidated under `implementations/`. The [relocation receipt](implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md) records their destinations, file-identity checks and repairs. Frozen source, configurations and saved results retain their identities; historical manifests keep their original path names. Direct frozen-study commands require an explicit relocation context, and [remaining legacy execution-path limits](implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/vifailback_adapter/LEGACY_CONSUMER_LIMITS.md) are documented. These path checks do not reproduce experiments or authorize resuming stopped work.

Dependencies: [pyproject.toml](pyproject.toml), [requirements.txt](requirements.txt). Before execution, read [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md). Historical commands do not authorize reruns; this navigation does not amend the PHM-centred written scope. [License](LICENSE).
