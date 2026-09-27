#!/usr/bin/env python3
"""Restore PHM A/B/F raw inputs; see docs/phm2026/RAW_DATA_RECOVERY.md."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from pi_multimodal_ad.acquisition.phm_download import main

if __name__ == '__main__':
    raise SystemExit(main())
