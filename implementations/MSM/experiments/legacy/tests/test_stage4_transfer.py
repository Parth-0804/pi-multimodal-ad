"""Tiny synthetic full-CNN transfer and source-provenance regression checks."""
import copy
import json
import sys
from pathlib import Path
import pytest
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "MILLING DATASET/source"))
from msm.data import digest
from msm.transfer import compatible_cnn_state, validated_source, transfer_completed_cnn


class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 2, 1)
        self.register_buffer("running_mean", torch.zeros(2))


def payload(model):
    state = {"backbone." + name: value.detach().clone() + 1 for name, value in model.state_dict().items()}
    state["head.classifier.weight"] = torch.full((1, 2), 900.)
    state["mean"] = torch.full((2,), 800.)
    state["std"] = torch.full((2,), 700.)
    return {"model": state, "arm": "C_full_finetuned16", "seed": 42,
            "fit_identity": "synthetic_only", "selected_epoch": 7}


def complete(folder, value):
    torch.save(value, folder / "PHASE1_BEST_MODEL.pt")
    receipt = {"arm": "C_full_finetuned16", "seed": 42, "job_index": 4, "best": {"epoch": 7},
               "executed_epochs": 25, "fit_identity": "synthetic_only",
               "selected_model_sha256": digest(folder / "PHASE1_BEST_MODEL.pt")}
    (folder / "PHASE1_FIT_COMPLETE.json").write_text(json.dumps(receipt))
    return receipt


def test_full_cnn_transfer_excludes_failure_head_and_source_scalers(tmp_path):
    model = TinyCNN()
    original = {key: value.clone() for key, value in model.state_dict().items()}
    value = payload(model)
    complete(tmp_path, value)
    info = transfer_completed_cnn(model, tmp_path, 42, 4)
    assert info["cnn_tensor_count"] == 3
    assert set(info["excluded_keys"]) == {"head.classifier.weight", "mean", "std"}
    assert all(not p.requires_grad for p in model.parameters()) and not model.training
    for name, tensor in model.state_dict().items():
        assert torch.equal(tensor, original[name] + 1)


@pytest.mark.parametrize("failure", ["partial", "detector", "shape", "dtype", "nonfinite", "head_only"])
def test_reject_incomplete_wrong_or_nonfinite_cnn(failure):
    model = TinyCNN()
    state = payload(model)["model"]
    if failure == "partial":
        state.pop("backbone.running_mean")
    elif failure == "detector":
        state["backbone.decoder.weight"] = torch.ones(1)
    elif failure == "shape":
        state["backbone.conv.weight"] = torch.ones(10)
    elif failure == "dtype":
        state["backbone.conv.weight"] = state["backbone.conv.weight"].double()
    elif failure == "nonfinite":
        state["backbone.conv.bias"][0] = float("nan")
    else:
        state = {"head.weight": torch.ones(1)}
    with pytest.raises(ValueError):
        compatible_cnn_state(state, model.state_dict())


def test_reject_active_or_preflight_checkpoint_without_completion(tmp_path):
    torch.save(payload(TinyCNN()), tmp_path / "PHASE1_BEST_MODEL.pt")
    with pytest.raises(ValueError, match="completed-fit"):
        validated_source(tmp_path, 42, 4)


@pytest.mark.parametrize("failure", ["B_arm", "seed", "role", "hash", "identity", "epoch", "incomplete"])
def test_require_source_receipt_and_checkpoint_consistency(tmp_path, failure):
    value = payload(TinyCNN())
    if failure == "identity":
        value["fit_identity"] = "wrong"
    receipt = complete(tmp_path, value)
    if failure == "B_arm":
        receipt["arm"] = "B_long_frozen16"
    elif failure == "seed":
        receipt["seed"] = 123
    elif failure == "role":
        receipt["job_index"] = 0
    elif failure == "hash":
        receipt["selected_model_sha256"] = "0" * 64
    elif failure == "epoch":
        receipt["best"]["epoch"] = 8
    elif failure == "incomplete":
        receipt["executed_epochs"] = 5
    (tmp_path / "PHASE1_FIT_COMPLETE.json").write_text(json.dumps(receipt))
    before = {name: tensor.clone() for name, tensor in value["model"].items()}
    with pytest.raises(ValueError):
        validated_source(tmp_path, 42, 4)
    for name in before:
        assert torch.equal(before[name], value["model"][name])
