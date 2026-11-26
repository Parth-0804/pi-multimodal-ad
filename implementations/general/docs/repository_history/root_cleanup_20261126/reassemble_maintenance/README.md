# REASSEMBLE maintenance-documentation relocation — 26 November 2026

Moved `docs/maintenance/` to `implementations/REASSEMBLE/docs/maintenance/` by one same-filesystem directory rename. No raw data, cache payload, checkpoint or experiment source was moved or executed.

`BEFORE.json` and `AFTER.json` record every file’s device, inode, size, mode and modification time. All 14 file identities and 11 bounded file hashes matched immediately after relocation. The 13 dated cleanup-evidence files remain unchanged. The three large historical inventories received metadata checks only, not new content hashes.

The current retention guide was subsequently updated only to repair its handoff link and the read-only checker command path. Its exact preimage is under `preimages/`; historical report and source identities inside the dated evidence remain unchanged. The current guide and dated README’s ten local links resolve. `ACTIONS.jsonl` records the rename and guide edits.

No commit, push, experiment rerun, cache reconstruction or deletion was performed.
