#!/usr/bin/env python3
"""Simple disk-space reporting script.

Usage:
  python3 scripts/ops/check_disk_space.py         # check root '/'
  python3 scripts/ops/check_disk_space.py -p /home
  python3 scripts/ops/check_disk_space.py -a    # list all mounts (uses psutil or df)
"""
from __future__ import annotations
import shutil
import subprocess
import sys

try:
    import psutil  # optional, nicer output
except Exception:
    psutil = None


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}EB"


def print_usage(path: str) -> None:
    try:
        if psutil:
            u = psutil.disk_usage(path)
            total, used, free, percent = u.total, u.used, u.free, u.percent
        else:
            du = shutil.disk_usage(path)
            total, free = du.total, du.free
            used = total - free
            percent = (used / total * 100) if total else 0

        print(f"{path}\t{human(total)} total\t{human(used)} used\t{human(free)} free\t{percent:.1f}%")
    except Exception as exc:
        print(f"{path}\tERROR: {exc}", file=sys.stderr)


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Report disk space usage")
    p.add_argument("-p", "--path", default="/", help="Path to check (default '/')")
    p.add_argument("-a", "--all", action="store_true", help="List all mounted filesystems")
    args = p.parse_args()

    if args.all:
        if psutil:
            for part in psutil.disk_partitions(all=False):
                print_usage(part.mountpoint)
        else:
            # Fallback to calling `df -h` to get human-friendly table
            try:
                out = subprocess.check_output(["df", "-h", "--output=target,size,used,avail,pcent"], text=True)
                print(out)
            except Exception:
                # If df isn't available, at least print the requested path
                print_usage(args.path)
    else:
        print_usage(args.path)


if __name__ == "__main__":
    main()
