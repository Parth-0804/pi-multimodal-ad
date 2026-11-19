"""Prepare a fresh, version-pinned minimal laboratory acquisition audit."""
import csv
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path(__file__).parent
sys.path.insert(0, str(SOURCE / 'stage2'))
from download_msm import audit_plan, sha256


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run = Path('MILLING DATASET/runs') / (stamp + '-stage5-full-lab')
    for name in ('config', 'manifests', 'evidence', 'logs', 'cache', 'figures', 'experiments'):
        (run / name).mkdir(parents=True, exist_ok=False)
    cfg = {'handle': 'manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2',
           'dataset_id': 8392825, 'version': 2, 'dataset_doi': '10.34740/kaggle/ds/8392825',
           'paper_doi': '10.1038/s41597-026-07255-7',
           'data_root': 'MILLING DATASET/data/raw/msm/versions/2', 'run_root': str(run),
           'max_download_bytes': 2_700_000_000, 'free_space_reserve_gib': 10,
           'workers': 2, 'split_seed': 42, 'outer_folds': 3, 'inner_folds': 2,
           'stage1': 'MILLING DATASET/runs/20261026T230520276818Z-stage1',
           'stage2': 'MILLING DATASET/runs/20261027T001047876764Z-stage2-validated',
           'stage3': 'MILLING DATASET/runs/20261027T003527238586Z-stage3',
           'stage4': 'MILLING DATASET/runs/20261027T005343579234Z-stage4',
           'visibility_policy': 'All new interval-level visibility judgements pending independent review',
           'training_allowed': False, 'final_split_frozen': False}
    write(run / 'config/resolved_config.json', cfg)
    # Use the existing official-interface snapshotter, not a fabricated file listing.
    result = subprocess.run([sys.executable, '-B', str(SOURCE / 'inspect_official.py'), '--run', str(run)],
                            capture_output=True, text=True)
    (run / 'logs/official_snapshot.txt').write_text(result.stdout + result.stderr)
    result.check_returncode()
    inv = json.loads((run / 'manifests/official_file_inventory.json').read_text())
    old = json.loads((Path(cfg['stage1']) / 'manifests/official_file_inventory.json').read_text())
    if {x['name']: x['bytes'] for x in inv['files']} != {x['name']: x['bytes'] for x in old['files']}:
        raise ValueError('Pinned inventory changed since Stage 1: stop for evidence review')
    labs = ('imi_vm20i', 'imi_vmx30ui')
    groups = sorted({str(Path(f['name']).parent) for f in inv['files']
                     if f['name'].endswith('/label.csv') and f['name'].split('/')[0] in labs})
    assert len(groups) == 56
    plan = []
    for f in inv['files']:
        path = Path(f['name']); purpose = None
        if str(path.parent) in groups:
            purpose = ('video alignment and native frames' if path.suffix == '.mp4' else
                       'common 15-channel MTConnect contract' if path.name.endswith('_mtc.csv') else
                       'label-blind synchronization reference S2' if path.name.endswith('_s2.wav') else
                       'NC program identity and dependency audit' if path.suffix.lower() in ('.nc', '.txt') else None)
        elif f['name'] in [m + '.xml' for m in labs]:
            purpose = 'machine schema and native units'
        if purpose:
            plan.append({**f, 'purpose': purpose})
    for group in groups:
        names = [x['name'] for x in plan if str(Path(x['name']).parent) == group]
        assert sum(x.endswith('.mp4') for x in names) == 1, group
        assert sum(x.endswith('_mtc.csv') for x in names) == 1, group
        assert sum(x.endswith('_s2.wav') for x in names) == 1, group
    cfg.update(selected_groups=groups, download_plan=plan)
    # Initial config is preserved; download_config is the fully resolved plan.
    write(run / 'config/download_config.json', cfg)
    rows = audit_plan(cfg, inv, Path(cfg['data_root']))
    new_bytes = sum(x['bytes'] for x in rows if x['status'] == 'missing')
    free = shutil.disk_usage(cfg['data_root']).free
    assert new_bytes <= cfg['max_download_bytes']
    assert free - new_bytes >= 10 * 1024**3
    enriched = []
    for p, r in zip(plan, rows):
        parts = r['path'].split('/')
        enriched.append({'machine': parts[0] if len(parts)>1 else Path(parts[0]).stem,
                         'experiment': parts[1] if len(parts)>1 else '',
                         'relative_source_path': r['path'], 'official_bytes': r['bytes'],
                         'availability': r['status'], 'required_download_bytes': r['bytes'] if r['status']=='missing' else 0,
                         'purpose': p['purpose'], 'sha256': r['sha256']})
    with (run / 'MSM_DOWNLOAD_MANIFEST.csv').open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(enriched[0])); writer.writeheader(); writer.writerows(enriched)
    write(run / 'manifests/acquisition_gate.json', {'files': len(rows), 'existing': len(rows)-sum(x['status']=='missing' for x in rows),
             'new_files': sum(x['status']=='missing' for x in rows), 'new_bytes': new_bytes, 'free_bytes': free,
             'reserve_bytes': 10*1024**3, 'inventory_unchanged': True, 'automatic_authorization_gate': True})
    write(run / 'provenance_initial.json', {'started_utc': datetime.now(timezone.utc).isoformat(),
          'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
          'git_dirty': subprocess.check_output(['git','status','--short','--untracked-files=no'], text=True),
          'command': sys.argv, 'python': platform.python_version(), 'official_inventory_sha256': sha256(run/'manifests/official_file_inventory.json')})
    print(json.dumps({'run': str(run), 'files':len(rows),'new_bytes':new_bytes,'new_files':sum(x['status']=='missing' for x in rows)},indent=2))


if __name__ == '__main__':
    main()
