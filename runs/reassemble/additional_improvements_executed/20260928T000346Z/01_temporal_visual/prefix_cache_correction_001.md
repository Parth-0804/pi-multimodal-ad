# Prefix-cache equivalence correction — before V-FT outcomes

The first GPU audit (`prefix_GPU_audit.log`) tested extraction in16-image batches
against the intended two-segment32-image fine-tuning forward. Prediction maximum
error was3.933906555175781e-6, but gradient error5.340576171875e-5 exceeded the
predeclared1e-5 tolerance. No real cache or V-FT fit was produced from that attempt.

Keep the tolerance. Match the32-image convolution batch shape when extracting
prefix activations. For singleton microbatches, use the original live pixel
forward (16 images), preserving its kernel behavior. This retains the original
effective batch128, dropout/RNG sequence, trainable parameters and budget. The
second GPU audit checks prediction and gradient parity before cache use.
