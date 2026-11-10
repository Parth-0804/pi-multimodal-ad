import numpy as np
import pytest
from reassemble.additional_improvements.corruption_resume import atomic_npz_outputs


def test_atomic_bank_reuses_without_rewriting_and_rejects_difference(tmp_path):
    path=tmp_path/'bank.npz'
    data=dict(names=np.array(['one','two']),p=np.array([.2,np.nan]),rows=np.array([1,2]))
    original=np.savez_compressed
    with atomic_npz_outputs():
        np.savez_compressed(path,**data);before=path.read_bytes();mtime=path.stat().st_mtime_ns
        np.savez_compressed(path,**data)
        assert path.read_bytes()==before and path.stat().st_mtime_ns==mtime
        with pytest.raises(ValueError,match='values differ'):np.savez_compressed(path,**{**data,'rows':np.array([2,1])})
    assert np.savez_compressed is original
    assert not list(tmp_path.glob('*.pending.*'))


def test_uncommitted_partial_is_preserved_and_ignored(tmp_path):
    partial=tmp_path/'bank.npz.pending.interrupted';partial.write_bytes(b'partial')
    with atomic_npz_outputs():np.savez_compressed(tmp_path/'bank.npz',p=[.1,.9])
    assert partial.read_bytes()==b'partial'
    with np.load(tmp_path/'bank.npz') as z:assert np.array_equal(z['p'],[.1,.9])


def test_json_representation_resume_preserves_values_and_old_bytes(tmp_path):
    from reassemble.additional_improvements.common import write
    from reassemble.additional_improvements.corruption_resume import canonical_write
    path=tmp_path/'model.json';write(path,{'mean':[.1,.2],'revision':'fixed'})
    before=path.read_bytes();stamp=path.stat().st_mtime_ns
    # The original restart check fails even though serialized values are identical.
    with pytest.raises(AssertionError):write(path,{'mean':(.1,.2),'revision':'fixed'})
    canonical_write(path,{'mean':(.1,.2),'revision':'fixed'})
    assert path.read_bytes()==before and path.stat().st_mtime_ns==stamp
    with pytest.raises(AssertionError):canonical_write(path,{'mean':(.1,.3),'revision':'fixed'})


def test_external_stage_requires_recorded_completion_or_live_identity(tmp_path):
    from reassemble.additional_improvements.common import write
    from reassemble.additional_improvements.task4_external import ExternalVisual
    path=tmp_path/'receipt.json';write(path,{'pid':99999999})
    assert ExternalVisual(path).poll()==127
    write(path,{'pid':99999999,'returncode':0},replace=True)
    assert ExternalVisual(path).poll()==0
    write(path,{'pid':99999999,'returncode':75},replace=True)
    assert ExternalVisual(path).poll()==75
