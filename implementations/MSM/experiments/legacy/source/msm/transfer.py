"""Strict CNN-only transfer checks; no source-domain head/scaler/fusion reuse."""
from pathlib import Path
import json
import torch
from .data import digest


def compatible_cnn_state(checkpoint_state, target_state):
    """Require every executed CNN tensor, including frozen normalization buffers.

    Phase 1 promoted normalization weight/bias buffers to Parameters. State-dict
    names and shapes are unchanged, so the values map back into frozen buffers.
    Partial last-stage checkpoints, classifier-only fits and detector tensors
    cannot silently stand in for a complete full-backbone source.
    """
    cnn = {name.removeprefix("backbone."): value for name, value in checkpoint_state.items()
           if name.startswith("backbone.")}
    missing = sorted(set(target_state) - set(cnn))
    extra = sorted(set(cnn) - set(target_state))
    if missing or extra:
        raise ValueError(f"Incomplete/incompatible CNN scope: missing={missing}, extra={extra}")
    for name, expected in target_state.items():
        actual = cnn[name]
        if not torch.is_tensor(actual) or actual.shape != expected.shape or actual.dtype != expected.dtype:
            raise ValueError("CNN tensor shape/dtype mismatch: " + name)
        if not bool(torch.isfinite(actual).all()):
            raise ValueError("Nonfinite CNN tensor: " + name)
    excluded = sorted(name for name in checkpoint_state if not name.startswith("backbone."))
    return cnn, excluded


def validated_source(folder, seed, job_index):
    """Accept only a completed, hash-verified C fit with a stable selected model."""
    folder = Path(folder)
    receipt_path = folder / "PHASE1_FIT_COMPLETE.json"
    checkpoint_path = folder / "PHASE1_BEST_MODEL.pt"
    if not receipt_path.is_file():
        raise ValueError("No completed-fit receipt; active/preflight checkpoint is inadmissible")
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("arm") != "C_full_finetuned16" or receipt.get("seed") != seed or receipt.get("job_index") != job_index:
        raise ValueError("Wrong source arm, seed, or predefined source role")
    if not checkpoint_path.is_file() or digest(checkpoint_path) != receipt.get("selected_model_sha256"):
        raise ValueError("Selected source checkpoint missing/hash mismatch")
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if payload.get("arm") != receipt["arm"] or payload.get("seed") != seed or payload.get("fit_identity") != receipt.get("fit_identity"):
        raise ValueError("Checkpoint/receipt provenance mismatch")
    if payload.get("selected_epoch") != receipt.get("best", {}).get("epoch") or receipt.get("executed_epochs", 0) < 25:
        raise ValueError("Source selection/completion boundary mismatch")
    if digest(checkpoint_path) != receipt["selected_model_sha256"]:
        raise ValueError("Source checkpoint changed during read")
    return payload, receipt


def transfer_completed_cnn(backbone, folder, seed, job_index):
    """Mutate only the supplied NEW MSM backbone after full source validation."""
    payload, receipt = validated_source(folder, seed, job_index)
    state, excluded = compatible_cnn_state(payload["model"], backbone.state_dict())
    backbone.load_state_dict(state, strict=True)
    backbone.requires_grad_(False)
    backbone.eval()
    return {"source_checkpoint_sha256": receipt["selected_model_sha256"],
            "source_fit_identity": receipt["fit_identity"], "source_seed": seed,
            "source_job_index": job_index, "selected_epoch": payload["selected_epoch"],
            "cnn_tensor_count": len(state), "excluded_keys": excluded,
            "all_cnn_parameters_frozen": all(not parameter.requires_grad for parameter in backbone.parameters())}
