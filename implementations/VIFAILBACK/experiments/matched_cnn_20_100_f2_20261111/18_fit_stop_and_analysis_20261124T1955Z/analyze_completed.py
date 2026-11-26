"""Independent saved-score arithmetic and a researcher-stopped scope handoff.

No model, raw video, sensor payload, feature bank or training entry point is
loaded. Existing OOF F2 fitting/assessment is performed by the original runner.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import os

import numpy as np
from sklearn.metrics import (average_precision_score, roc_auc_score,
                             brier_score_loss, log_loss)

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO = STUDY.parents[2]
MODELS = ("visual", "sensor_LR", "average", "F2", "historical_HGB", "historical_V1")


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    temporary = path.with_name(path.name + f".writing.{os.getpid()}")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    os.replace(temporary, path)


def table(headers, rows):
    return "\n".join(["|" + "|".join(headers) + "|", "|" + "|".join("---" for _ in headers) + "|"] +
                     ["|" + "|".join(str(x).replace("|", "/") for x in row) + "|" for row in rows])


def scores(y, probability):
    failure = average_precision_score(y, probability)
    success = average_precision_score(1-y, 1-probability)
    return {"AP_failure": float(failure), "AP_success": float(success),
            "macro_AP": float((failure+success)/2), "AUROC": float(roc_auc_score(y, probability)),
            "Brier": float(brier_score_loss(y, probability)),
            "log_loss": float(log_loss(y, probability, labels=[0, 1]))}


def independent_interval(y, a, b, tasks, draws=2000, seed=20261111):
    """Independent sklearn weighted AP implementation of paired task resampling."""
    groups, indices = np.unique(tasks, return_inverse=True)
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(draws):
        counts = np.bincount(rng.integers(len(groups), size=len(groups)), minlength=len(groups))
        weights = counts[indices]
        if weights[y == 1].sum() == 0 or weights[y == 0].sum() == 0:
            continue
        def macro(p):
            return (average_precision_score(y, p, sample_weight=weights) +
                    average_precision_score(1-y, 1-p, sample_weight=weights))/2
        differences.append(macro(a)-macro(b))
    if not differences:
        raise ValueError("No valid paired task resamples")
    return np.quantile(differences, [.025, .975]).tolist(), len(differences)


def formatted_interval(value):
    if not value:
        return "Untested / insufficient support"
    return (f"{value['difference']:+.6f} [{value['lower95']:+.6f}, {value['upper95']:+.6f}]; "
            f"{value['interpretation']}")


def records_for(cohort):
    folds = range(3) if str(cohort["outer"]) == "pooled3" else [cohort["outer"]]
    records = []
    for fold in folds:
        root = STUDY / "09_f2_fusion" / cohort["condition"] / f"seed{cohort['seed']}" / f"outer{fold}"
        receipt = read(root / "COMPLETE.json")
        if digest(root / "OUTER_PREDICTIONS.json") != receipt["prediction_sha256"]:
            raise ValueError("Fusion prediction hash changed")
        if digest(root / "metrics.json") != receipt["metrics_sha256"]:
            raise ValueError("Fusion metrics hash changed")
        lock = read(root / "FIT_LOCK.json")
        if lock["outer_prediction_records_loaded_before_fit"] or lock["outer_labels_used_in_fitting"]:
            raise ValueError("F2 fitting/assessment separation failed")
        records.extend(read(root / "OUTER_PREDICTIONS.json"))
    ids = [r["episode_index"] for r in records]
    if len(ids) != len(set(ids)) or len(ids) != cohort["assessment_N"]:
        raise ValueError("Assessment example identity/count mismatch")
    return records


def analyze(phase):
    folder = HERE / ("initial_analysis" if phase == "initial" else "completed_scope_analysis")
    folder.mkdir(exist_ok=False)
    result_path = STUDY / "11_metrics_and_statistics/CURRENT_RESULTS.json"
    results = read(result_path)
    fits = read(STUDY / "11_metrics_and_statistics/FIT_COVERAGE.json")
    request = read(HERE / "CONTROL_REQUEST.json")
    keyed = {}
    metric_checks = []
    for cohort in results["cohorts"]:
        records = records_for(cohort)
        key = (cohort["condition"], cohort["seed"], str(cohort["outer"]))
        keyed[key] = records
        y = np.asarray([r["label"] for r in records], dtype=int)
        if set(y) != {0, 1}:
            raise ValueError("Expected both native outcome classes")
        for model in MODELS:
            p = np.asarray([r[model] for r in records], dtype=float)
            measured = scores(y, p)
            errors = {k: abs(v-cohort["metrics"][model][k]) for k, v in measured.items()}
            if max(errors.values()) > 1e-10:
                raise ValueError(f"Independent saved-score disagreement: {key}, {model}, {errors}")
            metric_checks.append({"condition": key[0], "seed": key[1], "fold": key[2], "model": model,
                                  "assessment_N": len(y), "failure_prevalence": float(y.mean()),
                                  "metrics": measured, "max_absolute_difference": max(errors.values())})
    # The newly completed FULL20 comparison and the existing FULL100 pilot are
    # independently recomputed with a second, sklearn-based bootstrap path.
    interval_checks = []
    for contrast in results["matched_contrasts"]:
        if contrast["treatment"] not in ("FULL20", "FULL100"):
            continue
        a = keyed[(contrast["treatment"], contrast["seed"], str(contrast["fold"]))]
        b_lookup = {r["episode_index"]: r for r in keyed[(contrast["control"], contrast["seed"], str(contrast["fold"]))]}
        if set(b_lookup) != {r["episode_index"] for r in a}:
            raise ValueError("Paired model assessment IDs differ")
        b = [b_lookup[r["episode_index"]] for r in a]
        if any((x["label"], x["task_id"]) != (z["label"], z["task_id"]) for x, z in zip(a, b)):
            raise ValueError("Paired labels or task IDs differ")
        for branch in ("visual", "F2"):
            saved = contrast[branch]
            y = np.asarray([r["label"] for r in a], dtype=int)
            lower_upper, valid = independent_interval(y, np.asarray([r[branch] for r in a]),
                np.asarray([r[branch] for r in b]), np.asarray([r["task_id"] for r in a]),
                saved["requested"], saved["seed"])
            expected = saved["macro_AP"]
            if not np.allclose(lower_upper, [expected["lower95"], expected["upper95"]], atol=1e-10, rtol=0):
                raise ValueError("Independent paired task interval disagreement")
            interval_checks.append({"treatment": contrast["treatment"], "control": contrast["control"],
                "seed": contrast["seed"], "fold": contrast["fold"], "branch": branch,
                "lower95": lower_upper[0], "upper95": lower_upper[1], "valid_draws": valid,
                "scope": "fixed models; paired canonical-task resampling; no refitting/selection uncertainty"})
    completed = [r for r in fits if r["complete"]]
    incomplete = [r for r in fits if not r["complete"]]
    full_completed = [r for r in completed if r["condition"] == "FULL20"]
    target_complete = read(HERE/"STOP_RECEIPT.json")["target_complete"] if phase == "final" else False
    summary = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "phase": phase,
        "classification": "VERIFIED saved-score arithmetic and inspected completion records; not training reproduction",
        "analysis_source_sha256": digest(Path(__file__)),
        "control_request_sha256": digest(HERE/"CONTROL_REQUEST.json"),
        "authority": request["authorization"], "current_results_sha256": digest(result_path),
        "completed_fits": len(completed), "unfinished_fits": len(incomplete),
        "FULL20_completed_fits": len(full_completed), "base_fusion_cohorts": results["completed_fusion_cohorts"],
        "cohorts_including_per_seed_pooled_views": len(results["cohorts"]),
        "metric_vector_checks": len(metric_checks), "scalar_metric_checks": len(metric_checks)*6,
        "independent_paired_interval_checks": len(interval_checks),
        "training_reproduced": False, "new_CNN_training_launched": False,
        "remaining_GPU_planning_constraint_days": 47,
        "runtime_constraint_classification": "INFERRED planning allowance requested by researcher; split-weighted measured-rate central estimate approximately 43 days; not elapsed runtime",
        "metric_checks": metric_checks, "interval_checks": interval_checks,
        "unexecuted_full20_fits": [{k:r[k] for k in ("condition","seed","fit_id","executed_epochs")} for r in incomplete]}
    write_json(folder / "INDEPENDENT_VERIFICATION.json", summary)
    compact = []
    for cohort in results["cohorts"]:
        # Keep pooled three-fold results per seed separate from the one-fold FULL20 and pilots.
        if str(cohort["outer"]) != "pooled3" and cohort["condition"] not in ("FULL20","FROZEN100","FULL100","DONOR100"):
            continue
        m = cohort["metrics"]
        compact.append([cohort["condition"],cohort["seed"],cohort["outer"],cohort["assessment_N"],
                        f"{m['visual']['macro_AP']:.6f}",f"{m['sensor_LR']['macro_AP']:.6f}",
                        f"{m['F2']['macro_AP']:.6f}",f"{m['historical_HGB']['macro_AP']:.6f}"])
    contrasts = []
    for row in results["matched_contrasts"]:
        contrasts.append([row["treatment"]+" minus "+row["control"],row["seed"],row["fold"],
                          formatted_interval(row["visual"].get("macro_AP")),
                          formatted_interval(row["F2"].get("macro_AP"))])
    count_rows=[]
    for condition in ("FROZEN20","FULL20","DONOR20","FROZEN100","FULL100","DONOR100"):
        xs=[r for r in fits if r["condition"]==condition]
        count_rows.append([condition,len(xs),sum(x["complete"] for x in xs),
                           sum(not x["complete"] for x in xs)])
    scope_text = ("The training controller is stopped; remaining CNN work is NOT RUN / PARTIAL — RESEARCHER STOP."
                  if phase == "final" else "Stop guard armed: finish the current fit, then start no further CNN fits. This is a pre-completion snapshot.")
    findings = []
    for row in results["matched_contrasts"]:
        if row["treatment"] in ("FULL20", "FULL100"):
            findings.append(f"{row['treatment']} versus {row['control']}, seed {row['seed']}, fold {row['fold']}: "
                f"visual macro-AP {formatted_interval(row['visual'].get('macro_AP'))}; "
                f"F2 macro-AP {formatted_interval(row['F2'].get('macro_AP'))}.")
    if not any(row["treatment"] == "FULL20" for row in results["matched_contrasts"]):
        findings.append("FULL20 versus FROZEN20 remains untested until the current fit and complete outer0 OOF assessment finish.")
    detail_rows = []
    coefficient_rows = []
    for cohort in results["cohorts"]:
        if str(cohort["outer"]) != "0" or cohort["seed"] != 42:
            continue
        for model in ("visual", "sensor_LR", "average", "F2", "historical_HGB"):
            m = cohort["metrics"][model]
            detail_rows.append([cohort["condition"],model,f"{m['positive_prevalence']:.4f}",
                f"{m['AUROC']:.6f}",f"{m['AP_success']:.6f}",f"{m['Brier']:.6f}",
                f"{m['ECE10']:.6f}",f"{m['recall_failure']:.4f}",f"{m['recall_success']:.4f}"])
        if "f2_coefficients" in cohort:
            coefficients=cohort["f2_coefficients"]
            coefficient_rows.append([cohort["condition"],cohort["meta_N"],
                f"{coefficients['coefficient'][0]:+.6f}",f"{coefficients['coefficient'][1]:+.6f}",
                f"{coefficients['intercept']:+.6f}"])
    lines = ["# Completed-scope result analysis", "", scope_text, "",
        f"Generated {summary['utc']}. {len(completed)} completed fit records; {len(incomplete)} unfinished planned fits. "
        "The original 111-fit protocol remains preserved; this administrative cap does not turn its unexecuted work into negative results.", "",
        "## Training evidence and scope", "",
        table(["Condition","Original planned fits","Completed","Unfinished / not run"],count_rows), "",
        "VERIFIED: independent saved-score arithmetic, per-example identity checks, prediction/metric hashes, F2 fit-lock separation "
        "and two-class assessment support within the saved completed scope. Completion/checkpoint lineage is inspected evidence; "
        "training was not rerun. Original source/checkpoint hashes remain in FIT_COVERAGE and per-fit COMPLETE receipts.", "",
        "## Assessment results", "",
        "The native positive class is whole-episode failure (1). Both-class macro AP is the arithmetic mean of failure-class "
        "AP and success-class AP; it is average precision, not trapezoidal PR area. Prevalence varies by assessment fold and is "
        "recorded in INDEPENDENT_VERIFICATION.json. Each pooled3 row pools only that seed's three disjoint outer assessments; "
        "it is not mean-fold AP and is not a larger sample formed by pooling seeds.", "",
        table(["Condition","Seed","Fold / pooled","N","Visual macro AP","Sensor LR macro AP","F2 macro AP","Historical HGB macro AP"],compact), "",
        "HGB is a secondary historical sensor baseline and is not an input to original F2. The 100-epoch rows use their frozen "
        "single-bank pilot protocol; they must not be silently pooled with the 20-epoch nested-OOF study.", "",
        "## Main findings within completed coverage", "", "\n\n".join(findings), "",
        "The original paired uncertainty results are independently rechecked for the available full-CNN comparisons. "
        "A higher point estimate alone does not establish an improvement when its paired interval crosses zero. "
        "The completed frozen/donor rows retain their full per-seed pooled results; no seed or fold is selected by the assessment scores.", "",
        "## Calibration and class-specific trade-offs — seed42, fold0", "",
        table(["Condition","Model","Failure prevalence","AUROC","Success AP","Brier","ECE10","Failure recall@0.5","Success recall@0.5"],detail_rows), "",
        "The threshold remains the predeclared 0.5; no outer-test threshold tuning is performed. Recall, class AP and calibration "
        "must be assessed alongside macro AP. ECE10 and threshold summaries in this table are the existing report's values; the "
        "independent checks below cover AP, AUROC, Brier and log loss. The same assessment episodes appear across matched model rows.", "",
        "## F2 fitting — seed42, fold0", "",
        table(["Condition","OOF / pilot meta N","Visual probability coefficient","Sensor probability coefficient","Intercept"],coefficient_rows), "",
        "F2 is an L2 logistic model of calibrated visual and sensor-LR probabilities. Signed unrestricted coefficients are not "
        "convex weights, causal modality importance or percentages. The 20-epoch fit uses the complete three-inner OOF bank; "
        "the 100-epoch pilot uses its distinct predefined held-out meta bank. No assessment labels fit these coefficients.", "",
        "## Matched visual-training comparisons", "",
        table(["Treatment minus control","Seed","Fold","Visual delta [95% interval]","F2 delta [95% interval]"],contrasts), "",
        "Intervals resample paired canonical-task clusters conditional on fixed fitted models. They omit refitting, seed variability, "
        "donor/selection uncertainty and unverified session/operator dependence. These are exploratory marginal intervals without "
        "multiplicity adjustment. An interval crossing zero is inconclusive and does not establish equivalence.", "",
        "## Limits and unfinished questions", "",
        "FULL20 is limited to seed42, outer fold0 when the current inner2 fit completes. It cannot establish three-fold or "
        "three-seed full-CNN stability. FROZEN20 and DONOR20 retain their completed three-fold/three-seed coverage. "
        "Finishing inner2 permits the already specified outer0 F2 analysis only after all three inner OOF roles and the outer-final "
        "receipt pass the unchanged gates; in-sample replacements are prohibited. Any other uncompleted FULL20 assessments remain untested.", "",
        "The study remains retrospective completed-episode classification on previously examined tasks. No new independent cohort, "
        "online early-warning, deployment readiness or general robustness claim follows. No new corruption/GPU experiment is launched "
        "under this stop instruction. Donor features reuse learned source CNN weights, whereas the other arms use their recorded original "
        "initialization; neither detector heads nor a full detector training path should be inferred.", "",
        "INFERRED resource constraint: completing the remaining FULL20 matrix would require approximately 47 additional GPU days as "
        "a planning allowance on the current single T4 (approximately 43 days at the measured split-weighted central rate, with variation "
        "and overhead). This is estimated future runtime, not47 elapsed GPU days and not a model-performance result. "
        "The researcher therefore requested stopping further CNN training; this is not evidence that the unfinished models performed poorly.", "",
        "## Independent arithmetic checks", "",
        f"{len(metric_checks)} model/cohort metric vectors ({len(metric_checks)*6} scalar AP/AUROC/Brier/log-loss checks) "
        f"and {len(interval_checks)} independently implemented paired task-bootstrap intervals agree within 1e-10. "
        "See INDEPENDENT_VERIFICATION.json. No raw payload scan, model inference or training is performed by this analysis script.", "",
        "## Reproducibility and handoff", "",
        "CONTROL_REQUEST.json retains the exact researcher authorization; STOP_RECEIPT.json records the intentional boundary stop. "
        "FINAL_STATUS.json records analysis exit status and the hard three-hour post-fit limit. before_stop/, after_training_stop/ "
        "and final_evidence/ preserve report/metric snapshots. The next-fit placeholder contains only FIT.lock; it is not a trained fit. "
        "Do not restart the original training lane without a new explicit instruction.", ""]
    (folder/"RESULT_ANALYSIS.md").write_text("\n".join(lines))
    # A compact table requested by the researcher; exact source paths preserve chronology.
    comparison = ["# REASSEMBLE and VIFAILBACK training coverage", "",
        "The approximately 47-day VIFAILBACK constraint is an INFERRED additional-runtime planning allowance, not measured elapsed time.", "",
        table(["Dataset / study","Training completed","Limited or unexecuted scope"],[
            ["REASSEMBLE core","Frozen CNN feature/head, statistical sensor and PatchTST baselines; fusion and controlled robustness studies closed",
             "Audio and physical-object modelling excluded by feasibility gates; retained extension Task1 discontinued"],
            ["REASSEMBLE later full CNN","25 full-CNN fits ×20 epochs, seed42, five outer folds and their inner fits; separate frozen/full100-epoch comparison",
             "50 fits deferred under the researcher-approved25-fit cap; complete three-seed full-CNN stability not established"],
            ["VIFAILBACK frozen/donor20","36 FROZEN20 and 36 DONOR20 fits; frozen donor CNN plus newly fitted target heads; existing sensor fits reused",
             "These completed arms do not establish benefit from target-domain CNN fine-tuning"],
            ["VIFAILBACK 100-epoch pilot","One FROZEN100, one FULL100 and one DONOR100 fit, seed42, predefined fold0 pilot",
             "Single-split/single-seed exploratory evidence; frozen/donor CNNs are not target-domain CNN fine-tuning"],
            ["VIFAILBACK FULL20",f"{len(full_completed)} completed fits; current fit finishes before stop" if phase!="final" else f"{len(full_completed)} completed fits, seed42 outer0 roles",
             "Remaining 32 fits not run after current completion; full three-fold/three-seed FULL20 comparison and full fusion coverage unachieved. Constraint: approximately 47 additional GPU days on the current T4."]]), "",
        "REASSEMBLE entries are REPORTED by the retained dated closure/stop records, not a new reproduction or checkpoint audit. "
        "VIFAILBACK counts are VERIFIED within the inspected saved completion-record scope. "
        "Sources: REASSEMBLE core closure in implementations/REASSEMBLE/results/artifacts/reports/REASSEMBLE_COMPLETION_STATUS.md; "
        "25-fit stop receipt in 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/"
        "02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json; separate 100-epoch report in implementations/REASSEMBLE/experiments/"
        "cnn_seed_stability/backbone_comparison/reports/PHASE1_100EPOCH_COMPARISON_REPORT.md; VIFAILBACK FIT_COVERAGE.json, "
        "per-fit histories/receipts and CURRENT_RESULTS.json. Earlier review validation statements remain attributed to those records.", ""]
    (folder/"TRAINING_COMPARISON.md").write_text("\n".join(comparison))
    if phase == "final":
        banner = ("> **RESEARCHER-STOPPED SCOPE:** No further CNN training is authorized. "
                  "The remaining planned fits are NOT RUN — RESEARCHER STOP. Any queued/pending counts below describe "
                  "the preserved original protocol, not an active execution queue. "
                  "See ../18_fit_stop_and_analysis_20261124T1955Z/completed_scope_analysis/RESULT_ANALYSIS.md.\n\n")
        for path in (STUDY/"14_final_research_reports").glob("*.md"):
            text = path.read_text()
            if not text.startswith("> **RESEARCHER-STOPPED SCOPE:"):
                path.write_text(banner+text)
        for row in fits:
            if not row["complete"]:
                row["status"] = "NOT RUN — RESEARCHER STOP" if not row["executed_epochs"] else "PARTIAL — RESEARCHER STOP"
                row["stop_authority"] = str((HERE/"CONTROL_REQUEST.json").relative_to(REPO))
        write_json(STUDY/"11_metrics_and_statistics/FIT_COVERAGE.json",fits)
        status = ["# VIFAILBACK matched CNN study — researcher-stopped scope", "",
            f"{len(completed)} completed fits; {len(incomplete)} remaining original-plan fits are not queued and will not run.", "",
            ("The current FULL20 fit completed its 20 epochs and postfit predictions. " if target_complete else
             "The controller exited before the current FULL20 fit completed; its incomplete evidence is retained. ") + "The original 111-fit protocol "
            "is incomplete; the researcher requested no further CNN training and a maximum three-hour post-fit analysis window.", "",
            table(["Condition","Original planned","Complete","Not run / partial"],count_rows), "",
            "- [Completed-scope results](18_fit_stop_and_analysis_20261124T1955Z/completed_scope_analysis/RESULT_ANALYSIS.md)",
            "- [REASSEMBLE/VIFAILBACK training table](18_fit_stop_and_analysis_20261124T1955Z/completed_scope_analysis/TRAINING_COMPARISON.md)",
            "- [Stop receipt](18_fit_stop_and_analysis_20261124T1955Z/STOP_RECEIPT.json)",
            "- [Analysis/deadline status](18_fit_stop_and_analysis_20261124T1955Z/FINAL_STATUS.json)", "",
            "Do not resume training without a new explicit researcher instruction. Unexecuted work is not a negative scientific result.", ""]
        (STUDY/"VIFAILBACK_MATCHED_CNN_STUDY_STATUS.md").write_text("\n".join(status))
        amended = list((STUDY/"14_final_research_reports").glob("*.md")) + [
            STUDY/"VIFAILBACK_MATCHED_CNN_STUDY_STATUS.md", STUDY/"11_metrics_and_statistics/FIT_COVERAGE.json"]
        write_json(folder/"REPORT_AMENDMENT_PROVENANCE.json", {
            "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "reason": "Explicit researcher stop; preserve original planned coverage while closing execution queue",
            "source_sha256": digest(Path(__file__)), "control_request_sha256": digest(HERE/"CONTROL_REQUEST.json"),
            "original_generator_provenance": "13_reproducibility/REPORT_PROVENANCE.json",
            "preserved_snapshots": ["before_stop", "after_training_stop"],
            "amended_files": [{"path": str(path.relative_to(STUDY)), "sha256": digest(path)} for path in amended]})
    print(json.dumps({k:summary[k] for k in ["phase","completed_fits","unfinished_fits","FULL20_completed_fits","metric_vector_checks","scalar_metric_checks","independent_paired_interval_checks"]}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument("--phase",choices=["initial","final"],default="final")
    analyze(parser.parse_args().phase)
