# REASSEMBLE storage preflight after PHM retirement

Measured 2026-09-27T13:37:16.712454+00:00. **PREFERRED STORAGE PASS — STORAGE GO.**

Available root-filesystem capacity is **403.37 GiB**
(433,111,760,896 bytes), exceeding both the 160 GiB minimum and
200 GiB preferred thresholds. The repository occupies 51G according to `du -sh`.
The filesystem remains `/dev/sda1`, ext4, mounted at `/`; paths sharing it do
not provide additional independent capacity. Inodes are 1% used.

The authorized PHM raw retirement released 355.28 GiB.
See [PHM retirement report](../../phm2026/PHM_RAW_RETIREMENT_REPORT.md) and
[measured commands and exact bytes](../../phm2026/post_retirement_storage.json).
`df -h` and `df -BG` both round available capacity to 404G.

This dated report supersedes only the capacity decision in the preserved
[earlier preflight](STORAGE_PREFLIGHT.md). Its official-source metadata and
hardware observations remain historical observations; they were not re-fetched.
The previously reported main archive size was 54.8 GiB. Extracted size remains
unknown until archive inspection. Passing a workspace threshold does not
establish the eventual extracted/cache size.

No REASSEMBLE download, extraction, data-root creation or training occurred.
The proposed external `../datasets/REASSEMBLE` location still shares this disk;
this report does not change filesystem permissions or authorize work there.
The next phase is a separately authorized REASSEMBLE acquisition and bounded
archive inspection using the current official record and an explicit data root.

STORAGE GO — PREFERRED STORAGE PASS
