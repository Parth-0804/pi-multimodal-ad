# Prepared implementation links

[Chapter 5 footnote snippets](chapter05_footnotes.tex) are prepared for the next
chapter-specific writing review. No manuscript entry point inputs that file.
Suggested boundaries are provisional and follow the
[PHM investigation map](../../../../implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md).

## Existing evidence system

Appendix F still prints `tables/evidence_register.tex`. At the researcher's
request on 28 November, former E003/E004 were removed, E001/E002 were retained,
and former E005–E154 became E003–E152. The [publication manifest](../../evidence_publication_20261128/manifest.json)
records the complete mapping. Historical records and the cited PHM investigation
map retain their prior evidence IDs. Current E122–E131 identify the added PHM
implementation, configuration, saved-result and verification resources. The companion `evidence_source_index.csv`
retains the original source-name column and adds current location, SHA-256,
browsing/publication commit, historical execution revision and lineage notes.
The retained evidence sources keep their source identities.

The canonical `evidence_links.tex` now accepts an optional descriptive role:

```latex
\EvidenceRef[Source code]{E033}{measure\_damage\_candidate, lines 114--194}
\ev*{Implementation: photographic proxy}{\EvidenceRef[Source code]{E033}{lines 114--194}}
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
to show `Link unavailable`. All 152 current entries have verified permalinks.

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

E025 retains its original misnamed `phm2026_patchtst_baseline` configuration:
the recorded command ran `train_late_fusion.py`. It is not evidence of a
single-branch PatchTST execution.

Consult the active source index for each resource's verified publication revision.
The [28 November publication manifest](../../evidence_publication_20261128/manifest.json)
records the renumbering and nineteen previously unlinked exact sources published
at `c1fd5b2f93bd3d6243b4207f0d04c33178e4b47e`; their published bytes match the
recorded hashes. Existing correct links retain their verified earlier revisions.

## Validation scope

The [remote-byte checks](../../../consolidation_20261126/github_permalink_validation.json)
record unauthenticated access and digest equality for prepared published resources.
Line pinpoints were checked against the same browsing revision. The
[PHM saved-evidence receipt](../../../../implementations/PHM2026/docs/studies/THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json)
checks saved numbers without training or inference.
