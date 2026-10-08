# Annotation-boundary adjudication request

The automated audit found positive overlaps among stored high-level annotations. The following pairs affect the frozen primary cohort:

| recording_id | segment_a | segment_b | action_a | action_b | failure_a | failure_b | a_primary | b_primary | overlap_seconds | same_start_end | same_fold | same_selected_frames | same_statistics |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-01-10-15-49-06 | 42 | 44 | insert | insert | 0 | 0 | True | True | 22.299856662750244 | True | True | True | True |
| 2025-01-10-17-54-09 | 34 | 37 | pick | pick | 0 | 0 | True | True | 9.165385246276855 | False | True | False | False |
| 2025-01-10-17-54-09 | 35 | 38 | insert | insert | 0 | 0 | True | True | 18.48333191871643 | True | True | True | True |

The two exact repeated input windows and the contained partial window have matching action/outcome labels and remain in the same recording/fold. This is not evidence of cross-fold leakage. The original cross-recording duplicate gate did not claim to exclude within-recording repeated annotations. Preserve the original4530-row evaluation and all uncertainty as defined.

Please adjudicate whether these are duplicate annotations, intended alternative spans or annotation errors before any correction. Do not remove rows, alter labels or recalculate performance without a separately approved correction protocol. The frozen balanced64-case human review sample is unchanged; these targeted source identities are kept outside its blinded export. No nonoverlap/unique-physical-action claim is supported until adjudication.
