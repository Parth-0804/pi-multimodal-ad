# RT-DETR Model 1 — frozen-encoder scalar regression

**Question:** can a frozen pretrained image representation and a small fitted head reproduce the provisional image-derived candidate-area percentage?

**Review finding:** the saved head has 769 inputs because `feature_latency_ms` was included alongside the 768 image features. [Read the evidence and implications](KNOWN_IMPLEMENTATION_ISSUES.md).

Pinned run: `20260814T020338751021Z-d0f225c8`. It contains 995 image-view predictions, including training and validation rows; the held-out test subset is the 224 EXP-F images.

1. [00 — Dataset, samples and labels](00_data_overview/README.md)
2. [01 — Target construction and model-input preprocessing](01_data_preprocessing/README.md)
3. [02 — Functions, architecture and saved parameters](02_model/README.md)
4. [03 — Prediction, evaluation and result files](03_model_outputs_and_results/README.md)

[Follow EXP-F / Run 1 / Tooth 01 through every stage](SAMPLE_WALKTHROUGH.md)

[Back to PHM start](../README.md)
