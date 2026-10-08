# Thesis documentation continuation

Completed the user’s documentation tasks 1, 2 and 5. Stop after documentation; do not start training, downloads or figure regeneration from this handoff.

Run: `runs/thesis/documentation/20260928T025444Z`.
Documentation-start HEAD: `8d4e7a9378cb51ffc3cd7b9be1e2785efc02d792`.
Build config: `artifacts/thesis/documentation_build_config.json`.
Generator: `scripts/thesis/build_final_documentation.py`.
Exact request retained in the run as `user_documentation_request.txt`.

## Delivered

- `docs/thesis/EXPOSE_TO_FINAL_THESIS_MATRIX.md`: 28 correspondence rows, source-qualified intentions, deviations, SQ answerability and useful supervisor acknowledgement.
- `artifacts/thesis/EXPOSE_COMPLIANCE_SUMMARY.json`: machine-readable matching rows.
- `docs/thesis/FINAL_CLAIM_MATRIX.md`: 34 claims, current/exploratory/historical/retired status, exact safe sentences, 5 abstract and 8 conclusion candidates, complementarity by action and failure subset.
- `artifacts/thesis/final_claim_matrix.csv`: matching ledger. This exists locally but the existing global CSV ignore rule excludes it from ordinary Git staging. Preserve it explicitly in any export; no ignore rule was changed.
- `docs/thesis/FINAL_THESIS_REPRODUCIBILITY.md`: 18 headline provenance chains and status per chain.
- `artifacts/thesis/FINAL_REPRODUCIBILITY_AUDIT.json`: source identities, validation details, environment, Git state, gaps and headline statuses.

Final status: **THESIS REPRODUCIBILITY PACKAGE READY WITH DOCUMENTED GAPS**.

## Checks and scientific qualifications

Documentation validation and output SHA256s are in the run’s `documentation_validation.json`; input identities are in `source_manifest.json`. All referenced paths/configs, PHM output/input manifests, retained PHM MAE/RMSE and v3 labels, core REASSEMBLE AP/AUROC, split membership, stacker train/test indices, figure/script paths, dependency and whitespace checks passed. Completed core manifests and protected metadata checks passed. Source hashes were rechecked after writing the documents. No independent retraining or new bootstrap was performed.

The approved exposé and external PHM master Reasoning Record were not found. The user answered “idk look for it.” Accessible document filenames, designated attachments, repository evidence and Git path history were searched; exclusions and matches are retained in `original_document_search.json`. Use `docs/intel_welding/research_contract.md` only as an explicitly provisional RQ proxy. Do not claim original compliance or supervisor approval has been verified.

Historical records were preserved. New documentation makes these distinctions explicit:

- PHM’s stored paired ΔMAE is the mean of bootstrap differences, not the direct empirical difference of displayed MAEs.
- The PHM LOEO resolved config contains stale v2/fixed-split descriptive fields; verified source artifacts and retained labels are v3, and the evaluator applies LOEO.
- REASSEMBLE split file SHA256 and canonical-content SHA256 differ by serialization; the folds match.
- Core RT-DETR feature extraction uses `rt_detr_resnet` through `.model.backbone.model`; its Transformer encoder/decoder is not used. The visual SQ1 scope is therefore partial, despite useful visual features.
- Retired PHM raw archives require authorized recovery for extraction reproduction. Synthetic-control and PHM sensor-fusion per-run predictions/checkpoints were not identified; aggregate evidence is retained but independent numerical reproduction requires training.

## Separate ongoing work

The previously authorized additional-improvements queue remains separate under `runs/reassemble/additional_improvements_executed/20260928T000346Z`. This documentation task did not change, restart or stop those jobs. Completed primary temporal-visual, longer-budget sensor and static-anchored adaptation comparisons are labelled exploratory in the ledger. Fine-tuning, hybrid and repeated-corruption refinements are not certified complete by this freeze. Consult that run’s own live status and continuation files before any later experiment work.

## Next action only if requested

Locate the actual approved exposé and external master, then reconcile the provisional rows in a new versioned documentation snapshot. Do not edit the external master without authorization. For corrections to this newly created documentation package only, the generator supports explicit same-run `--resume`; its owner record prevents an accidental overwrite of unrelated outputs. New completed experiment results require a new snapshot and claim review, not silent changes to historical conclusions.

No documentation commit was made. Existing unrelated untracked files and live experiment status changes were preserved.
