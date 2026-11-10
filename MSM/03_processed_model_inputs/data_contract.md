# MSM input/output contract

16 ordered, distinct native RGB frames → aspect-preserving SAR-corrected 640×640 black letterbox, divide by 255, no ImageNet normalization → frozen ResNet CNN only → last three spatial-map means concatenate to 896 values per frame → mean over 16 frames → one 896-value vector. Source native frame indices, actual PTS and source-clock associations are retained.

The allowed channels are `watt, Spindle_Speed, S_Axis_Load, Feed_Rate, X_Axis_Load, Y_Axis_Load, Z_Axis_Load, smarms, xmarms, ymarms, zmarms, smvrms, xmvrms, ymvrms, zmvrms`. Channel-major statistics are mean, population std (ddof 0), RMS, minimum, maximum and peak-to-peak: **90 values** per native example. No label, tool ID, program, direction, folder, robot, task or participant metadata enters the main predictors. Training-only means/standard deviations are fitted separately for every inner and final fit.

Outputs: one abnormal/failure probability per original native example, with source label, split/fit identity and checkpoint hash. Image overlays/qualitative crops are never CNN training inputs.
