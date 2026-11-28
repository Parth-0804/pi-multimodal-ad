# Authoritative thesis manuscript

This is the sole active project following the researcher-authorized cleanup of
28 November 2026. Compile `main.tex`. The project retains the complete manuscript,
bibliographies, evidence tables, cover PDF, figure sources and supporting files.
Earlier review/preview entry points were removed. Recovery of removed manuscript
copies is described in the [current state](../../Thesis/revision_pipeline/THESIS_STATE.md).
No new compilation is implied by this cleanup.

The following revision and build notes retain their original dates. Their PDFs
predate subsequent source changes.

Updated 26 November 2026 with the author's Abstract and Chapters 1–4, the Chapter 1–2 citation corrections, and the integrated figures and tables. The accompanying delivery package contains the full thesis, the abstract-through-conclusion edition, and `Manav_review_Abstract_Chapters_1-4.pdf`.

On 27 November 2026, Chapters 5–8 were revised against the supplied examiner assessment,
with matching framing changes in Chapters 1–4 and 9 and evidence additions in Appendices
D/F/J. The [revision and verification record](../../empirical_revision_20261127_01/VERIFICATION.md)
separates independent saved-score checks from retained reports. That revision did not
build an updated PDF; the existing delivery PDFs remain their earlier versions.

The subsequent [chapter reconciliation](../../chapter_reconciliation_20261127_01/MERGE_REPORT.md)
merged the external chapter wording with the current working tree. Chapter 2 remains an
independent critical literature review; the requirements and five-study mapping now open
Chapter 4. The complete, 189-page thesis was rebuilt from the then-active project with XeLaTeX,
Biber and latexmk. The [reconciliation thesis](../../Thesis/LaTeX_Project/build/chapter_reconciliation_20261127_01/thesis/main.pdf)
and its [150 dpi review previews](../../Thesis/LaTeX_Project/build/chapter_reconciliation_20261127_01/previews/)
belong to this reconciliation. The review editions and historical delivery PDFs were not
regenerated.

The later [literature-visual integration](../../literature_visual_integration_20261127_01/INTEGRATION_REPORT.md)
adds the author's seven-topic appraisal figure before the Chapter 2 research-gap discussion
and consolidates the closing synthesis and follow-up questions into one table.
The literature-visual integration build recorded in that report
had 191 pages: Figure 2.2 is on PDF page 44 (printed page 32), and Table 2.1 is on
PDF pages 46–47 (printed pages 34–35). The editable source is
[figures/review_figure_table.tex](figures/review_figure_table.tex), loaded in embedded mode
through the shared preamble. The original upload is not a build dependency.

Use XeLaTeX and Biber. `main.tex` is the sole manuscript entry point: title page,
declaration, abstract, acknowledgements, contents and lists, Chapters 1–10, disclosure,
references and appendices.

From this directory, run `latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build/final_prep main.tex`.
Select `main.tex` and XeLaTeX in Overleaf. Biber runs automatically through latexmk.
Edit the included files in `frontmatter/`, `chapters/`, `appendices/` and `tables/`.
All editable figure sources and their support remain available under `figures/`.

Chapter 2 includes the literature synthesis table. Chapter 4, Section 4.1, contains the supplied welding-to-requirements diagram, the R1–R5 explanations and the five-study scope table. Three explanatory diagrams are added by section heading: prediction availability (§2.2.4), overlapping sensor patches (§3.3) and the stacker recording flow (§4.6.2). Chapter 3 retains its three comparison tables and fusion-interface overview. Five supplied vector workflows are placed under §§3.5.1–3.5.5: PHM feature concatenation, F1 equal averaging, F2 logistic stacking, context-based gating and anchored adjustment. The unchanged five-page source is included as `figures/fusion_workflows_20261126.pdf`. Chapter 4 retains the research-workflow figure. Editable figures and build details are documented in `figures/review_explanatory_20261126/README.md`. Unselected diagrams under `figures/draft_chapters_01_02/` remain drafts and are excluded from the delivery source ZIP. The date-free draft Figure 3 is preserved separately.

The DRAFT watermark remains controlled by `\thesisdrafttrue` in `main.tex`. Historical chapter PDFs remain in the unchanged baseline and are excluded from this package. Appendix F and `tables/evidence_register.tex` retain the evidence index; empty publication URL fields remain empty rather than inventing links. The disclosure is in `appendices/I_ai_assistance.tex`.

## Working and historical identity

Edit this project only. It was copied from the then-current working tree.
The [historical applied-revision directory](../../scientific_cross_mapping_20261125/applied_revision_01/working/LaTeX_Project/)
retains supporting assets and historical build material; redundant loose manuscript
sources are recoverable from the cleanup checkpoint rather than a second active copy.
[The submitted review source](../../review_submissions/2026-11-26/README.md) is retained separately.

[Evidence-link preparation](implementation_links/README.md) documents opt-in
footnotes, publication lineage and the uninserted Chapter 5 snippets. Existing
chapter footnotes remain disabled by default, so adding registry URLs does not
activate notes in previously reviewed chapters. Appendix F remains the full
register. [Consolidation validation](../../consolidation_20261126/VALIDATION.md)
records the earlier build tooling and checks. The
[reconciliation report](../../chapter_reconciliation_20261127_01/MERGE_REPORT.md)
records that earlier build and preservation checks; the literature-visual integration
record above documents its historical main build.
