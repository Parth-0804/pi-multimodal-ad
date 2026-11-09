"""Read only original statistic/index members, not raw sensor/video payloads."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from common import ROOT, REPO, STUDY, read, write, relative, sha, cohort


def main():
    x = np.load(STUDY/'shared_cache/sensor_statistics.npy', allow_pickle=False)
    rows = cohort()
    seen = set()
    receipts = []
    for path in sorted((REPO/'runs/reassemble/20260927T154732Z-section1/features').glob('*.npz')):
        with np.load(path, allow_pickle=False) as archive:
            indices = archive['row_index']
            statistics = archive['statistics']
        assert statistics.shape == (len(indices), 220)
        assert np.array_equal(x[indices], statistics, equal_nan=True), ('ORIGINAL_SENSOR_REPRESENTATION_DRIFT', path.name)
        assert not seen & set(indices.tolist())
        seen.update(indices.tolist())
        for index in indices:
            assert rows[int(index)]['recording_id'] == path.stem
        metadata = path.with_suffix('.json')
        receipts.append({'source_feature_archive': relative(path),
            'original_declared_archive_sha256_not_rehashed_here': read(metadata)['feature_sha256'],
            'metadata_path': relative(metadata), 'metadata_sha256': sha(metadata),
            'rows': len(indices), 'statistic_and_index_members_checked_only': True})
    assert seen == set(range(4530)) and len(receipts) == 148
    write(ROOT/'03_static_sensor_evidence/ORIGINAL_FEATURE_PARITY.json',
          {'passed': True, 'rows': 4530, 'dimensions': 220, 'original_recording_blocks': 148,
           'cached_statistics_match_original_exactly': True, 'row_recording_mapping_verified': True,
           'source_files_modified': False, 'raw_video_or_HDF5_payloads_read': False,
           'sources': receipts})
    print('ORIGINAL_SENSOR_FEATURE_PARITY_PASS', len(seen), 'rows /220 features /148 original blocks', flush=True)


if __name__ == '__main__':main()
