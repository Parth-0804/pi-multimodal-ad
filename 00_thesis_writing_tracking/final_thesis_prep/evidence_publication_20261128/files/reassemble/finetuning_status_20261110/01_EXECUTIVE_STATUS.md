# REASSEMBLE current CNN status —2026-11-10

What has actually been completed in REASSEMBLE CNN fine-tuning as of this audit?

**As of the 2026-11-10 audit, the early16/32-frame study, the two-seed matched2-epoch study,25 C20 fits for seed 42, and both 100-epoch pilot arms are complete in their stated scopes.** C20 covers all five outer folds and20 inner fits:500 completed epochs. Its approved25-fit cap is complete; the wider75-fit campaign is not. C20 F2 has **NOT EXECUTED**. Frozen100 and Full100 each executed100 epochs, selected14/47, and have completed single-fold F2 follow-ups. Fifty C20 fits for seeds 123/20261023 remain explicitly deferred. No additional completed main-CNN fits beyond the November3 evidence were found in the inspected roots.

The known local C20/Phase1/100-epoch training and controller entry points had no matching live PIDs at the audit snapshot ([process check](support/CURRENT_PROCESS_CHECK.json)); the saved cap state is stopped.

The original frozen16 reference, original nested F2, later fixed-budget visual/F2 studies, limited temporal fine-tuning, frozen temporal/boundary heads, encoder probe and superseded/recovery artifacts are preserved as separate conditions. A renamed/reused fit does not count as a new trained model. [02](02_ALL_FINETUNING_EXPERIMENTS.md), [03](03_COMPLETE_MODEL_CONFIGURATIONS.csv) and [04](04_SEED_FOLD_AND_EPOCH_COVERAGE.csv) retain individual roles and identities.

All 4,714 sources in the November3 cohort evidence manifest were independently rehashed and unchanged. Current receipt/config/checkpoint and prediction checks supplement that historical manifest. Git additions on November9/10 are not by themselves new training. The existing partial audit directory was preserved; this `_02` directory is a new report set.

The 753-action population is original outer fold0:26 recordings and77 failures. The full 4530-action population has148 recordings and509 failures. The 920-action bank has28 recordings and97 failures; it is a separate inner held-out role used to fit the pilot F2. The selected pilot's T/V/C/inner/outer roles are1752/419/686/920/753 and partition the4530 actions with no action or recording overlap. The selected-job JSON has a stale `prediction_recordings` field referring to inner920; actual `predict` IDs and saved predictions establish outer753. See [role proof](support/RESULTS_ROLE_PROOF.json).

The 100-epoch fit was selected from three then-completed C20 candidates by training-side validation AP on different validation groups. Both100-epoch arms restarted from the original CNN and the same fresh head seed; they did not extend the selected C20 weights. This preserves the within-pilot contrast but does not remove the exploratory fit-selection or prior dataset exposure.

Reported uncertainty conditions on fitted models and recording resampling. It does not cover refitting, unseen seeds, the pilot fit-selection process or all prior analyses. Full100-minus-Frozen100 F2 AP is+0.014117 with95% interval[-0.000773,+0.029089]; improvement and equivalence are both unestablished. Equal epochs do not imply equal computation. Cross-study pooled AP differences are not controlled effects.

The original sensor is 220 statistics from 22 channels. Its selected-C nested fitting produces pooled AP0.429392. The later fixed-C1, separate-calibration sensor gives0.420803; it is a different fitting protocol. The pilot uses the canonical original sensor's identical753 outer scores in both fusion arms. C20's sensor figure in08 is the actual prepared fixed-C1, separate-calibration sensor score vector across five outer folds (AP0.420803), not a completed C20 fusion result.

Costs distinguish training, measured process time and fit wall. Full100 training is23.964191h; Full100 active processes total25.818357h. The historically quoted25.893729h is the sum of **both** pilot arms. C20 training sums126.231611h; validation/inference-inclusive components sum137.474850h. Do not add recovery/development prefixes to completed-fit histories twice.

Read [15_RESEARCHER_HANDOFF.md](15_RESEARCHER_HANDOFF.md) for all five requested summary tables and [14](14_UNRESOLVED_EVIDENCE.md) for remaining evidence limits. Audit checks and manifests are linked from [README](README.md).
