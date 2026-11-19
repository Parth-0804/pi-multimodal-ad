# Version-control handoff for the completed 32-frame study

This handoff packages the existing study without changing its scientific
source, configuration, figures, metrics, predictions or conclusions. It does
not authorize or perform another experiment. The earlier
`GIT_COMMIT_REPORT.md` remains the historical record of the prerequisite
commits; it is not a claim that this new study had already been pushed.

The requested single commit message is:

`Add frozen vs fine-tuned 32-frame study and findings`

## Included evidence

- Study source, tests, configuration, locked protocol and final README.
- The unchanged results summary, 15 compact comparison tables, and five plots
  in PNG and editable SVG form.
- Exact cohort/frame and partition manifests, input/output hash manifests,
  completed fit manifests, calibration metadata, F2 model metadata, two-row
  training curves, update/replay check reports and software provenance.
- Small verification logs, including the documented early preflight attempts.

The cohort/frame manifest (14,305,320 bytes) and partition manifest
(2,372,219 bytes) are byte-identical to the already tracked manifests in
`../visual_backbone_one_day/run_01_two_epoch_finetuning/data_manifests/`.
The new paths reuse existing Git blobs; their contents are not new uploads.

`VERSION_CONTROL_MANIFEST.json` records selected payload sizes and SHA256
identities. Git itself covers that manifest. The study-local `.gitignore`
explicitly allows only the selected tables, curves and check logs while
keeping the repository-wide ignore policy unchanged.

## Retained locally and excluded from Git

- All CNN/head model files and optimizer checkpoints, including `*.pt`.
- Feature/pixel caches and generated Matplotlib caches.
- Per-action assessment, OOF and calibration prediction banks. Their existing
  relative paths and hashes remain in the retained scientific manifests.
- `results/REVIEW_PACKAGE.zip`, runtime logs/events and writer locks.
- Generated synthetic report fixtures and local Git-operation evidence.

These files remain on disk. A successful Git push does not back up the
excluded checkpoints, prediction banks, caches or ZIP. The ZIP also excludes
model/optimizer blobs. Reproduction that needs those artifacts depends on
their separately retained local copies and the referenced original study.

## Static verification for this handoff

Before staging, inspection confirmed 100 completed visual-fit manifests:
75 new and 25 reused, with two epochs in every fit and 25 roles per
seed/condition cell. Each cell has five matched outer folds and the same
4,530 assessment actions, including 509 failures. The recorded resumed-session
runtime is 78,646.272259 seconds; the conclusion remains `CAUSE_NOT_RESOLVED`.

The ten source/test hashes and 797 retained output hashes matched the saved
completion manifests. This handoff checks existing evidence; it does not
rescore metrics, load models, repeat tests or rerun training/inference.

The base branch is `main`, with configured upstream `origin/main`. The live
remote ref and local HEAD both equalled
`29b8ca4bc3726e246a8202078163127a604aa26a` before staging. No unrelated tracked
changes, staged changes or untracked paths outside this study were present.
No active custom Git hooks were found.

## Staged whitespace review

`git diff --cached --check` reports formatting already present in 13 retained
files: trailing whitespace in the five generated SVG plots, CRLF line endings
in the verbatim execution request, and final blank lines in six source files
and one test file. Every flagged file matches the saved scientific completion
hash. These findings are recorded rather than normalized: the figures,
request and original source/test snapshots remain byte-identical. The new
administrative tracking files have no whitespace findings.

The resulting commit hash and push outcome are recorded after the operation
in the local `git_handoff/COMMIT_PUSH_RESULT.md` and in the final response;
they are not embedded circularly in the commit they identify. This local
handoff folder is intentionally ignored. Existing study files are preserved.
