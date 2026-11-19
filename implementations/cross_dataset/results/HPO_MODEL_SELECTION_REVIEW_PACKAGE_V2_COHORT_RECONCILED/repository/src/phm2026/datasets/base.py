"""Dataset-neutral adapter boundary."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath

from ..data_contracts import AssetRecord


@dataclass(frozen=True, slots=True)
class AssetIdentity:
    """Normalized identity returned by a dataset adapter for one source asset."""

    relative_path: PurePosixPath
    modality: str
    experiment: str
    run: int | None
    asset_kind: str
    archive_member: PurePosixPath | None = None


@dataclass(frozen=True, slots=True)
class ImageSourceIdentity:
    """Dataset-neutral semantic identity for one source image.

    Timestamps remain separated by evidence quality.  ``timestamp_utc`` is
    reserved for timezone-aware evidence, while ``timestamp_local_naive`` may
    retain a filename time whose timezone is unknown.  Implementations must
    not promote archive ordering or filesystem/ZIP modification times to an
    acquisition timestamp.
    """

    experiment: str
    run: int | None
    raw_inspection_stage: str | None
    inspection_stage: str
    inspection_id: str
    inspection_id_source: str
    tooth_id: str | None
    image_role: str
    sequence_id: str | None
    raw_sequence_token: str | None
    timestamp_utc: datetime | None
    timestamp_local_naive: datetime | None
    timestamp_raw: str | None
    timestamp_source: str | None
    timestamp_status: str
    timestamp_clock_domain: str | None
    timestamp_evidence: str | None
    internal_run_token: int | None
    internal_run_conflict: bool | None
    internal_run_parse_error: str | None

    def __post_init__(self) -> None:
        if self.timestamp_utc is not None and (
            self.timestamp_utc.tzinfo is None or self.timestamp_utc.utcoffset() is None
        ):
            raise ValueError("timestamp_utc must be timezone-aware")
        if self.timestamp_local_naive is not None and (
            self.timestamp_local_naive.tzinfo is not None
            or self.timestamp_local_naive.utcoffset() is not None
        ):
            raise ValueError("timestamp_local_naive must not carry a timezone")
        if self.timestamp_utc is not None and self.timestamp_local_naive is not None:
            raise ValueError(
                "UTC and timezone-unknown timestamps are mutually exclusive"
            )


class BaseDatasetAdapter(ABC):
    """Minimum boundary required by future generic profiling code."""

    dataset_name: str

    @abstractmethod
    def normalize_experiment(self, value: str) -> str:
        """Normalize a source experiment label or raise a validation error."""

    @abstractmethod
    def parse_run(self, value: str) -> int | None:
        """Return an explicitly encoded run number, otherwise null."""

    @abstractmethod
    def parse_asset_identity(
        self, relative_path: str | PurePosixPath, *, archive_member: str | None = None
    ) -> AssetIdentity:
        """Parse dataset-relative storage identity without opening the asset."""

    @abstractmethod
    def sensor_path_aliases(self, channel_role: str) -> tuple[str, ...]:
        """Return dataset-specific internal paths for a canonical sensor role."""

    @abstractmethod
    def asset_naming_pattern(self, relative_path: str | PurePosixPath) -> str:
        """Return the dataset-specific normalized naming family for an asset."""

    @abstractmethod
    def parse_image_identity(
        self,
        relative_path: str | PurePosixPath,
        *,
        archive_member: str | None = None,
    ) -> ImageSourceIdentity:
        """Parse image grouping and filename semantics without reading pixels."""

    def classify_sensor_path(self, hdf5_path: str) -> str:
        """Map one internal HDF5 path to a canonical role.

        Dataset-neutral profilers call this hook and preserve unknown paths.
        """

        return "unknown"

    def sensor_attribute_aliases(self, field: str) -> tuple[str, ...]:
        """Return adapter-owned HDF5 attribute aliases for a semantic field."""

        return ()

    def parse_sensor_timestamp(self, value: object) -> datetime | None:
        """Parse an evidenced, timezone-aware sensor timestamp or return null."""

        return None

    def make_asset_record(
        self,
        relative_path: str | PurePosixPath,
        *,
        archive_member: str | None = None,
        size_bytes: int | None = None,
        uncompressed_size_bytes: int | None = None,
        checksum_algorithm: str | None = None,
        checksum: str | None = None,
    ) -> AssetRecord:
        """Create a generic AssetRecord from adapter-owned parsing rules."""

        identity = self.parse_asset_identity(
            relative_path, archive_member=archive_member
        )
        return AssetRecord(
            dataset=self.dataset_name,
            relative_path=identity.relative_path.as_posix(),
            asset_kind=identity.asset_kind,  # type: ignore[arg-type]
            modality=identity.modality,
            experiment=identity.experiment,
            run=identity.run,
            archive_member=(
                identity.archive_member.as_posix()
                if identity.archive_member is not None
                else None
            ),
            size_bytes=size_bytes,
            uncompressed_size_bytes=uncompressed_size_bytes,
            checksum_algorithm=checksum_algorithm,
            checksum=checksum,
        )
