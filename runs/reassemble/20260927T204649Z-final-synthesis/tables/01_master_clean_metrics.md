| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE | Parameters | Latency ms* |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Prior | 0.4839 | 0.1083 | 0.5000 | 0.4702 | 0.0000 | 0.0000 | 0.0998 | 0.0002 | 1 | not measured |
| Action only | 0.6851 | 0.1808 | 0.6505 | 0.4835 | 0.7642 | 0.1727 | 0.0951 | 0.0080 | 7 | not measured |
| Sensor statistics | 0.7793 | 0.4294 | 0.7056 | 0.6223 | 0.6149 | 0.2765 | 0.0804 | 0.0174 | 223 | 26.27 |
| RT-DETR | 0.6978 | 0.2307 | 0.6414 | 0.5153 | 0.6621 | 0.1810 | 0.0943 | 0.0070 | 11305059 | 478.42 |
| PatchTST | 0.7054 | 0.2416 | 0.6352 | 0.5463 | 0.5639 | 0.1956 | 0.0937 | 0.0067 | 109507 | not measured |
| Uniform late | 0.7951 | 0.4457 | 0.7087 | 0.6331 | 0.6031 | 0.2913 | 0.0834 | 0.0355 | 11305282 | 504.69 |
| Learned static | 0.7950 | 0.4473 | 0.7117 | 0.6340 | 0.6110 | 0.2920 | 0.0784 | 0.0138 | 11305285 | 504.69 |
| Concatenation | 0.7856 | 0.4122 | 0.6999 | 0.6024 | 0.6385 | 0.2529 | 0.0827 | 0.0149 | 11490409 | not measured |
| Process gate | 0.7815 | 0.4437 | 0.7047 | 0.6268 | 0.6031 | 0.2827 | 0.0802 | 0.0128 | 11305720 | not measured |
| Quality gate | 0.7760 | 0.4445 | 0.7001 | 0.6206 | 0.6012 | 0.2747 | 0.0806 | 0.0126 | 11307256 | 564.04 |
| Process + quality | 0.7755 | 0.4414 | 0.7019 | 0.6384 | 0.5717 | 0.3012 | 0.0807 | 0.0124 | 11307448 | 564.02 |
| Modality dropout | 0.7754 | 0.4377 | 0.6981 | 0.6310 | 0.5737 | 0.2903 | 0.0809 | 0.0130 | 11307448 | 564.02 |
| AST | not run | not run | not run | not run | not run | not run | not run | not run | not measured | not measured |
| Tri-modal fusion | not run | not run | not run | not run | not run | not run | not run | not run | not measured | not measured |

*Warm sequential component-sum estimate; not production end-to-end timing. Latency not remeasured for retired PatchTST/concatenation/process gate. Full per-metric CIs and source pointers are in CSV. Parameter counts include shared branches where used and three seed heads; counts can vary by outer fold.
