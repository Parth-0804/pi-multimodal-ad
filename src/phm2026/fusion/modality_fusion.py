"""Four fusion architectures over sensor sub-modalities, for SQ2 and SQ3.

The exposé's four-architecture comparison is reframed onto the SENSOR streams,
because images do not exist at inference and an image+sensor comparison cannot
deploy. All modalities here are present at test time.

Groups are defined by HDF5 provenance (see `SUB_MODALITY_PROVENANCE`). Note
that the encoder group is EMPTY: no channel in the committed feature pipeline
reads `/Vibration/Encoder`. The organiser's condition indicators come from
`/CI/*`, which does not distinguish accelerometer 1 from 2, so they cannot be
attributed to either and form their own group rather than being discarded.

  A2  concatenation   -- one encoder over all channels (the existing baseline)
  A3  modular late    -- one encoder AND one scalar head per group, combined at
                         the DECISION level by a learned weighting of scalars
  A4  process-aware   -- one encoder per group projected to a shared space,
      gated              combined by a gate whose weights are produced from the
                         process-context group, then a single head

A4 is "process-aware" in the exposé's literal sense: the gate conditions on
process context (speed, torque, temperature).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import torch
from torch import nn

from .patchtst import PatchTSTConfig, PatchTSTRegressor

# base channel -> HDF5 path, from configs/experiments/phm2026_sensor_features.yaml
SUB_MODALITY_PROVENANCE: Mapping[str, tuple[str, ...]] = {
    "M1_accel1": ("axial_rms",),            # /Context/Accel1 RMS
    "M2_accel2": ("radial_rms",),           # /Context/Accel2 RMS
    "M3_encoder": (),                       # EMPTY -- /Vibration/Encoder not in pipeline
    "M4_context": ("rpm", "torque", "temperature"),   # /Context/PAU Speed, Torque, Temperature
    "M5_condition_indicators": ("fm4", "na4", "m6a", "alr"),  # /CI/* -- accel unattributable
}
GATE_GROUP = "M4_context"


def group_column_indices(
    feature_columns: Sequence[str], base_channels: Sequence[str]
) -> list[int]:
    indices = []
    for index, column in enumerate(feature_columns):
        for base in base_channels:
            if column == f"{base}_missing" or column.startswith(f"{base}_"):
                indices.append(index)
                break
    return indices


def resolve_groups(feature_columns: Sequence[str]) -> dict[str, list[int]]:
    """Non-empty groups only, so an empty modality cannot silently become a branch."""
    resolved = {}
    for name, bases in SUB_MODALITY_PROVENANCE.items():
        indices = group_column_indices(feature_columns, bases)
        if indices:
            resolved[name] = indices
    return resolved


def _branch_config(config: PatchTSTConfig, n_channels: int) -> PatchTSTConfig:
    return PatchTSTConfig(
        input_channels=n_channels, patch_length=config.patch_length,
        patch_stride=config.patch_stride, d_model=config.d_model,
        n_heads=config.n_heads, encoder_layers=config.encoder_layers,
        feedforward_dimension=config.feedforward_dimension, dropout=config.dropout,
        head_hidden_dimension=config.head_hidden_dimension,
    )


class DecisionLevelFusion(nn.Module):
    """A3: one encoder and one scalar head per group; combine the SCALARS."""

    def __init__(self, config: PatchTSTConfig, *, group_indices: Mapping[str, Sequence[int]]):
        super().__init__()
        if not group_indices:
            raise ValueError("at least one non-empty group is required")
        self.group_names = tuple(group_indices)
        branches, heads = {}, {}
        for name, indices in group_indices.items():
            branches[name] = PatchTSTRegressor(_branch_config(config, len(indices)))
            heads[name] = nn.Sequential(
                nn.LayerNorm(len(indices) * config.d_model),
                nn.Linear(len(indices) * config.d_model, config.head_hidden_dimension),
                nn.GELU(), nn.Dropout(config.dropout),
                nn.Linear(config.head_hidden_dimension, 1),
            )
            self.register_buffer(f"index_{name}", torch.tensor(list(indices), dtype=torch.long))
        self.branches = nn.ModuleDict(branches)
        self.heads = nn.ModuleDict(heads)
        # decision-level combination: a learned weighting over per-branch scalars
        self.combination = nn.Linear(len(group_indices), 1)
        nn.init.constant_(self.combination.weight, 1.0 / len(group_indices))
        nn.init.zeros_(self.combination.bias)

    def forward(self, inputs: torch.Tensor, time_mask: torch.Tensor) -> torch.Tensor:
        scalars = []
        for name in self.group_names:
            indices = getattr(self, f"index_{name}")
            encoded, _ = self.branches[name].encode(inputs.index_select(2, indices), time_mask)
            scalars.append(self.heads[name](encoded.flatten(start_dim=1)))
        return self.combination(torch.cat(scalars, dim=1)).squeeze(-1)


class ProcessAwareGatedFusion(nn.Module):
    """A4: per-group encoders projected to a shared space, gated on process context.

    The gate's weights are produced from the process-context group only. If that
    group's inputs are removed at evaluation time the gate still produces a
    weighting -- from its bias alone -- so the model falls back to a fixed
    combination rather than failing. That behaviour is the point of ablation R4
    and is deliberately not special-cased here.
    """

    def __init__(self, config: PatchTSTConfig, *, group_indices: Mapping[str, Sequence[int]],
                 shared_dimension: int = 32):
        super().__init__()
        if GATE_GROUP not in group_indices:
            raise ValueError(f"gated fusion requires the {GATE_GROUP} group")
        self.group_names = tuple(group_indices)
        self.shared_dimension = shared_dimension
        branches, projections = {}, {}
        for name, indices in group_indices.items():
            branches[name] = PatchTSTRegressor(_branch_config(config, len(indices)))
            projections[name] = nn.Sequential(
                nn.LayerNorm(len(indices) * config.d_model),
                nn.Linear(len(indices) * config.d_model, shared_dimension),
            )
            self.register_buffer(f"index_{name}", torch.tensor(list(indices), dtype=torch.long))
        self.branches = nn.ModuleDict(branches)
        self.projections = nn.ModuleDict(projections)
        gate_width = len(group_indices[GATE_GROUP]) * config.d_model
        self.gate = nn.Sequential(
            nn.LayerNorm(gate_width),
            nn.Linear(gate_width, config.head_hidden_dimension),
            nn.GELU(),
            nn.Linear(config.head_hidden_dimension, len(group_indices)),
        )
        self.head = nn.Sequential(
            nn.LayerNorm(shared_dimension),
            nn.Linear(shared_dimension, config.head_hidden_dimension),
            nn.GELU(), nn.Dropout(config.dropout),
            nn.Linear(config.head_hidden_dimension, 1),
        )

    def gate_weights(self, inputs: torch.Tensor, time_mask: torch.Tensor) -> torch.Tensor:
        indices = getattr(self, f"index_{GATE_GROUP}")
        encoded, _ = self.branches[GATE_GROUP].encode(
            inputs.index_select(2, indices), time_mask
        )
        return torch.softmax(self.gate(encoded.flatten(start_dim=1)), dim=1)

    def forward(self, inputs: torch.Tensor, time_mask: torch.Tensor) -> torch.Tensor:
        weights = self.gate_weights(inputs, time_mask)
        projected = []
        for name in self.group_names:
            indices = getattr(self, f"index_{name}")
            encoded, _ = self.branches[name].encode(inputs.index_select(2, indices), time_mask)
            projected.append(self.projections[name](encoded.flatten(start_dim=1)))
        stacked = torch.stack(projected, dim=1)             # (B, G, shared)
        combined = (stacked * weights.unsqueeze(-1)).sum(1)  # gate-weighted sum
        return self.head(combined).squeeze(-1)
