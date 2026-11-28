# Approved thesis consolidation — 26 November 2026

The canonical manuscript is [../Thesis/LaTeX_Project](../Thesis/LaTeX_Project/README.md).
The complete applied revision remains a historical snapshot, and the submitted
71-page review source remains unchanged. This phase made local organization,
documentation and evidence-navigation changes; nothing was staged or published.

| Record | Purpose |
| --- | --- |
| [Migration receipt](migration_receipt.json) | Exact old/new paths, pre-move hashes, complete baseline match and promotion inventory. |
| [Current source manifest](canonical_source_manifest.json) | Hashes for all 99 current manuscript source/support files, after approved navigation/macro changes. |
| [Validation](VALIDATION.md) and [machine-readable checks](validation.json) | Preservation, bibliography/reference/input checks, available tooling and symlink limits. |
| [Link repairs](active_link_repairs.json) | 32 canonical Markdown links redirected to retained historical build/reference evidence. |
| [GitHub checks](github_permalink_validation.json) | 21 published browsing resources checked by unauthenticated access, local/remote digest equality and line-range bounds. |
| [Evidence publication index](evidence_publication_links.json) | Current paths/hashes, browsing/publication commits, historical run identities and unresolved lineage. |
| [Publication review](PUBLICATION_MANIFEST.md) and [file manifest](publication_manifest.json) | Proposed inclusions, exclusions, manual-review items and bounded inspection limits. |
| [Thesis-to-code map](../../docs/THESIS_CODE_MAP.md) | Thin chapter navigation using Appendix F IDs. |
| [Detailed PHM map](../../implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md) | 21 investigations, supported findings, limitations, implementation/evidence and prepared footnotes. |

## Resulting structure and exact organization changes

```text
00_thesis_writing_tracking/
  Thesis/
    LaTeX_Project/                 sole authoritative working source
    PDFs/, References/, Release/ retained historical/reference resources
    revision_pipeline/            current state alongside earlier guidance
  scientific_cross_mapping_20261125/
    applied_revision_01/          complete original provenance package
  review_submissions/2026-11-26/   unchanged 71-page review source and README
  consolidation_20261126/          this phase's receipts and review decisions
```

1. Moved `00_thesus_writing_tracking/scientific_cross_mapping_20261125/`
   directly into `00_thesis_writing_tracking/`; verified all 2,601 file hashes
   immediately after the move. No intermediate wrapper or compatibility alias
   was introduced.
2. Compared every one of the old canonical project's 56 files with
   `applied_revision_01/baseline/LaTeX_Project/`. Only after exact tree/hash
   equality was established, removed the redundant canonical copy.
3. Copied all 97 non-build files from the latest historical `working/LaTeX_Project/`
   into the canonical location. The 626 build-cache files stay in the complete
   historical package. Canonical documentation, registry/macros and two prepared
   link files then produced the current 99-file project.
4. Removed the 11-byte `dummz.txt` (`dummy check`) after the scoped dependency
   search found no references. Removed the now-empty incorrectly spelled parent.
5. Updated root/thesis navigation, current state and dataset guides; added the
   thin code map and PHM mapping/verification records. Historical state/README
   preimages are retained here as `*_before.md`. The cross-mapping README has a
   current navigation banner; its original is preserved separately.
6. Extended the existing Appendix F registry from E001–E123 to E001–E133.
   Original IDs and source-name fields remain unchanged. Added descriptive
   optional roles and pinpoints, keeping ordinary footnotes and inline external
   links off by default. Chapter 5 snippets are prepared but not input.
7. Added nine exact small-evidence ignore exceptions and targeted exclusions for
   third-party full text and generated files. No implementation tree, raw data,
   checkpoint, experiment configuration or historical result was moved/changed.

The original eight tracked manuscript edits were preserved in the relocated
historical package. Git reports old-path removals and new-path untracked files
until a later reviewed staging operation can record the relocation. Do not use
`git add -A` as a substitute for the publication manifest.

## Remaining boundaries

Compilation and rendered-layout validation await an available XeLaTeX/Biber
installation. Seventeen existing implementation symlinks do not resolve;
[validation](VALIDATION.md) identifies them without altering protected pointers
or historical study evidence. Exact fixed-fusion/LOEO producing source lineage
remains unresolved. Archive rights/privacy review, existing tracked image/large
metadata review, and new-file publication permalinks remain pending. A later
content/link commit and academic-review tag require separate authorization.

## Final Git handoff

`git diff --check` passed. `git status --short --branch --untracked-files=all`
shows no staged files. The tracked-only `git diff --stat` summary is
`94 files changed, 188 insertions(+), 8910 deletions(-)`. The 80 old-path deletions are
relocated tracked files, whose retained bytes are verified in the migration
receipt; their new untracked locations are not included in that diff statistic.
The exact current status counts and 822 successful local-link checks are in
[final_checks.json](final_checks.json). Existing untracked work remains preserved.
