# D1.2 checkpoint — HDF5 and sensor structural profile

Status: **COMPLETE WITH BOUNDED PHM COVERAGE**  
Evidence date: `2026-08-13`

## Exact source

D1.2 consumes only the exact D1.1 run
`20260813T202043619114Z-ad7f9832`. The source artifact hashes are validated
before selection:

- `tables/asset_inventory.parquet`:
  `3e6b1c488fab9faa5b3700187d3b789469b8020ff04c6f4c5f4239da11d9ab4e`
- `tables/archive_members.parquet`:
  `01bfc91ed669f93502f9bb2225e58bc4069184fae16242964758809881c3ae3d`

No “latest run” discovery is used.

## Generated D1.2 runs

- Representative metadata run:
  `20260813T212734652736Z-f7c665fd`
- Deterministic sampled-statistics run (one HF member, 128 values per dataset):
  `20260813T212817486478Z-f7c665fd`

The metadata run selected one D1.1 source in each of high-frequency,
low-frequency, and condition-indicator modalities. Because each selected
LF/CI source is a nested per-run ZIP, this covered 745 HDF5 members (1 direct
HF + 372 LF + 372 CI), 27,165 datasets, and 68,327,640 materialized bytes.
All 745 members were readable. Its tables contain exact shapes, dtypes,
chunks, compression, attributes, evidenced units/rates/times, run lineage,
schema IDs, unknown paths, and null value statistics. CSV and Parquet row
counts match, and every declared output hash was revalidated.

The sampled run covered one HF member, 83 datasets, and 33,577,784
materialized bytes. All 83 dataset rows use deterministic sampled statistics.
No complete full-value scan was run.

## Evidence highlights

The representative run observed 13 file-schema variants, 12 exact shape
families, and float32, float64, and uint16 datasets. Evidenced rates included
0.25 Hz, 1 Hz, 100,000 Hz, and approximately 102,400 Hz; every rate retains
its source attribute or `1/wf_increment` derivation. The 102,400 Hz value was
derived from a recorded interval, not supplied as a fallback.

Unknown paths are preserved. In the representative run these include DM4500
and ICM2 bins and transform datasets. Rank-greater-than-one layouts retain
their exact shape; the generic sample/channel counts use an explicitly
documented axis-0 assumption and are not treated as proven physical layout.

The representative nested Run-1 LF/CI inputs contain 446 internal filenames
with a Run-2 token. The nested archive Run-1 remains authoritative and the
conflicting token is retained as warning evidence, without renaming or
excluding any raw member.

## Resource and cost decision

A complete metadata run was **not** launched. D1.1 reports 7,124 direct HF
members with about 354.5 GiB compressed and 533.1 GiB uncompressed payload.
Seekable HDF5 inspection would therefore require at least about 887.6 GiB of
archive-read plus temporary-write traffic before filesystem and HDF5 metadata
reads. The largest known direct member is about 526.8 MiB.

The representative metadata run completed its profiling phase in 29.4 s and
used at most one member plus one small nested container at a time; observed
recorded member peak was 33.6 MB. Extrapolation is uncertain because direct HF
sizes and schemas vary. Conservative planning estimates are:

| Mode | Complete-run estimate | Main cost |
|---|---|---|
| metadata | roughly 1.5–6 h; about 0.9 TiB minimum I/O; potentially around one million output rows | decompress and materialize every member, HDF5 metadata traversal |
| sampled (4,096 points/dataset) | roughly 3–12 h; metadata I/O plus bounded value reads | many deterministic reads, especially multidimensional datasets |
| full values | roughly 4–16+ h; at least another 0.5 TiB value pass and over 1.4 TiB aggregate traffic | complete numeric reads and statistics CPU |

These are capacity estimates, not measured full-run timings. Full mode is
gated by an explicit positive source limit in both CLI and profiling API.
Arrays are read in multidimensional tiles bounded by `max_block_bytes`;
virtual and external-storage datasets are never dereferenced for statistics.

## Validation

- Focused D1.2 suite: `31 passed`
- Complete unit suite: `64 passed in 7.92s`
- Black check: `29 files would be left unchanged`
- `pip check`: no broken requirements
- Dry run: 7,164 source rows discovered; three selected; no archive opened and
  no output written
- Full mode without a positive limit: rejected with exit code 2 before raw
  payload access
- Temporary cleanup: no `pi_multimodal_archive_*` directory remained
- Generated output-manifest SHA-256 values: all revalidated

## Limitations carried forward

- Coverage is representative, not complete across every experiment/run.
- Metadata mode does not establish constant arrays, NaN/Inf counts, extrema,
  mean, or standard deviation; those columns remain null.
- Sampled statistics are not whole-array proofs.
- HDF timestamps are accepted as UTC only when the source attribute carries an
  explicit timezone.
- Oil/environment role prefixes are supported, but none should be claimed
  present outside generated rows that actually use those roles.
- Complete archive integrity, target semantics, and a six-hour interpretation
  remain unresolved.

No raw file, Intel data, historical output, or `.gitignore` content was
modified. D1.3 may begin from this checkpoint.
