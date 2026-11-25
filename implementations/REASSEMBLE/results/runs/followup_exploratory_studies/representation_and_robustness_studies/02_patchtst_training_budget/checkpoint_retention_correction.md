# Checkpoint-retention correction

[CORRECTED] Post-execution review found that the short-budget inner trainer saved
its best checkpoint among epochs1–6, whereas S-6 calibration correctly used the
saved logits at the aggregate-selected epoch3 or6. All reported predictions and
selection rules are correct; the checkpoint retained for some inner fits was not
the state generating those selected logits. Outer selected checkpoints exist.

Before Task2 completion, reuse any matching selected state and reconstruct each
missing state once with the same seed, architecture, data, microbatch and original
selected3/6 duration. Require agreement with the previously saved selected logits
within1e-6, without looking at new performance or choosing a different epoch.
Store reconstructed states separately under fits/S-6_selected_checkpoint_replay;
keep all originals. This is provenance repair, not an expanded scientific budget.
The numerical predictions used in every comparison remain unchanged.
