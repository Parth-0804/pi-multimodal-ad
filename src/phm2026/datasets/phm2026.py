"""PHM North America 2026 naming and schema boundary.

This module parses metadata only. It does not open, extract, hash, or modify raw
assets, and it deliberately does not define the unresolved six-hour target.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
from types import MappingProxyType
from typing import NoReturn

from ..data_contracts import ContractValidationError, deterministic_id
from .base import AssetIdentity, BaseDatasetAdapter, ImageSourceIdentity


class UnverifiedTargetSemanticsError(RuntimeError):
    """Raised when code attempts to use the unresolved PHM target contract."""


@dataclass(frozen=True, slots=True)
class PHMPhotoIdentity:
    experiment: str
    run: int | None
    inspection_stage: str
    raw_inspection_stage: str
    tooth_id: str | None
    sequence: int | None
    timestamp: datetime | None


class PHM2026Adapter(BaseDatasetAdapter):
    """PHM-specific normalization that emits dataset-neutral records."""

    dataset_name = "phm2026"
    data_root_name = "gtc-data-experiment"
    supported_runs = MappingProxyType(
        {
            "EXP-A": frozenset(range(1, 6)),
            "EXP-B": frozenset(range(1, 8)),
            "EXP-F": frozenset(range(1, 9)),
        }
    )
    _sensor_aliases = MappingProxyType(
        {
            "vibration": ("/Vibration",),
            "operating_context": ("/Context",),
            "condition_indicator": ("/CI", "/CI_4s"),
            "oil": ("/Oil",),
            "environment": ("/Environment",),
            "timestamp": ("/Timestamp", "/Time"),
        }
    )
    _sensor_role_prefixes = (
        ("/CI_4s", "condition_indicator"),
        ("/Vibration", "vibration"),
        ("/Context", "operating_context"),
        ("/CI", "condition_indicator"),
        ("/Oil", "oil"),
        ("/Environment", "environment"),
        ("/Timestamp", "timestamp"),
        ("/Time", "timestamp"),
    )
    _sensor_attribute_aliases = MappingProxyType(
        {
            "unit": ("unit_string", "NI_UnitDescription", "unit", "units"),
            "sampling_rate": (
                "sampling_rate",
                "sample_rate",
                "samplerate",
                "fs",
                "frequency",
            ),
            "sampling_interval": ("wf_increment",),
            "start_timestamp": ("wf_start_time",),
        }
    )
    _experiment_re = re.compile(
        r"(?<![A-Za-z0-9])EXP[\s_-]*([ABF])(?![A-Za-z0-9])", re.IGNORECASE
    )
    _run_re = re.compile(r"RUN[\s_-]*(\d+)", re.IGNORECASE)
    _tooth_re = re.compile(r"TOOTH[\s_-]*0*(\d+)", re.IGNORECASE)
    _sequence_re = re.compile(
        r"(?:IMAGE|IMG|PHOTO|VIEW|SEQ(?:UENCE)?)[\s_-]*0*(\d+)", re.IGNORECASE
    )
    _canonical_tooth_image_re = re.compile(r"^TOOTH[\s_-]*0*(\d+)$", re.IGNORECASE)
    _win_image_re = re.compile(
        r"^WIN_(\d{8})_(\d{2})_(\d{2})_(\d{2})_PRO(?:\s+\((\d+)\))?$",
        re.IGNORECASE,
    )
    _timestamp_patterns = (
        re.compile(
            r"(?<!\d)(\d{4})-(\d{2})-(\d{2})T(\d{2})[-:](\d{2})[-:](\d{2})Z(?!\d)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?<!\d)(\d{4})(\d{2})(\d{2})[_T](\d{2})(\d{2})(\d{2})Z(?!\d)",
            re.IGNORECASE,
        ),
    )

    @staticmethod
    def _error(field: str, message: str) -> ContractValidationError:
        return ContractValidationError("PHM2026Adapter", field, message)

    @classmethod
    def _dataset_relative_path(cls, value: str | PurePosixPath) -> PurePosixPath:
        text = str(value)
        if not text or text != text.strip():
            raise cls._error("relative_path", "must be a non-empty normalized path")
        if "\\" in text:
            raise cls._error("relative_path", "must use POSIX '/' separators")
        path = PurePosixPath(text)
        if path.is_absolute() or "." in path.parts or ".." in path.parts:
            raise cls._error("relative_path", "must be a safe repository-relative path")
        if path.parts and path.parts[0] == cls.data_root_name:
            path = PurePosixPath(*path.parts[1:])
        if not path.parts:
            raise cls._error(
                "relative_path", "must identify an asset below the data root"
            )
        if "Full Dataset" in path.parts or (
            len(path.parts) >= 2 and path.parts[:2] == ("data", "Full Dataset")
        ):
            raise cls._error(
                "relative_path", "the historical Intel dataset is out of scope"
            )
        if path.as_posix() != str(path):
            raise cls._error("relative_path", "must be normalized")
        return path

    @classmethod
    def _archive_member_path(cls, value: str) -> PurePosixPath:
        if not isinstance(value, str) or not value or value != value.strip():
            raise cls._error("archive_member", "must be a non-empty normalized path")
        if "\\" in value:
            raise cls._error("archive_member", "must use POSIX / separators")
        path = PurePosixPath(value)
        if path.is_absolute() or "." in path.parts or ".." in path.parts:
            raise cls._error("archive_member", "must be a safe relative member path")
        if path.as_posix() != value:
            raise cls._error("archive_member", "must be normalized")
        return path

    def normalize_experiment(self, value: str) -> str:
        if not isinstance(value, str):
            raise self._error("experiment", "must be a string")
        match = self._experiment_re.fullmatch(value.strip())
        if match is None:
            raise self._error(
                "experiment", "must identify one of the in-scope experiments A, B, or F"
            )
        return f"EXP-{match.group(1).upper()}"

    def _experiments_in_text(self, value: str) -> tuple[str, ...]:
        experiments = {
            f"EXP-{match.group(1).upper()}"
            for match in self._experiment_re.finditer(value)
        }
        if not experiments:
            raise self._error("experiment", "no in-scope experiment token was found")
        if len(experiments) > 1:
            raise self._error("experiment", "conflicting experiment tokens were found")
        return tuple(experiments)

    def parse_run(self, value: str) -> int | None:
        if not isinstance(value, str):
            raise self._error("run", "source text must be a string")
        runs = {int(match.group(1)) for match in self._run_re.finditer(value)}
        if not runs:
            return None
        if len(runs) > 1:
            raise self._error("run", "conflicting run tokens were found")
        run = runs.pop()
        if run <= 0:
            raise self._error("run", "run number must be positive")
        return run

    @staticmethod
    def _modality(path: PurePosixPath) -> str:
        root = path.parts[0]
        if root == "high_frequency":
            return "high_frequency"
        if root == "low-frequency (CIs + Oil + Environment)":
            return "low_frequency"
        if root == "low-frequency (CIs)":
            return "condition_indicator"
        if root == "photos":
            return "image"
        raise PHM2026Adapter._error(
            "relative_path", f"unrecognized PHM modality root {root!r}"
        )

    def parse_asset_identity(
        self, relative_path: str | PurePosixPath, *, archive_member: str | None = None
    ) -> AssetIdentity:
        path = self._dataset_relative_path(relative_path)
        modality = self._modality(path)
        experiment = self._experiments_in_text(path.as_posix())[0]
        run = self.parse_run(path.as_posix())
        if run is not None and run not in self.supported_runs[experiment]:
            raise self._error(
                "run", f"run {run} is outside the configured scope for {experiment}"
            )
        if modality == "high_frequency" and run is None:
            raise self._error("run", "high-frequency archives must encode a run number")
        member_path: PurePosixPath | None = None
        if archive_member is not None:
            member_path = self._archive_member_path(archive_member)
            asset_kind = "archive_member"
        elif path.suffix.lower() == ".zip":
            asset_kind = "archive"
        else:
            asset_kind = "file"
        return AssetIdentity(
            relative_path=path,
            modality=modality,
            experiment=experiment,
            run=run,
            asset_kind=asset_kind,
            archive_member=member_path,
        )

    def sensor_path_aliases(self, channel_role: str) -> tuple[str, ...]:
        try:
            return self._sensor_aliases[channel_role]
        except KeyError as exc:
            supported = ", ".join(sorted(self._sensor_aliases))
            raise self._error(
                "channel_role",
                f"unknown role {channel_role!r}; expected one of {supported}",
            ) from exc

    def classify_sensor_path(self, hdf5_path: str) -> str:
        if not isinstance(hdf5_path, str) or not hdf5_path.startswith("/"):
            raise self._error("hdf5_path", "must be an absolute internal HDF5 path")
        for prefix, role in self._sensor_role_prefixes:
            if hdf5_path == prefix or hdf5_path.startswith(f"{prefix}/"):
                return role
        return "unknown"

    def sensor_attribute_aliases(self, field: str) -> tuple[str, ...]:
        try:
            return self._sensor_attribute_aliases[field]
        except KeyError as exc:
            supported = ", ".join(sorted(self._sensor_attribute_aliases))
            raise self._error(
                "sensor_attribute_field",
                f"unknown field {field!r}; expected one of {supported}",
            ) from exc

    def parse_sensor_timestamp(self, value: object) -> datetime | None:
        """Parse only timestamp values carrying an explicit timezone."""

        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError:
                return None
        if not isinstance(value, str):
            return None
        text = value.strip()
        if not text:
            return None
        normalized = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)

    def asset_naming_pattern(self, relative_path: str | PurePosixPath) -> str:
        identity = self.parse_asset_identity(relative_path)
        letter = identity.experiment.removeprefix("EXP-")
        if identity.modality == "high_frequency":
            return f"Exp-{letter}_HDF5_Run-{{run}}.zip"
        if identity.modality == "low_frequency":
            return f"Exp-{letter}_HDF5_LF.zip"
        if identity.modality == "condition_indicator":
            return f"Exp-{letter}_HDF5_CI.zip"
        if identity.run is not None:
            return f"Exp-{letter}_Photos_Run-{{run}}.zip"
        photo = self.parse_photo_identity(relative_path, "unclassified.jpg")
        return f"Exp-{letter}_Photos_{{{photo.inspection_stage}}}.zip"

    def parse_timestamp(self, value: str) -> datetime | None:
        """Parse only explicit UTC timestamp tokens; never infer missing timezone."""

        if not isinstance(value, str):
            raise self._error("timestamp", "source text must be a string")
        for pattern in self._timestamp_patterns:
            match = pattern.search(value)
            if match is None:
                continue
            try:
                parts = tuple(int(part) for part in match.groups())
                return datetime(*parts, tzinfo=timezone.utc)
            except ValueError as exc:
                raise self._error(
                    "timestamp", f"invalid explicit timestamp: {exc}"
                ) from exc
        return None

    def parse_image_identity(
        self,
        relative_path: str | PurePosixPath,
        *,
        archive_member: str | None = None,
    ) -> ImageSourceIdentity:
        asset = self.parse_asset_identity(relative_path, archive_member=archive_member)
        if asset.modality != "image":
            raise self._error("relative_path", "must identify a PHM photo source")
        if archive_member is None:
            raise self._error("archive_member", "is required for an archive image")
        member = self._archive_member_path(archive_member).as_posix()
        archive_stem = asset.relative_path.stem
        marker = re.search(r"_PHOTOS_(.+)$", archive_stem, re.IGNORECASE)
        raw_stage = marker.group(1) if marker is not None else archive_stem
        normalized_stage_text = re.sub(r"[\s_-]+", " ", raw_stage).strip().lower()
        if asset.run is not None:
            stage = "run"
        elif normalized_stage_text == "0 hours test start":
            stage = "test_start"
        elif normalized_stage_text == "pre run":
            stage = "pre_run"
        elif normalized_stage_text == "break in":
            stage = "break_in"
        else:
            stage = "unclassified"
        tooth_matches = {
            int(match.group(1)) for match in self._tooth_re.finditer(member)
        }
        if len(tooth_matches) > 1:
            raise self._error("tooth_id", "conflicting tooth identifiers were found")
        tooth_id = str(tooth_matches.pop()) if tooth_matches else None
        internal_error: str | None = None
        try:
            internal_run = self.parse_run(member)
        except ContractValidationError as exc:
            internal_run = None
            internal_error = str(exc)
        run_conflict = (
            internal_run != asset.run
            if internal_run is not None and asset.run is not None
            else None
        )
        win = re.search(
            r"(?P<raw>WIN_(?P<date>\d{8})_(?P<hour>\d{2})_(?P<minute>\d{2})_"
            r"(?P<second>\d{2})_Pro(?P<copy> \(\d+\))?)",
            PurePosixPath(member).stem,
            re.IGNORECASE,
        )
        timestamp_utc = self.parse_timestamp(member)
        local_naive = None
        timestamp_raw = None
        timestamp_source = None
        timestamp_status = "missing"
        timestamp_clock_domain = None
        timestamp_evidence = None
        raw_sequence = None
        sequence_id = None
        image_role = "canonical_tooth"
        if win is not None:
            timestamp_raw = win.group("raw")
            timestamp_source = "member_filename"
            timestamp_status = "timezone_unknown"
            timestamp_clock_domain = "camera_local_timezone_unknown"
            timestamp_evidence = "WIN_YYYYMMDD_HH_MM_SS_Pro filename token"
            try:
                local_naive = datetime.strptime(
                    f"{win.group('date')}{win.group('hour')}{win.group('minute')}{win.group('second')}",
                    "%Y%m%d%H%M%S",
                )
            except ValueError as exc:
                raise self._error("timestamp", f"invalid WIN timestamp: {exc}") from exc
            raw_sequence = win.group("raw")
            sequence_id = deterministic_id(
                "image_sequence",
                {"archive": asset.relative_path.as_posix(), "token": raw_sequence},
            )
            image_role = "camera_sequence"
            timestamp_utc = None
        elif timestamp_utc is not None:
            timestamp_raw = timestamp_utc.isoformat()
            timestamp_source = "member_filename"
            timestamp_status = "utc_verified"
            timestamp_clock_domain = "UTC"
            timestamp_evidence = "explicit Z filename token"
        inspection_id = deterministic_id(
            "image_inspection", {"archive": asset.relative_path.as_posix()}
        )
        return ImageSourceIdentity(
            experiment=asset.experiment,
            run=asset.run,
            raw_inspection_stage=raw_stage,
            inspection_stage=stage,
            inspection_id=inspection_id,
            inspection_id_source="outer_photo_archive",
            tooth_id=tooth_id,
            image_role=image_role,
            sequence_id=sequence_id,
            raw_sequence_token=raw_sequence,
            timestamp_utc=timestamp_utc,
            timestamp_local_naive=local_naive,
            timestamp_raw=timestamp_raw,
            timestamp_source=timestamp_source,
            timestamp_status=timestamp_status,
            timestamp_clock_domain=timestamp_clock_domain,
            timestamp_evidence=timestamp_evidence,
            internal_run_token=internal_run,
            internal_run_conflict=run_conflict,
            internal_run_parse_error=internal_error,
        )

    def parse_photo_identity(
        self, archive_path: str | PurePosixPath, member_path: str
    ) -> PHMPhotoIdentity:
        identity = self.parse_asset_identity(archive_path)
        if identity.modality != "image":
            raise self._error("archive_path", "must identify a PHM photo archive")
        member = self._archive_member_path(member_path).as_posix()
        archive_stem = identity.relative_path.stem
        marker = re.search(r"_PHOTOS_(.+)$", archive_stem, re.IGNORECASE)
        raw_stage = marker.group(1) if marker is not None else archive_stem
        normalized_stage_text = re.sub(r"[\s_-]+", " ", raw_stage).strip().lower()
        if identity.run is not None:
            stage = "run"
        elif normalized_stage_text == "0 hours test start":
            stage = "test_start"
        elif normalized_stage_text == "pre run":
            stage = "pre_run"
        elif normalized_stage_text == "break in":
            stage = "break_in"
        else:
            stage = "unclassified"
        tooth_matches = {
            int(match.group(1)) for match in self._tooth_re.finditer(member)
        }
        if len(tooth_matches) > 1:
            raise self._error("tooth_id", "conflicting tooth identifiers were found")
        tooth_id = str(tooth_matches.pop()) if tooth_matches else None
        sequence_matches = {
            int(match.group(1)) for match in self._sequence_re.finditer(member)
        }
        if len(sequence_matches) > 1:
            raise self._error(
                "sequence", "conflicting image sequence tokens were found"
            )
        sequence = sequence_matches.pop() if sequence_matches else None
        timestamp = self.parse_timestamp(member)
        if timestamp is None:
            timestamp = self.parse_timestamp(archive_stem)
        return PHMPhotoIdentity(
            experiment=identity.experiment,
            run=identity.run,
            inspection_stage=stage,
            raw_inspection_stage=raw_stage,
            tooth_id=tooth_id,
            sequence=sequence,
            timestamp=timestamp,
        )

    @property
    def target_definition_status(self) -> str:
        return "unverified"

    def require_verified_target_definition(self) -> NoReturn:
        raise UnverifiedTargetSemanticsError(
            "PHM 2026 target semantics are unverified: no target name, physical "
            "meaning, unit, timestamp association, or six-hour interpretation may "
            "be assumed in F0.2"
        )
