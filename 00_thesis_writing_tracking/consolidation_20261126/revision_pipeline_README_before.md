# Thesis revision — minimal workspace v0.3

**Principle:** Diagnose the thesis systematically, edit only where necessary, and independently verify consequential changes.

The objective is natural, precise engineering prose and a coherent scientific argument. The author retains responsibility for the research, interpretation and final text. This version tightens v0.2 with an explicit structural-editing gate, mandatory scripted checks for editable LaTeX, primary-evidence verification, and a human read-aloud gate. Editorial assessments guide diagnosis. Scientific claims are supported by the implementation, results and publications.

## Five files, five purposes

| File | Use |
|---|---|
| `README.md` | Entry point and source inventory |
| `00_THESIS_CANON.md` | Short reference sheet: research questions, non-claims and numerical anchors. The name is retained for compatibility; it is not an ontology or independent ground truth. |
| `01_STYLE_AND_FIDELITY.md` | Operational editing rules, examples, scientific protection and acceptance conditions |
| `02_REVISION_PROTOCOL.md` | Diagnosis, selective revision, verification, stopping rule and copyable prompts |
| `THESIS_STATE.md` | Actual progress, open scientific issues and approved decisions |

Use the existing thesis workspace. The professor-submitted PDF and its matching LaTeX project are preserved at tag `professor-submitted-2026-11-20-v2` (`47fdaae`). The working branch is `revision/academic-writing`. After author approval, use the existing `../LaTeX_Project/` on that branch and keep structural, linguistic and evidence-supported scientific changes in separate commits. The earlier pilot examples remain in the style specification.

The five Markdown files are accompanied by one utility, `scripts/verify_tex_integrity.py`. This implements mandatory, deterministic flagging of protected textual changes in editable `.tex` files; it does not establish scientific correctness. See Phase 4 for usage, limitations and the PDF-only fallback.

## Source inventory

| Source | Status |
|---|---|
| [Professor-submitted full PDF](../PDFs/DRAFT_Thesis_2026-11-20_FULL.pdf) | November 20 v2. 193 physical pages. Main text uses printed pp. 1–131, with the disclosure on p. 132. References and appendices follow. |
| [Editable project](../LaTeX_Project/) and [bibliography](../LaTeX_Project/references.bib) | `main.tex` builds the full edition. `review.tex` builds the abstract and main chapters. Both share the chapter sources. See the [baseline verification](../README.md) and [build notes](../LaTeX_Project/README.md). |
| [V2 evidence bundle](../Release/Thesis_2026-11-20_v2_LaTeX_and_Evidence.zip) | Contains the edition-specific checks, supporting evidence, and `audit/evidence_reference_locators.csv`. Start from the in-project [evidence source index](../LaTeX_Project/tables/evidence_source_index.csv) and follow the relevant file ID. |
| Recovered implementation | `C:/Thesis/03_IMPLEMENTATION_AND_CODE/pi-multimodal-ad.bundle` holds the versioned repository. The adjacent `RESTORE_IMPLEMENTATION.md` describes provenance. Identify the producing version from run records for each claim. |
| Recovered experiments | `C:/Thesis/04_EXPERIMENTS_AND_RESULTS/EXPERIMENT_RESTORE_AND_STATUS.md` locates the HPO export, recovered run archives and cited evidence. Check the actual configuration and saved results for the claim under review. |
| Literature registers and papers | Use the [37-work register](../References/literature_review/original37_literature_matrix.csv), [94-work register](../References/literature_review/expanded_comparison_matrix.csv), [citation-to-PDF index](../References/CITATION_PDFS.csv) and [PDF provenance](../References/PDF_PROVENANCE.csv). The optional recovered Zotero export is `C:/Thesis/02_LITERATURE_AND_ZOTERO/Zotero_2026-11-24_export.bib`. |
| Earlier pilots and revisions | The style examples are illustrative. The earlier pilots remain historical and unaccepted. Use the tagged source for current paragraph locators. |
| University rules on AI assistance and submission | Applicability remains open. Retain an accurate disclosure and check the programme and cohort rules before submission. |

Baseline PDF SHA-256: `30a55e9fd13fe0878b0d067ffa28ba1d787e8fe3b8db47ae2dbfec9faad70bd7`

The PDF is the fixed textual baseline, not an authoritative substitute for actual experimental records or publications. Never silently substitute an earlier source version. Preserve and reconcile discrepancies when matching source is found. If only the PDF is available, draft and audit in provisional mode; original citation keys, labels and LaTeX integrity cannot be certified. No fabricated keys or claims of source recovery.

## Start in this Git workspace

The read-only Phase 1 review is in [STRUCTURAL_DIAGNOSIS.md](STRUCTURAL_DIAGNOSIS.md). Review its proposed dispositions before opening the structural gate. The same method can be continued in a session with access to this repository and the relevant local evidence.

Paste this instruction:

> Read the five Markdown files in this workspace, verify the baseline and inspect the available source files. Follow the v0.3 protocol. Begin with Phase 1 only: produce a concise, thesis-wide reverse outline from the main-text chapters, identify structural repetition and unclear argumentative links, and triage passages into KEEP, LOCAL EDIT, STRUCTURAL REVIEW or VERIFY. Use section/paragraph locators and explain why a change would be useful. Do not rewrite, delete, reorder or change any thesis content. Keep the diagnostic report concise, retain necessary methodological caveats, and stop for my review. Record the source limitations and actual progress in THESIS_STATE.md.

Read the five files at setup; for each subsequent edit, load only the relevant constraints, local passage, context and evidence. The initial diagnosis can use the PDF. The author approves structural decisions, and the approved cuts, moves and argument repairs must be completed and checked before sentence polishing begins in the affected material. Use the two short test passages only after diagnosis and the structural gate. With editable LaTeX, run the included verification script on every changed source file or directory; review every flag, compile, and check altered or suspicious claims against primary evidence. In PDF-only mode, do not report source-level verification as complete. Reserve a final human read-aloud of approximately 15–20 high-leverage pages across the Abstract, Introduction, Discussion and Conclusion (and key results commentary where needed); extend the reading if unresolved issues remain. No comprehensive citation map, manual per-paragraph ledger, or additional automation is required.
