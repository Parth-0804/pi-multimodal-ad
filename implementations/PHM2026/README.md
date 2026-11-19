# PHM2026

Gear-condition and image-derived proxy-target studies using photos and vibration measurements.

Image-derived targets are provisional supervision, not independently validated physical damage. The canonical selection remains EXP-A Runs 1–5, EXP-B Runs 1–7 and EXP-F Runs 1–8. The protected initial EDA retains its original location.

[Source](src/phm2026) · [Scripts](scripts) · [Dataset configuration](dataset_config.yaml) · [Experiment configurations](../../configs/experiments) · [Tests](tests) · [Walkthrough](walkthrough/README.md)

Implementation files are stored here. Original code paths remain relative symlinks
for compatibility; native inputs and saved study evidence retain their original locations.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](../../docs/phm2026/RAW_DATA_RECOVERY.md) | Raw-source identity, availability and recovery requirements; no restoration is performed by this index. |
| 02 | [Labels and targets](src/phm2026/targets) | Proxy-target implementation; version history is linked below. |
| 03 | [Processed inputs](src/phm2026/features) | Feature extraction; preprocessing implementation is linked below. |
| 04 | [Experiment protocol](dataset_config.yaml) | Canonical selection; use each experiment configuration and run snapshot for its fitting protocol. |
| 05 | [Models and training](src/phm2026/models) | RT-DETR/PatchTST implementations; training entry points are linked below. |
| 06 | [Evaluation results](../../docs/thesis/RUN_INDEX.md) | Run index pointing to the separate historical evaluation collections. |
| 07 | [Robustness and claim scope](../../docs/thesis/FINAL_CLAIM_MATRIX.md) | Use the claim matrix and source protocols to determine which robustness claims are supported. |
| 08 | [Examples and EDA](../../experiments/exp_a_initial_eda_r1_r3_r5/EXPERIMENT_NOTES.md) | Protected historical lifecycle EDA; preserve its narrower study scope. |
| 09 | [Reports and reproducibility](../../docs/thesis/FINAL_THESIS_REPRODUCIBILITY.md) | Cross-study thesis evidence and reproduction boundaries; PHM-specific records remain separately identified. |

## Related work

- [Target-version ledger](../../docs/thesis/TARGET_VERSION_LEDGER.md)
- [Preprocessing](src/phm2026/preprocessing)
- [Training entry points](scripts/training)
- [Evaluation entry points](scripts/results)
- [Fusion implementation](src/phm2026/fusion)
- [Raw-retirement evidence](artifacts/PHM_RAW_RETIREMENT_REPORT.md)
- [Supplementary raw-vibration study](../../docs/thesis/RAW_VIB_20260927T095726Z.md)
- [Paderborn study record](../../docs/thesis/ARCH_VAL_PB_20260926T224859Z.md)
- [Paderborn utilities](../general/scripts/paderborn)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
