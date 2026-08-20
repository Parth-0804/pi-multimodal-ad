# The RT-DETR Storybook 🔍

A gentle, picture-book explanation of how a real object detector — RT-DETR
(Real-Time Detection Transformer) — looks at a photo and guesses where
things are. Written so a curious beginner (or a curious kid) can follow
along, using **real photos from the PHM 2026 gear-tooth dataset**.

> **This is a tutorial, not thesis evidence.** It lives in `tutorials/`,
> separate from `src/pi_multimodal_ad/`, `scripts/`, `configs/`, and
> `runs/`. It does not follow — and does not need to follow — the
> governed run/provenance rules in `AGENTS.md`; those apply to the actual
> research pipeline, not to this teaching aid. Nothing here counts as
> "model training": both scripts either copy files or run a pretrained
> model in inference mode only. No weight is ever updated.

## Meet the cast of characters

Imagine the model as a small robot detective looking at a photo of a
worn gear tooth:

| Story character | Real name | What it does |
|---|---|---|
| **The Eyes** 👀 | Backbone (a convolutional network) | Puts on many pairs of "magic glasses," each noticing a different simple thing: an edge here, a bright spot there, a rough texture over there. |
| **The Brain** 🧠 | Hybrid encoder (RT-DETR's "AIFI" Transformer layer) | Lets far-apart puzzle pieces of the photo "raise their hands" and talk to each other — even ones on opposite corners of the image — so the model can reason about the whole picture, not just nearby pixels. To keep things fast, RT-DETR only does this expensive chatting on the smallest, most zoomed-out view, then blends the result back into the other zoom levels. |
| **The Finder** 🕵️ | Decoder + object queries | Sends out a fixed number of little detectives (often 300!). Each one independently guesses "I think something is *here*, and I think it's a *this*." Most guesses get thrown out; only the confident, non-duplicate ones survive. |
| **The Final Drawing** 🖍️ | Bounding boxes | We draw boxes around the survivors: green for the "official" answer key, red for the robot's own guess. |

## Why Markdown files instead of a normal label format?

Most object-detection tutorials store labels as `.txt` (YOLO format) or a
big `.json` (COCO format) — both are efficient but not very readable.
This tutorial instead pairs every `image_sample_....jpg` with a matching
`image_sample_....md` file you can open and read like a little report
card. `rtdetr_storybook.py` contains a small **custom parser** —
`parse_md_targets()` — that scans these `.md` files for three things:

- a line like `- Image size: 2560 x 1440 pixels`
- a line like `- Status: PROVISIONAL pseudo-label — ...`
- a Markdown table of boxes:

  ```markdown
  | class | x_min | y_min | x_max | y_max |
  |---|---|---|---|---|
  | damage_candidate | 424.0 | 217.0 | 450.0 | 225.0 |
  ```

Everything else in the file (headings, extra notes) is ignored, so you
can freely annotate these files by hand without breaking anything.

## ⚠️ Important: these boxes are not "ground truth"

The `.md` files are generated from **real, already-computed provisional
pseudo-boxes** — heuristic, mask-derived "candidate damage" regions from
`runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/`. They
are:

- **not** organizer-provided ground truth,
- **not** expert-reviewed,
- explained in full in `docs/planning/R4_PSEUDO_BOX_CHECKPOINT.md`.

Please don't treat anything drawn or computed by this tutorial as a
validated physical-damage measurement. It's here to teach how RT-DETR
works, using real (not toy/synthetic) images so the lesson feels
concrete.

Likewise, the model itself is the **stock, COCO-pretrained baseline**
(`rtdetr-l.pt`) — it has never seen a gear tooth and was never fine-tuned
on this data. Its raw guesses will use everyday COCO object names, and
will very likely **not** line up with the green "damage_candidate"
boxes. That mismatch is expected, and is itself part of the lesson: it's
exactly why the real, governed pipeline
(`scripts/train_rtdetr_detector.py`) has to fine-tune RT-DETR on labeled
data before it becomes useful for this task.

## How to run it

```bash
cd tutorials/rtdetr_storybook

# 1. Install the (only) dependency — it pulls in torch, pillow, numpy,
#    and matplotlib automatically.
pip install ultralytics

# 2. Build a small, real demo dataset (read-only copy of 6 real images +
#    their .md target files) from the pinned pseudo-box run.
python make_demo_dataset.py

# 3. Run the storybook! First run downloads the ~65 MB pretrained
#    checkpoint from Ultralytics, so you need internet access once.
python rtdetr_storybook.py
```

Look inside `outputs/<image_name>/` afterwards for:

- `step1_eyes.png` — original photo next to an "activation energy" map
  from an early backbone layer (edges/colors/textures).
- `step2_brain.png` — same idea, but after the Transformer encoder has
  let distant patches talk to each other.
- `step4_final_drawing.png` — the photo with green (answer key) and red
  (model guess) boxes drawn on top.

Console output narrates all four steps as they happen, including the
real tensor shapes captured along the way (how many "glasses" the Eyes
used, how many detectives the Finder sent out, how many survived).

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
python make_demo_dataset.py --output-dir my_demo # pick your own demo folder
```

## Files in this folder

| File | What it does |
|---|---|
| `make_demo_dataset.py` | Read-only: copies a handful of real PHM images + writes `.md` target files. Never modifies the source run. |
| `rtdetr_storybook.py` | The main event: custom `.md` parser, model loading, hook-based intermediate visualization, final drawing. |
| `demo_data/` | Generated by `make_demo_dataset.py` (git-ignored-worthy scratch output; not checked in as thesis evidence). |
| `outputs/` | Generated by `rtdetr_storybook.py`. |

## If something breaks

- **`ModuleNotFoundError` / "needs a few extra libraries"**: run
  `pip install ultralytics` — the script checks for this itself and
  prints exactly this fix instead of crashing.
- **No internet on first run**: the first `RTDETR("rtdetr-l.pt")` call
  needs to download the checkpoint once; after that it's cached locally
  by Ultralytics.
- **A "could not find a layer for '...'" note**: different Ultralytics
  versions occasionally rename internal modules. The script looks up
  layers by *class name* (e.g. any module whose class name contains
  `"AIFI"`) specifically so it keeps working across versions, but if a
  panel gets skipped, that's why — the rest of the story still runs.
