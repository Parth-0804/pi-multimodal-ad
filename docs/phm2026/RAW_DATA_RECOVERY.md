# PHM A/B/F raw-data recovery

This tooling restores the exact local training inputs recorded in
`artifacts/phm2026/raw_data_manifest.json` (CSV companion alongside it).
The recovery specification is `configs/phm2026/download_manifest.json`.
Raw data stay excluded from Git; code, exact sizes/hashes, recovery instructions
and small validation evidence are versioned. Retirement status and actual space
recovery are recorded separately in `artifacts/phm2026/PHM_RAW_RETIREMENT_REPORT.md`.

## Scope and preservation

The frozen inventory contains 53 files: 52 official raw archives plus a local
research script. High-frequency runs: A 1–5, B 1–7, F 1–8. Each experiment has
one CI archive and one LF/oil/environment archive. Photo archive counts are
A 7, B 9 and F 10, including the named pre-run/break-in archives. All 52 archive
filenames and sizes were matched to a fresh official server listing.

`gtc-data-experiment/inspect_dataset.py` was a local inspection helper, not
organizer data. It is preserved byte-for-byte as
`scripts/phm2026/legacy_inspect_dataset.py`, with its original checksum in both
manifests, and restored locally as part of `--components all`. Its historical
absolute paths and incomplete helper dependencies are preserved as evidence;
it is not invoked by the downloader. No research code is discarded.

The EXP-A Run-2 overlap warning remains applicable. No archive is deduplicated,
renamed or scientifically relabelled. Original destination paths are retained,
including spaces and differing hyphen/underscore conventions. Existing historical
configs continue to use `data_root: gtc-data-experiment` without edits.

## Official source and implementation provenance

The authoritative source is the [PHM Society challenge page](https://data.phmsociety.org/phm-north-america-2026-conference-data-challenge/).
Its Training Data link was verified as
`https://gtc-data.synology.me:51111/sharing/uIrAvzqEh` on 2026-09-27.
By default the CLI resolves the current Training Data hyperlink each invocation;
`--share-url` accepts a reviewed public HTTPS `/sharing/<id>` override. There is
no unofficial mirror or embedded account credential.

The former root `download.py` at commits `d3ce480` and `9a66390` supplied the
working Synology download mechanism: runtime public-share initialization,
`SYNO.FolderSharing.Download` v2 and hexadecimal encoding of a server file path.
That code remains in Git history. Its former single-experiment scanning, weak
size/ZIP validation, workstation path and cookie-file handling were replaced.
The new root file is a small entry point into
`src/pi_multimodal_ad/acquisition/phm_download.py`.

Live inspection of the share's public FileBrowser JavaScript identified
`SYNO.FolderSharing.List` v2. The working list request uses `folder_path`, starting
at `/train`, and `additional=["size"]`; pagination and folder traversal return
server-provided paths. Download requests are generated only for exact manifest
paths confirmed in that listing. Discovery is not a sequence of invented archive
URLs. Public initialization uses the page-advertised bootstrap and a fresh
in-memory cookie jar. No local cookie file, stored session or private credential
is read, logged, exported or reused. TLS verification stays enabled and HTTPS
redirect downgrades are refused. No browser automation is required.

The public listing currently contains 79 files; the restore scope is the exact
52 archives used locally, not all newly available or unrelated server files.
If the remote path or size changes, the downloader stops for review. Recorded
SHA256 verifies exact bytes on eventual restoration; current server availability
does not guarantee permanent future availability.

## Environment and commands

Use Python 3.10+ (the repository environment is Python 3.12). The acquisition
implementation uses only the standard library. This machine has `python3` but no
system `python` alias; activate the repository environment for the requested
`python` commands:

```bash
source ma_thesis_env/bin/activate
python download.py --help
python download.py --list
python download.py --experiments A B F --dry-run
```

Complete thesis subset:

```bash
python download.py --experiments A B F
```

One experiment, or high-frequency vibration only:

```bash
python download.py --experiments A
python download.py --experiments B
python download.py --experiments F
python download.py --experiments F --components high_frequency
```

An external disk (substitute an approved destination):

```bash
python download.py --experiments A B F --data-root /path/to/gtc-data-experiment
```

Component selectors are `all` (default), `high_frequency`, `low_frequency`,
`condition_indicators`, `oil_environment`, `photos`, and `other`.
`low_frequency` includes CI plus LF/oil/environment files. `other` is the
preserved local helper. Only A/B/F experiments are accepted.

The runtime share override, if the official page needs a reviewed correction:

```bash
python download.py --experiments A B F --dry-run --share-url https://gtc-data.synology.me:51111/sharing/uIrAvzqEh
```

A bounded live validation (one MiB, not a full restore):

```bash
python download.py --experiments A B F --transfer-test
```

The range test requires HTTP 206, exact Content-Range/total, ZIP signature and
one MiB of returned bytes. While local raw data exist it also compares those
bytes with the local prefix. The fragment remains in bounded memory only and is
not saved; there is no disk fragment to delete. If range support disappears,
this validation fails closed; a separately reviewed small-file transfer would
be required. It never falls back to an unbounded large-archive transfer.

## Streaming, resume and existing files

Files stream in bounded chunks to `<destination>.part`. Rerun the identical
command to resume. A Range resume must return matching HTTP 206 start/end/total;
otherwise the downloader reports restart required and retains the partial file.
It does not automatically truncate or delete an old `.part` file. Interrupted
transfers retain bytes for a later invocation; completed files are unchanged.
A checksum-failing full partial is retained for explicit review, not promoted.

Before a real transfer, every existing final is checked by size and full SHA256.
A valid final is skipped. A corrupt final is refused unless the user explicitly
passes `--overwrite-corrupt`; even then it remains until the replacement is
complete and verified. Size and SHA256 validation precede atomic rename on the
same filesystem. `.part` files are never treated as completed raw data.

The disk preflight sums bytes remaining after validated existing files and partial
offsets, separately per destination filesystem, and requires 5% additional margin.
It does not silently assume a size for unknown entries: `--allow-unknown-size`
would be required, with a warning. All current recovery entries have exact sizes.
A low-free-space guard also stops a live transfer while preserving its partial.
There are explicit timeouts and bounded exponential retries; Ctrl+C returns 130.

`--list` and `--dry-run` perform live discovery and exact requested inventory
coverage checks without creating the data root or downloading archive payloads.
Existing files are labelled SIZE_MATCH_CHECKSUM_NOT_CHECKED during those modes;
this is not a checksum-valid skip claim. A missing root is supported. These modes
still emit the requested small provenance log outside raw data.

## Provenance and safety gates

Each CLI invocation, including help/failed invocations, writes an exclusive
UTC/UUID log under `artifacts/phm2026/downloads/`. It records selection, mode,
share identity, resolved paths/sizes, completion/skip/failure, transferred-byte
counts and checksum status. It never dumps response headers, private runtime
state, authentication values or credential-bearing URLs.

D1 requires a frozen SHA256 manifest, help/list/dry-run success, exact coverage
and a real bounded official-server transfer. D2 additionally requires offline
tests, documentation, a Git checkpoint, and an exact non-symlink deletion target.
Neither the downloader nor a successful dry-run performs deletion. The current
user authorized retirement of only `gtc-data-experiment/` after D1 and D2; this
is a specific exception to the repository's usual immutable-raw policy, not a
policy change for any other raw tree or historical output.

Before retirement, preserve code and snapshot retained research artifacts. After
retirement, verify their existence/metadata, raw-tree absence, free space and
another A/B/F live dry run. Never alter `.git/`, Intel raw data, runs, historical
experiments, models, reports, environments or scratch evidence to reclaim space.

Offline validation:

```bash
ma_thesis_env/bin/python -B -m pytest -q tests/unit/test_phm_download.py
git diff --check
ma_thesis_env/bin/python -B -m pip check
```

Tests use a local synthetic HTTP Range server and synthetic fixtures, never live
NAS payloads. They cover selection, manifest/path safety, missing roots, range
semantics, partials, interruption, checksums, valid-file skipping, corrupt-file
refusal, disk budget, atomic completion, official-link parsing and listing schema.
