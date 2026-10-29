"""Compare locked judgments and independently rejoin all native source labels."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import json
import zipfile

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REV = '619791b94f61667333fe179d471051e0bca0e06f'
ORIGINAL_REV = '21df46c2585c52e5a62df5f4b946bae6cbc6fed7'


def load(path):
    return json.loads(path.read_text())


def lines(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    with (RUN / path).open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def table(path, rows):
    with (RUN / path).open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    lock = load(RUN / '00_LOCKED_REVIEW/REVIEW_LOCK.json')
    review_path = SOURCE / 'VIFAILBACK_INDEPENDENT_BLINDED_VISUAL_REVIEW.md'
    assert sha(review_path) == lock['source_sha256']
    assert sha(RUN / '00_LOCKED_REVIEW/INDEPENDENT_REVIEW_LOCKED.md') == lock['source_sha256']
    evidence = SOURCE / 'source_evidence'
    meta = evidence / 'vifailback/meta'
    inventory = load(evidence / 'vifailback_files.json')
    assert inventory['sha'] == REV
    files = {row['rfilename']: row for row in inventory['siblings']}
    annotations = lines(meta / 'vifailback_annotations.jsonl')
    episodes = {row['episode_index']: row for row in lines(meta / 'episodes.jsonl')}
    tasks = {row['task']: row['task_index'] for row in lines(meta / 'tasks.jsonl')}
    assert len(annotations) == len(episodes) == 5202 and len(tasks) == 100
    by_id = {row['episode_index']: row for row in annotations}
    assert len(by_id) == 5202
    originals = defaultdict(list)
    receipts = []
    original_paths = sorted((evidence / 'original/annotated_data').rglob('*.json'))
    original_paths = [path for path in original_paths if not path.name.endswith('.receipt.json')]
    assert len(original_paths) == 109
    for path in original_paths:
        receipt = load(path.with_name(path.name + '.receipt.json'))
        assert sha(path) == receipt['sha256'] and path.stat().st_size == receipt['bytes']
        assert ORIGINAL_REV in receipt['source_url']
        receipts.append({'path': str(path.relative_to(SOURCE)), 'sha256': sha(path), 'url': receipt['source_url']})
        for record in load(path):
            originals[record['video']].append(record)
    assert len(originals) == 5202 and all(len(rows) == 1 for rows in originals.values())
    rows, issues, video_hashes = [], [], defaultdict(list)
    for a in annotations:
        eid = a['episode_index']
        episode = episodes[eid]
        native = a['annotation']
        assert originals[native['video']][0] == native
        assert a['episode_success'] == {'yes': 'failure', 'no': 'success'}[native['failure_detection']]
        assert episode['tasks'] == [native['task']] and episode['length'] == a['num_frames']
        tid = tasks[native['task']]
        paths = [f'data/chunk-{eid // 1000:03d}/episode_{eid:06d}.parquet'] + [
            f'videos/chunk-{eid // 1000:03d}/observation.images.{camera}/episode_{eid:06d}.mp4'
            for camera in ('cam_high', 'cam_left_wrist', 'cam_right_wrist')]
        missing = [path for path in paths if path not in files]
        if missing:
            issues.append({'episode_index': eid, 'missing_paths': missing})
        for path in paths:
            if path in files:
                item = files[path]
                assert item['size'] > 0 and len(item['lfs']['sha256']) == 64
                if path.endswith('.mp4'):
                    video_hashes[item['lfs']['sha256']].append(path)
        rows.append({'episode_index': eid, 'canonical_task_id': tid, 'task_instruction': native['task'],
                     'source_task': a['source_task'], 'source_episode': a['source_episode'],
                     'source_hdf5': a['source_hdf5'], 'native_outcome': a['episode_success'],
                     'failure_type': native.get('failure_type') or '', 'label': int(a['episode_success'] == 'failure'),
                     'frame_count': a['num_frames'], 'native_human_intervention': native.get('failure_type') == 'human intervention',
                     'data': paths[0], 'video_high': paths[1], 'video_left': paths[2], 'video_right': paths[3],
                     'remote_four_file_join': not missing})
    assert not issues
    assert len({row['source_hdf5'] for row in rows}) == 5202
    table('02_COHORT_AND_SPLITS/ALL_NATIVE_EPISODES.csv', rows)
    save('provenance/ORIGINAL_ANNOTATION_SOURCE_HASHES.json', receipts)

    export = SOURCE / 'PORTABLE_REVIEW_EXPORTS/20261028T222841Z'
    archive = export / 'VIFAILBACK_UNBLINDING.zip'
    expected = next(row for row in load(export / 'EXPORT_PROVENANCE.json')['packages'] if row['path'] == archive.name)
    assert sha(archive) == expected['sha256'] and archive.stat().st_size == expected['bytes']
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None
        key_bytes = zipped.read('UNBLINDING/SOURCE_LABEL_KEY.json')
        assert key_bytes == (SOURCE / 'MATCHED_EXAMPLE_GALLERY/UNBLINDING/SOURCE_LABEL_KEY.json').read_bytes()
        key = json.loads(key_bytes)
    keyed = {row['blind_id']: row for row in key}
    assert len(keyed) == 20
    comparison = []
    for predicted in lock['predictions']:
        identity = keyed[predicted['blind_id']]
        a = by_id[int(identity['episode_index'])]
        for field in ('source_hdf5', 'source_task', 'source_episode', 'episode_success'):
            assert identity[field] == str(a[field])
        assert identity['failure_type'] == (a['annotation'].get('failure_type') or 'success')
        status = 'UNCERTAIN_RETAINED' if predicted['locked_prediction'] == 'uncertain' else (
            'AGREEMENT' if predicted['locked_prediction'] == a['episode_success'] else 'DISAGREEMENT')
        comparison.append({**predicted, 'episode_index': a['episode_index'], 'source_hdf5': a['source_hdf5'],
                           'canonical_task_id': tasks[a['annotation']['task']], 'native_outcome': a['episode_success'],
                           'native_failure_type': a['annotation'].get('failure_type') or '', 'comparison': status,
                           'native_human_intervention': a['annotation'].get('failure_type') == 'human intervention'})
    table('01_UNBLINDING/LOCKED_PREDICTIONS_VS_NATIVE_LABELS.csv', comparison)
    verdict = Counter(row['comparison'] for row in comparison)
    save('01_UNBLINDING/UNBLINDING_VERIFICATION.json', {
        'verified_utc': datetime.now(timezone.utc).isoformat(), 'locked_review_sha256': lock['source_sha256'],
        'lock_created_before_comparison': True, 'source_key_archive': str(archive.relative_to(SOURCE)),
        'source_key_archive_sha256': sha(archive), 'key_sha256': hashlib.sha256(key_bytes).hexdigest(),
        'conversion_revision': REV, 'original_revision': ORIGINAL_REV,
        'original_annotation_files_verified': 109, 'original_records_rejoined': 5202,
        'pilot_key_joins_verified': 20, 'comparison_counts': dict(verdict),
        'decided_agreement_fraction': verdict['AGREEMENT'] / (verdict['AGREEMENT'] + verdict['DISAGREEMENT']),
        'coverage': (20 - verdict['UNCERTAIN_RETAINED']) / 20,
        'B02': 'Locked uncertain; original native label revealed separately; prediction never revised',
        'interpretation': 'Selected pilot annotation agreement of AI-assisted judgments; not model accuracy, human reliability or prevalence estimate'})
    summary = {'native_episodes': len(rows), 'native_counts': dict(Counter(row['native_outcome'] for row in rows)),
               'native_failure_categories': dict(Counter(row['failure_type'] or 'success' for row in rows)),
               'canonical_tasks': len(tasks), 'source_directories': len({row['source_task'] for row in rows}),
               'source_hdf5_unique': True, 'remote_rgb_files': sum(path.endswith('.mp4') for path in files),
               'remote_rgb_bytes': sum(item['size'] for path, item in files.items() if path.endswith('.mp4')),
               'all_remote_rgb_sensor_joins_present': True, 'missing_files': issues,
               'identical_video_hash_components': [paths for paths in video_hashes.values() if len(paths) > 1],
               'raw_video_scope': 'Remote pinned inventory hashes for full release; actual media decode evidence limited to previous pilot and QC files'}
    save('02_COHORT_AND_SPLITS/FULL_NATIVE_AND_FILE_AUDIT.json', summary)
    print(json.dumps({'unblinding': dict(verdict), 'native': summary['native_counts'],
                      'human_intervention': summary['native_failure_categories']['human intervention'],
                      'remote_files': summary['remote_rgb_files']}, indent=2))
