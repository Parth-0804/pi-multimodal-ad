"""Portable copies of existing review derivatives; no new labels or image edits."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import shutil
import zipfile

PROJECT = Path(__file__).resolve().parents[2]
BASE = PROJECT / 'REBOOT'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def write_new(path, text):
    if path.exists():
        assert path.read_text() == text, f'Existing derivative differs: {path}'
    else:
        with path.open('x') as f:
            f.write(text)


def make_archive(package, dest, include_keys=False):
    files = sorted(p for p in package.rglob('*') if p.is_file() and ('UNBLINDING' in p.relative_to(package).parts) == include_keys)
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for p in files:
            # PNG/MP4 already compressed; storing preserves bytes and avoids CPU contention.
            z.write(p, str(p.relative_to(package)), compress_type=zipfile.ZIP_STORED if p.suffix in ('.png', '.mp4') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(files)
        assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
    return {'path': str(dest.relative_to(PROJECT)), 'bytes': dest.stat().st_size, 'sha256': digest(dest), 'members': len(files)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    args = p.parse_args()
    run = args.run.resolve()
    target = BASE / '08_visual_examples_and_eda/INDEPENDENT_VISUAL_REVIEW_PACKAGE'
    if shutil.disk_usage(PROJECT).free < 21_000_000_000:
        raise RuntimeError('Free reserve guard')
    target.mkdir(parents=True, exist_ok=True)
    old = BASE / '04_visual_failure_review/galleries/blinded_pilot_v1'
    source_frame_rows = list(csv.DictReader((BASE / '03_video_sensor_alignment/SELECTED_FRAME_MANIFEST.csv').open()))
    receipts, neutral_frames = [], []
    cameras = ['cam_high', 'cam_low', 'cam_left_wrist', 'cam_right_wrist']
    contents = ['<!doctype html><meta charset="utf-8"><title>Independent REBOOT visual review</title>',
                '<style>body{font:16px system-ui;max-width:1200px;margin:auto;padding:20px}img{max-width:100%;height:auto}summary{padding:14px;cursor:pointer}section{border-top:2px solid #999;margin-top:24px}video{max-width:100%}</style>',
                '<h1>Independent visual review: B001–B010</h1><p>Record observations before requesting the separate source key. No model targets are supplied. Four views describe the same ten demonstrations, not forty independent events.</p>',
                '<p><a href="RESEARCHER_VISUAL_REVIEW_SHEET.csv">Blank review sheet</a> · <a href="README.md">Review instructions</a></p>',
                '<p>Object: 16 mm cylinder; intended target: matching task-board fixture. Identify the object, target, occlusion and observed motion independently. Image crops are fixed by camera and can miss the moving target; compare full view and motion preview. All times refer to original episode seconds.</p>']

    def copy(src, rel):
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            with src.open('rb') as reader, dest.open('xb') as writer:
                shutil.copyfileobj(reader, writer)
        sha = digest(dest)
        assert sha == digest(src)
        receipts.append({'path': str(rel), 'bytes': dest.stat().st_size, 'sha256': sha})

    for i in range(1, 11):
        masked = f'B{i:03d}'
        copy(old / masked / 'sensor_timeline.png', Path('gallery') / masked / 'sensor_timeline.png')
        contents.append(f'<section><h2>{masked}</h2><img loading="lazy" src="gallery/{masked}/sensor_timeline.png" alt="Observed state timelines">')
        for cam in cameras:
            rel = Path('gallery') / masked / cam
            for name in ['full_sequence.png', 'context_sequence.png', 'preview.mp4']:
                copy(old / masked / cam / name, rel / name)
            for n in range(1, 17):
                name = f'frame_{n:02d}_context.png'
                copy(old / masked / cam / name, rel / name)
            contents.append(f'<details><summary>{masked} / {cam}</summary><video controls preload="none" width="640" src="{rel}/preview.mp4"></video><p>Review derivative; not the original acquisition video.</p><img loading="lazy" src="{rel}/full_sequence.png" alt="Sixteen full-frame samples"><img loading="lazy" src="{rel}/context_sequence.png" alt="Sixteen enlarged-context samples"><p>Full-resolution region images: ')
            contents.extend(f'<a href="{rel}/frame_{n:02d}_context.png">{n:02d}</a> ' for n in range(1, 17))
            contents.append('</p></details>')
        contents.append('</section>')
    write_new(target / 'index.html', '\n'.join(contents))
    copy(BASE / '04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv', Path('RESEARCHER_VISUAL_REVIEW_SHEET.csv'))
    review = list(csv.DictReader((target / 'RESEARCHER_VISUAL_REVIEW_SHEET.csv').open()))
    assert len(review) == 40 and all(not v for row in review for k, v in row.items() if k not in ('masked_id', 'camera'))
    for row in source_frame_rows:
        rel = f"gallery/{row['masked_id']}/{row['camera']}/{Path(row['context_frame']).name}"
        assert digest(target / rel) == row['context_png_sha256']
        neutral_frames.append({k: row[k] for k in ('masked_id', 'camera', 'frame_order', 'native_frame_index', 'native_timestamp_s', 'context_crop_box_xyxy', 'context_png_sha256')})
        neutral_frames[-1]['context_frame'] = rel
    with (target / 'BLINDED_FRAME_MANIFEST.csv').open('x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(neutral_frames[0])); w.writeheader(); w.writerows(neutral_frames)
    readme = '''# Independent visual review package

Extract the main ZIP and open `index.html` in a browser; all links work offline.
The main ZIP is suitable for upload for an independent review. Its source key
is intentionally withheld in a SECOND archive, `INDEPENDENT_VISUAL_REVIEW_UNBLINDING.zip`.
The expanded package's `UNBLINDING/` directory contains the same key. Do not
upload/open that archive or directory before the reviewer has saved observations.

Review B001–B010 across overhead (`cam_high`), front (`cam_low`), and left/right
wrist views. Each view contains sixteen original selected frame indices in full
and enlarged-context contact sheets, a motion preview, and sixteen 640×480
enlarged-context PNGs for closer inspection. Full-resolution contact sheets are
960×840; sensor plots are 1320×840. Fixed camera crops can exclude the target;
the full view and preview remain available. Enlarging does not create physical detail.

Complete one row per example/view in `RESEARCHER_VISUAL_REVIEW_SHEET.csv`:
identify object and target; describe observed motion/phase; judge failure
visibility yes/no/uncertain with a concrete observation; estimate event times
in original episode seconds; rate confidence 1–5, occlusion and camera utility;
flag force-only or visually ambiguous cases. Report uncertainty rather than
inferring contact forces, submillimetre mating success or hidden causes.
Fourteen traces are observed position feedback, with units not declared in
the release; commands are excluded from these plots. No physical latency
calibration or independent human visual certification is claimed.

Save the completed sheet with reviewer identity/date under a NEW filename.
Only then obtain the separate source key and compare the observations with
native annotations. Keep independent observations distinct from source labels.
An LLM review must be identified as an LLM assessment, not a human review or
original annotation. All forty human assessment rows are currently blank.

These diagnostic windows differ in duration and lack phase-matched normal
controls. The masked gallery does not establish controlled blinding, classifier
accuracy, early warning, or valid binary targets. Existing pilot examples are
development material; future evaluation needs fresh held-out recordings.

`BLINDED_FRAME_MANIFEST.csv` retains index/time/crop/hash without source labels.
`PACKAGE_FILE_MANIFEST.json` records immutable derivative identities.
The separate key retains original repository revisions, LFS source references,
native annotations, episode/video offsets and exact selected-frame mappings.
Original multi-gigabyte recording chunks and duplicate full-frame PNGs are
omitted; no re-encoding or image editing was performed in this packaging step.
'''
    write_new(target / 'README.md', readme)
    key = target / 'UNBLINDING'
    key.mkdir(exist_ok=True)
    for src, name in [
        (BASE / '04_visual_failure_review/UNBLINDING_KEY.json', 'UNBLINDING_KEY.json'),
        (BASE / '03_video_sensor_alignment/SELECTED_FRAME_MANIFEST.csv', 'ORIGINAL_SELECTED_FRAME_MANIFEST.csv'),
        (BASE / '03_video_sensor_alignment/NUMERICAL_ACQUISITION_MANIFEST.json', 'ORIGINAL_NUMERICAL_SOURCE_IDENTITIES.json'),
        (BASE / '01_raw_dataset/PILOT_VIDEO_DOWNLOAD_MANIFEST.json', 'ORIGINAL_VIDEO_SOURCE_IDENTITIES.json')]:
        copy(src, Path('UNBLINDING') / name)
    (key / 'README.md').write_text('Open only after saving the independent review. Native annotation values remain uncorrected and do not certify binary targets. Original source paths refer to the researcher workspace; pinned public URLs and revisions identify remote originals.\n')
    public_receipts = [r for r in receipts if not r['path'].startswith('UNBLINDING/')]
    (target / 'PACKAGE_FILE_MANIFEST.json').write_text(json.dumps({'media_files': public_receipts, 'images_edited': False, 'human_reviews_completed': 0, 'original_videos_included': False}, indent=2) + '\n')
    (key / 'SOURCE_KEY_FILE_MANIFEST.json').write_text(json.dumps([r for r in receipts if r['path'].startswith('UNBLINDING/')], indent=2) + '\n')
    main_zip = make_archive(target, target.with_suffix('.zip'))
    key_zip = make_archive(target, target.parent / 'INDEPENDENT_VISUAL_REVIEW_UNBLINDING.zip', include_keys=True)
    with (run / 'reports/VISUAL_PACKAGE_VALIDATION.json').open('x') as f:
        json.dump({'blinded_archive': main_zip, 'separate_unblinding_archive': key_zip,
                   'contact_sheets': 80, 'sensor_timelines': 10, 'motion_previews': 40,
                   'full_resolution_region_frames': 640, 'source_frame_hashes_matched': 640,
                   'blank_human_review_rows': 40, 'human_review_complete': False,
                   'no_key_in_main_archive': True, 'main_gallery_has_no_source_identity': 'REBOOT26' not in (target / 'index.html').read_text()}, f, indent=2)
    print(json.dumps({'main_zip': main_zip, 'key_zip': key_zip}, indent=2), flush=True)


if __name__ == '__main__':
    main()
