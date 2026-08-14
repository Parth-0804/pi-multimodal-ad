"""Model-facing utilities; scientific formulations remain configuration-gated."""

from .rtdetr_feasibility import (
    RTDETRFeasibilityOptions,
    RTDETRFeasibilityResult,
    select_balanced_images,
)

__all__ = [
    "RTDETRFeasibilityOptions",
    "RTDETRFeasibilityResult",
    "select_balanced_images",
]
