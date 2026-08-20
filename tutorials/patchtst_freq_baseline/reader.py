"""From-scratch, read-only, bounded HF archive discovery + member access.

Independent of pi_multimodal_ad.profiling.archive_io — written fresh for
this tutorial. Never calls zipfile.ZipFile.extract() (which can write
outside the target directory via crafted paths); instead streams one
member at a time into a uniquely-named temporary file and removes it when
the caller's `with` block exits. Never modifies gtc-data-experiment/.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import tempfile
from typing import Iterator
import zipfile

_EXPERIMENT_DIR_RE = re.compile(r"^EXP\s*([ABF])$", re.IGNORECASE)
_RUN_ZIP_RE = re.compile(r"^Exp-([ABF])_HDF5_Run-(\d+)\.zip$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class RunArchive:
    experiment: str  # "EXP-A" / "EXP-B" / "EXP-F"
    run: int
    archive_path: Path


def discover_hf_run_archives(raw_root: Path) -> list[RunArchive]:
    """Find every Exp-<X>_HDF5_Run-<n>.zip under raw_root/high_frequency/.

    Directory names ("EXP A") and zip filenames ("Exp-A_HDF5_Run-1.zip")
    use inconsistent casing/spacing in the real archive, so both are
    parsed with their own small, explicit regex rather than assumed.
    """
    hf_root = raw_root / "high_frequency"
    if not hf_root.is_dir():
        raise FileNotFoundError(f"expected high_frequency/ under {raw_root}")
    found: list[RunArchive] = []
    for experiment_dir in sorted(hf_root.iterdir()):
        if not experiment_dir.is_dir():
            continue
        dir_match = _EXPERIMENT_DIR_RE.match(experiment_dir.name.strip())
        if dir_match is None:
            continue
        for zip_path in sorted(experiment_dir.glob("*.zip")):
            zip_match = _RUN_ZIP_RE.match(zip_path.name)
            if zip_match is None:
                continue
            letter_dir = dir_match.group(1).upper()
            letter_zip = zip_match.group(1).upper()
            if letter_dir != letter_zip:
                raise ValueError(
                    f"directory {experiment_dir.name!r} disagrees with zip "
                    f"filename {zip_path.name!r} on experiment letter"
                )
            found.append(
                RunArchive(
                    experiment=f"EXP-{letter_dir}",
                    run=int(zip_match.group(2)),
                    archive_path=zip_path,
                )
            )
    found.sort(key=lambda item: (item.experiment, item.run))
    return found


def list_hdf5_members(archive_path: Path) -> list[str]:
    """Central-directory listing only — no payload bytes touched."""
    with zipfile.ZipFile(archive_path, mode="r") as archive:
        return sorted(
            info.filename
            for info in archive.infolist()
            if not info.is_dir() and info.filename.lower().endswith(".hdf5")
        )


@contextmanager
def materialize_member(
    archive_path: Path, member_name: str, *, max_member_bytes: int
) -> Iterator[Path]:
    """Stream one ZIP member to a temp file; delete it when the caller is done.

    Never uses ZipFile.extract(). Enforces max_member_bytes both from the
    declared central-directory size (fast fail) and while streaming (in
    case the declared size understates the real payload), matching the
    bounded-read discipline this repo's own archive_io module documents,
    reimplemented independently here.
    """
    with tempfile.TemporaryDirectory(prefix="patchtst_freq_hf_") as tmp_name:
        tmp_dir = Path(tmp_name)
        with zipfile.ZipFile(archive_path, mode="r") as archive:
            info = archive.getinfo(member_name)
            if info.file_size > max_member_bytes:
                raise ValueError(
                    f"member {member_name!r} declares {info.file_size} bytes, "
                    f"exceeding the {max_member_bytes}-byte limit"
                )
            target = tmp_dir / "payload.hdf5"
            written = 0
            with archive.open(info, mode="r") as source, target.open("wb") as dest:
                while True:
                    chunk = source.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > max_member_bytes:
                        raise ValueError(
                            f"member {member_name!r} exceeded {max_member_bytes} "
                            "bytes while streaming"
                        )
                    dest.write(chunk)
        try:
            yield target
        finally:
            pass  # TemporaryDirectory context cleans this up on exit


def free_disk_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free
