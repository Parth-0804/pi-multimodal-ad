"""Small deterministic group assignment used by smoke-test infrastructure."""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import math


def deterministic_group_split(
    group_key: str,
    *,
    seed: int,
    fractions: Mapping[str, float],
) -> str:
    """Assign a complete group to one split using a stable hash.

    This is infrastructure only, not the final PHM split policy from T2.2.
    """

    if not isinstance(group_key, str) or not group_key.strip():
        raise ValueError("group_key must be a non-empty string")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
        raise ValueError("seed must be an integer in [0, 2**32)")
    if not fractions:
        raise ValueError("fractions must not be empty")
    ordered = sorted(fractions.items())
    total = 0.0
    for name, fraction in ordered:
        if not isinstance(name, str) or not name:
            raise ValueError("split names must be non-empty strings")
        if isinstance(fraction, bool) or not isinstance(fraction, (int, float)):
            raise ValueError(f"fraction for {name!r} must be numeric")
        number = float(fraction)
        if not math.isfinite(number) or number <= 0:
            raise ValueError(f"fraction for {name!r} must be finite and positive")
        total += number
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("split fractions must sum to 1.0")
    digest = sha256(f"{seed}:{group_key}".encode("utf-8")).digest()
    position = int.from_bytes(digest[:8], "big") / 2**64
    cumulative = 0.0
    for name, fraction in ordered:
        cumulative += float(fraction)
        if position < cumulative:
            return name
    return ordered[-1][0]
