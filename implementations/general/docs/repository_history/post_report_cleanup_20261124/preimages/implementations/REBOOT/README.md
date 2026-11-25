# REBOOT

Dataset qualification, annotation audits, alignment and visual-observability
feasibility. These records describe feasibility investigations, not a trained
model or predictive-performance evaluation.

| Part | Location |
|---|---|
| Implementation | [src](src) |
| Checks | [tests](tests) |
| Source and version audit | [results/00_dataset_overview](results/00_dataset_overview) |
| Labels and annotations | [results/02_labels_and_annotations](results/02_labels_and_annotations) |
| Video/state alignment | [results/03_video_sensor_alignment](results/03_video_sensor_alignment) |
| Visual review | [results/04_visual_failure_review](results/04_visual_failure_review) |
| Architecture feasibility | [results/05_architecture_compatibility](results/05_architecture_compatibility) |
| Evaluation feasibility | [results/06_evaluation_feasibility](results/06_evaluation_feasibility) |
| Scientific decision | [REBOOT_RESEARCH_DECISION.md](results/07_research_decision/REBOOT_RESEARCH_DECISION.md) |
| Examples and EDA | [results/08_visual_examples_and_eda](results/08_visual_examples_and_eda) |
| Workspace documentation | [docs/WORKSPACE.md](docs/WORKSPACE.md) |

Native inputs remain at `REBOOT/01_raw_dataset/`. Source and investigation
evidence under [REBOOT/runs](../../REBOOT/runs) also retains its original path.
The research decision governs further work; feasibility does not establish
successful fusion or robustness.

Old source aliases were removed. Source-path and packaging updates remain
unfinished; use the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
for historical paths.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
