from __future__ import annotations

import pandas as pd

from pi_multimodal_ad.targets.model_dataset import build_image_samples


def test_experiment_split_is_deterministic_and_leakage_safe() -> None:
    rows = []
    for experiment in ("EXP-A", "EXP-B", "EXP-F"):
        for index in range(2):
            rows.append(
                {
                    "decoding_status": "ok",
                    "run": 1,
                    "experiment": experiment,
                    "target_definition_version": "v",
                    "image_id": f"{experiment}-{index}",
                    "source_member_id": f"m-{experiment}-{index}",
                    "archive_path": "a.zip",
                    "archive_member": f"{index}.jpg",
                    "inspection_id": f"{experiment}-r1",
                    "tooth_id": index + 1,
                    "image_type": "canonical_tooth",
                    "damage_candidate_area_pct": float(index),
                    "pairing_evidence": "synthetic",
                    "near_duplicate_group": f"g-{experiment}",
                }
            )
    samples, split, validation = build_image_samples(
        pd.DataFrame(rows),
        split_config={"train": ["EXP-B"], "validation": ["EXP-A"], "test": ["EXP-F"]},
    )
    assert validation["valid"] is True
    assert validation["counts_by_split"] == {"test": 2, "train": 2, "validation": 2}
    assert split.groupby(["experiment", "run"]).split.nunique().max() == 1
    assert samples.sample_id.is_unique
