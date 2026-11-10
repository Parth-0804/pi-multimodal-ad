#!/usr/bin/env python3
"""DEPRECATED forwarding wrapper only; canonical script: scripts/phm2026/training/train_rtdetr_detector.py.

No scientific implementation belongs here. No automatic removal date.
"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / 'phm2026/training/train_rtdetr_detector.py'
    runpy.run_path(str(target), run_name="__main__")
