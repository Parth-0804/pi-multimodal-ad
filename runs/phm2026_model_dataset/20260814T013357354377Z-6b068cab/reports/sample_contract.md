# Sample contract

The RT-DETR engineering sample is one post-run tooth image with its own provisional image-mask area ratio. Multiple views are separate view samples and are aggregated to a tooth with the versioned maximum-view rule; tooth predictions aggregate to a run with the top-3 mean. No run target is repeated across teeth.

Canonical development split: EXP-B train, EXP-A validation, EXP-F untouched test. No run, inspection, tooth group, or near-duplicate group crosses an experiment boundary. No random split is generated inside a loader.

The sensor-file and sensor-run manifests are traceability records. `minute_feature_table` records that compact signal features were not computed in this image-baseline task; it must not be treated as a feature dataset.
