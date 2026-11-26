# REASSEMBLE cache retention and recovery — 2026-10-26

## Researcher-authorized retention change

On 2026-10-26 the researcher explicitly requested removal of the two derived
caches identified in the storage review, documentation of recovery requirements,
and code prechecks. This is a narrow exception to the previous cache-preservation
instruction in the [September handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md).
Its experimental conclusions and the cancellation of Task 1 remain unchanged.
Historical reports, manifests and `complete.json` files describe past execution;
they do not establish present cache availability.

The exact deletion inventory, retained-metadata checks and measured outcome are
recorded in [the dated cleanup evidence](cache_cleanup/20261026T211622Z/).
Consult `completion.json` there for final status; a plan alone does not prove deletion.

**Completed:** 7,241 arrays removed, freeing approximately **66.9 GiB**; available
filesystem space was approximately **79.0 GiB** afterward. All 4,536 retained
metadata hashes matched, and filesystem metadata for 111,916 other study files
was unchanged. The evidence directory keeps bulky audit inventories locally
ignored by Git and compact summaries/output identities available for review.

| Derived bulk selected for removal | Approximate allocated size before cleanup | Preserved recovery evidence |
|---|---:|---|
| `runs/reassemble/additional_improvements_executed/20260928T000346Z/01_temporal_visual/frozen_prefix/*.npz` | 43.2 GiB; 4,530 arrays | All 4,534 JSON files, including original per-array hashes, model identity, manifest and historical timing; about 19 MiB |
| `parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/pixels/**/*.npz` | 23.8 GiB; 2,711 cached entries | Cohort/frame manifest with frame indices and pixel-content hashes, configuration, feature arrays and source code |

Only the enumerated `.npz` bulk is covered. Raw data, encoded source videos,
pretrained weights, learned checkpoints, recovery states, predictions, feature
arrays outside these two roots, historical reports and Git history are retained.
The old bootstrap workspace itself is retained: newer workspaces point into it
using symlinks. Each emptied cache receives an additive `CACHE_EVICTED.json`
record; existing historical metadata is not rewritten.

## Preflight before any future reuse

Run from the repository root:

```bash
ma_thesis_env/bin/python -B scripts/reassemble/check_cache_availability.py --cache prefix
ma_thesis_env/bin/python -B scripts/reassemble/check_cache_availability.py --cache pixels
```

The standard-library checker reads saved manifests and filesystem metadata only.
It never decodes data, initializes a GPU, downloads, trains or writes files.
Exit 2 means required arrays/manifests/inputs are missing or inconsistent.
After this eviction the prefix check must report missing arrays despite the
preserved historical `complete.json`. The pixel check can return exit 0 with
`READY_WITH_REDECODING`, because disk-cached pixels are optional; it checks saved
frame selection, pixel hashes, video size/mtime and local model-file availability.
Neither exit 0 nor file-size agreement proves content identity, numerical parity,
scientific validity or permission to run an experiment.

This is a standalone prerequisite, not an automatic hook in the old entry points.
Historical experiment code and source snapshots are unchanged to preserve their
identities. Do not bypass the preflight and assume old completion flags are live.

## Prefix-cache recovery requires a new cache-only runner

The [historical generator](../../src/reassemble/additional_improvements/prefix_cache.py)
contains the extraction method, but it is **not safe to rerun in place**:

- It hard-codes the historical run through `execution.json`, writes progress and
  model/manifest/completion records there, and `write()` rejects changed existing
  metadata. A fresh elapsed time alone conflicts with the old completion record.
- Legacy `finetune.main()` chooses `PrefixSource` merely because `complete.json`
  exists; `PrefixSource` then opens the deleted arrays without a cache-miss fallback.
- `visual_resume` and the legacy supervisor are training/resumption entry points.
  Task 1 was cancelled; cache cleanup does not authorize restarting it.

Before reuse, develop and review a separate **cache-only extraction runner** with
a new configurable output directory, no historical progress/report writes, no
training/resumption calls, and no downloads. Reuse the original frame indices,
preprocessor, model revision, deterministic settings, 32-frame extraction batches,
precision and frozen-prefix boundary. Retain source/video/model identities and
compare regenerated arrays against the preserved original identities. Compare
array contents separately if archive-byte hashes differ; do not silently replace
the historical manifest or claim exact reproduction from matching file sizes.
Consumers need an explicit new cache-path option before using the replacement.

Original extraction completed all 4,530 segments in **6,034.65 seconds (1 h 41 min)**,
as recorded in the preserved `frozen_prefix/complete.json`. Input-path checks found
all 148 encoded videos and required feature/model files. This is historical runtime
and existence evidence, not a fresh recovery benchmark or content verification.
The existing generator requires 30 GiB free during extraction; a full replacement
also needs approximately 43.2 GiB storage. Keep that headroom or review a bounded
alternative rather than silently weakening the guard. Regeneration has not been
implemented or executed by this cleanup.

## Pixel-cache recovery already has decoding logic

The saved `source/data.py:pixels`, `source/pixel_access.py:input_pixels` and
`source/fast_input.py:readonly_pixels` in the old/new visual workspaces implement
cache-miss decoding. They use the recorded encoded video, 32-frame selections,
16-frame subset, pinned preprocessing and saved uncompressed pixel-content SHA256.
Decoding requires the encoded videos and processor files; no model fit is needed.
The 2,711 removed entries were a bounded partial cache of 4,530 samples, not a
separately irreplaceable dataset. A complete cold-cache rebuild time was not
isolated; the historical 2.84-hour feature pass included mixed cache access and CNN
extraction and is not a measured pixel-cache rebuild duration.

Reuse this decoding logic only through a newly configured run/cache directory.
Some loaders write/evict cache entries, and the newer workspace's `shared_cache`
symlinks lead back into the old workspace. A future replay must bind an isolated
cache path or use its read-only on-miss decoding route; do not run the whole
historical preparation/training driver merely to recreate cached pixels. Validate
a bounded sample against saved pixel-content hashes before wider use.

## Checks performed and limits

Cleanup records contain before/after disk space, the exact array inventory and
checks that retained metadata stayed unchanged. Synthetic tests cover stale
completion flags, missing/changed arrays, escaping paths, cold pixel caches and
missing/changed source-video metadata. No real data were decoded, no cache was
regenerated, no model forward/training ran, and no fresh numerical reproduction
is claimed. Full recovery remains separately scoped work when a future run needs it.
