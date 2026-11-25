# PHM2026

Gear-condition research using photos and vibration measurements. Image-derived
targets are provisional supervision, not independently validated physical
damage. The canonical dataset selection remains EXP-A Runs 1–5, EXP-B Runs 1–7
and EXP-F Runs 1–8; see the [dataset configuration](configs/dataset.yaml).

| Part | Location |
|---|---|
| Implementation | [src/phm2026](src/phm2026) |
| Entry points | [scripts](scripts) |
| Raw-vibration and tooth-sector tools | [scripts/rawvib](scripts/rawvib) |
| Configuration | [configs](configs), [experiment configurations](configs/experiments) |
| Checks | [tests](tests) |
| Study workspaces | [experiments](experiments), [walkthrough](experiments/walkthrough/README.md) |
| Local inspection workspace | [Legacy blinded inspection](experiments/blind_inspection_legacy) (ignored by Git; derived images and blinded key) |
| Saved evidence | [results/runs](results/runs), [artifacts](results/artifacts), [superseded records](results/superseded) |
| Derived vibration features | [results/processed/raw_vibration](results/processed/raw_vibration) |
| Documentation | [docs](docs), [historical tutorials](docs/tutorials) |
| Historical study records | [docs/studies](docs/studies), [target-version ledger](docs/studies/TARGET_VERSION_LEDGER.md) |
| Research history | [Checkpoints and decisions](docs/research_history/checkpoints), [plans](docs/research_history/plans), [acquisition lessons](docs/research_history/LARGE_DATASET_ACQUISITION_BEST_PRACTICES.md) |

RT-DETR, PatchTST and fusion implementations retain their distinct experimental
roles. Use each study's target version, executed configuration and report;
earlier negative or provisional findings remain part of the evidence.

The study records include protocols, reports and their derived CSV/JSON
companions. Closing-study synthetic controls retain their separate evidence
role; interpret them with the [closing-study report](docs/studies/CLOSING_EXPERIMENTS.md).
The [latest consolidation record](../general/docs/repository_history/dataset_layout_cleanup.json)
maps the latest readable names; earlier relocation history is retained alongside it.

Raw-source identity and availability are documented in
[RAW_DATA_RECOVERY.md](docs/RAW_DATA_RECOVERY.md) and the
[retirement record](results/artifacts/PHM_RAW_RETIREMENT_REPORT.md). Those records
do not authorize restoration or another cleanup. The protected
[initial EDA](../../experiments/exp_a_initial_eda_r1_r3_r5) retains its original path.

Old source aliases were removed. Source-path and packaging updates are still
unfinished; the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
connects historical paths with this layout. Study evidence has not been rerun by
this reorganisation.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
