# Full numerical sensor audit

All5,202 actual Parquet payloads,1,297,146 rows, were acquired/reused and verified
against the pinned public LFS SHA-256 inventory. Every state/velocity/effort array
is N-by14,finite,correctly keyed to episode/task/frame/global index; every repeated
episode-label flag and annotated avoid/correct index matches the native record.
Those target-containing fields were used only for audit and are forbidden inputs.
Published extrema match the actual arrays; published float32 mean/std are not
reused as model population normalization or sufficient proof of quality.

| Input | Retained indices | Excluded structural placeholders | Interpretation |
| --- | --- | --- | --- |
| observation.state | 0–13 | none | 14 native observed joint/gripper positions |
| observation.velocity | 0–5 and7–12 | 6 and13 globally zero | 12 native joint-velocity fields |
| observation.effort | 6 and13 | 12 arm-joint fields globally zero | two native gripper-effort fields; not force/torque |


These are observed source fields, not the separate `action` command arrays.
Previous original-HDF5 checks covered two pilot and two constant-position source
records. Three additional input-selected checks here cover2791,3034,5080. Their
nine qpos/qvel/effort comparisons have zero conversion error; total ranged bytes
160,512,without image extraction. This verifies stored source-observation
provenance in checked originals, not every sensor's physical calibration.
Receipts and source LFS identities are in
`ADDITIONAL_ORIGINAL_SENSOR_CHECKS.json` and `../source_evidence/`.

The 173 completely constant position episodes comprise162 native failures and11
no-failure records. The prior source/video checks demonstrate real robot motion
despite frozen positions in two such recordings. This makes blanket finite-value
or timestamp checks insufficient. Individual stationary joints and globally
placeholder effort channels are different and are not mislabeled as faults.

Three gross position episodes:2960,3034,3086. Six gross velocity episodes:
2761,2832,2928,2960,2982,5080. Raw extrema include33070.77734375,-292.6617431640625
and repeated28.92799949645996. The position absolute99.9th percentile across
episode-channel extrema is approximately2.68 native units, so the large mixed
scales are not ordinary bulk variation. The recorded values are preserved;
none were clipped, imputed or sign-flipped. Source record3034 contains the same
extreme position and5080 contains the same velocity spike before conversion.

For5023 nonconstant-position episodes, the median within-episode diagnostic
correlation between position finite differences and matching velocity fields
has corpus median about0.9655. However,528 episode medians are negative;
498 belong to canonical task55's500 episodes. Individual signed correlations in
2791 are about-0.99 for channels0,1,3,5 and positive for2,4, suggesting an
unresolved axis-convention difference rather than a universal delay. The original
HDF5 arrays reproduce these inputs exactly. The cause and intended coordinate
convention are **not established**. No automatic sign correction is scientifically
justified. V2 quarantines the entire task pending clarification. Other isolated
low/negative correlations remain diagnostics because noise/static axes/sampling
can affect this check; they are not asserted hardware defects.

See [SENSOR_ANOMALY_DIAGNOSTICS.png](SENSOR_ANOMALY_DIAGNOSTICS.png),
`GROSS_NUMERICAL_OUTLIERS.csv`, `TASK_POSITION_VELOCITY_CONSISTENCY.csv`, and
`ALL_EPISODE_CHANNEL_QC.csv`(218,484 episode/channel rows). The V2 policy is
`../config/COHORT_QC_POLICY_V2.json`, separately reviewable from the initial policy.

The maximum converted timestamp/index-over25 difference is
1.83105468921e-06 seconds. This verifies the
conversion's shared25-Hz frame-clock construction and valid joins. It does not
independently measure original camera-to-device hardware synchronization,
per-channel acquisition latency, sampling jitter or calibrated physical units.
Pilot video PTS evidence remains sample-limited, as documented in the original
modality report. No offset was fitted using outcomes or failure annotations.

**Usability:** native position, velocity and gripper-effort statistics are plausible
inputs in the restricted V2 study, with target-train-only scaling and explicit
quality limits. A velocity ablation and position-plus-gripper-effort sensitivity
analysis should accompany any later result. Do not call these wrist force,
torque, six-axis wrench, or calibrated contact force. Quality-aware fusion must
not hide defective sensors or assume that low variation means normal operation.
