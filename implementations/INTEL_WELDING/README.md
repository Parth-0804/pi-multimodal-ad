# INTEL_WELDING

Historical intended-weld-condition research and dataset foundation audits.
Intended-condition labels are not verified physical-defect labels. The
[results review](docs/RESULTS_REVIEW.md) records failed scientific gates and
limitations; namespace placeholders are not evaluated models.

| Part | Location |
|---|---|
| Namespace and scope | [src/intel_welding](src/intel_welding/README.md) |
| Implemented audits | [scripts](scripts) |
| Configuration | [configs](configs) |
| Checks | [tests](tests) |
| Historical study | [experiments/legacy](experiments/legacy/README.md) |
| Saved evidence | [results/artifacts](results/artifacts), [runs](results/runs) |
| Protocols and decisions | [docs](docs), [research contract](docs/research_contract.md), [protocol addendum](docs/FOUNDATION_PROTOCOL_ADDENDUM.md) |

The protected native-root identity `data/Full Dataset/**` is unchanged. Recovery
of historical inventories or predictions would support an exposure audit; it
would not recreate an untouched test sample. Follow the study's evidence and
eligibility boundaries before interpreting any model output.

Old source aliases were removed. Source-path and packaging updates remain
unfinished; use the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
when reading historical paths.

## Thesis and evidence

Original application and Appendix G research chronology; existing evidence E018–E019 and E120. The later [foundation review](docs/RESULTS_REVIEW.md) is a NO-GO before new model training because of target, grouping, holdout and support limitations. It does not establish absence of unimodal signal or failure of a trained fusion architecture. The [legacy study](experiments/legacy/README.md) remains a separate historical investigation.

The [research contract](docs/research_contract.md), [foundation configuration](configs/foundations.json), [audit scripts](scripts/) and retained result manifests supply the dataset/input identities, preprocessing probes and decision procedure. See the [thesis-to-code map](../../docs/THESIS_CODE_MAP.md) for current browsing paths and the limits of historical source correspondence.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
