# PHM2026

Gear-condition research using photos and vibration. Image-derived targets are proxy supervision, not independently validated physical damage labels.

| Stage | Location |
|---|---|
| 01 — Data and targets | [Data configuration](configs/dataset.yaml); [Target-version ledger](docs/studies/TARGET_VERSION_LEDGER.md) |
| 02 — Verification and preprocessing | [Data contracts and preprocessing](src/phm2026); [Derived vibration features](results/processed/raw_vibration) |
| 03 — Protocols and experiments | [Study workspaces](experiments); [Experiment configurations](configs/experiments) |
| 04 — Models and training | [Model implementations](src/phm2026/models); [Training entry points](scripts/training) |
| 05 — Results and limitations | [Saved runs](results/runs); [Study reports](docs/studies) |
| 06 — Recovery and history | [Raw-data recovery](docs/RAW_DATA_RECOVERY.md); [Research history](docs/research_history) |

[Source](src) · [Scripts](scripts) · [Configurations](configs) · [Tests](tests) · [Documentation](docs)

Canonical selection remains EXP-A Runs 1–5, EXP-B Runs 1–7 and EXP-F Runs 1–8. The protected initial EDA remains at `experiments/exp_a_initial_eda_r1_r3_r5/` in the repository root. Raw-retirement records do not authorize another deletion or restoration.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
