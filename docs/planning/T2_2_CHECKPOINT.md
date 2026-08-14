# T2.2 checkpoint — manifests and splits

Status: **COMPLETE FOR PROVISIONAL IMAGE BASELINE; SENSOR FEATURES DEFERRED**  
Run: `20260814T013357354377Z-6b068cab`

- 7,124 one-minute HDF5 source records and 20 run windows are traceable by archive/member, CRC evidence, experiment/run and sequence position.
- Observed run durations are file count × 60 seconds: 73–528 minutes. No equal division or ZIP-order grouping was used.
- 995 post-run image-view samples: EXP-B train 448, EXP-A validation 323, EXP-F untouched test 224.
- Zero experiment/run or near-duplicate cross-split violation; no random image/tooth split and no physical train/validation/test copies.
- Each view keeps its own provisional image ratio. Multiple views aggregate to a tooth, then 28 teeth aggregate to a run; the run target is never repeated as every tooth label.
- `minute_feature_table` is a status table: compact signal features were not computed in this image-only task. A later bounded streaming sensor job is required before PatchTST or sensor-to-damage modelling.

Primary artifacts: `runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/{tables,reports}`.
