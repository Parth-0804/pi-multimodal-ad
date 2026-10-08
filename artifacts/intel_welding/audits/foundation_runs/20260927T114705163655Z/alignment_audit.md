# Temporal-alignment feasibility audit

Evidence directory: `artifacts/intel_welding/audits/foundation_runs/20260927T114705163655Z`. Manifest SHA256: `9c4fb4df70bb137fc851dd858ac22d53eed86ba08c3806d7177e40b300406826`.

Status: CONDITIONAL / NOT VALIDATED. No temporal cross-attention is enabled.
This is a structural feasibility audit, not a measured cross-modal alignment.
Envelope/lag estimation is deferred because the final-holdout gate has failed.

| measurement | median | range / caveat |
|---|---:|---|
| audio duration | 38.000 s | 25–38 s, 2,723 files |
| video duration | 35.800 s | 21–43.033 s, container metadata |
| sensor duration | 36.617 s | 21.794–188.344 s, 2,693 valid timestamp series |
| sensor nominal adjacent-step rate | 8.621 Hz | 8.621–9.091 Hz; not guaranteed uniform |
| absolute audio–video duration gap | 2.355 s | maximum 16.233 s |
| absolute audio–sensor duration gap | 1.659 s | maximum 150.344 s |
| absolute video–sensor duration gap | 0.449 s | maximum 154.215 s |

These gaps are not lag estimates. They can reflect clipping, duration differences,
recording starts/stops, sensor interruptions or metadata problems. Thirty-two
sensor series contain nonpositive timestamp steps and cannot safely be interpolated
without an explicitly reviewed policy. No interpolation, resampling, scaling,
trimming, offset correction or synchronization claim is made here.

After holdout recovery, specify a development-only test of RMS audio energy,
video arc/luminance/motion and current/voltage activity envelopes, timestamps,
common-grid resolution, admissible lag range, minimum overlap, peak sharpness,
flat-envelope handling, boundary rejection, confidence and session stability.
Predeclare thresholds before inspecting those results. Low-rate sensor data
limits temporal resolution. Validate the estimator on synthetic shifted and flat
signals. A measurable stable lag may justify temporal fusion; otherwise sample-
level fusion remains the permitted option after unimodal gates pass.

No estimated lags, confidence values or lag plots exist yet. Do not replace them
with duration differences. A feasibility audit alone cannot pass Gate 4.
