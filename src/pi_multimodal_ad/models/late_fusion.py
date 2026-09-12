"""Late fusion over sensor sub-modalities that exist at inference time.

Images are unavailable at test time, so fusion here means combining the sensor
sub-modalities actually present, not image+sensor fusion. The nine channels
partition into three groups that differ in kind, not just in name:

    process context      rpm, torque, temperature      operating conditions
    organiser RMS        axial_rms, radial_rms         broadband energy
    condition indicators fm4, na4, m6a, alr            classical gear-fault CIs

One PatchTST encoder per group, pooled embeddings concatenated, one scalar
head. The encoder path is `PatchTSTRegressor.encode` unchanged -- this module
only routes channels and joins the results, so a fused model and the
single-encoder baseline differ in how channels are encoded rather than in the
encoder itself. With all three groups present the head sees the same width as
the single-encoder baseline (sum of group channels x d_model), which keeps the
comparison to that baseline about fusion and not about capacity.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import torch
from torch import nn

from .patchtst import PatchTSTConfig, PatchTSTRegressor

SUB_MODALITY_CHANNELS: Mapping[str, tuple[str, ...]] = {
    "process_context": ("rpm", "torque", "temperature"),
    "organiser_rms": ("axial_rms", "radial_rms"),
    "condition_indicators": ("fm4", "na4", "m6a", "alr"),
}


def sub_modality_column_indices(
    feature_columns: Sequence[str], base_channels: Sequence[str]
) -> list[int]:
    """Indices of every feature column derived from the given base channels.

    A base channel contributes its statistics (`rpm_mean`, `rpm_std`, ...) and
    its missingness mask (`rpm_missing`). Matching is anchored on the exact
    prefix so that `alr_*` cannot absorb a column belonging to another channel
    that merely starts with the same letters.
    """

    indices: list[int] = []
    for index, column in enumerate(feature_columns):
        for base in base_channels:
            if column == f"{base}_missing" or column.startswith(f"{base}_"):
                indices.append(index)
                break
    if not indices:
        raise ValueError(f"no feature columns matched base channels {tuple(base_channels)}")
    return indices


class LateFusionRegressor(nn.Module):
    """One encoder per sub-modality, concatenated pooled embeddings, one head."""

    def __init__(
        self,
        config: PatchTSTConfig,
        *,
        group_indices: Mapping[str, Sequence[int]],
    ) -> None:
        super().__init__()
        if not group_indices:
            raise ValueError("at least one sub-modality group is required")
        self.group_names = tuple(group_indices)
        self.register_buffer(
            "_unused", torch.zeros(0), persistent=False
        )  # keeps .to(device) well-defined when every branch is registered below
        self.group_index_tensors: dict[str, torch.Tensor] = {}
        branches: dict[str, PatchTSTRegressor] = {}
        pooled_width = 0
        for name, indices in group_indices.items():
            indices = list(indices)
            if not indices:
                raise ValueError(f"sub-modality {name!r} has no channels")
            branch_config = PatchTSTConfig(
                input_channels=len(indices),
                patch_length=config.patch_length,
                patch_stride=config.patch_stride,
                d_model=config.d_model,
                n_heads=config.n_heads,
                encoder_layers=config.encoder_layers,
                feedforward_dimension=config.feedforward_dimension,
                dropout=config.dropout,
                head_hidden_dimension=config.head_hidden_dimension,
            )
            branches[name] = PatchTSTRegressor(branch_config)
            self.register_buffer(
                f"group_index_{name}",
                torch.tensor(indices, dtype=torch.long),
                persistent=True,
            )
            pooled_width += len(indices) * config.d_model
        self.branches = nn.ModuleDict(branches)
        self.config = config
        self.pooled_width = pooled_width
        self.head = nn.Sequential(
            nn.LayerNorm(pooled_width),
            nn.Linear(pooled_width, config.head_hidden_dimension),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.head_hidden_dimension, 1),
        )

    def forward(self, inputs: torch.Tensor, time_mask: torch.Tensor) -> torch.Tensor:
        pooled: list[torch.Tensor] = []
        for name in self.group_names:
            indices = getattr(self, f"group_index_{name}")
            encoded, _ = self.branches[name].encode(
                inputs.index_select(2, indices), time_mask
            )
            pooled.append(encoded.flatten(start_dim=1))
        joined = torch.cat(pooled, dim=1)
        return self.head(joined).squeeze(-1)
