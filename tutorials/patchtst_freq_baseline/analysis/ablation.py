#!/usr/bin/env python3
"""Phase 4 ablation: which channels/frequency bands carry the signal, if any?

Retrains the SAME real PatchTST (via train.train_and_evaluate) on several
feature-column subsets and compares EXP-F MAE -- not a separate toy linear
probe, the actual model architecture, so results reflect what this model
relies on. Given N=7 training runs, results here are explicitly reported
as suggestive, not statistically decisive (see REPORT.md's discussion of
what's supportable at this sample size).
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from train import (  # noqa: E402
    OUTPUT_DIR as MAIN_OUTPUT_DIR,
    all_feature_columns,
    load_pinned_split_and_targets,
    load_run_features,
    train_and_evaluate,
)

OUT_DIR = Path(__file__).resolve().parent / "ablation_output"


def band_columns(tag: str, indices: range) -> list[str]:
    return [f"{tag}_band{index:02d}_log1p_energy" for index in indices]


def stat_columns(tag: str) -> list[str]:
    return [f"{tag}_rms", f"{tag}_crest_factor", f"{tag}_spectral_centroid_hz"]


def build_variants(all_columns: list[str]) -> dict[str, list[str]]:
    tags = ("accel1", "accel2")
    all_bands = {tag: band_columns(tag, range(32)) for tag in tags}
    all_stats = {tag: stat_columns(tag) for tag in tags}
    missing = [f"{tag}_missing" for tag in tags]

    variants = {
        "all_72_features": list(all_columns),
        "accel1_only_36": all_bands["accel1"] + all_stats["accel1"] + ["accel1_missing"],
        "accel2_only_36": all_bands["accel2"] + all_stats["accel2"] + ["accel2_missing"],
        "bands_only_66_no_broadband_stats": (
            all_bands["accel1"] + all_bands["accel2"] + missing
        ),
        "broadband_stats_only_8_no_bands": (
            all_stats["accel1"] + all_stats["accel2"] + missing
        ),
        "low_bands_20_297hz_only": (
            band_columns("accel1", range(0, 11)) + band_columns("accel2", range(0, 11))
            + all_stats["accel1"] + all_stats["accel2"] + missing
        ),
        "mid_bands_297_4408hz_only": (
            band_columns("accel1", range(11, 22)) + band_columns("accel2", range(11, 22))
            + all_stats["accel1"] + all_stats["accel2"] + missing
        ),
        "high_bands_4408_51200hz_only": (
            band_columns("accel1", range(22, 32)) + band_columns("accel2", range(22, 32))
            + all_stats["accel1"] + all_stats["accel2"] + missing
        ),
    }
    for name, columns in variants.items():
        missing_cols = set(columns) - set(all_columns)
        if missing_cols:
            raise ValueError(f"variant {name!r} references unknown columns: {missing_cols}")
    return variants


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_table = load_pinned_split_and_targets()
    probe = load_run_features(*run_table.iloc[0][["experiment", "run"]])
    all_columns = all_feature_columns(probe)
    assert len(all_columns) == 72

    variants = build_variants(all_columns)
    rows = []
    for name, columns in variants.items():
        print(f"\n=== variant: {name} ({len(columns)} features) ===")
        result = train_and_evaluate(columns, run_table, verbose=False)
        metrics = result["model_metrics"]
        print(
            f"  MAE={metrics['mae']:.4f}  RMSE={metrics['rmse']:.4f}  "
            f"Spearman={metrics['spearman']:.4f}  R2={metrics['r2']:.4f}  "
            f"best_epoch={result['best_epoch']}  params={result['parameter_counts']['total_parameters']}"
        )
        rows.append(
            {
                "variant": name,
                "n_features": len(columns),
                **metrics,
                "mae_95ci_low": result["mae_95ci_low"],
                "mae_95ci_high": result["mae_95ci_high"],
                "best_epoch": result["best_epoch"],
                "training_seconds": result["training_seconds"],
            }
        )
        result["predictions_table"].to_csv(OUT_DIR / f"predictions_{name}.csv", index=False)

    ablation_table = pd.DataFrame(rows).sort_values("mae")
    ablation_table.to_csv(OUT_DIR / "ablation_comparison.csv", index=False)
    print("\n=== Full ablation comparison, sorted by MAE (lower is better) ===")
    print(ablation_table.to_string(index=False))

    main_result_path = MAIN_OUTPUT_DIR / "comparison_table.csv"
    if main_result_path.is_file():
        main_comparison = pd.read_csv(main_result_path)
        print("\n=== For reference, Phase 3's main comparison table ===")
        print(main_comparison.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
