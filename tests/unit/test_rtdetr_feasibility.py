from __future__ import annotations

import pandas as pd

from pi_multimodal_ad.models.rtdetr_feasibility import (
    RTDETRFeasibilityOptions,
    select_balanced_images,
)


def _profile() -> pd.DataFrame:
    rows = []
    for experiment in ("EXP-A", "EXP-B", "EXP-F"):
        for index in range(6):
            rows.append(
                {
                    "image_id": f"{experiment}-{index}",
                    "source_member_id": f"member-{experiment}-{index}",
                    "source_relative_path": f"{experiment}/{index}.jpg",
                    "experiment": experiment,
                    "inspection_stage": f"stage-{index % 2}",
                    "image_role": f"role-{index % 3}",
                    "header_status": "ok",
                }
            )
    return pd.DataFrame(rows)


def test_balanced_rtdetr_selection_is_deterministic_and_experiment_balanced() -> None:
    frame = _profile()
    first = select_balanced_images(frame, images_per_experiment=3, seed=7)
    second = select_balanced_images(
        frame.sample(frac=1, random_state=11), images_per_experiment=3, seed=7
    )

    assert first["image_id"].tolist() == second["image_id"].tolist()
    assert first["experiment"].value_counts().to_dict() == {
        "EXP-A": 3,
        "EXP-B": 3,
        "EXP-F": 3,
    }


def test_rtdetr_options_reject_unbounded_or_unpinned_values() -> None:
    try:
        RTDETRFeasibilityOptions(
            seed=1,
            images_per_experiment=0,
            image_size=640,
            confidence_threshold=0.25,
            max_detections=300,
            device="cpu",
            max_member_bytes=1024,
            checkpoint_name="model.pt",
            checkpoint_url="https://example.invalid/model.pt",
            checkpoint_sha256="a" * 64,
            checkpoint_size_bytes=1,
            trace_layers=(),
        )
    except ValueError as exc:
        assert "images_per_experiment" in str(exc)
    else:
        raise AssertionError("expected invalid bounded selection to fail")
