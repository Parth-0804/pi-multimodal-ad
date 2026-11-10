# MSM dataset overview

A manufacturing domain with native per-cut abnormalities, phone video and numerical MTC signals tests software/representation portability beyond robot manipulation.

56 laboratory experiments on VM20i/VMX30Ui; industrial VF10 excluded because it has no supplied video.

The original `MILLING DATASET/` tree remains intact. The canonical raw path is a verified relative symlink; no large video or sensor file was moved or copied. All 282 minimal laboratory raw-file hashes were verified. Historical Stage 1–5 reports, corrections, matched reviews and negative/blocked findings remain in `MSM/99_preserved_previous_work/MILLING_DATASET/`.

Native 0 is stable normal cutting, 1 is intervention-worthy abnormal cutting and 2 is stable cutting with a defective tool. Primary binary target is 1 versus 0/2. The entire fitting/splitting pipeline is repeated after excluding label 2 as a separate sensitivity; no native label was rewritten.

Official source: [10.34740/kaggle/ds/8392825](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly).
