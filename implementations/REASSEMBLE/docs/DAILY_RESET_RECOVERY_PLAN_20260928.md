# Daily GPU/VM reset recovery plan

Status: inspected and proposed; recovery changes and automatic startup are NOT yet implemented. No training process was started or stopped during this inspection.

## Observed state

At 2026-09-28 09:32 UTC, no training processes were active and the T4 reported zero utilization and allocated memory. The VM booted at 04:00:09 UTC (06:00:09 Europe/Berlin). The last sensor-hybrid log entry was 03:59:55 UTC. This is consistent with interruption by the daily reset reported by the researcher. Existing `running` status files refer to dead processes.

Run: `runs/reassemble/additional_improvements_executed/20260928T000346Z`.

- Task 3 and the approved frozen-prefix cache are complete.
- Tasks 1, 2 and 4 remain incomplete.
- Supervisor skips completed stages and individual fitting functions reuse completed fits. This is not arbitrary mid-training recovery.
- `src/reassemble/additional_improvements/finetune.py` saves live metric history each epoch, but model state only after a complete fit. Optimizer, mixed-precision scaler and random-generator state are not currently persisted for interruption recovery.
- The supervisor depends on four separately launched CPU sensor-bank workers; restarting only the supervisor is insufficient.
- Some NPZ outputs are written directly before their identity sidecars. A reboot during writing can leave an incomplete pair. Validate these rather than trusting existence or silently deleting/replacing them.
- No user crontab or user systemd service directory was present at inspection.

## Recommended next implementation

1. Inventory/hash completed checkpoints, prediction files and cache/sidecar pairs. Preserve any interrupted or invalid outputs with an explicit recovery record; never overwrite completed evidence. Reuse the fixed folds, seeds, configurations and experiment budgets.
2. Add a separately reviewable interruption-recovery change before V-FT starts. Save model, optimizer, mixed-precision scaler, random-generator states, epoch/batch position, data order, best-selection state and stopping history atomically at safe optimizer-step boundaries. Target a few minutes of recoverable progress, with checkpoint size/overhead measured. Do not change `neural.py`/`models.py` identities of completed fits or silently invalidate their signatures.
3. Verify interrupted/resumed versus uninterrupted execution on a tiny deterministic test, including predictions, optimizer state and stopping decisions. This verifies recovery mechanics, not new scientific performance. Preserve code/config/checkpoint identities.
4. Add a single-instance launcher for the existing supervisor and missing CPU shards. Reuse completed units; retain new attempt logs. Distinguish planned reset interruption from a genuine exception. Stop for scientific/preservation failures rather than retrying indefinitely.
5. Configure automatic startup after reboot with a GPU-readiness check, and retry startup around 06:10 Europe/Berlin if necessary. Record the actual installation and verify it. A repository script, detached shell or tmux alone does not provide reboot startup. If the VM remains powered off after reset, external VM startup must be handled separately.
6. Request a checkpoint and orderly stop around 05:50 Europe/Berlin, then resume after the reset. Periodic atomic checkpoints still protect against an earlier unexpected reset. Keep existing two-GPU-job/four-CPU-worker resource bounds and storage floors.
7. Update the durable queue continuation/status with actual process identities and recovery attempts. Once the original bounded work is complete, stop; no budget expansion, architecture changes or automatic combination of winners.

## Time estimate

The retained planning estimate is roughly 3–6 more days of runtime after resumption, dominated by 75 bounded V-FT fits whose actual throughput has not yet been measured. It is not a verified deadline. A 05:50–06:10 pause consumes about 20 minutes/day if the machine promptly returns; boot delays and replay add overhead. Refine the estimate after the first real resumed work and completed V-FT fits. Time while the queue is stopped does not reduce the remaining compute.

The completed validity audit remains sealed and separate. Human review can proceed while these exploratory runs execute. Do not alter its outputs, the completed studies, raw data or external Reasoning Record.
