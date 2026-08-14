# Multitask genuine RT-DETR engineering baseline

> **PROVISIONAL PSEUDO-BOXES AND PSEUDO-TARGETS — NOT PHYSICAL-DAMAGE GROUND TRUTH.**

This run retains genuine RT-DETR classification and box heads and attaches a differentiable scalar head to encoder layer 27 (`B×256×20×20`, global-average pooled to `B×256`). Standard Ultralytics classification/L1/GIoU detection losses are optimized jointly with a SmoothL1 scalar loss. The scalar target is the exact pinned `target_value_pct` (`phm2026_image_damage_v2`) used by the earlier frozen-encoder baseline. View predictions aggregate by maximum to a tooth; tooth predictions aggregate by run top-3 mean, with a separately retained causal cumulative maximum.

Training used EXP-B only (448 views), validation/model selection used EXP-A only (323), and EXP-F (224) was evaluated once after selection. No EXP-F statistic selected the loss balance, epoch, checkpoint, or confidence threshold. The current task is post-run state estimation, not six-hour-ahead forecasting.

Detection on EXP-F at validation-selected confidence 0.0100: precision=0.001525, recall=0.008904, F1=0.002604, mAP@0.50=0.000054, mAP@0.50:0.95=0.000013. These are agreement with mask-derived pseudo-boxes only. Scalar EXP-F view MAE=0.732990 pp (N=224); raw run top-3 MAE=1.627254 pp (N=8). Physical validity requires expert review of the masks and boxes.

EXP-F is also an acquisition-protocol/domain shift: it contains canonical tooth views rather than the EXP-A/EXP-B canonical-plus-close-up protocol. Generic COCO detections are not treated as gear damage. Exact metrics, hashes, environment, trainable/frozen parameter counts, optimizer groups, loss balance, and the one-pass test declaration are machine-readable in this run.
