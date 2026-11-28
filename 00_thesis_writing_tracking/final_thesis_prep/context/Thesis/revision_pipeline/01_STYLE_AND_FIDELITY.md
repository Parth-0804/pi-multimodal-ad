# Operational style and fidelity rules — v0.3

**Edit the problem, not the paragraph by default.** The scientific content and the author's voice take precedence over stylistic uniformity. Leave adequate prose unchanged. Structural problems must be diagnosed and author-approved cuts, merges, moves and argument repairs completed before sentence polishing. Do not polish material still marked for structural review. Preserve its meaning, evidence and necessary qualifications wherever it survives.

## 1. Six writing rules

| Rule | Apply when |
|---|---|
| 1. Make the actual action and actor clear; prefer a meaningful verb over an empty verb plus process noun. | A sentence hides what was done, to what or under which conditions. Do not invent an agent or causal mechanism. |
| 2. Unpack dense noun stacks using a clause or postmodifier. | Modifier relationships are difficult to recover. Keep established technical nouns such as calibration, regularisation, temporal misalignment and multimodal fusion. |
| 3. Keep the grammatical subject and main verb reasonably close; split only genuinely overloaded sentences. | Long modifiers interrupt the main claim. Vary rhythm naturally, without fixed sentence lengths. |
| 4. Link known information to new information and state the real relation between adjacent claims. | Argument flow is unclear. Do not insert causal or contrastive connectives merely to make the prose smoother. |
| 5. Remove empty introductions, generic boosters and redundant conclusions; use precise, concrete terms. | The expression adds no meaning. Repetition of scientific terminology is often preferable to arbitrary synonyms. |
| 6. Match the rhetorical purpose. | Introduction motivates the problem; literature synthesises evidence; methods state procedures; results report scoped comparisons; discussion qualifies implications. Do not impose one paragraph template on all chapters. |

A linter can flag possible noun stacks, empty phrasing, overused connectives, long sentences and repeated openings. Flags are diagnostic only. Do not target a percentage of paragraphs, word-count reduction, sentence length or a banned-word score. The presence of a nominalisation, passive voice, technical noun or common transition is not sufficient reason to edit.

### Candidate examples from this thesis

These are illustrative, not approved replacement passages. Read the source and relevant evidence before using them.

| Original | Minimal editing direction | Protected meaning |
|---|---|---|
| Known absence raises a different problem from an apparently valid sensor reading corrupted by noise. | A known missing input poses a different problem from a corrupted reading that still appears valid. | Known versus undetected failure. |
| Filtering or a harsh-environment title alone cannot fill a robustness cell. | Signal filtering or a reference to harsh environments does not, by itself, establish that robustness was tested. | Replace internal matrix jargon without changing evidence. |
| The healthy companion is part of that condition. | The reported comparison retains an uncorrupted companion stream. | State the observed condition, not a necessary cause of recovery. |
| Fusion uses branch prediction banks with recording-excluded row construction and held-out outer assessment recordings. | Fusion uses prediction banks constructed by excluding the recording associated with each predicted observation. The outer assessment recordings remain held out. | Verify precise prediction/feature construction before acceptance; do not extend the description to F3 by assumption. |
| All three original gates have lower AUROC than F2, with intervals excluding zero for those differences. Their AP differences remain unresolved. | Keep the original unless the surrounding argument requires a clearer link. | This is already precise. Never replace it with “none of the gates outperforms F2.” |

## 2. Scientific preservation contract

**Protected by default:** research questions, target definitions, prediction horizons, method names and executed components, training and evaluation conditions, sample sizes, comparison directions, numbers/signs/units/precision, uncertainty, caveats, equations, tables, figure references, citations and their claim associations, LaTeX labels/macros and cross-references. Do not silently change them, including rounding or synonym changes that change technical meaning.

| Evidence type | Wording boundary |
|---|---|
| Direct matched comparison | State model, comparator, metric and scope; e.g. “achieved higher AP on these held-out actions.” |
| Unresolved statistical contrast | “The paired interval includes zero” / “the difference remains unresolved.” Not equivalence or proof of no effect. |
| Observational pattern or hypothesis | Use appropriately qualified association or possibility. Do not replace it with “causes,” “proves” or a guaranteed mechanism. |
| Controlled intervention with unmatched factors | Describe the tested pipeline/recipe and conditions. Do not isolate a mechanism unless supported by the controls. |
| Literature finding | Preserve the scope, attribution and source-specific conditions. Verify changed claims against the publication. |
| Incomplete or exploratory experiment | Distinguish candidate, planned, executed, deferred and assessed; do not present exploratory findings as independent confirmation. |

A word is not inherently forbidden; its epistemic effect is what matters. Hedges encoding real uncertainty are not filler. Do not collapse distinct limitations merely to reduce length. When consolidating a repeated qualification, ensure each retained claim can still be interpreted correctly in its immediate context.

**Relative fidelity:** did editing change the original claim, including its conditions or uncertainty? **Absolute fidelity:** is that claim actually supported by the implementation, data or paper? Both matter; neither follows from fluency or a successful LaTeX build. Flag suspected original errors separately rather than silently correcting or laundering them into smoother prose.

## 3. High-stakes acceptance rule

A scientific change is consequential if it concerns the research gap/contribution, results or their interpretation, method/data definitions, limitations, or literature attribution. In these cases inspect the relevant primary record and obtain author approval. Where evidence is missing, mark the passage provisional or blocked. Preserve the truthful AI assistance disclosure.

For editable LaTeX, run the included deterministic checker on the changed source before acceptance. Every unexplained change to protected numbers, citation commands, equations, references or locked terms blocks acceptance. A clean script report is not proof of scientific validity: verify changed or suspicious claims against actual experimental records, implementation and cited source PDFs. Where those are unavailable, keep the affected claims provisional or blocked.

For every edited passage ask: Is the stated linguistic defect resolved? Is there a concrete improvement for the reader? Are the claims and their qualifiers preserved, and the protected elements checked? Does the new passage still serve its role in the surrounding argument? Has the author reviewed the consequential changes? If the answer is yes, stop editing. Do not polish further merely for variation. See the protocol for exact status and escalation handling.
