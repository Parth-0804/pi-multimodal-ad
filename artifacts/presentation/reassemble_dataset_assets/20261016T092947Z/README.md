# REASSEMBLE dataset presentation assets

Frozen cohort: **4,530 completed actions**, **4,021 successes**, **509 failures**, **148 recordings**. The raw inventory contains **149 recordings**. The pack contains **39 PNG figures**, eight exact **512 × 22** sensor arrays, label cards, tables and provenance.

Use `contact_sheets/*_5frame.png` for slides, `*_16frame.png` to explain actual frame selection, `sensors/*_heatmap.png` and `*_grouped_lines.png` for sensor examples, and `statistics_insert_failure.png` for the 22 × 10 = 220 engineered statistics. `recording_contents.json` describes a recording; `sample_label_cards.json` exposes the actual selected annotation fields; `sample_alignment_timeline.json` supplies the insert/failure diagram data.

No model training or inference was run. No labels or cohort files were changed. No raw files were modified. No Task 4 execution occurred. No models or dependencies were downloaded or installed. No commits, pushes or Git index/branch changes were made. The pre-existing deletion of `src/shared/README.md` was left untouched. All new writes are under this timestamped asset directory. Full recordings, audio payloads and private human-review mappings are not exported.

Examples were selected without prediction outcomes, scores, correctness, or human-review outcomes. Within each action/failure stratum, duration is end minus start; select the first row sorted by absolute distance from that stratum's median duration, then recording_id and segment_id as strings. CSV readers should explicitly preserve recording_id and segment_id as strings. The exact identities and median distances are in `selected_examples.csv` and `selection_details.json`.

The eight selected IDs are: pick_success, pick_failure, insert_success, insert_failure, remove_success, remove_failure, place_success, place_failure.

Frame positions are uniformly spaced ranks in the inclusive in-interval index set, using NumPy rounding; they are not a claim of an exact frame at the annotation boundary. The 5 display positions are 0%, 25%, 50%, 75%, 100%. The 16 indices use the unmodified expression from the current Section 1 extractor. Every selected frame is inside its action interval and matches the retained extractor indices. Actual encoded videos are H.264, **640 × 480 at 30 fps**. Their frame counts equal timestamp counts. Container duration is frame_count/fps, which can differ from timestamp-span duration; config image_size=640 is not a raw-resolution declaration.

Sensor groups, in concatenation order: measured_force **3**, measured_torque **3**, gripper_positions **2**, joint_efforts **7**, joint_velocities **7** = **22 scalar channels**. The schema uses component indices, not invented axis names. `scalar_channel_count` is the group's width repeated on each component row; count the 22 rows or sum one width per group. Units were absent from the inspected sensor dataset attributes and are recorded as `NOT_AVAILABLE`.

Resampling calls the existing `interval_indices` and `resample_progress` functions with 512 positions and gap_multiple=5, then concatenates groups and casts to float32 exactly as Section 1. No population statistics, standardization, or imputation are applied to saved arrays. All eight arrays exactly match retained Section 1 sensor arrays, including NaNs. Finite fractions range from 97.7805% to 99.2720%; no channels are entirely missing. Boundary/gap NaNs are retained. Heatmap colors use per-channel within-example z-scores only (clipped to ±3), labelled “per-channel visualization scaling only — not model preprocessing”; line plots use source values.

Statistics execute the unmodified pure function definition from `src/reassemble/section1_features.py::statistics`, without importing or calling its model-loading/extraction entry points. Output is statistic-major: mean, population standard deviation, median, minimum, maximum, q25, q75, range, RMS, and slope per normalized progress. Exactly 220 values match retained Section 1 statistics. The compact statistics plot divides each channel's ten values by its maximum absolute value for display; the CSV retains the original values.

Audio figures are **illustrative full-recording excerpts, not action-aligned evidence**. The recording is the lexicographically first selected recording (`2025-01-09-14-47-32`); each excerpt is its own stream's central ten seconds. Action labels and action intervals do not select these excerpts. Hama1/Hama2 are stereo MP3 at 16 kHz; hand_audio is mono MP3 at 48 kHz. All three are encoded byte values stored in int64 HDF5 arrays, not raw int64 PCM samples. No audio files are exported.

Sample counts are decoded sample frames per channel, not byte counts or total interleaved scalar samples. For the illustrated recording, decoded counts were recounted blockwise to EOF. For the other seven selected recordings, counts and durations retain the existing full-decode inventory after confirming raw size/mtime; current headers and beginning/central probes were decoded. These evidence types and header-versus-decoded counts are explicit in `audio_decode_evidence.json` and `audio_metadata.csv`. `decoded_successfully` records successful current probes; it does not claim a fresh full decode of all 24 streams. Header counts may overestimate duration. Waveforms show min/max envelopes; spectrograms show actual PSD with an excerpt-specific 80 dB display range, detailed in `figure_presentation_notes.json`.

Annotations supply absolute Unix-style start/end timestamps. Video and sensors use their HDF5 timestamp arrays. The nominal audio origin is the inventory's minimum first non-audio timestamp, following the established inventory convention. It is not an independently measured mapping from decoded audio time to the annotation clock. No verified offset, drift calibration, or segment anchor is available. Nominal overlap therefore does not establish label-safe action extraction. Audio was excluded by this prerequisite, not by a finding that it has no predictive signal. No audio samples are assigned to the displayed action.

Retained gate coverage matches the requested rounded values: hama1_audio **97.31% nominal / 96.46% failures**, hama2_audio **96.20% / 95.48%**, hand_audio **100.00% / 100.00%**; each has **148 nominally valid recordings and zero verified action intervals**. Exact source values, paths and SHA256 hashes are preserved in `audio_alignment_status.json`.

Visual inspection of all 16 contact sheets found no identifiable faces, badges, screens or private text; no redactions were needed (`redactions.json`).

`validation.json` is the final asset validation. `validation_pending.json` is the retained intermediate report, superseded by it and excluded from the ZIP. `repository_checks.json` records successful git diff --check, Git status/diff inspection and pip check. Existing repository implementation and historical outputs were not edited. This is an asset task, not a restructuring phase.

Raw size/mtime checks cover all **149 inventoried raw HDF5 files** plus eight selected encoded videos, before/after generation and after final presentation adjustments. Cohort, config, code and audit input hashes are checked unchanged. These are preservation metadata checks, not a fresh whole-dataset payload hash scan. Retained raw SHA256 identities come from the authoritative inventory.

The scripts `build_assets.py`, `polish_figures.py`, and `finalize_package.py` record the generation and verification process. Run with the existing repository Python and `-B`. These files are tied to this run; build/finalization use exclusive creation and intentionally refuse to overwrite completed outputs. To reproduce, place the scripts in a **new authorized timestamp directory** under the same root and execute in that order, including visual review. No clean second extraction run is claimed. Reproduction dependencies and software versions are in `provenance.json`.

Package: `REASSEMBLE_DATASET_PPT_ASSETS_20261016T092947Z.zip`. It contains the timestamp-named asset directory, excluding the ZIP itself, its post-package integrity record, the intermediate validation report and the Matplotlib font cache. `manifest.csv` inventories the pre-package files (including excluded intermediates); its own hash is covered by `checksums.sha256`. Checksums cover all packaged files except checksums.sha256 itself. The ZIP SHA256 and post-write CRC/content verification are in `package_integrity.json` beside the ZIP. These exclusions avoid circular/self hashes. All paths below are relative to `artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/`:

- `README.md`
- `REASSEMBLE_DATASET_PPT_ASSETS_20261016T092947Z.zip`
- `action_outcome_counts.csv`
- `audio/hama1_audio_spectrogram.png`
- `audio/hama1_audio_waveform.png`
- `audio/hama2_audio_spectrogram.png`
- `audio/hama2_audio_waveform.png`
- `audio/hand_audio_spectrogram.png`
- `audio/hand_audio_waveform.png`
- `audio_alignment_status.json`
- `audio_decode_evidence.json`
- `audio_metadata.csv`
- `build_assets.py`
- `checksums.sha256`
- `config_snapshot.json`
- `contact_sheets/insert_failure_16frame.png`
- `contact_sheets/insert_failure_5frame.png`
- `contact_sheets/insert_success_16frame.png`
- `contact_sheets/insert_success_5frame.png`
- `contact_sheets/pick_failure_16frame.png`
- `contact_sheets/pick_failure_5frame.png`
- `contact_sheets/pick_success_16frame.png`
- `contact_sheets/pick_success_5frame.png`
- `contact_sheets/place_failure_16frame.png`
- `contact_sheets/place_failure_5frame.png`
- `contact_sheets/place_success_16frame.png`
- `contact_sheets/place_success_5frame.png`
- `contact_sheets/remove_failure_16frame.png`
- `contact_sheets/remove_failure_5frame.png`
- `contact_sheets/remove_success_16frame.png`
- `contact_sheets/remove_success_5frame.png`
- `dataset_summary.json`
- `figure_presentation_notes.json`
- `finalize_package.py`
- `frame_selection.csv`
- `function_execution.json`
- `input_manifest.json`
- `manifest.csv`
- `package_integrity.json`
- `plot_cache/fontlist-v3.11.0.json`
- `polish_figures.py`
- `provenance.json`
- `recording_contents.json`
- `redactions.json`
- `repository_checks.json`
- `retained_feature_comparison_sources.json`
- `sample_alignment_timeline.json`
- `sample_label_cards.json`
- `selected_examples.csv`
- `selection_details.json`
- `sensor_channel_schema.csv`
- `sensor_shapes.csv`
- `sensors/insert_failure_512x22.npy`
- `sensors/insert_failure_grouped_lines.png`
- `sensors/insert_failure_heatmap.png`
- `sensors/insert_success_512x22.npy`
- `sensors/insert_success_grouped_lines.png`
- `sensors/insert_success_heatmap.png`
- `sensors/pick_failure_512x22.npy`
- `sensors/pick_failure_grouped_lines.png`
- `sensors/pick_failure_heatmap.png`
- `sensors/pick_success_512x22.npy`
- `sensors/pick_success_grouped_lines.png`
- `sensors/pick_success_heatmap.png`
- `sensors/place_failure_512x22.npy`
- `sensors/place_failure_grouped_lines.png`
- `sensors/place_failure_heatmap.png`
- `sensors/place_success_512x22.npy`
- `sensors/place_success_grouped_lines.png`
- `sensors/place_success_heatmap.png`
- `sensors/remove_failure_512x22.npy`
- `sensors/remove_failure_grouped_lines.png`
- `sensors/remove_failure_heatmap.png`
- `sensors/remove_success_512x22.npy`
- `sensors/remove_success_grouped_lines.png`
- `sensors/remove_success_heatmap.png`
- `source_preservation_after.json`
- `source_preservation_before.json`
- `statistics_insert_failure.csv`
- `statistics_insert_failure.png`
- `validation.json`
- `validation_pending.json`
- `video_metadata.csv`
