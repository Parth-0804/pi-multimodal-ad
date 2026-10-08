"""Canonical, deterministic identifiers for dataset-neutral records."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
import math
from pathlib import PurePath
import re
from typing import Any

_NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _canonicalize(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("deterministic identifiers cannot contain NaN or infinity")
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "deterministic identifiers require timezone-aware datetimes"
            )
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    if isinstance(value, Enum):
        return _canonicalize(value.value)
    if isinstance(value, PurePath):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {
            str(key): _canonicalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_canonicalize(item) for item in value]
    raise TypeError(f"unsupported deterministic-ID value: {type(value).__name__}")


def deterministic_id(namespace: str, identity: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 identifier for a canonical identity mapping."""

    if not _NAMESPACE_RE.fullmatch(namespace):
        raise ValueError(
            "identifier namespace must start with a lowercase letter and contain "
            "only lowercase letters, digits, or underscores"
        )
    payload = json.dumps(
        _canonicalize(identity),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{namespace}_{sha256(payload).hexdigest()}"
