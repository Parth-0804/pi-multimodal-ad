# INTEL_WELDING

Historical intended-weld-condition research and dataset foundation audits.

The foundation review reports NO-GO for model comparison because scientific gates failed. Intended-condition labels are not verified physical-defect labels. The implemented audit scripts and historical code remain available; namespace placeholders are not trained models.

[Implemented audit scripts](scripts) · [Configurations](configs) · [Tests](tests) · [Namespace description](src/intel_welding/README.md) · [Historical workspace](../../archive/legacy_intel_welding_dataset/README.md)

Implementation files are stored here. Original code paths remain relative symlinks
for compatibility; native inputs and saved study evidence retain their original locations.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](artifacts/audits/GATE_0_DATA_ACCESS.md) | Bounded local-source access record; historical native-root identity remains protected. |
| 02 | [Labels and alignment](artifacts/audits) | Intended labels, session confounds, missingness and alignment findings. |
| 03 | [Processed inputs](scripts/04_foundations.py) | Structural foundation-audit implementation; not evidence of encoder feature extraction. |
| 04 | [Experiment protocol](../../docs/intel_welding/FOUNDATION_PROTOCOL_ADDENDUM.md) | Holdout incident, grouping corrections and stopping requirements. |
| 05 | Models and training | No admissible new model comparison is established by the foundation review; see the results review. |
| 06 | [Evaluation evidence](../../docs/intel_welding/RESULTS_REVIEW.md) | Audit findings and the invalidated holdout; no untouched-test result is implied. |
| 07 | Robustness | The foundation review records that model robustness was not evaluated. |
| 08 | [Examples and inspection](artifacts) | Existing audit/inspection artifacts; inspect their provenance before use. |
| 09 | [Reports and gates](artifacts/audits/PHASE_1_GATE_REPORT.md) | Authoritative failed-gate and eligibility record for this audit. |

## Related work

- [Research contract](../../docs/intel_welding/research_contract.md)
- [Namespace source](src/intel_welding)
- [Foundation runbook](../../docs/intel_welding/FOUNDATION_RUNBOOK.md)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
