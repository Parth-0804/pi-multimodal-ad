"""From-scratch PatchTST in plain PyTorch.

Structurally follows the published PatchTST idea (Nie et al. 2023,
"A Time Series is Worth 64 Words"): each input channel is treated as an
independent univariate series, split into overlapping patches, linearly
embedded, and passed through ONE SHARED Transformer encoder across all
channels (channel independence -- the architecture's defining idea, not
an implementation detail of any particular codebase). No code is imported
from this repository's own src/pi_multimodal_ad/models/patchtst.py; every
layer below is defined fresh for this tutorial.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True, slots=True)
class PatchTSTConfig:
    n_channels: int = 72
    patch_len: int = 16
    stride: int = 8
    d_model: int = 32
    n_heads: int = 4
    n_layers: int = 2
    d_ff: int = 64
    dropout: float = 0.1
    head_hidden: int = 64
    max_patches: int = 128  # (528 - 16)/8 + 1 = 65, generous headroom


def make_patches(x: torch.Tensor, patch_len: int, stride: int) -> torch.Tensor:
    """x: (B, C, T) -> (B, C, N, patch_len) via a sliding window along T."""
    return x.unfold(dimension=2, size=patch_len, step=stride)


def patch_validity_mask(
    lengths: torch.Tensor, n_patches: int, patch_len: int, stride: int
) -> torch.Tensor:
    """A patch counts as valid only if every one of its patch_len positions
    is real (unpadded) data -- i.e. patch_start + patch_len <= real length.
    Returns (B, N) bool.
    """
    device = lengths.device
    patch_starts = torch.arange(n_patches, device=device) * stride
    patch_ends = patch_starts + patch_len  # (N,)
    return patch_ends.unsqueeze(0) <= lengths.unsqueeze(1)  # (B, N)


class PatchTSTRegressor(nn.Module):
    """Channel-independent PatchTST encoder -> masked pooling -> scalar head."""

    def __init__(self, config: PatchTSTConfig) -> None:
        super().__init__()
        self.config = config
        self.patch_embed = nn.Linear(config.patch_len, config.d_model)
        self.position_embed = nn.Parameter(
            torch.randn(config.max_patches, config.d_model) * 0.02
        )
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.n_heads,
            dim_feedforward=config.d_ff,
            dropout=config.dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=config.n_layers)
        self.dropout = nn.Dropout(config.dropout)
        self.head = nn.Sequential(
            nn.Linear(config.d_model, config.head_hidden),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.head_hidden, 1),
        )

    def forward(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        """x: (B, T, C) standardized feature sequence, right-padded.
        lengths: (B,) real (unpadded) sequence length per sample.
        Returns: (B,) scalar prediction.
        """
        config = self.config
        B, T, C = x.shape
        assert C == config.n_channels, f"expected {config.n_channels} channels, got {C}"
        x = x.transpose(1, 2)  # (B, C, T)
        if T < config.patch_len:
            pad = config.patch_len - T
            x = nn.functional.pad(x, (0, pad))
            T = config.patch_len
        patches = make_patches(x, config.patch_len, config.stride)  # (B, C, N, patch_len)
        n_patches = patches.shape[2]

        embedded = self.patch_embed(patches)  # (B, C, N, d_model)
        embedded = embedded + self.position_embed[:n_patches].view(1, 1, n_patches, -1)
        embedded = self.dropout(embedded)

        flat = embedded.reshape(B * C, n_patches, config.d_model)
        encoded = self.encoder(flat)  # (B*C, N, d_model)
        encoded = encoded.reshape(B, C, n_patches, config.d_model)

        mask = patch_validity_mask(lengths, n_patches, config.patch_len, config.stride)
        mask = mask.to(encoded.dtype)  # (B, N)
        mask_expanded = mask.view(B, 1, n_patches, 1)  # broadcast over C, d_model
        summed = (encoded * mask_expanded).sum(dim=2)  # (B, C, d_model)
        counts = mask.sum(dim=1).clamp(min=1.0).view(B, 1, 1)  # (B,1,1)
        pooled_per_channel = summed / counts  # (B, C, d_model)

        pooled = pooled_per_channel.mean(dim=1)  # (B, d_model) -- average across channels
        out = self.head(pooled).squeeze(-1)  # (B,)
        return out

    def count_parameters(self) -> dict[str, int]:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total_parameters": total, "trainable_parameters": trainable}
