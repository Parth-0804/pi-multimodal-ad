# Consolidation validation — 26 November 2026

**Preservation and scoped source checks passed. Compilation is unavailable;
17 pre-existing implementation links remain unresolved.** These limits are not
reported as a successful complete build or experiment reproduction.

## Preservation

- All 2,601 moved-package file hashes matched immediately after relocation.
  The final sweep found only the approved top-level README navigation banner
  changed; its original is retained as `cross_mapping_README_before.md`.
  Every file inside `applied_revision_01/`, including historical manifests,
  source snapshots, saved outputs, ZIPs and build caches, remains byte-identical.
- All 56 November 20 baseline file hashes match the old canonical tree.
  The duplicate was removed only after complete tree equality.
- All 97 promoted non-build files initially matched the latest snapshot.
  Current approved changes are identified by the
  [99-file source manifest](canonical_source_manifest.json).
- The Abstract and all ten empirical/discussion chapter source files remain
  byte-identical to the promoted snapshot. No chapter was rewritten.
- The submitted 71-page PDF remains
  `24462fb81165749b50634a04abc4770caf5ae8c828997cb0657bc1bcd37ff062`
  (SHA-256); only its README's relocated links changed.
- Existing E001–E123 source-index fields and identities remain unchanged.
  E124–E133 add missing PHM resources without replacing old evidence IDs.

## Manuscript and path checks

Static inspection of 32 active TeX files found 111 bibliography keys, 108 distinct
cited keys, 82 labels and 86 literal input/figure/bibliography references. No
missing citation keys, cross-reference labels, literal files or evidence IDs were
found. Static inspection does not evaluate conditional TeX expansion, Biber
formatting, PDF hyperlinks or rendered layout.

`main.tex`, `review.tex`, `manav_review.tex` and `chapter-preview.tex` retain their
source entry points. The new footnote file is not input anywhere. Source review
of the macros confirmed that ordinary `\ev` notes remain disabled by default,
and inline `\EvidenceRef` links keep their Appendix F destinations. Explicit
`\ev*` snippets and Appendix F URL cells use external links. New Appendix F rows
can change appendix pagination; they require a build before publication.

The existing `latexmk`, `xelatex`, `biber`, `pdftotext` and `pdftoppm` tools were
not found on PATH. The retained records' `/tmp/thesis_tex_20261125` kit is absent.
Common local installation locations did not provide an alternative. No dependency
was installed, no manuscript was compiled, no figure was regenerated and no new
PDF is claimed. Earlier successful builds remain attributed to their original
receipts.

The F2 script's `parents[2]` and ViFailback checker’s `parents[4]` still resolve
the repository root after the same-depth move. The canonical draft-figure script
already finds the repository by `pyproject.toml`; no code repair was necessary.
Four relevant Python files passed AST parsing. Historical verification scripts
were not rerun into their existing outputs. Thirty-two canonical Markdown links
now reach retained historical artifacts/reference records; original historical
Markdown and manifests remain unchanged.

## Implementation symlinks

Metadata-only traversal checked 86 symlinks under `src/` and `implementations/`:
69 resolve; 17 do not. All four root package compatibility links resolve.
The unresolved set is one MSM raw-dataset pointer and 16 REASSEMBLE walkthrough
pointers to old root `runs/reassemble/...` locations. Fourteen are tracked and
have exactly the same targets as the pre-consolidation HEAD; three prediction
links are untracked/ignored local pointers. None was edited or relocated in
this task. Exact paths/targets are in [validation.json](validation.json).
Do not infer absence of all corresponding evidence from a stale walkthrough link;
use current dataset guides and study records. Repairing protected/raw pointers or
historical walkthrough artifacts is outside this thesis relocation's scope.

## Published links and numerical evidence

All 21 distinct prepared GitHub file links were read without authentication,
returned HTTP 200 and matched current local bytes at published browsing commit
`e2037412036c5bbfc01fb2323215a37ef0b2e090`. Line ranges were checked; two proposed
endpoints were corrected to the actual file endings (LateFusion 119, PatchTST267).
The repository API reports `private: false`, default branch `main`. This proves
public access to the checked resources, not that new local files are published.
The [link receipt](github_permalink_validation.json) preserves each check.

The [PHM verification receipt](../../implementations/PHM2026/docs/studies/THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json)
independently reconstructs 20 v3 run targets from 480 tooth rows and checks the
73-row saved comparison, including its non-LOEO image subset. Target aggregation
matches within `8.88e-16`; saved MAE/RMSE and 10,000-draw bootstrap match within
`1e-12`. No training, inference, image processing or new fitting was performed.
Observed fusion-minus-mean MAE is +0.019629384; its stored bootstrap mean is a
separate statistic. The 95% paired interval spans zero and does not establish
equivalence. The detailed PHM map preserves the E027 correction, source-lineage
gaps and the separate supplementary preprocessing issue.

## Publication checks and limits

The [publication manifest](PUBLICATION_MANIFEST.md) records exact candidates,
exclusions and manual review. Nine exact evidence exceptions and 14 representative
protected/excluded paths passed ignore checks. Full copyright/confidentiality or
secret clearance is not claimed. Automatic approval review rejected the broader
ZIP-hashing command; bounded member checks and recorded hashes were used instead.
Historical source/package hashes verified during migration retain that separate
scope and provenance.

Final Markdown links, Git status and whitespace/diff summaries are recorded in
`final_checks.json`. No files were staged, committed, pushed or tagged; repository
access permissions were not changed.
