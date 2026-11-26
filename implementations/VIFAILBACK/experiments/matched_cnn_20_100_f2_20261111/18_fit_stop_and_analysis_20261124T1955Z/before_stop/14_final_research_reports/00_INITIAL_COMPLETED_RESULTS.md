# Initial completed-results snapshot

Written 2026-11-10T23:47:26.655652+00:00. This is the completed frozen/donor stage; Full100 is running and all Full20 CNN fits remain queued. The live study reports supersede this dated snapshot when further fits complete.

**The primary full-CNN question is still untested.** No result below compares a completed full-CNN fit with its matched frozen control. All74 cached-head fits have completed and passed independent epoch, selection, state and hash checks;20 F2 models and120 saved metric vectors have been independently replayed.

**The donor transfers mechanically, but a reliable visual benefit is not established.** Donor20 visual macro-AP intervals include zero in every matched fold and in all three pooled seed comparisons. Its pooled point differences are negative for seeds42 and123 and positive for seed20261023. Donor100 improves the pilot visual point estimate by0.020453, with a95% interval spanning zero. These findings do not establish equivalence.

**F2 does not establish superiority over the retained strong sensor baseline.** All six pooled20-epoch F2 versus HGB differences have negative conditional task-bootstrap intervals. The pilot F2 models also score below HGB, although their one-fold intervals span zero. Both pilot F2 versus LR intervals are negative. Within-fold20-epoch F2 versus LR intervals all include zero; pooling separately fitted/calibrated fold scores gives different ranking behavior and must not be confused with a mean of fold metrics.

## Completed pooled20 results

|Condition|Seed|Visual macro AP|Sensor LR macro AP|F2 macro AP|HGB macro AP|
|---|---|---|---|---|---|
|FROZEN20|42|0.507865|0.648974|0.629280|0.700020|
|FROZEN20|123|0.495229|0.648974|0.627039|0.700020|
|FROZEN20|20261023|0.487612|0.648974|0.624555|0.700020|
|DONOR20|42|0.491368|0.648974|0.627750|0.700020|
|DONOR20|123|0.489011|0.648974|0.637852|0.700020|
|DONOR20|20261023|0.492185|0.648974|0.630936|0.700020|

## Matched donor20 minus original-frozen20

|Seed|Visual macro AP difference [95% interval]|F2 macro AP difference [95% interval]|
|---|---|---|
|42|-0.016497 [-0.032908, +0.001339]|-0.001530 [-0.002673, -0.000237]|
|123|-0.006219 [-0.025260, +0.012160]|+0.010813 [+0.006082, +0.015846]|
|20261023|+0.004573 [-0.021106, +0.035886]|+0.006381 [+0.003638, +0.009305]|

F2 changes are not consistent in direction across seeds: negative for42 and positive for123 and20261023. Each interval is conditional on fixed fitted models, task resampling and the declared analysis; no multiple-comparison adjustment or model-refitting uncertainty is included. Seeds reuse the same episodes and are not additional independent samples.

## What continues

The GPU controller runs the100-epoch pilot first, then36 full20 fits across the three predeclared seeds. It retains exact scheduled epochs, selected and final checkpoints, and epoch-boundary recovery. The reporter admits F2 only after the required complete held-out banks exist. The conservative prelaunch forecast was228 GPU process-hours for Full100 and1731 hours for the full admitted GPU queue; these are estimates, not completed costs.

Follow `../VIFAILBACK_MATCHED_CNN_STUDY_STATUS.md`, `01_EXECUTIVE_SUMMARY.md`, and `../13_reproducibility/runtime/`. All task/fold/seed metrics, confidence intervals, coefficient signs, calibration comparisons and error identities remain in the full reports and saved JSONs. Historical results and data were preserved.
