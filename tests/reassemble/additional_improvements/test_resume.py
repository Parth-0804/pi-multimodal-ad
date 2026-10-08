import json
import hashlib
import numpy as np
import pytest
from reassemble.additional_improvements.resume_io import completed_hybrid_fold


def make_fold(root):
    tr, te = np.array([0, 1]), np.array([2, 3])
    np.savez(root/'hybrid_outer0.npz', train_rows=tr, test_rows=te, p=[.2,.8], hard=[0,1])
    (root/'hybrid_outer0.json').write_text(json.dumps({'fold':0,'threshold':.5}))
    return tr, te


def test_completed_fold_unchanged(tmp_path):
    tr,te=make_fold(tmp_path)
    before={p:(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for p in tmp_path.iterdir()}
    p,h=completed_hybrid_fold(tmp_path,0,tr,te)
    assert np.array_equal(p,[.2,.8]) and np.array_equal(h,[0,1])
    assert before=={p:(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for p in tmp_path.iterdir()}


def test_missing_and_partial_fold(tmp_path):
    assert completed_hybrid_fold(tmp_path,0,[0],[1]) is None
    (tmp_path/'hybrid_outer0.json').write_text('{}')
    with pytest.raises(ValueError,match='Incomplete'):
        completed_hybrid_fold(tmp_path,0,[0],[1])


def test_wrong_identity_and_decision(tmp_path):
    tr,te=make_fold(tmp_path)
    with pytest.raises(ValueError,match='identity/order'):
        completed_hybrid_fold(tmp_path,0,tr,te[::-1])
    (tmp_path/'hybrid_outer0.json').write_text(json.dumps({'fold':0,'threshold':.9}))
    with pytest.raises(ValueError,match='decisions'):
        completed_hybrid_fold(tmp_path,0,tr,te)


def test_daily_reset_deadline():
    from datetime import datetime, timezone
    from reassemble.additional_improvements.sensor_resume import pause_deadline, PlannedPause
    before=datetime(2026,9,28,3,49,tzinfo=timezone.utc)
    assert pause_deadline(before)==datetime(2026,9,28,3,50,tzinfo=timezone.utc)
    with pytest.raises(PlannedPause):
        pause_deadline(datetime(2026,9,28,4,0,tzinfo=timezone.utc))
    assert pause_deadline(datetime(2026,9,28,4,10,tzinfo=timezone.utc))==datetime(2026,9,29,3,50,tzinfo=timezone.utc)
    # Winter time: local 05:50 is 04:50 UTC.
    assert pause_deadline(datetime(2026,12,1,3,0,tzinfo=timezone.utc))==datetime(2026,12,1,4,50,tzinfo=timezone.utc)
