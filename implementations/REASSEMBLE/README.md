# REASSEMBLE

Retrospective completed-action failure classification, representation comparison and multimodal fusion.

The core study, exploratory extensions and later CNN/fusion comparisons are separate studies. Their protocols and run identities remain separate. Completed-action prediction does not establish online early warning.

[Source](src) · [Scripts](scripts) · [Configurations](configs) · [Tests](tests) · [Walkthrough](walkthrough/README.md)

This folder links to the existing workspace. Its implementation paths were retained
to protect the training job and its shared source dependencies during this reorganisation.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](src/inventory.py) | Acquisition/inventory implementation; input availability is documented in the audit records. |
| 02 | [Labels and alignment](src/alignment.py) | Alignment implementation; label/grouping evidence is under artifacts/reassemble/audits/. |
| 03 | [Processed inputs](src/section1_features.py) | Core representation extraction; separate studies retain their own feature paths. |
| 04 | [Experiment protocol](../../docs/reassemble) | Study contracts, section protocols and methodology corrections. |
| 05 | [Models and training](src/section1_models.py) | Unimodal definitions; fusion implementations are linked below. |
| 06 | [Evaluation results](evidence) | Versioned run artifacts, predictions and assessment outputs. |
| 07 | [Robustness](../../docs/reassemble/SECTION_3_CORRUPTION_PROTOCOL.md) | Original robustness protocol; reports retain missingness and synthetic-corruption limits. |
| 08 | [Examples and EDA](../../tutorials/EDA/REASSEMBLE_README.md) | Existing representation/data walkthrough. |
| 09 | [Reports and handoff](artifacts/reports/FINAL_REASSEMBLE_HANDOFF.md) | Core handoff; extensions have their own closure records. |

## Related work

- [Core fusion](src/section2_models.py)
- [Extension closure](artifacts/reports/ADDITIONAL_IMPROVEMENTS_STATUS.md)
- [Later experiments](../../00_experiments)
- [October feedback experiments](../../26.10.2026_feedback_experiments)
- [Bootstrap experiment workspace](../../parth_ws_bootstrap/00_experimentation)
- [CNN100 comparison](walkthrough/29102026_cnn100_static_sensor_f2_comparison)
- [Cache-retention record](../../docs/maintenance/REASSEMBLE_CACHE_RETENTION.md)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
