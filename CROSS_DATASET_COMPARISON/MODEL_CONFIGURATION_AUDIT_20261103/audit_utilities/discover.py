"""Read-only repository metadata inventory; write only inside this audit."""
from pathlib import Path
import collections
import csv
import datetime as dt
import json
import os

OUT = Path(__file__).resolve().parents[1]
REPO = OUT.parents[1]
SKIP = {'.git', '.agents', '.codex', '.aws', '.ssh', 'ma_thesis_env',
        '__pycache__', '.pytest_cache', '.mypy_cache', 'node_modules'}


def sensitive(name):
    low = name.lower()
    return (low == '.env' or low.startswith('.env.') or low == 'synology_cookies.txt'
            or low.endswith(('.pem', '.key')) or low in {'credentials', 'id_rsa', 'id_ed25519'}
            or 'access_token' in low or 'session_cookie' in low)


def dataset(path):
    value = path.lower()
    for text, label in [('reassemble', 'REASSEMBLE'), ('vifailback', 'VIFAILBACK'),
                        ('handover', 'HANDOVER'), ('msm', 'MSM'), ('milling', 'MSM_LEGACY'),
                        ('phm2026', 'PHM2026'), ('intel', 'INTEL_WELDING'),
                        ('reboot', 'REBOOT')]:
        if text in value:
            return label
    return 'OTHER_OR_SHARED'


def kind(path):
    p = Path(path)
    low = path.lower()
    if p.suffix.lower() in {'.pt', '.pth', '.ckpt', '.pkl', '.pickle', '.joblib', '.safetensors'}:
        return 'MODEL_OR_CHECKPOINT_CANDIDATE'
    if p.suffix == '.py': return 'SOURCE_CODE'
    if p.suffix.lower() in {'.yaml', '.yml', '.toml'} or 'config' in p.name.lower():
        return 'CONFIGURATION_CANDIDATE'
    if p.suffix.lower() in {'.csv', '.json', '.jsonl', '.npz', '.parquet'}:
        if 'predict' in low or 'oof' in low: return 'PREDICTION_CANDIDATE'
        if any(x in low for x in ['metric', 'result', 'assessment', 'evaluation']):
            return 'RESULT_CANDIDATE'
        if any(x in low for x in ['history', 'epoch', 'learning_curve', 'training']):
            return 'TRAINING_EVIDENCE_CANDIDATE'
        return 'STRUCTURED_METADATA_CANDIDATE'
    if p.suffix in {'.md', '.rst', '.txt'}: return 'DOCUMENTATION_CANDIDATE'
    if p.suffix in {'.log', '.out'}: return 'EXECUTION_LOG'
    return 'OTHER_METADATA_ONLY'


def main():
    totals = collections.defaultdict(lambda: {'files': 0, 'bytes': 0, 'categories': collections.Counter()})
    rows = []
    excluded = []
    for base, directories, files in os.walk(REPO, followlinks=False):
        parent = Path(base)
        directories[:] = sorted(d for d in directories if d not in SKIP
                                and not sensitive(d) and not d.startswith('.'))
        if parent == OUT or parent.is_relative_to(OUT):
            directories[:] = []
            continue
        for name in sorted(files):
            if sensitive(name):
                continue
            p = parent/name
            if p.is_symlink():
                continue
            try:
                stat = p.stat()
            except OSError as exc:
                excluded.append({'path': str(p.relative_to(REPO)), 'reason': str(exc)})
                continue
            relative = str(p.relative_to(REPO))
            category = kind(relative)
            row = {'path': relative, 'bytes': stat.st_size,
                   'mtime_utc': dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc).isoformat(),
                   'dataset_hint': dataset(relative), 'artifact_category': category,
                   'content_opened_by_discovery': False}
            rows.append(row)
            top = relative.split('/')[0]
            totals[top]['files'] += 1
            totals[top]['bytes'] += stat.st_size
            totals[top]['categories'][category] += 1
    with (OUT/'09_reviewer_handoff/REPOSITORY_ARTIFACT_INVENTORY.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = {'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'inventoried_files': len(rows),
              'top_level': totals, 'read_errors': excluded,
              'excluded_directory_names': sorted(SKIP),
              'secrets_content_accessed': False, 'raw_contents_accessed': False,
              'symlinks_followed': False}
    (OUT/'provenance/DISCOVERY_SUMMARY.json').write_text(json.dumps(report, indent=2)+'\n')
    model = [r for r in rows if r['artifact_category']=='MODEL_OR_CHECKPOINT_CANDIDATE']
    (OUT/'provenance/CHECKPOINT_CANDIDATE_PATHS.json').write_text(json.dumps(model, indent=2)+'\n')
    print(json.dumps({'files': len(rows), 'checkpoint_candidates': len(model),
                      'top_levels': len(totals), 'read_errors': len(excluded)}))
    for top, data in sorted(totals.items()):
        print(top, data['files'], data['bytes'], 'checkpoint_candidates',
              data['categories']['MODEL_OR_CHECKPOINT_CANDIDATE'])


if __name__ == '__main__':
    main()
