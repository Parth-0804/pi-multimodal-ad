# Separate setup review — original verdict and repair history

Reviewer: in-session delegated AI agent /root/controller_setup_reviewer, separate context, no model identity asserted. It used read-only text/hash inspection; it reports no writes, imports, test execution or model requests. Shared filesystem access means reviewer-specific OS-enforced isolation was not demonstrated. This is an additional AI code/evidence review, not scientific certification or user approval.

Original verdict: REVISION_REQUIRED at the pre-repair checkpoint. Final repair recheck pending.

| ID | Severity | Primary source at original checkpoint | Finding | Coordinator correction in final repair2 |
|---|---|---|---|---|
| R1 | HIGH | runner/controller.py464–478 | Resume left completed dependents DONE after upstream artifact invalidation; a pending descendant could dispatch | Dependency-first revalidation transitively withdraws DONE trust to NEEDS_RECONCILIATION/INVALID and blocks pending descendants; artifacts preserved; regression30 |
| R2 | MEDIUM | runner/controller.py473–478 | Queue list order could prematurely block a valid dependency DAG | Topological/eligible scheduling independent of input list order; regression29 |
| R3 | LOW | config/derived_queue.json6–17,699–712 at original read | Audit-only scope fields mixed with bootstrap derivation | Effective bootstrap scope explicit; inherited effective scope namespaced in derivation |

Coordinator also demonstrated/fixed related cached-config drift (regression31) in the same final repair2. All3 new checks failed before code repair and passed in the final31-check suite. No third repair cycle is available. Earlier logs and code snapshots remain in evidence/repair_cycle01, repair_cycle02 and test_run_01/02/03.txt.

Independently inspected by reviewer: original controller.py1–555 SHA2566a6d888744a37e448762874e527baadd0f2ea3ab94b2455baedf554446b523e5; adapters.py1–58 cfc6231b7c9ae8a3591846ea87300ec3d758f6a14d3ce43c92eb8a8c5f7b5308; synthetic_worker.py1–42 355ed3c0851d443562c653918e46395b8adbac1bc7795d061f068730cc449802; tests/test_controller.py1–277 70fe8a7a1f248a1959150dd8f756117caa0f1c37258ac9a06deea1a4dc02010e. Full new-source identifiers are in evidence/CODE_IDENTITIES.json; preserved preimages identify the reviewed older checkpoint.

Reviewer also inspected all6 schemas, report mapping, README, USER_DECISIONS, draft SETUP_RESULT, derived queue authorization/dependency/acceptance/provenance sections, recorded28-test runs/repair log/11-command smoke index and representative preview/completed demo/activation refusal/execution receipt/negative-result artifact/review response. It did not independently execute tests. Original inspected TEST_SUMMARY hash0c157b6d95ddf0f235d248b083e17fb72d1088b2d2da9896c53055f4719a3f8f; test_run_02 e570a4d7cc566bdd4e4b62766634921c97bea47e804448fe26c6a1e2c70fb337; CLI_SMOKE d50a4b3a13b602ef901d64f9e910856f225dfcaa1a184f8676afed907f0c8486. Negative artifact hash80f4daeb7523ddbda82957c3957336c97b6bc6f352279a4962acc615bc2ef606 matched its reviewer receipt.

The reviewer found no additional infrastructure blocker: fixed synthetic operations only, unconditional live refusal, public fixture keys/application path checks properly distinguished from host trust/results isolation, and missing live approvals/handlers stated honestly. The two correctness findings blocked original recovery/progression claims until repaired; they were not silently erased from this handoff.

Evidence checked: independent static code/tests/schema/permission-boundary inspection and recorded offline evidence. Still uncertain: final repair recheck, final preservation/manifest, host isolation and live scientific authorization. Defensible conclusion: original review required a bounded repair; no verdict grants scientific execution.

## Final repair recheck — ACCEPT_WITH_LIMITATIONS

Separate reviewer independently inspected changed source/diffs/hashes and recorded outcomes, without executing tests or writing files. R1 resolved at controller.py487–506: transitive dependency-first withdrawal of DONE trust, pending descendants block. R2 resolved at205–217/487–506: order-independent scheduling. Scope ambiguity resolved in derived-queue diff. Related current-config drift fixed at347–362/368–372. New regressions29–31 failed before repair; final recorded31-test suite passed,0 failures/errors,13.287s. Final smoke index has11 expected outcomes,6 dispatches for the complete demo, no duplicate resume dispatch, exit2/LIVE_DISABLED for activation.

Final reviewer checkpoints: controller.py1a34407b8392a8ff289f0d3d07921a0c5276e7c5c4c1cff1bc68286ac6074fcf; tests11374b3ca738a770c011e71b067cc1ec552d47d839b3c6fcd1d13203c8e08059; derived queue before final setup-status update a9197f466ff79b18b3f229cd1a30d48d20c14c30949a6484f52338c56343fa7c; TEST_SUMMARY16f47dbc2acfaf29ebf2d2daf089825b238c3baa7522cae6dabe026e5ffbe8f1; test_run_033b49d0437ad70b5475eb173d571b34b5601d0040d097c8c6054b675a61b89b29; CLI_SMOKE_FINALfffd9deab7c6fd487291a8079a5f9db9fd65ec9fc024eb233afde2ce1408e213. Adapter/worker unchanged. No unresolved offline implementation blocker identified.

Remaining limits: live host protection/isolation/results blindness, approved exact scope/version/access/budgets and research handlers are absent. Public synthetic signatures/path checks do not provide these. Both repair cycles used. Final preservation, artifact manifest and final setup-state updates are coordinator-only checks outside the reviewer verdict. Additional AI review does not certify science or grant execution authority.
