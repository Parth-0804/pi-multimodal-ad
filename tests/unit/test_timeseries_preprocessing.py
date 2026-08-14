import numpy as np
import pandas as pd

from pi_multimodal_ad.preprocessing.timeseries import (
    fit_feature_normalizer,
    transform_feature_frame,
)


def test_missing_values_use_training_median_not_validation_information() -> None:
    minute = pd.DataFrame(
        {
            "split": ["train", "train", "train", "validation"],
            "sequence_inclusion_status": ["included"] * 4,
            "feature": [1.0, np.nan, 3.0, 10_000.0],
        }
    )
    normalizer = fit_feature_normalizer(minute, feature_columns=["feature"])
    assert normalizer.medians == (2.0,)
    assert normalizer.means == (2.0,)
    transformed = transform_feature_frame(
        pd.DataFrame({"feature": [np.nan, 2.0]}), normalizer
    )
    assert transformed.tolist() == [[0.0], [0.0]]


def test_split_identity_is_not_created_by_the_normalizer() -> None:
    minute = pd.DataFrame(
        {
            "split": ["train", "validation", "test"],
            "sequence_inclusion_status": ["included"] * 3,
            "feature": [1.0, 2.0, 3.0],
        }
    )
    original = minute.split.copy()
    fit_feature_normalizer(minute, feature_columns=["feature"])
    pd.testing.assert_series_equal(minute.split, original)
