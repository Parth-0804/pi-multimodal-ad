# Study 2 acquisition and audit

The frozen research contract is `RESEARCH_CONTRACT.md`. This execution covers
acquisition, actual-schema inventory, label/completeness support and split safety.
It does not authorize training. Review `PHASE_A_B_GATE_REPORT.md` at completion.

From repository root, use the existing environment:

```bash
ma_thesis_env/bin/python -B scripts/reassemble/00_acquire.py --run-dir runs/reassemble/<unique-run>
ma_thesis_env/bin/python -B scripts/reassemble/01_inventory.py --run-dir runs/reassemble/<unique-run> --workers 3
ma_thesis_env/bin/python -B scripts/reassemble/02_audit.py --run-dir runs/reassemble/<unique-run>
ma_thesis_env/bin/python -B -m pytest -q tests/reassemble
```

Create the unique run directory and copy the configuration there before running.
The default config is `configs/reassemble/audit.json`; pass `--config` for a
reviewed alternate. `data_root` resolves relative to the invoking repository
root, defaults to `../datasets`, and contains `REASSEMBLE/downloads`, `raw`, and
`cache`. Keep these outside Git. Original archives are retained.

Acquisition resolves the official TU Wien record API, confirms its DOI and the
frozen data.zip MD5, continues `.part` transfers with curl, and verifies all
published sizes/checksums. It scans ZIP CRCs and path safety before extraction,
checks expanded size against available capacity, and promotes a fresh staging
directory only after successful extraction. An existing raw directory is never
overwritten. Failed checksum bytes are preserved under a uniquely dated name;
one fresh retry is attempted. A partial extraction requires manual inspection
before a new attempt; automatic destructive cleanup is intentionally absent.

Inventory opens HDF5 read-only and never imports the upstream loader runtime.
It stores complete actual schemas, SHA256s, segment labels and annotation text
for auditing only, per-stream timestamp/quality evidence and warnings. Encoded
media caches live outside Git under a source SHA256 key. The audit uses 16
in-segment video frame checks, OpenCV and libsndfile; no system ffmpeg installation
or new dependency was required. No raw event payload is decoded for this phase.

Per-recording JSON checkpoints support interrupted inventory continuation in the
same run. Continuation requires unchanged source size and nanosecond mtime; raw
inputs are immutable. When code or configuration changes, use a fresh run unless
no recording checkpoint has yet been generated. The final aggregate reports
refuse overwriting existing fixed output paths; use a new reviewed output
namespace for a later audit instead of replacing historical evidence.

Audio nominal zero-based coverage follows the upstream visualization convention.
A decodable file does not establish its alignment to HDF5 time; audio remains
secondary until that origin/drift is verified. The report may support the
predeclared visual+sensor cohort without audio. Quality proxies are descriptive;
training-fold scaling, supervised feature selection and model calibration belong
to later approved work.

Official references:

- https://researchdata.tuwien.ac.at/records/0ewrv-8cb44
- https://github.com/TUWIEN-ASL/REASSEMBLE/tree/432cc15ce3e028edc2f98a786f28bf6baf31ac6f
- https://tuwien-asl.github.io/REASSEMBLE_page/

To overlap auditing with extraction safely, after `archive_inventory.json`
exists (all archives have passed CRC), the optional scheduler is:

```bash
ma_thesis_env/bin/python -B scripts/reassemble/01_inventory_during_extraction.py --run-dir runs/reassemble/<inventory-run> --acquisition-run runs/reassemble/<acquisition-run> --workers 3
```

It schedules only members with their complete manifest size, handles the atomic
promotion of the staging directory, and records the same per-file checkpoints.
After extraction/audit completion, run `01_inventory.py` on that inventory run
to assemble its Parquet tables from verified checkpoints. Preserve acquisition
provenance alongside the inventory run before generating the final reports.
