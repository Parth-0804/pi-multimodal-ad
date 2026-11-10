#!/usr/bin/env python3
"""Acquire only the fixed conservative core's three published camera streams."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from vifailback.acquisition import acquire

if __name__ == '__main__':
    result = acquire()
    raise SystemExit(0 if result['complete'] else 2)
