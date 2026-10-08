"""Late-fusion routing, shapes and gradient flow."""

from __future__ import annotations

import pytest
import torch

from pi_multimodal_ad.models.late_fusion import (
    SUB_MODALITY_CHANNELS,
    LateFusionRegressor,
    sub_modality_column_indices,
)
from pi_multimodal_ad.models.patchtst import PatchTSTConfig

COLUMNS = [
    f"{base}_{stat}"
    for base in ("rpm", "torque", "temperature", "axial_rms", "radial_rms",
                 "fm4", "na4", "m6a", "alr")
    for stat in ("mean", "std", "median", "min", "max", "last", "slope_per_sample")
] + [
    f"{base}_missing"
    for base in ("rpm", "torque", "temperature", "axial_rms", "radial_rms",
                 "fm4", "na4", "m6a", "alr")
]


def test_sub_modalities_partition_the_feature_columns_exactly():
    seen: set[int] = set()
    for bases in SUB_MODALITY_CHANNELS.values():
        indices = sub_modality_column_indices(COLUMNS, bases)
        assert not seen & set(indices), "sub-modalities must not overlap"
        seen |= set(indices)
    assert len(seen) == len(COLUMNS) == 72


def test_channel_counts_match_the_preregistered_split():
    counts = {
        name: len(sub_modality_column_indices(COLUMNS, bases))
        for name, bases in SUB_MODALITY_CHANNELS.items()
    }
    assert counts == {
        "process_context": 24,
        "organiser_rms": 16,
        "condition_indicators": 32,
    }


def test_prefix_matching_does_not_leak_between_channels():
    """`m6a` must not absorb `m6astar`-style columns from another channel."""

    columns = ["m6a_mean", "m6astar_mean", "m6a_missing"]
    indices = sub_modality_column_indices(columns, ("m6a",))
    assert [columns[i] for i in indices] == ["m6a_mean", "m6a_missing"]


def _model(groups):
    config = PatchTSTConfig(input_channels=72, patch_length=8, patch_stride=4, d_model=16)
    indices = {
        name: sub_modality_column_indices(COLUMNS, SUB_MODALITY_CHANNELS[name])
        for name in groups
    }
    return LateFusionRegressor(config, group_indices=indices), indices


def test_forward_shape_and_head_width():
    model, indices = _model(SUB_MODALITY_CHANNELS)
    assert model.pooled_width == 72 * 16  # same width as a single 72-channel encoder
    inputs = torch.randn(3, 40, 72)
    mask = torch.ones(3, 40, dtype=torch.bool)
    out = model(inputs, mask)
    assert out.shape == (3,)
    assert torch.isfinite(out).all()


def test_single_group_model_only_sees_its_own_channels():
    model, indices = _model(["organiser_rms"])
    assert model.pooled_width == 16 * 16
    model.eval()  # dropout would otherwise make two passes differ for its own reasons
    inputs = torch.randn(2, 32, 72)
    mask = torch.ones(2, 32, dtype=torch.bool)
    with torch.no_grad():
        baseline = model(inputs, mask)
        # perturbing a channel this branch does not consume must not change output
        untouched = inputs.clone()
        untouched[:, :, sub_modality_column_indices(COLUMNS, ("fm4",))] += 99.0
        assert torch.allclose(baseline, model(untouched, mask), atol=1e-6)


def test_padding_is_masked_out():
    model, _ = _model(SUB_MODALITY_CHANNELS)
    model.eval()
    inputs = torch.randn(1, 30, 72)
    mask = torch.ones(1, 30, dtype=torch.bool)
    mask[:, 20:] = False
    with torch.no_grad():
        base = model(inputs, mask)
        changed = inputs.clone()
        changed[:, 20:] = 123.0  # garbage in the padded region
        assert torch.allclose(base, model(changed, mask), atol=1e-5)


def test_gradients_reach_every_branch():
    model, _ = _model(SUB_MODALITY_CHANNELS)
    out = model(torch.randn(2, 40, 72), torch.ones(2, 40, dtype=torch.bool))
    out.sum().backward()
    for name, branch in model.branches.items():
        grads = [p.grad for p in branch.parameters() if p.grad is not None]
        assert grads, f"no gradient reached branch {name}"
        assert any(g.abs().sum() > 0 for g in grads), f"zero gradient in branch {name}"


def test_rejects_empty_group_specification():
    config = PatchTSTConfig(input_channels=72, d_model=16)
    with pytest.raises(ValueError):
        LateFusionRegressor(config, group_indices={})
    with pytest.raises(ValueError):
        LateFusionRegressor(config, group_indices={"empty": []})
