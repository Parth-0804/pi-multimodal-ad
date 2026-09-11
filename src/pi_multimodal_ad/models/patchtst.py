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
    output_teeth: int | None = None
    """When set, the head emits a sorted-ascending per-tooth profile of this
    length instead of a single scalar (see `SortedProfileHead`)."""
    profile_init_base: float = 0.0
    """SortedProfileHead only: untrained profile[0] in RAW target units, fit
    from TRAINING profiles as mean_profile[0] (never validation/test)."""
    profile_init_steps: tuple[float, ...] | None = None
    """SortedProfileHead only: untrained tooth-to-tooth increments in RAW
    target units, one per gap (length output_teeth - 1), fit from TRAINING
    profiles as np.diff(P.mean(axis=0)) -- the actual mean-profile shape,
    skew included, not a single averaged step. None falls back to a uniform
    0.2 step (matches the old, since-shown-wrong linear-ramp default) and
    should only be used when output_teeth is None."""
    profile_target_mean: float = 0.0
    """Target-scaler mean (RAW units), fit on flattened TRAINING profile
    values. Applied to both the training loss target and the init biases
    below, so the two are on the same scale -- see profile_target_scale."""
    profile_target_scale: float = 1.0
    """Target-scaler scale (RAW units, i.e. std of flattened TRAINING
    profile values). Defaults to 1.0 (no scaling) for backward
    compatibility; the profile-head training script must fit this on train
    only and pass it through here so the init constants land in the same
    (scaled) space the model actually trains and predicts in."""

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
        if self.output_teeth is not None and self.output_teeth < 2:
            raise ValueError("output_teeth must be at least 2 when set")
        if (
            self.output_teeth is not None
            and self.profile_init_steps is not None
            and len(self.profile_init_steps) != self.output_teeth - 1
        ):
            raise ValueError(
                "profile_init_steps must have output_teeth - 1 entries when set"
            )
        if self.profile_target_scale <= 0:
            raise ValueError("profile_target_scale must be positive")


class SortedProfileHead(nn.Module):
    """Pooled representation -> monotonically increasing n_teeth vector.

    Output is the run's tooth-damage profile sorted ascending, so
    profile[:, -top_k:].mean(1) reproduces the challenge's top-k
    aggregation. Monotonicity is enforced structurally (softplus deltas),
    not learned, so it holds even for an untrained model.

    At init, weights are zero and biases are set so the (scaled) output
    equals the (scaled) mean training profile exactly -- shape and skew
    included, not a linear approximation of it -- so an untrained model
    reproduces the constant-profile baseline, not an arbitrary point.
    """

    def __init__(
        self,
        in_features: int,
        n_teeth: int = 28,
        *,
        init_base: float = 0.0,
        init_steps: tuple[float, ...] | float = 0.2,
        target_mean: float = 0.0,
        target_scale: float = 1.0,
        step_floor: float = 1e-4,
    ) -> None:
        super().__init__()
        self.base = nn.Linear(in_features, 1)
        self.deltas = nn.Linear(in_features, n_teeth - 1)
        if isinstance(init_steps, (int, float)):
            init_steps = (float(init_steps),) * (n_teeth - 1)
        if len(init_steps) != n_teeth - 1:
            raise ValueError("init_steps must have n_teeth - 1 entries")
        # Zero weights -> untrained output is input-independent and equal to
        # the marginal (scaled) mean training profile. Gradients w.r.t. the
        # weights are still nonzero (softplus and cumsum are not saturated
        # at this point), so this does not block learning; it only sets the
        # starting point to the constant-profile baseline instead of an
        # arbitrary, target-scale-mismatched one.
        #
        # init_base/init_steps are RAW target units (e.g. percentage
        # points); the model trains and predicts in SCALED units (see
        # target_mean/target_scale), so both go through the same z-score
        # transform the training target does before becoming a bias: the
        # base subtracts the mean (it's a level), the per-gap steps only
        # divide by scale (they're differences, translation-invariant).
        scaled_base = (init_base - target_mean) / target_scale
        scaled_steps = torch.tensor(init_steps, dtype=torch.float32) / target_scale
        scaled_steps = scaled_steps.clamp_min(step_floor)  # guard expm1 underflow near 0
        nn.init.zeros_(self.base.weight)
        nn.init.zeros_(self.deltas.weight)
        nn.init.constant_(self.base.bias, scaled_base)
        with torch.no_grad():
            self.deltas.bias.copy_(torch.log(torch.expm1(scaled_steps)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base = self.base(x)  # (B, 1)
        deltas = F.softplus(self.deltas(x))  # (B, n_teeth - 1), > 0
        return torch.cat([base, base + deltas.cumsum(dim=1)], dim=1)  # (B, n_teeth)


def profile_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    *,
    top_k: int = 3,
    w_top: float = 0.5,
) -> torch.Tensor:
    """Tooth-level L1 plus a weighted top-k-mean L1 term.

    `pred` and `target` are both sorted ascending along the last dimension,
    so `[:, -top_k:].mean(1)` is the run-level top-k aggregate.
    """

    return F.l1_loss(pred, target) + w_top * F.l1_loss(
        pred[:, -top_k:].mean(1), target[:, -top_k:].mean(1)
    )


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
        pooled_features = config.input_channels * config.d_model
        if config.output_teeth is None:
            self.head = nn.Sequential(
                nn.LayerNorm(pooled_features),
                nn.Linear(pooled_features, config.head_hidden_dimension),
                nn.GELU(),
                nn.Dropout(config.dropout),
                nn.Linear(config.head_hidden_dimension, 1),
            )
        else:
            self.head = nn.Sequential(
                nn.LayerNorm(pooled_features),
                SortedProfileHead(
                    pooled_features,
                    config.output_teeth,
                    init_base=config.profile_init_base,
                    init_steps=config.profile_init_steps
                    if config.profile_init_steps is not None
                    else 0.2,
                    target_mean=config.profile_target_mean,
                    target_scale=config.profile_target_scale,
                ),
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
        output = self.head(encoded.flatten(start_dim=1))
        return output if self.config.output_teeth is not None else output.squeeze(-1)
