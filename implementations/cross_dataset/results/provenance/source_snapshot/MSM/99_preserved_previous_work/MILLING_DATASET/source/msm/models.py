"""Thin MSM composition around the verified REASSEMBLE CNN/head primitives."""
from pathlib import Path
import json
import numpy as np
import torch
from torch import nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, roc_auc_score, balanced_accuracy_score,
                             f1_score, precision_score, recall_score, brier_score_loss, log_loss,
                             confusion_matrix)
from reassemble.section1_features import load_visual, sha
from reassemble.section1_models import VisualHead, Standardizer


def verified_backbone(config):
    """Reuse local pinned pretrained weights; missing/mismatching files stop."""
    base = json.loads(Path(config["reassemble_config"]).read_text())
    identity = json.loads(Path(config["pretrained_identity"]).read_text())
    if base["visual"]["revision"] != config["visual"]["revision"]:
        raise ValueError("Pinned backbone revision mismatch")
    folder = Path(base["data_root"]) / "cache/section1_models" / config["visual"]["revision"]
    for name, expected in identity["files"].items():
        if not (folder / name).is_file() or sha(folder / name) != expected["sha256"]:
            raise ValueError("Pretrained file missing/changed; no automatic download permitted")
    processor, backbone, actual = load_visual(base)
    if actual["files"] != identity["files"] or actual["backbone_parameters"] != 11190112:
        raise ValueError("Unverified feature extractor")
    if processor.do_normalize or processor.size != {"height": 640, "width": 640}:
        raise ValueError("Unexpected verified image processor")
    return processor, backbone, actual


class MillingVisual(nn.Module):
    """New weights for the milling head; no failure head/checkpoint is loaded."""
    def __init__(self, width=896):
        super().__init__()
        self.head = VisualHead(width, {})

    def forward(self, features):
        if features.ndim != 2 or features.shape[1] != 896:
            raise ValueError("One pooled 896-value vector per cutting interval required")
        return self.head(features)[0]


class IntervalCNN(nn.Module):
    """16-frame contract, frozen CNN, FP32 spatial/temporal mean pooling."""
    def __init__(self, backbone, microbatch=2):
        super().__init__()
        self.backbone = backbone.eval().requires_grad_(False)
        self.microbatch = microbatch

    def train(self, mode=True):
        super().train(mode)
        self.backbone.eval()
        return self

    def forward(self, pixels):
        if pixels.ndim != 5 or tuple(pixels.shape[1:]) != (16, 3, 640, 640):
            raise ValueError("Expected [B,16,3,640,640] aligned interval pixels")
        flat = pixels.flatten(0, 1)
        chunks = []
        with torch.no_grad():
            for part in flat.split(self.microbatch):
                maps = self.backbone(part).feature_maps
                chunks.append(torch.cat([m.float().mean((-2, -1)) for m in maps], dim=1))
        return torch.cat(chunks).reshape(len(pixels), 16, 896).mean(1)


def fit_visual(x, y, config, seed, epochs=None, device="cpu"):
    if set(np.asarray(y)) != {0, 1} or not np.isfinite(x).all():
        raise ValueError("Finite features and both classes required")
    torch.manual_seed(seed)
    scaler = Standardizer().fit(x)
    values = torch.from_numpy(scaler.transform(x)).to(device)
    labels = torch.as_tensor(y, dtype=torch.float32, device=device)
    model = MillingVisual().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["learning_rate"], weight_decay=config["weight_decay"])
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((len(y) - sum(y)) / sum(y)), device=device))
    rng = torch.Generator().manual_seed(seed)
    losses, nonzero = [], False
    for _ in range(config["epochs"] if epochs is None else epochs):
        model.train()
        for order in torch.randperm(len(y), generator=rng).split(config["batch_size"]):
            optimizer.zero_grad(set_to_none=True)
            output = model(values[order.to(device)])
            loss = criterion(output, labels[order.to(device)])
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite loss")
            loss.backward()
            gradients = [p.grad for p in model.parameters()]
            if any(g is None or not torch.isfinite(g).all() for g in gradients):
                raise ValueError("Missing/nonfinite head gradient")
            nonzero |= all(bool(torch.count_nonzero(g)) for g in gradients)
            nn.utils.clip_grad_norm_(model.parameters(), 1.)
            optimizer.step()
            losses.append(float(loss.detach()))
    model.eval()
    return model, scaler, {"updates": len(losses), "finite_losses": bool(np.isfinite(losses).all()),
                           "all_head_parameters_nonzero_gradient": nonzero, "losses": losses}


def predict_visual(model, scaler, x):
    with torch.no_grad():
        return torch.sigmoid(model(torch.from_numpy(scaler.transform(x)).to(next(model.parameters()).device))).cpu().numpy()


class SensorClassifier:
    def __init__(self, C=1.):
        self.scaler = Standardizer()
        self.model = LogisticRegression(C=C, class_weight="balanced", solver="lbfgs", max_iter=2000, random_state=0)

    def fit(self, x, y):
        if x.ndim != 2 or not np.isfinite(x).all() or set(y) != {0, 1}:
            raise ValueError("Finite interval statistics/both classes required")
        self.model.fit(self.scaler.fit(x).transform(x), y)
        if np.any(self.model.n_iter_ >= self.model.max_iter):
            raise ValueError("Sensor logistic regression failed to converge")
        return self

    def predict(self, x):
        if not np.isfinite(x).all():
            raise ValueError("Nonfinite sensor predictors")
        return self.model.predict_proba(self.scaler.transform(x))[:, 1]


class StaticF2:
    """Three freshly fitted parameters; only two cross-fitted probabilities."""
    def fit(self, probabilities, labels, ids, groups, provenance):
        p = np.asarray(probabilities)
        if p.shape != (len(labels), 2) or len(set(ids)) != len(ids) or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
            raise ValueError("Exactly two finite OOF probabilities per unique interval required")
        for interval, group in zip(ids, groups):
            for branch in ("visual", "sensor"):
                entry = provenance[interval][branch]
                fit_groups = set(entry["fit_groups"])
                if group in fit_groups or group in set(entry.get("selection_groups", [])) or not fit_groups:
                    raise ValueError("OOF stacking leakage detected")
        self.model = LogisticRegression(C=1., class_weight=None, solver="lbfgs", max_iter=2000, random_state=0).fit(p, labels)
        self.fit_ids = tuple(ids)
        return self

    def predict(self, probabilities):
        p = np.asarray(probabilities)
        if p.ndim != 2 or p.shape[1] != 2 or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
            raise ValueError("Invalid branch probabilities")
        return self.model.predict_proba(p)[:, 1]


def averaging(probabilities):
    p = np.asarray(probabilities)
    if p.ndim != 2 or p.shape[1] != 2 or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("Invalid branch probabilities")
    return p.mean(1)


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    if y.shape != p.shape or set(y) != {0, 1} or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("Binary interval outcomes/probabilities and both classes required")
    hard = p >= .5
    return {"AP": float(average_precision_score(y, p)), "AUROC": float(roc_auc_score(y, p)),
            "balanced_accuracy": float(balanced_accuracy_score(y, hard)), "F1": float(f1_score(y, hard, zero_division=0)),
            "precision": float(precision_score(y, hard, zero_division=0)), "recall": float(recall_score(y, hard)),
            "Brier": float(brier_score_loss(y, p)), "log_loss": float(log_loss(y, p)),
            "confusion_matrix_tn_fp_fn_tp": confusion_matrix(y, hard, labels=[0, 1]).ravel().tolist(),
            "prevalence": float(y.mean()), "intervals": len(y)}


def save_bundle(path, model, scaler, sensor, fusion, metadata):
    # Tensor/primitives only: safe weights_only reload; no estimator pickle.
    def logistic(estimator):
        return {"coef": torch.tensor(estimator.coef_), "intercept": torch.tensor(estimator.intercept_)}
    torch.save({"visual": model.cpu().state_dict(), "visual_mean": torch.tensor(scaler.mean),
                "visual_std": torch.tensor(scaler.std), "sensor": logistic(sensor.model),
                "sensor_mean": torch.tensor(sensor.scaler.mean), "sensor_std": torch.tensor(sensor.scaler.std),
                "fusion": logistic(fusion.model), "metadata": metadata}, path)


def load_bundle(path):
    saved = torch.load(path, map_location="cpu", weights_only=True)
    model, scaler, sensor, fusion = MillingVisual(), Standardizer(), SensorClassifier(), StaticF2()
    model.load_state_dict(saved["visual"])
    model.eval()
    for normalizer, prefix in ((scaler, "visual"), (sensor.scaler, "sensor")):
        normalizer.mean = saved[prefix + "_mean"].numpy()
        normalizer.std = saved[prefix + "_std"].numpy()
    for estimator, key in ((sensor.model, "sensor"), (fusion, "fusion")):
        if key == "fusion":
            fusion.model = LogisticRegression()
            estimator = fusion.model
        estimator.coef_ = saved[key]["coef"].numpy()
        estimator.intercept_ = saved[key]["intercept"].numpy()
        estimator.classes_ = np.array([0, 1])
        estimator.n_features_in_ = estimator.coef_.shape[1]
    return model, scaler, sensor, fusion, saved["metadata"]
