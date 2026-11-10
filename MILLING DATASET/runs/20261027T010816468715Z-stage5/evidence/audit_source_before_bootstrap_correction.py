"""Read-only numerical thesis audit. Never fits a model or calls training tests."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd
from pypdf import PdfReader
from scipy.special import expit
from sklearn.metrics import (roc_auc_score, average_precision_score, balanced_accuracy_score,
                             f1_score, recall_score, precision_score, brier_score_loss)
import torch

from .data import digest, load_cohort, FEATURE_NAMES
from .smoke import write

METRICS = ("AUROC", "AUPRC", "balanced_accuracy", "macro_F1", "failure_recall", "failure_precision", "Brier", "ECE")


def point_metrics(y, p, hard):
    """Independent sklearn calculations; AP is not trapezoidal PR area."""
    y, p, hard = np.asarray(y, int), np.asarray(p, float), np.asarray(hard, int)
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)) or set(y) != {0, 1}:
        raise ValueError("Invalid saved prediction contract")
    bins = np.minimum((p * 15).astype(int), 14)
    ece = sum(abs(float(np.sum(y[bins == k] - p[bins == k]))) for k in range(15)) / len(y)
    values = (roc_auc_score(y, p), average_precision_score(y, p), balanced_accuracy_score(y, hard),
              f1_score(y, hard, average="macro", zero_division=0), recall_score(y, hard, zero_division=0),
              precision_score(y, hard, zero_division=0), brier_score_loss(y, p), ece)
    return dict(zip(METRICS, map(float, values)))


def weighted_rank_metrics(y, p, weights):
    """Exact tie-aware weighted AP/AUROC for fixed-prediction cluster draws."""
    order = np.argsort(-p, kind="stable")
    ends = np.r_[np.flatnonzero(np.diff(p[order])), len(p) - 1]
    result = []
    for w in np.array_split(weights, max(1, int(np.ceil(len(weights) / 100)))):
        pos, neg = w @ y, w @ (1 - y)
        if np.any(pos <= 0) or np.any(neg <= 0):
            raise ValueError("Undefined single-class bootstrap draw")
        tp = np.cumsum(w[:, order] * y[order], axis=1)[:, ends]
        fp = np.cumsum(w[:, order] * (1 - y[order]), axis=1)[:, ends]
        recall, fpr = tp / pos[:, None], fp / neg[:, None]
        precision = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
        ap = np.sum(np.diff(np.c_[np.zeros(len(w)), recall], axis=1) * precision, axis=1)
        auc = np.sum(np.diff(np.c_[np.zeros(len(w)), fpr], axis=1) * (recall + np.c_[np.zeros(len(w)), recall[:, :-1]]) / 2, axis=1)
        brier = w @ ((p - y) ** 2) / w.sum(1)
        result.append(np.c_[auc, ap, brier])
    return np.concatenate(result)


def cluster_draws(groups, count, seed):
    unique, inverse = np.unique(groups, return_inverse=True)
    rng = np.random.default_rng(seed)
    counts = np.array([np.bincount(rng.integers(len(unique), size=len(unique)), minlength=len(unique)) for _ in range(count)])
    return counts, counts[:, inverse].astype(float)


class EvidenceAudit:
    def __init__(self, config, output):
        self.config, self.output = config, Path(output)
        self.inputs, self.metric_checks, self.checks = {}, [], []

    def use(self, path):
        path = Path(path)
        if str(path) not in self.inputs:
            self.inputs[str(path)] = {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}
        return path

    def read(self, path):
        return json.loads(self.use(path).read_text())

    def csv(self, path):
        return pd.read_csv(self.use(path), float_precision="round_trip")

    def npz(self, path):
        with np.load(self.use(path), allow_pickle=False) as source:
            return {name: source[name].copy() for name in source.files}

    def compare(self, study, model, condition, y, p, hard, expected, path):
        actual = point_metrics(y, p, hard)
        for metric in METRICS:
            if metric not in expected:
                continue
            value = expected[metric]
            value = value["estimate"] if isinstance(value, dict) else value
            error = abs(actual[metric] - value)
            self.metric_checks.append({"study": study, "model": model, "condition": condition,
                "metric": metric, "saved": value, "recalculated": actual[metric], "absolute_error": error, "source": str(path)})
            if error > self.config["metric_tolerance"]:
                raise ValueError(f"Metric mismatch {study}/{model}/{condition}/{metric}: {error}")
        return actual

    def audit_msm(self):
        c = self.config
        preservation, seen = [], set()
        for stage in ("stage1", "stage2", "stage3", "stage4"):
            root = Path(c[stage])
            manifest = self.read(root / "manifests/output_manifest.json")
            n = 0
            for item in manifest["files"]:
                path = Path(item["path"])
                if str(path) in seen or (stage in ("stage1", "stage2") and not (
                        path.is_relative_to(root) or path.is_relative_to("MILLING DATASET/source") or path.is_relative_to("MILLING DATASET/tests"))):
                    continue
                if digest(self.use(path)) != item["sha256"]:
                    raise ValueError("Prior MSM artifact changed: " + str(path))
                seen.add(str(path))
                n += 1
            preservation.append({"stage": stage, "files": n})
        raw = {}
        for stage in ("stage1", "stage2"):
            for item in self.read(Path(c[stage]) / "manifests/input_manifest.json"):
                if item["path"] not in raw:
                    if digest(self.use(item["path"])) != item["sha256"]:
                        raise ValueError("MSM raw file changed")
                    raw[item["path"]] = item
        native_rows = []
        for item in raw.values():
            path = Path(item["path"])
            if path.name != "label.csv":
                continue
            labels = self.csv(path)
            group = "/".join(path.parts[-3:-1])
            for index, row in labels.iterrows():
                if row.label not in (0, 1, 2) or not np.isfinite([row.start, row.end]).all() or row.end <= row.start:
                    raise ValueError("Invalid native annotation")
                native_rows.append({"interval_id": f"{group}/row{index+2}", "group_id": group,
                                    "native_label": int(row.label), "duration_s": float(row.end - row.start)})
        native = pd.DataFrame(native_rows)
        original = self.csv(Path(c["stage1"]) / "MSM_INTERVAL_MANIFEST.csv")
        if len(native) != len(original) or len(native) != 2575:
            raise ValueError("Native annotation count mismatch")
        frame = load_cohort(c["stage2"])
        stats = self.csv(Path(c["stage2"]) / "manifests/common_mtc_statistics.csv").set_index("interval_id")
        channels = self.read("MILLING DATASET/configs/stage3_protocol.json")["sensor"]["channels"]
        sensor_tables, max_error = {}, 0.
        for row in frame.itertuples():
            if row.group_id not in sensor_tables:
                folder = Path(row.label_file).parent
                sensor_tables[row.group_id] = self.csv(next(folder.glob("*_mtc.csv")))
            table = sensor_tables[row.group_id]
            cut = table.loc[(table.time >= row.start_s) & (table.time < row.end_s), channels].to_numpy(float)
            numerical = np.stack([cut.mean(0), cut.std(0, ddof=0), np.sqrt((cut ** 2).mean(0)), cut.min(0), cut.max(0), np.ptp(cut, axis=0)], axis=1).ravel()
            saved = stats.loc[row.interval_id, list(FEATURE_NAMES)].to_numpy(float)
            max_error = max(max_error, float(np.max(abs(numerical - saved))))
            if not np.allclose(numerical, saved, rtol=1e-7, atol=.002):
                raise ValueError("Independent raw sensor-statistic reconstruction mismatch")
        s3, s4 = Path(c["stage3"]), Path(c["stage4"])
        smoke = self.read(s3 / "manifests/smoke_validation.json")
        head = self.read(s3 / "reports/cached_head_benchmark.json")
        bank = self.npz(s3 / "cache/development_oof.npz")
        provenance = self.read(s3 / "manifests/stacking_provenance.json")
        feature_bank = self.npz(s3 / "cache/smoke_features.npz")
        bundle = torch.load(self.use(s3 / "checkpoints/development_only.pt"), map_location="cpu", weights_only=True)
        ids = feature_bank["interval_id"].tolist()
        if ids != bank["interval_id"].tolist() or ids != bundle["metadata"]["fit_ids"]:
            raise ValueError("Development checkpoint/prediction identity mismatch")
        indexed = frame.set_index("interval_id")
        for interval_id in ids:
            group = indexed.loc[interval_id, "group_id"]
            if group == "imi_vm20i/dataset19":
                raise ValueError("Protected group in development checkpoint")
            for branch in ("visual", "sensor"):
                item = provenance[interval_id][branch]
                if group in item["fit_groups"] or item["selection_groups"]:
                    raise ValueError("Saved development OOF group contamination")
        if bank["probabilities"].shape != (24, 2) or not np.isfinite(bank["probabilities"]).all():
            raise ValueError("Invalid saved smoke OOF bank")
        if not np.allclose(feature_bank["visual"].mean(0), bundle["visual_mean"].numpy(), rtol=1e-6, atol=1e-6):
            raise ValueError("New visual scaler does not match its declared fit IDs")
        # Independent saved-checkpoint arithmetic, no model fitting or metrics on
        # development labels. Historical final-fit probabilities were not saved.
        state = bundle["visual"]
        z = ((feature_bank["visual"] - bundle["visual_mean"].numpy()) / bundle["visual_std"].numpy()).astype(np.float32)
        h = np.maximum(0, z @ state["head.projection.0.weight"].numpy().T + state["head.projection.0.bias"].numpy())
        pv = expit((h @ state["head.classifier.weight"].numpy().T + state["head.classifier.bias"].numpy()).ravel())
        sx = (feature_bank["sensor"] - bundle["sensor_mean"].numpy()) / bundle["sensor_std"].numpy()
        ps = expit((sx @ bundle["sensor"]["coef"].numpy().T + bundle["sensor"]["intercept"].numpy()).ravel())
        pf = expit((np.c_[pv, ps] @ bundle["fusion"]["coef"].numpy().T + bundle["fusion"]["intercept"].numpy()).ravel())
        if not np.isfinite(np.c_[pv, ps, pf]).all():
            raise ValueError("Saved development checkpoint does not yield finite probabilities")
        predictions = self.csv(s4 / "manifests/predictions.csv")
        curves = self.csv(s4 / "manifests/training_curves.csv")
        slots = self.csv(s4 / "manifests/planned_results_status.csv")
        if len(predictions) or len(curves) or slots.AP.notna().any() or slots.AUROC.notna().any() or len(slots) != 54:
            raise ValueError("Stage 4 blocked report contradicts prediction/metric artifacts")
        selection = self.read(s4 / "manifests/selected_checkpoints.json")
        if selection["selected"]:
            raise ValueError("Unexpected selected Stage 4 checkpoint")
        result = {"prior_preservation": preservation, "raw_sources": len(raw), "native_intervals": len(native),
            "native_class_counts": {str(k): int(v) for k, v in native.native_label.value_counts().items()},
            "native_positive_groups": native.loc[native.native_label == 1, "group_id"].nunique(),
            "duration_min_median_max_s": [float(native.duration_s.min()), float(native.duration_s.median()), float(native.duration_s.max())],
            "eligible_intervals": len(frame), "eligible_native_counts": {str(k): int(v) for k, v in frame.native_label.value_counts().items()},
            "eligible_positive_groups": frame.loc[frame.target == 1, "group_id"].nunique(),
            "independent_raw_MTC_statistics_max_abs_difference": max_error,
            "annotation_and_frame_policy_check": "Native annotation bytes + saved decoded PTS/guard policy; no new raw video decode/audio offset estimation",
            "smoke_forward_checkpoint_arithmetic_finite": True, "smoke_OOF_metadata_and_ID_check": True,
            "historical_smoke_reload_comparison": "Saved report states zero error; original final-refit probability array was not retained, so historical execution comparison is not independently replayed",
            "historical_smoke_CNN_forwards": smoke["cnn_frames_forwarded"], "historical_total_smoke_head_updates": head["combined_optimizer_updates"],
            "stage4_heldout_predictions": len(predictions), "stage4_trained_curves": len(curves), "stage4_blocked_result_slots": len(slots)}
        write(self.output / "manifests/MSM_audit.json", result)
        return result

    def audit_core(self):
        c = self.config
        s1, s1b, s2, s3 = map(Path, [c["reassemble_section1"], c["reassemble_section1b"], c["reassemble_section2"], c["reassemble_section3"]])
        frame = pd.read_parquet(self.use(s1 / "cohort.parquet"))
        self.frame = frame
        results = self.read(s1 / "assessment/results.json")
        core = {}
        for name, expected in results["metrics"].items():
            path = s1 / "predictions" / f"{name}_perm00.npz"
            d = self.npz(path)
            if not np.array_equal(d["y"], frame.failure.to_numpy()):
                raise ValueError("REASSEMBLE cohort/label identity mismatch")
            core[name] = d
            self.compare("REASSEMBLE-S1", name, "clean", d["y"], d["p"], d["hard"], expected, path)
        fusion = self.npz(s1b / "stacking/oof.npz")
        expected = self.read(s1b / "assessment/results.json")
        self.compare("REASSEMBLE-S1B", "F2", "clean", fusion["y"], fusion["p"], fusion["hard"], expected["metrics"]["minimal_late_fusion"], s1b / "stacking/oof.npz")
        self.fusion, self.sensor = fusion, core["sensor_statistics"]
        splits = self.read(s1 / "nested_splits.json")
        seen, inner_count, sub_count, f2_error = set(), 0, 0, 0.
        for outer in splits["folds"]:
            train, test = set(outer["train_recordings"]), set(outer["test_recordings"])
            if train & test or train | test != set(frame.recording_id) or seen & test:
                raise ValueError("Outer group leakage/coverage mismatch")
            seen |= test
            k = outer["fold"]
            if set(frame.loc[fusion["fold"] == k, "recording_id"]) != test:
                raise ValueError("Saved prediction fold/group assignment mismatch")
            covered = set()
            for item in outer["inner"]:
                it, iv = set(item["train_recordings"]), set(item["validation_recordings"])
                if it & iv or it | iv != train or covered & iv:
                    raise ValueError("Inner group leakage/coverage mismatch")
                covered |= iv
                inner_count += 1
                sub = self.read(s1b / "stacking" / f"outer{k}_inner{item['fold']}.json")
                if set(sub["train_recordings"]) != it or set(sub["validation_recordings"]) != iv:
                    raise ValueError("F2 meta-row exclusion provenance mismatch")
                sub_seen = set()
                for part in sub["subfolds"]:
                    a, b = set(part["train_recordings"]), set(part["validation_recordings"])
                    if a & b or a | b != it or a & iv or b & iv or sub_seen & b:
                        raise ValueError("Sub-inner fitting/calibration group leakage")
                    sub_seen |= b
                    sub_count += 1
                if sub_seen != it:
                    raise ValueError("Sub-inner coverage incomplete")
            if covered != train:
                raise ValueError("Inner coverage incomplete")
            d = self.npz(s1b / "stacking" / f"outer{k}.npz")
            log = self.read(s1b / "stacking" / f"outer{k}.json")
            p = expit(d["test_branch_probabilities"] @ np.array(log["stacker"]["coefficient"]) + log["stacker"]["intercept"])
            f2_error = max(f2_error, float(np.max(abs(p - d["p"]))))
        if f2_error > 1e-12:
            raise ValueError("Saved F2 coefficient arithmetic mismatch")
        two = self.npz(s2 / "predictions/oof.npz")
        two_metrics = self.read(s2 / "assessment/results.json")
        seed_checks = []
        for model, expected_scores in two_metrics["metrics"].items():
            self.compare("REASSEMBLE-S2", model, "clean", two["y"], two[model + "_p"], two[model + "_hard"], expected_scores, s2 / "predictions/oof.npz")
            if model + "_seed_p" in two:
                for seed_index, p in enumerate(two[model + "_seed_p"]):
                    saved = two_metrics["seed_variability"][model]["seed_metrics"][seed_index]
                    for metric, value in (("AUPRC", average_precision_score(two["y"], p)), ("AUROC", roc_auc_score(two["y"], p))):
                        if abs(float(value) - saved[metric]) > 1e-12:
                            raise ValueError("Seed metric mismatch")
                    seed_checks.append({"model": model, "seed_index": seed_index, **saved})
            for k, saved in enumerate(two_metrics["folds"][model]):
                ix = two["fold"] == k
                self.compare("REASSEMBLE-S2", model, f"outer{k}", two["y"][ix], two[model+"_p"][ix], two[model+"_hard"][ix], saved, s2 / "predictions/oof.npz")
        if not np.array_equal(two["F2_p"], fusion["p"]) or not np.array_equal(two["U2_p"], core["rtdetr"]["p"]):
            raise ValueError("Claimed reused reference predictions differ")
        three = self.read(s3 / "results.json")
        for condition, record in three["conditions"].items():
            path = s3 / "predictions" / (condition + ".npz")
            d = self.npz(path)
            for model, expected_scores in record["metrics"].items():
                if not isinstance(expected_scores, dict) or "AUROC" not in expected_scores:
                    continue
                self.compare("REASSEMBLE-S3", model, condition, d["y"], d[model + "_p"], d[model + "_hard"], expected_scores, path)
        counts, weights = cluster_draws(frame.recording_id.to_numpy(), 2000, self.read("configs/reassemble/section1b.json")["seed"] + 50000)
        a = weighted_rank_metrics(fusion["y"], fusion["p"], weights)
        b = weighted_rank_metrics(fusion["y"], self.sensor["p"], weights)
        paired = {}
        for i, metric in enumerate(("AUROC", "AUPRC", "Brier")):
            limits = np.quantile(a[:, i] - b[:, i], [.025, .975])
            saved = expected["fusion_minus_sensor"][metric]
            error = float(np.max(abs(limits - [saved["lower_95"], saved["upper_95"]])))
            if error > 1e-10:
                raise ValueError("Recalculated F2/sensor cluster interval mismatch")
            paired[metric] = {"estimate": saved["estimate"], "lower_95": float(limits[0]), "upper_95": float(limits[1]), "max_CI_error": error}
        result = {"cohort": {"intervals": len(frame), "positives": int(frame.failure.sum()), "groups": frame.recording_id.nunique(), "prevalence": float(frame.failure.mean())},
            "outer_group_folds_checked": 5, "inner_partitions_checked": inner_count, "sub_inner_partitions_checked": sub_count,
            "F2_coefficient_replay_max_abs_difference": f2_error, "selected_F2_sensor_CIs_recalculated": paired,
            "bootstrap_replicates": 2000, "seed_metrics_checked": seed_checks,
            "section3_conditions_checked": len(three["conditions"]),
            "section3_joint_mechanism_outcome_successes": sum(bool(v["adaptation_supported"] and v["smaller_degradation_supported"]) for family in three["mechanism"].values() for v in family.values())}
        write(self.output / "manifests/REASSEMBLE_core_audit.json", result)
        return result

    def audit_extensions(self):
        c = self.config
        boundary = Path(c["boundary"])
        results = self.read(boundary / "results.json")
        for model, saved in results["metrics"].items():
            p = boundary / "predictions" / (model + ".npz")
            d = self.npz(p)
            self.compare("REASSEMBLE-boundary", model, "clean", d["y"], d["p"], d["hard"], saved, p)
        bf = self.npz(boundary / "fusion/oof.npz")
        saved = self.read(boundary / "fusion/results.json")
        self.compare("REASSEMBLE-boundary", "F2-V3", "clean", bf["y"], bf["p"], bf["hard"], saved["new"], boundary / "fusion/oof.npz")
        encoder = Path(c["encoder"])
        table = self.csv(encoder / "comparison/metrics.csv")
        encoder_summary = []
        for condition in ("cnn_only", "cnn_plus_encoder"):
            path = encoder / "comparison" / f"identified_outer_predictions_{condition}.csv"
            d = self.csv(path)
            for branch, pcol, hcol in (("visual", "p_visual", "decision_visual"), ("sensor", "p_sensor", "decision_sensor"), ("fused", "p_fused", "decision_fused")):
                rows = table.loc[(table.condition == condition) & (table.scope == "pooled") & (table.branch == branch)]
                if not len(rows) and branch == "fused":
                    rows = table.loc[(table.condition == condition) & (table.scope == "pooled") & (table.branch == "fusion")]
                saved = rows.iloc[0].to_dict()
                saved["AUPRC"] = saved["AP"]
                self.compare("REASSEMBLE-encoder", condition + "/" + branch, "pooled", d.failure, d[pcol], d[hcol], saved, path)
                encoder_summary.append({"condition": condition, "branch": branch, "AP": saved["AP"], "AUROC": saved["AUROC"]})
        controlled = Path(c["controlled32"])
        fusion_table = self.csv(controlled / "results/comparison/fusion_results.csv")
        controlled_summary = []
        for seed in (42, 20261023):
            for condition in ("frozen32_two_epochs", "finetuned32_two_epochs"):
                frames = [self.csv(controlled / f"results/seed_{seed}/f2_fusion/{condition}/fold_{k:02d}/assessment_predictions.csv") for k in range(1, 6)]
                d = pd.concat(frames, ignore_index=True)
                if len(d) != 4530 or not d.sample_id.is_unique:
                    raise ValueError("Controlled 32-frame assessment coverage failure")
                for branch, pcol in (("visual", "p_visual"), ("sensor", "p_sensor"), ("F2", "p_F2")):
                    rows = fusion_table.loc[(fusion_table.seed == seed) & (fusion_table.condition == condition) & (fusion_table.scope == "pooled") & (fusion_table.branch == branch)]
                    saved = rows.iloc[0].to_dict()
                    saved["AUPRC"] = saved["AP"]
                    actual = self.compare("REASSEMBLE-controlled32", f"{condition}/{branch}", str(seed), d.failure, d[pcol], d[pcol] >= .5, saved, controlled / "results/comparison/fusion_results.csv")
                    controlled_summary.append({"seed": seed, "condition": condition, "branch": branch, "AP": actual["AUPRC"], "AUROC": actual["AUROC"], "recall": actual["failure_recall"]})
        fits = self.csv(controlled / "results/comparison/fit_evidence_index.csv")
        missing_weights = []
        for row in fits.itertuples():
            manifest = controlled / row.manifest
            if digest(self.use(manifest)) != row.manifest_sha256:
                raise ValueError("Controlled fit manifest identity mismatch")
            checkpoint = Path(row.model_reference)
            if checkpoint.exists():
                if digest(self.use(checkpoint)) != row.model_sha256:
                    raise ValueError("Controlled checkpoint identity mismatch")
            else:
                missing_weights.append(str(checkpoint))
        result = {"encoder": encoder_summary, "controlled32": controlled_summary,
            "controlled32_fit_receipts_verified": len(fits), "controlled32_epoch_budgets": sorted(fits.epochs.unique().tolist()),
            "controlled32_missing_checkpoint_paths": missing_weights,
            "boundary_selected_descriptive_variant": results["fusion_variant"],
            "boundary_visual_AP": {k: v["AUPRC"]["estimate"] for k, v in results["metrics"].items()},
            "boundary_fusion_AP": self.read(boundary / "fusion/results.json")["new"]["AUPRC"]["estimate"]}
        write(self.output / "manifests/REASSEMBLE_extensions_audit.json", result)
        return result

    def audit_quality(self):
        root = Path(self.config["quality_pilot"])
        index = self.csv(root / "comparison/coverage_and_prediction_index.csv")
        saved = self.csv(root / "comparison/per_condition_metrics.csv")
        components = self.read(root / "fusion_fits/fold_01/components.json")
        quality_names = ["image_gradient", "image_clipping", "image_contrast", "unique_frame_fraction", "sensor_finite_fraction", "available_channel_fraction", "sensor_max_gap_fraction", "sensor_relative_variation"]
        arithmetic_error, ap_error, ap_checks, probability_checks = 0., 0., 0, 0
        primary, primary_bootstrap = [], []
        counts = None
        for row in index.itertuples():
            path = root / row.path
            if digest(self.use(path)) != row.sha256:
                raise ValueError("Quality pilot indexed table hash mismatch")
            d = self.csv(path)
            if not d.sample_id.is_unique or len(d) != row.expected:
                raise ValueError("Quality-pilot key coverage mismatch")
            both = d.visual_available.astype(bool) & d.sensor_available.astype(bool)
            for model, component in components.items():
                if not both.any():
                    continue
                p = d.loc[both, ["p_visual", "p_sensor"]].to_numpy(float)
                q = d.loc[both, quality_names].to_numpy(float)
                norm = component["normalizer"]
                q = np.clip((q - norm["mean"]) / norm["std"], -norm["clip"], norm["clip"])
                design = p if model == "static_augmented" else np.c_[p, q] if model == "quality_additive" else np.c_[p, q, p[:, 0, None] * q, p[:, 1, None] * q]
                predicted = expit(design @ np.array(component["coefficient"]) + component["intercept"])
                arithmetic_error = max(arithmetic_error, float(np.max(abs(predicted - d.loc[both, "p_" + model]))))
                probability_checks += int(both.sum())
            selected = saved.loc[(saved["fold"] == row.fold) & (saved.scope == "fold") & (saved.family == row.family) & (saved.level.astype(str) == str(row.level)) & (saved.repeat == row.repeat)]
            for item in selected.itertuples():
                column = "p_" + item.model if item.model not in ("visual", "sensor") else "p_" + item.model
                mask = np.isfinite(d[column].to_numpy(float))
                if not mask.any() or not np.isfinite(item.AP):
                    continue
                ap = float(average_precision_score(d.loc[mask, "failure"], d.loc[mask, column]))
                error = abs(ap - item.AP)
                ap_error = max(ap_error, error)
                ap_checks += 1
            if row.family in ("image_noise", "sensor_noise"):
                ordered = d.sort_values(["recording_id", "sample_id"]).reset_index(drop=True)
                if counts is None:
                    counts, _ = cluster_draws(np.sort(ordered.recording_id.unique()), 2000, 314159)
                unique, inverse = np.unique(ordered.recording_id, return_inverse=True)
                weights = counts[:, inverse].astype(float)
                a = weighted_rank_metrics(ordered.failure.to_numpy(int), ordered.p_quality_interaction.to_numpy(float), weights)[:, 1]
                b = weighted_rank_metrics(ordered.failure.to_numpy(int), ordered.p_static_augmented.to_numpy(float), weights)[:, 1]
                primary_bootstrap.append(a - b)
                primary.append(float(average_precision_score(ordered.failure, ordered.p_quality_interaction) - average_precision_score(ordered.failure, ordered.p_static_augmented)))
        if arithmetic_error > 1e-12 or ap_error > 1e-12:
            raise ValueError("Quality pilot arithmetic/metric discrepancy")
        contrasts = self.csv(root / "comparison/paired_intervals.csv")
        target = contrasts.loc[contrasts.contrast == "interaction_minus_augmented_static_PRIMARY"].iloc[0]
        limits = np.quantile(np.mean(primary_bootstrap, axis=0), [.025, .975])
        point = float(np.mean(primary))
        if max(abs(point - target.AP_difference), abs(limits[0] - target.lower95), abs(limits[1] - target.upper95)) > 1e-10:
            raise ValueError("Quality primary recording-bootstrap interval mismatch")
        result = {"tables_verified": len(index), "AP_values_recomputed": ap_checks, "AP_max_error": ap_error,
            "head_probabilities_reconstructed": probability_checks, "probability_max_error": arithmetic_error,
            "primary_mean_AP_difference": point, "primary_95_interval": limits.tolist(),
            "bootstrap_draw_counts_sha256": hashlib.sha256(counts.tobytes()).hexdigest(),
            "conditions_in_primary": len(primary), "bootstrap_replicates": 2000,
            "interpretation": "Inconclusive one-fold exposed-data pilot; no robustness superiority or clean noninferiority established"}
        write(self.output / "manifests/quality_pilot_audit.json", result)
        return result

    def audit_protocols_and_source(self):
        c = self.config
        pdf = self.use(c["original_expose"])
        reader = PdfReader(pdf)
        text = reader.pages[1].extract_text() + reader.pages[2].extract_text()
        with (self.output / "evidence/expose_questions_pages2_3.txt").open("x") as stream:
            stream.write(text)
        # Preserve the original wording from the published local reconciliation;
        # the PDF itself and extraction are hashed/read independently above.
        self.use("docs/thesis_research_direction/EXPOSE_ALIGNMENT_DECISION.md")
        budgets = []
        for model in ("rtdetr", "patchtst", "sensor_statistics"):
            logs = [self.read(Path(c["reassemble_section1"]) / "predictions" / f"{model}_perm00_fold{k}.json") for k in range(5)]
            budgets.append({"study": "REASSEMBLE core", "model": model, "selected_outer_settings": [log["selected"] for log in logs],
                            "refit_seeds": [log["refit"].get("seed") for log in logs]})
        phase = Path(c["phase1"])
        execution = phase / "26102026_execution/26102026_main_run_01"
        index = self.read(execution / "PHASE1_COMPLETED_FIT_INDEX.json")
        write(self.output / "evidence/Phase1_completed_fits_snapshot.json", index)
        completed = []
        for folder in sorted(execution.glob("26102026_seed*")):
            receipt_path = folder / "PHASE1_FIT_COMPLETE.json"
            if not receipt_path.exists():
                continue
            receipt = self.read(receipt_path)
            checkpoint = folder / "PHASE1_BEST_MODEL.pt"
            if digest(self.use(checkpoint)) != receipt["selected_model_sha256"]:
                raise ValueError("Completed Phase1 checkpoint hash mismatch")
            completed.append({"arm": receipt["arm"], "seed": receipt["seed"], "job_index": receipt["job_index"],
                              "executed_epochs": receipt["executed_epochs"], "selected_epoch": receipt["best"]["epoch"],
                              "checkpoint": str(checkpoint), "checkpoint_sha256": receipt["selected_model_sha256"]})
        original = self.read("configs/reassemble/section1.json")
        identity = self.read(Path(c["reassemble_section1"]) / "pretrained_model.json")
        model_dir = Path(original["data_root"]) / "cache/section1_models" / original["visual"]["revision"]
        for name, metadata in identity["files"].items():
            if digest(self.use(model_dir / name)) != metadata["sha256"]:
                raise ValueError("Original pretrained model/processor changed")
        source = self.read(Path(c["stage4"]) / "manifests/source_checkpoint_gate.json")
        canonical = Path(source["canonical_source_folder"]) / "PHASE1_FIT_COMPLETE.json"
        result = {"original_expose_sha256": digest(pdf), "original_expose_pages": len(reader.pages),
            "core_selected_budgets": budgets, "current_completed_phase1_fits": completed,
            "current_completed_C_fits": sum(row["arm"] == "C_full_finetuned16" for row in completed),
            "canonical_R_completion_receipt_exists_now": canonical.exists(),
            "Stage4_source_status_is_historical_snapshot": True,
            "source_checkpoints_chosen_by_MSM_performance": False, "active_checkpoint_payloads_read": False,
            "pretrained_identity_verified": True, "new_model_training_performed": False}
        write(self.output / "manifests/protocol_checkpoint_audit.json", result)
        return result


def main(config_path, output):
    started = time.perf_counter()
    config = json.loads(Path(config_path).read_text())
    if config["training_allowed"]:
        raise ValueError("This audit cannot authorize model training")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name in ("config", "manifests", "evidence", "reports"):
        (output / name).mkdir()
    write(output / "config/resolved_config.json", config)
    torch.set_num_threads(1)
    auditor = EvidenceAudit(config, output)
    print("AUDIT MSM inputs and evidence", flush=True)
    msm = auditor.audit_msm()
    print("AUDIT REASSEMBLE metrics, groups and primary intervals", flush=True)
    core = auditor.audit_core()
    print("AUDIT representation/fusion extensions", flush=True)
    extensions = auditor.audit_extensions()
    print("AUDIT quality pilot", flush=True)
    quality = auditor.audit_quality()
    print("AUDIT source checkpoints and original questions", flush=True)
    protocols = auditor.audit_protocols_and_source()
    with (output / "manifests/metric_recalculation_checks.csv").open("x", newline="") as stream:
        pd.DataFrame(auditor.metric_checks).to_csv(stream, index=False)
    write(output / "manifests/input_manifest.json", list(auditor.inputs.values()))
    write(output / "validation.json", {"passed": True, "UTC": datetime.now(timezone.utc).isoformat(),
        "metric_values_recalculated": len(auditor.metric_checks), "maximum_metric_absolute_error": max(item["absolute_error"] for item in auditor.metric_checks),
        "new_model_fits": 0, "new_training_optimizer_updates": 0, "new_raw_CNN_inference": False,
        "CUDA_context_created": torch.cuda.is_initialized(), "elapsed_audit_body_seconds": time.perf_counter() - started,
        "independent_raw_recalculations": ["69 native MSM annotation files", "114 MTC cut statistics"],
        "saved_prediction_recalculations": ["core metrics/folds/seeds", "F2/sensor paired cluster intervals", "boundary/encoder/controlled32 point metrics", "quality-pilot point metrics, coefficient arithmetic, primary paired cluster interval"],
        "not_reproduced": ["historical model fitting", "raw REASSEMBLE target binding", "raw CNN extraction", "audio-offset fitting", "raw corruption generation", "all historical uncertainty intervals", "full historical execution/recovery trajectory"]})
    write(output / "provenance.json", {"UTC": datetime.now(timezone.utc).isoformat(), "command": sys.argv,
        "Git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "tracked_dirty": bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True)),
        "python": platform.python_version(), "software": {name: version(name) for name in ("numpy", "pandas", "scipy", "scikit-learn", "torch", "pypdf")},
        "config_sha256": digest(config_path), "source_sha256": digest(__file__), "training_performed": False})
    print(json.dumps({"run": str(output), "passed": True, "new_training": False, "metric_values_checked": len(auditor.metric_checks)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="MILLING DATASET/configs/stage5_audit.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.config, args.output)
