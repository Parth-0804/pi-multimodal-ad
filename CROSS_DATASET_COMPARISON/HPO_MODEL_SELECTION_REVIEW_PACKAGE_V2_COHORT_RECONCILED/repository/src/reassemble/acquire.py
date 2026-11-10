"""Official-record acquisition with checksum-gated, non-overwriting extraction."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import urllib.request
import zipfile


def digest(path, algorithm='md5'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_members(archive):
    seen = set()
    for info in archive.infolist():
        p = PurePosixPath(info.filename)
        if p.is_absolute() or '..' in p.parts or '\\' in info.filename:
            raise ValueError(f'Unsafe member: {info.filename}')
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError('Archive symlinks forbidden')
        if str(p) in seen:
            raise ValueError('Duplicate member name')
        seen.add(str(p))
        yield info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/reassemble/audit.json')
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    run = Path(args.run_dir)
    root = Path(config['data_root']).resolve() / 'REASSEMBLE'
    ancestor = root
    while not ancestor.exists():
        ancestor = ancestor.parent
    free = shutil.disk_usage(ancestor).free
    if free < config['minimum_free_GiB'] * 2**30:
        raise RuntimeError('G0 FAIL: less than 160 GiB free')
    downloads = root / 'downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(config['record_api'], timeout=60) as response:
        metadata = json.load(response)
    if metadata['pids']['doi']['identifier'] != config['doi']:
        raise ValueError('Unexpected DOI')
    (run / 'official_record_download.json').write_text(json.dumps(metadata, indent=2))
    entries = metadata['files']['entries']
    if entries['data.zip']['checksum'] != 'md5:812103a652ca9201e87a3bcecfee4ef3':
        raise ValueError('Main archive checksum differs from frozen specification')
    result = {'started_utc': datetime.now(timezone.utc).isoformat(), 'free_before_bytes': free, 'files': []}
    for name in ['README.txt', 'poses.zip', 'splits.zip', 'data.zip']:
        entry = entries[name]
        url = entry['links']['content']
        if not url.startswith('https://researchdata.tuwien.ac.at/'):
            raise ValueError('Nonofficial file URL')
        final = downloads / name
        expected = entry['checksum'].split(':', 1)[1]
        if final.exists():
            if final.stat().st_size != entry['size'] or digest(final) != expected:
                raise RuntimeError(f'Existing final file mismatch: {name}; preserved')
        else:
            part = downloads / (name + '.part')
            for attempt in range(2):
                print(f'Downloading {name}; attempt {attempt + 1}', flush=True)
                subprocess.run(['curl', '--fail', '--location', '--proto', '=https', '--proto-redir', '=https',
                                '--connect-timeout', '30', '--speed-time', '120', '--speed-limit', '1024',
                                '--retry', '8', '--retry-delay', '5', '--continue-at', '-', '--output', str(part), url], check=True)
                print(f'Checking MD5 {name}', flush=True)
                if part.stat().st_size == entry['size'] and digest(part) == expected:
                    os.replace(part, final)
                    break
                # Preserve failed bytes as evidence, then fetch a fresh candidate once.
                rejected = downloads / (name + '.checksum_failed.' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
                part.rename(rejected)
                if attempt == 1:
                    raise RuntimeError(f'G1 FAIL: checksum mismatch twice: {name}')
        result['files'].append({'name': name, 'size_bytes': final.stat().st_size, 'md5': expected, 'source': url})
        (run / 'acquisition_progress.json').write_text(json.dumps(result, indent=2))
    archives = []
    for name in ['data.zip', 'poses.zip', 'splits.zip']:
        with zipfile.ZipFile(downloads / name) as z:
            members = list(safe_members(z))
            print(f'Integrity scan {name}: {len(members)} members', flush=True)
            bad = z.testzip()
            if bad:
                raise RuntimeError(f'CRC failure: {name}: {bad}')
            archives.append({'archive': name, 'members': [{'name': m.filename, 'size_bytes': m.file_size, 'crc32': m.CRC} for m in members], 'extracted_bytes': sum(m.file_size for m in members)})
    (run / 'archive_inventory.json').write_text(json.dumps(archives, indent=2))
    required = sum(a['extracted_bytes'] for a in archives)
    if shutil.disk_usage(root).free < required * 1.05 + 10 * 2**30:
        raise RuntimeError('Insufficient extraction space with reserve')
    raw = root / 'raw'
    if raw.exists():
        raise RuntimeError('Refusing to overwrite existing extraction; inspect provenance before resume')
    staging = root / 'raw.extracting'
    staging.mkdir(exist_ok=False)
    for archive in archives:
        print(f"Extracting {archive['archive']}", flush=True)
        with zipfile.ZipFile(downloads / archive['archive']) as z:
            for info in safe_members(z):
                dest = staging / info.filename
                if info.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(info) as src, dest.open('xb') as out:
                        shutil.copyfileobj(src, out, 8 * 1024 * 1024)
    staging.rename(raw)
    files = [p for p in raw.rglob('*') if p.is_file()]
    result.update(status='PASS', completed_utc=datetime.now(timezone.utc).isoformat(), extracted_bytes=sum(p.stat().st_size for p in files), h5_files=sum(p.suffix == '.h5' for p in files), json_files=sum(p.suffix == '.json' for p in files), free_after_bytes=shutil.disk_usage(root).free)
    (run / 'acquisition.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
