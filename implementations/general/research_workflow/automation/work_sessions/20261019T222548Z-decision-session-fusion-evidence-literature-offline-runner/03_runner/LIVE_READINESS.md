# Live readiness

| Area | State | Evidence / remaining condition |
| --- | --- | --- |
| Persistent synthetic DAG and states | IMPLEMENTED / OFFLINE_TESTED | controller.py;33 tests; runtime event log |
| Fixed implementer/verifier handoff | IMPLEMENTED / OFFLINE_TESTED | Separate trusted fake subprocesses; actual JSON/hash/validity checks |
| Approval rejection / Task4 exclusion | OFFLINE_TESTED SYNTHETIC ONLY | Missing/malformed/revoked/mismatched/forged fixture cases and unknown operation refusal; no real issuer provisioned |
| Path/argument checks | OFFLINE_TESTED APPLICATION CHECKS | Traversal/symlink/unknown operation/argument rejection; no shell-response execution |
| Recovery/locking/stop | OFFLINE_TESTED | Real flock and owned-child termination; no duplicate on complete resume; uncertain interrupted jobs require reconciliation |
| Clean no-work | OFFLINE_TESTED | Completed resume dispatches nothing; status/preview do not change fixture; empty graph explicitly refused |
| Real model adapter | DISABLED / LIVE_UNTESTED | execute() always raises LIVE_DISABLED; no JSON switch enables it |
| Scientific/literature live handlers | ABSENT / BLOCKED | Unknown operations fail; public research in this session used interactive approved browsing, not this runner |
| Host-owned code/policy/approval boundary | NOT ESTABLISHED / BLOCKED | Same filesystem/user privilege can alter files; synthetic signatures and hashes do not protect against that actor |
| Results-blind worker workspace | NOT ESTABLISHED | This session used the explicit nonblind scoping fallback |
| Actual approval/provider/access/budgets | UNAPPROVED / REQUIRED | Must bind exact protocol/code/inputs/commands/output/access/limits outside worker writes, before later live use |
| Scheduling / service | NOT CREATED | No daemon, automation or future activation |

No future training, fine-tuning, inference, feature extraction, corruption generation, external dataset execution or historical Task4 revival is authorized. The current prompt authorizes direct interactive literature/evidence/offline work only. It does not approve a live controller. Live integration is a distinct later decision, with no universal launch command supplied.
