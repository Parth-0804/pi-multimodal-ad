# 00 — Data overview: Core fusion

**One sample is one completed action segment**, identified by `(recording_id, segment_id)` and its `[start, end]` timestamps. Several samples belong to one recording. The task predicts the recorded action outcome retrospectively: `failure = 1` means failure; `0` means success. It is not forecasting before the action starts.

The raw inventory has 149 recordings. The frozen primary cohort contains **4,530 segments from 148 recordings: 509 failures and 4,021 successes**, across pick, insert, remove and place. Eligibility requires `primary_task` and `dual_complete`; therefore even single-modality baselines use this same paired cohort.

- [Frozen sample table](../../../../runs/reassemble/20260927T154732Z-section1/cohort.parquet) — row order used by the saved prediction arrays.
- [Inventory table with eligibility fields](../../../../runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort.parquet) — why a row is included.
- [Dataset counts and modalities](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/dataset_summary.json) and [What a recording contains](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/recording_contents.json).
- [Original sample label cards](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/sample_label_cards.json) — includes annotation text and timestamps.

**Sample to follow:** recording `2025-01-13-16-45-31`, segment `21`, action `insert`, recorded failure `1`. Its interval is `1736783322.9826488` to `1736783338.2159712` (15.2333 seconds), and its zero-based cohort row is **3326**. It was selected for the presentation pack by median duration within action/outcome, before consulting predictions; it is an illustration, not performance evidence.

Audio exists in the dataset but is excluded from these core predictive models because action alignment is unverified. See [Recorded audio alignment status](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/audio_alignment_status.json).

Next: [01 — Preprocessing](../01_data_preprocessing/README.md).
