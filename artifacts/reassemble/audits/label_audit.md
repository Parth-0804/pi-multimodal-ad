# Label audit

{
  "all_annotations": {
    "segments": 4863,
    "failures": 517,
    "successes": 4346,
    "recordings": 149,
    "failure_recordings": 131,
    "success_recordings": 149
  },
  "primary_actions": {
    "segments": 4551,
    "failures": 516,
    "successes": 4035,
    "recordings": 149,
    "failure_recordings": 131,
    "success_recordings": 148
  },
  "dual_complete": {
    "segments": 4530,
    "failures": 509,
    "successes": 4021,
    "recordings": 148,
    "failure_recordings": 130,
    "success_recordings": 147
  },
  "tri_complete": {
    "segments": 0,
    "failures": 0,
    "successes": 0,
    "recordings": 0,
    "failure_recordings": 0,
    "success_recordings": 0
  }
}

| action | segments | failures | failure_rate |
| --- | --- | --- | --- |
| insert | 1165 | 247 | 0.21201716738197424 |
| pick | 1195 | 100 | 0.08368200836820083 |
| place | 1091 | 22 | 0.02016498625114574 |
| remove | 1100 | 147 | 0.13363636363636364 |

Published reference: 4,551 action demonstrations; 4,035 successful and 516 failed.
Observed counts above are recomputed from success fields; idle/other annotations
remain in the inventory but are excluded from the primary action task.

Action-only prediction remains a required later baseline; no model was trained.
Object strings are descriptive annotation suffixes, not validated universal IDs
and never predictors. The full per-recording/object/duration/availability tables
are stored as labels_by_*.parquet in the versioned run.

## duration_bin

| duration_bin | segments | failures | failure_rate |
| --- | --- | --- | --- |
| [0.0, 5.0) | 648 | 32 | 0.04938271604938271 |
| [10.0, 20.0) | 1361 | 226 | 0.16605437178545188 |
| [20.0, 60.0) | 347 | 88 | 0.25360230547550433 |
| [5.0, 10.0) | 2195 | 170 | 0.0774487471526196 |

## visual_usable

| visual_usable | segments | failures | failure_rate |
| --- | --- | --- | --- |
| False | 9 | 2 | 0.2222222222222222 |
| True | 4542 | 514 | 0.11316600616468515 |

## sensor_usable

| sensor_usable | segments | failures | failure_rate |
| --- | --- | --- | --- |
| False | 13 | 6 | 0.46153846153846156 |
| True | 4538 | 510 | 0.1123843102688409 |

## audio_nominal_usable

| audio_nominal_usable | segments | failures | failure_rate |
| --- | --- | --- | --- |
| True | 4551 | 516 | 0.1133816743572841 |
