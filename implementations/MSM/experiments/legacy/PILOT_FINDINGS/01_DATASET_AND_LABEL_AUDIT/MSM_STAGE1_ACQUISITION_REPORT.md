# MSM Stage 1 acquisition report

**Status: annotation acquisition and native-label audit complete; review required before Stage 2.** No neural network was trained, no full video/audio/sensor payload was downloaded, and no complete-dataset archive was requested.

Dataset: **`manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`**. Official dataset ID **8392825**. Audit date: 2026-10-27T00:14:19.453082+01:00.

## Official identity and version provenance

The [dataset DOI](https://doi.org/10.34740/kaggle/ds/8392825) resolves to the [official Kaggle page](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly). The official public metadata endpoint returns `id=8392825`, `ref=manufuturetoday/multi-sensor-for-metal-milling-anomaly`, and `currentVersionNumber=2`. DataCite independently links the DOI to Kaggle dataset ID 8392825. Version **2**, created **2026-03-13T20:01:40.34Z**, was Ready and current at access. Its release note says the summary workbook corrected the machine name `imi_vm30i` to `imi_vmx30ui`, with no changes to raw sensor data. Every file-list and label request supplied `datasetVersionNumber=2`; an unversioned latest download was not used. Dataset license reported by Kaggle: CC BY 4.0.

The authoritative [data descriptor](https://www.nature.com/articles/s41597-026-07255-7) was retrieved from the publisher and inspected for native-label rules, interval interpretation, sensor synchronization, and laboratory video acquisition. Public access worked without reading credentials, local auth configuration, cookies, or session files. A failed unencoded nested-path request (404) was resolved using Kaggle's supported single-file query (`fileName` plus `datasetVersionNumber`); no access restriction was bypassed. Signed download redirect URLs were neither recorded nor exposed.

Evidence is under `evidence/`: public Kaggle metadata, DataCite metadata, source-access records, and an exact-byte copy of the supplied downloader. Publisher and landing-page HTML snapshots are local ignored evidence. The official inventory contains 481 unique entries and its 40,412,136,430-byte sum matches the official dataset total.

## Repository, persistent data, and preservation

The repository was already dirty at revision `94f61529116ebdc966bcf87704a93e4d02fa5e89`. Existing modified README/REPO_MAP/thesis evidence files and pre-existing untracked experiment/maintenance work were preserved. The initial status snapshot is `evidence/git_status_before.txt`. Repository/filename searches found no existing MSM dataset, annotation audit, or downloader; prior literature notes contained conceptual MSM discussion only. Protected PHM, Intel, REASSEMBLE, and historical experiment contents were not changed or scanned for payloads.

Per researcher instruction, all new work is contained in **`MILLING DATASET/`**. Persistent raw annotations are in **`MILLING DATASET/data/raw/msm/versions/2`**. Versioned outputs are in **`MILLING DATASET/runs/20261026T230520276818Z-stage1`**. The folder-local `.gitignore` excludes the entire `data/` subtree, including future media, NC/XML, receipts, and spreadsheets; raw inputs must never be committed. Small derived audit CSV files are narrowly allow-listed, while local source HTML and logs remain ignored. Nothing was staged or committed.

Preflight `df -h` reported 77G free (the downloader measured 76.6 GiB, approximately 82.2 decimal GB); free space at report generation was 76.645 GiB. Public DOI, publisher, DataCite, Kaggle metadata, file-list, and single-label endpoints were reachable. The default shell sandbox could not initialize its network namespace; approved execution outside that broken sandbox allowed the checks. KaggleHub and Kaggle CLI were absent. No dependencies were installed and no authentication blocker occurred.

## Selective acquisition and focused downloader changes

The supplied downloader's 69 paths exactly match the official version-2 hierarchy: 37 VM20i, 19 VMX30Ui, 13 VF10 experiments, with no numbering gaps. The preview verified **173,594 selected bytes**, then the selective run acquired **69 label files, 0 failures**. Their sizes match the pinned official inventory. Input SHA-256 values and the acquisition receipt provide local content identities; Kaggle's listing does not expose an official checksum, so do not describe size checks as independent cryptographic verification. Existing verified labels are skipped; mismatching existing paths are preserved for audit.

`source/download_msm.py` retains the supplied selection logic and adds an optional standard-library `public-api` backend restricted to small `label.csv` files. It requires a pinned handle and matching dataset-ID inventory, validates path membership, limits response bytes, validates CSV headers before exclusive file creation, and stops on HTTP 401/403. It also records hashes and preserves existing mismatches/zero-length paths. The original KaggleHub backend remains available for future reviewed use; it was not executed. No formula, native label, or experimental selection was silently corrected. Compare `evidence/download_msm.supplied.py` against the current source for the exact focused diff.

Commands, run from repository root:

```bash
ma_thesis_env/bin/python -B 'MILLING DATASET/source/inspect_official.py' --run 'MILLING DATASET/runs/20261026T230520276818Z-stage1'

# Preview first; --backend and --inventory are the documented local additions.
ma_thesis_env/bin/python -B 'MILLING DATASET/source/download_msm.py' \
  --handle manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2 \
  --dest 'MILLING DATASET/data/raw/msm/versions/2' --mode labels --backend public-api \
  --inventory 'MILLING DATASET/runs/20261026T230520276818Z-stage1/manifests/official_file_inventory.json'

# Selective annotation download, after the successful preview.
# Repeat the preceding command with --run.

ma_thesis_env/bin/python -B 'MILLING DATASET/source/audit_annotations.py' --run 'MILLING DATASET/runs/20261026T230520276818Z-stage1'
ma_thesis_env/bin/python -B 'MILLING DATASET/source/build_reports.py' --run 'MILLING DATASET/runs/20261026T230520276818Z-stage1'
```

Use a fresh versioned output directory for a new audit; table/report writers refuse existing targets. The command ledger and final verification record are in `manifests/commands.json` and `validation.json`. The receipt is preserved in raw storage and copied to `evidence/download_receipt.json` for review. Software versions, config, Git identity, dirty status, and source hashes are in `provenance.json`; input/output identities are under `manifests/`.

## Acquisition result and initial feasibility

| Machine | Experiments | Intervals | Label 0 | Label 1 | Label 2 | Label-1 groups |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i | 37 | 1585 | 1173 | 325 | 87 | 19 |
| imi_vmx30ui | 19 | 927 | 704 | 133 | 90 | 6 |
| tmf_vf10 | 13 | 63 | 56 | 7 | 0 | 5 |
| TOTAL | 69 | 2575 | 1933 | 465 | 177 | 30 |

There are **2,575 candidate interval examples**, including **465 label-1 intervals in 30 nominal experiment groups**. The two laboratory machines support all native classes; industry supports labels 0/1 only and has limited positives. Label meanings and starred-tool behavior agree with the publication. Labels alone support a provisional experiment-disjoint design, but do not establish independence of physical tools/sessions. All 56 laboratory experiments have listed video and sound; 13 industrial groups have sound and CT/MTC but no video. No paired multimodal example is validated yet.

Missing expected annotation files: **none**. Other 412 files: intentionally unacquired. Publication/label consistency, every-experiment counts, intervals, duration distributions, and grouping limitations are documented in `MSM_LABEL_AUDIT.md`. Exact hierarchy, missing modalities, per-file sizes, and next-pilot filenames are in `MSM_FILE_AVAILABILITY.md`.

## Proposed next action — wait for researcher review

Review the five laboratory groups **VM20i datasets 1, 4, 19; VMX30Ui datasets 9, 8**, plus optional **VF10 dataset1** for an industrial diagnostic. Obtain only the exact file plan in `manifests/pilot_file_plan.csv`, after approval. The primary laboratory plan plus metadata needs **106,130,475 bytes**; the industrial option adds **96,755,867 bytes**, for **202,886,342 bytes** total (202.886 MB). Optional ACC increases that total to **1,131,836,134 bytes**. No proposed pilot files were downloaded here.

Stage 2 should first inspect schemas and video/audio/sensor clocks, validate interval coverage and visual usefulness, reconcile physical tool/workpiece/session identities, and predeclare labels/grouping before any model fitting. This Stage 1 task grants no neural-network training authorization.

## Deliverables

- `MSM_STAGE1_ACQUISITION_REPORT.md` — this report.
- `MSM_LABEL_AUDIT.md` — native-label, duration, integrity, feasibility, and per-experiment audit.
- `MSM_INTERVAL_MANIFEST.csv` — all 2,575 rows with native labels, source row/hash, machine, experiment, time boundaries, duration, and unmodified context.
- `MSM_FILE_AVAILABILITY.md` — verified hierarchy, per-experiment modalities, and exact proposed pilot file/storage plan.

All four reside in `MILLING DATASET/runs/20261026T230520276818Z-stage1`. Preserve downloaded files and wait for researcher review before Stage 2.
