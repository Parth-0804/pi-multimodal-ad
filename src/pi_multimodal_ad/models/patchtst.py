"""A compact, channel-independent PatchTST-style scalar regressor."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True, slots=True)
class PatchTSTConfig:
    input_channels: int
    patch_length: int = 16
    patch_stride: int = 8
    d_model: int = 32
    n_heads: int = 4
    encoder_layers: int = 2
    feedforward_dimension: int = 64
    dropout: float = 0.1
    head_hidden_dimension: int = 64

    def __post_init__(self) -> None:
        for name in (
            "input_channels",
            "patch_length",
            "patch_stride",
            "d_model",
            "n_heads",
            "encoder_layers",
            "feedforward_dimension",
            "head_hidden_dimension",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.d_model % self.n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        if not 0 <= self.dropout < 1:
            raise ValueError("dropout must lie in [0, 1)")


class SinusoidalPositionEncoding(nn.Module):
    def __init__(self, d_model: int) -> None:
        super().__init__()
        self.d_model = d_model

    def forward(
        self, length: int, *, device: torch.device, dtype: torch.dtype
    ) -> torch.Tensor:
        position = torch.arange(length, device=device, dtype=torch.float32).unsqueeze(1)
        divider = torch.exp(
            torch.arange(0, self.d_model, 2, device=device, dtype=torch.float32)
            * (-math.log(10_000.0) / self.d_model)
        )
        encoding = torch.zeros(length, self.d_model, device=device, dtype=torch.float32)
        encoding[:, 0::2] = torch.sin(position * divider)
        encoding[:, 1::2] = torch.cos(position * divider[: encoding[:, 1::2].shape[1]])
        return encoding.to(dtype=dtype).unsqueeze(0)


class PatchTSTRegressor(nn.Module):
    """Patch features independently and pool only verified time steps."""

    def __init__(self, config: PatchTSTConfig) -> None:
        super().__init__()
        self.config = config
        self.patch_projection = nn.Linear(config.patch_length, config.d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.n_heads,
            dim_feedforward=config.feedforward_dimension,
            dropout=config.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=config.encoder_layers)
        self.position = SinusoidalPositionEncoding(config.d_model)
        self.head = nn.Sequential(
            nn.LayerNorm(config.input_channels * config.d_model),
            nn.Linear(
                config.input_channels * config.d_model,
                config.head_hidden_dimension,
            ),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.head_hidden_dimension, 1),
        )

    def patchify(
        self, inputs: torch.Tensor, time_mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if inputs.ndim != 3:
            raise ValueError("inputs must have shape batch x time x channels")
        if time_mask.shape != inputs.shape[:2] or time_mask.dtype != torch.bool:
            raise ValueError("time_mask must be a boolean batch x time tensor")
        if inputs.shape[2] != self.config.input_channels:
            raise ValueError("input channel count does not match model configuration")
        length = inputs.shape[1]
        patch_length = self.config.patch_length
        stride = self.config.patch_stride
        if length <= patch_length:
            padded_length = patch_length
        else:
            patch_count = math.ceil((length - patch_length) / stride) + 1
            padded_length = (patch_count - 1) * stride + patch_length
        right = padded_length - length
        masked_inputs = inputs * time_mask.unsqueeze(-1).to(inputs.dtype)
        values = F.pad(masked_inputs.transpose(1, 2), (0, right))
        mask = F.pad(time_mask, (0, right), value=False)
        patches = values.unfold(2, patch_length, stride)
        patch_mask = mask.unfold(1, patch_length, stride).any(dim=-1)
        return patches, patch_mask

    def encode(
        self, inputs: torch.Tensor, time_mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        patches, patch_mask = self.patchify(inputs, time_mask)
        batch, channels, patch_count, _ = patches.shape
        tokens = self.patch_projection(patches).reshape(
            batch * channels, patch_count, self.config.d_model
        )
        tokens = tokens + self.position(
            patch_count, device=tokens.device, dtype=tokens.dtype
        )
        expanded_mask = (
            patch_mask[:, None, :]
            .expand(batch, channels, patch_count)
            .reshape(batch * channels, patch_count)
        )
        encoded = self.encoder(tokens, src_key_padding_mask=~expanded_mask)
        weights = expanded_mask.unsqueeze(-1).to(encoded.dtype)
        pooled = (encoded * weights).sum(dim=1) / weights.sum(dim=1).clamp_min(1.0)
        return pooled.reshape(batch, channels, self.config.d_model), patch_mask

    def forward(self, inputs: torch.Tensor, time_mask: torch.Tensor) -> torch.Tensor:
        encoded, _ = self.encode(inputs, time_mask)
        return self.head(encoded.flatten(start_dim=1)).squeeze(-1)
