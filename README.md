# pi-multimodal-ad

Master’s thesis workspace for visual and numerical sensor representations, multimodal fusion and missing/degraded-modality evaluation.

Start with **[Datasets and research support](implementations/README.md)**. Every dataset has a guide linking its inputs and labels, protocols, model implementation, saved assessment and reports.

- [Cross-dataset comparisons](implementations/cross_dataset/README.md)
- [Thesis and repository support](implementations/general/README.md)
- [Complete repository map](REPO_MAP.md)
- [VS Code implementations workspace](.vscode/thesis.code-workspace)

## Reuse and evidence

Data and frozen experiments retain their original identities and paths. Raw inputs, checkpoints, negative results and incomplete work remain preserved. See each study’s protocol and actual fit records before drawing scientific conclusions. Proxy targets are not physical ground truth; independent dataset-specific fitting is not zero-shot generalization.

The post-report organization phase consolidates the shared REASSEMBLE source and repairs package visibility. It does not rerun models or validate every historical command. The [phase record](implementations/general/docs/repository_history/post_report_cleanup_20261124/STATUS.json) reports checks actually performed and any remaining source/configuration path issues. Dependencies remain in [pyproject.toml](pyproject.toml) and [requirements.txt](requirements.txt); no installation was performed by this phase.

Read [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md) before changing experiments or data. Protected identities include gtc-data-experiment/ and data/Full Dataset/ even when absent locally. Historical PHM EDA remains protected. The [REASSEMBLE cache-retention record](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md) governs historical cache availability.

[License](LICENSE)
