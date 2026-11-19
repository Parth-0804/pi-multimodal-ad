# HANDOVER input/output contract

16 ordered, distinct native RGB frames → aspect-preserving SAR-corrected 640×640 black letterbox, divide by 255, no ImageNet normalization → frozen ResNet CNN only → last three spatial-map means concatenate to 896 values per frame → mean over 16 frames → one 896-value vector. Source native frame indices, actual PTS and source-clock associations are retained.

The allowed channels are `force_x, force_y, force_z, torque_x, torque_y, torque_z`. Channel-major statistics are mean, population std (ddof 0), RMS, minimum, maximum and peak-to-peak: **36 values** per native example. No label, tool ID, program, direction, folder, robot, task or participant metadata enters the main predictors. Training-only means/standard deviations are fitted separately for every inner and final fit. Gripper/joint configurations differ between robots and are not fabricated into a shared joint vector. HSR wrench is measured; Gen3 wrench is estimated from joint torque. Fourteen trials have all-six-channel zero traces; they are retained as native, timestamp-valid observations and flagged as uninformative, not silently relabeled or “repaired”.

Outputs: one abnormal/failure probability per original native example, with source label, split/fit identity and checkpoint hash. Image overlays/qualitative crops are never CNN training inputs.
