# Prepared implementation links

[Chapter 5 footnote snippets](chapter05_footnotes.tex) are prepared for the next
chapter-specific writing review. No manuscript entry point inputs that file;
Chapter 5 and the reviewed Abstract/Chapters 1–4 remain byte-identical to the
promoted snapshot. Suggested boundaries are provisional and follow the
[PHM investigation map](../../../../implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md).

## Existing evidence system

Appendix F still prints `tables/evidence_register.tex`; E001–E123 retain their
identities. E124–E133 add previously unregistered PHM implementation, configuration,
saved-result and verification resources. The companion `evidence_source_index.csv`
retains the original source-name column and adds current location, SHA-256,
browsing/publication commit, historical execution revision and lineage notes.
No new evidence numbering scheme is introduced.

The canonical `evidence_links.tex` now accepts an optional descriptive role:

```latex
\EvidenceRef[Source code]{E035}{measure\_damage\_candidate, lines 114--194}
\ev*{Implementation: photographic proxy}{\EvidenceRef[Source code]{E035}{lines 114--194}}
```

The original `\EvidenceRef{ID}{pinpoint}` syntax remains valid. Both description
and pinpoint are printed in an enabled note. `\ev*` opts in to one note;
`\EnableEvidenceFootnotes` would enable ordinary `\ev` calls globally.
**Do not enable that global switch during consolidation.** Existing calls are
disabled by default, including those in previously reviewed chapters. Inline
`\EvidenceRef` destinations also stay internal to Appendix F while the switch is
off; populating URLs therefore does not silently change reviewed inline links.
The explicit `\ev*` notes and Appendix F link cells provide external access. Resources
without a published URL are omitted from notes; their register entry continues
to show `GitHub link TBD`.

New Appendix F rows and populated link cells can change the appendix's layout.
The macros require a TeX build before insertion or publication; current compilation
availability is recorded in [validation](../../../consolidation_20261126/VALIDATION.md).
No source change here establishes a new rendered PDF or unchanged pagination.

## Browsing version versus execution provenance

Prepared links use the verified public commit
`e2037412036c5bbfc01fb2323215a37ef0b2e090` where file bytes match it. This is
published browsing source, not automatically the experiment-producing source.
The fixed-fusion record names `8c4ae3111c83d8f263c44496bb64a0b04c0fae60`, whose
tracked tree lacks the named fusion implementation/training script. The principal
LOEO record names `c699cbd9727ed33f34f1785172db163eb74b071f`, whose tree lacks the
evaluation script. Both record untracked files; exact executed script lineage
remains UNKNOWN. Later containing commits are not substitutes for that evidence.

E027 retains its original misnamed `phm2026_patchtst_baseline` configuration:
the recorded command ran `train_late_fusion.py`. It is not evidence of a
single-branch PatchTST execution.

E127 (saved predictions), E129/E130 (generated target tables) and E131–E133
(new mapping/verification files) await a reviewed publication commit. Their
permalinks remain blank. The snippets currently use published code, configuration
and result-summary links; add the saved tables only after their actual commit
exists. The source index and [publication manifest](../../../consolidation_20261126/PUBLICATION_MANIFEST.md)
record this dependency.

## Validation scope

The [remote-byte checks](../../../consolidation_20261126/github_permalink_validation.json)
record unauthenticated access and digest equality for prepared published resources.
Line pinpoints were checked against the same browsing revision. The
[PHM saved-evidence receipt](../../../../implementations/PHM2026/docs/studies/THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json)
checks saved numbers without training or inference.
