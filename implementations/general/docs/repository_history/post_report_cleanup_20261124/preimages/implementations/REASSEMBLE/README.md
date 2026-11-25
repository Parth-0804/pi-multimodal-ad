# REASSEMBLE

Retrospective completed-action failure classification, representation comparison
and multimodal fusion. The core study, extensions and later CNN comparisons
retain separate protocols and run identities. Completed-action classification
does not establish online early warning.

| Part | Location |
|---|---|
| Relocated implementation modules | [src/reassemble](src/reassemble) |
| Entry points | [scripts](scripts) |
| Configurations | [configs](configs) |
| Checks | [tests](tests) |
| Protocols and methodology | [docs](docs) |
| Core walkthrough | [experiments/core](experiments/core/README.md) |
| Additional studies | [experiments/additional](experiments/additional) |
| All named run records | [results/runs](results/runs) |
| Unimodal baselines | [unimodal_baselines_visual_sensor](results/runs/unimodal_baselines_visual_sensor) |
| Sensor controls and static F2 | [sensor_controls_f2_nested_stacking](results/runs/sensor_controls_f2_nested_stacking) |
| Fusion comparisons | [fusion_method_comparison](results/runs/fusion_method_comparison) |
| Missing/degraded-modality robustness | [missing_degraded_modality_robustness](results/runs/missing_degraded_modality_robustness) |
| Follow-up execution records | [Representation and robustness](results/runs/followup_exploratory_studies/representation_and_robustness_studies), [boundary-aware visual](results/runs/followup_exploratory_studies/boundary_aware_visual_study) |
| Audits and scientific reports | [results/artifacts/audits](results/artifacts/audits), [reports](results/artifacts/reports) |
| Human-review interface | [Builder](scripts/review_interface), [derived exports](results/human_review) |
| GPU pipeline audit | [experiments/gpu_pipeline_audit](experiments/gpu_pipeline_audit) |
| CNN seed-stability study reports | [Main reports](experiments/cnn_seed_stability/reports), [backbone comparison](experiments/cnn_seed_stability/backbone_comparison/reports), [full-CNN revision](experiments/cnn_seed_stability/full_cnn_revision/reports) |
| Assignment chronology | [docs/experiment_assignments](docs/experiment_assignments) |
| Git publication history | [docs/research_history/git_handoffs](docs/research_history/git_handoffs) |
| Phase-one source/configuration and fit references retained in place | [26102026_phase1_full_cnn_seed_stability](../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability) |
| Bootstrap studies retained in place | [parth_ws_bootstrap/00_experimentation](../../parth_ws_bootstrap/00_experimentation) |

Five shared files remain temporarily in [root src/reassemble](../../src/reassemble)
to protect live training dependencies: `__init__.py`, `alignment.py`,
`section1_features.py`, `section1_models.py` and `section2_models.py`, together
with their existing bytecode cache. Their relocation is deferred while
VIFAILBACK uses them.
There are no replacement old-path aliases. General workflow automation lives
under [general/research_workflow](../general/research_workflow).

Use the retained [core closure](results/artifacts/reports/REASSEMBLE_COMPLETION_STATUS.md)
and [extension closure](results/artifacts/reports/ADDITIONAL_IMPROVEMENTS_STATUS.md)
for their respective evidence scopes. Later studies have their own reports.
Before reusing historical caches, read the
[retention and recovery record](../../docs/maintenance/REASSEMBLE_CACHE_RETENTION.md).

Source-path and packaging updates remain unfinished. The source is temporarily
split between the dataset folder and the five retained shared files. The
[layout mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
connects readable run names to original IDs and paths; frozen manifests retain
their historical identities. This navigation does not establish current training
status or reproduce a result.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
