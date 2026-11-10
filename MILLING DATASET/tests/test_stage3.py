"""Scientific contracts and leakage checks with tiny synthetic data only."""
import copy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "MILLING DATASET/source"))

from msm.data import binary_target, interval_statistics, letterbox_rgb, FEATURE_NAMES
from msm.splits import grouped_plan, nested_plan, verify_plan
from msm.models import (MillingVisual, IntervalCNN, SensorClassifier, StaticF2, averaging,
                        fit_visual, predict_visual, metrics, save_bundle, load_bundle)
from msm.experiment import fit_oof_fusion


@pytest.fixture
def config():
    return {"visual": {"learning_rate": .001, "weight_decay": .001, "epochs": 2, "batch_size": 4}}


@pytest.fixture
def synthetic():
    rng = np.random.default_rng(87)
    rows = [{"interval_id": f"g{g}/cut{i}", "group_id": f"g{g}", "target": i % 2} for g in range(8) for i in range(4)]
    return pd.DataFrame(rows), rng.normal(size=(32, 896)).astype(np.float32), rng.normal(size=(32, 18)).astype(np.float32)


def test_native_label2_is_stable_not_abnormal():
    y, keep = binary_target([0, 1, 2])
    assert y.tolist() == [0, 1, 0] and keep.all()
    assert binary_target([0, 1, 2], "exclude")[1].tolist() == [True, True, False]
    with pytest.raises(ValueError):
        binary_target([3])


def test_sensor_half_open_alignment_and_population_statistics():
    table = pd.DataFrame({"time": np.arange(10) / 10, "watt": np.arange(10, dtype=float)})
    values, evidence = interval_statistics(table, .2, .7, ["watt"])
    x = np.arange(2, 7)
    np.testing.assert_allclose(values, [x.mean(), x.std(ddof=0), np.sqrt(np.mean(x*x)), 2, 6, 4], rtol=1e-6)
    assert evidence["rows"] == 5


@pytest.mark.parametrize("failure", ["gap", "nan", "duplicate", "target_channel"])
def test_sensor_rejects_invalid_data_and_target_metadata(failure):
    table = pd.DataFrame({"time": np.arange(10) / 10, "watt": np.arange(10, dtype=float), "label": np.ones(10)})
    channels = ["watt"]
    if failure == "gap":
        table = table.iloc[[0, 1, 2, 8, 9]]
    elif failure == "nan":
        table.loc[2, "watt"] = np.nan
    elif failure == "duplicate":
        table.loc[2, "time"] = .1
    else:
        channels = ["label"]
    with pytest.raises(ValueError):
        interval_statistics(table, 0, 1, channels)


def test_sensor_channel_contract_is_not_reassemble_channel_count():
    t = np.arange(20) / 20
    table = pd.DataFrame({"time": t, "watt": t*2, "smarms": t*3})
    assert interval_statistics(table, 0, 1, ["watt"])[0].shape == (6,)
    assert interval_statistics(table, 0, 1, ["watt", "smarms"])[0].shape == (12,)
    assert len(FEATURE_NAMES) == 90


def test_display_geometry_preserves_portrait_and_rgb_order():
    bgr = np.zeros((480, 720, 3), np.uint8)
    bgr[:, :, 2] = 255
    image = letterbox_rgb(bgr)
    assert image.shape == (640, 640, 3)
    assert np.all(image[:, 140:500, 0] == 255)  # 270/480 * 640 = 360
    assert not image[:, :140].any() and not image[:, 500:].any()
    assert not image[:, :, 1:].any()


class SyntheticBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.scale = nn.Parameter(torch.ones(()))

    def forward(self, pixels):
        x = pixels.mean((1, 2, 3))[:, None, None, None] * self.scale
        return SimpleNamespace(feature_maps=[x.expand(-1, channels, 1, 1) for channels in (128, 256, 512)])


def test_16_frames_forward_one_prediction_per_interval_and_gradient_flow():
    torch.set_num_threads(1)
    encoder = IntervalCNN(SyntheticBackbone(), microbatch=3)
    # Expanded tensors keep the synthetic fixture tiny despite native input shape.
    pixels = torch.arange(16, dtype=torch.float32)[None, :, None, None, None].expand(2, 16, 3, 640, 640)
    pooled = encoder(pixels)
    assert pooled.shape == (2, 896)
    assert torch.equal(pooled, torch.full_like(pooled, 7.5))
    head = MillingVisual()
    before = {n: p.detach().clone() for n, p in head.named_parameters()}
    optimizer = torch.optim.SGD(head.parameters(), lr=.01)
    loss = nn.BCEWithLogitsLoss()(head(pooled), torch.tensor([0., 1.]))
    loss.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in head.parameters())
    assert any(torch.count_nonzero(p.grad) for p in head.parameters())
    optimizer.step()
    assert any(not torch.equal(before[n], p) for n, p in head.named_parameters())
    assert encoder.backbone.scale.grad is None and not encoder.backbone.scale.requires_grad
    assert head(pooled).shape == (2,)
    encoder.train()
    assert not encoder.backbone.training


def test_reject_arbitrary_experiment_frames_or_frame_level_prediction():
    encoder = IntervalCNN(SyntheticBackbone())
    with pytest.raises(ValueError):
        encoder(torch.zeros(1, 15, 3, 32, 32))
    with pytest.raises(ValueError):
        MillingVisual()(torch.zeros(1, 16, 896))


def test_nested_splits_are_group_disjoint_complete_and_both_classes(synthetic):
    frame = synthetic[0]
    outer = nested_plan(frame)
    for part in outer:
        a, b = part["train"], part["test"]
        assert not set(frame.iloc[a].group_id) & set(frame.iloc[b].group_id)
        verify_plan(frame, a, part["inner"])
    assert sorted(i for f in outer for i in f["test"]) == list(range(len(frame)))


def test_current_two_positive_group_structure_fails_full_evaluation():
    frame = pd.DataFrame({"group_id": ["p1", "p2", "n1", "n2", "n3"], "target": [1, 1, 0, 0, 0]})
    with pytest.raises(ValueError, match="Insufficient"):
        nested_plan(frame)


def test_split_validator_rejects_same_experiment_on_both_sides(synthetic):
    frame = synthetic[0]
    a = np.arange(0, 32, 2)
    b = np.arange(1, 32, 2)
    with pytest.raises(ValueError):
        verify_plan(frame, np.arange(32), [(a, b), (b, a)])


def test_oof_stacking_rejects_training_group_probability():
    p = np.array([[.1, .2], [.8, .7]])
    provenance = {"x": {b: {"fit_groups": ["g"]} for b in ("visual", "sensor")},
                  "y": {b: {"fit_groups": ["other"]} for b in ("visual", "sensor")}}
    with pytest.raises(ValueError, match="leakage"):
        StaticF2().fit(p, [0, 1], ["x", "y"], ["g", "h"], provenance)


def test_oof_stacking_rejects_selection_leakage_and_duplicate_units():
    p = np.array([[.1, .2], [.8, .7]])
    entry = {b: {"fit_groups": ["other"], "selection_groups": ["g"]} for b in ("visual", "sensor")}
    provenance = {"x": entry, "y": entry}
    with pytest.raises(ValueError):
        StaticF2().fit(p, [0, 1], ["x", "y"], ["g", "h"], provenance)
    with pytest.raises(ValueError):
        StaticF2().fit(p, [0, 1], ["x", "x"], ["g", "h"], provenance)


def test_real_composition_oof_outer_isolation_and_checkpoint(tmp_path, synthetic, config):
    frame, visual, sensor = synthetic
    outer = nested_plan(frame)[0]
    rows = np.array(outer["train"])
    plan = [(np.array(a), np.array(b)) for a, b in outer["inner"]]
    fit, fusion, bank, provenance, logs = fit_oof_fusion(frame, visual, sensor, rows, plan, config, 42)
    assert np.isnan(bank[outer["test"]]).all() and np.isfinite(bank[rows]).all()
    assert all(item["all_head_parameters_nonzero_gradient"] for item in logs)
    for i in rows:
        assert frame.iloc[i].group_id not in provenance[frame.iloc[i].interval_id]["visual"]["fit_groups"]
    probability = np.column_stack([predict_visual(fit[0], fit[1], visual), fit[2].predict(sensor)])
    path = tmp_path / "synthetic.pt"
    save_bundle(path, *fit[:3], fusion, {"synthetic": True})
    loaded = load_bundle(path)
    actual = np.column_stack([predict_visual(loaded[0], loaded[1], visual), loaded[2].predict(sensor)])
    np.testing.assert_array_equal(probability, actual)
    np.testing.assert_array_equal(fusion.predict(probability), loaded[3].predict(actual))
    assert loaded[4]["synthetic"]


def test_scalers_fit_only_declared_training_rows(synthetic, config):
    frame, visual, sensor = synthetic
    train = np.arange(16)
    visual[16:] = 1e6
    sensor[16:] = -1e6
    _, scaler, _ = fit_visual(visual[train], frame.target.to_numpy()[train], config["visual"], 3)
    fitted = SensorClassifier().fit(sensor[train], frame.target.to_numpy()[train])
    np.testing.assert_array_equal(scaler.mean, visual[train].mean(0))
    np.testing.assert_array_equal(fitted.scaler.mean, sensor[train].mean(0))


def test_outer_labels_cannot_change_fitted_branches_or_stacker(synthetic, config):
    frame, visual, sensor = synthetic
    outer = nested_plan(frame)[0]
    train = np.asarray(outer["train"])
    plan = [(np.asarray(a), np.asarray(b)) for a, b in outer["inner"]]
    original = fit_oof_fusion(frame, visual, sensor, train, plan, config, 42)
    changed = frame.copy()
    changed.loc[outer["test"], "target"] = 1 - changed.loc[outer["test"], "target"]
    repeated = fit_oof_fusion(changed, visual, sensor, train, plan, config, 42)
    np.testing.assert_array_equal(original[2][train], repeated[2][train])
    np.testing.assert_array_equal(original[1].model.coef_, repeated[1].model.coef_)
    for name, value in original[0][0].state_dict().items():
        assert torch.equal(value, repeated[0][0].state_dict()[name])


def test_metrics_on_known_binary_interval_predictions():
    result = metrics([0, 0, 1, 1], [.1, .4, .35, .8])
    assert result["AP"] == pytest.approx(5/6)
    assert result["AUROC"] == pytest.approx(.75)
    assert result["Brier"] == pytest.approx((.01+.16+.4225+.04)/4)
    assert result["balanced_accuracy"] == pytest.approx(.75)
    assert result["F1"] == pytest.approx(2/3)
    assert result["confusion_matrix_tn_fp_fn_tp"] == [2, 0, 1, 1]
    with pytest.raises(ValueError):
        metrics([0, 0], [.2, .3])


def test_averaging_is_nonlearned_and_rejects_missing_branch():
    np.testing.assert_array_equal(averaging([[.2, .8], [.4, .6]]), [.5, .5])
    with pytest.raises(ValueError):
        averaging([[np.nan, .2]])
