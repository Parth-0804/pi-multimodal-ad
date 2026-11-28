# REASSEMBLE

Retrospective completed-action failure classification using visual and numerical sensor representations. This is not online early warning.

| Stage | Location |
|---|---|
| 01 — Labels, alignment and protocols | [Methodology](docs); [Configurations](configs) |
| 02 — Representations and models | [Implementation](src/reassemble); [Core walkthrough](experiments/core/README.md) |
| 03 — Core training and fusion | [Unimodal baselines](results/runs/unimodal_baselines_visual_sensor); [Static F2 and sensor controls](results/runs/sensor_controls_f2_nested_stacking) |
| 04 — Further experiments | [Additional studies](experiments/additional); [CNN seed stability](experiments/cnn_seed_stability) |
| 05 — Assessment and robustness | [Fusion comparison](results/runs/fusion_method_comparison); [Missing/degraded modalities](results/runs/missing_degraded_modality_robustness) |
| 06 — Reports and completion | [Core closure](results/artifacts/reports/REASSEMBLE_COMPLETION_STATUS.md); [Extension closure](results/artifacts/reports/ADDITIONAL_IMPROVEMENTS_STATUS.md); [All scientific reports](results/artifacts/reports) |

[Source](src) · [Scripts](scripts) · [Configurations](configs) · [Tests](tests) · [Documentation](docs)

Core, extensions and later CNN studies retain distinct protocols, cohorts and completion boundaries. The source package now lives here. Root `src/reassemble` is a compatibility link preserving historical imports and source identities. The original [phase-one feedback workspace](experiments/cnn_seed_stability/phase1_feedback/) and [bootstrap workspace](experiments/bootstrap/) now live here; their frozen source, configurations, stop records and results retain their identities. Historical manifests retain original names.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Direct commands for relocated frozen studies require an explicit context as described in the [relocation activation guide](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/reassemble_adapter/README.md); consult the [relocation receipt](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md) for bounded checks and remaining dependencies. Historical commands retain their original paths. Navigation and source-identity checks do not reproduce models or authorize job resumption.

## Thesis and evidence

Evidence IDs below follow the researcher-requested 28 November renumbering. The [complete mapping](../../00_thesis_writing_tracking/final_thesis_prep/evidence_publication_20261128/manifest.json) relates them to the prior IDs retained in historical records.

Chapter 6; current evidence E036–E065 and E110–E112/E120. The [final core handoff](results/artifacts/reports/FINAL_REASSEMBLE_HANDOFF.md) reports a bounded incremental F2 gain over the sensor reference, without establishing a clean or prescribed reliability-aware advantage for the tested gates. The [extension closure](results/artifacts/reports/ADDITIONAL_IMPROVEMENTS_STATUS.md), [encoder comparison](experiments/additional/rt_detr_encoder_comparison/README.md), [one-fold adaptive pilot](experiments/additional/adaptive_fusion_robustness/README.md) and [later CNN100 F2 study](experiments/core/cnn100_static_sensor_f2_comparison/README.md) retain separate cohorts and outcomes. Audio modelling failed its alignment prerequisite; it was not a negative predictive result.

The core handoff supplies dataset/label/recording scope; [protocols](docs/) and run manifests supply acquisition, preprocessing, fitting and assessment identities. The core RT-DETR-derived visual path executes frozen CNN maps, not detector encoder/decoder/box heads. Consult the [chapter map](../../docs/THESIS_CODE_MAP.md) for exact sources and evidence roles.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
