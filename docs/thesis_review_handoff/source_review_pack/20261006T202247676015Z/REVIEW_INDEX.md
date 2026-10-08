# Primary source review index

Collected UTC: 2026-10-06T20:22:47.676032+00:00. Repository: /home/student/Master_Thesis_WS/pi-multimodal-ad. HEAD: `8d4e7a9378cb51ffc3cd7b9be1e2785efc02d792`. Pre-existing status: 209 staged, 105 unstaged and 763 untracked entries (categories can overlap). HEAD does not identify uncommitted code. Full read-only status was retained privately for comparison; its SHA256 is `c6c7ceddf9693276f3ad44743879d290adaeeb7b318ba38e94db38a3f519483a`.

This is a primary-file export, not another thesis summary or a runnable/full reproduction environment. 49 explicitly requested files are accounted for. 89 existing files are copied under `files/` with complete repository-relative paths; 9 exact recorded Git source objects are under `historical_sources/git/<recorded_revision>/<original_repository_path>`. The exact file inventory, reasons, sizes, hashes and exclusions are in [EXPORT_MANIFEST.csv](EXPORT_MANIFEST.csv). Total copied primary/historical bytes: 5,741,228. The three new export documents are additional archive members, not scientific evidence.

## Read the actual logic in this order

PHM: `image_damage.py` target geometry/view selection → `sensor_minutes.py` features → `timeseries.py` training-fit normalization/masks → `models/patchtst/model.py` and `fusion/late_fusion.py` → `scripts/phm2026/results/loeo_evaluation.py` fold overrides/refits → `evaluation/regression.py` and saved `loeo_predictions.parquet`. The separate `monotonic.py`/`rescore_monotonic.py` path is an evaluation-label-fitted diagnostic, not deployable recalibration. All listed source paths are in `files/`; exact canonical paths are in the manifest.

REASSEMBLE: `alignment.py` / `section1_features.py` cohort/representations → `splits.py` / `section1_models.py` recording splits, fitting/calibration → `section1b.py` strict branch OOF and F2 stacking → `section2_data.py` / `section2.py` / `section2_models.py` original gate scope → `section1_report.py`, added `section1b_report.py` / `section2_report.py`. Then inspect the independent `scripts/thesis/final_validity_audit/metrics.py`, `numerical.py` and added `common.py`. Selected tests are copied for inspection only; none was run.

## Config and scope discrepancies stay visible

- PHM LOEO `config/resolved_config.yaml` retains its documented v2/fixed-split metadata. The entry point overrides evaluation folds; the retained target/default files and original small numerical summary are supplied separately. No labels, metadata or formulas were repaired while copying.
- REASSEMBLE current and run-specific JSON comparisons: configs/reassemble/section1.json versus runs/reassemble/20260927T154732Z-section1/config.json: byte-identical; configs/reassemble/section1b.json versus runs/reassemble/20260927T175336Z-section1b/config.json: byte-identical; configs/reassemble/section2.json versus runs/reassemble/20260927T192852Z-section2/config.json: byte-identical.
- Partition-file byte SHA256 and the embedded unsigned sorted-JSON partition hash are distinct identities, not silently reconciled. Both original fixed partition files are copied.
- The final `SCOPE_DECISION.json` is an administrative reference: Task1 was discontinued/excluded. It does not authorize a supervisor, worker or any research execution.
- The copied full pytest log records an earlier execution. Copying it or tests supplies no new test success or scientific validation.

## Producing-source identity and gaps

`VERIFIED` in the manifest means an explicit producing-source hash match, a scoped recorded-clean-revision/path comparison, or an existing recorded artifact/config identity match as stated in that row. `DIFFERENT` preserves a known byte mismatch; `NOT_VERIFIED` refuses to infer producing identity from a filename, later audit hash or HEAD; `NOT_APPLICABLE` marks tests/references that are not producing implementations. Every copy additionally has its own source/copy SHA256 agreement.

REASSEMBLE sources named in Section1/1B/2 `source_sha256` signatures match those signatures. PHM tracked target/feature/model/metric objects are compared only at exact recorded clean revisions and paths established by the migration CSV. A record of `dirty=false` with `untracked_present=true` is not a complete source freeze. In particular, the original LOEO script and the monotonic module/script are absent at their recorded Git revision/path. Their current canonical files are included, but no original dirty/untracked source substitute is invented.

Current scientific-source producing matches still NOT_VERIFIED:
- [files/scripts/phm2026/results/loeo_evaluation.py](files/scripts/phm2026/results/loeo_evaluation.py)
- [files/src/phm2026/evaluation/monotonic.py](files/src/phm2026/evaluation/monotonic.py)
- [files/scripts/phm2026/results/rescore_monotonic.py](files/scripts/phm2026/results/rescore_monotonic.py)
- [files/src/reassemble/alignment.py](files/src/reassemble/alignment.py)
- [files/src/reassemble/splits.py](files/src/reassemble/splits.py)
- [files/scripts/thesis/final_validity_audit/metrics.py](files/scripts/thesis/final_validity_audit/metrics.py)
- [files/scripts/thesis/final_validity_audit/numerical.py](files/scripts/thesis/final_validity_audit/numerical.py)
- [files/scripts/thesis/final_validity_audit/common.py](files/scripts/thesis/final_validity_audit/common.py)

Known current-versus-producing byte differences:
- [files/src/phm2026/fusion/late_fusion.py](files/src/phm2026/fusion/late_fusion.py)

Exact historical object gaps:
- `c699cbd9727ed33f34f1785172db163eb74b071f:scripts/results/loeo_evaluation.py` — Exact recorded revision/path lacks this Git object; producing script/module may have been untracked. No dirty/source snapshot match is asserted.
- `246024367e8b8a0b2463274115d760fb579ef50c:src/pi_multimodal_ad/evaluation/monotonic.py` — Exact recorded revision/path lacks this Git object; producing script/module may have been untracked. No dirty/source snapshot match is asserted.
- `246024367e8b8a0b2463274115d760fb579ef50c:scripts/results/rescore_monotonic.py` — Exact recorded revision/path lacks this Git object; producing script/module may have been untracked. No dirty/source snapshot match is asserted.

## Identity-preserving retained predictions

Included existing compact prediction/identity subset: 14 files, 3,303,874 bytes, below the 10 MiB cap. No numerical arrays were loaded or recalculated. ZIP/NPY headers were inspected with standard-library tools only; no object/pickle dtypes are accepted. The Parquet files were copied unchanged, with format magic checked only.

`files/runs/reassemble/20260927T192852Z-section2/predictions/oof.npz` contains U1/U2/F2/F6 held-out probability and decision arrays plus y/fold. Section2 `collect` explicitly copies U1/U2/F2 from their original banks after label/fold equality assertions. The five Section2 `outer*.npz` carry F6 `test_rows`/y; the five Section1B `outer*.npz` carry F2 `test_rows`/`train_rows` and meta-training probability pairs. They accompany original F2 `oof.npz`, saved S1 keyed cohort, frozen splits and the independent keyed inventory cohort.

The authoritative identity relationship is the copied source writer/collector and `numerical.load_cohort`: it filters original inventory primary_task/dual_complete, verifies recording_id/segment_id and labels/boundaries by keyed merge, verifies saved cohort order, and associates row positions with frozen recording folds. It is not a join guessed from array length or a filename. Existing sealed manifest hashes identify the files. These establish a safe static review bundle; this export did **not** execute or independently revalidate the joins/numerical arrays. The original U1/U2 NPZ banks remain local because the included combined bank already preserves their scores and their originals contain unnecessary embeddings. No feature bank, model checkpoint, joblib, pickle or Torch payload is exported.

## Dependencies and fixtures

Only six essential directly imported local modules were added, each justified in the manifest. The ancestor PHM conftest is copied; selected tests generate synthetic cases within their own code/tmp_path, so no raw fixture payload is added. This is not a complete executable dependency closure.

Framework/third-party imports, not copied or imported here: PIL, cv2, h5py, matplotlib, numpy, pandas, pytest, scipy, sklearn, threadpoolctl, torch, transformers, yaml. Optional local configuration/provenance/plot/report plumbing remains in the repository: phm2026.reporting.common, phm2026.utils.artifacts, phm2026.utils.config, phm2026.utils.provenance. Framework implementations, nested helper imports and their environments are outside this first slice; no recursive repository bundling was performed.

## Approved originals and export-only boundary

Approved original exposé and current manuscript: **USER_HELD_OR_UNLOCATED**. Only obvious permitted repository thesis-document locations were checked (., docs, docs/thesis, thesis, manuscript, documents); no approved original was identified. Candidate filenames found: none. No home-directory/email/environment/private-state search was performed, and no supervisor acceptance was inferred.

No project imports, tests, --help routes, report generators, model loading, training/inference/evaluation, downloads/recovery, queues/supervisors/schedulers, dependency operations, adjudication, stage/commit/push/reset/checkout were executed. Only filesystem reads, read-only Git, standard-library hashes/copies/AST/header inspection and archive construction were used. See [EXPORT_CHECKS.md](EXPORT_CHECKS.md) for exact preservation scope and exclusions.
