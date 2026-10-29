#!/usr/bin/env python3
"""Export existing evidence; never decode videos, fit models, or edit inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import re
import struct
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

CASES = [f"B{i:02d}" for i in range(1, 21)]
CAMERAS = ["cam_high", "cam_left_wrist", "cam_right_wrist"]
REPORTS = [
    "NATIVE_LABEL_AUDIT.md", "MODALITY_AND_ALIGNMENT_AUDIT.md",
    "GROUP_INDEPENDENCE_AUDIT.md", "VISUAL_OBSERVABILITY_REVIEW.md",
    "SECONDARY_CANDIDATE_AUDIT.md", "FINAL_RESEARCH_DECISION.md",
    "README.md", "RESEARCHER_HANDOFF.md",
]
PNG_STRIP = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def neutral_image(data, suffix):
    """Losslessly remove optional identity/time/comment metadata, preserving pixels."""
    if suffix == ".png":
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        out = bytearray(data[:8])
        offset = 8
        while offset < len(data):
            length = struct.unpack(">I", data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            end = offset + length + 12
            assert end <= len(data)
            if kind not in PNG_STRIP:
                out.extend(data[offset:end])
            offset = end
        assert offset == len(data)
        result = bytes(out)
    elif suffix == ".jpg":
        assert data[:2] == b"\xff\xd8"
        out = bytearray(data[:2])
        offset = 2
        while offset < len(data):
            assert data[offset] == 255
            marker = data[offset + 1]
            if marker == 0xDA:  # Preserve the complete compressed scan verbatim.
                out.extend(data[offset:])
                break
            length = struct.unpack(">H", data[offset + 2:offset + 4])[0]
            end = offset + length + 2
            if not (0xE1 <= marker <= 0xEF or marker == 0xFE):
                out.extend(data[offset:end])
            offset = end
        result = bytes(out)
    else:
        raise AssertionError(suffix)
    if result != data:
        with Image.open(io.BytesIO(data)) as before, Image.open(io.BytesIO(result)) as after:
            assert before.mode == after.mode and before.size == after.size
            assert sha(before.tobytes()) == sha(after.tobytes()), "Image pixels changed"
    return result


def create_zip(tree, dest):
    with zipfile.ZipFile(dest, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(tree.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(path.relative_to(tree).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=6)
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
    return {"path": dest.name, "bytes": dest.stat().st_size, "sha256": file_sha(dest)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--attempt", default="01")
    args = parser.parse_args()
    source = args.source.resolve()
    output = Path(__file__).resolve().parent
    gallery = source / "MATCHED_EXAMPLE_GALLERY"
    assert re.fullmatch(r"[0-9]{2}", args.attempt)
    staging = output / ("staging_attempt_" + args.attempt)
    staging.mkdir(exist_ok=False)
    blind = staging / "blinded"
    docs = staging / "research_reports"
    key = staging / "unblinding"
    for directory in (blind, docs, key):
        directory.mkdir()

    # Verify every pre-existing registered evidence file before reading exports.
    previous_manifest = json.loads((source / "OUTPUT_MANIFEST.json").read_text())
    protected = {}
    for row in previous_manifest:
        path = source / row["path"]
        assert path.stat().st_size == row["bytes"], row["path"]
        digest = file_sha(path)
        assert digest == row["sha256"], row["path"]
        protected[row["path"]] = digest
    protected["OUTPUT_MANIFEST.json"] = file_sha(source / "OUTPUT_MANIFEST.json")
    dump(output / ("source_evidence_before_attempt_" + args.attempt + ".json"), protected)

    manifests = {blind: [], docs: [], key: []}

    def put(tree, relative, data, original=None, transformation="generated package guidance"):
        dest = tree / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        assert not dest.exists()
        dest.write_bytes(data)
        original_rel = ""
        original_hash = ""
        if original is not None:
            original_rel = original.relative_to(gallery if tree == blind else source).as_posix()
            original_hash = file_sha(original)
        manifests[tree].append({
            "path": relative, "bytes": len(data), "sha256": sha(data),
            "source_asset": original_rel, "source_sha256": original_hash,
            "transformation": transformation,
        })

    # Strict allowlist: source logs, annotations, analyst judgments, keys and raw
    # recordings cannot enter the blinded archive through recursive copying.
    index_source = gallery / "index.html"
    html = index_source.read_text()
    html, n = re.subn(r'<p>After recording judgments, open .*?</p>', '', html)
    assert n == 1
    html = html.replace(
        "Review independently before opening the source key. These pages contain no outcome labels or native failure keyframes.",
        "Record independent observations using the blank review form before consulting any separate documentation.",
    )
    html = html.replace("</body>", '<p><a href="HUMAN_REVIEW_FORM.csv">Blank review form</a> · <a href="README.md">Offline instructions</a> · <a href="FILE_MANIFEST.csv">File hashes</a> · <a href="FRAME_TIMESTAMPS.csv">Frame timestamps</a></p></body>')
    put(blind, "index.html", html.encode(), index_source, "removed key link; added local review resources")

    timing_rows = []
    for bid in CASES:
        page_source = gallery / f"{bid}.html"
        html = page_source.read_text()
        html, n = re.subn(
            r'<p>Outcome, failure category, pair and original episode ID are withheld\..*?</p>',
            '<p>Sixteen uniformly spaced positions span this complete recording. Examine the physical execution independently of source annotations.</p>',
            html,
        )
        assert n == 1
        html = html.replace("enlarged for both classes", "enlarged consistently for every case")
        selected = json.JSONDecoder().raw_decode(html.split("const frames=", 1)[1])[0]
        assert len(selected) == 16
        assert len({frame["index"] for frame in selected}) == 16
        assert all(a["time"] < b["time"] for a, b in zip(selected, selected[1:]))
        put(blind, f"{bid}.html", html.encode(), page_source, "neutralized introductory wording; retained all frame/timing/plot logic")
        for name in ("BLINDED_OVERVIEW.jpg", "sensor_timeline.png"):
            src = gallery / "assets" / bid / name
            data = src.read_bytes()
            clean = neutral_image(data, src.suffix)
            put(blind, f"assets/{bid}/{name}", clean, src,
                "optional metadata stripped losslessly; pixels verified identical" if clean != data else "byte-identical")
        for camera in CAMERAS:
            for name in [f"frame_{i:02d}.png" for i in range(16)] + ["full_sequence.jpg", "region_sequence.jpg"]:
                src = gallery / "assets" / bid / camera / name
                data = src.read_bytes()
                clean = neutral_image(data, src.suffix)
                put(blind, f"assets/{bid}/{camera}/{name}", clean, src,
                    "optional metadata stripped losslessly; pixels verified identical" if clean != data else "byte-identical")
            for i, frame in enumerate(selected):
                timing_rows.append({"blind_id": bid, "camera": camera, "selected_position": i + 1,
                                    "source_frame_index": frame["index"], "time_seconds": frame["time"],
                                    "image": f"assets/{bid}/{camera}/frame_{i:02d}.png"})
    table = io.StringIO(newline="")
    writer = csv.DictWriter(table, fieldnames=list(timing_rows[0]))
    writer.writeheader()
    writer.writerows(timing_rows)
    put(blind, "FRAME_TIMESTAMPS.csv", table.getvalue().encode(), transformation="only neutral case IDs and frame timing copied from existing case HTML")
    review = gallery / "HUMAN_REVIEW_FORM.csv"
    rows = list(csv.DictReader(io.StringIO(review.read_text())))
    assert [r["blind_id"] for r in rows] == CASES
    assert all(not value for row in rows for name, value in row.items() if name != "blind_id")
    put(blind, review.name, review.read_bytes(), review, "byte-identical blank form")
    put(blind, "README.md", b"""# Independent blinded visual review

Unzip the complete archive into a new folder and open **index.html** in a browser.
Keep the assets/ folder beside the HTML files. No server, network, login, Python,
or original dataset directory is required. JavaScript must be enabled for the slider.
For ChatGPT file review, inspect the image files directly if HTML is not executed.

There are 20 neutrally identified recordings, B01-B20. Each includes 16 uniformly
spaced temporal positions from all three RGB cameras (960 full-resolution PNGs).
Each original selected image is 640 x 480 pixels: click the browser image's
Open image action to view its full size. No original videos are bundled.

Each case page has three complete camera views and three enlarged central views.
The fixed region is x=20-80%, y=20-80%, enlarged equally for every recording.
This crop can miss relevant objects; always inspect the complete camera views.
Existing full_sequence.jpg and region_sequence.jpg sheets provide all 16 positions
without JavaScript. BLINDED_OVERVIEW.jpg is a compact three-camera overview.

sensor_timeline.png plots measured position, velocity, and effort versus recording
time. Grey vertical guides mark selected frame times; FRAME_TIMESTAMPS.csv gives
the corresponding indices/times for each camera. Position/velocity/effort channels
0-6 are the left six joints plus gripper, and 7-13 the right six joints plus
gripper. Native calibration and units are unverified. These are converted shared
frame-clock timings, not independently established hardware clock synchronization.
Displayed streams include constant/placeholder channels; do not infer observability
or sensor quality from a missing motion signal alone.

Save a copy of HUMAN_REVIEW_FORM.csv and fill in each row before requesting any
separate research documentation. Suggested visibility entries: clear / partial /
occluded / uncertain. Describe concrete physical observations and timing in notes;
record apparent task completion and confidence without assuming every relevant
event is visible. Blank judgments are deliberately provided; no analyst decisions
are included. The task sentence describes the intended action, not its outcome.

FILE_MANIFEST.csv lists every payload except itself, its byte count, exported
SHA-256, neutral source asset path and source SHA-256 when an asset was copied.
Source hashes refer to existing gallery assets, not original recording identities.
Generated guidance/timing files have blank source fields. Text exports remove the
key link and neutralize introductory wording. Optional image identity/time/comment
metadata is removed without re-encoding pixels; all other image bytes are retained.
ZIP member timestamps and permissions are uniform. No frame extraction was rerun.

This archive contains no native per-recording outcomes, annotation categories,
pair assignments, original recording IDs, decoding logs, or source identity key.
Do not open separate research documentation until your independent observations
are saved. Do not infer a category from the neutral case ID or file ordering.
""")

    # Reports are copied exactly; they intentionally belong outside blind review.
    for name in REPORTS:
        src = source / name
        put(docs, name, src.read_bytes(), src, "byte-identical original report")
    src = source / "SOURCE_PROVENANCE.json"
    put(docs, src.name, src.read_bytes(), src, "byte-identical original provenance")
    # Compact factual audit records make the reports independently inspectable.
    supplementary = [
        "native_label_summary.json", "class_counts_by_task.csv", "class_counts_by_source_task.csv",
        "original_native_annotation_comparison.json", "original_publisher_identity_validation.json",
        "pilot_numerical_audit.json", "pilot_media_audit.json", "group_and_quality_screen.json",
        "provisional_cohort_screen.json", "constant_state_origin_audit.json",
        "original_hdf5_conversion_audit.json", "post_unblinding_observability.json",
        "secondary_bounded_native_audit.json", "validation.json",
    ]
    for name in supplementary:
        src = source / "checks" / name
        put(docs, f"checks/{name}", src.read_bytes(), src, "byte-identical supporting audit record; not blinded")
    for name in ("pilot_policy.json", "verification_config.json"):
        src = source / "config" / name
        put(docs, f"config/{name}", src.read_bytes(), src, "byte-identical audit configuration; not blinded")
    put(docs, "OPEN_AFTER_BLIND_REVIEW.md", b"""# Research documentation: open after independent review

This archive contains outcome information, cohort counts, source identities and
previous analyst observations. Keep it separate from a blinded visual reviewer.

The five audit reports are NATIVE_LABEL_AUDIT.md,
MODALITY_AND_ALIGNMENT_AUDIT.md, GROUP_INDEPENDENCE_AUDIT.md,
VISUAL_OBSERVABILITY_REVIEW.md, and SECONDARY_CANDIDATE_AUDIT.md.
FINAL_RESEARCH_DECISION.md contains the decision. Original README.md,
RESEARCHER_HANDOFF.md, SOURCE_PROVENANCE.json, compact checks/, config/ and
FILE_MANIFEST.csv support independent document review. Original files are
byte-identical; this note and the file manifest are export additions.

The original reports use the original verification directory as their link root.
To follow their gallery links, extract VIFAILBACK_BLINDED_REVIEW.zip into a
MATCHED_EXAMPLE_GALLERY/ subdirectory beside these reports. This is optional:
all five reports and the decision can be read without the images or network.
Some narrative paths refer to full original evidence/code not bundled here;
downloaded raw recordings, full source trees and credentials are not included.
The separate VIFAILBACK_UNBLINDING.zip preserves the unchanged source key and
initial analyst screen; it is never nested in the visual-review archive.
""")

    for name in ("SOURCE_LABEL_KEY.json", "index.html"):
        src = gallery / "UNBLINDING" / name
        put(key, f"UNBLINDING/{name}", src.read_bytes(), src, "byte-identical separate source key")
    src = gallery / "INITIAL_BLINDED_SCREEN.json"
    put(key, src.name, src.read_bytes(), src, "byte-identical prior analyst screen; not a blank independent review")
    put(key, "README.md", b"""# Separate unblinding material

Do not give this archive to an independent blinded reviewer.
The unchanged source identity/outcome key is UNBLINDING/index.html and
UNBLINDING/SOURCE_LABEL_KEY.json. INITIAL_BLINDED_SCREEN.json preserves the
previous analyst screen; it is not an independent human review.
The original evidence remains unchanged. This extra archive preserves separation
of the key from both the visual-review ZIP and its file manifest.
""")

    for tree, entries in manifests.items():
        table = io.StringIO(newline="")
        writer = csv.DictWriter(table, fieldnames=list(entries[0]))
        writer.writeheader()
        writer.writerows(sorted(entries, key=lambda row: row["path"]))
        (tree / "FILE_MANIFEST.csv").write_text(table.getvalue(), newline="")
    packages = [
        create_zip(blind, output / "VIFAILBACK_BLINDED_REVIEW.zip"),
        create_zip(docs, output / "VIFAILBACK_RESEARCH_REPORTS.zip"),
        create_zip(key, output / "VIFAILBACK_UNBLINDING.zip"),
    ]
    for relative, expected in protected.items():
        assert file_sha(source / relative) == expected, relative
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": "ma_thesis_env/bin/python -B " + str(Path(__file__).resolve().relative_to(Path.cwd())) + " --source " + str(args.source) + " --attempt " + args.attempt,
        "staging_directory": staging.name,
        "source": str(args.source), "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "tracked_status": subprocess.check_output(["git", "status", "--short", "--untracked-files=no"], text=True),
        "python": sys.version, "platform": platform.platform(), "pillow": Image.__version__,
        "registered_source_files_verified_unchanged": len(protected),
        "source_videos_read_or_reextracted": False, "training_run": False,
        "staged_or_committed": False, "gallery_cases": len(CASES),
        "selected_positions": 320, "full_resolution_frames": 960,
        "full_view_sheets": 60, "enlarged_view_sheets": 60, "sensor_plots": 20,
        "overview_sheets": 20, "image_count": 1120,
        "image_files_metadata_sanitized": sum("metadata stripped" in row["transformation"] for row in manifests[blind]),
        "zip_metadata": "uniform 1980-01-01 timestamps; mode 0644; no comments or extra fields",
        "exclusions": ["all source logs", "raw media", "native annotations", "source identities", "analyst observations", "pair assignments", "unblinding key"],
        "packages": packages,
        "warnings": ["Documentation and unblinding ZIPs disclose outcomes; withhold them until blind review is complete.",
                     "16 positions can miss transient events; crops can miss objects; native signal units are unverified."],
    }
    dump(output / "EXPORT_PROVENANCE.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
