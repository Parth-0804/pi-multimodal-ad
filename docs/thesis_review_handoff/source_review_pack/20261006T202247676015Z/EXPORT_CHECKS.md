# Export checks

Collection began UTC 2026-10-06T20:22:47.676032+00:00; workspace /home/student/Master_Thesis_WS/pi-multimodal-ad; HEAD `8d4e7a9378cb51ffc3cd7b9be1e2785efc02d792`. New unique export directory: `docs/thesis_review_handoff/source_review_pack/20261006T202247676015Z`. No prior package was overwritten. No source/config/test/report/run/raw/index/status file was edited.

| Check | Result and scope |
|---|---|
| Explicit requested-file accounting | 49/49 file paths have manifest rows, including any missing/withheld files; the three permitted directory paths and two user-held originals also have rows. |
| Primary/historical copied files | 98 existing file/object copies; 5,741,228 bytes. Every additional source/config/test/evidence item has a rationale. |
| Source/copy bytes | SHA256 of each selected source/object matches its exported copy. Files are copied exactly; nothing is redacted and called byte-identical. |
| Source stability | Size, mtime_ns and SHA256 captured before copying, checked after each copy and checked across the collection. 0 concurrent changes detected; affected files, if any, are excluded from the safe archive and reported below. |
| Historical source identity | Exact recorded clean revisions/paths read with Git show; objects checked twice. Current code is kept separate from historical objects. No checkout or producing source invented. |
| Optional prediction subset | 3,303,874 bytes; cap 10,485,760 bytes. Existing arrays/keyed cohorts only, no new verified table. |
| NPZ safety | ZIP/NPY header metadata only; no object/pickle dtype, numerical loading, model payload deserialization or research code execution. |
| Parquet handling | Original bytes copied unchanged; PAR1 header/footer checked; no table conversion or metric calculation. |
| Git preservation | Read-only --no-optional-locks inspection: HEAD and staged entries unchanged; all pre-existing status entries unchanged, with only this export directory's new outputs added. |
| Pre-existing dirty state | Staged 209, unstaged 105, untracked 763 entries; exact status-byte SHA256 `c6c7ceddf9693276f3ad44743879d290adaeeb7b318ba38e94db38a3f519483a`. Full before/after records are kept privately under the task's /tmp verification location, not archived. |
| Forbidden actions | No project import/test/help or research workflow was called; no dependency or environment operation and no stage/commit/push/reset/clean/checkout. |

## Missing, withheld and inconsistent items

- **MISSING_RECORDED_GIT_OBJECT** `git:c699cbd9727ed33f34f1785172db163eb74b071f:scripts/results/loeo_evaluation.py`: Exact recorded revision/path lacks this Git object; producing script/module may have been untracked. No dirty/source snapshot match is asserted. Current file: scripts/phm2026/results/loeo_evaluation.py; authority: runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/provenance.json.
- **MISSING_RECORDED_GIT_OBJECT** `git:246024367e8b8a0b2463274115d760fb579ef50c:src/pi_multimodal_ad/evaluation/monotonic.py`: Exact recorded revision/path lacks this Git object; producing script/module may have been untracked. No dirty/source snapshot match is asserted. Current file: src/phm2026/evaluation/monotonic.py; authority: runs/phm2026_monotonic_rescoring/20260912T053108724500Z-c0b86e16/provenance.json.
- **MISSING_RECORDED_GIT_OBJECT** `git:246024367e8b8a0b2463274115d760fb579ef50c:scripts/results/rescore_monotonic.py`: Exact recorded revision/path lacks this Git object; producing script/module may have been untracked. No dirty/source snapshot match is asserted. Current file: scripts/phm2026/results/rescore_monotonic.py; authority: runs/phm2026_monotonic_rescoring/20260912T053108724500Z-c0b86e16/provenance.json.
- **USER_HELD_OR_UNLOCATED** `APPROVED_ORIGINAL_EXPOSE`: No approved original identified in obvious permitted repository thesis-document locations: ., docs, docs/thesis, thesis, manuscript, documents. No proxy, outline or task prompt is exported as the approved document; supervisor acceptance is not inferred.
- **USER_HELD_OR_UNLOCATED** `CURRENT_THESIS_MANUSCRIPT`: No approved original identified in obvious permitted repository thesis-document locations: ., docs, docs/thesis, thesis, manuscript, documents. No proxy, outline or task prompt is exported as the approved document; supervisor acceptance is not inferred.

## Limitations

No full raw-dataset integrity/payload audit, unrelated-process monitoring, dependency freeze inspection, test execution, independent prediction join, metrics/bootstrap recomputation or bitwise model retraining was performed. Textual safety checks apply only to selected files; credential/private-state locations were not searched. Frameworks and optional plumbing are not bundled. Missing original producing objects/untracked source are provenance gaps, not permission to repair code or reinterpret results.

The archive is built from the explicit COPIED_BYTE_IDENTICAL manifest export paths plus exactly EXPORT_MANIFEST.csv, REVIEW_INDEX.md and EXPORT_CHECKS.md. It excludes itself and any inconsistent/withheld item, raw data, environment internals, Git database, restricted human-review keys/identities, feature banks and checkpoints. The exporter verifies archive membership and each archived byte stream against the copies, then rechecks selected source and Git stability before reporting completion. The archive is not transmitted automatically.
