#!/usr/bin/env python3
"""C.3 retest: rank distillation in the UNSATURATED regime.

The original C.3 ran where the synthetic student had already solved the task
(MAE at the 0.10 floor), so any auxiliary loss could only perturb a solved
problem. This retest moves alpha into the region where the student has partial
signal, and sweeps the distillation weight so that "mechanism ineffective" can
be separated from "weight badly chosen".

Two noise models are available. Under `per_minute` noise the student averages
~370 minutes x 72 channels ~ 26,640 samples of alpha*z_r, so effective
run-level SNR is ~alpha/0.0061 and tiny alphas already suffice. Under
`per_run` noise the draw is made once per run per channel, so within-run
averaging confers no benefit and alpha means feature-target correlation as
originally intended. The calibration check decides which is used.

EVERY NUMBER HERE IS SYNTHETIC and built from the true target by construction.
It is a control on the architecture, never a PHM result, and must never share
a table with a real number.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "task_c", Path(__file__).resolve().parent / "closing_task_c.py"
)
task_c = importlib.util.module_from_spec(_spec)
sys.modules["task_c"] = task_c
_spec.loader.exec_module(task_c)

from phm2026.preprocessing.timeseries import RunSequence  # noqa: E402

ALPHAS = (0.0, 0.005, 0.01, 0.02, 0.05)
WEIGHTS = (0.0, 0.1, 0.5, 1.0)
SEEDS = (1, 2, 3)
BETA = 0.678


def synthesise(skeleton, *, alpha, seed, noise_model, n_channels=72):
    """Student features with a known amount of target signal.

    per_minute: eps drawn for every (minute, channel) -- within-run averaging
                reduces the noise, so small alpha already gives high run SNR.
    per_run:    eps drawn once per (run, channel) and held constant across the
                run's minutes -- averaging over minutes confers no benefit.
    """
    targets = skeleton.target.to_numpy(dtype=float)
    z = (targets - targets.mean()) / targets.std(ddof=0)
    rng = np.random.default_rng(seed)
    scale = float(np.sqrt(max(0.0, 1 - alpha ** 2)))
    sequences = []
    for row, z_r in zip(skeleton.itertuples(), z):
        if noise_model == "per_minute":
            eps = rng.normal(size=(row.length, n_channels))
        elif noise_model == "per_run":
            eps = np.repeat(rng.normal(size=(1, n_channels)), row.length, axis=0)
        else:
            raise ValueError(noise_model)
        values = alpha * z_r + scale * eps
        sequences.append(RunSequence(
            sequence_id=row.sequence_id, experiment=row.experiment, run=row.run,
            split="", values=values.astype(np.float32), target_raw=row.target,
            target_monotonic=row.target, minute_ids=tuple(),
        ))
    return sequences


def make_teacher(skeleton, seed):
    targets = skeleton.target.to_numpy(dtype=float)
    z = (targets - targets.mean()) / targets.std(ddof=0)
    rng = np.random.default_rng(1000 + seed)
    values = BETA * z + np.sqrt(1 - BETA ** 2) * rng.normal(size=len(z))
    return {(r.experiment, r.run): float(v)
            for r, v in zip(skeleton.itertuples(), values)}


def cell(skeleton, *, alpha, weight, seed, noise_model, device):
    sequences = synthesise(skeleton, alpha=alpha, seed=seed, noise_model=noise_model)
    teacher = make_teacher(skeleton, seed) if weight > 0 else None
    errors, constant = task_c.loeo(sequences, n_channels=72, seed=seed, device=device,
                                   teacher=teacher, weight=weight)
    return errors, constant


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--noise-model", default="per_minute",
                        choices=("per_minute", "per_run"))
    parser.add_argument("--stage", default="calibration",
                        choices=("calibration", "grid"))
    parser.add_argument("--alphas", type=float, nargs="*", default=None,
                        help="override the alpha grid; used to extend it upward")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    global ALPHAS
    if args.alphas:
        ALPHAS = tuple(args.alphas)
    skeleton = task_c.real_skeleton()
    print(f"ALL NUMBERS SYNTHETIC. noise_model={args.noise_model}, "
          f"{len(skeleton)} runs, seeds={SEEDS}\n")
    payload = {"WARNING": "ALL NUMBERS SYNTHETIC — control, not a PHM result",
               "noise_model": args.noise_model, "beta": BETA,
               "frozen_hyperparameters": task_c.FROZEN, "seeds": list(SEEDS)}

    if args.stage == "calibration":
        print("CALIBRATION CHECK — weight = 0 only")
        print(f"{'alpha':>8} {'MAE mean':>10} {'seed std':>9}  clustered 95% CI      constant")
        rows = []
        for alpha in ALPHAS:
            maes, cis, constants = [], [], []
            for seed in SEEDS:
                errors, constant = cell(skeleton, alpha=alpha, weight=0.0, seed=seed,
                                        noise_model=args.noise_model, device=args.device)
                maes.append(float(errors.mean()))
                constants.append(float(constant.mean()))
                cis.append(task_c.clustered_ci(errors))
            low = float(np.mean([c[0] for c in cis]))
            high = float(np.mean([c[1] for c in cis]))
            print(f"{alpha:>8.3f} {np.mean(maes):>10.4f} {np.std(maes):>9.4f}  "
                  f"[{low:.4f}, {high:.4f}]   {np.mean(constants):.4f}")
            rows.append({"alpha": alpha, "mae_mean": float(np.mean(maes)),
                         "mae_std": float(np.std(maes)), "ci_low": low, "ci_high": high,
                         "constant": float(np.mean(constants)), "per_seed": maes})
        payload["calibration"] = rows
        near_floor = [r for r in rows if r["alpha"] == 0.005 and r["mae_mean"] < 0.20]
        print()
        if near_floor:
            print("STOP CONDITION MET: MAE is already near the floor at alpha=0.005.")
            print("The regime is still saturated under this noise model. Re-run with")
            print("--noise-model per_run before attempting the full grid.")
        else:
            print("Calibration spans a usable range; proceed to the full grid.")
    else:
        print("FULL GRID — rows alpha, columns weight")
        grid, deltas = [], []
        baseline: dict[tuple[float, int], np.ndarray] = {}
        for alpha in ALPHAS:
            line = {}
            for weight in WEIGHTS:
                maes, per_seed_errors = [], {}
                for seed in SEEDS:
                    errors, _ = cell(skeleton, alpha=alpha, weight=weight, seed=seed,
                                     noise_model=args.noise_model, device=args.device)
                    maes.append(float(errors.mean()))
                    per_seed_errors[seed] = errors
                    if weight == 0.0:
                        baseline[(alpha, seed)] = errors
                line[weight] = (float(np.mean(maes)), float(np.std(maes)))
                grid.append({"alpha": alpha, "weight": weight,
                             "mae_mean": float(np.mean(maes)),
                             "mae_std": float(np.std(maes)), "per_seed": maes})
                if weight > 0.0:
                    # paired by seed: positive delta = distillation helped
                    base = np.concatenate([baseline[(alpha, s)] for s in SEEDS])
                    with_distill = np.concatenate([per_seed_errors[s] for s in SEEDS])
                    mean, low, high = task_c.paired_ci(base, with_distill)
                    deltas.append({"alpha": alpha, "weight": weight, "delta": mean,
                                   "ci_low": low, "ci_high": high,
                                   "helps": bool(mean > 0 and low > 0),
                                   "hurts": bool(mean < 0 and high < 0)})
            cells = "  ".join(f"w={w}: {line[w][0]:.4f}+/-{line[w][1]:.4f}" for w in WEIGHTS)
            print(f"  alpha={alpha:.3f}  {cells}")
        print("\nPAIRED DELTAS vs weight=0 (positive = distillation helped)")
        for d in deltas:
            verdict = "HELPS" if d["helps"] else ("HURTS" if d["hurts"] else "ns")
            print(f"  alpha={d['alpha']:.3f} w={d['weight']}: delta {d['delta']:+.4f} "
                  f"[{d['ci_low']:+.4f}, {d['ci_high']:+.4f}]  {verdict}")
        payload["grid"] = grid
        payload["deltas"] = deltas

    out = args.out or f"docs/thesis/CLOSING_C3_RETEST_{args.stage}_{args.noise_model}.json"
    with open(out, "w") as handle:
        json.dump(payload, handle, indent=2)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
