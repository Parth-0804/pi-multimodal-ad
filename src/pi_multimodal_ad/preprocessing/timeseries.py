"""Training-only normalization and mask-aware run sequence construction."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import torch


@dataclass(frozen=True, slots=True)
class FeatureNormalizer:
    feature_columns: tuple[str, ...]
    medians: tuple[float, ...]
    means: tuple[float, ...]
    scales: tuple[float, ...]
    fitted_split: str = "train"

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "feature_columns": list(self.feature_columns),
            "medians": list(self.medians),
            "means": list(self.means),
            "scales": list(self.scales),
            "fitted_split": self.fitted_split,
            "missing_value_policy": "training_median_then_training_standardization",
        }


@dataclass(frozen=True, slots=True)
class RunSequence:
    sequence_id: str
    experiment: str
    run: int
    split: str
    values: np.ndarray
    target_raw: float
    target_monotonic: float
    minute_ids: tuple[str, ...]


def fit_feature_normalizer(
    minute: pd.DataFrame,
    *,
    feature_columns: Sequence[str],
    training_split: str = "train",
) -> FeatureNormalizer:
    """Fit imputation and scaling on included training minutes only."""

    columns = tuple(feature_columns)
    scoped = minute[
        minute.split.eq(training_split)
        & minute.sequence_inclusion_status.eq("included")
    ]
    if scoped.empty:
        raise ValueError("training minute set is empty")
    values = scoped[list(columns)].apply(pd.to_numeric, errors="coerce")
    medians = values.median(axis=0, skipna=True).fillna(0.0)
    imputed = values.fillna(medians)
    means = imputed.mean(axis=0)
    scales = imputed.std(axis=0, ddof=0)
    scales = scales.mask(scales < 1e-8, 1.0).fillna(1.0)
    return FeatureNormalizer(
        feature_columns=columns,
        medians=tuple(float(value) for value in medians),
        means=tuple(float(value) for value in means),
        scales=tuple(float(value) for value in scales),
        fitted_split=training_split,
    )


def transform_feature_frame(
    frame: pd.DataFrame, normalizer: FeatureNormalizer
) -> np.ndarray:
    """Apply persisted training statistics without fitting on the input frame."""

    values = frame[list(normalizer.feature_columns)].apply(
        pd.to_numeric, errors="coerce"
    )
    medians = pd.Series(normalizer.medians, index=normalizer.feature_columns)
    imputed = values.fillna(medians).to_numpy(np.float32)
    means = np.asarray(normalizer.means, dtype=np.float32)
    scales = np.asarray(normalizer.scales, dtype=np.float32)
    transformed = (imputed - means) / scales
    if not np.isfinite(transformed).all():
        raise ValueError("normalization produced non-finite values")
    return transformed


def build_run_sequences(
    minute: pd.DataFrame,
    run_summary: pd.DataFrame,
    *,
    normalizer: FeatureNormalizer,
) -> list[RunSequence]:
    """Build chronological variable-length arrays from verified minute rows."""

    summary_index = run_summary.set_index(["experiment", "run"])
    sequences: list[RunSequence] = []
    for (experiment, run_number), scoped in minute.groupby(["experiment", "run"]):
        included = scoped[scoped.sequence_inclusion_status.eq("included")].sort_values(
            "sequence_position", kind="stable"
        )
        if included.empty:
            continue
        positions = included.sequence_position.astype(int).to_numpy()
        if not np.array_equal(positions, np.arange(1, len(positions) + 1)):
            raise ValueError(
                f"non-contiguous sequence positions for {experiment}/{run_number}"
            )
        summary = summary_index.loc[(experiment, run_number)]
        sequences.append(
            RunSequence(
                sequence_id=str(summary.sequence_id),
                experiment=str(experiment),
                run=int(run_number),
                split=str(summary.split),
                values=transform_feature_frame(included, normalizer),
                target_raw=float(summary.raw_top3_mean_pct),
                target_monotonic=float(summary.causal_monotonic_top3_mean_pct),
                minute_ids=tuple(included.minute_id.astype(str)),
            )
        )
    return sorted(sequences, key=lambda item: (item.experiment, item.run))


def collate_run_sequences(
    sequences: Sequence[RunSequence],
) -> dict[str, Any]:
    """Right-pad a batch and return a validity mask separate from data values."""

    if not sequences:
        raise ValueError("cannot collate an empty sequence batch")
    channels = sequences[0].values.shape[1]
    if any(sequence.values.ndim != 2 for sequence in sequences):
        raise ValueError("sequence values must have shape time x channels")
    if any(sequence.values.shape[1] != channels for sequence in sequences):
        raise ValueError("all sequences must have the same channel count")
    maximum = max(sequence.values.shape[0] for sequence in sequences)
    values = np.zeros((len(sequences), maximum, channels), dtype=np.float32)
    mask = np.zeros((len(sequences), maximum), dtype=bool)
    for index, sequence in enumerate(sequences):
        length = sequence.values.shape[0]
        values[index, :length] = sequence.values
        mask[index, :length] = True
    return {
        "inputs": torch.from_numpy(values),
        "time_mask": torch.from_numpy(mask),
        "targets_raw": torch.tensor(
            [sequence.target_raw for sequence in sequences], dtype=torch.float32
        ),
        "targets_monotonic": torch.tensor(
            [sequence.target_monotonic for sequence in sequences], dtype=torch.float32
        ),
        "sequence_ids": [sequence.sequence_id for sequence in sequences],
        "experiments": [sequence.experiment for sequence in sequences],
        "runs": [sequence.run for sequence in sequences],
        "splits": [sequence.split for sequence in sequences],
        "lengths": [sequence.values.shape[0] for sequence in sequences],
    }
