# Publication-content review — 2026-11-26

The approved consolidation is local. **Nothing in this manifest authorizes staging, a commit, a push, a tag or an access change.** An ignore exception makes a file eligible for review; it does not establish that the file is published or that all redistribution requirements have been satisfied.

The [machine-readable manifest](publication_manifest.json) records exact paths, sizes, decisions, available SHA-256 identities, hash provenance, bounded inspection results and ignore-rule checks. It records the bounded content review at Git HEAD `7274a0ec3b163de1e3ca66a09e2a164693be7c75`, followed by a final local metadata/hash refresh of ordinary manuscript sources and the exact documentation candidates. The publication commit remains **UNKNOWN**. Any later edits need hash verification before staging; the hash refresh does not extend the earlier content-review or archive-inspection scope. Historical source and delivery identities remain in the [migration receipt](migration_receipt.json), rather than being replaced with current manuscript hashes.

## Include after final scoped review

- The sole [authoritative LaTeX project](../Thesis/LaTeX_Project/README.md), its bibliographies, selected figures and necessary source aids. The refreshed manifest inventories 99 files; 25 unselected figure-draft files are separately marked for optional publication review. They are not alternative manuscripts.
- The immutable [71-page academic-review snapshot and provenance](../review_submissions/2026-11-26/README.md). The researcher reports that the sent attachments were page extracts from this combined PDF. Do not reconstruct and label new extracts as the exact sent attachments.
- Professor-facing navigation, the [thesis-to-code map](../../docs/THESIS_CODE_MAP.md), relevant dataset guides, the scientific cross-mapping documents, verification scripts and compact reports.
- Historical baseline/source snapshots, revision explanations, original manifests, hashes and selected delivered PDFs within `scientific_cross_mapping_20261125/applied_revision_01/`, subject to the explicit exclusions and manual-review flags below. The complete package remains preserved locally, including material excluded from Git.
- Existing executed implementation/configuration/report paths identified by the thesis map. Existing publication and later browsing commits must remain distinct from experiment-producing source identities.

The JSON field `consolidation_documentation_candidates` individually lists the root README/REPO_MAP, tracking/Thesis/revision-pipeline guides, current manuscript state, scientific-cross-mapping README, all dataset/support guides and the following new PHM resources:

- [Chapter 5 investigation-to-code mapping](../../implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md).
- [Saved-evidence verification script](../../implementations/PHM2026/docs/studies/verify_thesis_saved_evidence.py).
- [Executed saved-evidence verification receipt](../../implementations/PHM2026/docs/studies/THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json).
- [Prepared implementation-link instructions](../Thesis/LaTeX_Project/implementation_links/README.md) and [Chapter 5 footnote source](../Thesis/LaTeX_Project/implementation_links/chapter05_footnotes.tex), individually inventoried within the authoritative project. These footnotes have not been inserted into Chapter 5.

The [consolidation receipt directory](.) is itself a publication candidate for task-specific migration, path repairs, evidence/publication links and final validation. Its README, VALIDATION document and final check/hash JSONs belong with the task receipts. It is referenced as a directory rather than recursively hashing this manifest and mutually referencing receipts.

The following nine exact exceptions were added to the [root ignore rules](../../.gitignore). All nine files were inspected as small text artifacts; CSV schemas and row counts were checked, and current SHA-256 hashes are recorded in the JSON manifest. No high-confidence secret, workstation-path or email pattern was found in these nine files. These checks do not certify scientific validity or legal clearance.

| Publication candidate | Bytes | Purpose and boundary |
|---|---:|---|
| [PHM LOEO predictions](../../implementations/PHM2026/results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv) | 5,261 | Saved predictions; 73 rows include the explicitly non-LOEO image subset. Preserve model and fold identities. |
| [PHM LOEO summary](../../implementations/PHM2026/results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_summary.csv) | 535 | Original compact numerical summary. |
| [PHM v3 run targets](../../implementations/PHM2026/results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/tables/run_damage_targets.csv) | 4,982 | Twenty photographic proxy targets; not independently validated physical damage labels. |
| [PHM v3 tooth targets](../../implementations/PHM2026/results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/tables/per_tooth_damage.csv) | 187,073 | 480 derived tooth records for aggregation verification; no image payloads. |
| [RAW-VIB L1 summary](../../implementations/PHM2026/results/processed/raw_vibration/l1_screen.json) | 1,847 | Preserve the failed diagnostic gate. |
| [RAW-VIB sector summary](../../implementations/PHM2026/results/processed/raw_vibration/sector_screen.json) | 5,297 | Supplementary diagnostic summary; feature arrays remain excluded. |
| [F2 fold metrics](../scientific_cross_mapping_20261125/f2_verification/fold_metrics.csv) | 817 | Existing five-fold verification output. |
| [Citation/PDF metadata](../Thesis/References/CITATION_PDFS.csv) | 26,982 | Bibliographic identity, source URLs and availability; no full text. |
| [PDF provenance metadata](../Thesis/References/PDF_PROVENANCE.csv) | 62,977 | Recorded reference-PDF identities and hashes; not redistribution permission. |

The RAW-VIB parent rule now excludes its contents instead of excluding the directory itself, so that only the two named JSON files can be admitted. All four existing feature/cache artifacts in that directory remain ignored. Global CSV and ZIP exclusions remain in force; no general result-directory or archive exception was added. The canonical manuscript's existing two table exceptions remain in its own `.gitignore`.

## Keep local and excluded

| Material | Treatment |
|---|---|
| Raw datasets, extracted source payloads, model weights/checkpoints, large numerical caches and environments | Preserve the existing exclusions. No payload or credential contents were opened by this review. |
| `Thesis/References/PDFs/` | All 90 third-party PDFs are explicitly ignored. Exact filenames and sizes, plus available recorded hashes for all 90, are listed in the JSON manifest. Rights to redistribute them have not been established. |
| Revision check `citation_review_ch01_ch02_20261126_01/root_pdf_texts/` | All 20 extracted literature full texts are ignored; retained locally without modification. |
| The same check's `metadata_inventory.json` | Exact exclusion: it embeds first-two-page literature extracts and author contact strings. Public citation metadata is supplied by the two CSVs above. |
| LaTeX auxiliary files and historical `checks/**/*_build/` directories | Ignore generated compilation products while preserving source snapshots and surrounding validation reports. |
| Historical rendered-page/preview directories | Ignore regenerable review images; preserve them locally and retain the review reports. Selected manuscript figures remain eligible. |
| All 15 thesis ZIP archives | Keep ignored pending explicit selection and rights/privacy review. Their exact names, sizes, member summaries and available recorded hashes are listed in the JSON manifest. |

No file was deleted, untracked or rewritten by this publication review. Adding ignore rules does not remove files already tracked in Git.

## Manual review before publication

**Historical ZIPs.** Central-directory metadata was inspected for all 15 thesis archives. No obvious credential/raw-payload/checkpoint filenames were found. A bounded sample of at most 20 text members of at most 250 KB per archive was inspected: 273 members, 4,497,165 bytes in total. No high-confidence secret, workstation-path or email pattern matched those selected members. Binary members and unselected text were not cleared. The November 20 release bundle contains manuscript PDFs and the original exposé, rather than a folder of downloaded literature PDFs, but this does not establish all embedded-figure rights. Keep the archives local until the specific publication selection is reviewed.

**Historical text and personal paths.** A bounded source/document scan covered 852 files and 21,319,295 bytes, excluding credential files, large files, raw payloads and build directories. It found no selected high-confidence credential patterns. It flagged workstation-path patterns in 26 files and contact strings in the excluded literature metadata inventory. Exact flagged paths appear under `manual_text_review` in the JSON manifest. Historical logs/manifests retain their bytes; review whether to omit them or prepare a separately identified public derivative. Do not silently sanitize the originals. Scholarly appraisals and quotation-audit records also need review of copied excerpts before public staging; a citation alone does not establish redistribution permission.

**Already tracked material.** Filename/size inspection identified 5,333 tracked JPG/PNG/JPEG files, including PHM imagery/overlays, REBOOT examples and protected historical EDA graphics. Dataset-specific rights, privacy and raw-versus-derived status require review. The manifest also lists 15 tracked files larger than 10 MB, including a 43.5 MB HANDOVER archive-member inventory, three 27.3 MB configuration inventories and compressed audit states. These were examined by metadata only. No automatic deletion, deduplication, untracking or Git-history rewrite was performed. No tracked sensitive-filename candidate was found; this is not a repository-wide secret scan.

## Retrieval, retention and stable links

- Literature: use DOI/source URLs in `CITATION_PDFS.csv`, lawful publisher/repository/library access and the recorded identities in `PDF_PROVENANCE.csv`. Reference PDFs stay in their local `Thesis/References/PDFs/` location.
- Datasets and pretrained resources: use the respective [implementation guides](../../implementations/README.md) and acquisition/retention records. The [PHM recovery guide](../../implementations/PHM2026/docs/RAW_DATA_RECOVERY.md) is a historical recovery procedure; provider access and any stale paths must be checked before separately authorized recovery. This manifest authorizes no download, restoration or raw archive scan.
- Historical ZIPs: retain the listed local paths. Migration-receipt hashes are attributed as recorded evidence, not newly computed here. No independent backup/recovery copy was verified by this publication review. The November 20 release ZIP has no archive SHA-256 available in the inspected records; its integrity field remains explicitly unavailable.
- Publication: review a scoped staging list, create an authorized content commit, generate links only to actual existing published commits, and record any subsequent link/build commit. An annotated academic-review tag may then freeze the reviewed state, only after explicit authorization. New local files do not yet have final GitHub permalinks.

## Validation and limits

The [published-permalink validation receipt](github_permalink_validation.json) records unauthenticated GitHub checks of all 21 distinct prepared URLs and their fragments, including remote/local byte identities and public repository metadata. Consult its finalized `links` array for the exact checked URL set. These are checks of existing published browsing sources; this task still has no publication commit. The final local refresh updated ordinary manuscript/document hashes only and did not repeat the earlier broad text inspection or any archive checks.

All 23 ignore checks passed: the nine exact candidates are visible, and 14 representative protected/excluded paths remain ignored. The exact ignore diff was reviewed. No training, inference, preprocessing or experimental fitting was performed. This is a bounded publication-content review, not a complete confidentiality, secrets, copyright or license clearance.

Automatic approval review rejected a command that would also have hashed every thesis ZIP in full, because full archive hashing was outside the interpreted bounded inspection scope. That command did not run. The review continued with central metadata, selected small members and existing recorded archive hashes; no new full-archive hash claim is made. Additional archive-wide verification would require separate authorization before publication of those archives.
