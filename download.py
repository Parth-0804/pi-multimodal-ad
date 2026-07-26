#!/usr/bin/env python3
"""
PHM North America 2026
Robust EXP-B High-Frequency Downloader

PURPOSE
-------
Download all available high-frequency EXP-B run archives.

Existing EXP-A and EXP-F files are NOT touched.

The script automatically checks:

    Exp-B_HDF5_Run-1.zip
    Exp-B_HDF5_Run-2.zip
    Exp-B_HDF5_Run-3.zip
    ...

and downloads every valid EXP-B archive that exists.

Destination:
    /home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment

FEATURES
--------
- Downloads EXP-B only
- Does not touch EXP-A or EXP-F
- Automatically discovers available EXP-B runs
- VM creates its own Synology sharing_sid
- 1-byte probe before full download
- Validates application/octet-stream
- Reads exact file size using Content-Range
- Uses .part while downloading
- Resumes interrupted downloads
- Creates a fresh Synology session on retries
- Verifies ZIP signature
- Verifies exact final size
- Skips already-complete EXP-B files
- Stops scanning after several consecutive missing runs

No additional Python packages required.
Only curl is required.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "https://gtc-data.synology.me:51111"

SHARE_ID = "uIrAvzqEh"

SHARE_URL = f"{HOST}/sharing/{SHARE_ID}"


# ------------------------------------------------------------
# Repository paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(
    "/home/student/Master_Thesis_WS/"
    "pi-multimodal-ad"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "gtc-data-experiment"
)

COOKIE_FILE = (
    PROJECT_ROOT
    / "synology_cookies.txt"
)


# ------------------------------------------------------------
# Browser identity
# ------------------------------------------------------------

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/150.0.0.0 Safari/537.36"
)


# ------------------------------------------------------------
# File validation
# ------------------------------------------------------------

# HF archives should be large.
# Anything smaller than 1 GiB is suspicious.
MIN_VALID_FILE_SIZE = 1 * 1024**3


# ------------------------------------------------------------
# Retry behaviour
# ------------------------------------------------------------

RETRY_DELAY = 10


# ------------------------------------------------------------
# EXP-B automatic discovery
# ------------------------------------------------------------

EXPERIMENT = "B"

# We do NOT assume the number of runs.
#
# The script checks Run-1 ... Run-20.
# It stops earlier after several consecutive missing runs.
MAX_RUN_TO_SCAN = 20

# Example:
#
# Run-1 valid
# Run-2 valid
# ...
# Run-8 valid
# Run-9 missing
# Run-10 missing
# Run-11 missing
#
# -> stop scanning
CONSECUTIVE_MISSING_TO_STOP = 3


# ============================================================
# DATA CLASS
# ============================================================

@dataclass(frozen=True)
class DownloadItem:

    experiment: str
    run: int

    @property
    def experiment_folder(self) -> str:

        return f"EXP-{self.experiment}"

    @property
    def filename(self) -> str:

        return (
            f"Exp-{self.experiment}_"
            f"HDF5_Run-{self.run}.zip"
        )

    @property
    def remote_path(self) -> str:

        return (
            f"/train/high-frequency/"
            f"{self.experiment_folder}/"
            f"{self.filename}"
        )


# ============================================================
# GENERAL UTILITIES
# ============================================================

def gib(value: int) -> float:
    """
    Convert bytes to GiB.
    """

    return value / (1024**3)


def require_curl() -> None:
    """
    Verify that curl is installed.
    """

    if shutil.which("curl") is None:

        print()
        print("ERROR: curl is not installed.")

        print()
        print("Install it with:")

        print()
        print("sudo apt update")
        print("sudo apt install -y curl")

        sys.exit(1)


def has_zip_signature(path: Path) -> bool:
    """
    ZIP archives normally begin with the bytes 'PK'.

    This detects common Synology failure responses where
    JSON or HTML is saved instead of the actual ZIP.
    """

    if not path.exists():

        return False

    if path.stat().st_size < 2:

        return False

    with path.open("rb") as handle:

        signature = handle.read(2)

    return signature == b"PK"


# ============================================================
# BUILD SYNOLOGY DOWNLOAD URL
# ============================================================

def build_download_url(
    item: DownloadItem,
) -> str:
    """
    Build the Synology direct-download URL.

    Synology uses a hexadecimal representation of
    the remote path as the dlink parameter.
    """

    dlink = (
        item.remote_path
        .encode("utf-8")
        .hex()
    )

    no_cache = int(
        time.time() * 1000
    )

    return (
        f"{HOST}"
        f"/fsdownload/webapi/file_download.cgi/"
        f"{item.filename}"
        f"?dlink=%22{dlink}%22"
        f"&noCache={no_cache}"
        f"&_sharing_id=%22{SHARE_ID}%22"
        f"&api=SYNO.FolderSharing.Download"
        f"&version=2"
        f"&method=download"
        f"&mode=download"
        f"&stdhtml=false"
    )


# ============================================================
# CREATE VM-SIDE SYNOLOGY SESSION
# ============================================================

def create_fresh_session() -> None:
    """
    Open the public Synology share directly from the VM.

    Synology then creates a sharing_sid specifically
    for this VM.
    """

    print()
    print("Creating fresh Synology sharing session...")

    if COOKIE_FILE.exists():

        COOKIE_FILE.unlink()

    command = [
        "curl",

        "-sS",
        "-L",
        "--fail",

        # Save cookies
        "-c",
        str(COOKIE_FILE),

        # Read cookies
        "-b",
        str(COOKIE_FILE),

        "--user-agent",
        USER_AGENT,

        SHARE_URL,

        "-o",
        "/dev/null",
    ]

    result = subprocess.run(
        command
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Could not open the Synology "
            "public sharing page."
        )

    if not COOKIE_FILE.exists():

        raise RuntimeError(
            "Synology did not create "
            "a cookie file."
        )

    cookie_text = (
        COOKIE_FILE.read_text(
            encoding="utf-8",
            errors="replace",
        )
    )

    match = re.search(
        r"sharing_sid\s+([^\s]+)",
        cookie_text,
    )

    if not match:

        raise RuntimeError(
            "Synology page opened, but "
            "no sharing_sid was returned."
        )

    sid = match.group(1)

    print(
        "Session established: "
        f"sharing_sid={sid[:8]}..."
    )


# ============================================================
# PROBE FILE
# ============================================================

def probe_file(
    item: DownloadItem,
) -> int | None:
    """
    Request only ONE BYTE.

    A valid archive should return something like:

        HTTP 206
        Content-Type: application/octet-stream
        Content-Range: bytes 0-0/TOTAL_SIZE

    Returns:
        expected file size in bytes

    Returns None:
        when the requested EXP-B run apparently
        does not exist.

    This function intentionally avoids crashing when
    auto-discovering EXP-B runs.
    """

    url = build_download_url(
        item
    )

    print()
    print("=" * 78)

    print(
        f"PROBING: "
        f"{item.experiment_folder} "
        f"Run-{item.run}"
    )

    print(
        f"FILE   : {item.filename}"
    )

    print("=" * 78)

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir = Path(temp_dir)

        headers_file = (
            temp_dir
            / "headers.txt"
        )

        probe_output = (
            temp_dir
            / "probe.bin"
        )

        command = [
            "curl",

            "-sS",
            "-L",

            # Request first byte only
            "--range",
            "0-0",

            # Never allow the probe response
            # to become unexpectedly large
            "--max-filesize",
            "1048576",

            "-b",
            str(COOKIE_FILE),

            "-c",
            str(COOKIE_FILE),

            "--referer",
            SHARE_URL,

            "--user-agent",
            USER_AGENT,

            "-D",
            str(headers_file),

            "-o",
            str(probe_output),

            url,
        ]

        result = subprocess.run(
            command
        )

        # ----------------------------------------------------
        # Could not even perform request
        # ----------------------------------------------------

        if result.returncode != 0:

            print(
                "Probe request failed."
            )

            return None

        if not headers_file.exists():

            print(
                "No headers returned."
            )

            return None

        headers = (
            headers_file.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )


    # ========================================================
    # PARSE RESPONSE HEADERS
    # ========================================================

    http_matches = re.findall(
        r"HTTP/\S+\s+(\d+)",
        headers,
        flags=re.IGNORECASE,
    )

    type_matches = re.findall(
        r"content-type:\s*([^\r\n]+)",
        headers,
        flags=re.IGNORECASE,
    )

    range_matches = re.findall(
        r"content-range:\s*bytes\s+"
        r"\d+-\d+/(\d+)",
        headers,
        flags=re.IGNORECASE,
    )

    disposition_matches = re.findall(
        r"content-disposition:\s*"
        r"([^\r\n]+)",
        headers,
        flags=re.IGNORECASE,
    )


    status = (
        http_matches[-1]
        if http_matches
        else "UNKNOWN"
    )

    content_type = (
        type_matches[-1].strip()
        if type_matches
        else "UNKNOWN"
    )


    print(
        f"HTTP status        : {status}"
    )

    print(
        f"Content-Type       : {content_type}"
    )


    if disposition_matches:

        print(
            "Content-Disposition: "
            f"{disposition_matches[-1]}"
        )


    # ========================================================
    # DETECT NONEXISTENT / INVALID RUN
    # ========================================================

    if (
        "application/octet-stream"
        not in content_type.lower()
    ):

        print(
            f"Run-{item.run} does not appear "
            "to be a valid HF archive."
        )

        return None


    if not range_matches:

        print(
            "No Content-Range returned."
        )

        print(
            f"Run-{item.run} will be treated "
            "as unavailable."
        )

        return None


    # ========================================================
    # VALID FILE FOUND
    # ========================================================

    expected_size = int(
        range_matches[-1]
    )


    print(
        f"Expected file size : "
        f"{expected_size:,} bytes"
    )

    print(
        f"Expected file size : "
        f"{gib(expected_size):.2f} GiB"
    )


    if expected_size < MIN_VALID_FILE_SIZE:

        print(
            "File is unexpectedly small."
        )

        print(
            "Treating this run as invalid."
        )

        return None


    print(
        "Probe result       : VALID ✓"
    )


    return expected_size


# ============================================================
# DOWNLOAD ONE EXP-B ARCHIVE
# ============================================================

def download_item(
    item: DownloadItem,
    expected_size: int,
) -> None:

    final_path = (
        OUTPUT_DIR
        / item.filename
    )

    part_path = (
        OUTPUT_DIR
        / f"{item.filename}.part"
    )


    # ========================================================
    # CHECK FINAL FILE
    # ========================================================

    if final_path.exists():

        size = (
            final_path.stat().st_size
        )

        if (
            size == expected_size
            and has_zip_signature(
                final_path
            )
        ):

            print()
            print(
                "SKIPPING — already complete:"
            )

            print(
                f"{item.filename}"
            )

            print(
                f"Size: {gib(size):.2f} GiB"
            )

            return


        print()
        print(
            "Existing final file is "
            "invalid or incomplete."
        )

        print(
            f"File: {final_path}"
        )

        print(
            f"Current size: "
            f"{gib(size):.2f} GiB"
        )

        print(
            "Removing invalid final file."
        )

        final_path.unlink()


    # ========================================================
    # CHECK EXISTING PARTIAL DOWNLOAD
    # ========================================================

    if part_path.exists():

        part_size = (
            part_path.stat().st_size
        )

        if not has_zip_signature(
            part_path
        ):

            print()
            print(
                "Existing .part file is "
                "not a valid ZIP response."
            )

            print(
                f"Deleting: {part_path}"
            )

            part_path.unlink()

        else:

            print()
            print(
                "Partial ZIP detected:"
            )

            print(
                f"{gib(part_size):.2f} / "
                f"{gib(expected_size):.2f} GiB"
            )

            print(
                "Download will resume."
            )


    # ========================================================
    # DOWNLOAD / RETRY LOOP
    # ========================================================

    attempt = 0


    while True:

        attempt += 1


        current_size = (
            part_path.stat().st_size
            if part_path.exists()
            else 0
        )


        if current_size == expected_size:

            break


        if current_size > expected_size:

            raise RuntimeError(
                f"{item.filename} is already "
                "larger than expected.\n"
                f"Expected: {expected_size:,}\n"
                f"Actual:   {current_size:,}"
            )


        print()
        print("=" * 78)

        print(
            f"DOWNLOADING : {item.filename}"
        )

        print(
            f"EXPERIMENT  : "
            f"{item.experiment_folder}"
        )

        print(
            f"RUN         : {item.run}"
        )

        print(
            f"ATTEMPT     : {attempt}"
        )

        print(
            f"CURRENT     : "
            f"{gib(current_size):.2f} GiB"
        )

        print(
            f"EXPECTED    : "
            f"{gib(expected_size):.2f} GiB"
        )

        print("=" * 78)


        # ----------------------------------------------------
        # Fresh session on every outer retry
        # ----------------------------------------------------

        create_fresh_session()


        url = build_download_url(
            item
        )


        command = [
            "curl",

            "-L",

            "--fail",

            # Resume existing .part
            "-C",
            "-",

            # Retry temporary failures
            "--retry",
            "5",

            "--retry-all-errors",

            "--retry-delay",
            "5",

            "--connect-timeout",
            "30",

            # Detect dead/very slow connections
            "--speed-time",
            "60",

            "--speed-limit",
            "1024",

            # Synology cookies
            "-b",
            str(COOKIE_FILE),

            "-c",
            str(COOKIE_FILE),

            "--referer",
            SHARE_URL,

            "--user-agent",
            USER_AGENT,

            "--progress-bar",

            "-o",
            str(part_path),

            url,
        ]


        result = subprocess.run(
            command
        )


        # ====================================================
        # CHECK RESULT
        # ====================================================

        if not part_path.exists():

            print()
            print(
                "No output file was created."
            )

            print(
                f"Retrying in "
                f"{RETRY_DELAY} seconds..."
            )

            time.sleep(
                RETRY_DELAY
            )

            continue


        current_size = (
            part_path.stat().st_size
        )


        # ----------------------------------------------------
        # Detect JSON / HTML response
        # ----------------------------------------------------

        if not has_zip_signature(
            part_path
        ):

            print()
            print(
                "WARNING:"
            )

            print(
                "Synology returned something "
                "other than the ZIP."
            )

            print(
                "Deleting invalid response."
            )

            part_path.unlink()

            print(
                f"Retrying in "
                f"{RETRY_DELAY} seconds..."
            )

            time.sleep(
                RETRY_DELAY
            )

            continue


        print()
        print(
            "Current downloaded size: "
            f"{gib(current_size):.2f} GiB"
        )


        # ----------------------------------------------------
        # Complete
        # ----------------------------------------------------

        if current_size == expected_size:

            break


        # ----------------------------------------------------
        # Too large = corruption
        # ----------------------------------------------------

        if current_size > expected_size:

            raise RuntimeError(
                f"{item.filename} became "
                "larger than expected.\n"
                f"Expected: "
                f"{expected_size:,} bytes\n"
                f"Actual:   "
                f"{current_size:,} bytes"
            )


        # ----------------------------------------------------
        # Still incomplete
        # ----------------------------------------------------

        print()
        print(
            "File is incomplete."
        )

        print(
            "Refreshing Synology session "
            "and resuming in "
            f"{RETRY_DELAY} seconds..."
        )

        time.sleep(
            RETRY_DELAY
        )


    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    final_size = (
        part_path.stat().st_size
    )


    if final_size != expected_size:

        raise RuntimeError(
            f"Final size mismatch for "
            f"{item.filename}.\n"
            f"Expected: {expected_size:,}\n"
            f"Actual:   {final_size:,}"
        )


    if not has_zip_signature(
        part_path
    ):

        raise RuntimeError(
            "Final file does not have "
            "a ZIP signature:\n"
            f"{item.filename}"
        )


    # --------------------------------------------------------
    # Promote .part -> .zip
    # --------------------------------------------------------

    part_path.rename(
        final_path
    )


    print()
    print("=" * 78)

    print(
        "DOWNLOAD COMPLETE ✓"
    )

    print("=" * 78)

    print(
        f"Experiment : "
        f"{item.experiment_folder}"
    )

    print(
        f"Run        : {item.run}"
    )

    print(
        f"File       : {item.filename}"
    )

    print(
        f"Size       : "
        f"{gib(final_size):.2f} GiB"
    )

    print(
        f"Path       : {final_path}"
    )


# ============================================================
# EXP-B AUTO DISCOVERY + DOWNLOAD
# ============================================================

def discover_and_download_exp_b() -> (
    list[tuple[DownloadItem, int]]
):

    completed: list[
        tuple[DownloadItem, int]
    ] = []


    missing_in_a_row = 0


    print()
    print("=" * 78)

    print(
        "AUTO-DISCOVERING EXP-B RUNS"
    )

    print("=" * 78)


    for run in range(
        1,
        MAX_RUN_TO_SCAN + 1,
    ):

        item = DownloadItem(
            EXPERIMENT,
            run,
        )


        print()
        print("#" * 78)

        print(
            f"CHECKING "
            f"EXP-{EXPERIMENT} "
            f"RUN-{run}"
        )

        print("#" * 78)


        # ----------------------------------------------------
        # Fresh session for probe
        # ----------------------------------------------------

        try:

            create_fresh_session()

            expected_size = probe_file(
                item
            )

        except Exception as error:

            print()
            print(
                "Probe encountered an error:"
            )

            print(
                error
            )

            print()
            print(
                "Creating one fresh session "
                "and retrying probe..."
            )


            try:

                create_fresh_session()

                expected_size = probe_file(
                    item
                )

            except Exception as second_error:

                print(
                    "Second probe failed:"
                )

                print(
                    second_error
                )

                expected_size = None


        # ====================================================
        # RUN NOT FOUND
        # ====================================================

        if expected_size is None:

            missing_in_a_row += 1

            print()
            print(
                f"EXP-B Run-{run} "
                "not available."
            )

            print(
                "Consecutive unavailable runs: "
                f"{missing_in_a_row}/"
                f"{CONSECUTIVE_MISSING_TO_STOP}"
            )


            if (
                missing_in_a_row
                >=
                CONSECUTIVE_MISSING_TO_STOP
            ):

                print()
                print("=" * 78)

                print(
                    "No further EXP-B runs "
                    "appear to be available."
                )

                print(
                    "Stopping automatic scan."
                )

                print("=" * 78)

                break


            continue


        # ====================================================
        # VALID RUN FOUND
        # ====================================================

        missing_in_a_row = 0


        download_item(
            item,
            expected_size,
        )


        completed.append(
            (
                item,
                expected_size,
            )
        )


    return completed


# ============================================================
# LOCAL SUMMARY
# ============================================================

def print_local_dataset_summary() -> None:
    """
    Display all EXP-A, EXP-B and EXP-F HF archives
    currently present in the dataset directory.
    """

    print()
    print()
    print("=" * 78)

    print(
        "LOCAL HIGH-FREQUENCY DATASET SUMMARY"
    )

    print("=" * 78)


    total_bytes = 0


    for experiment in [
        "A",
        "B",
        "F",
    ]:

        files = sorted(
            OUTPUT_DIR.glob(
                f"Exp-{experiment}_"
                "HDF5_Run-*.zip"
            )
        )


        if not files:

            continue


        print()
        print(
            f"EXP-{experiment}:"
        )


        experiment_total = 0


        for path in files:

            size = (
                path.stat().st_size
            )

            experiment_total += size
            total_bytes += size


            print(
                f"  {path.name:<32} "
                f"{gib(size):>8.2f} GiB"
            )


        print(
            f"  {'EXP-' + experiment + ' TOTAL':<32} "
            f"{gib(experiment_total):>8.2f} GiB"
        )


    print()
    print("-" * 78)

    print(
        f"{'TOTAL A + B + F':<34}"
        f"{gib(total_bytes):>8.2f} GiB"
    )

    print("=" * 78)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    require_curl()


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    print()
    print("=" * 78)

    print(
        "PHM NORTH AMERICA 2026"
    )

    print(
        "EXP-B HIGH-FREQUENCY DOWNLOADER"
    )

    print("=" * 78)


    print()
    print(
        "Target:"
    )

    print(
        "  EXP-B high-frequency runs only"
    )


    print()
    print(
        "Existing EXP-A / EXP-F:"
    )

    print(
        "  LEFT UNTOUCHED ✓"
    )


    print()
    print(
        "Destination:"
    )

    print(
        OUTPUT_DIR
    )


    print()
    print(
        "Automatic scan:"
    )

    print(
        f"  Run-1 → Run-{MAX_RUN_TO_SCAN}"
    )


    print(
        "  Stop after "
        f"{CONSECUTIVE_MISSING_TO_STOP} "
        "consecutive unavailable runs"
    )


    print()
    print(
        "Starting EXP-B discovery..."
    )


    completed = (
        discover_and_download_exp_b()
    )


    # ========================================================
    # EXP-B SUMMARY
    # ========================================================

    print()
    print()
    print("=" * 78)

    print(
        "EXP-B DOWNLOAD PROCESS COMPLETE"
    )

    print("=" * 78)


    if completed:

        print()
        print(
            "Valid EXP-B archives found:"
        )


        for item, expected_size in completed:

            path = (
                OUTPUT_DIR
                / item.filename
            )


            if path.exists():

                size = (
                    path.stat().st_size
                )

                print(
                    f"  Run-{item.run:<2} "
                    f"{item.filename:<30} "
                    f"{gib(size):>7.2f} GiB"
                )


    else:

        print()
        print(
            "No valid EXP-B archives "
            "were downloaded/found."
        )


    # ========================================================
    # FULL LOCAL A/B/F SUMMARY
    # ========================================================

    print_local_dataset_summary()


    print()
    print(
        "Dataset location:"
    )

    print(
        OUTPUT_DIR
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        main()


    except KeyboardInterrupt:

        print()
        print()

        print(
            "Stopped manually."
        )

        print(
            "Any valid .part file has "
            "been preserved."
        )

        print(
            "Run download.py again "
            "to resume."
        )

        sys.exit(130)


    except Exception as error:

        print()
        print()

        print("=" * 78)

        print(
            "ERROR"
        )

        print("=" * 78)

        print(
            error
        )

        print()
        print(
            "Any valid .part file has "
            "been preserved."
        )

        print(
            "Run download.py again "
            "after resolving the issue."
        )

        sys.exit(1)