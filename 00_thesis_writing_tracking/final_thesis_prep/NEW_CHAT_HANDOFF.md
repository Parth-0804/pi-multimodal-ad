# New-chat handoff

The sole active manuscript is [LaTeX_Project/main.tex](LaTeX_Project/main.tex),
following the researcher-authorized cleanup on 28 November 2026.
Use branch `main` for subsequent thesis editing after the cleanup merge.
Its contents were copied from the current working tree, rather than an older
release, external chapter upload or historical revision snapshot. Original files
were preserved at initial copy time. Later cleanup removed redundant loose manuscript
`.tex` files and review/preview roots while retaining figure sources and support.
The [source cleanup record](SOURCE_CLEANUP_20261128.json) lists removed paths and
hashes, checkpoint recovery for 423 files and the separate local archive for 11 ignored
files. The [current state](../Thesis/revision_pipeline/THESIS_STATE.md) describes recovery;
the copy manifest identifies the initial source snapshot.
The subsequent [front-matter update](changes/frontmatter_20261127_01/README.md)
adds the supplied title/declaration pages and acknowledgements to the prepared
`main.tex`, retaining its own before/after identities and build record.

## Suggested opening message

> I want to complete my thesis end to end using
> `00_thesis_writing_tracking/final_thesis_prep`. Read its README,
> NEW_CHAT_HANDOFF and COPY_MANIFEST, then the current repository instructions.
> Use `LaTeX_Project/main.tex` and its included files as the starting manuscript
> for this session. First inspect the draft and existing review records, identify
> the remaining writing, evidence, citation and formatting work, and prepare a
> chapter-by-chapter completion checklist. Preserve earlier evidence and distinguish
> verified findings, reported checks and unresolved issues. Ask for missing
> university requirements or feedback when needed. Do not infer permission for
> new model experiments, raw-data changes or publication from this handoff.

## Entry points

| File | Purpose |
| --- | --- |
| [main.tex](LaTeX_Project/main.tex) | Complete thesis. |
| [Project instructions](LaTeX_Project/AGENTS.md) | Figure style, compilation and preview requirements for future figure edits. |
| [Evidence index](LaTeX_Project/tables/evidence_source_index.csv) | Existing evidence identities and source navigation. |

## Dated context and remaining cautions

- **VERIFIED at initial copy time:** source and copy hashes matched. The copied
  `main.tex` and `chapter-preview.tex` differ from their identities in the prior
  literature-integration manifest. The initial copy task did not compile a new PDF or validate
  the scientific content. Later front-matter validation is recorded separately.
- **REPORTED in the November 27 records:** the empirical revision and chapter
  reconciliation were incorporated into the original working draft. Read the
  [empirical verification](context/empirical_revision_20261127_01/VERIFICATION.md),
  [examiner specification](context/empirical_revision_20261127_01/examiner_specification.txt)
  and [reconciliation report](context/chapter_reconciliation_20261127_01/MERGE_REPORT.md).
  Earlier checks retain their original scope and dates.
- **REPORTED remaining citation work:** seven Chapter 2 page/version checks were
  still open at reconciliation. Their exact details are in the
  [Chapter 2 review](context/chapter_reconciliation_20261127_01/reviews/chapter_02.md).
  Reassess their current status before claiming they are resolved.
- **REPORTED build limitation:** the
  [literature-visual integration](context/literature_visual_integration_20261127_01/INTEGRATION_REPORT.md)
  records a successful 191-page main build and a failed fast Chapter 2 preview
  caused by a missing `\textcite` definition. It also records an Appendix F
  caption warning. These are prior results, not new checks of this snapshot.
- **REPORTED separate proofreading work:** the
  [LTeX pilot](context/ltex_pilot_chapters_01_04_20261127_01/README.md) and
  [its change list](context/ltex_pilot_chapters_01_04_20261127_01/CHANGES.md)
  describe separate revised Chapter 1–4 copies, not an integrated full project.
  No pilot wording was merged during preparation. Original candidate files remain
  [in the pilot directory](../ltex_pilot_chapters_01_04_20261127_01/reworked/tex/).
- The [November 26 state note](context/Thesis/revision_pipeline/THESIS_STATE.md)
  predates the November 27 revisions. Treat its chapter statuses as dated context.
  The copied [canon](context/Thesis/revision_pipeline/00_THESIS_CANON.md),
  [style guide](context/Thesis/revision_pipeline/01_STYLE_AND_FIDELITY.md) and
  [revision protocol](context/Thesis/revision_pipeline/02_REVISION_PROTOCOL.md)
  also need their historical scope retained.
- The [results audit](context/results_audit_ch05_ch08_20261127_01/AUDIT_REPORT.md)
  provides additional evidence-navigation context. Copying it does not independently
  verify its claims or authorize publication.

## Front matter added on 27 November 2026

The full edition includes the supplied title page and declaration before the
abstract, and the author's acknowledgements between the abstract and contents.
The declaration wording and acknowledgement prose are preserved as supplied.
Submission/signing dates remain `xx November 2026`; the signature line is blank.
No university-template or declaration-compliance check is implied. The 27 November
front-matter build had 194 pages; PDF pages 1–6 were visually inspected in that pass.
That build predates later source edits and does not validate the current manuscript.
The abstract's keywords occupied a separate page (Roman ii) in that build. No abstract
prose or spacing was changed during that front-matter pass.

## Proposed first completion pass

Inventory each chapter, abstract, discussion, conclusion and appendix against the
latest applicable feedback. Check the current title, university template,
submission date, required declarations and AI disclosure with the researcher.
Resolve citation and evidence gaps without inventing sources or results. Maintain
a single working project for the session, then compile and visually inspect the
full thesis after approved writing changes. Preserve
research scope, negative/incomplete studies and methodological limitations.

These are proposed next steps, not completed thesis review or academic sign-off.
