# P4.1–P4.5 initial sensor-only PatchTST checkpoint

Status: **COMPLETE — INITIAL BASELINE; EXP-F NOT IMPROVED OVER CONSTANTS**  
Evidence date: `2026-08-14`  
Target status: `provisional_pending_human_review`

## Scope and scientific decision

The implemented formulation is current-state sequence-to-one regression:

```text
sensor history recorded within experiment/run
→ compact chronological minute features
→ one scalar estimate of the current post-run damage state
```

It is not six-hour-ahead forecasting. Six hours remains the typical run and
inspection cadence. The supervised sample is one experiment/run; the 7,124
HDF5 members are repeated within-run observations, not independent labels.

Primary target: `raw_top3_mean_pct`. Secondary reporting target:
`causal_monotonic_top3_mean_pct`. Both come from target version
`phm2026_image_damage_v2` and are provisional image-derived values in
percentage points of visible-flank candidate area, not organizer ground truth
or validated physical spall area.

## Pinned inputs

- D1.1 inventory run `20260813T202043619114Z-ad7f9832`;
  `archive_members.parquet` SHA-256
  `01bfc91ed669f93502f9bb2225e58bc4069184fae16242964758809881c3ae3d`.
- Target run `20260814T012054997053Z-e195f6d9`;
  `run_damage_targets.parquet` SHA-256
  `b0e0116dc3df840d550aec25082b427cb056c0573f66f3c6ad0ccd843cc41277`.
- T2.2 split run `20260814T013357354377Z-6b068cab`;
  `split_manifest.parquet` SHA-256
  `6463b00cafa8785708b1a32b13901077f7b9eef1e177c54f7fc6e0a6137d4359`.
- Matching image-only RT-DETR run
  `20260814T020338751021Z-d0f225c8` is comparison evidence only.

## Feature dataset

Canonical feature run:
`runs/phm2026_sensor_features/20260814T121146792755Z-4016432b/`.

- 7,124 LF HDF5 records processed one at a time from 20 nested run ZIPs.
- 7,119 records have verified UTC `wf_start_time` and enter sequences.
- Five EXP-F records have no verified timestamp. They remain in the minute
  table with exclusion reasons and do not enter sequences.
- Zero duplicate verified timestamps were observed within runs.
- Chronology is timestamp-sorted; ZIP order and filenames are not used as
  model time.
- Sequence counts: EXP-B train 7, EXP-A validation 5, EXP-F test 8.
- Sequence lengths range from 73 to 526 included minute records.
- Raw archive size and modification-time invariance passed.

Configured channels and evidenced source units:

| Channel | HDF5 path | Unit evidence |
|---|---|---|
| RPM | `/Context/PAU Speed` | source attribute `RPM` |
| Torque | `/Context/PAU Torque` | source attribute `ft-lbf` |
| Temperature | `/Context/Temperature` | source attribute `degF` |
| Axial RMS | `/Context/Accel1 RMS` | source attribute `g` |
| Radial RMS | `/Context/Accel2 RMS` | source attribute `g` |
| FM4, NA4, M6A, ALR | `/CI/{name}` | unit not observed; not inferred |

Each channel contributes mean, population standard deviation, median, minimum,
maximum, last finite value, and slope per within-file sample index. The slope
is not assigned a physical-time unit because the within-file cadence was not
verified. An explicit channel missingness mask yields 72 model inputs. No raw
102.4-kHz waveform, FFT feature, extracted HDF5 collection, or raw-array cache
was created.

## Preprocessing and tensor flow

- Training-only median imputation and standardization are fit on EXP-B minute
  rows and persisted in `reports/feature_normalizer.json`.
- Variable sequences are right-padded only within batches; a boolean time mask
  prevents invalid positions from influencing patches or pooling.
- Input: `B × T × 72`.
- Patching: length 16 minutes, stride 8, producing `B × 72 × N × 16`.
- Per-channel linear projection to `d_model=32`.
- Two channel-independent Transformer encoder layers, four heads,
  feed-forward width 64, dropout 0.1.
- Mask-aware patch pooling produces `B × 72 × 32`; a 64-unit MLP emits `B`.
- Total/trainable parameters: 169,825.
- Robust scaled smooth-L1 loss; AdamW, learning rate 0.001, weight decay
  0.0001; validation early stopping with patience 10.

## Training and validation

Canonical model run:
`runs/phm2026_patchtst_baseline/20260814T121641338050Z-433d4154/`.

- Device: NVIDIA Tesla T4; PyTorch `2.13.0+cu130`. PyTorch warned that the selected CUDA memory-efficient attention backward kernel is nondeterministic under `warn_only=True`; the fixed seed is recorded, but bitwise replay is not claimed.
- Real-data tiny-batch loss: 0.931469 → 0.001752.
- Early stopped after 14 epochs; best EXP-A validation epoch: 4.
- EXP-F did not fit normalization, Ridge alpha, early stopping, or any model
  setting. It was evaluated once after the validation-selected state loaded.
- Only best and last checkpoints were saved.

## Untouched EXP-F result (raw target, N=8)

| Model | MAE | RMSE | Spearman | R² |
|---|---:|---:|---:|---:|
| Training mean | 0.680 | 0.777 | undefined (constant) | -0.015 |
| Training median | 0.680 | 0.771 | undefined (constant) | -0.001 |
| Ridge run summary | 5.015 | 11.311 | 0.095 | -214.272 |
| PatchTST | 1.011 | 1.243 | -0.262 | -1.601 |

The primary question has a negative answer for this canonical run: PatchTST
did not extract enough transferable run-level information to beat either
constant baseline on EXP-F. Ridge was severely unstable because hundreds of
summary dimensions were fit from seven training runs. The result was retained
without test-driven retuning. Run-resampling confidence intervals are provided
but remain unstable at N=8.

## Professor package and figures

Canonical report run:
`runs/phm2026_patchtst_results/20260814T122147349749Z-44877f9f/`.

Primary report:
`reports/professor_patchtst_baseline.md`. Figure index:
`reports/FIGURE_INDEX.md`. It contains 13 PNG/SVG figure pairs and exact source
CSVs, including the dataset funnel, records/run, duration distribution,
missingness heatmap, deterministic normalized sequence, target distribution,
architecture, losses, scatter, residuals, EXP-F trajectory, four-sensor-model
comparison, and matching run-level image-versus-sensor comparison.

## Reproduction commands

```bash
PYTHONPATH=src ma_thesis_env/bin/python -B scripts/build_sensor_features.py --dry-run
PYTHONPATH=src ma_thesis_env/bin/python -B scripts/build_sensor_features.py
PYTHONPATH=src ma_thesis_env/bin/python -B scripts/train_patchtst.py --dry-run
PYTHONPATH=src ma_thesis_env/bin/python -B scripts/train_patchtst.py
PYTHONPATH=src ma_thesis_env/bin/python -B scripts/generate_patchtst_results.py
```

These commands are non-overwriting and therefore create new run IDs. Exact
canonical input hashes are stored in the three `phm2026_*patchtst*.yaml`
configurations and each run manifest.

## Resource and safety evidence

- Canonical feature/model/report runs use 29,418,577 + 3,421,310 + 3,548,522
  bytes (36,388,409 bytes total).
- Final free space: 75,270,725,632 bytes, above the 50-GiB gate.
- Source LF archives passed size/mtime invariance. No PHM archive, Intel data,
  historical output, or `.gitignore` content was modified.

## Limitations and next gate

The effective sample size is 20 runs. The target remains provisional; target
measurement error and A/B-versus-F domain shift can dominate these results.
This initial LF representation omits raw vibration spectral information and
does not prove sensors lack damage information.

Before a complex PatchTST model, finish expert review of the image-derived
target, review channel/path/unit coverage, and pre-register a very small set of
EXP-B/EXP-A-only representation or architecture changes. Do not tune against
EXP-F and do not begin fusion until both unimodal baselines are scientifically
stable.
