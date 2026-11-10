# Cache cleanup evidence — 2026-10-26

**Completed:** 7,241 inventoried cache arrays removed; 71,868,174,336 allocated
bytes (66.9 GiB) unlinked. Available filesystem space increased from about
12.1 GiB to 79.0 GiB. Filesystem activity outside the cleanup can affect this delta.

- [Authorization and prepared plan](plan.json)
- [Measured completion and preservation checks](completion.json)
- [Preflight before eviction](preflight_before.json)
- [Preflight after eviction](preflight_after.json)
- [Validation results](validation.json)
- [Output identities](output_manifest.json)
- [Retention and future recovery requirements](../../REASSEMBLE_CACHE_RETENTION.md)

The local bulk detail files below are deliberately ignored by Git; keep them with
the local audit or an approved external evidence backup. They remain on disk.
Their SHA256 identities are recorded in the compact output manifest:

- `array_inventory.json`: exact cache paths, sizes, allocation, file identities,
  and original recorded array/pixel-content hashes. Cache payloads were not
  rehashed; these historical hashes are explicitly distinguished from new checks.
- `deletion_log.jsonl`: one successful unlink entry per inventoried array.
- `retained_metadata_sha256.json`: 4,536 retained JSON/manifest hashes, freshly
  checked before and after cleanup.
- `protected_files_metadata.json`: filesystem identities of 111,916 retained
  files across the affected study areas. Compared before/after; their contents
  were not all rehashed.

`cleanup_driver.py.txt` is an audit snapshot of the one-off cleanup procedure,
not a future regeneration command. No training, GPU computation, data download
or cache reconstruction occurred. Historical metadata and results were preserved;
the original Task 1 cancellation remains in force. Fresh numerical reproduction
has not been demonstrated. Use the separate read-only preflight before future reuse.
