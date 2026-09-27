# Initial audit methods and interpretation limits

The pre-download `RESEARCH_CONTRACT.md` fixes the task, support thresholds and
selection rules. This note specifies implementation details before real-recording
inventory. All resulting counts come from the data; documented dimensions are
only comparison points.

## Timestamp coverage and sensors

Timestamps must be finite and strictly increasing. Multiple timestamp columns
collapse only when they agree to 1e-9 absolute tolerance; otherwise the stream is
flagged. Interval endpoints are inclusive. Coverage is the sum of adjacent
in-segment timestamp gaps no larger than five native median intervals, divided
by segment duration. Large gaps and time outside observed endpoints contribute
zero. This conservative statistic does not bridge a missing tail or leading gap.

Linear interpolation maps each channel independently to 512 progress positions,
using only in-segment finite samples. Unobserved endpoints and large gaps remain
NaN with explicit masks. A primary stream requires at least 90% timestamp and
resampled finite coverage and no entirely missing channel. Combined sensor
availability requires all five predeclared streams. Constant channels are
reported, not automatically excluded: an action can physically remain still.
Actual per-stream channel counts are retained.

Quality includes missing/constant channel counts, finite fraction, interpolation
fraction and a descriptive outlier fraction beyond ten scaled within-segment
MADs. Zero-MAD channels do not supply a defensible outlier denominator and are
reported as constant where appropriate. These are label-independent descriptive
statistics, not trained normalization. Hardware clipping bounds are unavailable,
so sensor clipping is null rather than invented. Future corruption scale and
model normalization must still be estimated using training folds only.

## Media

Video blobs are copied only to a SHA256-keyed encoded-media cache outside Git.
Containers must open and their frame counts must match timestamp counts. Sixteen
evenly spaced in-segment timestamp indices are checked deterministically. Every
selected frame must decode; a 90% interval-coverage threshold also applies.
Brightness, focus and motion proxies use 160x120 grayscale previews. Motion is
mean absolute change between these sparse previews, not optical flow. These
checks establish sampled representation availability, not exhaustive clean video.

Audio is decoded with the existing libsndfile MP3 support. Sample rate, channels,
duration and decoding are measured. Explicit per-sample timestamps, when present
and matched to decoded sample count, permit verified interval selection. Otherwise
zero-based sample timing is only a nominal convention inherited from the upstream
visualizer; it does not independently verify cross-modal clock origin or drift.
Such audio is inventoried but cannot make the primary tri-modal cohort complete.
RMS, near-full-scale clipping and sample amplitudes below 1e-4 (silence proxy)
are measured; no unsupported SNR estimate is supplied. Operator narration remains
a semantic-shortcut concern even after timing is resolved.

## Defects, labels and groups

Read the official README issues into the evidence record. Missing-camera coverage
is measured segment by segment. For documented final-action F/T and gripper
failures, retain the affected annotation but exclude the named sensor stream at
that segment. Numeric values alone cannot conclusively verify a physical defect;
the report distinguishes measured evidence from reliance on the official warning.
Pose is not among initial primary channels. Missing idle segments are never
invented.

Action extraction accepts only an annotation starting with a recognized form of
pick/insert/remove/place. Unrecognized annotations remain visible. Object suffixes
are audit text, not validated identities or model inputs. Label support counts
independent recordings and checks both classes in each fixed-seed nested fold.
The official project describes one H5 file per trial; audit exact recording and
combined primary-sensor segment hashes for cross-recording duplicates. Collection
calendar dates do not by themselves prove a common trial. Same-day acquisition
conditions remain a limit of recording-disjoint generalization.

No baseline/model is fitted during this phase. Availability is not signal;
independent predictive information, permutation controls and fusion positive
controls belong to later approved gates.

## Actual-schema corrections established before the full inventory

The first extracted recording uses absolute Unix timestamps, three measured
Torque channels, and MP3 bytes represented as int64 values in the 0–255 range.
The local reader validates that range before conversion to bytes. The official
visualizer subtracts the minimum first timestamp across all streams; nominal
audio coverage now uses that same recording origin, with no absolute time fed
to predictors.

The pilot recording `2025-01-11-11-35-53` exposed libsndfile header-length
overestimation for hand_audio: 32,704,128 reported frames versus 13,895,424
actually decoded frames at 48 kHz (681.336 versus 289.488 seconds). The full
inventory streams each audio file to EOF to count actual decoded frames before
computing coverage; a synthetic regression test enforces this distinction.
The pilot JSON is retained in the acquisition run and excluded from final
aggregates. The corrected full inventory uses a separate run directory.

A documented origin convention still does not supply independently measured
microphone start offsets or drift. Stored per-sample audio timestamps are used
if available; otherwise nominal audio coverage is reported separately from
verified primary-cohort support.

Official final-action warnings refer to the final recognized manipulation, not
the trailing `No action.` annotation. All five listed final-action defect
recordings have a trailing idle segment; the exclusion selector is regression-tested.
