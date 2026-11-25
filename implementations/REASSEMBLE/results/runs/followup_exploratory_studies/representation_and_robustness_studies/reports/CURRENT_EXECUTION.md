# Current execution — Task 4 only

complete: Task 4 complete; Task 1 remains paused; no winner combination or new task launched

Task 1 is paused at user request with recovery checkpoints retained. Tasks 2 and 3 are complete. Task 4 has one GPU worker and four one-BLAS-thread sensor workers, followed by scoring, matched fusion, historical references and uncertainty/report generation.

Attempt: `runs/reassemble/additional_improvements_executed/20260928T000346Z/recovery/task4/20260929T135624Z`. Stage logs, source snapshot, bank/branch checks and process identities are inside. Existing completed banks/fits are reused. No full supervisor or final all-task consolidation is launched.

Safe stop is requested at 05:30 Europe/Berlin and workers finish the current committed recording/partition or stage. Some CPU partitions can be long; a VM reset may lose the unfinished unit, not completed banks. No automatic reboot startup is installed. To resume, check all worker processes then run `PYTHONPATH=src ma_thesis_env/bin/python -B -m reassemble.additional_improvements.corruption_resume --attempt-dir <NEW_TIMESTAMPED_DIR>`. Keep fixed seeds, budgets and configuration.
