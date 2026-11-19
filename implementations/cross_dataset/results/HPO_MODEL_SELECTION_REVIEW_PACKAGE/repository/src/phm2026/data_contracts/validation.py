"""Validation primitives shared by dataset-neutral record contracts."""

from __future__ import annotations

from datetime import datetime
from pathlib import PurePosixPath
import re
from typing import NoReturn

_TOKEN_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")


class ContractValidationError(ValueError):
    """A field-level contract failure with stable, actionable context."""

    def __init__(self, record_type: str, field: str, message: str) -> None:
        self.record_type = record_type
        self.field = field
        self.message = message
        super().__init__(f"{record_type}.{field}: {message}")


def fail(record_type: str, field: str, message: str) -> NoReturn:
    raise ContractValidationError(record_type, field, message)


def require_text(record_type: str, field: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(record_type, field, "must be a non-empty string")
    if value != value.strip():
        fail(record_type, field, "must not contain leading or trailing whitespace")
    return value


def optional_text(record_type: str, field: str, value: object) -> str | None:
    if value is None:
        return None
    return require_text(record_type, field, value)


def require_token(record_type: str, field: str, value: object) -> str:
    text = require_text(record_type, field, value)
    if not _TOKEN_RE.fullmatch(text):
        fail(
            record_type,
            field,
            "must start with a lowercase letter and contain only lowercase "
            "letters, digits, dots, underscores, or hyphens",
        )
    return text


def require_relative_path(record_type: str, field: str, value: object) -> str:
    text = require_text(record_type, field, value)
    if "\\" in text:
        fail(record_type, field, "must use POSIX '/' separators")
    path = PurePosixPath(text)
    if path.is_absolute():
        fail(record_type, field, "must be relative")
    if "." in path.parts or ".." in path.parts:
        fail(record_type, field, "must not contain '.' or '..' components")
    if path.as_posix() != text:
        fail(record_type, field, "must be normalized")
    return text


def require_hdf5_path(record_type: str, field: str, value: object) -> str:
    text = require_text(record_type, field, value)
    if "\\" in text:
        fail(record_type, field, "must use POSIX '/' separators")
    path = PurePosixPath(text)
    if not path.is_absolute() or text == "/":
        fail(record_type, field, "must be a full internal path below the HDF5 root")
    if "." in path.parts or ".." in path.parts:
        fail(record_type, field, "must not contain '.' or '..' components")
    if path.as_posix() != text:
        fail(record_type, field, "must be normalized")
    return text


def require_aware_datetime(record_type: str, field: str, value: object) -> datetime:
    if not isinstance(value, datetime):
        fail(record_type, field, "must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        fail(record_type, field, "must include an explicit timezone")
    return value


def optional_aware_datetime(
    record_type: str, field: str, value: object
) -> datetime | None:
    if value is None:
        return None
    return require_aware_datetime(record_type, field, value)


def require_schema_version(
    record_type: str, value: object, supported_version: str
) -> str:
    text = require_text(record_type, "schema_version", value)
    if text != supported_version:
        fail(
            record_type,
            "schema_version",
            f"unsupported version {text!r}; expected {supported_version!r}",
        )
    return text
