"""Best-effort deterministic seed handling with an auditable report."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import random
from typing import Any


@dataclass(frozen=True, slots=True)
class SeedReport:
    seed: int
    python_seeded: bool
    numpy_seeded: bool
    torch_seeded: bool
    torch_deterministic_algorithms: bool


def set_reproducible_seed(seed: int) -> SeedReport:
    """Seed Python, NumPy, and PyTorch when installed without requiring either."""

    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
        raise ValueError("seed must be an integer in [0, 2**32)")
    random.seed(seed)
    numpy_seeded = False
    torch_seeded = False
    torch_deterministic = False
    try:
        numpy: Any = importlib.import_module("numpy")
    except ImportError:
        pass
    else:
        numpy.random.seed(seed)
        numpy_seeded = True
    try:
        torch: Any = importlib.import_module("torch")
    except ImportError:
        pass
    else:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
        except (AttributeError, RuntimeError):
            torch_deterministic = False
        else:
            torch_deterministic = True
        torch_seeded = True
    return SeedReport(
        seed=seed,
        python_seeded=True,
        numpy_seeded=numpy_seeded,
        torch_seeded=torch_seeded,
        torch_deterministic_algorithms=torch_deterministic,
    )
