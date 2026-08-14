"""Dataset-neutral record contracts used by adapters and later pipelines."""

from .identifiers import deterministic_id
from .records import (
    SCHEMA_VERSION,
    AssetRecord,
    ImageRecord,
    SampleRecord,
    SensorRecord,
    SensorWindowReference,
    TargetRecord,
    record_to_dict,
)
from .validation import ContractValidationError

__all__ = [
    "SCHEMA_VERSION",
    "AssetRecord",
    "ContractValidationError",
    "ImageRecord",
    "SampleRecord",
    "SensorRecord",
    "SensorWindowReference",
    "TargetRecord",
    "deterministic_id",
    "record_to_dict",
]
