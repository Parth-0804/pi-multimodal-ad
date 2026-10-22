# Completed REASSEMBLE work: Git commit and push report

Status: **BLOCKED at Phase 0 authentication gate**. Five selective local commits succeeded; no commit was pushed. The new scientific experiment was not created, implemented or started.

Branch: `main`. Existing configured remote: `origin`, `https://github.com/Parth-0804/pi-multimodal-ad.git`. Existing upstream: `origin/main`. No branch switch, history rewrite, force-push, stash, broad add, raw-data operation or ignore-policy change occurred.

| Commit | Message | Files | Major paths | Push status |
|---|---|---:|---|---|
| `8e09335501f384fd43b59faf63785cb34de51247` | reassemble: add frozen CNN vs hybrid encoder study | 66 | `00_experiments/rt_detr_encoder_comparison/` | Local only |
| `3a5f5f117577355ab20d827d2ae35d79dbb4b0e6` | reassemble: add selected-model robustness study | 148 | `00_experiments/fusion_noise_test/` | Local only |
| `a03450852f705a310fd12b6e7ca83592c2cbcf05` | reassemble: add quality-aware fusion robustness pilot | 79 | `00_experiments/adaptive_fusion_robustness/` | Local only |
| `4f563c168e4a493a87e5361474157b0562cc4ef4` | reassemble: add frame-count and backbone fine-tuning study | 87 | `00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/` | Local only |
| `411b2d2c6381008164a870d7e6423fb0ae0d1060` | reassemble: add fusion AP diagnostic analysis | 35 | `00_experiments/visual_backbone_one_day/{fine_tuning_diagnostics_01,fusion_AP_explanation_addendum_01}/` | Local only |

## Push blocker

Attempt: `git push --porcelain origin HEAD:refs/heads/main` with terminal prompting disabled. Exit status 128.

```text
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

No usable GitHub authentication was available to Git. This is an authentication failure, not a branch-protection rejection; the protected-branch fallback was not applicable. No credential files were read, credentials requested, alternate authentication route attempted or remote changed. The experiment gate remains closed.

## Included and excluded material

Included: selectively reviewed source, tests, existing configuration, compact Markdown/JSON reports and validation/provenance receipts, plus selected final plots. The encoder comparison is five folds; the selected-model robustness and adaptive-fusion results are completed one-fold pilots and are not relabelled as five-fold results. The backbone study and its two later numerical diagnostics are separate commits.

Deliberately excluded and preserved locally:

- Raw datasets, model-weight blobs, extracted payloads, caches, generated temporary/runtime files and locks.
- All globally ignored CSV prediction/metric tables and ZIP review packages; no force-add or `.gitignore` exception was introduced.
- Large membership/frame manifests, full Git-state dumps, old intermediate snapshots and duplicated evidence bundles.
- Generated text test transcripts, preserved unchanged; compact JSON test/check receipts were committed instead.
- The Matplotlib font cache, explicitly unstaged before the diagnostic commit.
- Unrelated `REPO_MAP.md` edits, all twenty pre-existing presentation-asset deletions, the deleted `src/shared/README.md`, and unrelated untracked presentation, walkthrough, EDA, bootstrap and test work.

This is selective Git versioning of suitable scientific material, not a remote backup of ignored datasets, predictions, caches or model blobs. Full selected path lists and excluded categories/examples are in `selection/commit_groups.json`; the exact staged lists are in `commits/*_staged_files.txt`.

## Checks and existing whitespace findings

Every commit was preceded by an exact path-set check and `git diff --cached --check`. The encoder and diagnostic final checks passed. The other three checks reported pre-existing whitespace; those scientific files were retained verbatim:

- Robustness: `code/prefix.py` and its preserved repair snapshot have an extra final blank line; `code/selection.py:151` has trailing whitespace.
- Adaptive pilot: original `ASSIGNMENT.md` uses CRLF line endings that Git flags as trailing whitespace; `code/prefix.py` has an extra final blank line.
- Backbone study: `source/amendment_report.py:23` has trailing whitespace.

These failures were recorded rather than hidden or reported as passing. No scientific code or original report was normalised to make the check pass. Full output/exit codes are saved in `commits/*_staged_check.txt`.

After committing, the index is empty, the unrelated tracked diff statistics match the initial snapshot exactly, and all newly tracked scientific paths match their working-tree contents. No old validation suite or scientific experiment was rerun.

## Required next action

Restore normal GitHub authentication for this repository, then resume. The next operation is to push the existing five local commits and verify the remote; Phase 1 may proceed only after that succeeds. Do not create duplicate commits or restart the old experiments.

Phase 0 elapsed time to report: 7.1 minutes. Finished UTC: 2026-10-22T19:15:30.614751+00:00.
