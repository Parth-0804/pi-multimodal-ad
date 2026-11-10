# Handover official source information

Official [Zenodo record10708763](https://zenodo.org/records/10708763), DOI10.5281/zenodo.10708763, release **v1**. The record JSON, source-access receipt, exact official file URLs, acquisition UTC times, MD5 and SHA-256 checksums are saved in source_evidence. The sample passed both-robot video/timestamp/wrench/label gates before the complete train/validation/test archives were downloaded automatically. The sample is not an independent test set. Complete official archives remain preserved; only required RGB/timestamp/wrench/metadata members were extracted.

Associated publication: Thoduka et al., *A Multimodal Handover Failure Detection Dataset and Baselines*, ICRA2024, DOI10.1109/ICRA57147.2024.10610143. Author reference code is pinned to Git commit6665d7ec6a1ee724b62dc32a5dd5c2e1afc7f5ef at https://github.com/sthoduka/handover_failure_detection. Its nearest-raw-time resampling rule was reproduced exactly for every admitted trial. The supplied wrench_stats.json is preserved but never used as a globally fitted model normalizer.

The native release reports17 participants but supplies no participant-to-trial mapping in the archives, label/task metadata or inspected author code. Official split identities are kept unchanged; participant independence and participant-safe inner OOF are not invented. All learned F2/quality-fusion comparisons consequently remain blocked while the five permissible official-split baselines continue.

Active cohort and all model outputs: HANDOVER/experiments/common_support_v2. Earlier full-video audit files at the canonical stage root are historical evidence, not the evaluated cohort. See the explicit pre-score COMMON_SUPPORT_AMENDMENT.json for the horizon correction.
