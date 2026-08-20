#!/usr/bin/env python3
"""Phase 3: from-scratch PatchTST training + evaluation on HF spectral features.

Train EXP-B, select on EXP-A, evaluate once on EXP-F. Constant mean/median
baselines are recomputed here from the same pinned target values, as an
internal consistency check against the cited P4 LF-only numbers. No
pi_multimodal_ad imports anywhere in this file.

`train_and_evaluate()` is written as a reusable function (not just script
logic) so Phase 4's band/channel ablation can call the exact same training
procedure on feature-column subsets, rather than a separate toy probe.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import PatchTSTConfig, PatchTSTRegressor  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FEATURES_DIR = Path(__file__).resolve().parent / "features" / "per_run"
SPLIT_PARQUET = (
    REPO_ROOT
    / "runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/tables/split_manifest.parquet"
)
TARGETS_PARQUET = (
    REPO_ROOT
    / "runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/run_damage_targets.parquet"
)
OUTPUT_DIR = Path(__file__).resolve().parent / "training_output"
TARGET_COLUMN = "raw_top3_mean_pct"
SEED = 20260820


def set_seed(seed: int) -> None:
    import random

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_pinned_split_and_targets() -> pd.DataFrame:
    split = pd.read_parquet(SPLIT_PARQUET)
    run_split = split[["experiment", "run", "split"]].drop_duplicates()
    targets = pd.read_parquet(TARGETS_PARQUET)
    merged = run_split.merge(
        targets[["experiment", "run", TARGET_COLUMN, "inclusion_status"]],
        on=["experiment", "run"],
        how="left",
    )
    missing = merged[merged[TARGET_COLUMN].isna()]
    if not missing.empty:
        raise RuntimeError(f"runs missing a pinned target: {missing.to_dict('records')}")
    return merged.sort_values(["split", "experiment", "run"]).reset_index(drop=True)


def load_run_features(experiment: str, run: int) -> pd.DataFrame | None:
    path = FEATURES_DIR / f"{experiment}_run{run}.parquet"
    if not path.is_file():
        return None
    frame = pd.read_parquet(path)
    if frame.empty:
        return None
    return frame.sort_values("wf_start_time", kind="stable").reset_index(drop=True)


def all_feature_columns(frame: pd.DataFrame) -> list[str]:
    return [
        column
        for column in frame.columns
        if column not in ("experiment", "run", "member_name", "wf_start_time")
    ]


def build_dataset(run_table: pd.DataFrame, columns: list[str]) -> dict[str, list]:
    sequences: list[np.ndarray] = []
    lengths: list[int] = []
    targets: list[float] = []
    labels: list[str] = []
    for row in run_table.itertuples(index=False):
        frame = load_run_features(row.experiment, row.run)
        if frame is None:
            raise RuntimeError(f"no features found for {row.experiment} run {row.run}")
        matrix = frame[columns].to_numpy(dtype=np.float64)
        sequences.append(matrix)
        lengths.append(matrix.shape[0])
        targets.append(float(getattr(row, TARGET_COLUMN)))
        labels.append(f"{row.experiment}/run-{row.run}")
    return {"sequences": sequences, "lengths": lengths, "targets": targets, "labels": labels}


def fit_normalizer(train_sequences: list[np.ndarray]) -> dict[str, np.ndarray]:
    stacked = np.concatenate(train_sequences, axis=0)
    median = np.nanmedian(stacked, axis=0)
    filled = np.where(np.isnan(stacked), median, stacked)
    mean = filled.mean(axis=0)
    std = filled.std(axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    return {"median": median, "mean": mean, "std": std}


def apply_normalizer(sequence: np.ndarray, normalizer: dict[str, np.ndarray]) -> np.ndarray:
    filled = np.where(np.isnan(sequence), normalizer["median"], sequence)
    return (filled - normalizer["mean"]) / normalizer["std"]


def pad_batch(sequences: list[np.ndarray], lengths: list[int]) -> tuple[torch.Tensor, torch.Tensor]:
    max_len = max(lengths)
    n_channels = sequences[0].shape[1]
    batch = np.zeros((len(sequences), max_len, n_channels), dtype=np.float32)
    for index, sequence in enumerate(sequences):
        batch[index, : sequence.shape[0]] = sequence
    return torch.from_numpy(batch), torch.tensor(lengths, dtype=torch.long)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    error = y_pred - y_true
    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(error**2)))
    if np.all(y_true == y_true[0]) or np.all(y_pred == y_pred[0]):
        spearman = float("nan")  # undefined when either side is constant (e.g. a constant baseline)
    else:
        spearman = float(stats.spearmanr(y_true, y_pred).correlation)
    ss_res = float(np.sum(error**2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
    return {"mae": mae, "rmse": rmse, "spearman": spearman, "r2": r2}


def bootstrap_mae_interval(
    y_true: np.ndarray, y_pred: np.ndarray, *, n_boot: int = 2000, seed: int = SEED
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(y_true)
    errors = np.abs(y_pred - y_true)
    boot_maes = np.empty(n_boot)
    for index in range(n_boot):
        sample = rng.integers(0, n, size=n)
        boot_maes[index] = errors[sample].mean()
    return float(np.percentile(boot_maes, 2.5)), float(np.percentile(boot_maes, 97.5))


def train_and_evaluate(
    columns: list[str],
    run_table: pd.DataFrame,
    *,
    max_epochs: int = 4000,
    patience: int = 400,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    device: str | None = None,
    seed: int = SEED,
    verbose: bool = True,
) -> dict:
    """Train one PatchTST on `columns` only; evaluate once on EXP-F.

    Returns a dict with model_metrics, mean/median constant baselines,
    per-run test predictions, training history, and the trained model
    state -- used both by main() (full 72-column run) and Phase 4's
    ablation script (column subsets), so both exercise identical code.
    """
    set_seed(seed)
    device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

    train_runs = run_table[run_table.split == "train"]
    val_runs = run_table[run_table.split == "validation"]
    test_runs = run_table[run_table.split == "test"]

    train_data = build_dataset(train_runs, columns)
    val_data = build_dataset(val_runs, columns)
    test_data = build_dataset(test_runs, columns)

    normalizer = fit_normalizer(train_data["sequences"])

    def normalized_batch(data: dict) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        normed = [apply_normalizer(sequence, normalizer) for sequence in data["sequences"]]
        x, lengths = pad_batch(normed, data["lengths"])
        y = torch.tensor(data["targets"], dtype=torch.float32)
        return x, lengths, y

    train_x, train_lengths, train_y = normalized_batch(train_data)
    val_x, val_lengths, val_y = normalized_batch(val_data)
    test_x, test_lengths, test_y = normalized_batch(test_data)

    config = PatchTSTConfig(n_channels=len(columns))
    model = PatchTSTRegressor(config).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.SmoothL1Loss()

    train_x, train_lengths, train_y = train_x.to(device), train_lengths.to(device), train_y.to(device)
    val_x, val_lengths, val_y = val_x.to(device), val_lengths.to(device), val_y.to(device)

    best_val_mae = float("inf")
    best_state = None
    best_epoch = -1
    epochs_since_improvement = 0
    history = []
    started = time.perf_counter()

    for epoch in range(1, max_epochs + 1):
        model.train()
        optimizer.zero_grad()
        prediction = model(train_x, train_lengths)
        loss = loss_fn(prediction, train_y)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_prediction = model(val_x, val_lengths)
            val_loss = loss_fn(val_prediction, val_y).item()
            val_mae = torch.mean(torch.abs(val_prediction - val_y)).item()
            train_mae = torch.mean(torch.abs(prediction.detach() - train_y)).item()

        history.append(
            {"epoch": epoch, "train_loss": loss.item(), "train_mae": train_mae,
             "val_loss": val_loss, "val_mae": val_mae}
        )
        if val_mae < best_val_mae - 1e-6:
            best_val_mae = val_mae
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            best_epoch = epoch
            epochs_since_improvement = 0
        else:
            epochs_since_improvement += 1
        if verbose and (epoch % 200 == 0 or epoch == 1):
            print(
                f"epoch {epoch:5d}  train_loss={loss.item():.5f}  train_mae={train_mae:.4f}  "
                f"val_mae={val_mae:.4f}  best_val_mae={best_val_mae:.4f} (epoch {best_epoch})"
            )
        if epochs_since_improvement >= patience:
            if verbose:
                print(f"Early stopping at epoch {epoch} (no val improvement for {patience} epochs).")
            break

    elapsed = time.perf_counter() - started
    assert best_state is not None
    model.load_state_dict(best_state)

    model.eval()
    test_x_dev, test_lengths_dev = test_x.to(device), test_lengths.to(device)
    with torch.no_grad():
        test_prediction = model(test_x_dev, test_lengths_dev).cpu().numpy()
    test_true = test_y.numpy()

    model_metrics = compute_metrics(test_true, test_prediction)
    ci_low, ci_high = bootstrap_mae_interval(test_true, test_prediction, seed=seed)

    train_targets = np.array(train_data["targets"])
    mean_baseline = np.full_like(test_true, train_targets.mean())
    median_baseline = np.full_like(test_true, np.median(train_targets))
    mean_metrics = compute_metrics(test_true, mean_baseline)
    median_metrics = compute_metrics(test_true, median_baseline)

    predictions_table = pd.DataFrame(
        {
            "label": test_data["labels"],
            "y_true": test_true,
            "y_pred": test_prediction,
            "abs_error": np.abs(test_prediction - test_true),
        }
    )

    return {
        "columns": columns,
        "n_columns": len(columns),
        "model": model,
        "normalizer": normalizer,
        "device": str(device),
        "raw_data": {"train": train_data, "val": val_data, "test": test_data},
        "model_metrics": model_metrics,
        "mean_baseline_metrics": mean_metrics,
        "median_baseline_metrics": median_metrics,
        "mae_95ci_low": ci_low,
        "mae_95ci_high": ci_high,
        "predictions_table": predictions_table,
        "history": pd.DataFrame(history),
        "best_epoch": best_epoch,
        "training_seconds": elapsed,
        "parameter_counts": model.count_parameters(),
        "sequence_lengths": {
            "train": train_data["lengths"], "val": val_data["lengths"], "test": test_data["lengths"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-epochs", type=int, default=4000)
    parser.add_argument("--patience", type=int, default=400)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args(argv)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_table = load_pinned_split_and_targets()
    print(run_table.to_string(index=False))

    probe = load_run_features(*run_table.iloc[0][["experiment", "run"]])
    columns = all_feature_columns(probe)
    print(f"\nFeature dimensionality: {len(columns)}")
    assert len(columns) == 72, f"expected 72 features, found {len(columns)}"

    result = train_and_evaluate(
        columns, run_table,
        max_epochs=args.max_epochs, patience=args.patience,
        lr=args.lr, weight_decay=args.weight_decay, device=args.device,
    )

    print(f"\nSequence-length summary (minutes/run): {result['sequence_lengths']}")
    print(f"Model parameter counts: {result['parameter_counts']}")
    print(f"Training time: {result['training_seconds']:.1f}s, best epoch: {result['best_epoch']}")

    torch.save(result["model"].state_dict(), OUTPUT_DIR / "best_model.pt")
    result["history"].to_csv(OUTPUT_DIR / "training_history.csv", index=False)
    result["predictions_table"].to_csv(OUTPUT_DIR / "test_predictions.csv", index=False)

    comparison = pd.DataFrame(
        [
            {"model": "training_mean_constant", **result["mean_baseline_metrics"]},
            {"model": "training_median_constant", **result["median_baseline_metrics"]},
            {"model": "patchtst_freq_baseline (this run)", **result["model_metrics"],
             "mae_95ci_low": result["mae_95ci_low"], "mae_95ci_high": result["mae_95ci_high"]},
        ]
    )
    comparison.to_csv(OUTPUT_DIR / "comparison_table.csv", index=False)

    print("\n=== Comparison table (EXP-F, N=8, raw_top3_mean_pct) ===")
    print(comparison.to_string(index=False))
    print("\n=== Per-run test predictions ===")
    print(result["predictions_table"].to_string(index=False))
    print(
        f"\nInternal consistency check -- recomputed training-mean/median MAE should be close to "
        f"P4's cited 0.680 pp: mean={result['mean_baseline_metrics']['mae']:.4f}, "
        f"median={result['median_baseline_metrics']['mae']:.4f}"
    )

    environment = {
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device_used": result["device"],
        "seed": SEED,
        "max_epochs": args.max_epochs,
        "patience": args.patience,
        "best_epoch": result["best_epoch"],
        "training_seconds": result["training_seconds"],
        "model_parameters": result["parameter_counts"],
    }
    (OUTPUT_DIR / "environment.json").write_text(json.dumps(environment, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
