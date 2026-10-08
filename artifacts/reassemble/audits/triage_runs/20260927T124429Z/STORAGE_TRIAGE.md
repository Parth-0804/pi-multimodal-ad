# Storage triage — diagnostic only

Snapshot: 20260927T124429Z UTC. Repository: `/home/student/Master_Thesis_WS/pi-multimodal-ad`.
**Recommendation: new persistent storage is required.** No suitable alternative
volume is currently mounted. Relocating within this root filesystem recovers no
filesystem space. No files were moved, removed, compressed, staged or cleaned;
no Git maintenance, downloads, model training or PHM artifact modification occurred.

## 1. Filesystem summary and exact capacity gap

Repository filesystem: `/dev/sda1`, ext4, mount `/` (`df` calls it `/dev/root`).
Allocated repository footprint: **405.973 GiB**.
Available at the final byte-level check: **51,662,290,944 bytes = 48.114258 GiB**.
Free capacity fluctuates; values are a timestamped observation, not a reservation.

- Additional free bytes to reach 160 GiB: **120,136,400,896 bytes
  (111.885742 GiB)**.
- Additional free bytes to reach 200 GiB: **163,086,073,856 bytes
  (151.885742 GiB)**.

A separate disk must independently provide the required 160/200 GiB workspace;
do not add free space across filesystems unless a split-storage strategy is
explicitly designed. The prior official-metadata preflight records REASSEMBLE's
54.8-GiB compressed main archive. Its extracted size remains unknown. The archive
alone does not fit in the current available capacity.

```text
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       495G  447G   49G  91% /
tmpfs            32G     0   32G   0% /dev/shm
tmpfs            13G  992K   13G   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
efivarfs        256K  123K  129K  49% /sys/firmware/efi/efivars
/dev/sda16      881M  142M  677M  18% /boot
/dev/sda15      105M  6.2M   99M   6% /boot/efi
tmpfs           6.3G  8.0K  6.3G   1% /run/user/1001

$ df -BG
Filesystem     1G-blocks  Used Available Use% Mounted on
/dev/root           495G  447G       49G  91% /
tmpfs                32G    0G       32G   0% /dev/shm
tmpfs                13G    1G       13G   1% /run
tmpfs                 1G    0G        1G   0% /run/lock
efivarfs              1G    1G        1G  49% /sys/firmware/efi/efivars
/dev/sda16            1G    1G        1G  18% /boot
/dev/sda15            1G    1G        1G   6% /boot/efi
tmpfs                 7G    1G        7G   1% /run/user/1001

$ df -i
Filesystem       Inodes  IUsed    IFree IUse% Mounted on
/dev/root      66977792 378467 66599325    1% /
tmpfs           8221918      1  8221917    1% /dev/shm
tmpfs            819200    809   818391    1% /run
tmpfs           8221918      2  8221916    1% /run/lock
efivarfs              0      0        0     - /sys/firmware/efi/efivars
/dev/sda16        58496    605    57891    2% /boot
/dev/sda15            0      0        0     - /boot/efi
tmpfs           1644383     36  1644347    1% /run/user/1001
```

## 2. Explanation of the repository footprint

The PHM raw tree (355.283 GiB), data (25.089 GiB) and Git history
(14.522 GiB) explain **97.27%** of total repository allocation.
The next two contributors are the active environment (6.719
GiB) and run outputs (3.840 GiB). This is predominantly retained raw
data, not a large expendable cache. No extraction or cache deletion is proposed.

Measurement uses same-device metadata, allocated blocks and inode de-duplication.
File rankings below use logical bytes; directory totals use allocated bytes and
include directory metadata. Parent/child totals overlap and must not be summed.
The metadata scan covered 83,655 regular files with 0
errors. Tiny source trees were not separately recursively analysed after the
single repository-wide metadata pass needed for top-file ranking.

## 3. Top directories, purpose, Git visibility and classification

| Path | Allocated size | File Git status / allocated bytes | Inferred purpose | Classification |
| --- | --- | --- | --- | --- |
| gtc-data-experiment | 355.283 GiB | IGNORED: 355.283 GiB | PHM immutable raw archives | MOVE_CANDIDATE (policy exception required) |
| data | 25.089 GiB | TRACKED: 0.00 MiB; IGNORED: 25.057 GiB | Intel raw files, small derived/Paderborn files | MOVE_CANDIDATE / protected raw |
| .git | 14.522 GiB | GIT_INTERNAL: 14.521 GiB | Git object database/history | KEEP_LOCAL_REQUIRED |
| ma_thesis_env | 6.719 GiB | IGNORED: 6.690 GiB | Active Python/CUDA runtime | KEEP_LOCAL_REQUIRED |
| runs | 3.840 GiB | IGNORED: 1.552 GiB; TRACKED: 2.286 GiB | PHM caches, checkpoints, overlays, reports | KEEP_LOCAL_REQUIRED / selective MOVE_CANDIDATE |
| experiments | 352.29 MiB | TRACKED: 97.06 MiB; IGNORED: 255.14 MiB | Protected historical EDA outputs | KEEP_LOCAL_REQUIRED |
| tutorials | 111.77 MiB | TRACKED: 22.60 MiB; IGNORED: 89.06 MiB | Tutorial results and pretrained checkpoint | KEEP_LOCAL_REQUIRED |
| scratch | 48.88 MiB | IGNORED: 48.84 MiB | Blind-inspection images and local artifacts | UNKNOWN; preserve |
| presentation_assets | 6.53 MiB | TRACKED: 6.52 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| artifacts | 2.30 MiB | UNTRACKED: 0.23 MiB; IGNORED: 2.01 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| src | 1.93 MiB | TRACKED: 0.84 MiB; IGNORED: 0.98 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| scripts | 1.38 MiB | TRACKED: 0.72 MiB; IGNORED: 0.51 MiB; UNTRACKED: 0.07 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| tests | 0.82 MiB | TRACKED: 0.23 MiB; UNTRACKED: 0.00 MiB; IGNORED: 0.57 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| docs | 0.58 MiB | TRACKED: 0.49 MiB; UNTRACKED: 0.03 MiB; IGNORED: 0.05 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| configs | 0.12 MiB | TRACKED: 0.10 MiB; UNTRACKED: 0.00 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| archive | 0.05 MiB | TRACKED: 0.05 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| .pytest_cache | 0.04 MiB | IGNORED: 0.03 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |
| .github | 0.01 MiB | TRACKED: 0.00 MiB | Code/configuration/documentation/small artifacts | KEEP_LOCAL_REQUIRED |

Raw high-frequency breakdown:

| Path | Allocated size |
| --- | --- |
| gtc-data-experiment/high_frequency/EXP A | 95.279 GiB |
| gtc-data-experiment/high_frequency/EXP B | 122.895 GiB |
| gtc-data-experiment/high_frequency/EXP F | 136.334 GiB |
| gtc-data-experiment/low-frequency (CIs) | 80.78 MiB |
| gtc-data-experiment/low-frequency (CIs + Oil + Environment) | 109.17 MiB |
| gtc-data-experiment/photos | 603.22 MiB |
| data/Full Dataset | 25.031 GiB |

Largest run families (overlap the runs total):

| Run family | Allocated size |
| --- | --- |
| runs/phm2026_image_target | 1.168 GiB |
| runs/phm2026_rtdetr_detection | 708.89 MiB |
| runs/phm2026_rtdetr_pseudo_boxes | 676.79 MiB |
| runs/_superseded | 614.96 MiB |
| runs/phm2026_rtdetr_multitask | 340.98 MiB |
| runs/phm2026_dataset_description | 164.48 MiB |
| runs/phm2026_rtdetr_regression | 103.61 MiB |
| runs/phm2026_sensor_features | 56.29 MiB |
| runs/phm2026_rtdetr_results | 42.31 MiB |
| runs/phm2026_patchtst_baseline | 13.57 MiB |

## 4. Top 50 files

Paths relative to repository; sizes are logical bytes expressed in binary units.
Python/CUDA libraries are runtime files, not cache or checkpoint files.

| Rank | Path | Logical size | Type | Git status |
| --- | --- | --- | --- | --- |
| 1 | gtc-data-experiment/high_frequency/EXP A/Exp-A_HDF5_Run-5.zip | 19.533 GiB | PHM raw archive | IGNORED |
| 2 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-5.zip | 19.429 GiB | PHM raw archive | IGNORED |
| 3 | gtc-data-experiment/high_frequency/EXP A/Exp-A_HDF5_Run-2.zip | 19.380 GiB | PHM raw archive | IGNORED |
| 4 | gtc-data-experiment/high_frequency/EXP A/Exp-A_HDF5_Run-1.zip | 19.379 GiB | PHM raw archive | IGNORED |
| 5 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-2.zip | 19.276 GiB | PHM raw archive | IGNORED |
| 6 | gtc-data-experiment/high_frequency/EXP A/Exp-A_HDF5_Run-3.zip | 19.267 GiB | PHM raw archive | IGNORED |
| 7 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-5.zip | 19.252 GiB | PHM raw archive | IGNORED |
| 8 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-3.zip | 19.243 GiB | PHM raw archive | IGNORED |
| 9 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-6.zip | 19.239 GiB | PHM raw archive | IGNORED |
| 10 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-1.zip | 19.221 GiB | PHM raw archive | IGNORED |
| 11 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-4.zip | 19.220 GiB | PHM raw archive | IGNORED |
| 12 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-8.zip | 19.203 GiB | PHM raw archive | IGNORED |
| 13 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-3.zip | 19.187 GiB | PHM raw archive | IGNORED |
| 14 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-6.zip | 19.184 GiB | PHM raw archive | IGNORED |
| 15 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-1.zip | 19.181 GiB | PHM raw archive | IGNORED |
| 16 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-2.zip | 18.604 GiB | PHM raw archive | IGNORED |
| 17 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-4.zip | 17.874 GiB | PHM raw archive | IGNORED |
| 18 | gtc-data-experiment/high_frequency/EXP A/Exp-A_HDF5_Run-4.zip | 17.720 GiB | PHM raw archive | IGNORED |
| 19 | .git/objects/pack/pack-387b3e682db456570101dff70e3fd01da5acace0.pack | 12.827 GiB | Git object/history | GIT_INTERNAL |
| 20 | gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-7.zip | 7.443 GiB | PHM raw archive | IGNORED |
| 21 | gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-7.zip | 3.672 GiB | PHM raw archive | IGNORED |
| 22 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcublasLt.so.13 | 516.52 MiB | Python environment | IGNORED |
| 23 | ma_thesis_env/lib/python3.12/site-packages/torch/lib/libtorch_cuda.so | 448.08 MiB | Python environment | IGNORED |
| 24 | ma_thesis_env/lib/python3.12/site-packages/triton/_C/libtriton.so | 440.18 MiB | Python environment | IGNORED |
| 25 | ma_thesis_env/lib/python3.12/site-packages/torch/lib/libtorch_cpu.so | 418.11 MiB | Python environment | IGNORED |
| 26 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcufft.so.12 | 273.27 MiB | Python environment | IGNORED |
| 27 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cudnn/lib/libcudnn_engines_precompiled.so.9 | 234.02 MiB | Python environment | IGNORED |
| 28 | ma_thesis_env/lib/python3.12/site-packages/nvidia/nccl/lib/libnccl.so.2 | 225.57 MiB | Python environment | IGNORED |
| 29 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cusparselt/lib/libcusparseLt.so.0 | 223.08 MiB | Python environment | IGNORED |
| 30 | ma_thesis_env/lib/python3.12/site-packages/_polars_runtime_32/_polars_runtime.abi3.so | 205.46 MiB | Python environment | IGNORED |
| 31 | ma_thesis_env/lib/python3.12/site-packages/llvmlite/binding/libllvmlite.so | 170.59 MiB | Python environment | IGNORED |
| 32 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcusparse.so.12 | 155.03 MiB | Python environment | IGNORED |
| 33 | runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/tables/component_decisions.csv | 151.87 MiB | figure/table/image (role inferred) | IGNORED |
| 34 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcusolver.so.12 | 134.61 MiB | Python environment | IGNORED |
| 35 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcurand.so.10 | 126.55 MiB | Python environment | IGNORED |
| 36 | runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099/checkpoints/best_multitask.pt | 125.83 MiB | model checkpoint | IGNORED |
| 37 | runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099/checkpoints/last_multitask.pt | 125.83 MiB | model checkpoint | IGNORED |
| 38 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libnvrtc.alt.so.13 | 104.73 MiB | Python environment | IGNORED |
| 39 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libnvrtc.so.13 | 104.27 MiB | Python environment | IGNORED |
| 40 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cudnn/lib/libcudnn_adv.so.9 | 104.11 MiB | Python environment | IGNORED |
| 41 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcusolverMg.so.12 | 99.14 MiB | Python environment | IGNORED |
| 42 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libnvJitLink.so.13 | 93.31 MiB | Python environment | IGNORED |
| 43 | experiments/exp_a_initial_eda_r1_r3_r5/outputs/advanced_eda/tables/lf_canonical.csv | 71.94 MiB | figure/table/image (role inferred) | IGNORED |
| 44 | ma_thesis_env/lib/python3.12/site-packages/cv2/cv2.abi3.so | 70.45 MiB | Python environment | IGNORED |
| 45 | experiments/exp_a_initial_eda_r1_r3_r5/outputs/advanced_eda/tables/lf_flattened.csv | 66.21 MiB | figure/table/image (role inferred) | IGNORED |
| 46 | tutorials/rtdetr_storybook/rtdetr-l.pt | 63.43 MiB | model checkpoint | IGNORED |
| 47 | runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/checkpoints/rtdetr-l.pt | 63.43 MiB | model checkpoint | IGNORED |
| 48 | runs/phm2026_rtdetr_detection/20260814T042853425937Z-7f1e13af/logs/finetune/weights/best.pt | 63.14 MiB | model checkpoint | IGNORED |
| 49 | runs/phm2026_rtdetr_detection/20260814T042853425937Z-7f1e13af/logs/finetune/weights/last.pt | 63.14 MiB | model checkpoint | IGNORED |
| 50 | runs/phm2026_rtdetr_detection/20260814T042853425937Z-7f1e13af/checkpoints/last_detector.pt | 63.14 MiB | model checkpoint | IGNORED |

## 5. Git storage diagnosis — no maintenance performed

```text
$ du -sh .git
15G	.git

$ git count-objects -vH
count: 6512
size: 1.69 GiB
in-pack: 29
packs: 2
size-pack: 12.82 GiB
prune-packable: 0
garbage: 0
size-garbage: 0 bytes
```

Metadata-only `git cat-file --batch-all-objects --batch-check` inspected
6541 object headers/sizes. `git rev-list --objects --all` mapped
reachable historical paths. No blob contents were printed or extracted.

The largest blob is the historical partial download
`gtc-data-experiment/Exp-B_HDF5_Run-1.zip.part`, object
`284ccffbfe2b61f2abc91d97f5db0d0ee7abd628`: 14,047,735,808 logical bytes
(13.083 GiB), about 12.827 GiB compressed in the object store. It is reachable
from an inspected ref and explains almost the entire 12.82-GiB pack footprint.
The working raw tree is ignored now; ignore rules do not remove historical blobs.
This is retained partial-archive storage, not a validated full dataset backup.
Git history is not budgeted as recoverable space in any scenario. No claim that
ordinary garbage collection would remove this reachable blob is made.

| Object ID | Historical path | Logical size | Object disk size |
| --- | --- | --- | --- |
| 284ccffbfe2b61f2abc91d97f5db0d0ee7abd628 | gtc-data-experiment/Exp-B_HDF5_Run-1.zip.part | 13.083 GiB | 12.827 GiB |
| a8a9dd2662e992b7e49c0c2fd4a941360c9134d5 | tutorials/presentations/PHM2026_RTDETR_PatchTST_Baselines.pptx | 8.51 MiB | 7.85 MiB |
| 43240be18c563fe07b4b6912bb64a640ae93d646 | runs/phm2026_rtdetr_results/20260814T021109387090Z-d15163e7/figures/best_worst_target_overlays.png | 8.35 MiB | 8.32 MiB |
| f1ed7e01a0e3190e2c51f7dbfdb0aad2c30c3072 | runs/phm2026_rtdetr_results/20260814T021109387090Z-d15163e7/figures/target_overlay_examples.png | 8.19 MiB | 8.16 MiB |
| 80d11f046dd210ae5d506ebda6b8ab65d538c0ca | runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/tables/coco_annotations.json | 7.92 MiB | 0.92 MiB |
| 30427962d46c2c756b81d46a60c6bcda7713caf2 | tutorials/rtdetr_storybook/example_run/step4_final_drawing.png | 3.39 MiB | 3.39 MiB |
| 9c723df53cdc4ba7dde53ece8d92cb6b4686c7b8 | tutorials/patchtst_freq_baseline/features/build_log.jsonl | 2.78 MiB | 0.08 MiB |
| 3a918b68011428347a52f6c0f95f6805b5b6ef15 | runs/phm2026_rtdetr_results/20260814T021150456003Z-d15163e7/figures/target_overlay_examples.svg | 1.49 MiB | 1.14 MiB |
| 64b037048e045f8c71e685fe7b85dd11b83781d2 | runs/phm2026_rtdetr_results/20260814T021109387090Z-d15163e7/figures/target_overlay_examples.svg | 1.49 MiB | 1.14 MiB |
| 90e3f896ae6cd70dfa0aca0f65e0afaf585fb9bd | runs/phm2026_rtdetr_results/20260814T021109387090Z-d15163e7/figures/best_worst_target_overlays.svg | 1.48 MiB | 1.12 MiB |

Object disk sizes are diagnostic and not a guarantee of removable allocation
(pack/delta relationships and reachability matter).

## 6. PHM storage inventory

The raw tree contains 52 archive files totalling approximately 355.283 GiB,
plus a tiny dataset-adjacent file. It includes HF, LF/CI and photo archives.
No standalone .h5/.hdf5 payload files were found outside the environment/Git.
No archives were opened, so nested archive contents and extraction ratios remain
uninspected. There is no observed archive-plus-fully-extracted PHM duplicate tree.

The following mutually exclusive file-role estimates cover the raw tree,
PHM/superseded runs, historical EXP-A outputs, rawvib and inspection scratch:

| Role inferred from path/type | Files | Allocated file size |
| --- | --- | --- |
| Waveform-derived artifacts (entire rawvib tree) | 6 | 55.65 MiB |
| Raw PHM archive/data | 53 | 355.283 GiB |
| Reproducibility/config/report/log artifacts | 341 | 5.45 MiB |
| Generated overlay images (preserved run artifacts) | 3933 | 1.722 GiB |
| Figures/inspection images | 514 | 129.34 MiB |
| Tables/features/numerical outputs (mixed) | 533 | 890.62 MiB |
| Explicit cache paths (mostly image/array caches) | 2191 | 572.65 MiB |
| Model checkpoints (activity status unknown) | 27 | 955.23 MiB |
| Other PHM-associated artifacts; preserve | 7 | 14.48 MiB |

Run directories total 3.840 GiB; historical
`experiments/exp_a_initial_eda_r1_r3_r5` totals
0.344 GiB. These are overlapping
container totals, not additions to the role table. Processed feature tables are
mixed with result tables; the broad numerical-output bucket is **not** all
expendable feature cache. Explicit cache paths are predominantly images/arrays.
No separately named embedding-cache store was identified. No checkpoint is
certified inactive merely from age or filename. Preserve all reproducibility
manifests, configurations, reports, figures and historical results.

## 7. Tracked, untracked, ignored and external references

| Status | Regular files | Allocated file size |
| --- | --- | --- |
| TRACKED | 7197 | 2.411 GiB |
| IGNORED | 69857 | 388.976 GiB |
| UNTRACKED | 44 | 0.34 MiB |
| GIT_INTERNAL | 6557 | 14.521 GiB |

These totals exclude directory metadata. Git internals are not working-tree
tracked/untracked files. Tracked files remain tracked even when a later ignore
pattern matches their extension. Approximately 2.41 GiB of working-tree files
are tracked, including many generated images/results; moving them casually would
change the working tree without reducing their historical Git copies.

Verified ignore rules include /gtc-data-experiment/, /data/Full Dataset/,
/ma_thesis_env/, scratch/, data/rawvib/ and data/paderborn/. `runs/` is mixed,
not wholly ignored; checkpoint/CSV/array extensions are generally ignored while
many images/JSON/Markdown files are tracked. No staging occurred.

No data symlinks outside the environment/Git were found. Inspected canonical
PHM config uses `data_root: gtc-data-experiment`; output configs reference local
runs. No external large-data dependency was demonstrated by these checks; private
.env/session/configuration contents were not inspected, so this is not a claim
that every possible external override is absent.

```text
$ git status --short
?? artifacts/
?? configs/intel_welding/
?? docs/intel_welding/FOUNDATION_PROTOCOL_ADDENDUM.md
?? docs/intel_welding/FOUNDATION_RUNBOOK.md
?? docs/intel_welding/RESULTS_REVIEW.md
?? docs/intel_welding/context_baseline_specification.md
?? scripts/intel_welding/01_inventory.py
?? scripts/intel_welding/02_label_audit.py
?? scripts/intel_welding/03_make_split.py
?? scripts/intel_welding/04_foundations.py
?? scripts/intel_welding/05_foundation_report.py
?? tests/unit/test_intel_foundations.py
```

## 8. Alternative storage

| Candidate | Device / filesystem / mount | Total | Used | Available | Readable/writable |
| --- | --- | --- | --- | --- | --- |
| /data | absent | — | — | — | — |
| /mnt | /dev/sda1 ext4   / | 494.919 GiB | 446.787 GiB | 48.116 GiB | True/False |
| /scratch | absent | — | — | — | — |
| /home/student | /dev/sda1 ext4   / | 494.919 GiB | 446.787 GiB | 48.116 GiB | True/True |

/mnt is a directory on the root filesystem, not a mounted data disk, and is not
writable by this user. /home/student is writable but shares root capacity. /data
and /scratch are absent. Read/write checks used metadata/os.access, not test
writes. Root is the only mounted substantial persistent storage; boot filesystems
and tmpfs are not suitable dataset volumes. No unrelated system crawl occurred.

```text
$ lsblk -f
NAME    FSTYPE  FSVER            LABEL           UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
sda                                                                                                  
├─sda1  ext4    1.0              cloudimg-rootfs 0d4bbbd1-29c7-4f5b-a154-667ab7106f8a   48.1G    90% /
├─sda14                                                                                              
├─sda15 vfat    FAT32            UEFI            55BC-B2C7                              98.2M     6% /boot/efi
└─sda16 ext4    1.0              BOOT            5897163b-af0c-4a92-b0be-22b2d3ac7a10    677M    16% /boot
sr0     iso9660 Joliet Extension cidata          2026-09-27-00-12-53-00
```

## 9. Move candidates — proposals only

- **MOVE_CANDIDATE:** complete PHM immutable tree, 355.283 GiB; or selected
  experiment archives, preserving modality coverage and original source identity.
  EXP-B high-frequency alone is 122.895 GiB.
- **MOVE_CANDIDATE:** Intel raw tree, 25.031 GiB, with its manifest and licence.
- **MOVE_CANDIDATE:** large derived caches and inactive checkpoints, only after
  activity/dependency review. Preserve versioned lineage and referenced paths.
- **KEEP_LOCAL_REQUIRED:** source/configs/small audit evidence, Git metadata,
  current environment and any checkpoint required immediately.
- **UNKNOWN:** scratch/blind-inspection state, unidentified artifacts and
  regeneration status. No deletion recommendation applies.

Current AGENTS.md explicitly prohibits moving raw roots and preserves historical
outputs. These are hypothetical migration candidates, **not** permission to move
them. Any later migration requires a specific researcher-approved policy exception,
destination capacity, verified copy/checksums, configuration changes and read-only
pipeline validation before approval of source retirement. Copying alone, or
moving within the same filesystem, recovers zero bytes on root. None was executed.

## 10. Regenerable candidates — unverified reproduction

Explicit PHM-associated cache paths total about 0.559 GiB, and the rawvib
waveform-derived tree is 0.054 GiB. Their combined **candidate** space is
0.614 GiB. Reproducibility has not been rerun or validated; existing
output-protection policy remains in force. The numerical/table bucket
(0.870 GiB) includes thesis evidence and must not be treated wholesale as cache.
Overlays and superseded runs may be derivable but are protected historical output.
The active 6.72-GiB environment is not an expendable cache in this recommendation.
No cache was removed; no hypothetical regeneration was counted twice.

## 11. Duplicate patterns and targeted evidence

- Two rtdetr-l.pt files, each 66,511,432 bytes, have identical SHA256
  `6de60b10d4bc566f00cda0f5b4d64afe4b66d48dc9695d2171effb7859d8e73f`.
  One is under tutorials/rtdetr_storybook and one under the regression run's
  checkpoints. This is a confirmed repeated pretrained asset, only ~63.43 MiB
  of redundant logical storage, and both references must remain reproducible.
- best_multitask.pt and last_multitask.pt are each 131,937,950 bytes but have
  **different SHA256 values**. They are not exact duplicates. No removal assumed.
- Two phm2026_image_target overlay trees have 1,311 matching relative paths and
  sizes each (614,724,053 logical bytes / ~0.573 GiB each). **POSSIBLE_DUPLICATE**:
  pixel/file contents were not hashed. Full paths are in duplicate_evidence.json.
- Fifteen basename-plus-size groups >=1 MiB were flagged across non-environment,
  non-Git files; this is a candidate list, not a deduplication proof.
- Six groups of byte-identical resolved run configs were found, including active
  and superseded dataset-description runs. Matching configs do not establish
  matching data, code revision, random state, checkpoints or outputs.
- The large historical Git .zip.part shares a dataset identity with current raw
  storage but is partial and not a proven duplicate. Never count it as a valid
  backup or deletable space.
- No full extracted PHM tree or second obvious raw PHM copy was observed. Nested
  archives were not inspected. The reported EXP-A Run-2 overlap warning remains
  preserved; filenames do not establish content duplication.

Only four suspicious checkpoint files (~0.370 GiB total) and small resolved
configs were content-hashed. No hundreds-of-GiB content scan was performed.

## 12. Recovery scenarios — none executed

| Scenario | Requirement / potential root recovery | Consequence |
|---|---|---|
| A. New storage only — recommended simplest route | Expand root by >= 111.886 GiB usable to reach 160, or >= 151.886 GiB to reach 200; alternatively mount a new volume with >=160/200 GiB **available on that volume** | No PHM migration needed; store REASSEMBLE externally |
| B. Relocate selected immutable data | EXP-B HF ~122.895 GiB would give root ~171.009 GiB; all PHM ~355.283 GiB would give ~403.397 GiB | Requires a new destination large enough, policy exception and verified source retirement; no such volume currently exists |
| C. Relocate data + regenerate expendable caches later | All PHM plus only explicit cache/rawvib candidates: upper-bound ~355.897 GiB recovered; root ~404.011 GiB | Increment beyond B is only ~0.614 GiB, conditional on proven regeneration and explicit retention approval; no deletion proposed now |
| D. New large volume plus relocation | PHM + Intel + entire runs allocation + 200-GiB REASSEMBLE headroom requires >= 584.155 GiB **available destination capacity**, before further margins | Prefer >=600 GiB available for this broader design; selected relocation could eventually recover ~384.155 GiB on root; tracked/protected runs need separate review |

Scenario C is an upper bound, not a committed reclaim plan. All recovery assumes
actual cross-filesystem relocation/source retirement later authorized; safe copy
verification temporarily needs both copies. Space on the destination consumed by
relocated data is not simultaneously available to REASSEMBLE. Scenario A avoids
those migration risks and is the immediate recommendation. Small-cache or even
whole-Git recovery would not close the current threshold gap.

## 13. Proposed final layout — not implemented

```text
<large-data-volume>/datasets/PHM/
<large-data-volume>/datasets/Intel_Welding/     # only if later migrated
<large-data-volume>/datasets/REASSEMBLE/downloads/
<large-data-volume>/datasets/REASSEMBLE/raw/
<large-data-volume>/cache/PHM/
<large-data-volume>/cache/REASSEMBLE/
<large-data-volume>/runs/PHM/                  # only approved archival runs
```

Repository remains `/home/student/Master_Thesis_WS/pi-multimodal-ad`. Future config/environment conventions may be
`PHM_DATA_ROOT=<large-data-volume>/datasets/PHM` and
`REASSEMBLE_DATA_ROOT=<large-data-volume>/datasets/REASSEMBLE`.
These overrides are a proposed interface, not a claim that all historical code
already supports them. Do not write absolute machine paths into portable configs,
copy datasets into Git, modify protected historical code or silently break pinned
artifact references. No layout directories or environment files were created.

## 14. Deliverables, limits and next action

Only this report and small versioned evidence under `triage_runs/20260927T124429Z/` were
added. Full scratch metadata remained outside the repository. This phase read
AGENTS.md and respected existing data/output policy; no credentials or session
contents were opened. Referenced restructuring/TASKS.md remains absent.

Validation: filesystem-local metadata inventory, Git object metadata, ignore-status
classification, four candidate hashes, config hashes, disk/inode/mount checks.
`git diff --check` passed; `git diff --stat` is empty (new audit files are untracked).
Repository environment check: No broken requirements found..
No model tests were needed or run. No archive integrity or reproducibility claim
is inferred from metadata. Estimates are snapshots and not permission to act.

Exact next action: provision persistent storage with >=160 GiB available,
preferably >=200 GiB, for REASSEMBLE, then rerun storage preflight. Consider the
>=600-GiB available-volume design only if a separately approved PHM/Intel migration
is desired. Stop diagnostic work here; no relocation or download is authorized.

NEW STORAGE REQUIRED
