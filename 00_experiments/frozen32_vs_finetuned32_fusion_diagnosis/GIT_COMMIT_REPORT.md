# Git commit and remote gate report

The earlier authentication failure is preserved in the Phase0 handoff. The user subsequently committed/pushed the completed work. This resume verified the live GitHub ref before creating the new experiment; no duplicate commit or push was necessary.

Branch: `main`; remote: `origin` (`https://github.com/Parth-0804/pi-multimodal-ad.git`).
Verified local and remote HEAD: `29b8ca4bc3726e246a8202078163127a604aa26a`.
Verified at: 2026-10-22T19:27:37.977219+00:00.

| Commit | Message | Task | Remote evidence |
|---|---|---|---|
| `8e09335501f384fd43b59faf63785cb34de51247` | reassemble: add frozen CNN vs hybrid encoder study | `encoder` | Present in verified origin/main history |
| `3a5f5f117577355ab20d827d2ae35d79dbb4b0e6` | reassemble: add selected-model robustness study | `noise` | Present in verified origin/main history |
| `a03450852f705a310fd12b6e7ca83592c2cbcf05` | reassemble: add quality-aware fusion robustness pilot | `adaptive` | Present in verified origin/main history |
| `4f563c168e4a493a87e5361474157b0562cc4ef4` | reassemble: add frame-count and backbone fine-tuning study | `backbone` | Present in verified origin/main history |
| `411b2d2c6381008164a870d7e6423fb0ae0d1060` | reassemble: add fusion AP diagnostic analysis | `diagnostic` | Present in verified origin/main history |

The current remote descendant also includes the user’s later commits. No existing history was rewritten. No files were staged, committed or pushed again during this resume.

The prior selected commits deliberately excluded raw datasets, weights, caches, ignored CSV/ZIP bulk, generated runtime files and unrelated dirty changes. The subsequent user commits are preserved as-is; no tracking-policy cleanup is attempted. Existing whitespace check findings remain recorded in the Phase0 report, with historical scientific files unchanged.

Evidence: `results/provenance/remote_gate_receipt.json`; original phase0 record `../completed_reassemble_work_git_handoff_01/GIT_COMMIT_REPORT.md`.

New scientific work stays under this study directory. The task’s push gate is CLEARED, and that status does not imply any new experimental result.
