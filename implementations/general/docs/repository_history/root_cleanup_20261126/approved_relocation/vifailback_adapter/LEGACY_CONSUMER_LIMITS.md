# Remaining legacy execution-path limits

Read-only source inspection on 26 November 2026. No dataset/model imports,
payload reads, fitting, inference, acquisition, preprocessing or replay occurred.
This record distinguishes existing path debt from paths changed by the approved
physical relocation; it does not amend any scientific protocol or eligibility
gate.

## Existing path assumptions

The six inspected files below were byte-identical to their current `HEAD`
versions during this audit: MSM and HANDOVER `src/dataset_adapter.py`, REBOOT
`src/source_audit.py`, and shared `external_eval/{run_all,data,leakage}.py`.
The implementation directories already owned these sources. Their remaining old
root source/configuration/stage names are therefore pre-existing source text,
not edits introduced by this relocation.

| Consumer | Exact interface | Existing issue and current relocation effect |
|---|---|---|
| `implementations/MSM/src/validate_inputs.py` | Lines 8–10, 15–18, 38–46 | Old `MSM/99_preserved_previous_work/MILLING_DATASET` import root and old numbered result-stage paths already differ from the implementation layout. Some output calls also pass plain strings directly to pandas. Moving the remaining raw root adds a separate input-location change. |
| `implementations/MSM/src/dataset_adapter.py` | `load_source`, line 10 | `pd.read_csv(row.mtc_file, ...)` sends a saved manifest string directly to pandas. A scoped `Path` substitution does not translate that argument. The original manifest and its hash must remain unchanged. |
| `implementations/HANDOVER/src/dataset_adapter.py` | `load_source`, line 10 | `np.load(row.sensor_file, ...)` likewise bypasses `Path`. Native sensor locations move with the approved raw tree; resolving this requires an explicit I/O-boundary adapter rather than rewriting saved scientific manifests. |
| `implementations/HANDOVER/src/validate_full.py` | Lines 12–17, 180; saved rows in lines 44–48 | Import roots and shared configuration paths retain the earlier layout. `ROOT/01_raw_dataset` now needs the approved raw-root mapping. The script can read raw arrays/video and write validation outputs; importing or running it is not part of a path-only check. |
| `implementations/REBOOT/src/source_audit.py` | Lines 12–15 | Marker-based repository discovery is portable, but it then appends `REBOOT` and reads `00_dataset_overview/ACTIVE_RUN.json` at import time. That overview already lives under implementation results. Raw and run roots have their additional approved moves. Importing this module is therefore not a side-effect-free way to test path discovery. |
| `implementations/REBOOT/src/build_gallery.py` | Line 23 | Decoder lookup uses `REPO/'MILLING DATASET/.tools'`. Its physical destination changes in this move. A scoped `Path` mapping can cover this lookup, but does not validate decoding or gallery generation. |
| `implementations/cross_dataset/src/external_eval/data.py` | `Store.__init__`, lines 40–53 | Dynamic adapters are loaded from `Path(dataset)/'src/dataset_adapter.py'`; this needs the specific source mapping, not the results mapping. Most subsequent feature-cache paths are wrapped in `Path` and are candidates for scoped translation. Raw-loading methods delegate to the string interfaces above. |
| `implementations/cross_dataset/src/external_eval/leakage.py` | Line 25 | `pd.read_csv('MSM/01_raw_dataset/download_manifest.csv')` is a literal-string I/O call unaffected by the scoped `Path` loader. The audit also hashes native payloads; it was not run. |
| `implementations/cross_dataset/src/external_eval/run_all.py` | Lines 17–20, 39–44, 64, 102–111 | Literal `PYTHONPATH` and child-script arguments retain old source paths. A parent's import context does not propagate into new Python processes. The controller can launch acquisition, preprocessing, fitting and reports; no controller execution was performed. |
| `implementations/cross_dataset/src/external_eval/protocol.py` | Lines 8, 14, 93 | The old milling configuration, import path and shared configuration root were already relocated earlier. This source is a protocol writer, not an inert configuration reader, and was not run. |

## Mapping requirements and safe coverage

A single broad `MSM -> implementations/MSM` mapping is insufficient: the raw tree
is directly under `implementations/MSM/`, source is under its `src/`, and numbered
research outputs are under its `results/`. HANDOVER and REBOOT have the same need
for exact sub-prefixes. Similarly, `CROSS_DATASET_COMPARISON/src` maps to
`implementations/cross_dataset/src`, whereas remaining comparison evidence maps
under `implementations/cross_dataset/results`. Use the recorded physical path
mapping, including earlier consolidation mappings, rather than guessing from
directory names.

The shared explicit loader can support the inspected `Path(...)`, fixed-depth
root, `relative_to`, `os.path.relpath` and scoped dynamic-import interfaces with
those exact mappings. This is an INFERRED extension of the synthetic-tested
interfaces, not a completed MSM/HANDOVER/REBOOT replay check. The ViFailback
activation helper intentionally enumerates its own source/dependency scopes and
does not automatically activate these other domains.

Full replay additionally needs explicit translation at plain-string pandas,
NumPy, OpenCV and subprocess/import-search boundaries. These must be designed
and tested without changing saved manifest bytes, prediction identities,
calibration/fitting roles or original hash gates. Process launch adapters need
their own explicit activation in each child interpreter. No blanket third-party
I/O monkeypatch or automatic legacy-controller runner is supplied.

The consolidated code and evidence remain inspectable. This relocation does not
claim that every historical command can be pasted unchanged, that original
training has been reproduced, or that currently inadmissible studies may run.
Mandatory study-specific OOF/participant gates and stopped-study boundaries
remain unchanged.
