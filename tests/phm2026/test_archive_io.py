from __future__ import annotations

from pathlib import Path
import zipfile

import pytest

from pi_multimodal_ad.profiling.archive_io import (
    ArchiveMaterializationError,
    ArchiveMemberRef,
    iter_materialized_nested_members,
    list_nested_archive_entries,
    materialize_archive_member,
)


def _zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)


def test_direct_member_is_streamed_and_temporary_directory_is_cleaned(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "outer.zip"
    _zip(archive, {"signals/member.h5": b"synthetic-hdf"})
    reference = ArchiveMemberRef(
        archive_path=archive,
        archive_relative_path="synthetic/outer.zip",
        member_path="signals/member.h5",
        expected_uncompressed_size_bytes=len(b"synthetic-hdf"),
    )
    temporary_path: Path
    with materialize_archive_member(reference, temp_root=tmp_path) as temporary_path:
        temporary_directory = temporary_path.parent
        assert temporary_path.read_bytes() == b"synthetic-hdf"
        assert temporary_directory.is_dir()
    assert not temporary_directory.exists()


def test_nested_members_are_listed_and_streamed_one_at_a_time(tmp_path: Path) -> None:
    inner = tmp_path / "inner.zip"
    _zip(inner, {"a.h5": b"first", "nested/b.hdf5": b"second", "ignore.txt": b"x"})
    outer = tmp_path / "outer.zip"
    _zip(outer, {"run-1.zip": inner.read_bytes()})
    container = ArchiveMemberRef(
        archive_path=outer,
        archive_relative_path="synthetic/outer.zip",
        member_path="run-1.zip",
    )
    entries = list_nested_archive_entries(
        container, suffixes={".h5", ".hdf5"}, temp_root=tmp_path
    )
    assert [entry.member_path for entry in entries] == ["a.h5", "nested/b.hdf5"]
    yielded = []
    parents: list[Path] = []
    for item in iter_materialized_nested_members(
        container,
        suffixes={".h5", ".hdf5"},
        temp_root=tmp_path,
    ):
        assert item.error is None
        assert item.path is not None
        yielded.append((item.reference.nested_member_path, item.path.read_bytes()))
        parents.append(item.path.parent)
    assert yielded == [("a.h5", b"first"), ("nested/b.hdf5", b"second")]
    assert all(not parent.exists() for parent in parents)


def test_member_size_guard_fails_without_leaving_temporary_files(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "outer.zip"
    _zip(archive, {"large.h5": b"12345"})
    reference = ArchiveMemberRef(
        archive_path=archive,
        archive_relative_path="synthetic/outer.zip",
        member_path="large.h5",
    )
    with pytest.raises(ArchiveMaterializationError, match="exceeding"):
        with materialize_archive_member(
            reference, temp_root=tmp_path, max_member_bytes=4
        ):
            raise AssertionError("unreachable")
    assert not list(tmp_path.glob("pi_multimodal_archive_*"))


def test_corrupt_outer_archive_is_reported(tmp_path: Path) -> None:
    archive = tmp_path / "broken.zip"
    archive.write_bytes(b"not-a-zip")
    reference = ArchiveMemberRef(
        archive_path=archive,
        archive_relative_path="synthetic/broken.zip",
        member_path="member.h5",
    )
    with pytest.raises(ArchiveMaterializationError, match="failed to materialize"):
        with materialize_archive_member(reference, temp_root=tmp_path):
            raise AssertionError("unreachable")
    assert not list(tmp_path.glob("pi_multimodal_archive_*"))
