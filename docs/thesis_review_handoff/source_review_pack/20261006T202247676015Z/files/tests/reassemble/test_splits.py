import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
import pandas as pd
import pytest
from reassemble.splits import nested_assignments,validate_predictor_fields

def test_nested_disjoint_and_each_recording_tested_once():
    rows=[{'recording_id':f'r{i:02d}','failure':label} for i in range(25) for label in [0,0,1]]
    manifest=nested_assignments(pd.DataFrame(rows));seen=[]
    for outer in manifest['folds']:
        assert not set(outer['train_recordings'])&set(outer['test_recordings'])
        seen+=outer['test_recordings']
        for inner in outer['inner']:
            assert not set(inner['train_recordings'])&set(inner['validation_recordings'])
            assert set(inner['train_recordings']+inner['validation_recordings'])==set(outer['train_recordings'])
    assert len(seen)==len(set(seen))==25
    assert manifest==nested_assignments(pd.DataFrame(rows))

def test_recording_support_not_segment_count():
    frame=pd.DataFrame([{'recording_id':str(i),'failure':j%2} for i in range(3) for j in range(100)])
    with pytest.raises(ValueError):nested_assignments(frame)

@pytest.mark.parametrize('bad',['text','recording_id','start','filename','segment_id','object_annotation','failure'])
def test_identity_annotation_label_blocked(bad):
    with pytest.raises(ValueError):validate_predictor_fields(['sensor',bad])

def test_valid_model_interface():
    validate_predictor_fields(['visual','sensor','audio','action','quality','availability'])
