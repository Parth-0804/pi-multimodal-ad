#!/usr/bin/env python3
"""Phase 4 residual analysis: are errors concentrated or spread evenly?

Retrains once under the same fixed seed as Phase 3 (train.py) -- this is
expected to reproduce Phase 3's EXP-F numbers closely (checked explicitly
below) -- then runs the SAME trained model on every one of the 20 runs
(train/validation/test), not just the 8 held-out test runs, to see whether
residual error tracks experiment, run order (progressive wear), or target
magnitude. N is tiny (20 runs total, 8 in test) -- every statistic here is
reported as descriptive/suggestive, not a hypothesis test with real power.
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from train import (  # noqa: E402
    OUTPUT_DIR as MAIN_OUTPUT_DIR,
    all_feature_columns,
    apply_normalizer,
    load_pinned_split_and_targets,
    load_run_features,
    pad_batch,
    train_and_evaluate,
)

OUT_DIR = Path(__file__).resolve().parent / "residuals_output"


def predict_split(model, normalizer, data: dict, device: str) -> np.ndarray:
    normed = [apply_normalizer(sequence, normalizer) for sequence in data["sequences"]]
    x, lengths = pad_batch(normed, data["lengths"])
    x, lengths = x.to(device), lengths.to(device)
    model.eval()
    with torch.no_grad():
        prediction = model(x, lengths).cpu().numpy()
    return prediction


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_table = load_pinned_split_and_targets()
    probe = load_run_features(*run_table.iloc[0][["experiment", "run"]])
    all_columns = all_feature_columns(probe)

    result = train_and_evaluate(all_columns, run_table, verbose=False)
    print(f"Retrained (same seed as Phase 3) -- best_epoch={result['best_epoch']}")
    print(f"EXP-F metrics this run: {result['model_metrics']}")

    main_comparison_path = MAIN_OUTPUT_DIR / "comparison_table.csv"
    if main_comparison_path.is_file():
        cached = pd.read_csv(main_comparison_path)
        cached_mae = cached.loc[
            cached.model == "patchtst_freq_baseline (this run)", "mae"
        ]
        if not cached_mae.empty:
            print(
                f"Phase 3's saved EXP-F MAE: {cached_mae.iloc[0]:.4f} vs this "
                f"retrain's: {result['model_metrics']['mae']:.4f} "
                "(should match closely under the same fixed seed)."
            )

    model = result["model"]
    normalizer = result["normalizer"]
    device = result["device"]

    rows = []
    for split_name, data in result["raw_data"].items():
        predictions = predict_split(model, normalizer, data, device)
        for label, y_true, y_pred, length in zip(
            data["labels"], data["targets"], predictions, data["lengths"]
        ):
            experiment, run_label = label.split("/run-")
            rows.append(
                {
                    "split": split_name,
                    "experiment": experiment,
                    "run": int(run_label),
                    "y_true": y_true,
                    "y_pred": float(y_pred),
                    "error": float(y_pred) - y_true,
                    "abs_error": abs(float(y_pred) - y_true),
                    "sequence_length_minutes": length,
                }
            )
    full = pd.DataFrame(rows).sort_values(["split", "experiment", "run"])
    full.to_csv(OUT_DIR / "all_run_residuals.csv", index=False)
    print("\n=== Residuals across all 20 runs (all splits) ===")
    print(full.to_string(index=False))

    by_split = full.groupby("split")["abs_error"].agg(["mean", "std", "min", "max", "count"])
    by_split.to_csv(OUT_DIR / "abs_error_by_split.csv")
    print("\n=== abs_error summary by split ===")
    print(by_split.to_string())

    test_only = full[full.split == "test"].sort_values("run")
    correlation_with_run = np.corrcoef(test_only.run, test_only.error)[0, 1]
    correlation_with_target = np.corrcoef(test_only.y_true, test_only.abs_error)[0, 1]
    print(f"\nEXP-F (N=8) correlation(run number, signed error) = {correlation_with_run:.4f}")
    print(f"EXP-F (N=8) correlation(target magnitude, abs error) = {correlation_with_target:.4f}")
    (OUT_DIR / "correlations.txt").write_text(
        f"EXP-F (N=8) correlation(run_number, signed_error) = {correlation_with_run:.6f}\n"
        f"EXP-F (N=8) correlation(target_magnitude, abs_error) = {correlation_with_target:.6f}\n"
        "N=8 -- these are descriptive, not statistically powered correlations.\n"
    )

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    colors = {"EXP-A": "#DD8452", "EXP-B": "#4C72B0", "EXP-F": "#55A868"}
    for experiment, group in full.groupby("experiment"):
        axes[0].scatter(group.run, group.error, label=experiment, color=colors[experiment])
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("run number (within experiment)")
    axes[0].set_ylabel("signed error (pred - true, pp)")
    axes[0].set_title("Error vs. run order, all 20 runs")
    axes[0].legend()

    for experiment, group in full.groupby("experiment"):
        axes[1].scatter(group.y_true, group.y_pred, label=experiment, color=colors[experiment])
    lims = [full.y_true.min() - 0.3, full.y_true.max() + 0.3]
    axes[1].plot(lims, lims, color="black", linewidth=0.8, linestyle="--")
    axes[1].set_xlabel("true raw_top3_mean_pct")
    axes[1].set_ylabel("predicted")
    axes[1].set_title("Predicted vs. true, all 20 runs")
    axes[1].legend()

    split_order = ["train", "val", "test"]
    axes[2].bar(
        split_order,
        [by_split.loc[s, "mean"] for s in split_order],
        yerr=[by_split.loc[s, "std"] for s in split_order],
        color=["#4C72B0", "#DD8452", "#55A868"],
    )
    axes[2].set_ylabel("mean |error| (pp)")
    axes[2].set_title("Mean absolute error by split")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "residual_analysis.png", dpi=150)
    plt.close(fig)

    print("\nWrote:")
    for path in sorted(OUT_DIR.iterdir()):
        print(" ", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
