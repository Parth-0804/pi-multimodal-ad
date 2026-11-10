#!/usr/bin/env python3
"""Write Stage 4 dependency-limited results, without inventing predictions."""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd

from msm.data import digest, load_cohort
from msm.splits import nested_plan
from msm.smoke import write


def main(run):
    run = Path(run)
    c = json.loads((run / "config/resolved_config.json").read_text())
    protocol = json.loads((run / "config/stage3_protocol.original.json").read_text())
    status = json.loads((run / "manifests/execution_status.json").read_text())
    source = json.loads((run / "manifests/source_checkpoint_gate.json").read_text())
    split = json.loads((run / "manifests/split_gate.json").read_text())
    transfer = json.loads((run / "manifests/CNN_transfer_compatibility.json").read_text())
    prov = json.loads((run / "provenance.json").read_text())
    prior = json.loads((run / "manifests/prior_stage_integrity.json").read_text())
    contract = json.loads((run / "manifests/interval_contract_check.json").read_text())
    cross = json.loads((run / "manifests/cross_machine_feasibility.json").read_text())
    tests = json.loads((run / "evidence/final_validation_commands.json").read_text())
    if tests["exit_code"] or "61 passed" not in tests["observed_stdout"] or "No broken requirements found." not in tests["observed_stdout"]:
        raise ValueError("Required test/environment evidence missing")
    if status["MSM_model_fits"] or status["MSM_outer_predictions"] or split["ready"] or source["ready"]:
        raise ValueError("This report writer only describes the observed blocked execution")

    sensitivity = load_cohort(protocol["stage2"], label2="exclude")
    label2_gate = {"intervals": len(sensitivity), "positive_intervals": int(sensitivity.target.sum()),
                   "groups": sensitivity.group_id.nunique(), "positive_groups": sensitivity.loc[sensitivity.target == 1, "group_id"].nunique(), "ready": False}
    try:
        nested_plan(sensitivity, outer=3, inner=2, seed=protocol["split_seed"])
        label2_gate["ready"] = True
    except ValueError as exc:
        label2_gate["reason"] = str(exc)
    write(run / "manifests/label2_sensitivity_gate.json", label2_gate)
    comparisons = ["visual_R_minus_P", "F2_R_minus_P", "F2_P_minus_visual_P", "F2_P_minus_sensor_P", "F2_R_minus_visual_R", "F2_R_minus_sensor_R"]
    differences = pd.DataFrame([{"comparison": name, "seed": seed, "metric": metric,
        "difference": None, "CI_95_lower": None, "CI_95_upper": None, "status": status["status"]}
        for name in comparisons for seed in c["training_seeds"] for metric in ("AP", "AUROC")])
    with (run / "manifests/paired_differences_status.csv").open("x", newline="") as stream:
        differences.to_csv(stream, index=False)

    def report(name, body):
        with (run / name).open("x") as stream:
            stream.write(body.strip() + "\n")

    report("MSM_STAGE4_MODEL_RESULTS.md", f"""
# MSM Stage 4 model results

**Status: BLOCKED_COHORT_AND_SOURCE. No held-out model result is available.** The authorized Stage 4 execution validated the existing artifacts and stopped at scientific admission checks. It did not run a replacement design, promote Stage 3 smoke scores, or manufacture predictions/checkpoints/training curves. The user's Stage 4 instruction supplies execution authorization; the historical Stage 3 `full_matrix_authorized=false` flag is not the blocker.

Dataset **`{protocol['dataset_handle']}`**, Kaggle ID 8392825; [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [publication](https://www.nature.com/articles/s41597-026-07255-7). Run `{run}`, recorded UTC **{prov['created_UTC']}**. This report is a measured dependency audit, not a completed independent evaluation.

## Preconditions checked before fitting

1. **Stage 1–3 integrity passed.** Rechecked {sum(item['unique_artifacts_checked'] for item in prior)} unique recorded artifact/source identities: 41 Stage 1, 100 Stage 2, 35 Stage 3. All **{prov['immutable_MSM_raw_inputs_verified']} local MSM raw source files** (69 labels and 35 previously acquired pilot modalities/metadata) matched their recorded SHA-256. No source files, prior output, raw data, Phase 1 active fit or credentials were changed/read beyond the authorized dataset/checkpoint evidence. Shared early-stage navigation/ignore hashes were excluded where they had intentionally evolved; current Stage 3 identities matched.
2. **Input construction reconfirmed.** All 114 admitted annotation/frame-selection policies revalidated. Rebuilt all 114 × 90 actual MTC statistics with maximum absolute difference **{contract['statistics_max_abs_difference']}** versus the recorded Stage 2 features. Native interval membership and all source/target associations remain traceable. No new video decode, feature extraction, fitting or model scoring was needed for this audit.
3. **Frozen split failed.** 114 intervals in five experiment folders, but only two folders contain native label 1. The frozen three-outer/two-inner experiment-disjoint design requires both classes in each fitting and assessment partition. Its implementation raises `{split['reason']}`. No seed search, fold reduction, interval shuffle, within-experiment split or test-driven cohort replacement was used.
4. **Source dependency failed.** Phase 1 had **{source['completed_C_fits_observed']} completed C/full-backbone fits** at snapshot. One completed B/frozen-head fit is not an R source; an active C checkpoint has no completion receipt. Source-domain numerical preflight passed, but its diagnostic weights are not a completed training-selected source model. Details: `MSM_CNN_WEIGHT_TRANSFER.md`.

## Actual counts and metrics availability

Native classes: **93 label 0 / 10 label 1 / 11 label 2**. For the frozen cutting-abnormality target, label 1 is positive and labels 0/2 are stable-cutting negatives: **104 negative / 10 positive**, cohort prevalence **10/114 = 0.0877192982**. This is observed cohort prevalence, not an outer-test metric. Label 2 means a defective tool during stable cutting, not automatically abnormal cutting.

| Initialization | Visual-only | Matched sensor-only | Static F2 |
| --- | --- | --- | --- |
| P: original pretrained CNN | Not run: cohort gate | Not run: cohort gate | Not run: cohort/OOF gate |
| R: completed full-backbone REASSEMBLE CNN | Not run: cohort + source gates | Not run: cohort gate; same matched sensor contract | Not run: cohort + source/OOF gates |

**AP, AUROC, held-out prevalence, Brier/log loss, per-fold/per-seed scores, paired effects and uncertainty intervals are unavailable.** Missing values in tables are blank/NA, never zero scores. No model is declared superior or inferior; no best fold or seed was selected. Interval-resampled confidence intervals cannot repair absent independent positive groups.

The predeclared label-2-exclusion sensitivity also fails: **103 intervals / four folders / two positive folders**, still ten positive intervals. It cannot rescue the evaluation and was not selected after inspecting performance.

## Frozen controlled comparison retained

Both conditions would use the same eligible intervals, original source-frame indices/PTS, aspect-preserving 640×640 preprocessing, 16-frame mean pooling, exact group partitions, 896→128→1 newly initialized MSM head, training-only standardization, weighted BCE, AdamW LR 0.001/decay 0.001, batch 32, clipping 1, ten fixed epochs, threshold 0.5, and all three MSM seeds **42, 123, 20261023**. Both CNNs remain **frozen/eval** per Stage 3. Full-backbone *source* training does not authorize changing MSM freezing rules for only R.

The sensor model remains the identical 90-feature balanced logistic C=1. Separately fit P-F2 and R-F2, each unweighted logistic C=1 over its own `[p_visual,p_sensor]` probabilities from strictly group-held-out inner fits. No source-domain head, scaler, calibrator or F2 coefficient transfers. Source R's canonical role was fixed without MSM results. No calibration or threshold search is added to the frozen protocol.

If dependencies eventually pass, the primary P/R comparison implies **54 visual-head fits** (27 per initialization), 18 F2 fits and nine unique deterministic sensor partitions that can be shared across conditions/seeds. This is a planned count, not completed work. A new matched eligibility/split manifest and validated resumable execution path would be needed before long fitting; Stage 3's inference/development checkpoint is not a resumable full-matrix artifact. No arbitrary GPU-hour cutoff caused this stop.

## Artifacts delivered

| Artifact | Actual content |
| --- | --- |
| `manifests/planned_results_status.csv` | All 54 requested initialization × seed × outer-fold × model result slots marked blocked, blank metrics |
| `manifests/predictions.csv` | Explicit prediction schema, **zero data rows**; no invented scores |
| `manifests/paired_differences_status.csv` | All requested P/R and fusion-vs-branch AP/AUROC comparisons per seed marked unavailable, blank intervals |
| `manifests/selected_checkpoints.json` | Empty selection with gate reasons; Stage 3 development checkpoint not promoted |
| `manifests/training_curves.csv` | Schema, **zero data rows**; no MSM Stage 4 training occurred |
| `figures/cohort_class_coverage.png` | Actual five-experiment native-label coverage plot; **not** a learning curve |
| `config/resolved_config.json` | Stage 4 authorization, matching rules and source selection |
| `config/stage3_protocol.original.json` | Exact preserved frozen scientific configuration bytes |
| `provenance.json`, `validation.json`, manifests | Runtime, CPU/GPU observation, versions, SHA-256, commands and tests |

There are no selected MSM Stage 4 checkpoints or trained-model curves to provide. Existing Stage 3 smoke checkpoints and source Phase 1 curves remain historical evidence, not substitutes for missing requested deliverables. Bulk media/checkpoints remain Git-ignored.

## Costs and validation

Stage 4 measured audit body: **{prov['audit_wall_seconds']:.3f} s wall / {prov['audit_CPU_seconds']:.3f} s CPU**, excluding interpreter/import startup. CPU resident memory at completion about **{prov['audit_peak_RSS_bytes']/1024**2:.1f} MiB**. The provenance key `audit_peak_RSS_bytes` records an end-of-body RSS observation, not a sampled peak; do not interpret it as peak memory. Original and diagnostic CNN states were inspected on CPU. **No CUDA context was created**, no MSM training GPU time accrued, and no MSM forward/inference/training throughput was measured in Stage 4.

The visible T4 had another Phase 1 process using about **9,264 MiB** and device-wide **100%** utilization. That is its workload, not MSM utilization. It continued untouched. Prior Stage 3 throughput/smoke costs remain in its own report and are not charged as Stage 4 training or independent accuracy evidence.

**61 synthetic/regression tests passed in 8.25 s**, including 15 new CNN transfer/source-consistency cases. `pip check` and `git diff --check` passed. Prior tracked Git diff remains three pre-existing files / 22 insertions. New files are confined to `MILLING DATASET/`; nothing staged/committed and no environment packages installed.

## Answers to the eight research questions

1. **Does the architecture work on MSM?** Its aligned interval construction and bounded forward/gradient/checkpoint pipeline work on the filtered subset. Predictive adaptation success under independent evaluation is **not established**.
2. **Does F2 improve over unimodal components?** **Unknown**; no held-out F2 or matched branch scores exist.
3. **Does REASSEMBLE initialization help or hurt?** **Unknown**; there is no admissible completed R checkpoint and no matched MSM evaluation.
4. **Stable across seeds?** **Unknown**; the three-seed evaluation was not run. A single Stage 3 development seed does not establish stability.
5. **Evidence of overfitting?** **Not assessed for MSM.** No Stage 4 learning/test curves exist; architecture size, the source-domain learning curve or a tiny smoke loss cannot establish MSM overfitting.
6. **Computational cost?** Audit cost above; **zero Stage 4 MSM model fits, optimizer steps, predictions and training GPU seconds**. Full evaluation cost is unmeasured.
7. **Cross-domain representation claim?** **Unsupported.** Tensor compatibility is software evidence, not demonstrated transfer benefit or causal representation generality.
8. **Exploratory/inconclusive findings?** Coarse visual context and MTC feature construction are validated engineering findings. Transfer efficacy, fusion gain, independent generalization, seed stability and calibration remain **inconclusive**. Corrupted/missing-modality robustness was not evaluated and is not claimed.

**Stop after this Stage 4 dependency-limited execution.** Prerequisites for a future evaluation: expand and independently audit positive laboratory experiments, resolve physical grouping, freeze a valid three-outer/two-inner assignment, obtain the completed canonical Phase 1 C checkpoint and validate the resumable matched runner. The present output does not claim completion of the experimental matrix.
""")

    report("MSM_CNN_WEIGHT_TRANSFER.md", f"""
# MSM CNN weight transfer

**Transfer efficacy is not evaluated: the required trained source checkpoint is unavailable.** A CPU-only state compatibility audit and strict transfer adapter are complete. No diagnostic or active checkpoint was used as condition R, and no source-domain classification/fusion weights were applied to MSM.

## Source selection fixed without MSM performance

Original P: verified local `PekingU/rtdetr_r18vd`, revision **ac77a11ff0170a41b771c03264987f8ce2b0d753**. Original safetensors SHA-256 **fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093**, with matching config/preprocessor hashes in `manifests/CNN_transfer_compatibility.json`. Only the executed ResNet CNN would initialize MSM; no hybrid encoder/decoder/detection outputs are used.

Canonical R rule, locked in `config/resolved_config.json`: Phase 1 arm **C_full_finetuned16**, source seed **42**, original outer fold **0** (human fold 1), role **outer_assessment**, job index **4**. Use that role's completed, source-validation-selected best checkpoint. It is a fixed source identity, not an MSM AP-based choice. All three MSM seeds would reuse this same R source, testing MSM fitting variability, not source-training-seed variability. There is no implicit permission to choose a better source from MSM test results.

Expected folder: `{source['canonical_source_folder']}`. A completed individual canonical C fit is sufficient after provenance verification; completing all 150 Phase 1 fits is **not** an arbitrary additional gate.

At snapshot **{prov['created_UTC']}**:

| Source candidate | Observed state | Admissibility |
| --- | --- | --- |
| Original pretrained P | Hashes match; 11,190,112 executed-CNN parameters | P initialization available |
| Completed B_long_frozen16 inner fit | One completion receipt; head-only checkpoint, original CNN stayed frozen | Cannot establish REASSEMBLE-trained CNN transfer |
| Active C_full_finetuned16 inner fit | Best/recovery checkpoint filenames exist; no completion receipt | Unfinished training/selection; not an admissible source |
| Canonical C outer-assessment fit | No completed selected checkpoint | R dependency missing |
| Full-CNN preflight reload file | Hash-verified diagnostic; numeric/recovery tests passed | Architecture/state audit only, never condition R |

Phase 1's **numeric gate PASSED** proves executed-CNN gradients/updates/reload/recovery on its pilot. It does not turn the diagnostic into a completed, validation-selected source fit. `PHASE1_COMPLETED_FIT_INDEX.json` recorded one B and **zero C** completions; `PHASE1_ALL_COMPLETE.json` was absent. Active snapshots are point-in-time observations and may change as the independent Phase 1 controller runs. No active `.pt` payload was read or copied. Stable completed B and diagnostic hashes were checked; source-domain held-out performance did not choose R.

## Measured compatible tensor scope

CPU structural audit used the immutable preflight reload payload solely to verify Phase 1 serialization compatibility with the original CNN. It was never loaded for MSM prediction/training:

- Original backbone has **{transfer['original_backbone_state_tensors']} state tensors**, **{transfer['original_backbone_parameters']:,} parameters**.
- Diagnostic serialization provides exactly **{transfer['compatible_CNN_tensors_in_diagnostic_payload']} compatible CNN tensors**, no missing/extra names and no shape/dtype/nonfinite errors.
- **{transfer['diagnostic_tensors_changed_vs_P']} tensors differ from original pretrained P** in that diagnostic. This confirms changed values exist in the serialization, not transfer efficacy or learned generality.
- Six source-domain entries are explicitly excluded: four visual-head weights/biases and `mean`, `std`. Sensor parameters, calibrators, F2 coefficients, optimizer/RNG and labels are not transferable input state.
- Diagnostic hash **{transfer['diagnostic_checkpoint_sha256']}**; exact path and exclusions are recorded in `manifests/CNN_transfer_compatibility.json`.

Phase 1 promotes FrozenBatchNorm affine weight/bias buffers into trainable Parameters. Their **state-dict names/shapes do not change**. Transfer must include their learned values along with all convolutions and preserved normalization running buffers, then load into the new frozen MSM backbone with `strict=True`. Discarding affine values or loading only the final stage would change the defined source condition. Both P and R then execute the same frozen/eval CNN and identical pooling/input transform; only initialization values differ.

## Reusable implementation and tests

`MILLING DATASET/source/msm/transfer.py` adds three focused functions:

1. `validated_source`: require final completion receipt, exact C arm/seed/predefined job, at least 25 completed source epochs, selected epoch/identity consistency, checkpoint SHA-256 before/after safe `weights_only=True` CPU loading.
2. `compatible_cnn_state`: select only exact `backbone.*` state and require complete target names/shapes/dtypes/finite values, including normalization buffers. Reject partial, detector, head-only and invalid states before modifying a target.
3. `transfer_completed_cnn`: load only the verified CNN into a supplied new MSM backbone and freeze it. It never loads source heads/scalers/fusion.

Fifteen new synthetic tests cover valid CNN-only state including buffers, head/scaler exclusion, incomplete/extra/shape/dtype/nonfinite tensors, absent completion, wrong source arm/seed/role/hash/identity/epoch and premature source completion. All 61 MSM tests pass. No executed operation mutated the active source fit, model framework or historical outputs.

## What the comparison can eventually support

After both cohort and canonical-source gates pass, fit new MSM heads with the same three seeds and fixed budget, compare held-experiment AP and other frozen metrics, and refit F2 independently from P/R group-OOF predictions. Use paired group-cluster uncertainty, not best-fold/seed selection. Additional source pretraining exposure and source checkpoint identity are part of condition R and must be reported. One fixed source checkpoint does not establish robustness over all REASSEMBLE training seeds.

Present conclusion: **CNN serialization compatibility is verified; positive or negative transfer, F2 benefit and a cross-domain representation claim are unmeasured.** Selected R source and selected MSM Stage 4 checkpoints remain empty in `manifests/selected_checkpoints.json`.
""")

    report("MSM_GENERALIZATION_EVALUATION.md", f"""
# MSM generalization evaluation

**No independent held-out model evaluation was admissible under the frozen protocol.** This report measures label/group/modality support, not prediction accuracy. Dataset `{protocol['dataset_handle']}`; exact group audit is `manifests/cohort_by_experiment.csv`.

## Actual eligible cohort

| Experiment | Label 0 | Label 1 | Label 2 | Binary positive prevalence |
| --- | ---: | ---: | ---: | ---: |
| imi_vm20i/dataset1 | 0 | 8 | 0 | 100% |
| imi_vm20i/dataset4 | 0 | 0 | 11 | 0% |
| imi_vm20i/dataset19 | 18 | 0 | 0 | 0% |
| imi_vmx30ui/dataset8 | 64 | 0 | 0 | 0% |
| imi_vmx30ui/dataset9 | 11 | 2 | 0 | 15.38% |
| TOTAL | 93 | 10 | 11 | 8.77% |

Native label 2 stays a stable-cutting negative for intervention-worthy cutting abnormality. The pure-positive VM20i/dataset1 and pure-negative folders illustrate why random interval/frame splits could learn experiment conditions. Holding complete experiments is necessary; it does not itself prove physical independence. Label-2 exclusion yields 103 intervals, four folders and the same two positive folders; it also fails the primary split gate.

Frozen three-outer/two-inner grouping cannot assign positives to three outer tests from two positive folders. Holding out one positive folder leaves only one positive training folder, which also prevents complete two-fold group-held-out branch probability construction for F2: one inner model would train without positives. Repeating seeds or bootstrapping intervals does not create independent anomalous experiments. Stage 3 smoke OOF fitting was development-only and is not a substitute for an outer test.

The five folders collapse to **three machine/reference-date clusters**, only **two positive clusters**. Physical tool/workpiece/session identities remain unresolved. Those dates are filename-reference proxies, not proven independent sessions; both the nominal and stricter grouping audit have insufficient support. Any future generalization claim must disclose that dependence.

## Cross-machine feasibility

Both laboratory machines have video and the same 15-channel MTC schema, but their class distributions differ sharply:

| Machine | Verified intervals | Experiment groups | Positive groups | Native 0 / 1 / 2 | Positive prevalence |
| --- | ---: | ---: | ---: | --- | ---: |
| imi_vm20i | 37 | 3 | 1 | 18 / 8 / 11 | 21.62% |
| imi_vmx30ui | 77 | 2 | 1 | 75 / 2 / 0 | 2.60% |

| Training → held-out machine | Train / test intervals | Both classes in each side? | Matching two-inner F2 bank? |
| --- | --- | --- | --- |
| VM20i → VMX30Ui | 37 / 77 | Yes | No: only one positive training group |
| VMX30Ui → VM20i | 77 / 37 | Yes | No: only one positive training group |

Thus technical input compatibility exists, but **matched full-architecture cross-machine evaluation fails in both directions**. No classifier or fusion scores were generated. A separately declared unimodal-only diagnostic would be a different question from the frozen matched full-model experiment and was not substituted. Prevalence, operating regimes, material distribution, tool condition and sensor update/aggregation rates can confound any eventual comparison; report them with model results and both-class denominators.

## Laboratory versus industry

Stage 1 counted 56 laboratory folders / 2,512 native intervals / 458 label-1 intervals in 25 nominal positive folders, but only the five laboratory folders above have a verified joint Stage 2 cohort. Candidate annotation counts are not aligned sample counts. Every added video requires the corrected label-blind alignment/support checks, unique 16-frame selection, camera-context review, native sensor gates and physical-group audit before its rows enter evaluation.

The 13 VF10 industrial folders have no provided video. The pilot industry MTC schema differs, CT is about one sample per 10 s, and material/machine conditions differ. **Zero industry visual-plus-sensor examples are eligible.** No industrial sensor-only score was produced or described as generalization of this visual architecture. Audio/sensor alternatives require their own explicit protocol and are not automatically substituted.

## Interpretation and required evidence

No experiment-disjoint AP/AUROC, seed stability, overfitting curve, transfer effect or confidence interval is available from Stage 4. Current positive prevalence and class-support counts are descriptive audit findings, not test results. The diagnostic CNN's compatible tensors establish software portability only. Frequent coolant occlusion and unknown MTC aggregation latency also restrict future interpretation to coarse retrospective milling-context classification unless separately resolved. Corrupted/missing-modality robustness is untested.

Before a resumed independent evaluation: obtain and audit more positive laboratory experiments under the same version, target and eligibility rules; reconcile dependency groups; freeze and validate the three-outer/two-inner partition; obtain the completed canonical REASSEMBLE full-CNN source; validate resumable P/R execution, then run all fixed seeds and report paired experiment-cluster uncertainty. No test-score-guided cohort/split/source selection is permitted.

All zero-prediction and blocked-result tables are preserved in this run. **Stop after Stage 4; no unsupported generalization or representation-transfer conclusion is drawn.**
""")

    report("REVIEW_HANDOFF.md", f"""
# Stage 4 dependency-limited handoff

Status **{status['status']}**. The user authorized Stage 4; scientific cohort/source prerequisites remain unsatisfied. Read `MSM_STAGE4_MODEL_RESULTS.md`, `MSM_CNN_WEIGHT_TRANSFER.md`, `MSM_GENERALIZATION_EVALUATION.md`.

Measured: 114 aligned examples, 90 statistics each with exact recorded parity, two positive experiment groups; zero completed source C fits at snapshot. 115 CNN tensors structurally compatible with diagnostic serialization; no diagnostic source used on MSM. 61 tests pass. Zero Stage 4 model fits, predictions, training GPU seconds or selected checkpoints. Blank metric/curve tables are explicit unavailable outputs, not zero performance.

New reusable source: `MILLING DATASET/source/msm/transfer.py`, `source/msm/stage4_audit.py`; report writer `source/write_stage4_reports.py`; config `configs/stage4_execution.json`; tests `tests/test_stage4_transfer.py`. All prior artifacts preserved. Raw inputs unchanged, no downloads or packages installed, no other jobs interrupted, no commit/staging.

Future execution requires an expanded audited cohort, defensible groups and a valid canonical full-CNN source. No alternative evaluation, checkpoint selection by MSM results, sensor-only industry substitution or missing-modality claim was made. Stop here.
""")

    for file in [*Path("MILLING DATASET/source/msm").glob("*.py"), Path(__file__), Path("MILLING DATASET/tests/test_stage4_transfer.py")]:
        ast.parse(file.read_text(), filename=str(file))
    diff = subprocess.run(["git", "diff", "--check"], text=True, capture_output=True)
    if diff.returncode:
        raise ValueError("Whitespace verification failed")
    validation = {"passed": True, "created_UTC": datetime.now(timezone.utc).isoformat(), "evaluation_completed": False,
        "status": status["status"], "test_count": 61, "tests_evidence": "evidence/final_validation_commands.json",
        "pip_check": "passed", "git_diff_check": "passed", "source_AST": "passed",
        "prior_stage_artifacts_verified": sum(item["unique_artifacts_checked"] for item in prior),
        "MSM_raw_sources_verified": prov["immutable_MSM_raw_inputs_verified"],
        "all_native_annotation_frame_policies_revalidated": True, "sensor_feature_max_abs_difference": 0.,
        "CNN_state_tensors_compatible": transfer["compatible_CNN_tensors_in_diagnostic_payload"],
        "source_diagnostic_not_used_as_R": True, "active_training_payload_not_read": True,
        "new_model_fits": 0, "new_outer_predictions": 0, "performance_metrics_estimated": False,
        "CUDA_context_created": prov["CUDA_context_created_by_stage4"]}
    write(run / "validation.json", validation)
    write(run / "manifests/commands.json", {"common_environment": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONPATH": "src:MILLING DATASET/source"},
        "commands": [f"ma_thesis_env/bin/python -B -m msm.stage4_audit --config 'MILLING DATASET/configs/stage4_execution.json' --output '{run}'",
                     "ma_thesis_env/bin/python -B -m pytest -q 'MILLING DATASET/tests' --disable-warnings",
                     "ma_thesis_env/bin/python -B -m pip check", "git diff --check", "git diff --stat",
                     f"ma_thesis_env/bin/python -B 'MILLING DATASET/source/write_stage4_reports.py' --run '{run}'"],
        "no_training_command_executed": True, "report_writer_sha256": digest(__file__)})
    entries = []
    candidates = [*run.rglob("*"), Path(__file__), Path("MILLING DATASET/source/msm/transfer.py"),
                  Path("MILLING DATASET/source/msm/stage4_audit.py"), Path("MILLING DATASET/configs/stage4_execution.json"), Path("MILLING DATASET/tests/test_stage4_transfer.py")]
    for file in sorted(set(candidates)):
        if not file.is_file():
            continue
        ignored = subprocess.run(["git", "check-ignore", "-q", str(file)]).returncode == 0
        entries.append({"path": str(file), "bytes": file.stat().st_size, "sha256": digest(file), "git_ignored": ignored})
    write(run / "manifests/output_manifest.json", {"self_excluded": True, "created_UTC": datetime.now(timezone.utc).isoformat(), "files": entries})
    print(json.dumps({"reports": str(run), "status": status["status"], "tests": 61, "evaluation_completed": False}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
