# Independent researcher handoff

Final candidates: RoboFAC and FAILURE. CRIA was withdrawn after initial acquisition and was not considered further. No existing historical study, trained checkpoint, raw corpus or running REASSEMBLE process was changed. No pilot acquisition, model training or GPU experimentation was started.

**Decision to review:** FAILURE is the best justified next visual pilot, specifically for action-level **RGB plus audio**, using 229 originally labeled joined recordings (147 failure, 82 success). It is not a force/proprioception dataset. RoboFAC has 602 real action path groups (480 failed, 122 successful) but no real numerical payload; its simulation flags cannot currently be treated as a clean replacement cohort.

Review these questions before authorizing a pilot:

1. Is measured audio an acceptable thesis modality, explicitly distinct from force/joint-state fusion? If not, neither remaining candidate qualifies.
2. Do independent recomputations recover 252 annotation identities and 229 complete joins, rather than the later paper's extended cohort?
3. Are whole-action labels appropriate? The ZIP has no onset field, and the source notebook expects a missing `start` column.
4. Are same-date/action pairs sufficiently comparable in object and camera context? The planned member list currently cannot establish that.
5. Which grouping claims are defensible? Seven observed dates have both classes, but task/date confounding and unknown operator/object identity remain.
6. Can use of the externally hosted raw data be confirmed under appropriate terms?

The exact proposed ten-example pilot is in FINAL_DATASET_RECOMMENDATION.md and `checks/FAILURE_PROPOSED_PILOT*.json`. It requires 113.013 MB compressed member data or 125.394 MB extracted, plus range/header/diagnostic overhead. No full ZIP download is needed. No candidate was selected from test/model performance.

## Four-eye reproduction from preserved evidence

Review all native examples in NATIVE_LABEL_EXAMPLES.csv against the original files and their SHA-256 receipts. Recompute counts with:

```bash
ma_thesis_env/bin/python -B DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/code/audit_sources.py
ma_thesis_env/bin/python -B DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/code/validate_delivery.py
```

These commands use preserved active-candidate sources and regenerate this audit's check tables. They do not train or download a dataset. Historical CRIA functions remain in source as an execution trace but are disabled in all entry points. `acquire_annotations.py`, `inspect_failure_archive.py` and `screen_failure_groups.py` document exact bounded network methods; they are not necessary for recounting the preserved evidence. Public API discovery hit GitHub's rate limit; pinned raw/Git HTTPS evidence was used. A fresh full acquisition reproduction was not performed.

Read SOURCE_PROVENANCE.json, `checks/validation.json`, and the individual source receipts for hashes, software, commands, HTTP statuses, byte ranges and limitations. Preview images are an unblinded initial screen; ask the second reviewer for blinded corpus-linked visibility judgments before any modeling decision. No accuracy, AP, fusion benefit, robustness, or learned-weight-transfer result is supplied by this audit.

## Deliverables

- README.md
- DATASET_COMPARISON.md
- ROBOFAC_LABEL_AUDIT.md
- FAILURE_LABEL_AUDIT.md
- NATIVE_LABEL_EXAMPLES.csv
- SOURCE_PROVENANCE.json
- GROUP_INDEPENDENCE_SCREENING.md
- VISUAL_FEASIBILITY_SCREENING.md
- FINAL_DATASET_RECOMMENDATION.md
- RESEARCHER_HANDOFF.md

Sources, checks, code and five initial source contact sheets are kept in their named subdirectories. CRIA_LABEL_AUDIT.md is intentionally omitted under the revised scope. Stop here for independent researcher review.
