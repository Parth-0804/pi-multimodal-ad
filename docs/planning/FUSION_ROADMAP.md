# Fusion roadmap

Status: **PLAN — no stage below has been executed.**
Written: 2026-09-11

This is the staged route from "two unimodal baselines that both lose to a
constant" to a defensible fusion result. Every stage ends in a **gate**: a
question with a factual answer that decides whether the next stage is worth
doing. Gates exist so that a dead end costs days, not weeks.

Nothing here may be reported as a result until it has actually been run.

---

## What is already settled (do not re-litigate)

| Fact | Source |
|---|---|
| Images do not exist at inference — test and validation experiments are sensor-only | Organizer challenge description |
| Therefore fusion cannot mean "two live input streams" | Follows from the above |
| Both baselines lose to the train-mean constant at run level | `runs/` reports; constant MAE 0.6797 pp |
| The constant is fit on train only, not an oracle | `models/patchtst_regression.py::build_predictions` |
| 20 labelled runs total: 7 train (EXP-B), 5 validation (EXP-A), 8 test (EXP-F) | `configs/experiments/phm2026_patchtst_baseline.yaml` |
| 560 per-tooth labels exist and are persisted | `tables/per_tooth_damage.parquet` |
| A 102.4 kHz shaft-encoder channel exists in the raw HDF5 | Organizer challenge description |
| That encoder channel is **not** in the 72-feature pipeline | `reports/feature_schema.json` |
| No keyphasor / index-pulse is documented anywhere in this repo | Repo-wide search |
| The target is a provisional pseudo-label; 0 of 560 human reviews are done | `reports/target_quality_report.json` |
| Official scoring is MSE **after an optimal monotonic rescale** | Organizer challenge description |
| No result in this repo has ever been scored that way | No such code exists |
| All 28 existing runs were produced from a dirty working tree | `docs/thesis/RUN_INDEX.md` |

---

## Stage 0 — Integrity lockdown

**Why first:** every number downstream inherits whatever is wrong here. This
is the cheapest stage and the only one that is unambiguously mandatory.

1. **Resolve the PatchTST discrepancy.** Two numbers exist for the same config
   hash `433d4154`: MAE 1.011 (Aug run, `cuda:0`) and MAE 0.8314
   (Sep run, `cpu`, plus uncommitted edits to `patchtst.py` /
   `timeseries.py`). Stash the edits, re-run on CPU, compare:
   - lands on ~1.011 → the code edits moved it
   - lands on ~0.8314 → the device change moved it
2. **Decide what the uncommitted edits are.** If they are an improvement,
   they are a *new variant* with its own name and its own run — not a
   re-run of the baseline. If they are scratch, revert them.
3. **Commit whatever the baselines actually need**, so at least the two
   canonical runs can be reproduced from committed code. All 28 current runs
   carry `git.dirty: true` at commit `d3ce4808`; the thesis needs at least the
   two headline runs to be clean.
4. **Pick the canonical image baseline** from R3 / R4-detector /
   R4-multitask. They are not interchangeable — R4-multitask beats R3 at
   image level (0.733 vs 0.894) and loses at run level (1.627 vs 1.347).
5. **Freeze the index:**
   ```bash
   python scripts/ops/build_thesis_run_index.py \
     --canonical <sensor-run-id> --canonical <image-run-id>
   ```

> ### GATE A
> *Do two baseline numbers exist that were produced from committed code, on a
> known device, with a documented split?*
> **No → stop. Nothing downstream is citable.**

---

## Stage 1 — Interrogate the label before building on it

**Why:** every model here is trained against `phm2026_image_damage_v2`, which
no human has ever checked. If the label is confounded, fusion will faithfully
learn the confound.

1. **Target scale.** `df.groupby("experiment")["raw_top3_mean_pct"].agg(["mean","std","min","max"])`.
   Needed to know whether MAE 0.68 is a large or trivial error.
2. **Protocol confound.** In EXP-A/B, teeth 1–4 get ten views; every other
   tooth and all of EXP-F get one. `aggregate_targets` takes the **max**
   across views, and max-of-10 stochastically dominates max-of-1. Check which
   tooth indices actually land in the top-3 per experiment. If teeth 1–4
   dominate in A/B but not in F, the label partly encodes camera protocol,
   and cross-experiment generalisation is partly measuring that.
3. **Shrinkage test.** Compare `std(prediction)` against `std(label)` for R3
   and R4 per-image outputs. A model that has collapsed toward the mean will
   show a much narrower prediction spread — which is consistent with the
   positive bias (+0.686) already observed on the sensor side.
4. **Human review of a sample.** Not all 560 — 30 stratified across
   low/medium/high would already tell you whether the masks are finding spall
   or finding shadows. `reports/HUMAN_TARGET_REVIEW_GUIDE.md` already
   specifies the procedure.

> ### GATE B
> *Is the label measuring damage, or measuring camera protocol?*
> - **Measuring damage** → proceed to Stage 2.
> - **Protocol-confounded** → fix the aggregation rule first (per-tooth
>   view-count normalisation, or drop to one view per tooth everywhere for
>   comparability). Re-derive the target. This is a detour, not a failure —
>   and it is a genuine thesis finding either way.

---

## Stage 2 — Re-score everything under the metric that actually counts

**Why:** the organizer applies an optimal monotonic transform before
computing MSE. Every number in this repo is raw MAE on a self-defined scale.
These can disagree sharply: a model that tracks trajectory *shape* well but
sits at the wrong offset scores badly on MAE and well under monotonic-MSE.

1. Implement `evaluation/monotonic.py`: fit an isotonic regression from
   prediction → target on the evaluation set, then compute MSE on the
   transformed predictions. Mirror the existing style in
   `evaluation/regression.py`.
2. Re-score, at minimum: both baselines, both constants, and the Ridge
   comparison already present in `build_predictions`.
3. Note the asymmetry honestly: **a constant cannot benefit from monotonic
   rescaling** (a flat prediction carries no rank information, so isotonic
   regression cannot recover any). If PatchTST has *any* real rank signal —
   current Spearman is 0.119, weak but not zero — this is precisely the metric
   where it could overtake the constant.

> ### GATE C
> *Does the ranking change under monotonic-MSE?*
> - **Yes, a model now beats the constant** → that is the headline result, and
>   the whole "our baselines lose" narrative needs rewriting. High value.
> - **No** → the negative result hardens considerably: it now holds under the
>   organizer's own metric, not just ours. Also high value, and much more
>   defensible than the current framing.

---

## Stage 3 — Fusion that needs no new data

**Why:** this is the only fusion that is fully buildable today, with data
already extracted, and it makes "missing-modality robustness" a real
experiment rather than a claim.

The 9 channels already in the feature pipeline split into three genuine
sub-modalities, all present at inference:

| Sub-modality | Channels | Nature |
|---|---|---|
| Process context | `rpm`, `torque`, `temperature` | operating conditions |
| Organizer RMS | `axial_rms`, `radial_rms` | broadband vibration energy |
| Condition indicators | `fm4`, `na4`, `m6a`, `alr` | classical gear-fault CIs |

1. **Unimodal-per-branch:** train the existing PatchTST on each subset alone.
   Three cheap runs. This alone is a publishable ablation at N=7 training runs.
2. **Late fusion:** one encoder per sub-modality, concatenate pooled
   embeddings, single scalar head.
3. **Gated fusion:** gate the vibration branches on the context branch. This
   is where "process-aware gating" becomes literal rather than aspirational —
   gating on RPM/torque/temperature is exactly what the phrase should mean.
4. **Missing-modality ablations:** drop one accelerometer, corrupt a channel,
   zero the CIs. Report degradation curves.

> ### GATE D
> *Does any sub-modality combination beat the constant (under both MAE and
> monotonic-MSE)?*
> - **Yes** → you have a working fusion result with no new data. Stages 4–6
>   become optional enrichment rather than necessity.
> - **No** → the binding constraint is confirmed to be sample size (7 training
>   runs), not representation. Proceed to Stage 4, which is the only stage that
>   actually attacks sample size.

---

## Stage 4 — Per-tooth supervision (the 28× lever)

**Why:** this is the highest-ceiling and highest-cost stage. You have 560
tooth-level labels and are currently squeezing them into 20 run-level
scalars. Supervising per-tooth multiplies effective sample count by 28 and
replaces an arbitrary cross-modal correspondence with a physical one.

**4a — Feasibility probe first (do this before anything else in Stage 4).**
Open one raw HDF5 file and answer, factually:
- Is there an encoder/tacho dataset, and what does it contain — raw pulses, or
  an already-derived angle?
- What are the actual `sampling_rate` attributes on accel1, accel2, encoder?
- Is there any index/trigger/keyphasor marking a fixed angular origin?

**4b — Rotation-invariant path (works without a keyphasor).**
Angular-resample the vibration to a fixed samples-per-revolution grid using
the encoder, segment into 28 equal sectors, but treat sector identity as
*unknown*. Supervise the per-tooth damage **distribution** (sorted profile)
rather than tooth-indexed values. You lose "which tooth" and keep "how the
damage is spread" — which is what the top-3 aggregation actually cares about.

**4c — Tooth-indexed path (requires a keyphasor).**
Only if 4a finds a fixed angular origin. Pairs tooth *j*'s photo with tooth
*j*'s vibration sector directly. This is the version that makes
"physics-informed" concrete.

> ### GATE E
> *Is the encoder channel usable, and does a fixed angular origin exist?*
> - **Encoder usable + keyphasor exists** → 4c. Strongest possible version.
> - **Encoder usable, no keyphasor** → 4b. Still a large gain, still principled.
> - **Encoder unusable / absent** → Stage 4 is closed. Say so explicitly in the
>   thesis; it is a legitimate documented limitation, and it makes the
>   run-level ceiling an evidenced constraint rather than an assumption.

---

## Stage 5 — Privileged-information distillation

**Why:** this is where the image modality's contribution actually lives, given
that images vanish at inference. The image branch is a **teacher** that shapes
the sensor representation during training and is then discarded.

1. Teacher: the canonical image model, producing either its 768-dim pooled
   embedding or its per-image scalar.
2. Student: the sensor model, trained with a combined loss — task loss against
   the target, plus a distillation term pulling the sensor embedding toward
   the image embedding for the same run.
3. Ablate the distillation weight, including zero (which reduces to Stage 3).

> ### GATE F
> *Does distillation beat the same sensor architecture trained without it?*
> - **Yes** → this is the thesis's central claim, and it is a clean one:
>   images improve a sensor-only model that never sees images.
> - **No** → report it. A negative distillation result at N=7 training runs is
>   an honest and expected outcome, and it is strengthened by Stage 6.

---

## Stage 6 — Oracle upper bound

Train a model that *does* get images at inference on the 20 labelled runs.
This is not deployable and is not a submission candidate — it is a
measuring instrument. The gap between the oracle and the deployable
sensor-only model is a quantitative answer to *"what is the image modality
worth here?"*, reported as a number rather than an intuition.

Report the oracle and the deployable model side by side, always, and never
let the oracle be mistaken for a result.

---

## Stage 7 — Thesis framing

By this point one of these is true, and each is a defensible thesis:

- **A model beats the constant.** Lead with it; Stages 1–2 become the
  methodology that made it trustworthy.
- **Nothing beats the constant, but the oracle gap is large.** The story is
  "the image modality carries real information that the sensor modality cannot
  currently recover at N=7" — with Stage 6 quantifying "real".
- **Nothing beats the constant and the oracle gap is small.** The story is
  "the provisional label is the binding constraint, not the modality or the
  architecture" — with Stage 1 as the evidence.

All three require the same work. Which one you get is not under your control;
whether it is defensible is.

---

## What would invalidate this plan

- Stage 1 finds the label is protocol-confounded → Stages 3–6 are all training
  against an artefact until the target is re-derived.
- Stage 4a finds no encoder data in the HDF5 → the 28× lever does not exist,
  and run-level N=20 is a hard ceiling.
- Human review rejects a large fraction of masks → the target needs redefining
  before any fusion claim is meaningful.

None of these are failures. Each is a finding, and each is cheaper to discover
at its own gate than after the fusion model is built.
