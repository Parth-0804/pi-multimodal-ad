"""Dataset adapter interfaces and implementations."""

from .base import AssetIdentity, BaseDatasetAdapter
from .phm2026 import (
    PHM2026Adapter,
    PHMPhotoIdentity,
    UnverifiedTargetSemanticsError,
)

__all__ = [
    "AssetIdentity",
    "BaseDatasetAdapter",
    "PHM2026Adapter",
    "PHMPhotoIdentity",
    "UnverifiedTargetSemanticsError",
]
