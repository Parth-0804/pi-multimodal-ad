# Efficiency and practical usability

warm VM measurements on 3 deterministic segments from distinct recordings; raw sensor arrays already in RAM; video decoding from existing cache measured separately; sequential component sums are estimates, not measured production end-to-end latency. No real-time or production claim.

| Model | Total parameters | Trainable | Checkpoint MiB | Preprocessing ms | Inference ms | Component-sum ms |
| --- | --- | --- | --- | --- | --- | --- |
| U1 | 223 | 223 | 0.039 | 26.167 | 0.100 | 26.267 |
| U2 | 11305059 | 114947 | 77.607 | 391.061 | 87.354 | 478.415 |
| F1 | 11305282 | 115170 | 77.646 | 417.228 | 87.460 | 504.688 |
| F2 | 11305285 | 115173 | 77.646 | 417.228 | 87.465 | 504.693 |
| F5 | 11307256 | 117144 | 77.664 | 476.286 | 87.752 | 564.038 |
| F6 | 11307448 | 117336 | 77.663 | 476.286 | 87.735 | 564.021 |
| D6 | 11307448 | 117336 | 77.664 | 476.286 | 87.730 | 564.016 |

Estimated sequential throughput (segments/s): U1 38.07, U2 2.09, F1 1.98, F2 1.98, F5 1.77, F6 1.77, D6 1.77. Four CPU threads; visual-containing models use the T4. Peak is the shared visual benchmark allocation, not separate per-model isolated profiling.
Peak GPU allocated bytes: 1416854528. RT-DETR source safetensors includes unused detection components; bytes reflect stored deployment source plus heads. Gate parameter totals use maximum ensemble size over all five outer folds. Frozen backbone contributes total but not trainable parameters. Trainable means fitted somewhere in pipeline, not fine-tuned in robustness.

Late fusion permits independent branch replacement, but replacement score distributions require training-only revalidation/recalibration of fusion. Static/gated fusion need no backbone joint retraining; their heads must be refitted when interfaces change. Missing modalities reduce exactly to the surviving branch.
