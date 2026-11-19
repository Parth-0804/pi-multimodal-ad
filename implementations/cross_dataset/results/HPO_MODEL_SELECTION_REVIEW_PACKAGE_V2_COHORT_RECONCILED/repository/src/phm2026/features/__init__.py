"""Compact, traceable feature extraction."""

from .sensor_minutes import (
    CHANNEL_STATISTICS,
    SENSOR_FEATURE_SCHEMA_VERSION,
    ChannelSpec,
    ExtractionOptions,
    extract_minute_features,
    feature_columns,
    summarize_feature_run,
)

__all__ = [
    "CHANNEL_STATISTICS",
    "SENSOR_FEATURE_SCHEMA_VERSION",
    "ChannelSpec",
    "ExtractionOptions",
    "extract_minute_features",
    "feature_columns",
    "summarize_feature_run",
]
