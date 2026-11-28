# Scientific cross-mapping and proposed manuscript revisions

Review package, 25 November 2026. **The existing manuscript has not been edited.** This is a bounded addition to the existing thesis revision work, in the `00_thesus_writing_tracking` folder requested by the researcher. The source manuscript remains under `00_thesis_writing_tracking/Thesis/LaTeX_Project`.

Start with [the proposed replacement passages](PROPOSED_MANUSCRIPT_REVISIONS.md). They identify the existing location, weakness, evidence, replacement text, improved argument and remaining limits. Most replace existing interpretation; they do not require new chapters.

Supporting analysis:

- [Controlled comparisons, external interpretation and research-question answers](SCIENTIFIC_CROSS_MAPPING.md).
- [Architecture rationale and targeted original-publication checks](ARCHITECTURE_AND_LITERATURE.md).
- [Consequential research chronology](RESEARCH_CHRONOLOGY.md).
- [Independent F2 saved-prediction verification](F2_VERIFICATION.md), [machine-readable results](f2_verification/results.json), [fold table](f2_verification/fold_metrics.csv) and [audit code](f2_recompute.py).
- [One proposed bibliography addition](proposed_bibliography.bib). No existing bibliography or Zotero library was changed.

The central correction is that the F2 visual contribution is stronger than the draft's blanket recalibration caveat suggests: adding the saved visual term improves within-fold AUROC in five of five folds and AP in four of five. A separate cross-fold score-alignment effect also exists. Neither finding identifies a causal modality contribution or eliminates selection uncertainty.

The other consequential update is chronological: the 24 November ViFailback closure contains a completed seed-42/fold-0 FULL20 comparison and a FULL100 pilot. Statements that target-CNN adaptation was entirely unexecuted are now stale. Their effects remain inconclusive; the wider FULL20 matrix remains incomplete.

## Evidence and scope

**VERIFIED** means source or artifact contents inspected here, or metrics recomputed here, with that scope stated. **REPORTED** denotes execution, prior verification or uncertainty results attributed to existing reports. **INFERRED** denotes interpretations of identified evidence. All manuscript passages are **PROPOSED**. **UNKNOWN** is used where a historical reason or required evidence is missing. Reading a report did not reproduce its training or independently verify its bootstrap.

New computation was limited to arithmetic on existing REASSEMBLE predictions, coefficients and split metadata. No training, model inference, raw-data preprocessing, new corruption experiment, installation, job control, commit or push was performed. No historical result was overwritten. Live Zotero was unavailable at its local API; existing manuscript references and literature records were reused, with selective original-paper inspection and one Elicit query for the missing stacking foundation.

Repository HEAD at review: `e2037412036c5bbfc01fb2323215a37ef0b2e090`. The worktree already contained untracked thesis material. [The baseline hash manifest](manuscript_before.json) identifies every existing LaTeX-project file before this work. [Source identities](source_manifest.json) and [validation](VALIDATION.md) record the final checks. These identities describe the inspected working files, not a claim that all manuscript files are committed at HEAD.

The original research questions and registered title are preserved. Dataset feasibility findings and reported supervisor agreement are not treated as a general amendment to written experiment scope. This task required documentary analysis and the specifically requested saved-score recomputation, not a new experimental authorization.
