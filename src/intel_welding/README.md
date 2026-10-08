# Intel Welding

This namespace marks the Intel Robotic Welding domain. The existing package subdirectories (`data`, `models`, `fusion`, `evaluation`, `analysis`, `robustness`) are retained placeholders, not claims of implemented models. The implemented inventory, label audit, split proposal, structural foundations and reporting currently live in `scripts/intel_welding/01_inventory.py` through `05_foundation_report.py`. No duplicate source implementation was created during restructuring.

Use `scripts/intel_welding/04_foundations.py --help` to inspect the foundation audit entry point. Config: `configs/intel_welding/foundations.json`. Tests: `tests/intel_welding/test_intel_foundations.py`. Evidence: existing `artifacts/intel_welding/` and `runs/intel_welding/` where present; retired material remains `archive/legacy_intel_welding_dataset/`. Read existing study reports for limitations; structural migration does not change scientific claims.

No dependency on a shared implementation has been established. Future extraction from scripts belongs here, with regression checks, rather than under PHM.
