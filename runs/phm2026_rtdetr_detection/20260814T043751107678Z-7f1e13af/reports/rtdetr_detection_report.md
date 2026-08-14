# Genuine RT-DETR damage-candidate detector

> Bounding boxes are pseudo-boxes derived from provisional masks. All metrics measure pseudo-label agreement, not physical-damage validity.

The one-class RT-DETR detector was selected using EXP-A validation only and evaluated once on EXP-F at confidence 0.6000. EXP-F represents an acquisition-protocol/domain shift. Overall test N=224 images: precision=0.0000, recall=0.0000, F1=0.0000, mAP@0.50=0.0001, mAP@0.50:0.95=0.0000. Full RT-DETR detection retains the backbone, multiscale encoder, transformer decoder/object queries, class head and box head; it is different from the earlier frozen-encoder scalar regression. Physical validity requires expert review.
