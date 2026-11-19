# Stage 2 review handoff

**LIMITED GO.** Final validated revision: `runs/20261027T001047876764Z-stage2-validated/`.

- 114 primary construction examples (93 label 0, 10 label 1, 11 label 2) from 127 intervals.
- 13 exclusions: six no video, four unsupported timing, one cannot supply 16 distinct guarded frames, two insufficient MTC coverage.
- 39 examples support a separate video+raw-ACC contract; cohorts overlap.
- Two positive-containing experiment groups; adequate grouped evaluation is not established by this pilot.

Required deliverables: `MSM_STAGE2_MODALITY_AUDIT.md`, `MSM_VIDEO_ALIGNMENT_REPORT.md`, `MSM_PILOT_SAMPLE_MANIFEST.csv`, and actual diagnostic figures under `figures/` (eight representative 16-frame/sensor examples, six full-recording timelines, five alignment plots, and all-frame visibility atlases).

A partial-overlap error was discovered and corrected before finalization. `METHODOLOGY_CORRECTION.md` and failing-then-passing synthetic evidence explain it. Earlier provisional counts and dataset9 sequences in the exploratory run are superseded; they remain preserved.

Changed files are confined to `MILLING DATASET/`: live index/ignore rules, Stage 2 source scripts, two synthetic test modules, acquisition evidence, and the new versioned analysis outputs. Stage 1 source, reports, inputs, and the exploratory run were hash-verified unchanged. Raw files, isolated tools, caches/staging, logs and generated figures are ignored. No files were staged or committed.

`git diff --stat` still describes only the pre-existing tracked modifications:

```text
 README.md                                              |  4 ++++
 REPO_MAP.md                                            |  6 ++++++
 docs/thesis_research_direction/THESIS_EVIDENCE_GAPS.md | 12 ++++++++++++
 3 files changed, 22 insertions(+)
```

Checks passed: all 26 MSM tests; the partial-overlap regression failed before and passed after the correction; independent native-label/frame/feature verification; all 41 selected input hashes match receipts; Stage 1/exploratory preservation; AST parsing; pip check; whitespace check; raw/figure Git exclusions. Maximum absolute numerical difference in independent MTC statistics was 6.10351562e-05 in native units (normal floating-point accumulation differences). Exact results are in `validation.json`.

Remaining issues: coolant occlusion; no external video timing fiducial; MTC feature-window latency; clipping/sparsity; physical group independence; and few positive pilot groups. These are limits of the current scientific claim, not pending training work.

Full lab video/MTC/ambient/metadata expansion needs 2,533,736,741 additional bytes. Including all VM20i raw acceleration increases the additional source requirement to 34,257,685,928 bytes. A full uint8 frame cache could add up to 6,050,021,376 bytes; admission is not guaranteed for uninspected recordings.

Exact next action: researcher review of the reports, corrected mapping, diagnostic visibility, and sensor-contract choice. Stop here. No further acquisition, architecture substitution, or model training is authorized by this completion.
