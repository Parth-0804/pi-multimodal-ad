# Revision protocol — v0.3

Diagnose globally; edit locally at the smallest sufficient scale; verify consequential changes. Run phases in order. Do not turn this into a research project about revision systems.

## Phase 0 — Establish the source

Use `professor-submitted-2026-11-20-v2` (`47fdaae`) as the frozen baseline and `revision/academic-writing` for approved work in [`Thesis/LaTeX_Project`](../LaTeX_Project/). Consult the [source inventory](README.md) for the matching PDF and evidence paths. Keep stage-specific Git commits for approved structural changes, linguistic edits and evidence-supported scientific corrections. PDF-only work is explicitly provisional. Use exact text and section or printed-page locators in that case. Reconstructed LaTeX cannot establish the release source or its citation keys and labels.

## Phase 1 — Reverse outline and triage (read-only first)

Read the main-text chapters in manageable units. Write a brief reverse outline: what each section actually contributes, what evidence it uses, and how it connects to the chapter and research questions. Identify repeated arguments, misplaced explanations, unclear links, and unnecessary compression. Examine the actual prose, not only first sentences or headings. Distinguish useful signposting and repeated necessary caveats from removable duplication. Appendices and routine text default to KEEP unless a concrete clarity, scientific or formatting issue exists.

Use four actions: **KEEP** (adequate), **LOCAL EDIT** (specific linguistic problem), **STRUCTURAL REVIEW** (possible cut, merge or move), **VERIFY** (scientific concern, may coexist with another action). Triage by impact on scientific understanding, not a fixed percentage. Prioritise the abstract, research problem and contributions, core results, discussion and conclusion for close author attention. Do not use a ranking algorithm as an automatic edit decision.

Copyable diagnosis prompt:

> Read the relevant chapter and its place in the thesis. Create a concise reverse outline of the actual argument; identify which passages need no change, which contain a concrete linguistic defect, which repeat or misplace an argument, and which require source verification. Give section/paragraph locators and reasons, distinguishing observed problems from proposed edits. Do not rewrite any text. Do not propose arbitrary cuts to meet a page target. Preserve essential caveats. Return the report for author review.

The [structural diagnosis](STRUCTURAL_DIAGNOSIS.md) records the section or paragraph locator, argumentative role, action, issue and evidence risk. Use that working note for decisions across chapters. Expand the local detail where editing demands it.

## Phase 2 — Author-approved structural changes (before prose polishing)

Resolve clear macro problems before line editing. Complete approved deletions of redundant explanations, merges, moves and repairs to weak argumentative links first, in a separate reversible structural diff. Record where retained evidence, citations and caveats survive. Do not polish any passage that may be deleted or moved. Review structural changes against the original and applicable evidence before opening Phase 3; unresolved structural questions block local polishing of that material. A proposed cut, merge or move must identify which information survives, where it remains accessible, and whether necessary caveats/citations still accompany the relevant claim. Moving or deleting a substantive assertion requires author approval. Do not drop or relocate methodological qualifications mechanically. Treat suspected scientific errors separately. Keep a reversible diff. Re-read the affected section as continuous prose after the approved change.

## Phase 3 — Selective linguistic editing

Start only after the Phase 2 structural gate is cleared for the affected material (or the author confirms no structural change is needed). Default to a local sentence edit for an isolated defect. Use a paragraph when multiple sentences need to be connected, split or combined. Use a subsection only for an approved structural problem. Preserve clear neighboring sentences. The appropriate context is the section's purpose plus the original passage and whatever nearby text/evidence is needed to understand it. Add more context only if required; neither a rigid sliding window nor the whole thesis is mandatory for each call.

For introduction, abstract and conclusions, the author defines the central argument and contribution in their own words; AI can critique or propose bounded edits. In the literature review, focus on synthesis and verify altered attributions. In methods, protect the executed procedure and distinguish candidates from selected settings. In results, prefer surgical edits while the actual results/table is available. In discussion, have the author settle interpretations, limitations and generalisation boundaries. Maintain consistent register without forcing first person or passive voice.

Copyable editor prompt:

> Read the exact passage, the relevant section context and the applicable style/fidelity rules. Identify the specific problem that makes the original difficult to read. If the prose is already clear, return KEEP. Otherwise propose the smallest change that solves the identified problem. Preserve correct terminology and every existing claim, condition, number, uncertainty and attribution. Do not add explanatory mechanisms, specific literature claims or causal links unless explicitly verified and authorised. Do not change unrelated sentences. If the original seems scientifically wrong or ambiguous, flag VERIFY separately and do not silently resolve it. Return the complete local candidate or minimal source diff, the criterion addressed, the consequential semantic differences (if any) and protected items requiring verification. Mark suggested structural/scientific changes separately. Save a candidate only; do not self-approve or overwrite the baseline.

For an actual source file, keep math, tables, figures, labels, citations and cross-reference commands untouched unless an intentional change is authorised. Avoid blind replacement of a whole chapter. In PDF-only mode, label the candidate as reconstructed or plain text, not original `.tex`.

### Small practical pilot before broad revision

After reviewing the outline and resolving approved structural changes for the test material, select one short, previously unedited results subsection (suggested §6.7.5, printed p. 84, PDF p. 95) and one literature subsection (suggested §2.6.4, printed p. 26, PDF p. 37). Select alternatives if diagnosis identifies more representative problems. Read enough neighboring context to understand the original argument. First retain the original as a comparator and propose lean targeted edits. Produce a controlled paragraph/subsection alternative only if the lean edits do not resolve a connected problem, or if author specifically wants a comparison. Apply the same scientific safeguards to every candidate. Compare actual clarity, coherence, claims changed, author preference and review effort. This is a practical choice of workflow, not a factorial or publishable experiment. No need to generate an expensive rewrite arm by default; no need to optimise detector scores.

## Phase 4 — Verification and author acceptance

**Mechanical checks (required for every changed editable LaTeX file):** Run the included script on each structural or linguistic diff, comparing the frozen original or previous approved checkpoint with the candidate. At final integration, also compare the integrated project against the frozen original and reconcile all intentional changes. Run the following in PowerShell from the repository root.

```powershell
$reviewDir = Join-Path ([IO.Path]::GetTempPath()) ("thesis-review-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $reviewDir | Out-Null
git archive --format=zip --output="$reviewDir/baseline.zip" professor-submitted-2026-11-20-v2 -- Thesis/LaTeX_Project
if ($LASTEXITCODE -ne 0) { throw 'Could not export baseline' }
Expand-Archive -LiteralPath "$reviewDir/baseline.zip" -DestinationPath "$reviewDir/baseline"
python Thesis/revision_pipeline/scripts/verify_tex_integrity.py "$reviewDir/baseline/Thesis/LaTeX_Project" Thesis/LaTeX_Project
```

For an individual passage, pass the two `.tex` files and add `--term "calibrated branch logits"` if that spelling needs protection. For incremental review, substitute the previous approved commit for the baseline tag in the export. The checker compares numeric tokens (including signs and exact precision), common numeric-unit spellings, citation/reference/label commands, conventional math blocks, table/figure environments, and exact occurrences of the locked terms in `00_THESIS_CANON.md`. Exit 0 means the checks detected no protected-token differences, 1 means review is required, and 2 means an input or check error occurred. Reconcile each flag against the diff, including authorised moves and corrections. Confirm that numbers still describe the same model, metric, population, unit and condition. The lexical checks cover `.tex` files. Use Git to review `references.bib`, external assets and protected associations, and inspect custom macros and any unsupported syntax. Rebuild both editions with the [existing build instructions](../LaTeX_Project/README.md), compare warnings to the baseline, and use `latexdiff` when available. PDF-only comparisons stay provisional until the matching sources can be checked. Scientific support comes from the primary evidence.

**Scientific checks (consequential changes and suspected errors):** Extract only the relevant original and revised claims, including metric/value, comparator, evidence strength, scope and source locator. For every altered scientific claim and every suspicious original claim, check the actual saved results, executed configuration/code and, for literature claims, the original cited source PDF or verified full text. Record the exact source locator and author decision. Do not use the original AI-assisted draft or the provisional canon as the final evidence of correctness. Distinguish a regression relative to the original from an error already present in the original. Use a fresh AI session to flag differences when useful, not as a final independent scientific verdict; author or appropriate human reviewer adjudicates every consequential discrepancy. A different model or fresh context does not guarantee independent or correct evaluation.

Copyable delta-review prompt:

> Compare the original passage and the candidate without relying on the editor's explanation. Identify concrete semantic or evidential deltas: stronger/weaker claims, changed or missing conditions, different metrics/comparators, altered uncertainty, changed implementation descriptions, new or redistributed attributions, and omitted limitations. Include the source locator and minimal repair where supported. Distinguish observed text changes from suspected errors in the original; do not infer a publication's findings from its citation alone. State which primary evidence you inspected and which checks are unavailable. Return a risk list for human adjudication, not a certification of scientific correctness. Do not rewrite the passage.

Record outcomes briefly: **KEEP**, **PROVISIONAL** (clarity candidate checked against draft only), **NEEDS CORRECTION**, **BLOCKED** (unresolved material evidence or source issue), or **ACCEPTED BY AUTHOR** (relevant checks completed and author approved; specify evidence scope). Do not label the whole thesis verified based on a local audit. Record only decisions that need persistence in `THESIS_STATE.md` or the relevant working note. Git/diffs provide the ordinary textual history; avoid duplicate per-paragraph bookkeeping.

**Stopping rule:** stop when the diagnosed problem is resolved, the passage reads clearly in context, scientific claims/qualifiers and protected elements are accounted for, and the appropriate human decision has been recorded. If two targeted attempts fail, stop and identify why (ambiguous intent, evidence missing, structural issue, or insufficient clarity); do not run open-ended paraphrase loops. The author may retain a provisional passage as a style example, but cannot mark unresolved science or unavailable source checks as verified.

## Phase 5 — Chapter and thesis review

Read each revised chapter in continuous prose, using the reverse outline as a guide rather than a substitute. Check repetition, progression, terminology, scientific scope, and consistency with research questions, methods, results and conclusion. Reserve a mandatory human read-aloud gate for approximately 15–20 high-leverage pages, prioritising the Abstract, Introduction, Discussion and Conclusion (include key results commentary where appropriate). The author reads the actual final prose aloud to detect monotonous AI cadence, awkward noun stacks, repeated transitions and claims that are difficult to defend. The page count is a practical allocation, not an evidence-based examiner weighting or a cap; extend it if material problems remain. Do not delegate this gate to an AI voice or AI rating. Verify any resulting scientific changes and repeat the affected checks. Resolve only material issues. Before submission, check cross-chapter alignment, document integrity and the applicable university policy/disclosure. Expand the pipeline only where a concrete recurring problem justifies the added cost. The goal is an improved thesis, not a maximally elaborate system.
