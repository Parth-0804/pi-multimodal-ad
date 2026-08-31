# The RT-DETR Storybook 🔍

A gentle, picture-book explanation of how a real object detector — RT-DETR
(Real-Time Detection Transformer) — looks at a photo and guesses where
things are. Written so a curious beginner (or a curious kid) can follow
along, using **real photos from the PHM 2026 gear-tooth dataset**, read
straight out of the **raw challenge archives**.

> **This is a tutorial, not thesis evidence.** It lives in `tutorials/`,
> separate from `src/pi_multimodal_ad/`, `scripts/`, `configs/`, and
> `runs/`. It does not follow — and does not need to follow — the
> governed run/provenance rules in `AGENTS.md`; those apply to the actual
> research pipeline, not to this teaching aid. Nothing here counts as
> "model training": every script here either reads raw data read-only, or
> runs a pretrained model in inference mode. No weight is ever updated,
> and `gtc-data-experiment/` is never written to.

## Meet the cast of characters

Imagine the model as a small robot detective looking at a photo of a
worn gear tooth:

| Story character | Real name | What it does |
|---|---|---|
| **Getting Ready** 🧹 | Preprocessing + target definition | Before any detective work starts, we crop a fixed region of the photo, even out the lighting, and highlight dark streaky patches. This turns "a photo" into "a provisional measurement of candidate damage" — see below. |
| **The Eyes** 👀 | Backbone (a convolutional network) | Puts on many pairs of "magic glasses," each noticing a different simple thing: an edge here, a bright spot there, a rough texture over there. |
| **The Brain** 🧠 | Hybrid encoder (RT-DETR's "AIFI" Transformer layer) | Lets far-apart puzzle pieces of the photo "raise their hands" and talk to each other — even ones on opposite corners of the image — so the model can reason about the whole picture, not just nearby pixels. To keep things fast, RT-DETR only does this expensive chatting on the smallest, most zoomed-out view, then blends the result back into the other zoom levels. |
| **The Finder** 🕵️ | Decoder + object queries | Sends out a fixed number of little detectives (often 300!). Each one independently guesses "I think something is *here*, and I think it's a *this*." Most guesses get thrown out; only the confident, non-duplicate ones survive. |
| **The Final Drawing** 🖍️ | Bounding boxes | We draw boxes around the survivors: green for the "official" answer key, red for the robot's own guess. |

## Two ways to get real demo images

| Loader | Where images come from | What you need |
|---|---|---|
| **`make_raw_demo_dataset.py`** (preferred) | Opens the **raw, immutable** challenge archives directly: `gtc-data-experiment/photos/EXP-{A,B,F}/Exp-*_Photos_Run-*.zip`. Read-only, one image at a time — never extracts in place, never modifies the archive. | The raw PHM 2026 data mounted locally (`gtc-data-experiment/`), plus `opencv-python`, `numpy`, `pillow`, `pandas`, `pyyaml` (all already in the repo's `requirements.txt`). |
| **`make_demo_dataset.py`** (fallback) | Copies already-cached images out of a prior pseudo-box run: `runs/phm2026_rtdetr_pseudo_boxes/<run-id>/`. Useful if you don't have the raw archives mounted where you're running this (e.g. a sandbox without the raw data). | Nothing beyond the Python standard library. |

Both write the same `image.jpg` + `image.md` pair format, so
`rtdetr_storybook.py` doesn't care which one produced its input.

## Why a raw photo needs "getting ready" first

The PHM 2026 challenge archives ship **no organizer damage boxes at
all** (`docs/planning/T2_TARGET_FORMULATION_DECISION.md`: *"The challenge
archives provide no organizer damage boxes"*). So before RT-DETR can be
taught to find anything, two questions have to be answered honestly:

1. **What part of the photo matters?** A gear tooth only occupies part of
   the frame, and lighting varies photo to photo. `make_raw_demo_dataset.py`
   crops to a *fixed* "visible flank" region of interest (ROI) — the same
   normalized box for every photo — and evens out brightness with CLAHE
   (contrast-limited adaptive histogram equalization) so a dark tooth in
   one photo and a bright tooth in another are judged on the same scale.

2. **What counts as "damage"?** The pipeline estimates a smooth local
   background (a big Gaussian blur) and subtracts it from the
   contrast-normalized image to get a "dark residual" — places noticeably
   darker than their surroundings. That residual is turned into a robust
   z-score (using the median and MAD, so a few extreme pixels can't skew
   the whole scale) and thresholded. The surviving blobs are cleaned up
   with morphological open/close, and only *wide, flat* ("horizontal")
   blobs are kept — real spall/pitting on a gear tooth tends to read as a
   horizontal streak, not a round dot.

**Every one of those parameters — the ROI box, the CLAHE clip limit, the
blur size, the z-score threshold — is read from the same pinned config
file the real thesis pipeline trains against:
`configs/experiments/phm2026_image_target.yaml`.** This tutorial does not
invent its own numbers or its own image-processing rule; it calls the
exact same function
(`pi_multimodal_ad.targets.image_damage.measure_damage_candidate`) the
governed pipeline calls. `rtdetr_storybook.py`'s new **Step 0** runs this
live and shows you the ROI and the surviving mask before Steps 1-4 even
start.

## What makes an RT-DETR result actually *valuable* here?

This is the honest part, and it's worth reading before you draw any
conclusions from boxes this tutorial produces. The percentage and boxes
above have an official name — target definition `phm2026_image_damage_v2`
— and an official status: **provisional pseudo-label, not organizer
ground truth, not expert-reviewed.**

Per `docs/planning/T2_TARGET_FORMULATION_DECISION.md`'s "Human
validation" section, a value only becomes trustworthy once someone has:

1. reviewed whether the fixed ROI actually captures the visible tooth
   flank for that photo (framing varies);
2. reviewed whether the mask is really damage, and not glare, shadow, a
   tooth edge, focus blur, or ordinary surface texture falsely flagged;
3. recorded a corrected value, a reviewer identity, and a timestamp when
   the automatic value is wrong;
4. accounted for the fact that EXP-A/EXP-B and EXP-F use *different
   imaging protocols* (`docs/planning/R4_PSEUDO_BOX_CHECKPOINT.md` — this
   is exactly why this tutorial's own EXP-F demo images tend to show many
   more "candidate" boxes than EXP-A/EXP-B ones: that's a protocol
   difference showing up in the heuristic, not proof of more real
   damage).

Until that review happens, here's what you can and can't honestly say
about anything RT-DETR predicts against these boxes:

| You CAN say | You CANNOT say |
|---|---|
| "The model's raw guesses do/don't overlap with our heuristic's candidate regions." | "The model correctly found spall damage." |
| "This is engineering evidence that the pipeline runs end-to-end." | "This measures physical damage accuracy." |
| "This pseudo-box standard is versioned, reproducible, and documented." | "This pseudo-box standard is validated ground truth." |

If you want to go further than this tutorial and get toward something
genuinely valuable for the thesis, the real next steps (already scoped in
`docs/planning/PROJECT_STATE.md`) are: (a) get a human to review a sample
of masks/boxes using the review guide the governed pipeline already
generates (`HUMAN_PSEUDO_BOX_REVIEW_GUIDE.md` in a
`phm2026_rtdetr_pseudo_boxes` run), (b) only *then* fine-tune RT-DETR for
real on the reviewed boxes via `scripts/training/train_rtdetr_detector.py`, and (c)
evaluate with a proper held-out split (the pipeline already uses
EXP-B/train, EXP-A/validation, EXP-F/test — this tutorial's raw loader
mirrors that same split for its 6-image demo, on purpose).

## Why Markdown files instead of a normal label format?

Most object-detection tutorials store labels as `.txt` (YOLO format) or a
big `.json` (COCO format) — both are efficient but not very readable.
This tutorial instead pairs every image with a matching `.md` file you
can open and read like a little report card. `rtdetr_storybook.py`
contains a small **custom parser** — `parse_md_targets()` — that scans
these `.md` files for three things:

- a line like `- Image size: 2560 x 1440 pixels`
- a line like `- Status: PROVISIONAL pseudo-label — ...`
- a Markdown table of boxes:

  ```markdown
  | class | x_min | y_min | x_max | y_max |
  |---|---|---|---|---|
  | damage_candidate | 424.0 | 217.0 | 450.0 | 225.0 |
  ```

Everything else in the file (headings, extra notes, the preprocessing
explanation `make_raw_demo_dataset.py` adds) is ignored by the parser, so
you can freely annotate these files by hand without breaking anything.

The model itself is the **stock, COCO-pretrained baseline**
(`rtdetr-l.pt`) — it has never seen a gear tooth and was never fine-tuned
on this data. Its raw guesses will use everyday COCO object names, and
will very likely **not** line up with the green "damage_candidate"
boxes. That mismatch is expected, and is itself part of the lesson: it's
exactly why the real, governed pipeline
(`scripts/training/train_rtdetr_detector.py`) has to fine-tune RT-DETR on
reviewed data before it becomes useful for this task.

## How to run it

```bash
cd tutorials/rtdetr_storybook

# 1. Install dependencies. For the full experience (raw-data loading +
#    Step 0 preprocessing), install everything the repo already uses:
pip install -r ../../requirements.txt
#    If you only want Steps 1-4 (no raw-data access, no Step 0), you can
#    get away with just: pip install ultralytics

# 2a. Preferred: build a small, real demo dataset straight from the raw
#     archives (needs gtc-data-experiment/ mounted locally).
python make_raw_demo_dataset.py

# 2b. Fallback: build it from a cached prior run instead (no raw data
#     needed; used automatically by rtdetr_storybook.py if raw_demo_data/
#     doesn't exist).
python make_demo_dataset.py

# 3. Run the storybook! First run downloads the ~65 MB pretrained
#    checkpoint from Ultralytics, so you need internet access once.
python rtdetr_storybook.py
```

Look inside `outputs/<image_name>/` afterwards for:

- `step0_preprocessing.png` — the fixed ROI on the full photo, and the
  final candidate mask painted on the ROI crop (only if you installed the
  full requirements and didn't pass `--no-preprocessing`).
- `step1_eyes.png` — original photo next to an "activation energy" map
  from an early backbone layer (edges/colors/textures).
- `step2_brain.png` — same idea, but after the Transformer encoder has
  let distant patches talk to each other.
- `step4_final_drawing.png` — the photo with green (answer key) and red
  (model guess) boxes drawn on top.

Console output narrates all five steps as they happen, including the
real tensor shapes and measurement numbers captured along the way.

### A note on Step 1 / Step 2 "attention" pictures

Those heatmaps show **activation magnitude** (how loudly a layer's
channels are firing at each spot), captured with a PyTorch forward hook —
not the literal numeric attention-weight matrix from inside
`nn.MultiheadAttention`. Extracting the exact attention weights would
mean patching PyTorch/Ultralytics internals in a way that's fragile
across versions. The activation-energy view tells the same story a
beginner needs ("here is where this stage of the network is focusing its
energy") without that fragility, and the script says so on-screen too.

### Useful flags

```bash
python rtdetr_storybook.py --max-images 1        # just do one photo
python rtdetr_storybook.py --device cuda:0       # use a GPU if you have one
python rtdetr_storybook.py --conf 0.1            # show more (lower-confidence) guesses
python rtdetr_storybook.py --no-preprocessing    # skip Step 0 even if available
python make_raw_demo_dataset.py --raw-root /path/to/gtc-data-experiment
python make_demo_dataset.py --output-dir my_demo
```

## Files in this folder

| File | What it does |
|---|---|
| `make_raw_demo_dataset.py` | Preferred, read-only: opens raw `gtc-data-experiment/photos/...` archives directly, re-runs the real pinned preprocessing/target pipeline, writes raw image copies + derived `.md` targets. |
| `make_demo_dataset.py` | Fallback, read-only: copies a handful of real PHM images + targets out of a prior cached run. Never modifies the source run. |
| `rtdetr_storybook.py` | The main event: Step 0 preprocessing walkthrough, custom `.md` parser, model loading, hook-based intermediate visualization, final drawing. |
| `raw_demo_data/` | Generated by `make_raw_demo_dataset.py` (scratch output, not checked in). |
| `demo_data/` | Generated by `make_demo_dataset.py` (scratch output, not checked in). |
| `outputs/` | Generated by `rtdetr_storybook.py`. |

## If something breaks

- **`ModuleNotFoundError` / "needs a few extra libraries"**: run
  `pip install -r ../../requirements.txt` from this folder (or
  `pip install ultralytics` if you only want Steps 1-4) — both loader
  scripts and the storybook check for this themselves and print exactly
  this fix instead of crashing.
- **"Raw data root not found"**: `make_raw_demo_dataset.py` needs
  `gtc-data-experiment/` mounted where you're running it; that raw data
  is never checked into git (see `AGENTS.md`'s data boundaries). Either
  run this where the raw challenge data lives, pass `--raw-root`, or fall
  back to `make_demo_dataset.py`.
- **No internet on first run**: the first `RTDETR("rtdetr-l.pt")` call
  needs to download the checkpoint once; after that it's cached locally
  by Ultralytics.
- **A "could not find a layer for '...'" note**: different Ultralytics
  versions occasionally rename internal modules. The script looks up
  layers by *class name* (e.g. any module whose class name contains
  `"AIFI"`) specifically so it keeps working across versions, but if a
  panel gets skipped, that's why — the rest of the story still runs.
- **This tutorial was authored in a sandbox with no `gtc-data-experiment/`
  and none of torch/ultralytics/opencv/pandas installed**, so the raw-data
  path and Step 0 have been verified by logic/unit-testing pieces in
  isolation, not by a real end-to-end run. Please treat the first real run
  in your actual environment as a verification step, not a formality.
