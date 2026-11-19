# RT-DETR-derived image-regression baseline

> **PROVISIONAL PSEUDO-TARGET — PENDING HUMAN MASK VALIDATION; NOT VALIDATED PHYSICAL SPALL PERFORMANCE.**

Formulation: frozen COCO-pretrained RT-DETR-L backbone/hybrid encoder; global average pooling of three 256-channel multi-scale maps; 768→128→1 regression head. Each view predicts its own provisional candidate-area ratio. View predictions aggregate by maximum to a tooth and the 28 tooth predictions aggregate by top-3 mean to a run.

Training used EXP-B only; EXP-A was validation and EXP-F was untouched until evaluation. No test tuning, hyperparameter sweep, sensor input, PatchTST, or organizer ground truth was used. Exact metrics are in `tables/metrics.csv`; naive comparison is in `tables/naive_metrics.csv`. These quantify pseudo-label reproducibility across acquisition protocols, not calibrated gear damage.

Preprocessing: BGR decoder input → Ultralytics scale-fill 640×640 → RGB/BCHW float32/255; no padding mask. Encoder frozen/precomputed; only the MLP head trained. Best and last head checkpoints are retained.
