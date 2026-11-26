# Manav review — Chapter 3 workflows, 26 November 2026

Five workflows from the supplied PDF are integrated under §§3.5.1–3.5.5, with captions, stable labels and references in the text. The original explanations, equations, citations and tables are preserved. The existing overview precedes the five subsections.

- [Manav: Abstract + Chapters 1–4](Manav_review_Abstract_Chapters_1-4.pdf) — **71 pages**.
- [Editable LaTeX ZIP](revised_latex_source.zip) — **72 source/assets files**, matching the compiled inputs.
- [Complete thesis](revised_thesis.pdf) — **187 pages**.
- [Abstract-through-conclusion review](revised_review.pdf) — **131 pages**, Chapters 1–10.
- [Current delivery notes](checks/ch3_workflows_20261126_01/DELIVERY_NOTES.md).
- [Current source diff](checks/ch3_workflows_20261126_01/chapter3_workflows.patch).
- [Current validation](checks/ch3_workflows_20261126_01/final_validation.json).

| Material | Manav PDF pages |
| --- | --- |
| Abstract | 1 |
| Chapter 1 | 2–7 |
| Chapter 2 | 8–43 |
| Chapter 3 | 44–58 |
| Chapter 4 | 59–71 |
| Prediction availability, §2.2.4 | 15 |
| Literature synthesis table | 35 |
| Five-study scope table | 39 |
| Literature synthesis diagram | 43 |
| Sensor patches, §3.3 | 48 |
| Representation, reference and fusion tables | 49, 50, 57 |
| Fusion-input overview | 51 |
| PHM feature concatenation, §3.5.1, Figure 3.3 | 52 |
| F1 equal averaging, §3.5.2, Figure 3.4 | 53 |
| F2 logistic stacking, §3.5.3, Figure 3.5 | 54 |
| Context-based gating, §3.5.4, Figure 3.6 | 55 |
| Anchored adjustment, §3.5.5, Figure 3.7 | 56 |
| Research workflow | 61 |
| Stacker recording flow, §4.6.2 | 65 |

The unchanged supplied five-page PDF is packaged as `figures/fusion_workflows_20261126.pdf`. Notes delimit PHM's sensor inputs and photographic target, fold-specific F2 coefficients, and the anchored model's clean two-input comparison and separate fallback.

The prior 67-page Manav PDF, 183-page thesis, 127-page review, 71-file source ZIP and affected sources are preserved in [the before snapshot](checks/ch3_workflows_20261126_01/before/). The [previous author-chapter delivery](checks/manav_author_ch34_20261126_01/DELIVERY_NOTES.md), earlier consolidation records and original baseline remain historical records.

All three editions rebuilt successfully with the existing XeLaTeX/Biber workflow. The two review editions have no LaTeX or Biber warnings; the full thesis retains its previously documented Appendix F caption/hypcap warning. The workflow source and final manuscript pages 50–59 were rendered at 150 dpi and inspected. The unchanged Abstract and Chapters 1–2 match the first 43 pages of the preceding review. All 71 Manav pages match the start of the Chapters 1–10 review.

The existing 12 pt font, A4 page, margins, one-and-a-half body spacing, centered one-page Abstract and DRAFT watermark are retained. No experiments, dependency installation, commit or GitHub publishing was performed.
