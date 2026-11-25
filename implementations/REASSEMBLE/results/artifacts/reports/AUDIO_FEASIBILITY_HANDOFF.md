# Audio feasibility handoff

**AUDIO NOT INCLUDED — SEGMENT-ALIGNMENT OR COVERAGE PRECONDITION FAILED**

The intended AST would aggregate independently within each high-level segment. Frame-perfect synchronization was not required. The missing prerequisite is a trustworthy mapping from annotation clock to the decoded waveform interval. No stream has an independently verified mapping; this is not evidence that audio lacks predictive signal.

| Stream | Nominal valid % | Failure valid % | Recordings | Verified segments | Frame-count mismatch recordings |
| --- | --- | --- | --- | --- | --- |
| hama1_audio | 97.31 | 96.46 | 148 | 0 | 63 |
| hama2_audio | 96.20 | 95.48 | 148 | 0 | 52 |
| hand_audio | 100.00 | 100.00 | 148 | 0 | 148 |

No AST, tri-modal fusion or audio-corruption model was trained because the segment-alignment gate failed. This is a completed gate-based exclusion, not unfinished modelling. Prior full decoding was reused after verifying immutable source metadata; actual audio dataset attributes and timestamp-key availability were rechecked. Details: runs/reassemble/20260927T204649Z-audio-gate.
