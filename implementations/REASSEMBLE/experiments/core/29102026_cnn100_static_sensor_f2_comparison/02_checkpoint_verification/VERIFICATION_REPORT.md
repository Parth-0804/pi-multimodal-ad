# Existing experiment verification — PASS

Verified actual checkpoint bytes/identities, strict CPU state loading with no missing/unexpected tensors, finite tensors, 100 history rows, selected epochs, original training-only normalizers, saved prediction IDs/labels and independently recomputed AP. Original C calibrators were refitted from their saved training-side logits and reproduced exactly.

| Arm | Epochs | Selected | Assessment AP | Actions | Recordings |
|---|---:|---:|---:|---:|---:|
| frozen | 100 | 14 | 0.193775578 | 753 | 26 |
| finetuned | 100 | 47 | 0.212584503 | 753 | 26 |

All 753 assessment actions (77 failures/676 nonfailures) are recording-disjoint from gradient training, checkpoint selection, branch calibration and the proposed F2 fitting bank. The pre-existing selected-job field `prediction_recordings` refers to its original inner holdout; actual new outer prediction IDs/recordings were checked against the cohort instead of trusting that stale field.

A valid untouched training-side bank exists:920 actions from28 recordings, with97 failures. Reusing it needs only new inference, not new CNN fitting. It is one original inner-fold holdout, not complete four-fold nested OOF coverage. Both fusion arms will use the same bank, sensor probabilities, fitting function and fixed threshold. The departure from historical all-inner-fold coverage is explicit in LOCKED_PROTOCOL_02.json. No in-sample base predictions or calibration-fit rows enter F2 fitting.

The saved static sensor branch uses220 statistics, balanced C1 logistic on G and independent unweighted sigmoid calibration on C. The original inner3 model supplies genuine out-of-fit F2-training inputs (G2171/C686); the original outer-assessment model supplies the unchanged M3-M7 baseline test probabilities (G2966/C811). This preserves the original inner-fit/outer-refit stacking roles instead of weakening the sensor baseline to the smaller inner fit. Both saved prediction banks reproduce to1e-12. Original checkpoints and the running75-fit study remain unchanged. New computations will use CPU only.
