# Extension execution queue — live continuation

Run: `runs/reassemble/additional_improvements_executed/20260928T000346Z`.
Protocol commit `26ae3a7`; initial Task3 `484bd35`; queue/cache source `e665029`.
User authorized no additional wall-time limit and verified frozen-prefix caching.
Original outputs, raw inputs and external Reasoning Record remain protected.

## Running supervisor

`PYTHONPATH=src ma_thesis_env/bin/python -B -m reassemble.additional_improvements.supervisor`

Tool session 75306; log `supervisor_attempt0.log`; state `supervisor_state.json`.
Check processes before resuming. Maximum two real GPU jobs, justified by saved
resource profiles. All budgets, seeds and architectures remain frozen.

Chain A: original branch recovery (105/105 done, clean parity passed) → approved
frozen-prefix extraction (running) → raw pixel corruption bank → partition-safe
visual scoring → wait for sensor banks → matched fusion fits → sealed historical
reference scoring → Task4 report.

Chain B: strict nested sensor hybrid (running) → Task2 report (including selected S-6 checkpoint retention repair) → wait for approved
cache or documented pixel fallback → bounded final-stage fine-tuning → Task1
report. Then final independent numerical/preservation audit and consolidation.

Four CPU sensor-bank workers run separately with one thread each:
`branch_banks sensor --shard N --shards 4`, N=0..3.
Sessions 6245, 93147, 44524, 97924; logs `04_corruption_training/sensor_bank_shardN.log`.
These are live jobs, not blockers. Recovery sensor checkpoints are complete.

## Completed evidence

- Task1 primary: V-MEAN AP .243399; V-TEMP .575180; V-NOPOS .489135.
  Temporal−mean ΔAP +.331781,95% [.287090,.372093]; temporal−no-position
  +.086045,[.055183,.115687]. V-FT remains pending.
- Task2 primary: S-6 AP .255658; S-LONG .285311; S-STATS .429392.
  Long−short +.029652,[.012193,.045106], but long−statistics
  −.144081,[−.186123,−.100893]. S-HYBRID remains pending.
- Task3 fully complete: adaptive−A0 ΔAP +.021014,[.001463,.041888];
  adaptive−constant +.022633,[.003617,.043160]. Recall and ECE deteriorated.
  Report `03_STATIC_ANCHORED_ADAPTATION_RESULTS.md`; retain its bounded claims.
- Independent interim recalculation passed all primary report points, fold/seed
  metrics and contrasts; all148 encoded video metadata identities unchanged.

## Cache authorization and corrections

GPU cached/direct prediction and gradient differences were both exactly zero
at the actual32-image microbatch. Cache unchanged stages0–2 outputs only; stage3
and head retain gradients. Singleton microbatches use the original pixel path.
Ten predetermined samples must support a conservative disk estimate with30GiB
reserve before full extraction. Preserve partial files and use live-pixel FT
if that cache estimate fails. FT itself is not skipped for a cache failure.

First audit used16-image extraction vs32-image FT kernels; strict gradient
parity failed. Preserved and corrected to32 without relaxing tolerance.
Task3 first attempt filename collision was fixed before completed results.
See correction files and protocol amendment. A report-helper indentation error
was caught at import before any report use and fixed; no fit/results changed.

## Remaining checks and continuation rules

Do not edit neural.py/models.py or completed fitting source: checkpoint signatures
protect reuse. All fits are resumable. Inspect errors; continue independent tasks
for isolated failures, stop globally for leakage/protected-input corruption.
No resource blocker is established merely by long runtime. Do not claim completion
while the supervisor or required subtasks remain active. Reports/CONTINUATION.md
updates automatically; this file describes dependencies and resume commands.

Finalization writes the three requested handoffs plus final comparison registry,
metrics and manifests. No winner combination or extra experiment is authorized.

Checkpoint retention review: S-6 selected3/6 logits were saved correctly, but some inner checkpoint files held an alternative best epoch1–6. Task2 report now recovers only missing selected states through one fixed same-budget replay, with saved-logit parity required. This does not change reported predictions or selection. See checkpoint_retention_correction.md.
