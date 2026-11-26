# Models

Pinned RT-DETR ResNet18-vd CNN only, revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`. Each of three cameras contributes 16 fixed timestamps, giving 48 frames per episode. Spatial means concatenate 128+256+512=896 features; equal temporal/camera means give one representation per episode. Head 896→128→ReLU→Dropout(0.1)→1 has 114,945 parameters.

FULL conditions train all 11,199,968 CNN parameters, including normalization affine terms; running moments remain fixed. Frozen and donor CNNs have zero trainable backbone parameters. Encoder, detection decoder and box heads are excluded.

Full CNN frame chunks propagate gradients through exact recomputation while preserving one episode-level pooled loss and an eight-episode head minibatch. Bounded numerical, gradient, frozen-buffer, save/reload and resume evidence: `../13_reproducibility/`. Successful checks do not establish external scientific validity.
