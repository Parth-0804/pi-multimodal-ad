# Complete directory structure

Audit `20261028T115408Z` · 2026-10-28T12:54:08+01:00. Read-only assessment; no cleanup or downloads initiated by this audit. Concurrent REBOOT work is identified separately. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

Every directory was inventoried recursively, including hidden folders. This presentation shows the actual research hierarchy to four levels, with explicit collapsed branches to keep the report compact. Repetitive raw sessions, installed packages, Git-object fanout, generated feature shards and exported copies are summarized with exact descendant counts. This is a complete coverage audit with a condensed display, not a claim that every leaf path is printed. Counts include descendants; sizes already include children, so do not sum tree rows.

## Every top-level directory

| Full relative path | Allocated | Files | Subdirs | Largest immediate subdirectories | Main content | Activity/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| data | 26.939 GB | 8296 | 8319 | data/Full Dataset: 26.877 GB; data/rawvib: 0.058 GB; data/paderborn: 0.004 GB | Intel Welding raw inputs; small Paderborn/raw-vibration supplements | Preserved raw; Intel modelling NO-GO |
| HANDOVER | 17.335 GB | 17370 | 1311 | HANDOVER/01_raw_dataset: 16.848 GB; HANDOVER/experiments: 0.474 GB; HANDOVER/02_labels_and_alignment: 0.010 GB | Official archives/extracted RGB/wrench/labels; active v2 and historical evaluations | Completed evidence; active results common_support_v2 |
| .git | 15.899 GB | 3400 | 294 | .git/objects: 15.885 GB; .git/refs: 0.000 GB; .git/logs: 0.000 GB | Version history, packed objects, index and refs | Required Git history; no GC/rewrite |
| runs | 9.102 GB | 27316 | 1408 | runs/reassemble: 4.974 GB; runs/phm2026_image_target: 1.254 GB; runs/phm2026_rtdetr_detection: 0.743 GB | Versioned PHM/Intel/REASSEMBLE/thesis runs and outputs | Required historical and completed result evidence |
| 00_experiments | 7.235 GB | 96779 | 1234 | 00_experiments/frozen32_vs_finetuned32_fusion_diagnosis: 3.626 GB; 00_experiments/visual_backbone_one_day: 2.137 GB; 00_experiments/adaptive_fusion_robustness: 0.892 GB | REASSEMBLE follow-ups, checkpoints, robustness and comparisons | Preserved evidence; source of later comparisons |
| ma_thesis_env | 7.215 GB | 60656 | 7579 | ma_thesis_env/lib: 7.167 GB; ma_thesis_env/share: 0.048 GB; ma_thesis_env/bin: 0.000 GB | Python 3.12 environment, CUDA/PyTorch/compiled libraries | In use by live training; preserve |
| MILLING DATASET | 4.359 GB | 2586 | 388 | MILLING DATASET/runs: 4.271 GB; MILLING DATASET/data: 3.732 GB; MILLING DATASET/.tools: 0.080 GB | Authoritative MSM data, acquisition staging, feasibility and model pilots | Raw source for MSM plus protected pilot history |
| 26.10.2026_feedback_experiments | 4.247 GB | 5602 | 144 | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability: 2.719 GB; 26.10.2026_feedback_experiments/runs: 1.528 GB; 26.10.2026_feedback_experiments/source: 0.000 GB | GPU benchmarks and current CNN seed-stability/comparison runs | LIVE writers and encoded-video readers observed |
| REBOOT | 3.590 GB | 1905 | 304 | REBOOT/01_raw_dataset: 2.957 GB; REBOOT/04_visual_failure_review: 0.620 GB; REBOOT/03_video_sensor_alignment: 0.010 GB | Pinned source metadata plus selected RGB pilot chunks, original/column-range numerical inputs and review derivatives | Concurrent independent pilot acquisition; audit initiated no payload transfer |
| CROSS_DATASET_COMPARISON | 2.712 GB | 8761 | 2371 | CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE: 2.710 GB; CROSS_DATASET_COMPARISON/provenance: 0.001 GB; CROSS_DATASET_COMPARISON/src: 0.000 GB | Frozen external evaluation, synthesis and independent review export | Current completed external-evaluation evidence |
| MSM | 1.434 GB | 6708 | 1023 | MSM/03_processed_model_inputs: 1.053 GB; MSM/05_trained_models: 0.212 GB; MSM/06_evaluation_results: 0.111 GB | Native-label audit, derived features, models, predictions and robustness | Completed final evaluation; raw source is a symlink |
| artifacts | 0.504 GB | 481 | 56 | artifacts/thesis: 0.437 GB; artifacts/presentation: 0.063 GB; artifacts/intel_welding: 0.002 GB | Curated research evidence, thesis/PHM/Intel/REASSEMBLE reports | Required reported-result and provenance chain |
| parth_ws_bootstrap | 0.471 GB | 11751 | 1349 | parth_ws_bootstrap/00_experimentation: 0.456 GB; parth_ws_bootstrap/controller_builds: 0.010 GB; parth_ws_bootstrap/work_sessions: 0.005 GB | Original visual workspace, shared features and retained cache metadata | Still referenced by newer workspace symlinks |
| experiments | 0.370 GB | 323 | 55 | experiments/exp_a_initial_eda_r1_r3_r5: 0.369 GB; experiments/reassemble: 0.000 GB; experiments/phm2026: 0.000 GB | Historical EXP-A EDA and domain navigation/symlinks | Protected historical EDA; linked walkthroughs |
| tutorials | 0.123 GB | 132 | 27 | tutorials/rtdetr_storybook: 0.094 GB; tutorials/presentations: 0.010 GB; tutorials/patchtst_freq_baseline: 0.009 GB | Research tutorials, baseline reports and model weights | Historical results/tutorial reproduction |
| docs | 0.074 GB | 433 | 111 | docs/maintenance: 0.041 GB; docs/repository_restructure: 0.021 GB; docs/thesis_review_handoff: 0.010 GB | Policies, protocols, result indexes and maintenance evidence | Authoritative interpretation/reproduction documentation |
| scratch | 0.051 GB | 92 | 7 | scratch/blind_inspection: 0.051 GB | PHM inspection/derived work, not certified disposable | UNKNOWN lineage; preserve pending review |
| src | 0.002 GB | 213 | 39 | src/reassemble: 0.001 GB; src/phm2026: 0.001 GB; src/pi_multimodal_ad: 0.000 GB | Domain implementation plus compatibility wrappers/bytecode | Current executable source |
| scripts | 0.002 GB | 167 | 25 | scripts/phm2026: 0.001 GB; scripts/__pycache__: 0.000 GB; scripts/thesis: 0.000 GB | Domain CLI/research/maintenance entry points and bytecode | Current executable source |
| .cache | 0.002 GB | 86 | 35 | .cache/repository_restructure: 0.002 GB | Retired module bytecode preserved by repository migration | Historical maintenance cache; source correspondence needs review |
| tests | 0.000 GB | 57 | 12 | tests/phm2026: 0.000 GB; tests/reassemble: 0.000 GB; tests/fixtures: 0.000 GB | Domain/operations tests and tiny synthetic fixtures | Current validation source |
| STORAGE_AUDIT | 0.000 GB | 10 | 1 | STORAGE_AUDIT/20261028T114917Z: 0.000 GB | Earlier dated read-only storage snapshot and provenance | Earlier audit retained; current final snapshot supersedes its capacity figures |
| configs | 0.000 GB | 31 | 6 | configs/experiments: 0.000 GB; configs/reassemble: 0.000 GB; configs/phm2026: 0.000 GB | Dataset and experiment configurations | Required experiment/input selections |
| .pytest_cache | 0.000 GB | 5 | 2 | .pytest_cache/v: 0.000 GB | Pytest node IDs and test-run convenience cache | Non-scientific cache; likely regenerable |
| archive | 0.000 GB | 9 | 1 | archive/legacy_intel_welding_dataset: 0.000 GB | Legacy Intel code/documentation | Research history; preserve |
| DATASET_RESEARCH | 0.000 GB | 2 | 0 | None | Dataset registry and navigation symlinks | Current navigation; target sizes excluded |
| .github | 0.000 GB | 1 | 0 | None | Contributor/assistant repository instructions | Governance |
| .vscode | 0.000 GB | 1 | 0 | None | Workspace editor settings | Local configuration; no useful recovery |

## Condensed measured tree

```text
./
  .cache/  0.002 GB; 86 files; 35 subdirs
    repository_restructure/  0.002 GB; 86 files; 34 subdirs
      20261005T131103Z/  0.002 GB; 86 files; 33 subdirs
        scripts/  0.000 GB; 5 files; 6 subdirs [collapsed]
        src/  0.001 GB; 51 files; 22 subdirs [collapsed]
        tests/  0.001 GB; 30 files; 2 subdirs [collapsed]
  .git/  15.899 GB; 3400 files; 294 subdirs
    branches/  0.000 GB; 0 files; 0 subdirs
    hooks/  0.000 GB; 14 files; 0 subdirs
    info/  0.000 GB; 2 files; 0 subdirs
    logs/  0.000 GB; 8 files; 5 subdirs
      refs/  0.000 GB; 7 files; 4 subdirs
        heads/  0.000 GB; 2 files; 0 subdirs [collapsed]
        remotes/  0.000 GB; 4 files; 2 subdirs [collapsed]
    objects/  15.885 GB; 3359 files; 258 subdirs [collapsed]
    refs/  0.000 GB; 9 files; 25 subdirs
      codex/  0.000 GB; 6 files; 19 subdirs
        turn-diffs/  0.000 GB; 6 files; 18 subdirs [collapsed]
      heads/  0.000 GB; 1 files; 0 subdirs
      remotes/  0.000 GB; 2 files; 2 subdirs
        origin/  0.000 GB; 2 files; 1 subdirs [collapsed]
      tags/  0.000 GB; 0 files; 0 subdirs
  .github/  0.000 GB; 1 files; 0 subdirs
  .pytest_cache/  0.000 GB; 5 files; 2 subdirs
    v/  0.000 GB; 2 files; 1 subdirs
      cache/  0.000 GB; 2 files; 0 subdirs
  .vscode/  0.000 GB; 1 files; 0 subdirs
  00_experiments/  7.235 GB; 96779 files; 1234 subdirs
    adaptive_fusion_robustness/  0.892 GB; 82464 files; 143 subdirs
      code/  0.000 GB; 15 files; 0 subdirs
      results/  0.892 GB; 82443 files; 140 subdirs
        run_01/  0.892 GB; 82443 files; 139 subdirs [collapsed]
      tests/  0.000 GB; 3 files; 0 subdirs
    completed_reassemble_work_git_handoff_01/  0.000 GB; 40 files; 4 subdirs
      before/  0.000 GB; 9 files; 0 subdirs
      checks/  0.000 GB; 5 files; 0 subdirs
      commits/  0.000 GB; 15 files; 0 subdirs
      selection/  0.000 GB; 6 files; 0 subdirs
    frozen32_vs_finetuned32_fusion_diagnosis/  3.626 GB; 1096 files; 206 subdirs
      code/  0.000 GB; 7 files; 0 subdirs
      data_manifests/  0.017 GB; 4 files; 0 subdirs
      existing_evidence/  0.000 GB; 4 files; 0 subdirs
      git_handoff/  0.001 GB; 14 files; 0 subdirs
      results/  3.607 GB; 1034 files; 184 subdirs
        checks/  0.000 GB; 10 files; 0 subdirs [collapsed]
        comparison/  0.002 GB; 26 files; 1 subdirs [collapsed]
        matplotlib_cache/  0.000 GB; 1 files; 0 subdirs [collapsed]
        provenance/  0.001 GB; 25 files; 1 subdirs [collapsed]
        seed_20261023/  3.496 GB; 510 files; 88 subdirs [collapsed]
        seed_42/  0.090 GB; 460 files; 88 subdirs [collapsed]
      tests/  0.001 GB; 24 files; 16 subdirs
        synthetic_report_fixture/  0.001 GB; 22 files; 15 subdirs [collapsed]
    fusion_noise_test/  0.159 GB; 1939 files; 195 subdirs
      code/  0.000 GB; 9 files; 0 subdirs
      results/  0.159 GB; 1923 files; 192 subdirs
        run_01/  0.027 GB; 207 files; 28 subdirs [collapsed]
        run_02/  0.132 GB; 1716 files; 162 subdirs [collapsed]
      tests/  0.000 GB; 1 files; 0 subdirs
    rt_detr_encoder_comparison/  0.419 GB; 9706 files; 287 subdirs
      code/  0.000 GB; 7 files; 0 subdirs
      results/  0.419 GB; 9694 files; 284 subdirs
        run_01/  0.419 GB; 9694 files; 283 subdirs [collapsed]
      tests/  0.000 GB; 1 files; 0 subdirs
    visual_backbone_one_day/  2.137 GB; 1534 files; 393 subdirs
      fine_tuning_diagnostics_01/  0.021 GB; 54 files; 8 subdirs
        checks/  0.000 GB; 7 files; 0 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 5 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 4 files; 0 subdirs [collapsed]
        provenance/  0.017 GB; 9 files; 1 subdirs [collapsed]
        source/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.004 GB; 21 files; 0 subdirs [collapsed]
      fusion_AP_explanation_addendum_01/  0.048 GB; 121 files; 76 subdirs
        checks/  0.000 GB; 5 files; 0 subdirs [collapsed]
        original_inputs/  0.017 GB; 65 files; 67 subdirs [collapsed]
        provenance/  0.017 GB; 10 files; 0 subdirs [collapsed]
        reused/  0.000 GB; 19 files; 3 subdirs [collapsed]
        source/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.004 GB; 13 files; 0 subdirs [collapsed]
      run_01_two_epoch_finetuning/  2.068 GB; 1358 files; 306 subdirs
        checkpoint_resumption_01/  0.118 GB; 21 files; 4 subdirs [collapsed]
        checks/  0.000 GB; 19 files; 0 subdirs [collapsed]
        comparison/  0.019 GB; 20 files; 1 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        continuation_status_checks/  0.000 GB; 1 files; 0 subdirs [collapsed]
        data_manifests/  0.024 GB; 10 files; 0 subdirs [collapsed]
        final_evaluation_and_reporting_01/  0.015 GB; 14 files; 4 subdirs [collapsed]
        fine_tuned_16_frames/  0.875 GB; 270 files; 60 subdirs [collapsed]
        fine_tuned_32_frames/  0.875 GB; 270 files; 60 subdirs [collapsed]
        frozen_16_frames/  0.035 GB; 265 files; 60 subdirs [collapsed]
        frozen_32_frames/  0.035 GB; 270 files; 60 subdirs [collapsed]
        logs/  0.001 GB; 5 files; 0 subdirs [collapsed]
        provenance/  0.011 GB; 36 files; 5 subdirs [collapsed]
        sensor_reference/  0.011 GB; 125 files; 30 subdirs [collapsed]
        shared_cache/  0.000 GB; 0 files; 0 subdirs [collapsed]
        source/  0.000 GB; 19 files; 0 subdirs [collapsed]
        temporary/  0.000 GB; 1 files; 5 subdirs [collapsed]
  26.10.2026_feedback_experiments/  4.247 GB; 5602 files; 144 subdirs
    26102026_phase1_full_cnn_seed_stability/  2.719 GB; 5422 files; 107 subdirs
      26102026_bestfit_100epoch_frozen_vs_full_cnn/  0.612 GB; 380 files; 12 subdirs
        26102026_configuration/  0.000 GB; 2 files; 0 subdirs [collapsed]
        26102026_evidence/  0.000 GB; 10 files; 0 subdirs [collapsed]
        26102026_execution/  0.611 GB; 358 files; 6 subdirs [collapsed]
        26102026_reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        26102026_source/  0.000 GB; 4 files; 0 subdirs [collapsed]
        26102026_tests/  0.000 GB; 1 files; 0 subdirs [collapsed]
      26102026_c_only_20epoch_revision_01/  0.182 GB; 45 files; 10 subdirs
        26102026_configuration/  0.000 GB; 1 files; 0 subdirs [collapsed]
        26102026_evidence/  0.000 GB; 8 files; 0 subdirs [collapsed]
        26102026_execution/  0.181 GB; 23 files; 4 subdirs [collapsed]
        26102026_reports/  0.000 GB; 6 files; 0 subdirs [collapsed]
        26102026_source/  0.000 GB; 4 files; 0 subdirs [collapsed]
        26102026_tests/  0.000 GB; 1 files; 0 subdirs [collapsed]
      26102026_configuration/  0.000 GB; 1 files; 0 subdirs
      26102026_evidence/  0.019 GB; 17 files; 0 subdirs
      26102026_execution/  1.907 GB; 4955 files; 77 subdirs
        26102026_main_run_01/  1.907 GB; 4955 files; 76 subdirs [collapsed]
      26102026_reports/  0.000 GB; 7 files; 0 subdirs
      26102026_source/  0.000 GB; 12 files; 0 subdirs
      26102026_tests/  0.000 GB; 2 files; 0 subdirs
    configs/  0.000 GB; 1 files; 0 subdirs
    runs/  1.528 GB; 167 files; 32 subdirs
      20261026T212550Z-934ad6c7/  0.566 GB; 63 files; 8 subdirs
        cache/  0.226 GB; 24 files; 0 subdirs [collapsed]
        checks/  0.340 GB; 7 files; 0 subdirs [collapsed]
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 5 files; 0 subdirs [collapsed]
        provenance_source/  0.000 GB; 5 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261026T213457Z-stream-a8efd0e8/  0.359 GB; 33 files; 7 subdirs
        checks/  0.340 GB; 6 files; 0 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        logs/  0.019 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 4 files; 0 subdirs [collapsed]
        provenance_source/  0.000 GB; 5 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 4 files; 0 subdirs [collapsed]
      20261026T214258Z-stream-ca88704c/  0.359 GB; 37 files; 7 subdirs
        checks/  0.340 GB; 6 files; 0 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        logs/  0.019 GB; 8 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 4 files; 0 subdirs [collapsed]
        provenance_source/  0.000 GB; 7 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 2 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 5 files; 0 subdirs [collapsed]
      20261026T215300Z-selected16-e15865ad/  0.243 GB; 34 files; 6 subdirs
        checks/  0.227 GB; 9 files; 0 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        logs/  0.015 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 5 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
    source/  0.000 GB; 8 files; 0 subdirs
    tests/  0.000 GB; 1 files; 0 subdirs
  CROSS_DATASET_COMPARISON/  2.712 GB; 8761 files; 2371 subdirs
    INDEPENDENT_REVIEW_PACKAGE/  2.710 GB; 8597 files; 2345 subdirs [collapsed]
    configs/  0.000 GB; 4 files; 0 subdirs
    logs/  0.000 GB; 21 files; 0 subdirs
    provenance/  0.001 GB; 104 files; 18 subdirs
      source_snapshot/  0.001 GB; 74 files; 17 subdirs
        CROSS_DATASET_COMPARISON/  0.000 GB; 22 files; 3 subdirs [collapsed]
        HANDOVER/  0.000 GB; 5 files; 2 subdirs [collapsed]
        MSM/  0.001 GB; 44 files; 7 subdirs [collapsed]
        src/  0.000 GB; 3 files; 1 subdirs [collapsed]
    src/  0.000 GB; 21 files; 2 subdirs
      external_eval/  0.000 GB; 21 files; 1 subdirs
        __pycache__/  0.000 GB; 3 files; 0 subdirs [collapsed]
    tests/  0.000 GB; 4 files; 0 subdirs
  DATASET_RESEARCH/  0.000 GB; 2 files; 0 subdirs
  HANDOVER/  17.335 GB; 17370 files; 1311 subdirs
    01_raw_dataset/  16.848 GB; 13146 files; 1207 subdirs
      official_dataset/  16.780 GB; 13092 files; 1199 subdirs
        archives/  13.012 GB; 20 files; 0 subdirs [collapsed]
        data/  3.697 GB; 8246 files; 1184 subdirs [collapsed]
        labels/  0.002 GB; 1178 files; 6 subdirs [collapsed]
        sample/  0.069 GB; 3648 files; 5 subdirs [collapsed]
      source_evidence/  0.068 GB; 52 files; 6 subdirs
        author_code/  0.000 GB; 4 files; 4 subdirs [collapsed]
        receipts/  0.000 GB; 20 files; 0 subdirs [collapsed]
    02_labels_and_alignment/  0.010 GB; 1189 files; 1 subdirs
      trial_checkpoints/  0.007 GB; 1178 files; 0 subdirs
    03_processed_model_inputs/  0.001 GB; 5 files; 3 subdirs
      sensor_features/  0.000 GB; 1 files; 0 subdirs
      split_manifests/  0.000 GB; 2 files; 0 subdirs
      visual_features/  0.000 GB; 0 files; 0 subdirs
    04_experiment_protocol/  0.000 GB; 4 files; 0 subdirs
    05_trained_models/  0.000 GB; 1 files; 5 subdirs
      adaptive_fusion_if_applicable/  0.000 GB; 0 files; 0 subdirs
      averaging_fusion/  0.000 GB; 0 files; 0 subdirs
      f2_fusion/  0.000 GB; 0 files; 0 subdirs
      sensor_only/  0.000 GB; 0 files; 0 subdirs
      visual_only/  0.000 GB; 0 files; 0 subdirs
    06_evaluation_results/  0.000 GB; 1 files; 5 subdirs
      calibration/  0.000 GB; 0 files; 0 subdirs
      confusion_matrices/  0.000 GB; 0 files; 0 subdirs
      metrics/  0.000 GB; 0 files; 0 subdirs
      precision_recall_curves/  0.000 GB; 0 files; 0 subdirs
      predictions/  0.000 GB; 0 files; 0 subdirs
    07_robustness_experiments/  0.000 GB; 1 files; 4 subdirs
      comparison_reports/  0.000 GB; 0 files; 0 subdirs
      degraded_video/  0.000 GB; 0 files; 0 subdirs
      missing_modalities/  0.000 GB; 0 files; 0 subdirs
      noisy_sensors/  0.000 GB; 0 files; 0 subdirs
    08_visual_examples_and_eda/  0.000 GB; 1 files; 3 subdirs
      prediction_examples/  0.000 GB; 0 files; 0 subdirs
      sample_previews/  0.000 GB; 0 files; 0 subdirs
      sensor_visualizations/  0.000 GB; 0 files; 0 subdirs
    09_final_reports/  0.001 GB; 15 files; 0 subdirs
    99_preserved_previous_work/  0.000 GB; 1 files; 0 subdirs
    experiments/  0.474 GB; 2992 files; 68 subdirs
      common_support_v2/  0.474 GB; 2992 files; 67 subdirs
        02_labels_and_alignment/  0.014 GB; 1189 files; 1 subdirs [collapsed]
        03_processed_model_inputs/  0.311 GB; 1221 files; 5 subdirs [collapsed]
        04_experiment_protocol/  0.000 GB; 6 files; 0 subdirs [collapsed]
        05_trained_models/  0.002 GB; 18 files; 23 subdirs [collapsed]
        06_evaluation_results/  0.002 GB; 53 files; 12 subdirs [collapsed]
        07_robustness_experiments/  0.000 GB; 2 files; 1 subdirs [collapsed]
        08_visual_examples_and_eda/  0.144 GB; 499 files; 17 subdirs [collapsed]
        logs/  0.000 GB; 3 files; 0 subdirs [collapsed]
    logs/  0.001 GB; 6 files; 0 subdirs
    src/  0.000 GB; 5 files; 1 subdirs
      __pycache__/  0.000 GB; 1 files; 0 subdirs
    tests/  0.000 GB; 1 files; 0 subdirs
  MILLING DATASET/  4.359 GB; 2586 files; 388 subdirs
    .tools/  0.080 GB; 21 files; 5 subdirs
      imageio_ffmpeg/  0.080 GB; 14 files; 3 subdirs
        __pycache__/  0.000 GB; 5 files; 0 subdirs [collapsed]
        binaries/  0.080 GB; 4 files; 1 subdirs [collapsed]
      imageio_ffmpeg-0.6.0.dist-info/  0.000 GB; 7 files; 0 subdirs
    PILOT_FINDINGS/  0.005 GB; 97 files; 14 subdirs
      01_DATASET_AND_LABEL_AUDIT/  0.000 GB; 7 files; 1 subdirs
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
      02_VIDEO_ALIGNMENT_AND_MODALITIES/  0.000 GB; 9 files; 2 subdirs
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
      03_ARCHITECTURE_IMPLEMENTATION_SMOKE/  0.000 GB; 7 files; 2 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
      04_BLOCKED_EVALUATION_AND_TRANSFER/  0.000 GB; 7 files; 1 subdirs
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
      05_FULL_LABORATORY_FEASIBILITY/  0.005 GB; 61 files; 2 subdirs
        diagnostics/  0.005 GB; 52 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
      06_MATCHED_CUT_REVIEW/  0.000 GB; 2 files; 0 subdirs
    configs/  0.000 GB; 3 files; 0 subdirs
    data/  3.732 GB; 516 files; 76 subdirs
      raw/  3.732 GB; 516 files; 75 subdirs
        msm/  3.732 GB; 516 files; 74 subdirs [collapsed]
    runs/  4.271 GB; 1896 files; 283 subdirs
      20261026T230520276818Z-stage1/  0.004 GB; 44 files; 7 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        evidence/  0.001 GB; 12 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 4 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 12 files; 0 subdirs [collapsed]
        reproduction/  0.001 GB; 8 files; 2 subdirs [collapsed]
      20261026T233709740813Z-stage2/  1.298 GB; 177 files; 19 subdirs
        cache/  0.065 GB; 34 files; 0 subdirs [collapsed]
        config/  0.000 GB; 6 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 29 files; 1 subdirs [collapsed]
        figures/  0.034 GB; 40 files; 2 subdirs [collapsed]
        logs/  0.000 GB; 14 files; 0 subdirs [collapsed]
        manifests/  0.001 GB; 18 files; 0 subdirs [collapsed]
        staging/  1.197 GB; 35 files; 9 subdirs [collapsed]
      20261027T001047876764Z-stage2-validated/  0.101 GB; 120 files; 8 subdirs
        cache/  0.065 GB; 34 files; 0 subdirs [collapsed]
        config/  0.000 GB; 6 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 5 files; 0 subdirs [collapsed]
        figures/  0.034 GB; 35 files; 2 subdirs [collapsed]
        logs/  0.000 GB; 10 files; 0 subdirs [collapsed]
        manifests/  0.001 GB; 23 files; 0 subdirs [collapsed]
      20261027T003527238586Z-stage3/  0.001 GB; 23 files; 5 subdirs
        cache/  0.000 GB; 2 files; 0 subdirs [collapsed]
        checkpoints/  0.000 GB; 1 files; 0 subdirs [collapsed]
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 11 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
      20261027T005343579234Z-stage4/  0.000 GB; 34 files; 5 subdirs
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 5 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 1 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 20 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 0 files; 0 subdirs [collapsed]
      20261027T010816468715Z-stage5/  0.000 GB; 6 files; 4 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 2 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 0 files; 0 subdirs [collapsed]
      20261027T011419561081Z-stage5-validated/  0.001 GB; 25 files; 5 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 3 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 1 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 14 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 0 files; 0 subdirs [collapsed]
      20261027T013606719154Z-stage5-full-lab/  2.594 GB; 737 files; 178 subdirs
        cache/  0.000 GB; 0 files; 0 subdirs [collapsed]
        config/  0.000 GB; 3 files; 0 subdirs [collapsed]
        evidence/  0.001 GB; 215 files; 0 subdirs [collapsed]
        experiments/  0.045 GB; 296 files; 113 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 8 files; 0 subdirs [collapsed]
        manifests/  0.009 GB; 7 files; 0 subdirs [collapsed]
        staging/  2.534 GB; 204 files; 57 subdirs [collapsed]
      20261027T015205931708Z-stage5-full-lab-validated/  0.015 GB; 56 files; 11 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 27 files; 6 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 1 files; 0 subdirs [collapsed]
        manifests/  0.010 GB; 16 files; 0 subdirs [collapsed]
      20261027T190627566058Z-matched-visual-review/  0.019 GB; 139 files; 14 subdirs
        config/  0.000 GB; 0 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 8 files; 0 subdirs [collapsed]
        frames/  0.018 GB; 128 files; 8 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 0 files; 0 subdirs [collapsed]
      20261027T190717486889Z-matched-visual-review/  0.238 GB; 535 files; 16 subdirs
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        evidence/  0.000 GB; 0 files; 0 subdirs [collapsed]
        figures/  0.015 GB; 36 files; 0 subdirs [collapsed]
        frames/  0.059 GB; 480 files; 10 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 4 files; 0 subdirs [collapsed]
    source/  0.001 GB; 44 files; 3 subdirs
      __pycache__/  0.000 GB; 4 files; 0 subdirs
      msm/  0.000 GB; 12 files; 0 subdirs
      stage2/  0.000 GB; 13 files; 0 subdirs
    tests/  0.000 GB; 7 files; 0 subdirs
  MSM/  1.434 GB; 6708 files; 1023 subdirs
    01_raw_dataset/  0.000 GB; 4 files; 1 subdirs
      source_evidence/  0.000 GB; 2 files; 0 subdirs
    02_labels_and_alignment/  0.014 GB; 11 files; 0 subdirs
    03_processed_model_inputs/  1.053 GB; 4341 files; 5 subdirs
      sensor_features/  0.046 GB; 541 files; 1 subdirs
        corruptions/  0.043 GB; 540 files; 0 subdirs [collapsed]
      split_manifests/  0.002 GB; 2 files; 0 subdirs
      visual_features/  1.002 GB; 3796 files; 1 subdirs [collapsed]
    04_experiment_protocol/  0.000 GB; 8 files; 0 subdirs
    05_trained_models/  0.212 GB; 1566 files; 869 subdirs [collapsed]
    06_evaluation_results/  0.111 GB; 562 files; 114 subdirs [collapsed]
    07_robustness_experiments/  0.001 GB; 3 files; 4 subdirs [collapsed]
    08_visual_examples_and_eda/  0.042 GB; 181 files; 17 subdirs
      prediction_examples/  0.042 GB; 177 files; 14 subdirs
        example_01/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_02/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_03/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_04/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_05/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_06/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_07/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_08/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_09/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_10/  0.002 GB; 3 files; 0 subdirs [collapsed]
        example_11/  0.005 GB; 35 files; 0 subdirs [collapsed]
        example_12/  0.006 GB; 35 files; 0 subdirs [collapsed]
        example_13/  0.005 GB; 35 files; 0 subdirs [collapsed]
        example_14/  0.006 GB; 35 files; 0 subdirs [collapsed]
      sample_previews/  0.000 GB; 0 files; 0 subdirs
      sensor_visualizations/  0.000 GB; 0 files; 0 subdirs
    09_final_reports/  0.001 GB; 15 files; 0 subdirs
    99_preserved_previous_work/  0.000 GB; 0 files; 0 subdirs
    logs/  0.000 GB; 10 files; 0 subdirs
    src/  0.000 GB; 3 files; 0 subdirs
    tests/  0.000 GB; 1 files; 0 subdirs
  REBOOT/  3.590 GB; 1905 files; 304 subdirs
    00_dataset_overview/  0.000 GB; 4 files; 0 subdirs
    01_raw_dataset/  2.957 GB; 256 files; 215 subdirs
      official_release/  2.957 GB; 238 files; 210 subdirs
        16mm-bar_install/  0.001 GB; 7 files; 4 subdirs [collapsed]
        16mm-bar_recovery_install/  0.001 GB; 10 files; 4 subdirs [collapsed]
        16mm-bar_recovery_remove/  0.000 GB; 5 files; 4 subdirs [collapsed]
        16mm-bar_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        16mm-cylinder_install/  0.805 GB; 11 files; 13 subdirs [collapsed]
        16mm-cylinder_recovery_install/  0.001 GB; 6 files; 4 subdirs [collapsed]
        16mm-cylinder_recovery_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        16mm-cylinder_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        HAN10E_recovery_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        HAN10e-install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        M12-fastener_install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        M12-fastener_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        RJ45_recovery_remove/  0.001 GB; 6 files; 4 subdirs [collapsed]
        USB-A_recovery_install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        USB-A_recovery_remove/  0.001 GB; 6 files; 4 subdirs [collapsed]
        USBC_recovery_remove/  0.001 GB; 6 files; 4 subdirs [collapsed]
        han10e_recovery_install/  0.001 GB; 6 files; 4 subdirs [collapsed]
        han10e_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        m12_recovery_install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        m12_recovery_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        nema1-15-plug_install/  0.001 GB; 6 files; 4 subdirs [collapsed]
        nema1-15-plug_recovery_install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        nema1-15-plug_recovery_remove2/  0.001 GB; 6 files; 4 subdirs [collapsed]
        nema1-15-plug_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        rca_install/  0.001 GB; 6 files; 4 subdirs [collapsed]
        rca_recovery_install/  0.000 GB; 5 files; 4 subdirs [collapsed]
        rca_recovery_install1/  0.000 GB; 5 files; 4 subdirs [collapsed]
        rca_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        rj45-install/  0.001 GB; 8 files; 4 subdirs [collapsed]
        rj45_recovery_install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        rj45_remove/  0.001 GB; 7 files; 4 subdirs [collapsed]
        sample_recovery-demonstration/  2.132 GB; 27 files; 15 subdirs [collapsed]
        usb-c_install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        usb-c_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        usbA-install/  0.001 GB; 5 files; 4 subdirs [collapsed]
        usbA_remove/  0.001 GB; 5 files; 4 subdirs [collapsed]
        usbc_recovery_install/  0.000 GB; 5 files; 4 subdirs [collapsed]
        usbc_recovery_install2/  0.000 GB; 5 files; 4 subdirs [collapsed]
      remote_range_evidence/  0.000 GB; 16 files; 3 subdirs
        16mm-cylinder_install/  0.000 GB; 16 files; 2 subdirs [collapsed]
    02_labels_and_annotations/  0.000 GB; 4 files; 0 subdirs
    03_video_sensor_alignment/  0.010 GB; 40 files; 4 subdirs
      decoder_probe/  0.005 GB; 17 files; 0 subdirs
      numerical_projections/  0.004 GB; 20 files; 2 subdirs
        16mm-cylinder_install/  0.001 GB; 4 files; 0 subdirs [collapsed]
        sample_recovery-demonstration/  0.003 GB; 16 files; 0 subdirs [collapsed]
    04_visual_failure_review/  0.620 GB; 1455 files; 52 subdirs
      galleries/  0.620 GB; 1451 files; 51 subdirs
        blinded_pilot_v1/  0.620 GB; 1451 files; 50 subdirs [collapsed]
    05_architecture_compatibility/  0.000 GB; 0 files; 0 subdirs
    06_evaluation_feasibility/  0.000 GB; 0 files; 0 subdirs
    07_research_decision/  0.000 GB; 0 files; 0 subdirs
    runs/  0.002 GB; 141 files; 22 subdirs
      20261028T113139848361Z-independent-feasibility-v1/  0.002 GB; 141 files; 21 subdirs
        config/  0.000 GB; 0 files; 0 subdirs [collapsed]
        evidence/  0.002 GB; 57 files; 15 subdirs [collapsed]
        logs/  0.000 GB; 80 files; 1 subdirs [collapsed]
        manifests/  0.000 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 0 files; 0 subdirs [collapsed]
    src/  0.000 GB; 4 files; 0 subdirs
    tests/  0.000 GB; 0 files; 0 subdirs
  STORAGE_AUDIT/  0.000 GB; 10 files; 1 subdirs
    20261028T114917Z/  0.000 GB; 10 files; 0 subdirs
  archive/  0.000 GB; 9 files; 1 subdirs
    legacy_intel_welding_dataset/  0.000 GB; 8 files; 0 subdirs
  artifacts/  0.504 GB; 481 files; 56 subdirs
    intel_welding/  0.002 GB; 40 files; 9 subdirs
      audits/  0.002 GB; 36 files; 3 subdirs
        foundation_runs/  0.001 GB; 28 files; 2 subdirs [collapsed]
      features/  0.000 GB; 0 files; 0 subdirs
      figures/  0.000 GB; 0 files; 0 subdirs
      predictions/  0.000 GB; 0 files; 0 subdirs
      splits/  0.000 GB; 4 files; 0 subdirs
      tables/  0.000 GB; 0 files; 0 subdirs
    phm2026/  0.000 GB; 16 files; 1 subdirs
      downloads/  0.000 GB; 6 files; 0 subdirs
    presentation/  0.063 GB; 83 files; 6 subdirs
      reassemble_dataset_assets/  0.063 GB; 83 files; 5 subdirs
        20261016T092947Z/  0.063 GB; 83 files; 4 subdirs [collapsed]
    reassemble/  0.002 GB; 54 files; 6 subdirs
      audits/  0.002 GB; 32 files; 4 subdirs
        storage_runs/  0.000 GB; 6 files; 1 subdirs [collapsed]
        triage_runs/  0.000 GB; 9 files; 1 subdirs [collapsed]
      reports/  0.000 GB; 22 files; 0 subdirs
    thesis/  0.437 GB; 288 files; 29 subdirs
      FINAL_VALIDITY_AUDIT/  0.018 GB; 124 files; 17 subdirs
        20260928T032231Z/  0.018 GB; 124 files; 16 subdirs [collapsed]
      HUMAN_REVIEW_INTERFACE/  0.419 GB; 140 files; 4 subdirs
        20260929T142000Z/  0.209 GB; 136 files; 3 subdirs [collapsed]
      REVIEW_RESULTS_BUNDLE/  0.000 GB; 20 files; 5 subdirs
        20260929T152809Z/  0.000 GB; 19 files; 4 subdirs [collapsed]
  configs/  0.000 GB; 31 files; 6 subdirs
    datasets/  0.000 GB; 1 files; 0 subdirs
    experiments/  0.000 GB; 21 files; 0 subdirs
    intel_welding/  0.000 GB; 1 files; 0 subdirs
    phm2026/  0.000 GB; 1 files; 0 subdirs
    reassemble/  0.000 GB; 7 files; 1 subdirs
      additional_improvements/  0.000 GB; 1 files; 0 subdirs
  data/  26.939 GB; 8296 files; 8319 subdirs
    Full Dataset/  26.877 GB; 8286 files; 8316 subdirs [collapsed]
    paderborn/  0.004 GB; 3 files; 0 subdirs
    rawvib/  0.058 GB; 6 files; 0 subdirs
  docs/  0.074 GB; 433 files; 111 subdirs
    intel_welding/  0.000 GB; 5 files; 0 subdirs
    maintenance/  0.041 GB; 14 files; 2 subdirs
      cache_cleanup/  0.041 GB; 13 files; 1 subdirs
        20261026T211622Z/  0.041 GB; 13 files; 0 subdirs [collapsed]
    phm2026/  0.000 GB; 1 files; 0 subdirs
    planning/  0.000 GB; 17 files; 0 subdirs
    reassemble/  0.000 GB; 17 files; 0 subdirs
    repository_restructure/  0.021 GB; 224 files; 11 subdirs
      baseline/  0.009 GB; 11 files; 6 subdirs
        documentation_before/  0.000 GB; 3 files; 5 subdirs [collapsed]
      compatibility_runs/  0.011 GB; 160 files; 3 subdirs
        20261006T182404Z/  0.011 GB; 160 files; 2 subdirs [collapsed]
    thesis/  0.000 GB; 29 files; 0 subdirs
    thesis_research_direction/  0.000 GB; 15 files; 0 subdirs
    thesis_review_handoff/  0.010 GB; 107 files; 89 subdirs
      source_review_pack/  0.010 GB; 102 files; 88 subdirs
        20261006T202247676015Z/  0.010 GB; 102 files; 87 subdirs [collapsed]
  experiments/  0.370 GB; 323 files; 55 subdirs
    exp_a_initial_eda_r1_r3_r5/  0.369 GB; 279 files; 17 subdirs
      configs/  0.000 GB; 1 files; 0 subdirs
      outputs/  0.369 GB; 275 files; 14 subdirs
        advanced_eda/  0.368 GB; 256 files; 12 subdirs [collapsed]
        basic_eda/  0.001 GB; 19 files; 0 subdirs [collapsed]
      scripts/  0.000 GB; 0 files; 0 subdirs
    exp_b_eda_expA&F/  0.000 GB; 0 files; 0 subdirs
    phm2026/  0.000 GB; 13 files; 8 subdirs
      01_rtdetr_scalar_regression/  0.000 GB; 10 files; 7 subdirs
        00_data_overview/  0.000 GB; 1 files; 0 subdirs [collapsed]
        01_data_preprocessing/  0.000 GB; 1 files; 0 subdirs [collapsed]
        02_model/  0.000 GB; 4 files; 3 subdirs [collapsed]
        03_model_outputs_and_results/  0.000 GB; 1 files; 0 subdirs [collapsed]
    phm2026_dataset_description/  0.000 GB; 1 files; 0 subdirs
    phm2026_rtdetr_feasibility/  0.000 GB; 1 files; 0 subdirs
    reassemble/  0.000 GB; 28 files; 24 subdirs
      01_rtdetr_baseline/  0.000 GB; 8 files; 7 subdirs
        00_data_overview/  0.000 GB; 1 files; 0 subdirs [collapsed]
        01_data_preprocessing/  0.000 GB; 1 files; 0 subdirs [collapsed]
        02_model/  0.000 GB; 4 files; 3 subdirs [collapsed]
        03_model_outputs_and_results/  0.000 GB; 1 files; 0 subdirs [collapsed]
      02_patchtst_baseline/  0.000 GB; 8 files; 7 subdirs
        00_data_overview/  0.000 GB; 1 files; 0 subdirs [collapsed]
        01_data_preprocessing/  0.000 GB; 1 files; 0 subdirs [collapsed]
        02_model/  0.000 GB; 4 files; 3 subdirs [collapsed]
        03_model_outputs_and_results/  0.000 GB; 1 files; 0 subdirs [collapsed]
      03_core_fusion/  0.000 GB; 9 files; 7 subdirs
        00_data_overview/  0.000 GB; 1 files; 0 subdirs [collapsed]
        01_data_preprocessing/  0.000 GB; 1 files; 0 subdirs [collapsed]
        02_model/  0.000 GB; 4 files; 3 subdirs [collapsed]
        03_model_outputs_and_results/  0.000 GB; 2 files; 0 subdirs [collapsed]
  ma_thesis_env/  7.215 GB; 60656 files; 7579 subdirs
    bin/  0.000 GB; 102 files; 1 subdirs
      __pycache__/  0.000 GB; 1 files; 0 subdirs
    etc/  0.000 GB; 6 files; 5 subdirs
      jupyter/  0.000 GB; 6 files; 4 subdirs
        jupyter_notebook_config.d/  0.000 GB; 1 files; 0 subdirs [collapsed]
        jupyter_server_config.d/  0.000 GB; 4 files; 0 subdirs [collapsed]
        nbconfig/  0.000 GB; 1 files; 1 subdirs [collapsed]
    include/  0.000 GB; 0 files; 1 subdirs
      python3.12/  0.000 GB; 0 files; 0 subdirs
    lib/  7.167 GB; 60069 files; 7487 subdirs
      python3.12/  7.167 GB; 60069 files; 7486 subdirs
        site-packages/  7.167 GB; 60069 files; 7485 subdirs [collapsed]
    share/  0.048 GB; 477 files; 80 subdirs [collapsed]
  parth_ws_bootstrap/  0.471 GB; 11751 files; 1349 subdirs
    00_Experimentaitons/  0.000 GB; 3 files; 0 subdirs
    00_experimentation/  0.456 GB; 9542 files; 497 subdirs
      visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/  0.456 GB; 9542 files; 496 subdirs
        run_01/  0.456 GB; 9542 files; 495 subdirs [collapsed]
    controller_builds/  0.010 GB; 1534 files; 604 subdirs
      20261019T220330Z/  0.010 GB; 1534 files; 603 subdirs
        config/  0.000 GB; 3 files; 0 subdirs [collapsed]
        docs/  0.000 GB; 3 files; 0 subdirs [collapsed]
        evidence/  0.008 GB; 1449 files; 573 subdirs [collapsed]
        fixtures/  0.000 GB; 1 files; 0 subdirs [collapsed]
        review/  0.000 GB; 1 files; 0 subdirs [collapsed]
        runner/  0.000 GB; 3 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 60 files; 20 subdirs [collapsed]
        schemas/  0.000 GB; 6 files; 0 subdirs [collapsed]
        state/  0.001 GB; 3 files; 0 subdirs [collapsed]
        tests/  0.000 GB; 1 files; 0 subdirs [collapsed]
    outputs/  0.000 GB; 31 files; 11 subdirs
      20261019T213827Z-audit/  0.000 GB; 31 files; 10 subdirs
        00_state/  0.000 GB; 7 files; 0 subdirs [collapsed]
        01_environment/  0.000 GB; 3 files; 0 subdirs [collapsed]
        02_source/  0.000 GB; 2 files; 0 subdirs [collapsed]
        03_history/  0.000 GB; 4 files; 0 subdirs [collapsed]
        04_plan/  0.000 GB; 5 files; 1 subdirs [collapsed]
        05_review/  0.000 GB; 5 files; 2 subdirs [collapsed]
        06_approval/  0.000 GB; 4 files; 0 subdirs [collapsed]
    prompts/  0.000 GB; 2 files; 0 subdirs
    work_sessions/  0.005 GB; 628 files; 231 subdirs
      20261019T222548Z-decision-session-fusion-evidence-literature-offline-runner/  0.005 GB; 628 files; 230 subdirs
        00_control/  0.000 GB; 5 files; 0 subdirs [collapsed]
        01_evidence/  0.000 GB; 12 files; 0 subdirs [collapsed]
        02_literature/  0.000 GB; 10 files; 0 subdirs [collapsed]
        03_runner/  0.003 GB; 586 files; 223 subdirs [collapsed]
        04_decisions/  0.000 GB; 4 files; 0 subdirs [collapsed]
        05_review/  0.000 GB; 6 files; 1 subdirs [collapsed]
  runs/  9.102 GB; 27316 files; 1408 subdirs
    _superseded/  0.645 GB; 1598 files; 83 subdirs
      phm2026_dataset_description/  0.012 GB; 103 files; 49 subdirs
        20260813T201944173814Z-ad7f9832/  0.000 GB; 11 files; 6 subdirs [collapsed]
        20260813T212817486478Z-f7c665fd/  0.000 GB; 12 files; 6 subdirs [collapsed]
        20260813T213955074760Z-bd9395ad/  0.000 GB; 16 files; 6 subdirs [collapsed]
        20260813T214347126273Z-bd9395ad/  0.001 GB; 16 files; 6 subdirs [collapsed]
        20260813T214414076201Z-bd9395ad/  0.004 GB; 16 files; 6 subdirs [collapsed]
        20260813T214454592625Z-bd9395ad/  0.005 GB; 16 files; 6 subdirs [collapsed]
        20260813T225042643949Z-7d2070cf/  0.000 GB; 16 files; 6 subdirs [collapsed]
      phm2026_image_target/  0.624 GB; 1391 files; 9 subdirs
        20260814T011051111606Z-e7600a8a/  0.624 GB; 1391 files; 8 subdirs [collapsed]
      phm2026_patchtst_baseline/  0.007 GB; 80 files; 14 subdirs
        20260911T185916319369Z-433d4154/  0.004 GB; 40 files; 6 subdirs [collapsed]
        20260911T191705540892Z-433d4154/  0.004 GB; 40 files; 6 subdirs [collapsed]
      phm2026_sensor_features/  0.002 GB; 23 files; 7 subdirs
        20260814T121112307304Z-4016432b/  0.002 GB; 23 files; 6 subdirs [collapsed]
    intel_welding/  0.002 GB; 18 files; 18 subdirs
      20261016T105310968587Z-dataset-eda/  0.002 GB; 18 files; 17 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 4 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        media/  0.000 GB; 0 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 2 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 4 files; 10 subdirs [collapsed]
        tables/  0.000 GB; 1 files; 0 subdirs [collapsed]
    phm2026/  0.002 GB; 24 files; 27 subdirs
      20261016T105310968729Z-dataset-eda/  0.002 GB; 16 files; 17 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 2 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        media/  0.000 GB; 0 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 2 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 4 files; 10 subdirs [collapsed]
        tables/  0.000 GB; 1 files; 0 subdirs [collapsed]
      20261016T110121528469Z-dataset-eda/  0.000 GB; 8 files; 8 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 2 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        media/  0.000 GB; 0 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 1 files; 1 subdirs [collapsed]
        tables/  0.000 GB; 1 files; 0 subdirs [collapsed]
    phm2026_dataset_description/  0.172 GB; 99 files; 42 subdirs
      20260813T202043619114Z-ad7f9832/  0.004 GB; 11 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.004 GB; 4 files; 0 subdirs [collapsed]
      20260813T212734652736Z-f7c665fd/  0.039 GB; 12 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.039 GB; 4 files; 0 subdirs [collapsed]
      20260813T215718624432Z-bd9395ad/  0.004 GB; 16 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 3 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.001 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.002 GB; 5 files; 0 subdirs [collapsed]
      20260813T215756728445Z-bd9395ad/  0.005 GB; 16 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 3 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.001 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.002 GB; 5 files; 0 subdirs [collapsed]
      20260813T223944047252Z-d6474ff4/  0.120 GB; 28 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 1 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.120 GB; 19 files; 0 subdirs [collapsed]
      20260813T225147672972Z-7d2070cf/  0.000 GB; 16 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 2 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 2 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 8 files; 0 subdirs [collapsed]
    phm2026_evaluation/  0.001 GB; 11 files; 7 subdirs
      20260814T015914190145Z-4423f1fa/  0.001 GB; 11 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.001 GB; 4 files; 0 subdirs [collapsed]
    phm2026_fusion_latefusion/  0.000 GB; 6 files; 7 subdirs
      20260912T054016807597Z-e1911d4f/  0.000 GB; 6 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 2 files; 0 subdirs [collapsed]
    phm2026_image_target/  1.254 GB; 2782 files; 18 subdirs
      20260814T012054997053Z-e195f6d9/  0.628 GB; 1391 files; 8 subdirs
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        figures/  0.007 GB; 47 files; 1 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
        overlays/  0.618 GB; 1311 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.002 GB; 24 files; 0 subdirs [collapsed]
      20260912T052857044116Z-c936a4e3/  0.627 GB; 1391 files; 8 subdirs
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        figures/  0.007 GB; 47 files; 1 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 3 files; 0 subdirs [collapsed]
        overlays/  0.618 GB; 1311 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.002 GB; 24 files; 0 subdirs [collapsed]
    phm2026_loeo_evaluation/  0.000 GB; 8 files; 7 subdirs
      20260912T110848985882Z-e1911d4f/  0.000 GB; 8 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 4 files; 0 subdirs [collapsed]
    phm2026_model_dataset/  0.008 GB; 21 files; 7 subdirs
      20260814T013357354377Z-6b068cab/  0.008 GB; 21 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        tables/  0.008 GB; 13 files; 0 subdirs [collapsed]
    phm2026_monotonic_rescoring/  0.000 GB; 12 files; 14 subdirs
      20260912T053032782153Z-c0b86e16/  0.000 GB; 6 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 2 files; 0 subdirs [collapsed]
      20260912T053108724500Z-c0b86e16/  0.000 GB; 6 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 2 files; 0 subdirs [collapsed]
    phm2026_patchtst_baseline/  0.014 GB; 166 files; 35 subdirs
      20260814T121641338050Z-433d4154/  0.004 GB; 40 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 10 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 7 files; 0 subdirs [collapsed]
        tables/  0.001 GB; 17 files; 0 subdirs [collapsed]
      20260911T193200607744Z-433d4154/  0.004 GB; 40 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 10 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 7 files; 0 subdirs [collapsed]
        tables/  0.001 GB; 17 files; 0 subdirs [collapsed]
      20260912T052524347942Z-433d4154/  0.004 GB; 40 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 10 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 7 files; 0 subdirs [collapsed]
        tables/  0.001 GB; 17 files; 0 subdirs [collapsed]
      20260912T053924941825Z-4235307c/  0.000 GB; 6 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 2 files; 0 subdirs [collapsed]
      20260912T110509285682Z-433d4154/  0.004 GB; 40 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 10 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 7 files; 0 subdirs [collapsed]
        tables/  0.001 GB; 17 files; 0 subdirs [collapsed]
    phm2026_patchtst_results/  0.004 GB; 58 files; 7 subdirs
      20260814T122147349749Z-44877f9f/  0.004 GB; 58 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 26 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 5 files; 0 subdirs [collapsed]
        tables/  0.001 GB; 23 files; 0 subdirs [collapsed]
    phm2026_rtdetr_detection/  0.743 GB; 67 files; 25 subdirs
      20260814T042853425937Z-7f1e13af/  0.530 GB; 15 files; 13 subdirs
        checkpoints/  0.132 GB; 2 files; 0 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 0 files; 0 subdirs [collapsed]
        logs/  0.397 GB; 12 files; 6 subdirs [collapsed]
        manifests/  0.000 GB; 0 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 0 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 0 files; 0 subdirs [collapsed]
      20260814T043751107678Z-7f1e13af/  0.213 GB; 50 files; 10 subdirs
        checkpoints/  0.132 GB; 2 files; 0 subdirs [collapsed]
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 9 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 6 files; 3 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 2 files; 0 subdirs [collapsed]
        tables/  0.079 GB; 26 files; 0 subdirs [collapsed]
    phm2026_rtdetr_multitask/  0.358 GB; 85 files; 8 subdirs
      20260814T050026535618Z-9b00f099/  0.358 GB; 85 files; 7 subdirs
        checkpoints/  0.264 GB; 2 files; 0 subdirs [collapsed]
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.003 GB; 21 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 2 files; 0 subdirs [collapsed]
        tables/  0.091 GB; 56 files; 0 subdirs [collapsed]
    phm2026_rtdetr_pseudo_boxes/  0.710 GB; 2029 files; 16 subdirs
      20260814T040854991567Z-3fa0f794/  0.710 GB; 2029 files; 15 subdirs
        cache/  0.499 GB; 1992 files; 8 subdirs [collapsed]
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 8 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.209 GB; 19 files; 0 subdirs [collapsed]
    phm2026_rtdetr_r4_results/  0.000 GB; 19 files; 7 subdirs
      20260814T051127631836Z-18a96ee3/  0.000 GB; 19 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 2 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 10 files; 0 subdirs [collapsed]
    phm2026_rtdetr_regression/  0.109 GB; 61 files; 9 subdirs
      20260814T020338751021Z-d0f225c8/  0.109 GB; 61 files; 8 subdirs
        cache/  0.006 GB; 1 files; 0 subdirs [collapsed]
        checkpoints/  0.067 GB; 3 files; 0 subdirs [collapsed]
        config/  0.000 GB; 2 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 23 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.033 GB; 26 files; 0 subdirs [collapsed]
    phm2026_rtdetr_results/  0.044 GB; 78 files; 21 subdirs
      20260814T021046121152Z-d15163e7/  0.001 GB; 20 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.001 GB; 12 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 0 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20260814T021109387090Z-d15163e7/  0.022 GB; 27 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.022 GB; 16 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 8 files; 0 subdirs [collapsed]
      20260814T021150456003Z-d15163e7/  0.022 GB; 31 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.022 GB; 16 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 8 files; 0 subdirs [collapsed]
    phm2026_sensor_features/  0.059 GB; 46 files; 14 subdirs
      20260814T121146792755Z-4016432b/  0.030 GB; 23 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 4 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 5 files; 0 subdirs [collapsed]
        tables/  0.029 GB; 10 files; 0 subdirs [collapsed]
      20260912T053550461436Z-69f2e5ee/  0.030 GB; 23 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.000 GB; 4 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 5 files; 0 subdirs [collapsed]
        tables/  0.029 GB; 10 files; 0 subdirs [collapsed]
    phm2026_target_audit/  0.002 GB; 29 files; 7 subdirs
      20260814T003646307262Z-170ed954/  0.002 GB; 29 files; 6 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 12 files; 0 subdirs [collapsed]
        logs/  0.000 GB; 0 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 5 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 8 files; 0 subdirs [collapsed]
    reassemble/  4.974 GB; 20089 files; 1005 subdirs
      20260927T134437Z/  0.000 GB; 13 files; 1 subdirs
        records/  0.000 GB; 1 files; 0 subdirs [collapsed]
      20260927T141645Z-inventory/  0.057 GB; 197 files; 3 subdirs
        records/  0.047 GB; 149 files; 0 subdirs [collapsed]
        reports_v2/  0.001 GB; 11 files; 0 subdirs [collapsed]
        tables_v2/  0.001 GB; 12 files; 0 subdirs [collapsed]
      20260927T154732Z-section1/  0.295 GB; 858 files; 5 subdirs
        assessment/  0.000 GB; 4 files; 0 subdirs [collapsed]
        checkpoints/  0.005 GB; 10 files; 0 subdirs [collapsed]
        features/  0.189 GB; 296 files; 0 subdirs [collapsed]
        finalization/  0.000 GB; 2 files; 0 subdirs [collapsed]
        predictions/  0.100 GB; 528 files; 0 subdirs [collapsed]
      20260927T174424Z-section1b/  0.000 GB; 19 files; 2 subdirs
        sensor_controls/  0.000 GB; 12 files; 1 subdirs [collapsed]
      20260927T175336Z-section1b/  0.006 GB; 306 files; 5 subdirs
        assessment/  0.000 GB; 3 files; 0 subdirs [collapsed]
        finalization/  0.000 GB; 1 files; 0 subdirs [collapsed]
        sensor_controls/  0.004 GB; 240 files; 1 subdirs [collapsed]
        stacking/  0.002 GB; 51 files; 0 subdirs [collapsed]
      20260927T192852Z-section2/  0.049 GB; 1369 files; 5 subdirs
        assessment/  0.000 GB; 6 files; 0 subdirs [collapsed]
        finalization/  0.000 GB; 2 files; 0 subdirs [collapsed]
        fits/  0.014 GB; 1140 files; 0 subdirs [collapsed]
        inputs/  0.032 GB; 200 files; 0 subdirs [collapsed]
        predictions/  0.003 GB; 11 files; 0 subdirs [collapsed]
      20260927T204649Z-audio-gate/  0.002 GB; 7 files; 0 subdirs
      20260927T204649Z-completion-preflight/  0.000 GB; 4 files; 0 subdirs
      20260927T204649Z-efficiency/  0.000 GB; 5 files; 0 subdirs
      20260927T204649Z-final-synthesis/  0.003 GB; 72 files; 4 subdirs
        figures/  0.002 GB; 28 files; 0 subdirs [collapsed]
        review/  0.000 GB; 1 files; 0 subdirs [collapsed]
        review_correction_v2/  0.000 GB; 5 files; 0 subdirs [collapsed]
        tables/  0.000 GB; 21 files; 0 subdirs [collapsed]
      20260927T204649Z-modality-dropout/  0.003 GB; 92 files; 2 subdirs
        fits/  0.001 GB; 75 files; 0 subdirs [collapsed]
        predictions/  0.002 GB; 11 files; 0 subdirs [collapsed]
      20260927T204649Z-object-feasibility/  0.000 GB; 5 files; 0 subdirs
      20260927T204649Z-section3/  0.222 GB; 995 files; 5 subdirs
        assessment/  0.016 GB; 44 files; 0 subdirs [collapsed]
        branches/  0.000 GB; 10 files; 0 subdirs [collapsed]
        predictions/  0.018 GB; 44 files; 0 subdirs [collapsed]
        sensor/  0.038 GB; 440 files; 0 subdirs [collapsed]
        visual/  0.149 GB; 439 files; 0 subdirs [collapsed]
      20261016T103206785885Z-dataset-walkthrough/  0.013 GB; 25 files; 17 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.004 GB; 1 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 1 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 4 files; 10 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T103339469873Z-dataset-walkthrough/  0.019 GB; 47 files; 30 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 8 files; 0 subdirs [collapsed]
        manifests/  0.004 GB; 3 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 5 files; 0 subdirs [collapsed]
        runtime/  0.001 GB; 16 files; 23 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T103522253690Z-dataset-walkthrough/  0.018 GB; 34 files; 17 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.004 GB; 3 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 6 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 4 files; 10 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T104112813280Z-dataset-walkthrough/  0.004 GB; 23 files; 8 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 1 files; 1 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T105310168628Z-dataset-eda/  0.014 GB; 30 files; 17 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 4 files; 10 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T105418770811Z-dataset-eda/  0.014 GB; 31 files; 17 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 2 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 4 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 4 files; 10 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T110742319615Z-dataset-walkthrough/  0.004 GB; 23 files; 8 subdirs
        config/  0.000 GB; 1 files; 0 subdirs [collapsed]
        figures/  0.002 GB; 6 files; 0 subdirs [collapsed]
        manifests/  0.000 GB; 1 files; 0 subdirs [collapsed]
        media/  0.001 GB; 4 files; 0 subdirs [collapsed]
        reports/  0.000 GB; 3 files; 0 subdirs [collapsed]
        runtime/  0.000 GB; 1 files; 1 subdirs [collapsed]
        tables/  0.000 GB; 6 files; 0 subdirs [collapsed]
      20261016T110945957012Z-prediction-playback/  0.003 GB; 10 files; 0 subdirs
      20261016T111108284110Z-prediction-playback/  0.014 GB; 14 files; 0 subdirs
      20261016T111333786622Z-prediction-playback/  0.015 GB; 19 files; 0 subdirs
      20261016T111406351696Z-prediction-playback/  0.001 GB; 7 files; 0 subdirs
      20261016T111407518200Z-prediction-playback/  0.003 GB; 10 files; 0 subdirs
      20261016T111859141532Z-prediction-playback/  0.014 GB; 14 files; 0 subdirs
      additional_improvements_executed/  4.202 GB; 15860 files; 832 subdirs
        20260928T000346Z/  3.946 GB; 14721 files; 191 subdirs [collapsed]
        20260929T162710Z/  0.256 GB; 1139 files; 639 subdirs [collapsed]
    thesis/  0.000 GB; 9 files; 2 subdirs
      documentation/  0.000 GB; 9 files; 1 subdirs
        20260928T025444Z/  0.000 GB; 9 files; 0 subdirs [collapsed]
  scratch/  0.051 GB; 92 files; 7 subdirs
    blind_inspection/  0.051 GB; 92 files; 6 subdirs
      _KEY_DO_NOT_OPEN/  0.000 GB; 2 files; 0 subdirs
      sorted_clean/  0.000 GB; 0 files; 0 subdirs
      sorted_damaged/  0.000 GB; 0 files; 0 subdirs
      sorted_unsure/  0.000 GB; 0 files; 0 subdirs
      to_sort/  0.007 GB; 42 files; 0 subdirs
      to_sort_fullphoto/  0.029 GB; 42 files; 0 subdirs
  scripts/  0.002 GB; 167 files; 25 subdirs
    __pycache__/  0.000 GB; 20 files; 0 subdirs
    dataset/  0.000 GB; 6 files; 0 subdirs
    features/  0.000 GB; 2 files; 0 subdirs
    intel_welding/  0.000 GB; 6 files; 0 subdirs
    ops/  0.000 GB; 4 files; 1 subdirs
      __pycache__/  0.000 GB; 1 files; 0 subdirs
    paderborn/  0.000 GB; 9 files; 1 subdirs
      __pycache__/  0.000 GB; 2 files; 0 subdirs
    phm2026/  0.001 GB; 40 files; 5 subdirs
      dataset/  0.000 GB; 6 files; 0 subdirs
      features/  0.000 GB; 2 files; 0 subdirs
      results/  0.000 GB; 17 files; 0 subdirs
      targets/  0.000 GB; 8 files; 0 subdirs
      training/  0.000 GB; 6 files; 0 subdirs
    presentation/  0.000 GB; 1 files; 0 subdirs
    rawvib/  0.000 GB; 7 files; 1 subdirs
      __pycache__/  0.000 GB; 2 files; 0 subdirs
    reassemble/  0.000 GB; 28 files; 1 subdirs
      additional_improvements/  0.000 GB; 1 files; 0 subdirs
    results/  0.000 GB; 17 files; 0 subdirs
    targets/  0.000 GB; 8 files; 0 subdirs
    thesis/  0.000 GB; 13 files; 2 subdirs
      final_validity_audit/  0.000 GB; 10 files; 0 subdirs
      review_interface/  0.000 GB; 2 files; 0 subdirs
    training/  0.000 GB; 6 files; 0 subdirs
  src/  0.002 GB; 213 files; 39 subdirs
    intel_welding/  0.000 GB; 8 files; 6 subdirs
      analysis/  0.000 GB; 1 files; 0 subdirs
      data/  0.000 GB; 1 files; 0 subdirs
      evaluation/  0.000 GB; 1 files; 0 subdirs
      fusion/  0.000 GB; 1 files; 0 subdirs
      models/  0.000 GB; 1 files; 0 subdirs
      robustness/  0.000 GB; 1 files; 0 subdirs
    phm2026/  0.001 GB; 58 files; 14 subdirs
      acquisition/  0.000 GB; 2 files; 0 subdirs
      data_contracts/  0.000 GB; 4 files; 0 subdirs
      datasets/  0.000 GB; 3 files; 0 subdirs
      evaluation/  0.000 GB; 4 files; 0 subdirs
      features/  0.000 GB; 3 files; 0 subdirs
      fusion/  0.000 GB; 3 files; 0 subdirs
      models/  0.000 GB; 9 files; 2 subdirs
        patchtst/  0.000 GB; 3 files; 0 subdirs [collapsed]
        rtdetr/  0.000 GB; 5 files; 0 subdirs [collapsed]
      preprocessing/  0.000 GB; 2 files; 0 subdirs
      profiling/  0.000 GB; 9 files; 0 subdirs
      reporting/  0.000 GB; 5 files; 0 subdirs
      targets/  0.000 GB; 4 files; 0 subdirs
      utils/  0.000 GB; 6 files; 0 subdirs
    pi_multimodal_ad/  0.000 GB; 56 files; 11 subdirs
      acquisition/  0.000 GB; 2 files; 0 subdirs
      data_contracts/  0.000 GB; 4 files; 0 subdirs
      datasets/  0.000 GB; 3 files; 0 subdirs
      evaluation/  0.000 GB; 4 files; 0 subdirs
      features/  0.000 GB; 3 files; 0 subdirs
      models/  0.000 GB; 9 files; 0 subdirs
      preprocessing/  0.000 GB; 2 files; 0 subdirs
      profiling/  0.000 GB; 9 files; 0 subdirs
      reporting/  0.000 GB; 5 files; 0 subdirs
      targets/  0.000 GB; 4 files; 0 subdirs
      utils/  0.000 GB; 6 files; 0 subdirs
    reassemble/  0.001 GB; 91 files; 4 subdirs
      __pycache__/  0.000 GB; 5 files; 0 subdirs
      additional_improvements/  0.001 GB; 49 files; 1 subdirs
        __pycache__/  0.000 GB; 20 files; 0 subdirs [collapsed]
      boundary_visual/  0.000 GB; 7 files; 0 subdirs
  tests/  0.000 GB; 57 files; 12 subdirs
    compatibility/  0.000 GB; 3 files; 0 subdirs
    fixtures/  0.000 GB; 5 files; 2 subdirs
      phm_recovery/  0.000 GB; 1 files; 0 subdirs
      synthetic_multimodal/  0.000 GB; 4 files; 0 subdirs
    intel_welding/  0.000 GB; 1 files; 0 subdirs
    ops/  0.000 GB; 1 files; 0 subdirs
    phm2026/  0.000 GB; 30 files; 0 subdirs
    reassemble/  0.000 GB; 14 files; 2 subdirs
      additional_improvements/  0.000 GB; 4 files; 0 subdirs
      boundary_visual/  0.000 GB; 1 files; 0 subdirs
    thesis/  0.000 GB; 3 files; 1 subdirs
      final_validity_audit/  0.000 GB; 3 files; 0 subdirs
  tutorials/  0.123 GB; 132 files; 27 subdirs
    EDA/  0.006 GB; 8 files; 0 subdirs
    final_baseline_rtdetr/  0.005 GB; 31 files; 7 subdirs
      analysis/  0.004 GB; 19 files; 4 subdirs
        01_threshold_and_geometry/  0.000 GB; 3 files; 0 subdirs [collapsed]
        02_calibration_and_slicing/  0.000 GB; 5 files; 0 subdirs [collapsed]
        03_error_taxonomy/  0.001 GB; 7 files; 0 subdirs [collapsed]
        04_activation_hooks/  0.003 GB; 4 files; 0 subdirs [collapsed]
      data_summary/  0.000 GB; 4 files; 0 subdirs
      scripts/  0.000 GB; 5 files; 0 subdirs
    patchtst_freq_baseline/  0.009 GB; 54 files; 8 subdirs
      __pycache__/  0.000 GB; 2 files; 0 subdirs
      analysis/  0.000 GB; 16 files; 3 subdirs
        __pycache__/  0.000 GB; 1 files; 0 subdirs [collapsed]
        ablation_output/  0.000 GB; 9 files; 0 subdirs [collapsed]
        residuals_output/  0.000 GB; 4 files; 0 subdirs [collapsed]
      features/  0.009 GB; 23 files; 1 subdirs
        per_run/  0.006 GB; 20 files; 0 subdirs [collapsed]
      training_output/  0.000 GB; 5 files; 0 subdirs
    presentations/  0.010 GB; 2 files; 0 subdirs
    rtdetr_storybook/  0.094 GB; 37 files; 7 subdirs
      __pycache__/  0.000 GB; 2 files; 0 subdirs
      example_run/  0.006 GB; 5 files; 0 subdirs
      outputs/  0.018 GB; 12 files; 3 subdirs
        raw_expa_run1_tooth05/  0.006 GB; 4 files; 0 subdirs [collapsed]
        raw_expa_run1_tooth06/  0.006 GB; 4 files; 0 subdirs [collapsed]
        raw_expb_run1_tooth05/  0.006 GB; 4 files; 0 subdirs [collapsed]
      raw_demo_data/  0.003 GB; 12 files; 0 subdirs
```

## Representative deeper branches

| Exact relative path | Allocated | Files | Subdirs |
| --- | --- | --- | --- |
| HANDOVER/01_raw_dataset/official_dataset/archives | 13.012 GB | 20 | 0 |
| HANDOVER/experiments/common_support_v2/03_processed_model_inputs/visual_features | 0.308 GB | 1180 | 1 |
| MSM/03_processed_model_inputs/visual_features/P | 1.002 GB | 3796 | 0 |
| MILLING DATASET/data/raw/msm/versions/2 | 3.732 GB | 516 | 72 |
| MILLING DATASET/runs/20261026T233709740813Z-stage2/staging | 1.197 GB | 35 | 9 |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache | 0.000 GB | 0 | 0 |
| runs/reassemble/additional_improvements_executed/20260928T000346Z/01_temporal_visual/frozen_prefix | 0.020 GB | 4535 | 0 |
| parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/pixels | 0.001 GB | 1 | 148 |

## Symbolic links

All 74 links resolved at inventory time. Targets are not additional copies. MSM raw data and preserved Milling navigation refer to the existing `MILLING DATASET`; Handover canonical stage links refer to `experiments/common_support_v2`; newer REASSEMBLE visual workspaces refer back to the bootstrap shared cache. Empty cache paths and preserved completion markers do not establish array availability.

| Link | Target |
| --- | --- |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/frozen_features_complete.json | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/frozen_features_complete.json |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/original_feature_extraction_identity.json | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/original_feature_extraction_identity.json |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/original_features | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/original_features |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/original_features_16.npy | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/original_features_16.npy |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/original_features_32.npy | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/original_features_32.npy |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/pixels | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/pixels |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/preparation | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/preparation |
| 00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/sensor_statistics.npy | parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/sensor_statistics.npy |
| DATASET_RESEARCH/HANDOVER | ../HANDOVER |
| DATASET_RESEARCH/MILLING_DATASET | ../MILLING DATASET |
| DATASET_RESEARCH/MSM | ../MSM |
| DATASET_RESEARCH/REBOOT | ../REBOOT |
| HANDOVER/02_labels_and_alignment/active_common_support_v2 | ../experiments/common_support_v2/02_labels_and_alignment |
| HANDOVER/03_processed_model_inputs/active_common_support_v2 | ../experiments/common_support_v2/03_processed_model_inputs |
| HANDOVER/04_experiment_protocol/active_common_support_v2 | ../experiments/common_support_v2/04_experiment_protocol |
| HANDOVER/05_trained_models/active_common_support_v2 | ../experiments/common_support_v2/05_trained_models |
| HANDOVER/06_evaluation_results/active_common_support_v2 | ../experiments/common_support_v2/06_evaluation_results |
| HANDOVER/07_robustness_experiments/active_common_support_v2 | ../experiments/common_support_v2/07_robustness_experiments |
| HANDOVER/08_visual_examples_and_eda/active_common_support_v2 | ../experiments/common_support_v2/08_visual_examples_and_eda |
| HANDOVER/experiments/common_support_v2/01_raw_dataset | ../../01_raw_dataset |
| MSM/01_raw_dataset/official_dataset | ../../MILLING DATASET/data/raw/msm/versions/2 |
| MSM/99_preserved_previous_work/MILLING_DATASET | ../../MILLING DATASET |

No additional Python environment or project-local pip/Hub/Triton download cache was found outside `ma_thesis_env`; `.cache` contains repository-restructure bytecode. CUDA `.so` libraries inside the environment are installed dependencies. User-level caches outside this project were not scanned.
