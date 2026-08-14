"""Bounded, read-only access to ordinary and nested ZIP members.

The helpers in this module never call :meth:`zipfile.ZipFile.extract`.  A
payload that needs a seekable file is streamed into a uniquely named temporary
directory and removed when its context exits.  Nested archives are
materialized one level at a time; only the current nested ZIP and current
payload can coexist on disk.
"""

from __future__ import annotations

from collections.abc import Collection, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile

ARCHIVE_IO_SCHEMA_VERSION = "1.0.0"


class ArchiveMaterializationError(OSError):
    """A bounded archive read failed before a seekable payload was available."""


@dataclass(frozen=True, slots=True)
class ArchiveEntry:
    """Central-directory metadata for one file member."""

    member_path: str
    compressed_size_bytes: int
    uncompressed_size_bytes: int
    crc32: str
    compression_method: int
    encrypted: bool


@dataclass(frozen=True, slots=True)
class ArchiveMemberRef:
    """Identity of a direct ZIP member or a member inside one nested ZIP.

    ``member_path`` always names a member of ``archive_path``.  For a direct
    payload it is the payload itself.  For a nested payload it names the inner
    ZIP and ``nested_member_path`` names the payload within that ZIP.
    """

    archive_path: Path
    archive_relative_path: str
    member_path: str
    nested_member_path: str | None = None
    member_occurrence: int = 1
    nested_member_occurrence: int = 1
    expected_compressed_size_bytes: int | None = None
    expected_uncompressed_size_bytes: int | None = None
    expected_crc32: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "archive_path", Path(self.archive_path))
        if not self.archive_relative_path or self.archive_relative_path.isspace():
            raise ValueError("archive_relative_path must be non-empty")
        if not self.member_path or self.member_path.endswith("/"):
            raise ValueError("member_path must identify a file member")
        if self.nested_member_path is not None and (
            not self.nested_member_path or self.nested_member_path.endswith("/")
        ):
            raise ValueError("nested_member_path must identify a file member")
        for field_name, value in (
            ("member_occurrence", self.member_occurrence),
            ("nested_member_occurrence", self.nested_member_occurrence),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field_name} must be a positive integer")
        for field_name, value in (
            ("expected_compressed_size_bytes", self.expected_compressed_size_bytes),
            (
                "expected_uncompressed_size_bytes",
                self.expected_uncompressed_size_bytes,
            ),
        ):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                raise ValueError(f"{field_name} must be non-negative or null")
        if self.expected_crc32 is not None:
            normalized = self.expected_crc32.lower()
            if len(normalized) != 8 or any(
                character not in "0123456789abcdef" for character in normalized
            ):
                raise ValueError("expected_crc32 must contain eight hexadecimal digits")
            object.__setattr__(self, "expected_crc32", normalized)

    @property
    def payload_member_path(self) -> str:
        return self.nested_member_path or self.member_path

    @property
    def is_nested(self) -> bool:
        return self.nested_member_path is not None

    @property
    def is_nested_archive_container(self) -> bool:
        return (
            self.nested_member_path is None
            and PurePosixPath(self.member_path).suffix.lower() == ".zip"
        )


@dataclass(frozen=True, slots=True)
class MaterializedArchiveMember:
    """A temporary payload yielded while its containing generator is active."""

    reference: ArchiveMemberRef
    path: Path | None
    bytes_written: int
    error: str | None = None


def _positive_integer(value: int, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _find_info(
    archive: zipfile.ZipFile, member_path: str, occurrence: int
) -> zipfile.ZipInfo:
    matches = [info for info in archive.infolist() if info.filename == member_path]
    if len(matches) < occurrence:
        detail = f" occurrence {occurrence}" if occurrence != 1 or matches else ""
        raise ArchiveMaterializationError(
            f"ZIP member not found{detail}: {member_path!r}"
        )
    info = matches[occurrence - 1]
    if info.is_dir():
        raise ArchiveMaterializationError(
            f"ZIP member is a directory, not a payload: {member_path!r}"
        )
    return info


def _check_member_size(
    info: zipfile.ZipInfo,
    *,
    max_member_bytes: int | None,
    expected_uncompressed_size_bytes: int | None,
    expected_compressed_size_bytes: int | None = None,
) -> None:
    if max_member_bytes is not None and info.file_size > max_member_bytes:
        raise ArchiveMaterializationError(
            f"member {info.filename!r} declares {info.file_size} bytes, exceeding "
            f"the configured {max_member_bytes}-byte limit"
        )
    if (
        expected_compressed_size_bytes is not None
        and info.compress_size != expected_compressed_size_bytes
    ):
        raise ArchiveMaterializationError(
            f"member {info.filename!r} declares {info.compress_size} compressed bytes; "
            f"expected {expected_compressed_size_bytes}"
        )
    if (
        expected_uncompressed_size_bytes is not None
        and info.file_size != expected_uncompressed_size_bytes
    ):
        raise ArchiveMaterializationError(
            f"member {info.filename!r} declares {info.file_size} bytes; expected "
            f"{expected_uncompressed_size_bytes}"
        )


def _copy_info(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    destination: Path,
    *,
    copy_chunk_bytes: int,
    max_member_bytes: int | None,
    expected_uncompressed_size_bytes: int | None = None,
    expected_compressed_size_bytes: int | None = None,
    expected_crc32: str | None = None,
) -> int:
    _check_member_size(
        info,
        max_member_bytes=max_member_bytes,
        expected_uncompressed_size_bytes=expected_uncompressed_size_bytes,
        expected_compressed_size_bytes=expected_compressed_size_bytes,
    )
    if info.flag_bits & 0x1:
        raise ArchiveMaterializationError(
            f"encrypted ZIP member is not supported: {info.filename!r}"
        )
    actual_crc32 = f"{info.CRC:08x}"
    if expected_crc32 is not None and actual_crc32 != expected_crc32.lower():
        raise ArchiveMaterializationError(
            f"member {info.filename!r} has CRC32 {actual_crc32}; expected "
            f"{expected_crc32.lower()}"
        )
    written = 0
    try:
        with archive.open(info, mode="r") as source, destination.open("xb") as target:
            while True:
                block = source.read(copy_chunk_bytes)
                if not block:
                    break
                target.write(block)
                written += len(block)
                if max_member_bytes is not None and written > max_member_bytes:
                    raise ArchiveMaterializationError(
                        f"member {info.filename!r} exceeded the configured "
                        f"{max_member_bytes}-byte limit while streaming"
                    )
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        destination.unlink(missing_ok=True)
        if isinstance(exc, ArchiveMaterializationError):
            raise
        raise ArchiveMaterializationError(
            f"failed to stream ZIP member {info.filename!r}: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    if written != info.file_size:
        destination.unlink(missing_ok=True)
        raise ArchiveMaterializationError(
            f"member {info.filename!r} produced {written} bytes; central directory "
            f"declares {info.file_size}"
        )
    return written


def _payload_suffix(member_path: str) -> str:
    suffix = PurePosixPath(member_path).suffix
    if not suffix or len(suffix) > 16:
        return ".bin"
    return suffix.lower()


@contextmanager
def materialize_archive_member(
    reference: ArchiveMemberRef,
    *,
    temp_root: Path | None = None,
    max_member_bytes: int | None = None,
    copy_chunk_bytes: int = 8 * 1024 * 1024,
) -> Iterator[Path]:
    """Yield one seekable payload and remove all temporary files afterwards."""

    _positive_integer(copy_chunk_bytes, field="copy_chunk_bytes")
    if max_member_bytes is not None:
        _positive_integer(max_member_bytes, field="max_member_bytes")
    temporary_parent = Path(temp_root) if temp_root is not None else None
    with tempfile.TemporaryDirectory(
        prefix="pi_multimodal_archive_", dir=temporary_parent
    ) as temporary_name:
        temporary_directory = Path(temporary_name)
        try:
            with zipfile.ZipFile(
                reference.archive_path, mode="r", allowZip64=True
            ) as outer_archive:
                outer_info = _find_info(
                    outer_archive, reference.member_path, reference.member_occurrence
                )
                if not reference.is_nested:
                    target = temporary_directory / (
                        "payload" + _payload_suffix(reference.member_path)
                    )
                    _copy_info(
                        outer_archive,
                        outer_info,
                        target,
                        copy_chunk_bytes=copy_chunk_bytes,
                        max_member_bytes=max_member_bytes,
                        expected_uncompressed_size_bytes=(
                            reference.expected_uncompressed_size_bytes
                        ),
                        expected_compressed_size_bytes=(
                            reference.expected_compressed_size_bytes
                        ),
                        expected_crc32=reference.expected_crc32,
                    )
                    yield target
                    return

                nested_archive_path = temporary_directory / "nested.zip"
                _copy_info(
                    outer_archive,
                    outer_info,
                    nested_archive_path,
                    copy_chunk_bytes=copy_chunk_bytes,
                    max_member_bytes=max_member_bytes,
                )
            with zipfile.ZipFile(
                nested_archive_path, mode="r", allowZip64=True
            ) as nested_archive:
                nested_info = _find_info(
                    nested_archive,
                    reference.nested_member_path or "",
                    reference.nested_member_occurrence,
                )
                target = temporary_directory / (
                    "payload" + _payload_suffix(reference.payload_member_path)
                )
                _copy_info(
                    nested_archive,
                    nested_info,
                    target,
                    copy_chunk_bytes=copy_chunk_bytes,
                    max_member_bytes=max_member_bytes,
                    expected_uncompressed_size_bytes=(
                        reference.expected_uncompressed_size_bytes
                    ),
                    expected_crc32=reference.expected_crc32,
                )
            nested_archive_path.unlink(missing_ok=True)
            yield target
        except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            if isinstance(exc, ArchiveMaterializationError):
                raise
            raise ArchiveMaterializationError(
                f"failed to materialize {reference.archive_relative_path!r} / "
                f"{reference.payload_member_path!r}: {type(exc).__name__}: {exc}"
            ) from exc


def list_nested_archive_entries(
    container: ArchiveMemberRef,
    *,
    suffixes: Collection[str] | None = None,
    temp_root: Path | None = None,
    max_member_bytes: int | None = None,
    copy_chunk_bytes: int = 8 * 1024 * 1024,
) -> tuple[ArchiveEntry, ...]:
    """Return central-directory file entries from one nested ZIP member."""

    if container.nested_member_path is not None:
        raise ValueError("container must identify the nested ZIP, not its payload")
    normalized_suffixes = (
        {suffix.lower() for suffix in suffixes} if suffixes is not None else None
    )
    with materialize_archive_member(
        container,
        temp_root=temp_root,
        max_member_bytes=max_member_bytes,
        copy_chunk_bytes=copy_chunk_bytes,
    ) as nested_path:
        try:
            with zipfile.ZipFile(nested_path, mode="r", allowZip64=True) as archive:
                entries = []
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    if normalized_suffixes is not None and (
                        PurePosixPath(info.filename).suffix.lower()
                        not in normalized_suffixes
                    ):
                        continue
                    entries.append(
                        ArchiveEntry(
                            member_path=info.filename,
                            compressed_size_bytes=info.compress_size,
                            uncompressed_size_bytes=info.file_size,
                            crc32=f"{info.CRC:08x}",
                            compression_method=info.compress_type,
                            encrypted=bool(info.flag_bits & 0x1),
                        )
                    )
        except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            raise ArchiveMaterializationError(
                f"nested member {container.member_path!r} is not a readable ZIP: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
    return tuple(sorted(entries, key=lambda entry: entry.member_path))


def iter_materialized_nested_members(
    container: ArchiveMemberRef,
    *,
    suffixes: Collection[str],
    temp_root: Path | None = None,
    max_member_bytes: int | None = None,
    copy_chunk_bytes: int = 8 * 1024 * 1024,
) -> Iterator[MaterializedArchiveMember]:
    """Yield nested payloads sequentially while materializing the inner ZIP once.

    A corrupt or encrypted payload is yielded with ``path=None`` and an error,
    allowing callers to record that member and continue with later members.
    """

    if container.nested_member_path is not None:
        raise ValueError("container must identify the nested ZIP, not its payload")
    normalized_suffixes = {suffix.lower() for suffix in suffixes}
    with materialize_archive_member(
        container,
        temp_root=temp_root,
        max_member_bytes=max_member_bytes,
        copy_chunk_bytes=copy_chunk_bytes,
    ) as nested_path:
        try:
            nested_archive = zipfile.ZipFile(nested_path, mode="r", allowZip64=True)
        except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            raise ArchiveMaterializationError(
                f"nested member {container.member_path!r} is not a readable ZIP: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        with nested_archive:
            occurrences: dict[str, int] = {}
            entries = [
                info
                for info in nested_archive.infolist()
                if not info.is_dir()
                and PurePosixPath(info.filename).suffix.lower() in normalized_suffixes
            ]
            entries.sort(key=lambda info: info.filename)
            for index, info in enumerate(entries):
                occurrence = occurrences.get(info.filename, 0) + 1
                occurrences[info.filename] = occurrence
                reference = replace(
                    container,
                    nested_member_path=info.filename,
                    nested_member_occurrence=occurrence,
                    expected_compressed_size_bytes=info.compress_size,
                    expected_uncompressed_size_bytes=info.file_size,
                    expected_crc32=f"{info.CRC:08x}",
                )
                target = nested_path.parent / (
                    f"payload-{index}" + _payload_suffix(info.filename)
                )
                try:
                    written = _copy_info(
                        nested_archive,
                        info,
                        target,
                        copy_chunk_bytes=copy_chunk_bytes,
                        max_member_bytes=max_member_bytes,
                        expected_uncompressed_size_bytes=info.file_size,
                        expected_crc32=f"{info.CRC:08x}",
                    )
                except (ArchiveMaterializationError, OSError) as exc:
                    target.unlink(missing_ok=True)
                    yield MaterializedArchiveMember(
                        reference=reference,
                        path=None,
                        bytes_written=0,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                    continue
                try:
                    yield MaterializedArchiveMember(
                        reference=reference,
                        path=target,
                        bytes_written=written,
                    )
                finally:
                    target.unlink(missing_ok=True)
