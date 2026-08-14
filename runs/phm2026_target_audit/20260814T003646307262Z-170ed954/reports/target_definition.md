# PHM target definition

Status: **BLOCKED_REQUIRES_PROFESSOR_OR_PROVIDER_DECISION**

No `TargetRecord`, target computation, transformed target, sample manifest, split, regression metric, or regression model is authorized.

## Unresolved contract

- Exact target: UNKNOWN
- Physical meaning and unit: UNKNOWN
- Target type: UNKNOWN
- Current-state versus future prediction: UNKNOWN
- Six-hour interpretation: UNKNOWN (cadence, input history, forecast horizon, or another meaning)
- Image-to-target pairing rule: UNKNOWN
- Prediction horizon and input cutoff: UNKNOWN
- Target scaling/inverse scaling: NOT APPLICABLE UNTIL TARGET APPROVAL
- Inference-time target availability: UNKNOWN
- Leakage boundary: UNKNOWN

## Evidence boundary

D1.4 found zero verified UTC image timestamps, so local-naive image timestamps remain unconverted and no temporal image–sensor/target join is authorized. No authoritative local/provider specification defining the scalar or six-hour statement was found in the repository evidence reviewed for T2.1.

## Required decisions

1. What exact scalar should be predicted, with physical meaning and unit?
2. Is the task current-state estimation, six-hour-ahead forecasting, or another horizon?
3. Does six hours mean observation cadence, input history, forecast horizon, or something else?
4. What authoritative identifier or clock rule pairs each image/inspection with the target?
5. Would the target and all target-construction inputs exist at real inference time?
6. If a CI is selected, what formula/version produces it and which input channels must be excluded to prevent tautological leakage?
7. Are quantitative tooth-damage labels, RUL values, or external annotations supplied outside the reviewed archives?
