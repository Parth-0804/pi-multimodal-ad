#!/usr/bin/env bash
set -euo pipefail
study_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
study_root="$(cd -- "$study_source_dir/.." && pwd)"
study_repo="$(cd -- "$study_root/../../../.." && pwd)"
cd -- "$study_repo"
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
export CUDA_VISIBLE_DEVICES=0 CUBLAS_WORKSPACE_CONFIG=:4096:8
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export HF_HOME="$study_root/temporary/huggingface" MPLCONFIGDIR="$study_root/temporary/matplotlib"
export CUDA_CACHE_PATH="$study_root/temporary/cuda" TORCH_HOME="$study_root/temporary/torch"
export XDG_CACHE_HOME="$study_root/temporary/xdg" TMPDIR="$study_root/temporary" PYTHONDONTWRITEBYTECODE=1
mkdir -p -- "$CUDA_CACHE_PATH" "$TORCH_HOME" "$XDG_CACHE_HOME"
study_cpu_ids="$(ma_thesis_env/bin/python -I -B -c 'import os;print(",".join(map(str,sorted(os.sched_getaffinity(0))[:4])))')"
exec taskset -c "$study_cpu_ids" ma_thesis_env/bin/python -I -B "$study_source_dir/run_study.py" "$@"
