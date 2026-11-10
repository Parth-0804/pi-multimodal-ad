import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
import numpy as np
import pytest
from reassemble.alignment import action_from_text, interval_coverage, resample_progress, timestamps_1d, sensor_quality
from reassemble.acquire import safe_members
import zipfile

@pytest.mark.parametrize('text,action', [('Pick up the gear','pick'),('Inserting peg','insert'),('Remove shaft','remove'),('Placing object','place'),('', 'other'),('Do not pick','other')])
def test_action_is_restricted(text,action):
    assert action_from_text(text)==action

def test_no_future_or_endpoint_extrapolation():
    t=np.array([0.,1.,2.,3.]);x=np.array([999.,1.,2.,999.])
    actual=resample_progress(t,x,.5,2.5,5)[:,0]
    np.testing.assert_allclose(actual,[np.nan,1.,1.5,2.,np.nan],equal_nan=True)

def test_gap_not_counted_as_coverage():
    t=np.r_[np.arange(0.,1.,.1),np.arange(9.,10.1,.1)]
    assert interval_coverage(t,0,10)['coverage']<.21
    out=resample_progress(t,t,0,10,11)
    assert np.isnan(out[5,0])

def test_timestamp_columns_must_agree():
    with pytest.raises(ValueError):timestamps_1d([[1,2],[3,4]])
    with pytest.raises(ValueError):timestamps_1d([1,1,2])
    np.testing.assert_equal(timestamps_1d([[1,1],[2,2]]),[1,2])

def test_quality_detects_missing_constant():
    t=np.linspace(0,1,20);x=np.stack([t,np.ones(20),np.full(20,np.nan)],axis=1)
    q=sensor_quality(t,x,0,1)
    assert q['missing_channels']==1 and q['constant_channels']==1
    assert q['clipping_fraction'] is None

@pytest.mark.parametrize('name',['../escape','/absolute','folder/../../escape','folder\\escape'])
def test_zip_traversal_rejected(tmp_path,name):
    p=tmp_path/'synthetic.zip'
    with zipfile.ZipFile(p,'w') as z:z.writestr(name,b'fake')
    with zipfile.ZipFile(p) as z:
        with pytest.raises(ValueError):list(safe_members(z))
