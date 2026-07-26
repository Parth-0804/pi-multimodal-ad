"""
PHM North America 2026
Robust EXP-A High-Frequency Downloader

Downloads:
    Exp-A_HDF5_Run-1.zip  -> Early lifecycle
    Exp-A_HDF5_Run-3.zip  -> Intermediate lifecycle
    Exp-A_HDF5_Run-5.zip  -> Late lifecycle

Destination:
    /home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment

IMPORTANT:
This script DOES NOT use a copied Windows sharing_sid.

Instead:
    1. The VM opens the Synology public share.
    2. Synology gives the VM its own sharing_sid.
    3. The script verifies the requested file with a 1-byte probe.
    4. It confirms the real multi-GB ZIP exists.
    5. curl downloads the file.
    6. Interrupted downloads are resumed.
    7. A fresh Synology session is created when retrying.

No Python packages are required.
Only curl is required.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "https://gtc-data.synology.me:51111"

SHARE_ID = "uIrAvzqEh"

SHARE_URL = f"{HOST}/sharing/{SHARE_ID}"

OUTPUT_DIR = Path(
    "/home/student/Master_Thesis_WS/"
    "pi-multimodal-ad/"
    "gtc-data-experiment"
)

COOKIE_FILE = Path(
    "/home/student/Master_Thesis_WS/"
    "pi-multimodal-ad/"
    "synology_cookies.txt"
)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/150.0.0.0 Safari/537.36"
)

RUNS = [1, 3, 5]

# Anything smaller than 1 GiB is definitely not one
# of our ~19 GB high-frequency archives.
MIN_VALID_FILE_SIZE = 1 * 1024**3

RETRY_DELAY = 10


# ============================================================
# UTILITIES
# ============================================================

def gib(value: int) -> float:
    """Convert bytes to GiB."""
    return value / (1024**3)


def require_curl() -> None:
    """Verify that curl is installed."""

    if shutil.which("curl") is None:
        print("\nERROR: curl is not installed.")
        print("\nInstall it with:\n")
        print("sudo apt update")
        print("sudo apt install -y curl")
        sys.exit(1)


def get_filename(run: int) -> str:
    return f"Exp-A_HDF5_Run-{run}.zip"


def get_remote_path(run: int) -> str:
    return (
        f"/train/high-frequency/EXP-A/"
        f"Exp-A_HDF5_Run-{run}.zip"
    )


def build_download_url(run: int) -> str:
    """
    Build the Synology download URL in exactly the same
    format observed in Chrome DevTools.
    """

    filename = get_filename(run)
    remote_path = get_remote_path(run)

    # Synology dlink is the hexadecimal representation
    # of the remote path.
    dlink = remote_path.encode("utf-8").hex()

    no_cache = int(time.time() * 1000)

    return (
        f"{HOST}"
        f"/fsdownload/webapi/file_download.cgi/"
        f"{filename}"
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
# CREATE VM SYNOLOGY SESSION
# ============================================================

def create_fresh_session() -> None:
    """
    Open the public Synology sharing page from the VM.

    This creates a VM-specific sharing_sid and stores
    it inside COOKIE_FILE.
    """

    print("\nCreating fresh Synology sharing session...")

    # Remove previous session.
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

        # Read cookies too
        "-b",
        str(COOKIE_FILE),

        "--user-agent",
        USER_AGENT,

        SHARE_URL,

        "-o",
        "/dev/null",
    ]

    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(
            "Could not open the Synology public sharing page."
        )

    if not COOKIE_FILE.exists():
        raise RuntimeError(
            "Synology did not create a cookie file."
        )

    cookie_text = COOKIE_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )

    match = re.search(
        r"sharing_sid\s+([^\s]+)",
        cookie_text,
    )

    if not match:
        raise RuntimeError(
            "Synology page opened, but no sharing_sid "
            "was returned."
        )

    sid = match.group(1)

    print(
        f"Session established: "
        f"sharing_sid={sid[:8]}..."
    )


# ============================================================
# PROBE FILE
# ============================================================

def probe_file(run: int) -> int:
    """
    Request only ONE BYTE from the ZIP.

    Expected response:

        HTTP 206
        Content-Type: application/octet-stream
        Content-Range: bytes 0-0/TOTAL_SIZE

    This lets us know the exact total size BEFORE
    attempting the full download.
    """

    filename = get_filename(run)
    url = build_download_url(run)

    print()
    print("=" * 76)
    print(f"PROBING: {filename}")
    print("=" * 76)

    with tempfile.TemporaryDirectory() as temp_dir:

        headers_file = Path(temp_dir) / "headers.txt"
        probe_file = Path(temp_dir) / "probe.bin"

        command = [
            "curl",

            "-sS",
            "-L",
            "--fail",

            # Only request first byte
            "--range",
            "0-0",

            # Safety: never allow this probe to download
            # an unexpectedly large response.
            "--max-filesize",
            "1048576",

            # VM Synology session
            "-b",
            str(COOKIE_FILE),

            "-c",
            str(COOKIE_FILE),

            "--referer",
            SHARE_URL,

            "--user-agent",
            USER_AGENT,

            # Save headers
            "-D",
            str(headers_file),

            # Save first byte
            "-o",
            str(probe_file),

            url,
        ]

        result = subprocess.run(command)

        if result.returncode != 0:
            raise RuntimeError(
                "File probe failed."
            )

        headers = headers_file.read_text(
            encoding="utf-8",
            errors="replace",
        )

    # --------------------------------------------------------
    # Parse headers
    # --------------------------------------------------------

    http_matches = re.findall(
        r"HTTP/\S+\s+(\d+)",
        headers,
        flags=re.IGNORECASE,
    )

    content_type_matches = re.findall(
        r"content-type:\s*([^\r\n]+)",
        headers,
        flags=re.IGNORECASE,
    )

    content_range_matches = re.findall(
        r"content-range:\s*bytes\s+\d+-\d+/(\d+)",
        headers,
        flags=re.IGNORECASE,
    )

    content_disposition_matches = re.findall(
        r"content-disposition:\s*([^\r\n]+)",
        headers,
        flags=re.IGNORECASE,
    )

    status = (
        http_matches[-1]
        if http_matches
        else "UNKNOWN"
    )

    content_type = (
        content_type_matches[-1].strip()
        if content_type_matches
        else "UNKNOWN"
    )

    print(f"HTTP status        : {status}")
    print(f"Content-Type       : {content_type}")

    if content_disposition_matches:
        print(
            "Content-Disposition: "
            f"{content_disposition_matches[-1]}"
        )

    # --------------------------------------------------------
    # Reject Synology JSON response
    # --------------------------------------------------------

    if "application/json" in content_type.lower():

        raise RuntimeError(
            "Synology returned JSON instead of the ZIP.\n"
            "The sharing session is invalid."
        )

    if "application/octet-stream" not in content_type.lower():

        raise RuntimeError(
            f"Unexpected Content-Type: {content_type}"
        )

    # --------------------------------------------------------
    # Need Content-Range to determine full size
    # --------------------------------------------------------

    if not content_range_matches:

        print("\nRAW HEADERS:")
        print(headers[:3000])

        raise RuntimeError(
            "No Content-Range returned by Synology."
        )

    expected_size = int(
        content_range_matches[-1]
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

        raise RuntimeError(
            "Reported file is unexpectedly small."
        )

    print("Probe result       : VALID ✓")

    return expected_size


# ============================================================
# CHECK ZIP SIGNATURE
# ============================================================

def has_zip_signature(path: Path) -> bool:

    if not path.exists():
        return False

    if path.stat().st_size < 2:
        return False

    with path.open("rb") as f:
        return f.read(2) == b"PK"


# ============================================================
# DOWNLOAD ONE RUN
# ============================================================

def download_run(
    run: int,
    expected_size: int,
) -> None:

    filename = get_filename(run)

    final_path = OUTPUT_DIR / filename

    # Keep partial download separate.
    part_path = OUTPUT_DIR / f"{filename}.part"

    # --------------------------------------------------------
    # Handle old broken files
    # --------------------------------------------------------

    if final_path.exists():

        size = final_path.stat().st_size

        if (
            size == expected_size
            and has_zip_signature(final_path)
        ):
            print()
            print(
                f"Already complete: {filename} "
                f"({gib(size):.2f} GiB)"
            )
            return

        print()
        print(
            f"Removing old invalid/incomplete final file:"
        )
        print(final_path)
        print(
            f"Size: {size / 1024**2:.2f} MiB"
        )

        final_path.unlink()

    # --------------------------------------------------------
    # Validate existing .part file
    # --------------------------------------------------------

    if part_path.exists():

        part_size = part_path.stat().st_size

        if not has_zip_signature(part_path):

            print()
            print(
                "Existing .part file is not a ZIP."
            )

            print(
                "It is probably the old Synology JSON response."
            )

            print(
                f"Deleting: {part_path}"
            )

            part_path.unlink()

        else:

            print()
            print(
                f"Partial real ZIP detected:"
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

        print()
        print("=" * 76)
        print(f"DOWNLOADING: {filename}")
        print(f"Attempt    : {attempt}")
        print(
            f"Current    : "
            f"{gib(current_size):.2f} GiB"
        )
        print(
            f"Expected   : "
            f"{gib(expected_size):.2f} GiB"
        )
        print("=" * 76)

        # ----------------------------------------------------
        # Fresh session before each attempt
        # ----------------------------------------------------

        create_fresh_session()

        url = build_download_url(run)

        command = [
            "curl",

            "-L",

            # HTTP 4xx/5xx = failure
            "--fail",

            # Resume partial file
            "-C",
            "-",

            # A few retries using current session.
            # Outer Python loop creates a NEW session afterward.
            "--retry",
            "5",

            "--retry-all-errors",

            "--retry-delay",
            "5",

            "--connect-timeout",
            "30",

            # Detect dead connection
            "--speed-time",
            "60",

            "--speed-limit",
            "1024",

            # VM cookie
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

        result = subprocess.run(command)

        # ----------------------------------------------------
        # Inspect what exists after curl
        # ----------------------------------------------------

        if not part_path.exists():

            print()
            print(
                "No output file was created."
            )

            print(
                f"Retrying in {RETRY_DELAY}s..."
            )

            time.sleep(RETRY_DELAY)
            continue

        current_size = part_path.stat().st_size

        # ----------------------------------------------------
        # Detect JSON/HTML fake response
        # ----------------------------------------------------

        if not has_zip_signature(part_path):

            print()
            print(
                "WARNING:"
            )

            print(
                "Synology returned something other than "
                "the ZIP."
            )

            print(
                "Deleting invalid response and refreshing "
                "the sharing session."
            )

            part_path.unlink()

            time.sleep(RETRY_DELAY)
            continue

        print()
        print(
            f"Current downloaded size: "
            f"{gib(current_size):.2f} GiB"
        )

        # ----------------------------------------------------
        # Exact completion check
        # ----------------------------------------------------

        if current_size == expected_size:

            break

        if current_size > expected_size:

            raise RuntimeError(
                f"{filename} became larger than expected.\n"
                f"Expected: {expected_size}\n"
                f"Actual:   {current_size}"
            )

        print()
        print(
            "File is incomplete."
        )

        print(
            "Refreshing Synology session and resuming "
            f"in {RETRY_DELAY}s..."
        )

        time.sleep(RETRY_DELAY)

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    final_size = part_path.stat().st_size

    if final_size != expected_size:

        raise RuntimeError(
            "Final file size does not match expected size."
        )

    if not has_zip_signature(part_path):

        raise RuntimeError(
            "Final file does not have ZIP signature."
        )

    # Rename only after successful validation.
    part_path.rename(final_path)

    print()
    print("=" * 76)
    print("DOWNLOAD COMPLETE ✓")
    print("=" * 76)
    print(f"File : {filename}")
    print(
        f"Size : {gib(final_size):.2f} GiB"
    )
    print(f"Path : {final_path}")


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
    print("=" * 76)
    print("PHM NORTH AMERICA 2026")
    print("EXP-A ROBUST HIGH-FREQUENCY DOWNLOADER")
    print("=" * 76)

    print()
    print("Lifecycle sample:")
    print("  Run-1 -> Early lifecycle")
    print("  Run-3 -> Intermediate lifecycle")
    print("  Run-5 -> Late lifecycle")

    print()
    print("Destination:")
    print(OUTPUT_DIR)

    print()
    print(
        "Synology authentication:"
    )
    print(
        "VM creates its OWN sharing_sid automatically."
    )

    # --------------------------------------------------------
    # DOWNLOAD RUNS SEQUENTIALLY
    # --------------------------------------------------------

    for run in RUNS:

        # Create fresh VM session.
        create_fresh_session()

        # Confirm actual file exists and get exact size.
        expected_size = probe_file(run)

        # Download / resume.
        download_run(
            run,
            expected_size,
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print()
    print("=" * 76)
    print("ALL SELECTED RUNS COMPLETE")
    print("=" * 76)

    total = 0

    for run in RUNS:

        filename = get_filename(run)
        path = OUTPUT_DIR / filename

        if path.exists():

            size = path.stat().st_size
            total += size

            print(
                f"{filename:<30}"
                f"{gib(size):>8.2f} GiB"
            )

    print("-" * 76)

    print(
        f"{'TOTAL':<30}"
        f"{gib(total):>8.2f} GiB"
    )

    print()
    print("Dataset:")
    print(OUTPUT_DIR)


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print()
        print()
        print("Stopped manually.")
        print(
            "Partial .part file has been preserved."
        )

        print(
            "Run this script again to resume."
        )

        sys.exit(130)

    except Exception as error:

        print()
        print()
        print("=" * 76)
        print("ERROR")
        print("=" * 76)
        print(error)

        sys.exit(1)