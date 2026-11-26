# ViFailback — independent blinded visual feasibility review

**Review status:** Completed independently from the blinded pilot supplied by Parth. **No native labels, unblinding key, source identities, or prior case judgments were accessed.** Review is AI-assisted visual interpretation, **not** an independent human annotation, a validated outcome benchmark, or an ML model evaluation.

## Material and protocol

- Package: `VIFAILBACK_BLINDED_REVIEW.zip`; 20 anonymous executions (`B01`–`B20`), 16 timestamps/execution, three camera views/timestamp, plus synchronized *converted-time* numerical-observation plots.
- Read the task instruction for each anonymous case; examined **all 20 three-camera overview sheets** and then larger high-camera sequences and selected individual native frames for difficult and representative cases. Examined representative sensor plots only for interpretability; no signal-level validity or hardware synchronization audit is implied.
- Interpreted the **visible state of the target object at the end**, not the mere appearance of robot motion. A successful-looking image does not prove the native success annotation; absence of visible failure does not establish a native normal label.
- `Clear` means visually observable in these sampled images; `Partial` means an obstruction, small target or subtle outcome requires qualification. `Evidence` denotes visually apparent noncompletion versus no apparent noncompletion; it is **not a revealed ground-truth label**.

## Case-level blinded observations

| Blind ID | Object / interaction visibility | Visible outcome | Apparent task completion | Visible noncompletion evidence | Confidence |
|---|---|---|---|---|---|
| B01 | Clear | Drawer opened; marker appears deposited inside. | Yes | None evident | High |
| B02 | Partial for drawn ink line | Marker retrieved and returned; distinct new line cannot be reliably separated from existing tabletop marks. | **Uncertain** | **Indeterminate** | Low |
| B03 | Clear | Cup stays off the closed book. | No | Cup not placed on book | High |
| B04 | Clear | Spoon enters red pot; lid covers it. | Yes | None evident | High |
| B05 | Clear | Plate tilted; sausages appear to enter white basket. | Yes | None evident | High |
| B06 | Clear | Cube handed between grippers, but ends outside basket. | No | Cube outside target | High |
| B07 | Clear | Sausages remain on source plate; basket appears empty. | No | No visible transfer | High |
| B08 | Clear | Drawer opened; marker remains on table instead of inside. | No | Marker outside target | High |
| B09 | Clear with enlarged frame; object small | Tube remains horizontal beside holder/shelf at end. | No | Tube not upright on shelf | High |
| B10 | Clear | Visible ink line on table and marker returned to cup. | Yes | None evident | High |
| B11 | Clear with enlarged final frame | White plug seated in power strip/socket. | Yes | None evident | High |
| B12 | Clear | Cube transferred and ends inside basket. | Yes | None evident | High |
| B13 | Clear with enlarged final frame | Tube ends upright in the rack/shelf. | Yes | None evident | High |
| B14 | Clear | Cup placed upright on closed book. | Yes | None evident | High |
| B15 | Clear overall; small tube | Tube remains in source cup; rack placement not observed. | No | No visible insertion into rack | Medium–high |
| B16 | Clear | Mouse ends in white basket. | Yes | None evident | High |
| B17 | Clear with enlarged final frame | Tube appears upright in left-side rack position. | Yes | None evident | High |
| B18 | Clear with enlarged final frame | White plug remains separate from power strip/socket. | No | Plug not inserted | High |
| B19 | Clear | Spoon placed on saucer, not red pot; lid remains aside. | No | Wrong placement and missing lid action | High |
| B20 | Clear, but **human hand enters scene** | Mouse remains on tray, basket empty; person intervenes toward end. | No | No robot completion; **human intervention is a confound** | High for visible state |

### Pre-unblinding tally

- **10** appear to complete their instructed tasks.
- **9** appear not to complete their instructed tasks, with visible reasons.
- **1** is genuinely **uncertain** (`B02`, whether a line was drawn). Do not force this case into the failure/success column until source video or independent human review clarifies it.
- A person enters **B20**, which may become an outcome-correlated shortcut; temporal exclusion or episode quality control needs consideration before training.

These counts are **visual assessments, not recovered native labels or performance metrics**. The task-matched pilot is intentionally selected, and these 20 cases are not a representative prevalence or generalization estimate of the full dataset.

## Feasibility judgment

**Conditional GO for subsequent fusion research, after the label-key comparison and data-contract checks.** These camera views show **substantially more task-relevant action information than MSM's obstructed milling view** in the supplied pilot. Important contrasts are visible (correct/wrong target placement; dropped or unmoved objects; plugged/unplugged connector; tube orientation), so a learned visual feature branch has a plausible signal source.

However, **visual informativeness does not imply multimodal complementarity**. Robot positions/velocities and limited gripper effort may already predict many outcomes; sensors could also contain telemetry defects. The benefit of fusion remains an empirical question and must be tested against strong, quality-controlled unimodal baselines.

**Before interpreting any model result:**

1. Lock this blind review, then separately compare its case decisions with the native key; preserve disagreements, including `B02`, rather than retrospectively editing the blind judgments.
2. Obtain a separate human independent review if the thesis needs human-reliability claims. This AI inspection does not fulfill that requirement.
3. In a predeclared full-cohort quality-control procedure, handle six duplicate episode pairs and constant-position streams; check for target leakage from human interventions, backgrounds, task identity, late frames, or telemetry acquisition artifacts. Do not choose exclusions using outcome labels.
4. Adopt **task-disjoint held-out evaluation** and use all splits and preprocessing within training groups only; session/operator independence remains unverified. Avoid treating the 20 matched examples as a train/test sample or claiming cross-dataset weights were transferred without a checkpoint.
5. Predefine 16-frame video representations, sensor-only models, vision-only models, simple averaging, and the unchanged F2/gated fusion policies. Compare held-out Average Precision, PR metrics, calibration and corruption sensitivity across multiple fixed seeds, keeping features and training budgets comparable. Preserve original REASSEMBLE checkpoint lineage and document any retraining/adaptation explicitly.

## Scope and limitations

Inspection is from sparse 16-frame samples, not continuous replay or a mechanical validation of object contact. The 16 timestamps may miss short events. Cropped views can conceal targets; full high camera was preferred. The plotted observation streams demonstrate available channels and timing indices, **not** validated force/torque units, correct hardware time synchronization, or causal sensor usefulness. No native labels were opened; no unblinding, training, numerical model evaluation, source modification or repository commit was performed.
