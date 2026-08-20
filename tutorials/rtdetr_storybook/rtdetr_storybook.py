#!/usr/bin/env python3
"""RT-DETR Storybook: a beginner-friendly walk through a real object detector.

============================================================================
 WHAT THIS SCRIPT IS (please read before running)
============================================================================
This is a TUTORIAL, not part of the governed PHM 2026 thesis pipeline
(see AGENTS.md / docs/planning/PROJECT_STATE.md). It lives outside
src/pi_multimodal_ad, scripts/, configs/, and runs/ on purpose, so nothing
here is mistaken for thesis evidence or governed provenance.

It does inference only — it loads a stock, COCO-pretrained RT-DETR model
and never updates a single weight. No training happens in this file.

It works on REAL PHM 2026 gear-tooth photos. Two loaders can supply them:

  - make_raw_demo_dataset.py (preferred): opens the RAW, immutable
    challenge archives directly (gtc-data-experiment/photos/...) and
    derives provisional targets by re-running the real, pinned
    phm2026_image_damage_v2 pipeline.
  - make_demo_dataset.py (fallback, no raw-data access needed): copies
    already-cached images + targets out of a prior pseudo-box run under
    runs/phm2026_rtdetr_pseudo_boxes/<run-id>/.

Either way, the resulting boxes are heuristic, mask-derived candidates —
NOT organizer ground truth and NOT expert-reviewed. See docs/planning/
T2_TARGET_FORMULATION_DECISION.md and docs/planning/
R4_PSEUDO_BOX_CHECKPOINT.md.

Because the model is the plain pretrained baseline (it has never seen a
gear tooth), its raw guesses will use COCO's everyday object vocabulary
(things like "car" or "person"), not "damage_candidate". That mismatch is
expected and is part of the lesson: it shows why the real pipeline
(scripts/train_rtdetr_detector.py) has to fine-tune the model before it is
useful for this task.

============================================================================
 THE STORY, IN FIVE STEPS
============================================================================
Think of the model as a small robot detective looking at a photo:

  Step 0 - Getting the photo ready (preprocessing + target definition):
    Before any detector runs, we have to decide what we're even looking
    for. A raw PHM photo has no label at all. This step crops a fixed
    "visible flank" region, evens out the lighting, and highlights dark
    streaky patches — turning "a photo" into "a provisional measurement
    of candidate damage". This step only runs if you built your demo data
    with make_raw_demo_dataset.py and have opencv/pandas/pyyaml
    installed; otherwise it's skipped with a note (the .md file already
    carries the same result either way).

  Step 1 - The Eyes (backbone):
    The robot puts on several pairs of "magic glasses". Each pair is
    tuned to notice something different — edges, colors, little textures.
    None of them understands the *whole* picture yet; they just report
    "I see a stripe here" or "I see a bright blob there".

  Step 2 - The Brain (hybrid encoder / AIFI):
    The robot's brain lets far-apart puzzle pieces of the picture "raise
    their hands" and talk to each other, even if they are on opposite
    sides of the photo. This is what a Transformer's *attention* does.
    RT-DETR is clever about cost: the brain only does this expensive
    chatting on the most zoomed-out (smallest) feature map, then mixes
    the result back in with the other zoom levels.

  Step 3 - The Finder (decoder + object queries):
    The robot sends out a fixed number of little detectives (the
    "queries" — often 300 of them). Each detective independently guesses
    "I think something interesting is *here*, and I think it's a
    <class>". Most guesses are wrong or duplicates; only the confident,
    non-overlapping ones survive.

  Step 4 - The Final Drawing:
    We draw the survivors as boxes on the photo: GREEN boxes are the
    "official" provisional targets from the .md file, RED boxes are the
    model's own raw guesses.

============================================================================
 SETUP
============================================================================
    pip install ultralytics          # pulls in torch, pillow, numpy,
                                      # matplotlib, opencv automatically
    python make_demo_dataset.py      # creates demo_data/ from real PHM data
    python rtdetr_storybook.py       # runs this storybook

First run downloads the small pretrained "rtdetr-l.pt" checkpoint
(~65 MB) from Ultralytics' servers, so you need internet access once.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import sys
from typing import Any

# ----------------------------------------------------------------------
# Dependency check
# ----------------------------------------------------------------------
# We import the heavy, optional dependencies lazily and report a friendly
# one-line fix instead of a scary traceback if something is missing. This
# keeps the *parsing* logic below usable (and testable) even on a machine
# that doesn't have torch/ultralytics installed yet.
# ----------------------------------------------------------------------

_MISSING_DEPENDENCIES: list[str] = []
try:
    import numpy as np
except ImportError:
    _MISSING_DEPENDENCIES.append("numpy")
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    _MISSING_DEPENDENCIES.append("pillow")
try:
    import matplotlib.pyplot as plt
except ImportError:
    _MISSING_DEPENDENCIES.append("matplotlib")
try:
    import torch
except ImportError:
    _MISSING_DEPENDENCIES.append("torch")
try:
    from ultralytics import RTDETR
except ImportError:
    _MISSING_DEPENDENCIES.append("ultralytics")

# Step 0 (preprocessing/target-definition) is an optional extra: it reuses
# the real, pinned phm2026_image_damage_v2 pipeline via the sibling
# make_raw_demo_dataset.py module, which needs opencv-python/pandas/pyyaml
# on top of everything above. Importing that module never raises — it
# guards its own dependencies the same way this file does — so we can
# simply check its _MISSING_DEPENDENCIES list to decide whether Step 0 can
# run, and skip it gracefully otherwise.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import make_raw_demo_dataset as raw_loader

    _PREPROCESSING_AVAILABLE = not raw_loader._MISSING_DEPENDENCIES
except ImportError:
    raw_loader = None
    _PREPROCESSING_AVAILABLE = False


# ============================================================================
# PART A — The custom .md target parser
#
# This is the "bridge" between plain image folders and this tutorial's
# Markdown-based label format. It only needs the Python standard library,
# so it works even without torch/ultralytics installed.
# ============================================================================


@dataclass(frozen=True, slots=True)
class Box:
    """One target bounding box, in pixel coordinates (x_min, y_min, x_max, y_max)."""

    class_name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass(frozen=True, slots=True)
class TargetSheet:
    """Everything we parsed out of one image's .md sidecar file."""

    image_width: int | None
    image_height: int | None
    status: str | None
    boxes: tuple[Box, ...] = field(default_factory=tuple)


# Matches a Markdown table data row like:
#   | damage_candidate | 424.0 | 217.0 | 450.0 | 225.0 |
# Deliberately simple and explicit rather than a generic Markdown-table
# parser: this tutorial defines its own small, documented format instead
# of depending on a heavier Markdown library.
_TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*(?P<class_name>[^|]+?)\s*\|\s*(?P<x_min>-?[\d.]+)\s*\|\s*"
    r"(?P<y_min>-?[\d.]+)\s*\|\s*(?P<x_max>-?[\d.]+)\s*\|\s*(?P<y_max>-?[\d.]+)\s*\|\s*$"
)
_IMAGE_SIZE_PATTERN = re.compile(
    r"-\s*Image size:\s*(?P<width>\d+)\s*x\s*(?P<height>\d+)", re.IGNORECASE
)
_STATUS_PATTERN = re.compile(r"-\s*Status:\s*(?P<status>.+)", re.IGNORECASE)


def parse_md_targets(md_path: Path) -> TargetSheet:
    """Read a .md sidecar file and return its image size, status, and boxes.

    This is the "custom parser function" the whole tutorial is built
    around: it scans a Markdown file line by line looking for three
    things — a "- Image size: W x H" line, a "- Status: ..." line, and a
    small table of bounding boxes under a "## Boxes" heading. Anything
    else in the file (headings, prose, extra notes) is simply ignored,
    so a human can freely add commentary to these files without breaking
    the parser.
    """
    width: int | None = None
    height: int | None = None
    status: str | None = None
    boxes: list[Box] = []

    for raw_line in md_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        size_match = _IMAGE_SIZE_PATTERN.match(line)
        if size_match:
            width = int(size_match.group("width"))
            height = int(size_match.group("height"))
            continue

        status_match = _STATUS_PATTERN.match(line)
        if status_match:
            status = status_match.group("status").strip()
            continue

        row_match = _TABLE_ROW_PATTERN.match(line)
        if row_match:
            class_name = row_match.group("class_name").strip()
            # Skip the header row ("class | x_min | ...") and the
            # "|---|---|---|---|---|" separator row that every Markdown
            # table needs — neither one is a real box.
            if class_name.lower() == "class" or set(class_name) <= {"-"}:
                continue
            boxes.append(
                Box(
                    class_name=class_name,
                    x_min=float(row_match.group("x_min")),
                    y_min=float(row_match.group("y_min")),
                    x_max=float(row_match.group("x_max")),
                    y_max=float(row_match.group("y_max")),
                )
            )

    return TargetSheet(
        image_width=width, image_height=height, status=status, boxes=tuple(boxes)
    )


def pair_images_with_targets(demo_dir: Path) -> list[tuple[Path, Path]]:
    """Find every image in demo_dir that has a matching same-stem .md file."""
    pairs: list[tuple[Path, Path]] = []
    for image_path in sorted(demo_dir.glob("*.jpg")) + sorted(demo_dir.glob("*.png")):
        md_path = image_path.with_suffix(".md")
        if md_path.exists():
            pairs.append((image_path, md_path))
        else:
            print(f"  [skip] no matching .md file for {image_path.name}")
    return pairs


# ============================================================================
# PART B — Peeking inside the model with forward hooks
#
# A "forward hook" is a small function PyTorch calls automatically every
# time a chosen layer finishes its work, handing us that layer's output
# tensor without changing anything about how the model runs. We use this
# to "listen in" on the Eyes, Brain, and Finder without having to rewrite
# any of RT-DETR's own code.
# ============================================================================


def _first_tensor(value: Any):
    """Dig into a (possibly nested) tuple/list and return the first tensor found."""
    if isinstance(value, torch.Tensor):
        return value
    if isinstance(value, (list, tuple)):
        for item in value:
            found = _first_tensor(item)
            if found is not None:
                return found
    return None


def _find_first_module(model: "torch.nn.Module", name_contains: tuple[str, ...]):
    """Return the first submodule (in registration order) whose class name
    contains any of the given substrings, or None if there isn't one.

    We match by class name rather than by hard-coded layer index because
    exact layer indices can shift between Ultralytics versions, while the
    architectural building blocks (an "AIFI" encoder layer, an
    "RTDETRDecoder" head, an early "Conv"/"HGStem" backbone layer) are
    stable RT-DETR concepts.
    """
    for _, module in model.named_modules():
        class_name = type(module).__name__
        if any(fragment in class_name for fragment in name_contains):
            return module
    return None


class StorybookHooks:
    """Registers hooks on the Eyes, Brain, and Finder, and stores what they saw."""

    def __init__(self, model: "torch.nn.Module") -> None:
        self.captures: dict[str, Any] = {}
        self._handles = []

        targets = {
            "eyes": ("Conv", "HGStem", "Stem"),  # an early backbone layer
            "brain": ("AIFI",),  # RT-DETR's transformer encoder layer
            "finder": ("RTDETRDecoder",),  # the query-based decoder head
        }
        self.found_modules: dict[str, str | None] = {}
        for label, name_fragments in targets.items():
            module = _find_first_module(model, name_fragments)
            if module is None:
                self.found_modules[label] = None
                continue
            self.found_modules[label] = type(module).__name__
            self._handles.append(
                module.register_forward_hook(self._make_hook(label))
            )

    def _make_hook(self, label: str):
        def hook(_module, inputs, output):
            self.captures[label] = {
                "input_tensor": _first_tensor(inputs),
                "output_tensor": _first_tensor(output),
            }

        return hook

    def remove(self) -> None:
        for handle in self._handles:
            handle.remove()


# ============================================================================
# PART C — Turning raw tensors into friendly pictures
# ============================================================================


def _activation_heatmap(tensor: "torch.Tensor", target_size: tuple[int, int]) -> "np.ndarray":
    """Collapse a (1, C, H, W) feature map into a 0-255 grayscale heatmap.

    NOTE ON HONESTY: this is an *activation-magnitude* heatmap (how loudly,
    on average, the channels are firing at each spot), not literal
    Transformer attention weights. Extracting the exact attention-weight
    matrix would require patching PyTorch's MultiheadAttention internals,
    which is fragile across library versions. The activation map still
    tells the same beginner-friendly story — "here is where this stage of
    the network is paying the most energy/attention" — so we use it for
    both the Eyes and the Brain panels, and we say so on-screen.
    """
    with torch.no_grad():
        # Average the absolute activation across channels -> one (H, W) map.
        single_image = tensor[0] if tensor.dim() == 4 else tensor
        heat = single_image.abs().mean(dim=0).cpu().numpy()
    heat = heat - heat.min()
    denominator = heat.max() if heat.max() > 0 else 1.0
    heat = (heat / denominator * 255).astype("uint8")
    heat_image = Image.fromarray(heat).resize(target_size, Image.Resampling.BILINEAR)
    return np.asarray(heat_image)


def _draw_boxes(image: "Image.Image", boxes: list[Box], color, label_prefix: str):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for box in boxes:
        draw.rectangle(
            (box.x_min, box.y_min, box.x_max, box.y_max), outline=color, width=4
        )
        draw.text((box.x_min + 2, max(0, box.y_min - 12)), label_prefix, fill=color, font=font)
    return image


# ============================================================================
# PART D — Running the whole storybook on one image
# ============================================================================


def _save_preprocessing_panel(
    original: "Image.Image",
    mask: "np.ndarray",
    roi_xyxy: tuple[int, int, int, int],
    *,
    metrics: dict,
    path: Path,
) -> None:
    """Show the fixed ROI on the full photo, and the final candidate mask
    (red) painted on top of just that ROI crop."""
    x0, y0, x1, y1 = roi_xyxy
    roi_crop = original.crop((x0, y0, x1, y1))
    mask_crop = mask[y0:y1, x0:x1]

    overlay = np.asarray(roi_crop).copy()
    red_tint = np.zeros_like(overlay)
    red_tint[..., 0] = 255
    selected = mask_crop.astype(bool)
    overlay[selected] = (0.45 * overlay[selected] + 0.55 * red_tint[selected]).astype(
        "uint8"
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].imshow(original)
    axes[0].add_patch(
        plt.Rectangle(
            (x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor="lime", linewidth=2
        )
    )
    axes[0].set_title("Full photo + fixed visible-flank ROI (green)")
    axes[0].axis("off")
    axes[1].imshow(overlay)
    axes[1].set_title(
        f"ROI crop, red = surviving candidate pixels "
        f"({metrics['damage_candidate_area_pct']:.3f}% of ROI)"
    )
    axes[1].axis("off")
    fig.suptitle("Step 0: Preprocessing + provisional target definition")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_storybook_on_image(
    *,
    image_path: Path,
    md_path: Path,
    model: "RTDETR",
    device: str,
    confidence_threshold: float,
    max_boxes_drawn: int,
    output_dir: Path,
    preprocessing_options: "ImageDamageOptions | None" = None,
) -> None:
    stem = image_path.stem
    image_output_dir = output_dir / stem
    image_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 72}\nOpening the picture book to: {image_path.name}\n{'=' * 72}")

    # --- Read the .md sidecar: our "answer key" for this picture. ---
    targets = parse_md_targets(md_path)
    print(f"Answer key says: {targets.status}")
    print(
        f"It lists {len(targets.boxes)} provisional 'damage_candidate' box(es) "
        f"on a {targets.image_width}x{targets.image_height} photo."
    )

    with Image.open(image_path) as source:
        original_image = source.convert("RGB")

    # ---------------- Step 0: Preprocessing + target definition ----------------
    print("\nStep 0 - Getting the photo ready: a raw photo has no label at all, "
          "so before any detector runs we crop a fixed region, even out the "
          "lighting, and highlight dark streaky patches...")
    if preprocessing_options is None or not _PREPROCESSING_AVAILABLE:
        print("  (skipped: needs opencv-python/pandas/pyyaml — "
              "pip install -r ../../requirements.txt to see this step live. "
              "The .md file already carries the same result either way.)")
    else:
        rgb = np.asarray(original_image, dtype="uint8")
        metrics, mask, roi_xyxy = raw_loader.measure_damage_candidate(
            rgb, preprocessing_options
        )
        print(f"  Fixed visible-flank ROI (a constant box, not learned): "
              f"{preprocessing_options.roi_normalized_xyxy} of the image.")
        print(f"  After CLAHE contrast normalization, background subtraction, "
              f"a robust z-score threshold (z >= "
              f"{preprocessing_options.residual_z_threshold}), and keeping only "
              f"wide 'horizontal' blobs: {metrics['component_count']} candidate "
              f"patch(es) survived, covering "
              f"{metrics['damage_candidate_area_pct']:.3f}% of the ROI.")
        print(f"  This percentage IS the provisional target — see "
              "docs/planning/T2_TARGET_FORMULATION_DECISION.md for exactly what "
              "it does and doesn't mean yet (status: "
              f"{metrics['measurement_status']}).")
        _save_preprocessing_panel(
            original_image,
            mask,
            roi_xyxy,
            metrics=metrics,
            path=image_output_dir / "step0_preprocessing.png",
        )

    # --- Listen in on the Eyes, Brain, and Finder while the model looks. ---
    hooks = StorybookHooks(model.model)
    for label, class_name in hooks.found_modules.items():
        if class_name is None:
            print(f"  [note] could not find a layer for '{label}' in this "
                  "model version; that panel will be skipped.")

    results = model.predict(
        source=str(image_path),
        device=device,
        conf=confidence_threshold,
        max_det=300,
        verbose=False,
    )
    hooks.remove()
    result = results[0]

    # ---------------- Step 1: The Eyes ----------------
    print("\nStep 1 - The Eyes (backbone): looking for edges, colors, textures...")
    eyes = hooks.captures.get("eyes")
    if eyes and eyes["output_tensor"] is not None:
        eyes_tensor = eyes["output_tensor"]
        print(f"  The Eyes' first report is a stack of {eyes_tensor.shape[1]} "
              f"different 'glasses' (channels), each {eyes_tensor.shape[-2]}x"
              f"{eyes_tensor.shape[-1]} pixels — much smaller than the photo, "
              "because looking that closely at every pixel would be slow.")
        heatmap = _activation_heatmap(eyes_tensor, original_image.size)
        _save_side_by_side(
            original_image,
            heatmap,
            title="Step 1: The Eyes — early activation energy (proxy, not literal attention)",
            path=image_output_dir / "step1_eyes.png",
        )
    else:
        print("  (skipped: no matching backbone layer found)")

    # ---------------- Step 2: The Brain ----------------
    print("\nStep 2 - The Brain (AIFI hybrid encoder): letting far-apart puzzle "
          "pieces talk to each other...")
    brain = hooks.captures.get("brain")
    if brain and brain["output_tensor"] is not None:
        brain_tensor = brain["output_tensor"]
        print(f"  The Brain only does this expensive chatting on the smallest, "
              f"most zoomed-out feature map (shape {tuple(brain_tensor.shape)}), "
              "then RT-DETR mixes the result back in with the other zoom levels "
              "before handing everything to the Finder.")
        heatmap = _activation_heatmap(brain_tensor, original_image.size)
        _save_side_by_side(
            original_image,
            heatmap,
            title="Step 2: The Brain — post-attention activation energy (proxy)",
            path=image_output_dir / "step2_brain.png",
        )
    else:
        print("  (skipped: no AIFI encoder layer found)")

    # ---------------- Step 3: The Finder ----------------
    print("\nStep 3 - The Finder (decoder + object queries): sending out little "
          "detectives to guess where things are...")
    finder = hooks.captures.get("finder")
    if finder and finder["output_tensor"] is not None:
        finder_tensor = finder["output_tensor"]
        if finder_tensor.dim() >= 2:
            print(f"  The Finder's raw output has shape {tuple(finder_tensor.shape)}. "
                  f"Its query dimension ({finder_tensor.shape[1]}) is how many "
                  "independent guesses ('detectives') the decoder sent out for "
                  "this photo.")
    else:
        print("  (skipped: no RTDETRDecoder layer found)")
    kept = 0 if result.boxes is None else len(result.boxes)
    print(f"  After keeping only confident, non-duplicate guesses "
          f"(confidence >= {confidence_threshold}), {kept} guess(es) survived.")

    # ---------------- Step 4: The Final Drawing ----------------
    print("\nStep 4 - The Final Drawing: green = provisional answer key from the "
          ".md file, red = the model's own raw guess (pretrained on everyday "
          "COCO objects, NOT fine-tuned on gear teeth, so a mismatch here is "
          "expected and is the whole point of this demo).")

    reference_boxes = list(targets.boxes[:max_boxes_drawn])
    omitted_reference = len(targets.boxes) - len(reference_boxes)
    if omitted_reference > 0:
        print(f"  (only drawing the first {max_boxes_drawn} of "
              f"{len(targets.boxes)} answer-key boxes so the picture stays readable)")

    predicted_boxes: list[Box] = []
    if result.boxes is not None:
        names = result.names
        xyxy = result.boxes.xyxy.detach().cpu().numpy()
        classes = result.boxes.cls.detach().cpu().numpy().astype(int)
        for (x_min, y_min, x_max, y_max), class_id in list(
            zip(xyxy, classes, strict=True)
        )[:max_boxes_drawn]:
            predicted_boxes.append(
                Box(names.get(int(class_id), str(class_id)), x_min, y_min, x_max, y_max)
            )

    drawing = original_image.copy()
    _draw_boxes(drawing, reference_boxes, color=(0, 200, 0), label_prefix="target")
    _draw_boxes(drawing, predicted_boxes, color=(230, 30, 30), label_prefix="guess")
    final_path = image_output_dir / "step4_final_drawing.png"
    drawing.save(final_path)
    print(f"  Saved the final drawing to {final_path}")


def _save_side_by_side(
    original: "Image.Image", heatmap: "np.ndarray", *, title: str, path: Path
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(original)
    axes[0].set_title("Original photo")
    axes[0].axis("off")
    axes[1].imshow(heatmap, cmap="magma")
    axes[1].set_title("Activation energy (brighter = more energy)")
    axes[1].axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ============================================================================
# PART E — Command-line entry point
# ============================================================================


def _require_dependencies() -> None:
    if _MISSING_DEPENDENCIES:
        print(
            "This storybook needs a few extra libraries that aren't installed "
            f"yet: {', '.join(_MISSING_DEPENDENCIES)}.\n\n"
            "Install them with:\n\n"
            "    pip install ultralytics\n\n"
            "(that one package pulls in torch, pillow, numpy, and matplotlib "
            "automatically). Then re-run this script.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_demo_dir = Path(__file__).resolve().parent / "raw_demo_data"
    if not default_demo_dir.exists():
        default_demo_dir = Path(__file__).resolve().parent / "demo_data"
    parser.add_argument(
        "--demo-dir",
        type=Path,
        default=default_demo_dir,
        help="Folder of paired image + .md files (default: ./raw_demo_data "
        "if it exists, from make_raw_demo_dataset.py; otherwise "
        "./demo_data from make_demo_dataset.py).",
    )
    parser.add_argument(
        "--target-config",
        type=Path,
        default=None,
        help="Pinned preprocessing/target config for Step 0 (default: "
        "make_raw_demo_dataset.py's own default, "
        "configs/experiments/phm2026_image_target.yaml).",
    )
    parser.add_argument(
        "--no-preprocessing",
        action="store_true",
        help="Skip Step 0 even if opencv/pandas/pyyaml are installed.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="Where to write the step-by-step figures (default: ./outputs).",
    )
    parser.add_argument(
        "--weights",
        default="rtdetr-l.pt",
        help="Ultralytics RT-DETR checkpoint name or path (default: "
        "rtdetr-l.pt, the stock COCO-pretrained baseline; auto-downloaded "
        "on first use).",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device string, e.g. 'cpu' or 'cuda:0' (default: cpu).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold for the model's own guesses in Step 4 "
        "(default: 0.25, Ultralytics' usual default).",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=3,
        help="How many image/.md pairs to walk through (default: 3).",
    )
    parser.add_argument(
        "--max-boxes-drawn",
        type=int,
        default=15,
        help="Cap on boxes drawn per side in the final picture, for "
        "readability (default: 15).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _require_dependencies()

    pairs = pair_images_with_targets(args.demo_dir)
    if not pairs:
        print(
            f"No image/.md pairs found in {args.demo_dir}. Run "
            "make_demo_dataset.py first.",
            file=sys.stderr,
        )
        return 1

    preprocessing_options = None
    if not args.no_preprocessing and _PREPROCESSING_AVAILABLE:
        config_path = args.target_config or raw_loader.TARGET_CONFIG_DEFAULT
        preprocessing_options = raw_loader.load_pinned_image_measurement_options(
            config_path
        )
        print(f"Step 0 preprocessing is available; using pinned config: {config_path}")
    else:
        print("Step 0 preprocessing will be skipped for every image (see notes below).")

    print("Loading the pretrained RT-DETR baseline (this is inference-only; "
          "no training happens in this script)...")
    model = RTDETR(args.weights)

    for image_path, md_path in pairs[: args.max_images]:
        run_storybook_on_image(
            image_path=image_path,
            md_path=md_path,
            model=model,
            device=args.device,
            confidence_threshold=args.conf,
            max_boxes_drawn=args.max_boxes_drawn,
            output_dir=args.output_dir,
            preprocessing_options=preprocessing_options,
        )

    print(f"\nAll done! Look inside {args.output_dir} for the step-by-step pictures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
