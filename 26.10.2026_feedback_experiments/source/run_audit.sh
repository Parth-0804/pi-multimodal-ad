#!/usr/bin/env bash
set -euo pipefail
audit_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
audit_repo_dir="$(cd -- "$audit_source_dir/../.." && pwd)"
cd -- "$audit_repo_dir"
export PYTHONDONTWRITEBYTECODE=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
# Retain inherited GPU visibility/allocation. Never widen it.
exec ma_thesis_env/bin/python -B "$audit_source_dir/gpu_audit.py" run "$@"
