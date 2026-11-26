# Data and credential boundaries

## Immutable raw-data roots

The following repository-relative paths are immutable:

- `gtc-data-experiment/**` — PHM North America 2026 archives and local
  dataset-adjacent material;
- `data/Full Dataset/**` — historical Intel welding raw data.

The Intel dataset is outside the active PHM scope, but it remains raw data and
receives the same protection.

Never delete, move, rename, overwrite, rewrite, extract into, recompress, or
deduplicate anything in these roots. A suspected duplicate, corrupt archive, or
label mismatch must be reported; filename-based cleanup is prohibited.

## Permitted read-only operations

Unless a phase grants narrower authority, safe operations are limited to:

- listing paths and filesystem metadata;
- comparing expected and present archive names;
- opening archives read-only for bounded metadata inspection;
- reading representative members only when explicitly required by an approved
  integrity or analysis phase;
- recording both outer-archive and internal-member identity.

Do not perform full archive hashing, CRC scans, extraction, HDF5 payload scans,
or expensive EDA without explicit approval. Later code should prefer streaming
and bounded reads. If temporary extraction is necessary, use an isolated
temporary directory outside raw roots, clean only known temporary paths, and
retain source provenance.

## Credentials and private state

Do not read, print, copy, summarize, commit, or include the contents of:

- `synology_cookies.txt`;
- `.env` and environment-specific variants;
- tokens, passwords, private keys, cookies, or session files;
- local authentication or package-index configuration.

It is acceptable to verify that a sensitive path is ignored without reading
it. If a secret appears tracked or in output, stop work and notify the
researcher without reproducing the value.

## Historical experiment boundary

Everything under `experiments/exp_a_initial_eda_r1_r3_r5/**` is a protected
historical record during restructuring. This includes scripts, notes,
configuration snapshots, tables, figures, reports, and cached images.

Historical files are not immutable raw data, but they must not be edited,
overwritten, moved, or deleted until a validated replacement exists and a later
phase receives explicit approval.

## Safe test data

Tests must use tiny synthetic fixtures created for the repository. Never copy
real HDF5 members, images, sensor rows, archive payloads, or credentials into
test fixtures. Synthetic archives should contain no confidential or licensed
dataset content.

## Git boundary

Never commit:

- raw PHM or Intel data;
- ZIP/HDF5 payloads or extracted raw members;
- virtual environments and package caches;
- credentials or session material;
- Python, notebook, test, IDE, or tool caches;
- large temporary or exploratory outputs.

The current ignore rules provide broad protection but have known precision gaps
documented in `docs/restructuring/BASELINE.md`. Changes to that policy belong
to Phase 3.

## Stop conditions

Stop and request confirmation if an operation would:

- alter a raw or historical protected path;
- expose or repurpose credentials;
- require full payload scanning or large extraction;
- overwrite an existing result;
- broaden the approved phase;
- delete, move, or rename any repository material.
