# Section 1 failures and corrections

Before fitting outcomes, verified that prior cohort.parquet retains all annotations;
Section 1 explicitly filters primary_task AND dual_complete and asserts all counts.
No excluded or idle rows enter modelling. All 40 tests passed before training.
No failed training attempt has occurred at this point. Append any later failure;
never erase partial evidence or silently change the frozen protocol.

Synthetic two-epoch forward/backward training passed for both neural branches;
no experimental outcomes were used for these implementation smoke checks.

Pinned image processor inspected: do_normalize=False despite generic model-card wording; actual shipped processor is authoritative. RGB resized to640x640 and divided by255. No preprocessing change made.
