# Chapter 2 incremental wording update — 26 November 2026

Applied the author’s latest attachment (`eb2e0de0-2228-4fad-96e2-5312e3173a34`) selectively to the existing corrected Chapter 2. Exactly eight paragraphs changed: four opening paragraphs, two under Section 2.1 and two under Section 2.1.1. All text from the Baltrušaitis taxonomy paragraph onward is byte-identical to the previous working source. Previously approved spelling, terminology and scientific repairs remain, including the precise Intel Welding assessment-population statement.

The previous source, latest attachment and reconstructable [revision patch](chapter2_update.patch) are preserved here. [Source checks](source_checks.json) confirm identical numeric tokens and citation commands, an unchanged 56-file baseline, unchanged figures/other working files and an exact patch reconstruction. No references, models, experiments or figure designs were added.

The established integrity checker reports one review flag because line wrapping separates the words “Intel Welding”; the phrase and its meaning remain unchanged. It finds no numerical, citation, label, equation or table changes. See [pipeline report](pipeline_integrity.txt). The validation directories reuse unchanged auxiliary inputs from the preceding checked builds; their origins are recorded in `validation_seed_inputs.json`.

Compilation checks are recorded in `build_checks.json` after completion. PDFs here are validation outputs; the delivery PDFs and ZIP are not replaced in this source-update step. The combined Abstract + Chapters 1–4 review packet remains pending the author’s Chapter 3 and 4 files.
