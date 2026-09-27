#!/usr/bin/env python3
"""Package the blind inspection set for sorting away from this machine.

Produces two deliverables from the ALREADY-BUILT set at
scratch/blind_inspection/. Nothing is re-selected and nothing is rebuilt.

  sorter.html                  primary: one self-contained file, images
                               embedded, openable on a phone with no software
                               and no network
  blind_inspection_set.zip     fallback: drag-and-drop folders

This script never reads _KEY_DO_NOT_OPEN/. It only touches to_sort/ and
to_sort_fullphoto/, so packaging cannot leak the answer even by accident, and
the zip contents are explicitly checked for key material before finishing.
"""

from __future__ import annotations

import argparse
import base64
import io
import re
import zipfile
from pathlib import Path

from PIL import Image

ZIP_README = """BLIND TOOTH INSPECTION
======================

There are 42 images in to_sort/. Each shows one gear tooth flank.

WHAT TO DO
  1. Look at each image in to_sort/.
  2. Drag it into exactly one of:
         sorted_damaged/   visible damage
         sorted_clean/     no visible damage
         sorted_unsure/    genuinely cannot tell
     Use sorted_unsure/ only when you really cannot decide. How many land
     there is itself useful information, so do not force a guess.
  3. If a crop is ambiguous, open the SAME filename in full_photos/ to see
     the whole photograph.

IMPORTANT
  - Do NOT rename anything. The filenames are the only identifier, and a
    renamed file cannot be matched back.
  - There are 42 images. The split is not necessarily even, and you are not
    told what it is.
  - When you are finished, to_sort/ must be empty.

WHEN DONE
  Compress the three sorted_* folders -- with the images inside them -- into
  a single zip and send it back. The empty .keep files can stay.

  Please note roughly how long this took: ______________

The filenames are random and encode nothing: not experiment, not run, not
tooth, not score, not order. Sorting the directory listing tells you nothing.
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Blind Tooth Inspection</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  body { margin:0; background:#111; color:#eee; font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  header { padding:8px 12px; background:#181818; border-bottom:1px solid #2a2a2a; }
  .warn { color:#e8b339; font-size:13px; }
  .progress { font-variant-numeric:tabular-nums; font-weight:600; }
  main { display:block; padding:8px; text-align:center; }
  img { width:100%; height:auto; max-height:62vh; object-fit:contain; display:block;
        margin:0 auto; border-radius:4px; background:#000; min-height:120px; }
  footer { padding:10px 12px calc(10px + env(safe-area-inset-bottom)); background:#181818; border-top:1px solid #2a2a2a; }
  .row { display:flex; gap:8px; }
  button { flex:1; padding:16px 8px; font-size:15px; font-weight:650; letter-spacing:.02em;
           border:0; border-radius:8px; color:#111; cursor:pointer; }
  .damaged { background:#e2664f; } .clean { background:#5cc08a; } .unsure { background:#9aa0a6; }
  .sub { margin-top:8px; display:flex; gap:8px; }
  .sub button { flex:0 0 auto; padding:9px 14px; font-size:13px; font-weight:500;
                background:#2c2c2c; color:#ddd; }
  .sub button[disabled] { opacity:.35; cursor:default; }
  #done { display:none; padding:14px; }
  textarea { width:100%; height:46vh; background:#0b0b0b; color:#d8d8d8; border:1px solid #333;
             border-radius:6px; padding:10px; font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace; }
</style>
</head>
<body>
<div id="err" style="display:none;background:#7a1f1f;color:#fff;padding:10px;font:13px monospace;white-space:pre-wrap"></div>
<header>
  <div class="warn">Work is held in memory only. If you close or reload this page before finishing, everything is lost.</div>
  <div class="progress" id="progress"></div>
</header>
<main id="stage"><img id="shot" alt=""></main>
<footer id="controls">
  <div class="row">
    <button class="damaged" id="bDamaged">DAMAGED</button>
    <button class="clean"   id="bClean">CLEAN</button>
    <button class="unsure"  id="bUnsure">UNSURE</button>
  </div>
  <div class="sub">
    <button id="bBack">&larr; Back</button>
    <button id="bFull">Show full photograph</button>
  </div>
</footer>
<div id="done">
  <h2 style="margin:.2em 0">All 42 sorted.</h2>
  <p>Copy everything below and send it back.</p>
  <div class="sub" style="margin-bottom:8px">
    <button id="bCopy">Copy to clipboard</button>
    <button id="bReview">&larr; Review last image</button>
  </div>
  <textarea id="out" readonly></textarea>
</div>
<script>
window.onerror = function (message, source, line, column) {
  var box = document.getElementById('err');
  box.style.display = 'block';
  box.textContent = 'ERROR: ' + message + '\\nline ' + line + ':' + column +
    '\\nTell Claude this text.';
  return false;
};
const CROPS = __CROPS__;
const FULLS = __FULLS__;

// Fresh order every time the file is opened, so position carries no information.
const order = CROPS.map((_, i) => i);
for (let i = order.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [order[i], order[j]] = [order[j], order[i]];
}

const answers = new Map();      // index -> "DAMAGED" | "CLEAN" | "UNSURE"
const spent   = new Map();      // index -> accumulated seconds
let pos = 0, showingFull = false, entered = performance.now();
const started = performance.now();

const $ = (id) => document.getElementById(id);
const shot = $('shot');

function accrue() {
  const idx = order[pos];
  const delta = (performance.now() - entered) / 1000;
  spent.set(idx, (spent.get(idx) || 0) + delta);
  entered = performance.now();
}

function render() {
  const idx = order[pos];
  shot.src = showingFull ? FULLS[idx] : CROPS[idx];
  $('progress').textContent = (pos + 1) + ' / ' + CROPS.length;
  $('bFull').textContent = showingFull ? 'Show crop' : 'Show full photograph';
  $('bBack').disabled = pos === 0;
  entered = performance.now();
}

function answer(call) {
  accrue();
  answers.set(order[pos], call);
  showingFull = false;
  if (pos === CROPS.length - 1 && answers.size === CROPS.length) { finish(); return; }
  pos = Math.min(pos + 1, CROPS.length - 1);
  // skip forward to the first unanswered image, if any remain
  if (answers.has(order[pos])) {
    const next = order.findIndex((i) => !answers.has(i));
    if (next === -1) { finish(); return; }
    pos = next;
  }
  render();
}

function finish() {
  accrue();
  const total = Math.round((performance.now() - started) / 1000);
  const lines = ['BLIND_INSPECTION_RESULT_V1', 'total_seconds=' + total];
  CROPS.forEach((_, i) => {
    lines.push(TOKENS[i] + ',' + answers.get(i) + ',' + (spent.get(i) || 0).toFixed(1));
  });
  lines.push('END');
  $('out').value = lines.join('\\n');
  $('stage').style.display = 'none';
  $('controls').style.display = 'none';
  $('progress').textContent = CROPS.length + ' / ' + CROPS.length;
  $('done').style.display = 'block';
}

const TOKENS = __TOKENS__;
$('bDamaged').onclick = () => answer('DAMAGED');
$('bClean').onclick   = () => answer('CLEAN');
$('bUnsure').onclick  = () => answer('UNSURE');
$('bBack').onclick    = () => { if (pos > 0) { accrue(); pos--; showingFull = false; render(); } };
$('bFull').onclick    = () => { accrue(); showingFull = !showingFull; render(); };
$('bReview').onclick  = () => {
  $('done').style.display = 'none';
  $('stage').style.display = 'block';
  $('controls').style.display = 'block';
  render();
};
$('bCopy').onclick = async () => {
  const text = $('out').value;
  try { await navigator.clipboard.writeText(text); $('bCopy').textContent = 'Copied'; }
  catch (e) { $('out').select(); document.execCommand('copy'); $('bCopy').textContent = 'Copied'; }
  setTimeout(() => { $('bCopy').textContent = 'Copy to clipboard'; }, 1500);
};
render();
</script>
</body>
</html>
"""


def encode(path: Path, max_width: int, quality: int) -> tuple[str, int]:
    image = Image.open(path)
    width, height = image.size
    if width > max_width:
        image = image.resize((max_width, round(height * max_width / width)), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=quality)
    raw = buffer.getvalue()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii"), len(raw)


def build_html(root: Path, out: Path, *, crop_width: int, crop_quality: int,
               full_width: int, full_quality: int) -> None:
    crops = sorted((root / "to_sort").glob("*.jpg"))
    tokens = [p.name for p in crops]
    crop_uris, full_uris = [], []
    sizes = set()
    for path in crops:
        uri, _ = encode(path, crop_width, crop_quality)
        crop_uris.append(uri)
        full = root / "to_sort_fullphoto" / path.name
        if not full.is_file():
            raise SystemExit(f"missing full photograph for {path.name}")
        full_uri, _ = encode(full, full_width, full_quality)
        full_uris.append(full_uri)
        sizes.add(Image.open(path).size)
    if len(sizes) != 1:
        raise SystemExit(f"crops are not a uniform size: {sizes}")

    def as_array(values: list[str]) -> str:
        # One entry per line. A single 2.6 MB line is enough to defeat some
        # mobile parsers, which is what broke the first build.
        return "[\n" + ",\n".join(f'"{v}"' for v in values) + "\n]"

    html = (HTML_TEMPLATE
            .replace("__CROPS__", as_array(crop_uris))
            .replace("__FULLS__", as_array(full_uris))
            .replace("__TOKENS__", as_array(tokens)))
    out.write_text(html, encoding="utf-8")


def build_zip(root: Path, out: Path, *, full_width: int, full_quality: int) -> list[str]:
    crops = sorted((root / "to_sort").glob("*.jpg"))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in crops:
            archive.write(path, f"to_sort/{path.name}")
            source = root / "to_sort_fullphoto" / path.name
            image = Image.open(source)
            width, height = image.size
            if width > full_width:
                image = image.resize((full_width, round(height * full_width / width)),
                                     Image.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", quality=full_quality)
            archive.writestr(f"full_photos/{path.name}", buffer.getvalue())
        for folder in ("sorted_damaged", "sorted_clean", "sorted_unsure"):
            archive.writestr(f"{folder}/.keep", "")
        archive.writestr("README.txt", ZIP_README)
        return archive.namelist()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="scratch/blind_inspection")
    parser.add_argument("--crop-width", type=int, default=900)
    parser.add_argument("--crop-quality", type=int, default=72)
    parser.add_argument("--html-full-width", type=int, default=480)
    parser.add_argument("--html-full-quality", type=int, default=50)
    parser.add_argument("--zip-full-width", type=int, default=1600)
    parser.add_argument("--zip-full-quality", type=int, default=80)
    args = parser.parse_args(argv)

    root = Path(args.root)
    html_path = root / "sorter.html"
    zip_path = root / "blind_inspection_set.zip"

    build_html(root, html_path, crop_width=args.crop_width, crop_quality=args.crop_quality,
               full_width=args.html_full_width, full_quality=args.html_full_quality)
    names = build_zip(root, zip_path, full_width=args.zip_full_width,
                      full_quality=args.zip_full_quality)

    print("A1 sorter.html")
    print(f"  {html_path.resolve()}")
    print(f"  {html_path.stat().st_size / 1e6:.2f} MB, 42 crops + 42 full frames embedded")
    print("\nA2 blind_inspection_set.zip")
    print(f"  {zip_path.resolve()}")
    print(f"  {zip_path.stat().st_size / 1e6:.2f} MB, {len(names)} entries")

    print("\nKEY-LEAK CHECK")
    forbidden = ("key", "exp", "run", "tooth", "score")
    listing = "\n".join(names)
    hits = {word: [n for n in names if word in n.lower()] for word in forbidden}
    for word in forbidden:
        found = hits[word]
        print(f"  zip listing contains {word!r:8s}: {'YES -> ' + str(found) if found else 'no'}")
    banned_files = [n for n in names
                    if "key.csv" in n or "score_inspection" in n or "_KEY_DO_NOT_OPEN" in n]
    print(f"  key.csv / score_inspection.py / _KEY_DO_NOT_OPEN present: "
          f"{banned_files if banned_files else 'no'}")
    token_like = re.compile(r"^(to_sort|full_photos)/img_[0-9a-f]{8}\.jpg$")
    odd = [n for n in names
           if not token_like.match(n)
           and n not in {"README.txt"}
           and not n.endswith("/.keep")]
    print(f"  entries that are not a random token, README or .keep: {odd if odd else 'none'}")
    if any(hits.values()) or banned_files or odd:
        raise SystemExit("KEY-LEAK CHECK FAILED — zip not safe to send")

    print("\nNEXT: send sorter.html (open it, tap through 42 images, copy the result "
          "block) or the zip if the HTML will not open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
