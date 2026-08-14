from __future__ import annotations

import torch

from pi_multimodal_ad.models.patchtst import PatchTSTConfig, PatchTSTRegressor


def test_patch_shapes_masked_pooling_and_output() -> None:
    torch.manual_seed(7)
    config = PatchTSTConfig(
        input_channels=3,
        patch_length=4,
        patch_stride=2,
        d_model=8,
        n_heads=2,
        encoder_layers=1,
        feedforward_dimension=16,
        dropout=0.0,
        head_hidden_dimension=8,
    )
    model = PatchTSTRegressor(config).eval()
    inputs = torch.randn(2, 7, 3)
    mask = torch.tensor([[True] * 7, [True] * 5 + [False] * 2])
    patches, patch_mask = model.patchify(inputs, mask)
    assert patches.shape == (2, 3, 3, 4)
    assert patch_mask.shape == (2, 3)
    output = model(inputs, mask)
    assert output.shape == (2,)
    changed = inputs.clone()
    changed[1, 5:] = 99_999
    assert torch.allclose(output[1], model(changed, mask)[1], atol=1e-6)


def test_gradients_optimizer_and_deterministic_inference() -> None:
    torch.manual_seed(11)
    model = PatchTSTRegressor(
        PatchTSTConfig(
            input_channels=2,
            patch_length=3,
            patch_stride=2,
            d_model=8,
            n_heads=2,
            encoder_layers=1,
            feedforward_dimension=16,
            dropout=0.0,
            head_hidden_dimension=8,
        )
    )
    values = torch.randn(3, 6, 2)
    mask = torch.ones(3, 6, dtype=torch.bool)
    target = torch.tensor([1.0, 2.0, 3.0])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    optimizer.zero_grad()
    prediction = model(values, mask)
    loss = torch.nn.functional.mse_loss(prediction, target)
    loss.backward()
    assert model.patch_projection.weight.grad is not None
    assert model.head[-1].weight.grad is not None
    optimizer.step()
    model.eval()
    with torch.no_grad():
        first = model(values, mask)
        second = model(values, mask)
    assert torch.equal(first, second)
