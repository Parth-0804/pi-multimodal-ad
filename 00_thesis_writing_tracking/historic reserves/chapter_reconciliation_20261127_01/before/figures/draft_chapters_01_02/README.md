# Chapter 1–2 figure drafts — 25 November 2026

Review only. The chapters, main document, bibliography, existing figures, thesis PDFs and delivery ZIP are not edited by this task. Start with the **[four-page captioned review PDF](draft_review.pdf)**. All draft sources and copies of accepted renders are in this directory; compiler logs and iteration records are under `build/figures/` at the thesis root.

## Selection and placement

| Draft | Reviewable files | Tool and proposed placement | Recommendation |
| --- | --- | --- | --- |
| 01 Research framework | [PDF](fig01_research_framework.pdf), [PNG](fig01_research_framework.png), [editable TikZ](fig01_research_framework.tex) | TikZ: parallel research dimensions and scope connections, sized at the thesis text width. Chapter 1 after §1.3 or at the end of §1.4. | Include after §1.3: a concise map of the original questions before implementation details. |
| 02 Literature gap map | [PDF](fig02_literature_gap_map.pdf), [PNG](fig02_literature_gap_map.png), [editable TikZ](fig02_literature_gap_map.tex) | TikZ: five aligned evidence → comparison → requirement rows. End of current §2.8.2, before the selection discussion. | Preferred Chapter 2 synthesis figure, subject to accepting the proposed R1–R5 analytical labels. |
| 03 Corpus accounting | [PDF](fig03_literature_appraisal_flow.pdf), [PNG](fig03_literature_appraisal_flow.png), [editable TikZ](fig03_literature_appraisal_flow.tex) | TikZ with counts regenerated from existing registers. Current §2.1.2 or Appendix A, first section. | Prefer Appendix A if visual accounting is useful; main-chapter counts are already explained economically in prose. |
| Table 01 Traceability | [native table source](tab01_requirements_traceability.tex), [preview PDF](tab01_requirements_traceability_preview.pdf), [PNG](tab01_requirements_traceability_preview.png) | Native LaTeX `tabularx`/`booktabs`: requirement and SQ share one column, leaving readable method, coverage and boundary columns. End of current §2.8.4 or Appendix A. | Optional companion in Appendix A. It maps actual thesis coverage; Fig02 maps the argument from literature. Avoid placing both together with repetitive requirement prose. |

The attachment's assumed section titles are not the current file's titles. Current §2.8.2 is **Conflicting Findings and Unresolved Questions**, §2.8.3 **Implications for Representation and Fusion Selection**, and §2.8.4 **Implications for Experimental Design**. Chapter 2 currently has no explicit R1–R5 list and no synthesis table. These draft labels are proposed analytical requirements derived from the current argument, not historical protocol requirements or additional research questions. Insertion will require author review of that framing; nothing is inserted now.

## Proposed captions and notes

Exact caption and note wording is editable in [draft_captions.tex](draft_captions.tex) and rendered in the review PDF.

| Item | Caption | Essential note |
| --- | --- | --- |
| Fig01 | Conceptual Research Framework for Multimodal Industrial Monitoring | Parallel SQ1–SQ3 and spanning SQ4 describe the investigation. Dashed audio remains original scope without completed predictive comparisons. No jointly evaluated final architecture is implied. |
| Fig02 | Literature Gap Map for Multimodal Industrial and Robotic Monitoring | Published findings motivate task-specific comparisons and proposed R1–R5. The corpus is bounded; these are not a retrospectively claimed common protocol. Blue/amber/teal denote findings/questions/requirements; headings retain their meaning in grayscale. |
| Fig03 | Documented Development of the Literature Review Corpus | Candidate records, inclusions, full-text works and PDF inputs differ. The dashed abstract/metadata box is outside the historical 94-work count. Dates and the later methodological-addition branch are omitted. This is descriptive accounting, not PRISMA. |
| Table01 | Traceability of Proposed Analytical Requirements Across Research Questions and Empirical Investigations | Coverage means investigated comparisons, not requirements fully satisfied. Methods differ across studies; no universal ranking or unchanged-model generalization is established. |

## Scientific sources and boundaries

**Fig01:** [Chapter 1 §§1.3–1.5](../../chapters/01_introduction.tex) supplies original SQ meanings and incomplete audio scope. [Chapter 3](../../chapters/03_foundations.tex) and [Chapter 4 §§4.1, 4.5, 4.9](../../chapters/04_methodology.tex) delimit representations, completed windows and robustness. The figure contains no model names or result values and does not combine separately assessed components into a final architecture. Physical condition, manufacturing quality and operational outcomes describe the application domain, not three successfully validated thesis targets.

**Fig02:** [Chapter 2 §§2.2–2.8](../../chapters/02_literature_review.tex), [Appendix A](../../appendices/A_literature.tex), the [94-work matrix](../../../References/literature_review/expanded_comparison_matrix.json) and its cited appraisal records support the five rows. The following are representative, non-exhaustive source groups; the sources are not equivalent industrial evidence:

| Row | Existing citation keys | Inspected record anchors and scope |
| --- | --- | --- |
| [1] Target/correspondence | `Petrich2021Multimodal`, `Pandiyan2022Deep`, `Chen2023Multisensor` | Matrix F118/F119/F116; historical evidence #118 §§2.2–3.2/CT target, #119 §§3.3–4/X-ray guidance, #116 §§3.6–4.1 and synchronized spatial correspondence. The references differ from dataset-native outcome labels; correspondence does not guarantee independent assessment. |
| [2] Representations | `Horwitz2023Back`, `Roth2022Towards`, `Nie2023PatchTST` | F101/F109/P030; geometric inspection, PatchCore intermediate CNN features, PatchTST Table 7 forecasting ablation. Forecasting success is transferable motivation, not demonstrated industrial failure classification. |
| [3] Incremental fusion | `P003`, `Hua2026Weld`, `Thoduka2024Handover`, `Wang2020What`, `Ting1999Issues` | P003 Tables III/V; P032 Tables 1–3; P028 Table III; F106 Table 1. Positive, equal and adverse fusion findings are retained. Ting is a methodological foundation with a least-squares combiner, not an industrial logistic-F2 result. |
| [4] Reliability | `P005`, `P007`, `Huo2022Multisensor`, `Altinses2023Fuzzy`, `Zhang2023QMF`, `P022`, `P026` | ModDrop/EmbraceNet missing-input mechanisms; P029 Table VIII and bias/stuck tests; P037 simulated regression; P058 quality theorem/experiments; P022 noise tests; P026 Table 3 missing-3D result. Simulated or benchmark interventions are not natural industrial faults; quality weights do not certify calibrated reliability. |
| [5] Assessment/external scope | `P004`, `P017`, `P008`, `Bengio2004CVVariance`, `P026`, `P033` | Selection bias, leakage, uncertainty under shift and CV variance are transferable methodological evidence. P026/P033 use target-specific normal fitting/calibration. They do not demonstrate unchanged-model generalization. |

Citation keys resolve in the existing [bibliography](../../references.bib) and [separate Ting addition](../../references_additions.bib). Existing appraisal locators and the previous scientific revision's primary-source checks were consulted; this task does not claim a new full-text audit of all cited publications.

**Table01:** [Chapter 4 §§4.1, 4.5–4.11](../../chapters/04_methodology.tex), [PHM Chapter 5](../../chapters/05_phm.tex), [REASSEMBLE Chapter 6](../../chapters/06_reassemble.tex), [MSM Chapter 7](../../chapters/07_msm.tex), [ViFailback Chapter 8](../../chapters/08_vifailback.tex), and [HANDOVER Appendix H](../../appendices/H_handover.tex). R2 controlled budget/pooling coverage is principally REASSEMBLE. PHM fusion combines representations of sensor observations. F2 within-fold ordering and qualified pooled attribution remain distinct. HANDOVER learned stacking was blocked by its mandatory OOF eligibility gate. ViFailback includes completed frozen/donor comparisons and partial target-CNN adaptation; its stress assessment was not completed. No cell means complete fulfilment.

**Fig03 count reconciliation:** [screening CSV](../../../References/literature_review/historical/candidate_screening.csv), [historical evidence](../../../References/literature_review/historical/evidence.json), [normalized expansion](../../../References/literature_review/normalized_expansion_appraisals.json), [counts](../../../References/literature_review/review_counts.json), [aliases](../../../References/literature_review/citation_key_aliases.json), review-count macros and Appendix A agree:

- 120 candidate records = 39 INCLUDE + 37 EXCLUDE + 44 MAYBE. Candidate records are not all research papers.
- The 39 inclusions comprise 37 F full-text appraisals and two A abstract/metadata-only records: #19 `Zhang2026A`, DOI `10.1088/1361-6501/ae6de4`, and #36 `Liu2024Advancing`, DOI `10.1108/sr-03-2024-0183`. Their 17 November access records report unavailable readable full text, not scientific exclusion. The two are retained discovery inclusions outside the 37 full-text findings.
- 59 later PDF inputs contain two duplicate pairs: P039=P038 and P047=P046, as recorded with identical hashes in the [P021–P040 appraisal](../../../References/literature_review/appraisal_P021_P040.json) and [P041–P059 appraisal](../../../References/literature_review/appraisal_P041_P059.json). That gives 57 additional work identities.
- The expanded register has 94 distinct work IDs and canonical keys, with no DOI or normalized-title overlap between stages. Thirteen existing citation-key aliases are not duplicate works between stages. Four initial full-text appraisals used HTML, explaining why a 94-work register need not contain 94 local PDFs.
- The build script regenerates displayed count macros from these records and checks reconciliation; no source register is changed. Figure03 now shows only the two historical appraisal streams, without calendar dates or the later methodological-addition branch. The underlying historical total remains 94.

## Evidence-coverage chart: omitted under the stop condition

Neither a ten-axis stacked bar chart nor a selected-study heatmap can currently support the requested five evidence categories and applicable denominators from consistent structured fields. The records contain useful narrative evidence, but converting gaps in reporting into confirmed absence would be wrong.

| Requested dimension | Available record / missing requirement |
| --- | --- |
| Credible unimodal comparator | `unimodal_controls`; initial M code does not establish matched capacity, pretraining or tuning. Credibility/applicability is not uniformly coded. |
| Simple static fusion control | No common dedicated field or completeness criterion. |
| Independent acquisition/groups | `split_and_independence` prose; no common group-level eligibility classification. |
| Inference-time missingness | `missing_test` prose and distinct initial codes; planned deployment, training missingness and retrained subsets must not be merged. |
| Controlled corruption | `noise_test` prose; synthetic corruption, recorded-background mixing and fixed noisy benchmarks differ. |
| Matched static/adaptive exposure | No common field describing fitting exposure or an eligible matched contrast. |
| Calibration/probability quality | No uniform extracted field; confidence or uncertainty language is not calibration. |
| Uncertainty/paired comparison | Scattered findings/limits; units, pairing and fixed-fit versus retraining scope are not consistently coded. |
| Cross-dataset/domain evaluation | `shift_test` mixes target adaptation, condition transfer, simulated changes and window-length changes. |
| Resources/practical cost | No uniform field or common timing boundary. |

Reproducible raw code frequencies are available only as **historical-code descriptions** for the initial 37: missingness N28/PA4/TR1/NA1/SD1/GS1/RS1; noise N27/S6/B2/F1/NA1; shift N30/A2/C1/T1/W1/B1/NA1. Their [definitions](../../../References/literature_review/original37_literature_matrix.tex) state that N means no controlled trial established, not explicitly absent. A smaller chart of these codes would duplicate Appendix A without answering the requested coverage question, so none is drawn. A defensible future coverage chart would need source-located paper-by-axis coding, explicit applicability and evidence-status rules, group/target-access/exposure checks and reconciled denominators. That would be a new verification exercise, not an automated recoding of empty cells; the literature review was not restarted.

## Duplication and final selection

The existing [Fig3.1 fusion interfaces](../fusion_interfaces.png) shows actual probability/logit inputs to F2 and gates; Fig01 maps original research dimensions. [Fig4.1 workflow](../research_workflow.png) contains dataset admission and results; Fig01 avoids that chronology and all outcomes. [Fig9.2 coverage](../gap_coverage.png) maps prior evidence to empirical findings and limits; Fig02 stops at unresolved comparisons and analytical requirements. The three existing assets were opened and inspected. Their generation source was not identified among the current thesis figure files; they are preserved byte-for-byte.

There is no current Chapter 2 synthesis table to replace. If one is later introduced with the same evidence → gap → requirement columns, use Fig02 or that table, not both. Table01 here has a different method/coverage/boundary function; keep it in Appendix A if retained. The main-text recommendation is **Fig01 + Fig02**; the flow and traceability table are optional appendix material. This avoids four new main-text visuals and repetition of §2.8.4.

## Build and insertion after review

Verified existing tools: XeLaTeX/TeX Live 2023, Biber 2.19, latexmk 4.83, TikZ/standalone, fontspec, Latin Modern OTF, booktabs/tabularx and Poppler; Python 3.12.3, Matplotlib 3.11.1 and pypdf 6.19.0. TikZ preserves editable relationships and native typography; native tables retain readable boundaries. Without a defensible quantitative chart, Matplotlib/SVG add no benefit. No dependencies were installed.

Run from the thesis root with the existing tools on PATH:

```sh
python3 figures/draft_chapters_01_02/build_drafts.py \
  --run-dir build/figures/draft_chapters_01_02_NEW_RUN
```

The run directory must be new. Each build keeps its own logs and earlier PDFs. Current draft PDF/PNG copies in this review directory are refreshed. The local execution used the already-authorized temporary toolchain via `source /tmp/thesis_tex_20261125/env.sh`; that location is evidence of this execution, not a portable dependency default. The [captioned packet source](draft_review.tex), [preview wrapper](tab01_requirements_traceability_preview.tex) and [shared draft preamble](draft_preamble.tex) are editable. The sources import the existing [TikZ style](../tikz_style.tex). Node/secondary text is at least 9 PDF pt; figure canvases are 159.20 mm wide without resizing labels below that size.

After author review, a candidate insertion using the existing caption/note convention is:

```latex
\begin{figure}[htbp]
\caption{Conceptual Research Framework for Multimodal Industrial Monitoring}
\label{fig:research-framework}
\centering
\includegraphics[width=\linewidth]{figures/draft_chapters_01_02/fig01_research_framework.pdf}
\displaynote{Acoustic observations belong to the original scope; predictive audio
comparisons were not completed. The framework organizes research dimensions,
not a single implemented architecture.}
\end{figure}
```

For Fig02/Fig03, substitute their filename, unique label, caption and full scientific note above; keep Fig02's source groups. Table insertion uses `\caption`, `\label`, then `\input{figures/draft_chapters_01_02/tab01_requirements_traceability.tex}` and `\displaynote{...}` inside a table environment. Review the R1–R5 lead-in before insertion. No snippets have been added to the actual manuscript.

## Validation

**VERIFIED:** the original draft-set run [20261125_05](../../../../scientific_cross_mapping_20261125/applied_revision_01/working/LaTeX_Project/build/figures/draft_chapters_01_02_20261125_05/verification.json) produced three one-page vector diagrams, a one-page native table preview and the four-page review packet. All fonts are embedded; actual text sizes are at least 9 PDF pt. Diagram widths are 451.27 PDF pt (159.20 mm), within 0.01 PDF pt of the manuscript text width. The PDFs contain zero raster-image objects. Final logs have no package/font warnings, unresolved references/citations, overfull boxes or missing characters; Biber reports no warnings/errors. An empty underfull table line is visually harmless.

All four original packet pages and all three original grayscale diagrams were opened. Inspection at the intended inclusion width found no clipping, label/arrow overlap or ambiguous directions. Headings and source indices remain readable in grayscale; dashed audio and the abstract/metadata boundary retain their meanings. Caption/note typography follows the existing thesis convention. The dense gap-map source note is intentionally outside the diagram.

Hashes confirm all 54 pre-existing working-project files and all 56 original/baseline files unchanged. Existing thesis PDFs and ZIP retain their prior hashes. `git diff --check` and draft-source whitespace checks pass. Source hashes, count checks, dimensions and build commands are in the linked verification record; adjacent logs preserve the earlier iterations. No dependency, experiment, commit or push was introduced. The only remaining decision is the author's selection and acceptance of the proposed R1–R5 synthesis labels before manuscript insertion.

Figure03 follow-up: removed the later methodological-addition box, the initial search date and date-bearing citations from its figure note; cropped the unused lower canvas. Historical corpus counts are unchanged. The refreshed Figure03 and review packet are checked in the [follow-up verification record](../../../../scientific_cross_mapping_20261125/applied_revision_01/working/LaTeX_Project/build/figures/fig03_date_free_20261125_01/verification.json).
