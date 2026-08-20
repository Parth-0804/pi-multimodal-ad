# RT-DETR Storybook — first real end-to-end run

This is the record of the **first actual execution** of this tutorial against
real data, per the disclaimer at the bottom of `README.md` ("this tutorial
was authored in a sandbox with no `gtc-data-experiment/` ... please treat the
first real run in your actual environment as a verification step"). It ran
clean: **no code changes were needed** in `make_raw_demo_dataset.py` or
`rtdetr_storybook.py`. Every field mapping, filename-parsing assumption, and
forward-hook lookup the sandboxed author flagged as a "likely candidate" for
breakage turned out to work as designed against the real archives and the
installed Ultralytics version.

> As with everything else this tutorial produces: the numbers below are
> **provisional pseudo-labels from an untrained, stock COCO-pretrained RT-DETR
> baseline**, not validated results, not organizer ground truth, and not
> expert-reviewed. See `README.md`'s "What makes an RT-DETR result actually
> *valuable* here?" section before drawing any conclusion from them.

## Commands run

```bash
cd tutorials/rtdetr_storybook
../../ma_thesis_env/bin/python make_raw_demo_dataset.py
../../ma_thesis_env/bin/python rtdetr_storybook.py --max-images 3
```

(`ma_thesis_env` is this repo's existing virtualenv — already had every
dependency the tutorial needs, so no `pip install` step was required.)

## Environment

| | |
|---|---|
| OS | Linux 6.8.0-137-generic, x86_64 |
| Python | 3.12.3 (`ma_thesis_env`) |
| torch | 2.13.0+cu130 |
| torch CUDA available | `True` (NVIDIA GPU present, driver 580.167.08, CUDA 13.0) |
| Device actually used | **CPU** — ran with the script's default `--device cpu`; the GPU was available but not requested |
| ultralytics | 8.4.104 |
| opencv-python | 5.0.0 |
| numpy | 2.4.6 |
| pandas | 2.3.3 |
| pillow | 12.3.0 |
| RT-DETR checkpoint | `rtdetr-l.pt` (stock COCO-pretrained baseline, auto-downloaded from Ultralytics' release assets on first use, ~65 MB) |

## What actually happened vs. what the sandboxed author worried about

The task brief called out three specific risk areas to check. All three held up:

1. **`discover_run_archive()`'s glob/regex assumptions.** Real archive names
   for EXP-A/EXP-F use `Exp-<X>_Photos_Run-<n>.zip` (hyphen before the run
   number) while EXP-B uses `Exp-B_Photos_Run <n>.zip` (a space instead). Both
   forms matched `PHM2026Adapter.parse_run()`'s regex (`RUN[\s_-]*(\d+)`)
   without changes.
2. **`list_canonical_tooth_members()`'s `TOOTH_<n>` filename assumption.**
   The real canonical images are named `Tooth 05.jpg`, `Tooth 06.jpg`, etc.
   (space, not underscore, and not zero-padded consistently) — matched by
   `PHM2026Adapter`'s tooth regex (`TOOTH[\s_-]*0*(\d+)`, case-insensitive)
   without changes.
3. **`ImageDamageOptions` field mapping vs.
   `configs/experiments/phm2026_image_target.yaml`.** Every field the
   dataclass requires was present under the YAML's `image_measurement` /
   `target_definition` sections with matching names; the loader function in
   `make_raw_demo_dataset.py` needed no changes.

The README's warning about `StorybookHooks`' forward-hook module lookup being
"the most likely fragile point across Ultralytics versions" also did not
materialize: against ultralytics 8.4.104, all three named modules were found
by class-name substring match (`Conv`/`HGStem`/`Stem` for the Eyes,
`AIFI` for the Brain, `RTDETRDecoder` for the Finder) — the console never
printed the "`[note] could not find a layer for '...'`" fallback message for
any of the three images.

## Sanity-checking the boxes

Before running the storybook, boxes from a couple of `raw_demo_data/*.md`
files were drawn back onto their source `.jpg` (ad hoc, not part of the
tutorial's own code) to check they looked plausible. They did: every box sits
inside the fixed ROI (as it must, since boxes are pixel coordinates of
components found only within the ROI crop), and on both inspected images the
boxes cluster tightly along the actual dark, rough-textured streak running
across the tooth flank — not scattered across clean, undamaged metal and not
empty.

## Per-image numbers

### `make_raw_demo_dataset.py` — all 6 images written

| stem | split | tooth | box count | damage_candidate_area_pct | source |
|---|---|---|---|---|---|
| `raw_expb_run1_tooth05` | train | 5 | 18 | 1.579% | EXP-B Run 1 |
| `raw_expb_run1_tooth06` | train | 6 | 20 | 1.468% | EXP-B Run 1 |
| `raw_expa_run1_tooth05` | validation | 5 | 41 | 3.370% | EXP-A Run 1 |
| `raw_expa_run1_tooth06` | validation | 6 | 40 | 1.867% | EXP-A Run 1 |
| `raw_expf_run1_tooth01` | test | 1 | 46 | 2.556% | EXP-F Run 1 |
| `raw_expf_run1_tooth02` | test | 2 | 39 | 3.252% | EXP-F Run 1 |

All 6 report `segmentation_confidence` in the 0.97–0.99 range and
`measurement_status: provisional_pseudo_label_pending_human_review`. As the
README predicts, the two EXP-F (test) images and the EXP-A (validation)
images show a visibly higher candidate-area percentage than the EXP-B
(train) images — consistent with a protocol difference between experiments,
not necessarily more real damage (see README's "What makes an RT-DETR result
actually *valuable* here?").

### `rtdetr_storybook.py --max-images 3` — the 3 images actually walked through

Only the first 3 of the 6 image/`.md` pairs (alphabetical order) were
processed, per `--max-images 3`. For each: how many of the model's raw
guesses (out of the 300 decoder queries) survived at `--conf 0.25` (the
default), and what class/confidence/box they were.

**`raw_expa_run1_tooth05`** — target: 41 boxes, 3.370% candidate area.
Model: **1 of 300** guesses survived.
| class | conf | box (xyxy) |
|---|---|---|
| `tv` | 0.879 | `[3.3, -0.1, 2554.1, 1438.5]` (near-full-frame) |

**`raw_expa_run1_tooth06`** — target: 40 boxes, 1.867% candidate area.
Model: **3 of 300** guesses survived.
| class | conf | box (xyxy) |
|---|---|---|
| `tv` | 0.824 | `[2.7, 0.7, 2550.0, 1438.9]` (near-full-frame) |
| `refrigerator` | 0.309 | `[2.7, 0.7, 2550.0, 1438.9]` (same box, different class) |
| `cell phone` | 0.306 | `[2.7, 0.7, 2550.0, 1438.9]` (same box, different class) |

**`raw_expb_run1_tooth05`** — target: 18 boxes, 1.579% candidate area.
Model: **4 of 300** guesses survived.
| class | conf | box (xyxy) |
|---|---|---|
| `car` | 0.585 | `[0.5, 2.0, 2560.5, 1435.6]` (near-full-frame) |
| `tv` | 0.540 | `[0.5, 2.0, 2560.5, 1435.6]` (same box, different class) |
| `person` | 0.341 | `[943.2, 234.8, 1229.6, 594.7]` |
| `person` | 0.288 | `[950.2, 372.3, 1194.5, 597.2]` |

No layer lookups failed for any of the 3 images — `step1_eyes.png`,
`step2_brain.png`, and the Step 3 console narration were produced for all
three.

### Why the near-full-frame "guess" boxes look invisible in the final drawing

For `raw_expa_run1_tooth05` and `raw_expa_run1_tooth06`, the sole/dominant
surviving guess is a box spanning almost the entire 2560×1440 photo (e.g.
`[3.3, -0.1, 2554.1, 1438.5]`). Drawn at 4px width, that renders as a thin
red line hugging the image border — easy to miss at a glance but visible on
close inspection of `step4_final_drawing.png`, and confirmed by directly
querying `result.boxes` outside the drawing code. This is not a rendering
bug; it is the stock model's actual raw guess. Untrained on gear teeth, it is
reading the whole macro photo as an indoor scene and guessing everyday COCO
objects (`tv`, `refrigerator`, `cell phone`, `car`) that span the frame. For
`raw_expb_run1_tooth05`, two `person` guesses land as smaller, distinct boxes
over the dark hole/crater near the left of the flank — still a COCO-vocabulary
mismatch, but a more legible one.

This mismatch between the model's everyday-object guesses and the
`damage_candidate` targets is exactly the expected, intentional lesson the
README calls out: the stock baseline has never seen a gear tooth, so its raw
guesses use COCO's everyday vocabulary and won't line up with the green
boxes — which is why `scripts/train_rtdetr_detector.py` has to fine-tune the
model on reviewed data before it is useful for this task.

## What's in this folder

Copied from `outputs/raw_expb_run1_tooth05/` (chosen as the single
representative example — it has the clearest Step 0 mask and the most
legible Step 4 drawing among the 3 processed images):

- `step0_preprocessing.png` — fixed ROI + surviving candidate mask
- `step1_eyes.png` — backbone activation-energy heatmap
- `step2_brain.png` — post-AIFI-encoder activation-energy heatmap
- `step4_final_drawing.png` — green target boxes + red model guesses

`raw_demo_data/`, `demo_data/`, and the rest of `outputs/` (all 3 processed
images' full figure sets) were left alone — they're git-ignored scratch
output, not committed.
