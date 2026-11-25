# REASSEMBLE storage preflight

Recorded 20260927T123356Z (UTC). **Storage preflight only; NO-GO.**
No dataset download, extraction, deletion, training, raw-data change or data-root
creation occurred. Only small audit artifacts were written.

## Official archive verification

The [official TU Wien record](https://researchdata.tuwien.ac.at/records/0ewrv-8cb44),
DOI 10.48436/0ewrv-8cb44, independently confirms:

| File | Published compressed size | Published MD5 |
|---|---|---|
| data.zip | 54.8 GiB | 812103a652ca9201e87a3bcecfee4ef3 |
| poses.zip | 87.3 KiB | 2f3f86b65dc6312b504072a2460314c2 |
| splits.zip | 1.1 KiB | 641882928ef3a8b2c3db41ac7c60b994 |

Extracted size: **UNKNOWN UNTIL ARCHIVE IS INSPECTED/EXTRACTED**.
Published rounded sizes are not exact byte counts. No archive payload was fetched.
The DOI redirect was unavailable to the web tool; the official record itself was
successfully located and read. Metadata is stored with this audit.

## Relevant locations and filesystem capacity

| Location inspected | Device; format; mount | Available GiB | Read/write access |
|---|---|---:|---|
| /home/student/Master_Thesis_WS/pi-multimodal-ad | /dev/sda1; ext4; / | 48.13 | True/True |
| /home/student | /dev/sda1; ext4; / | 48.13 | True/True |
| /home | /dev/sda1; ext4; / | 48.13 | True/False |
| /data | absent | — | — |
| /mnt | /dev/sda1; ext4; / | 48.13 | True/False |
| /scratch | absent | — | — |

These locations share one filesystem: do not add their free-space figures.
Available bytes at the candidate-path check: 51,684,032,512.
`df -h`/`df -BG` round this to 49G, while the exact available capacity is
48.13 GiB. `/dev/root` in df resolves to the root filesystem shown by
findmnt/lsblk as `/dev/sda1`. No separate large data disk is mounted at /mnt.
Boot partitions and RAM-backed tmpfs mounts are unsuitable dataset workspaces.
Inodes are not the bottleneck (root filesystem approximately 66.6 million free).
Permissions were checked with os.access; no write-speed or write-permission test
files were created. Filesystem access does not override agent sandbox restrictions.

### Recorded filesystem commands

```text
$ pwd
/home/student/Master_Thesis_WS/pi-multimodal-ad

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
/dev/root      66977792 378438 66599354    1% /
tmpfs           8221918      1  8221917    1% /dev/shm
tmpfs            819200    809   818391    1% /run
tmpfs           8221918      2  8221916    1% /run/lock
efivarfs              0      0        0     - /sys/firmware/efi/efivars
/dev/sda16        58496    605    57891    2% /boot
/dev/sda15            0      0        0     - /boot/efi
tmpfs           1644383     36  1644347    1% /run/user/1001

$ lsblk -f
NAME    FSTYPE  FSVER            LABEL           UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
sda                                                                                                  
├─sda1  ext4    1.0              cloudimg-rootfs 0d4bbbd1-29c7-4f5b-a154-667ab7106f8a   48.1G    90% /
├─sda14                                                                                              
├─sda15 vfat    FAT32            UEFI            55BC-B2C7                              98.2M     6% /boot/efi
└─sda16 ext4    1.0              BOOT            5897163b-af0c-4a92-b0be-22b2d3ac7a10    677M    16% /boot
sr0     iso9660 Joliet Extension cidata          2026-09-27-00-12-53-00
```

## Current project size

```text
$ du -sh /home/student/Master_Thesis_WS/pi-multimodal-ad
406G	/home/student/Master_Thesis_WS/pi-multimodal-ad

$ du -h --max-depth=1 /home/student/Master_Thesis_WS/pi-multimodal-ad | sort -h
8.0K	/home/student/Master_Thesis_WS/pi-multimodal-ad/.github
44K	/home/student/Master_Thesis_WS/pi-multimodal-ad/.pytest_cache
56K	/home/student/Master_Thesis_WS/pi-multimodal-ad/archive
120K	/home/student/Master_Thesis_WS/pi-multimodal-ad/configs
592K	/home/student/Master_Thesis_WS/pi-multimodal-ad/docs
840K	/home/student/Master_Thesis_WS/pi-multimodal-ad/tests
1.4M	/home/student/Master_Thesis_WS/pi-multimodal-ad/scripts
2.0M	/home/student/Master_Thesis_WS/pi-multimodal-ad/src
2.3M	/home/student/Master_Thesis_WS/pi-multimodal-ad/artifacts
6.6M	/home/student/Master_Thesis_WS/pi-multimodal-ad/presentation_assets
49M	/home/student/Master_Thesis_WS/pi-multimodal-ad/scratch
112M	/home/student/Master_Thesis_WS/pi-multimodal-ad/tutorials
353M	/home/student/Master_Thesis_WS/pi-multimodal-ad/experiments
3.9G	/home/student/Master_Thesis_WS/pi-multimodal-ad/runs
6.8G	/home/student/Master_Thesis_WS/pi-multimodal-ad/ma_thesis_env
15G	/home/student/Master_Thesis_WS/pi-multimodal-ad/.git
26G	/home/student/Master_Thesis_WS/pi-multimodal-ad/data
356G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment
406G	/home/student/Master_Thesis_WS/pi-multimodal-ad
```

These are allocated disk-use measurements, rounded in binary human-readable
units. Largest immediate consumers are protected PHM raw data (~356 GiB), data
(~26 GiB), Git objects (~15 GiB), environment (~6.8 GiB), and runs (~3.9 GiB).
These measurements are informational, not deletion recommendations.

### Twenty largest entries under the thesis workspace

Bounded metadata-only scan of the requested workspace, not a system-wide crawl.
Directory totals overlap their children; they must not be summed.

```text
$ du -ah /home/student/Master_Thesis_WS | sort -h | tail -20
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-1.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-2.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-3.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-4.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-5.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-6.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-1.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-3.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-5.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-6.zip
20G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP F/Exp-F_HDF5_Run-8.zip
26G	/home/student/Master_Thesis_WS/pi-multimodal-ad/data
26G	/home/student/Master_Thesis_WS/pi-multimodal-ad/data/Full Dataset
96G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP A
123G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP B
137G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency/EXP F
355G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/high_frequency
356G	/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment
406G	/home/student/Master_Thesis_WS/pi-multimodal-ad
413G	/home/student/Master_Thesis_WS
```

## Existing dataset/archive search

No matches found for data.zip, poses.zip, splits.zip, names containing REASSEMBLE,
or HDF5 filenames matching the official recording dates/pattern in the searched
locations. Therefore no candidate archive size/mtime or MD5 calculation applies;
no archive is marked VALID EXISTING ARCHIVE.

Searched /home/student (including the project) and /mnt, 16,655
directories total, with zero traversal errors. /data and /scratch do not exist.
Search used filename/directory metadata only; symlink directories were not followed.
Credential/browser/agent state, Git internals, virtual environments, node_modules,
and directory names containing credential/session/cookie were pruned. The exact
exclusions are in search_and_locations.json. Unrelated system paths and pruned
private locations are outside this negative search result; no global absence
claim is made. File contents, secrets and authentication sessions were not read.

## Proposed DATA_ROOT and workspace budget

No currently inspected filesystem is suitable for the download.
The provisional existing-filesystem location is `DATA_ROOT=../datasets`, resolved
relative to the repository (outside Git, under the writable thesis workspace).
Proposed layout:

```text
<DATA_ROOT>/REASSEMBLE/downloads
<DATA_ROOT>/REASSEMBLE/raw
<DATA_ROOT>/REASSEMBLE/cache
```

This location still shares the nearly full root disk and is **not approved for
use now**. Do not create it as a workaround. Prefer a separately provisioned
persistent data volume with at least 160 GiB available, ideally 200+ GiB; then
set DATA_ROOT to that mounted location and rerun preflight. Root ext4 is a local
block-device filesystem; throughput was not benchmarked and backing-media speed
is not established by lsblk. No alternative faster/larger volume was found.

| Budget component | Capacity / status |
|---|---|
| A. Official main download | 54.8 GiB compressed |
| B. Extracted dataset | UNKNOWN UNTIL ARCHIVE IS INSPECTED/EXTRACTED |
| C. Minimum operational recommendation | 160 GiB free |
| D. Preferred longer-term headroom | 200+ GiB free; workspace headroom, not dataset size |

Headroom covers archive + extracted HDF5 + video/audio caches + embeddings +
checkpoints + logs/artifacts. At 48.13 GiB available the current root is
approximately 6.67 GiB short even for the published archive alone,
111.87 GiB short of the recommended operational threshold, and
151.87 GiB short of 200-GiB workspace headroom. These are capacity gaps,
not instructions to remove existing files or a guarantee of eventual fit.

| Free capacity | Classification |
|---|---|
| >=160 GiB | GO |
| >=120 and <160 GiB | CONDITIONAL; do not download yet |
| <120 GiB | NO-GO; do not download |

## GPU, RAM and CPU context

NVIDIA Tesla T4; 16,384 MiB VRAM (16 GiB), idle at inspection. Driver 580.167.08;
nvidia-smi advertises CUDA compatibility 13.0 (not proof of a separately installed
CUDA toolkit). Repository PyTorch 2.13.0+cu130 reports CUDA build 13.0,
cuda.is_available()=True and one visible device. No training or benchmark ran.
RAM approximately 62 GiB total / 59 GiB available; no swap; nproc reports 16 CPUs.
These capabilities do not change the disk decision.

```text
$ nvidia-smi
Sun Sep 27 14:33:58 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.167.08             Driver Version: 580.167.08     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla T4                       On  |   00000000:06:10.0 Off |                  Off |
| N/A   33C    P0             28W /   70W |       0MiB /  16384MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+

$ free -h
total        used        free      shared  buff/cache   available
Mem:            62Gi       3.5Gi       933Mi       4.9Mi        59Gi        59Gi
Swap:             0B          0B          0B

$ nproc
16
```

## Policy, provenance and validation

AGENTS.md was read before inspection. Its raw-data, credential and historical-output
boundaries were respected; the active-scope/data/output policies read earlier in
this session remain applicable. Referenced docs/restructuring/TASKS.md is absent.
No nested AGENTS.md was found on the new report's ancestor path.

Versioned evidence: `storage_runs/20260927T123356Z/` contains command results and exit
codes, search bounds/path measurements, official metadata, provenance and output
hashes. The fixed report path was created exclusively, with overwrite refusal.
Only REASSEMBLE audit files were added. Existing Intel/PHM files remain untouched.
`git diff --check` passed; `git diff --stat` is empty because additions are
untracked. Environment pip check: No broken requirements found..
No tests were added for this read-only storage report.

Exact next action: provision or expand persistent storage to at least 160 GiB
available (preferably 200+ GiB), then rerun storage preflight before separately
authorizing a download. No cleanup or provisioning was attempted. Stop here.

STORAGE NO-GO — DO NOT DOWNLOAD
