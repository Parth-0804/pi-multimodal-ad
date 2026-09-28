# Correction 001 — checkpoint naming, before completed comparison

First attempt log: `execution.log`. A decimal lambda embedded in a filename was
interpreted by pathlib as a suffix, collapsing different fit names. The signature
assertion stopped the second fit; no cross-fold comparison was produced. Preserve
`fits/outer0_A-CONSTANT_lambda0.*` as an unused first-attempt artifact. Corrected
filenames replace decimal dots with `p`, preserving unique lambda/inner/seed IDs.
Restart uses `execution_attempt2.log`; no original study file is changed.

Also made progress-file temporary names process-specific, allowing CPU fusion
fitting and GPU feature extraction to update separate task statuses safely.
