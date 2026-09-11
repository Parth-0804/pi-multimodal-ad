#!/usr/bin/env python3
"""Fit SortedProfileHead constants and check the per-tooth label for confounds.

Two jobs, one table read:

1. Fit the init/scaling constants `PatchTSTConfig` needs for a profile head
   (`profile_init_base`, `profile_init_steps`, `profile_target_mean`,
   `profile_target_scale`) from the TRAIN split only.

2. Test whether the per-tooth label is confounded by acquisition protocol.
   EXP-A/EXP-B photograph teeth 1-4 ten times and everything else once;
   EXP-F photographs every tooth once. The target takes the maximum across
   views, and a maximum over ten draws exceeds a maximum over one for the
   same underlying distribution. If that inflation is real, a model trained
   on EXP-B and evaluated on EXP-F should over-predict.

Writes nothing outside the report path; fitting is read-only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

SPLIT_BY_EXPERIMENT = {"EXP-B": "train", "EXP-A": "validation", "EXP-F": "test"}
VALUE = "per_tooth_damage_candidate_pct"


def build_profiles(teeth: pd.DataFrame, *, expected_teeth: int) -> pd.DataFrame:
    """One row per run: the run's tooth values sorted ascending."""

    rows = []
    for (experiment, run), scoped in teeth.groupby(["experiment", "run"]):
        values = np.sort(scoped[VALUE].to_numpy(dtype=np.float64))
        rows.append(
            {
                "experiment": experiment,
                "run": int(run),
                "split": SPLIT_BY_EXPERIMENT.get(str(experiment), "unassigned"),
                "tooth_count": len(values),
                "complete": len(values) == expected_teeth,
                "profile": values,
                "top3_mean": float(values[-3:].mean()) if len(values) >= 3 else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["experiment", "run"], kind="stable")


def fit_constants(profiles: pd.DataFrame, *, expected_teeth: int) -> dict[str, object]:
    """Fit profile-head init constants on complete TRAIN runs only."""

    train = profiles[profiles.split.eq("train") & profiles.complete]
    if train.empty:
        raise SystemExit(
            "no complete training runs; cannot fit profile constants "
            f"(need {expected_teeth} teeth per run)"
        )
    matrix = np.vstack(train.profile.to_numpy())
    mean_profile = matrix.mean(axis=0)
    flat = matrix.reshape(-1)
    return {
        "fitted_on": {
            "split": "train",
            "experiments": sorted(train.experiment.unique().tolist()),
            "run_count": int(len(train)),
            "teeth_per_run": expected_teeth,
        },
        "profile_init_base": float(mean_profile[0]),
        "profile_init_steps": [float(value) for value in np.diff(mean_profile)],
        "profile_target_mean": float(flat.mean()),
        "profile_target_scale": float(flat.std()),
        "mean_profile": [float(value) for value in mean_profile],
    }


def report_target_scale(profiles: pd.DataFrame) -> pd.DataFrame:
    return (
        profiles.groupby(["experiment", "split"])
        .top3_mean.agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )


def report_top3_membership(teeth: pd.DataFrame) -> pd.DataFrame:
    """Which tooth indices reach a run's top 3, per experiment."""

    rows = []
    for (experiment, run), scoped in teeth.groupby(["experiment", "run"]):
        top3 = scoped.nlargest(3, VALUE)
        for tooth_id in top3.tooth_id:
            rows.append({"experiment": experiment, "run": int(run), "tooth_id": int(tooth_id)})
    membership = pd.DataFrame(rows)
    membership["is_tooth_1_to_4"] = membership.tooth_id <= 4
    summary = (
        membership.groupby("experiment")
        .is_tooth_1_to_4.agg(["sum", "count"])
        .reset_index()
    )
    summary["share_teeth_1_to_4"] = summary["sum"] / summary["count"]
    # Under no confound this share should sit near the base rate 4/28 = 0.143.
    summary["base_rate"] = 4.0 / 28.0
    return summary


def report_view_count_effect(teeth: pd.DataFrame) -> pd.DataFrame:
    """Compare tooth values by how many views the tooth actually got."""

    if "view_count" not in teeth.columns:
        return pd.DataFrame()
    rows = []
    for experiment, scoped in teeth.groupby("experiment"):
        multi = scoped[scoped.view_count > 1][VALUE]
        single = scoped[scoped.view_count == 1][VALUE]
        rows.append(
            {
                "experiment": experiment,
                "multi_view_teeth": int(len(multi)),
                "multi_view_mean": float(multi.mean()) if len(multi) else np.nan,
                "single_view_teeth": int(len(single)),
                "single_view_mean": float(single.mean()) if len(single) else np.nan,
                "inflation_pp": (
                    float(multi.mean() - single.mean())
                    if len(multi) and len(single)
                    else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--per-tooth",
        default=(
            "runs/phm2026_image_target/20260814T012054997053Z-e195f6d9"
            "/tables/per_tooth_damage.parquet"
        ),
    )
    parser.add_argument("--expected-teeth", type=int, default=28)
    parser.add_argument("--output", default="docs/thesis/PROFILE_DIAGNOSTICS.json")
    args = parser.parse_args(argv)

    path = REPOSITORY_ROOT / args.per_tooth
    if not path.is_file():
        print(f"per-tooth table not found: {args.per_tooth}", file=sys.stderr)
        return 2
    teeth = pd.read_parquet(path)
    teeth["split"] = teeth.experiment.map(SPLIT_BY_EXPERIMENT).fillna("unassigned")

    profiles = build_profiles(teeth, expected_teeth=args.expected_teeth)

    print("=" * 72)
    print("RUN / PROFILE COVERAGE")
    print("=" * 72)
    print(
        profiles.groupby(["experiment", "split"])
        .agg(runs=("run", "count"), complete=("complete", "sum"),
             min_teeth=("tooth_count", "min"), max_teeth=("tooth_count", "max"))
        .reset_index()
        .to_string(index=False)
    )

    print()
    print("=" * 72)
    print("1. TARGET SCALE  (run-level top-3 mean, percentage points)")
    print("=" * 72)
    scale = report_target_scale(profiles)
    print(scale.to_string(index=False))
    print()
    print("Read against this: the constant baseline's MAE is 0.6797 pp.")

    print()
    print("=" * 72)
    print("2. PROTOCOL CONFOUND — who reaches the top 3?")
    print("=" * 72)
    membership = report_top3_membership(teeth)
    print(membership.to_string(index=False))
    print()
    print("base_rate 0.143 = 4/28, i.e. what you would see if teeth 1-4 were")
    print("no more likely than any other tooth to reach the top 3.")
    print("EXP-A/EXP-B give teeth 1-4 ten views each; EXP-F gives every tooth one.")
    print("A high share in A/B and a base-rate share in F is the confound.")

    print()
    print("=" * 72)
    print("3. VIEW-COUNT EFFECT — direct test")
    print("=" * 72)
    views = report_view_count_effect(teeth)
    if views.empty:
        print("no view_count column in this table; skipped")
    else:
        print(views.to_string(index=False))
        print()
        print("inflation_pp > 0 means multi-view teeth score higher than")
        print("single-view teeth. That is the maximum-over-more-draws effect,")
        print("and it is a property of the measurement, not of the gear.")

    print()
    print("=" * 72)
    print("4. PROFILE-HEAD CONSTANTS  (fitted on TRAIN only)")
    print("=" * 72)
    constants = fit_constants(profiles, expected_teeth=args.expected_teeth)
    print(f"profile_init_base     : {constants['profile_init_base']:.6f}")
    print(f"profile_target_mean   : {constants['profile_target_mean']:.6f}")
    print(f"profile_target_scale  : {constants['profile_target_scale']:.6f}")
    steps = constants["profile_init_steps"]
    assert isinstance(steps, list)
    print(f"profile_init_steps    : {len(steps)} values, "
          f"min {min(steps):.4f}, max {max(steps):.4f}")
    print(f"  first five: {[round(value, 4) for value in steps[:5]]}")
    print(f"  last five : {[round(value, 4) for value in steps[-5:]]}")

    output_path = REPOSITORY_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "source_table": args.per_tooth,
                "target_scale": scale.to_dict(orient="records"),
                "top3_membership": membership.to_dict(orient="records"),
                "view_count_effect": views.to_dict(orient="records"),
                "profile_constants": constants,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
