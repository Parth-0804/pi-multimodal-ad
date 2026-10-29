#!/usr/bin/env python3
"""Verify ZIP contents, blinding, hashes, and every frame in an offline browser."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent
CASES = [f"B{i:02d}" for i in range(1, 21)]
CAMERAS = ["cam_high", "cam_left_wrist", "cam_right_wrist"]
FORBIDDEN = re.compile(
    r"UNBLINDING|SOURCE_LABEL_KEY|INITIAL_BLINDED_SCREEN|episode_success|"
    r"native_failure_detection|failure_type|avoid_keyframe|correct_keyframe|"
    r"vifailback_flags|raw_data/|episode_\d+|\.hdf5|\.parquet|\.mp4|decode\.log|"
    r"gripper 6d-pose|gripper state|task planning|human intervention|"
    r"post_unblinding|source_hdf5|source_episode|/home/student/",
    re.I,
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)


def main():
    results = {"started_utc": datetime.now(timezone.utc).isoformat(), "errors": []}
    extraction = Path(tempfile.mkdtemp(prefix="vifailback_portable_review_"))
    results["isolated_extraction_directory"] = str(extraction)
    packages = {}
    provenance = json.loads((HERE / "EXPORT_PROVENANCE.json").read_text())
    for info in provenance["packages"]:
        path = HERE / info["path"]
        assert digest(path) == info["sha256"]
        assert path.stat().st_size == info["bytes"]
        target = extraction / path.stem
        target.mkdir()
        with zipfile.ZipFile(path) as archive:
            assert archive.comment == b"" and archive.testzip() is None
            names = archive.namelist()
            assert len(names) == len(set(names))
            for member in archive.infolist():
                assert member.date_time == (1980, 1, 1, 0, 0, 0)
                assert not member.extra and not member.comment
                assert not Path(member.filename).is_absolute()
                assert ".." not in Path(member.filename).parts
                assert member.external_attr >> 16 == 0o100644
            archive.extractall(target)
        rows = list(csv.DictReader((target / "FILE_MANIFEST.csv").open(newline="")))
        expected = {row["path"] for row in rows} | {"FILE_MANIFEST.csv"}
        assert set(names) == expected
        for row in rows:
            dest = target / row["path"]
            assert dest.stat().st_size == int(row["bytes"])
            assert digest(dest) == row["sha256"]
            if row["source_asset"]:
                root = SOURCE / "MATCHED_EXAMPLE_GALLERY" if path.stem == "VIFAILBACK_BLINDED_REVIEW" else SOURCE
                assert digest(root / row["source_asset"]) == row["source_sha256"]
        packages[path.stem] = {"member_count": len(names), "verified_manifest_entries": len(rows),
                               "crc_ok": True, "sha256_ok": True}

    blind = extraction / "VIFAILBACK_BLINDED_REVIEW"
    allowed = {"index.html", "README.md", "HUMAN_REVIEW_FORM.csv", "FRAME_TIMESTAMPS.csv", "FILE_MANIFEST.csv"}
    for bid in CASES:
        allowed.add(f"{bid}.html")
        allowed |= {f"assets/{bid}/BLINDED_OVERVIEW.jpg", f"assets/{bid}/sensor_timeline.png"}
        for camera in CAMERAS:
            allowed |= {f"assets/{bid}/{camera}/frame_{i:02d}.png" for i in range(16)}
            allowed |= {f"assets/{bid}/{camera}/full_sequence.jpg", f"assets/{bid}/{camera}/region_sequence.jpg"}
    actual = {path.relative_to(blind).as_posix() for path in blind.rglob("*") if path.is_file()}
    assert actual == allowed
    image_count = 0
    link_count = 0
    for relative in sorted(actual):
        assert not FORBIDDEN.search(relative), relative
        path = blind / relative
        if path.suffix in (".md", ".csv", ".html"):
            text = path.read_text()
            assert not FORBIDDEN.search(text), relative
            if path.suffix == ".html":
                parser = Links()
                parser.feed(text)
                for link in parser.links:
                    uri = urlsplit(link)
                    assert not uri.scheme and not uri.netloc
                    dest = (path.parent / unquote(uri.path)).resolve()
                    assert dest.is_relative_to(blind.resolve()) and dest.is_file(), (relative, link)
                    link_count += 1
                assert not re.search(r"fetch\(|XMLHttpRequest|WebSocket|https?://", text)
        elif path.suffix in (".png", ".jpg"):
            with Image.open(path) as checked:
                checked.verify()
            with Image.open(path) as image:
                assert not image.getexif()
                assert not set(image.info) & {"exif", "XML:com.adobe.xmp", "comment", "Software", "date:create", "date:modify"}
                assert not FORBIDDEN.search(str(image.info))
                if "/frame_" in relative:
                    assert image.size == (640, 480)
            image_count += 1
    assert image_count == 1120
    form = list(csv.DictReader((blind / "HUMAN_REVIEW_FORM.csv").open(newline="")))
    assert [row["blind_id"] for row in form] == CASES
    assert all(not v for row in form for k, v in row.items() if k != "blind_id")
    timing = list(csv.DictReader((blind / "FRAME_TIMESTAMPS.csv").open(newline="")))
    assert len(timing) == 960
    per_case = {}
    for bid in CASES:
        for camera in CAMERAS:
            selected = [row for row in timing if row["blind_id"] == bid and row["camera"] == camera]
            assert len(selected) == 16
            indices = [int(row["source_frame_index"]) for row in selected]
            times = [float(row["time_seconds"]) for row in selected]
            assert all(a < b for a, b in zip(indices, indices[1:]))
            assert all(a < b for a, b in zip(times, times[1:]))
            assert [int(row["selected_position"]) for row in selected] == list(range(1, 17))
            assert all(abs(t - idx / 25) < 1e-6 for t, idx in zip(times, indices))
            per_case.setdefault(bid, {})[camera] = len({digest(blind / row["image"]) for row in selected})

    # Real file:// browser test: no local server and no connection to source assets.
    browser_errors, failed_requests, requests, external_attempts = [], [], [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--disable-gpu", "--disable-background-networking", "--renderer-process-limit=2"])
        browser_version = browser.version
        context = browser.new_context(viewport={"width": 1440, "height": 1100}, service_workers="block")
        context.set_offline(True)

        def route(request_route):
            url = request_route.request.url
            if url.startswith("file:") or url.startswith("data:"):
                request_route.continue_()
            else:
                external_attempts.append(url)
                request_route.abort()

        context.route("**/*", route)
        context.add_init_script("""window.__draws = {};
const original = CanvasRenderingContext2D.prototype.drawImage;
CanvasRenderingContext2D.prototype.drawImage = function(...args) {
 const result = original.apply(this, args);
 window.__draws[this.canvas.id] = {src: args[0].src, rect: args.slice(1)};
 return result;
};""")
        page = context.new_page()
        page.on("pageerror", lambda error: browser_errors.append(str(error)))
        page.on("requestfailed", lambda request: failed_requests.append({"url": request.url, "failure": request.failure}))
        page.on("request", lambda request: requests.append(request.url))
        page.goto((blind / "index.html").as_uri(), wait_until="load")
        assert page.locator('a[href^="B"][href$=".html"]').count() == 20
        # Force lazy-loaded thumbnails to load using only extracted local assets.
        page.locator('img').evaluate_all("els => els.forEach(el => {el.loading = 'eager';})")
        page.wait_for_function("Array.from(document.images).every(im => im.complete && im.naturalWidth > 0)")
        page.screenshot(path=str(HERE / "offline_index_browser_check.png"))
        steps, drawings, static_images = 0, 0, 0
        for bid in CASES:
            page.goto((blind / f"{bid}.html").as_uri(), wait_until="load")
            assert page.title() == bid
            page.locator("details").evaluate_all("els => els.forEach(el => {el.open = true;})")
            page.locator("img").evaluate_all("els => els.forEach(el => {el.loading = 'eager';})")
            page.wait_for_function("Array.from(document.images).every(im => im.complete && im.naturalWidth > 0)")
            static_images += page.locator('img[src$="full_sequence.jpg"], img[src$="region_sequence.jpg"], img[src$="sensor_timeline.png"]').count()
            html_frames = page.evaluate("frames")
            for position in range(16):
                page.locator("#step").evaluate("(el, value) => { el.value = value; el.dispatchEvent(new Event('input', {bubbles: true})); }", str(position))
                suffix = f"frame_{position:02d}.png"
                page.wait_for_function("""suffix => ['cam_high','cam_left_wrist','cam_right_wrist'].every(v => {
 const im = document.getElementById(v), draw = window.__draws['crop_' + v];
 return im.complete && im.naturalWidth === 640 && im.naturalHeight === 480 &&
   im.src.endsWith('/' + v + '/' + suffix) && draw && draw.src === im.src &&
   JSON.stringify(draw.rect) === JSON.stringify([128,96,384,288,0,0,640,480]);
})""", arg=suffix)
                frame = html_frames[position]
                text = page.locator("#stamp").inner_text()
                assert text == f"Selected position {position + 1}/16; source frame {frame['index']}; {frame['time']:.3f} s"
                rows = [row for row in timing if row["blind_id"] == bid and int(row["selected_position"]) == position + 1]
                assert len(rows) == 3
                assert all(int(row["source_frame_index"]) == frame["index"] and abs(float(row["time_seconds"]) - frame["time"]) < 1e-10 for row in rows)
                steps += 1
                drawings += 3
            if bid == "B01":
                page.screenshot(path=str(HERE / "offline_case_browser_check.png"))
                for camera in CAMERAS:
                    screenshot = page.locator(f"#crop_{camera}").screenshot()
                    with Image.open(io.BytesIO(screenshot)) as image:
                        assert len(image.convert("RGB").getcolors(maxcolors=1000) or [0] * 1001) > 16
        assert steps == 320 and drawings == 960 and static_images == 140
        assert not browser_errors, browser_errors
        assert not failed_requests, failed_requests
        assert not external_attempts, external_attempts
        assert all(url.startswith(blind.as_uri() + "/") for url in requests), requests
        browser.close()

    before_path = HERE / (provenance["staging_directory"].replace("staging_", "source_evidence_before_") + ".json")
    before = json.loads(before_path.read_text())
    assert all(digest(SOURCE / relative) == expected for relative, expected in before.items())
    results.update({
        "passed": True, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "packages": packages, "strict_blind_allowlist_members": len(allowed),
        "images_decodable_and_metadata_checked": image_count, "local_html_references_verified": link_count,
        "blank_review_rows": len(form), "timestamp_rows": len(timing),
        "distinct_image_hashes_per_case_and_camera": per_case,
        "browser": {"name": "Chromium Headless Shell", "version": browser_version,
                    "file_url_mode": True, "offline": True, "gpu_disabled": True,
                    "cases": 20, "slider_positions_checked": steps,
                    "full_frame_and_crop_draws_checked": drawings, "static_sheets_and_plots_loaded": static_images,
                    "http_or_external_requests": external_attempts, "failed_requests": failed_requests,
                    "javascript_errors": browser_errors, "source_folder_requests": 0},
        "source_files_verified_unchanged": len(before),
        "no_video_extraction_or_training": True,
    })
    (HERE / "PACKAGE_VALIDATION.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({key: value for key, value in results.items() if key != "distinct_image_hashes_per_case_and_camera"}, indent=2))


if __name__ == "__main__":
    main()
