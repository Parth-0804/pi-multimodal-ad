"""Small synthetic data-audit checks; no fitting or GPU access."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).parents[1]/'source'))
from full_lab_audit import (source_identity,sensor_gate,distinct_content,
                            split_feasibility,ambiguity_gate,COMMON_MTC,finite_dump)
from msm.data import binary_target
from frame_contract import select_frames


def table():
    return pd.DataFrame({'time':np.arange(0,4,.1),**{c:np.arange(40,dtype=float)+i for i,c in enumerate(COMMON_MTC)}})


def test_source_row_identity_and_native_labels(tmp_path):
    p=tmp_path/'label.csv';p.write_text('start,end,label\n1,2,2\n3,4,1\n')
    source_identity(p,2,2,1,2)
    with pytest.raises(ValueError):source_identity(p,2,1,1,2)
    with pytest.raises(ValueError):source_identity(p,3,1,1,2)


def test_half_open_sensor_interval_and_ninety_fixed_statistics():
    t=table();ok,features,gate=sensor_gate(t,1,2)
    assert ok and len(features)==90 and gate['rows']==10
    assert features[0]==pytest.approx(t.watt.iloc[10:20].mean())
    t.loc[t.time==2,'watt']=np.nan
    assert sensor_gate(t,1,2)[0] # end excluded


@pytest.mark.parametrize('change,reason',[
    ('finite','nonfinite_mtc_measurements'),('gap','mtc_time_gap_exceeds_0.5s'),
    ('rows','insufficient_mtc_rows'),('clock','invalid_mtc_clock'),('column','missing_mtc_channels:')])
def test_exact_sensor_failure_reasons(change,reason):
    t=table();start,end=1.,2.
    if change=='finite':t.loc[15,'watt']=np.nan
    if change=='gap':t=t.loc[~t.time.between(1.1,1.8)]
    if change=='rows':start,end=1.,1.3
    if change=='clock':t.loc[2,'time']=t.loc[1,'time']
    if change=='column':t=t.drop(columns=['watt'])
    ok,features,gate=sensor_gate(t,start,end)
    assert not ok and features is None and any(s.startswith(reason) for s in gate['reasons'])


def test_exact_sixteen_content_hashes_reject_duplicate_or_missing():
    pts=np.arange(300)/30
    selection=select_frames(pts,2,3,.25,.08,[[0,10]])
    hashes={j:str(j) for j in selection['indices']}
    assert distinct_content(selection.copy(),hashes)['accepted']
    hashes[selection['indices'][0]]=hashes[selection['indices'][1]]
    bad=distinct_content({**selection,'reasons':[]},hashes)
    assert not bad['accepted'] and bad['unique_decoded_content']==15


def test_both_label_definitions_preserve_native_meanings():
    native=np.array([0,1,2]);target,keep=binary_target(native,'stable_negative')
    assert target.tolist()==[0,1,0] and keep.tolist()==[True]*3
    t,k=binary_target(native,'exclude');assert t.tolist()==[0,1,0] and k.tolist()==[True,True,False]
    assert native.tolist()==[0,1,2]


def synthetic_groups():
    rows=[]
    for i in range(12):
        for native in [0,1]:rows.append({'group_id':f'm/d{i}','machine_date_group':f'm/date{i//2}',
            'calendar_date_group':f'date{i//2}','machine':'m','native_label':native,'target':native})
    return pd.DataFrame(rows)


def test_existing_nested_split_is_reproducible_and_reveals_date_overlap():
    frame=synthetic_groups();a=split_feasibility(frame,'group_id');b=split_feasibility(frame,'group_id')
    assert a==b and a['passed'] and not a['final_split_frozen']
    assert any(f['outer_related_date_overlaps']['machine_date_group'] for f in a['fold_summary'])
    strict=split_feasibility(frame,'machine_date_group')
    assert strict['passed']
    assert all(not f['outer_related_date_overlaps']['machine_date_group'] for f in strict['fold_summary'])


def test_insufficient_positive_groups_fail_without_changing_folds():
    frame=synthetic_groups();frame.loc[frame.group_id!='m/d0','target']=0
    result=split_feasibility(frame,'group_id')
    assert not result['passed'] and result['outer_folds']==3 and 'Insufficient' in result['reason']


def test_equal_audio_aliases_rejected_using_only_calibration_and_withheld_audio():
    rng=np.random.default_rng(99);reference=rng.normal(size=(3,6400))
    video=np.concatenate([reference,np.zeros((3,100)),reference],axis=1)
    result=ambiguity_gate(video,reference,{'accepted':True},{'local_window_s':8,'local_min_correlation':.75,
        'min_validation_anchors':3,'min_anchor_span_s':30})
    assert result['ambiguous']


def test_rejected_alignment_nonfinite_diagnostics_are_serialized_as_null(tmp_path):
    import json
    result={'accepted':False,'max_validation_residual_s':float('inf'),'reason':'insufficient_validation_support'}
    p=tmp_path/'complete.json';finite_dump(p,result)
    published=json.loads(p.read_text())
    assert not published['accepted'] and published['max_validation_residual_s'] is None
    # Aggregation must consume the same normalized representation as restart.
    finite_dump(tmp_path/'aggregate.json',{'mapping':published})
    assert json.loads((tmp_path/'aggregate.json').read_text())['mapping']==published
