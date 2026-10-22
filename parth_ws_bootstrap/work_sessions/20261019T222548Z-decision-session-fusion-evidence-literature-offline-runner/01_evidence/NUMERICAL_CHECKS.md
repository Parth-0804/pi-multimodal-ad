# Optional historical prediction checks — completed within narrow scope

VERIFIED_WITHIN_SCOPE arithmetic; CONDITIONAL_ARRAY_ARITHMETIC scientific status. Two comparison sets selected in NUMERICAL_SELECTION_BEFORE_SCORES.md before any score payload was read in this session. This context had earlier outcome exposure. No post-score model/severity selection, new predictions, target changes, thresholds, calibration, fits or uncertainty resampling. Historical Task4 untouched.

NPZ_HEADER_PREFLIGHT.json records ZIP member uncompressed sizes and NPY headers before decoding, restricted nonobject dtypes and <=128MiB decoded/file. Four files total 2720232 compressed bytes; largest decoded bank 2068624 bytes. allow_pickle=False. Only y/fold and the preselected probability vectors decoded. Existing NumPy/sklearn/pyarrow used under two-thread environment caps, no package installation/project imports/model loading/GPU. check_retained_ap.py recomputes sklearn average_precision_score(pos_label=1) on pooled saved rows; the original source calls that same function while naming its report field AUPRC (not trapezoidal PR area). Definition: section1_report.py:14–23; section3_report.py:14–36; additional_improvements/reporting.py:9–20. Native positive-class construction: inventory.py:47–60.

All 15 recomputations equal stored AUPRC estimates (absolute difference 0.0 under the observed runtime; tolerance1e-12). This is floating-point agreement, not a mathematical exactness or bitwise cross-platform guarantee. No inference/training reproduced.

| Condition | Model | Recomputed AP | Difference from stored estimate |
| --- | --- | ---: | ---: |
| clean | U1 | 0.42939187 | 0 |
| clean | U2 | 0.23065832 | 0 |
| clean | F2 | 0.44729855 | 0 |
| clean | F6 | 0.44135589 | 0 |
| V1_0.1 | U1 | 0.42939187 | 0 |
| V1_0.1 | U2 | 0.11646095 | 0 |
| V1_0.1 | F2 | 0.39627466 | 0 |
| V1_0.1 | F6 | 0.12748323 | 0 |
| S1_1.0 | U1 | 0.16371022 | 0 |
| S1_1.0 | U2 | 0.23065832 | 0 |
| S1_1.0 | F2 | 0.22216018 | 0 |
| S1_1.0 | F6 | 0.17876917 | 0 |
| clean | A0 | 0.44729855 | 0 |
| clean | A-CONSTANT | 0.44567995 | 0 |
| clean | A-ADAPTIVE | 0.46831248 | 0 |

The three Section3 bank SHA256 values agree with their corresponding condition sidecars. The anchored execution.json prediction path/SHA/byte count agree with its bank. Current core source/config identities match selected retained implementation identities in the pinned audit, rechecked at preflight. This is a partial binding chain, not evidence that every fit used those bytes. The complete producing-run config/model/row chain is not certified here.

A separate bounded check used the existing small cohort.parquet (selected columns only, Parquet metadata checked first, no threaded decoding) and nested_splits.json. Source-defined primary_task & dual_complete selection measures 4530 rows / 509 positive labels/148 recordings, unique recording+segment keys. Each outer test recording set is disjoint from training and other outer tests; each saved inner train/validation partitions its outer training set and excludes outer test. Selected banks' y and fold vectors equal this CURRENT saved cohort order. The cohort key-order hash, inputs and versions are in MEMBERSHIP_CONSISTENCY.json.

Crucial limit: the banks contain no recording_id,segment_id,row_index or rows member. Label/fold equality does not prove row identity, since many rows share those values. Current source describes writing in that order, but execution and producing-time immutable row manifest are not established. Therefore these calculations remain conditional arrays rather than promoted cohort performance. Existing table labels do not validate raw annotations or independence beyond recording; no raw payload opened.

The selected arrays contradict a simple working assumption that visual noise must be harmless: F6 goes from 0.44135589 clean to 0.12748323 at the selected image-noise condition; selected sensor-noise AP is 0.17876917. These specific synthetic severities are not physically comparable scales, uncertainty was not re-evaluated, and F2/F6 have different links. This does not rank causal modality importance or certify a general robustness failure. It shows the proposed experiment has existing numerical evidence that merits careful reuse. Clean anchored AP values likewise establish retained control coverage, not corrupted-input advantage or fresh confirmation.

Unchecked: all other condition/model banks and severities, temporal/fine-tuning numerical banks, hard decisions/thresholds, calibration and CI reproduction, training/inference, raw targets and source video/sensor timing, higher-level groups, full per-fit producing-source/model lineage. A bank's missing keys are a blocker to stronger identity claims, not permission to fabricate IDs.

Exact commands (from repository root, outputs are exclusive and refuse overwrite):

    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 ma_thesis_env/bin/python -I -B SESSION_ROOT/01_evidence/check_retained_ap.py
    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 ma_thesis_env/bin/python -I -B SESSION_ROOT/01_evidence/check_saved_membership.py

Replace SESSION_ROOT with this packet's path. Commands were actually run with the full path; do not rerun over the preserved outputs. Scripts and result JSON retain exact inputs/checksums/library versions. Checker elapsed times are0.0755s and0.0929s excluding interpreter/library startup; the entire optional branch was well below30 minutes. Header/cohort/source inspection occurred around the checks. Payload bytes including small supporting tables/reports remain far below512MiB. No new uncertainty calculation or scoring convention was introduced.

Evidence checked: four bounded NPZ files and their header/checksum bindings,15 reported estimates, original metric source, current saved cohort/split membership.
Still uncertain: direct prediction-row identity, complete historical execution lineage, raw labels and higher-level independence.
Defensible conclusion: stored AP arithmetic is internally consistent in the selected banks; scientific reproduction and causal attribution remain unestablished.
