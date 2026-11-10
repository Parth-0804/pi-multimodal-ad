"""Synthetic regression checks; no model fitting or authentic data relabeling."""
from pathlib import Path
import copy
import io
import json
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from select_pilot import phase_checks
import acquire_pilot


def annotation():
 return {'episode_type':'recovery','duration_frames':900,
  'phase_boundaries':{f'tau_{i}':i*180 for i in range(6)},
  'failure':{'originating_phase':2,'induced_at_frame':200,'recovery_started_at_frame':300}}


def test_valid_phase_record_does_not_need_silent_repair():
 issues,consistent=phase_checks(annotation(),900)
 assert issues==[] and consistent


@pytest.mark.parametrize('phase',[0,21])
def test_invalid_one_based_phase_is_recorded_not_corrected(phase):
 value=annotation();value['failure']['originating_phase']=phase
 before=copy.deepcopy(value);issues,_=phase_checks(value,900)
 assert 'originating_phase_outside_explicitly_tested_one_based_1_to_5' in issues
 assert value==before


def test_duration_boundary_and_event_order_defects_are_kept():
 value=annotation();value['duration_frames']=897;value['phase_boundaries']['tau_3']=100
 value['failure']['recovery_started_at_frame']=100
 issues,_=phase_checks(value,900)
 assert {'declared_duration_differs_from_released_episode_length','nonmonotonic_or_missing_phase_boundaries','invalid_induction_recovery_order_or_bounds'}<=set(issues)


def test_missing_boundaries_are_gated_without_crashing():
 value=annotation();value['phase_boundaries'].pop('tau_3');value['failure']['induced_at_frame']=None
 issues,consistent=phase_checks(value,900)
 assert 'nonmonotonic_or_missing_phase_boundaries' in issues and not consistent


def test_pilot_never_uses_collection_membership_as_binary_target():
 root=Path(__file__).resolve().parents[1]
 rows=json.loads((root/'00_dataset_overview/PILOT_SELECTION.json').read_text())
 assert len(rows)==10 and all(r['binary_target'] is None for r in rows)
 assert all('UNVERIFIED' in r['label_status'] or 'NO_VERIFIED' in r['label_status'] for r in rows)
 for r in rows:
  indices=np.rint(np.linspace(r['window_start_frame'],r['window_end_frame_exclusive']-1,16)).astype(int)
  assert len(np.unique(indices))==16 and indices.min()>=0


class Response(io.BytesIO):
 def __init__(self,data,status,content_range):super().__init__(data);self.status=status;self.headers={'Content-Range':content_range}


def test_range_projection_rejects_full_download_and_wrong_offsets(tmp_path,monkeypatch):
 monkeypatch.setattr(acquire_pilot,'REPO',tmp_path)
 reader=acquire_pilot.RangeFile('https://example.invalid/file.parquet',1000,tmp_path/'fragments')
 monkeypatch.setattr(acquire_pilot.urllib.request,'urlopen',lambda *a,**k:Response(b'abc',200,''))
 with pytest.raises(AssertionError,match='ignored byte Range'):reader.read(3)
 monkeypatch.setattr(acquire_pilot.urllib.request,'urlopen',lambda *a,**k:Response(b'abc',206,'bytes 7-9/1000'))
 with pytest.raises(AssertionError):reader.read(3)
 monkeypatch.setattr(acquire_pilot.urllib.request,'urlopen',lambda *a,**k:Response(b'abc',206,'bytes 0-2/1000'))
 assert reader.read(3)==b'abc' and reader.tell()==3 and reader.receipts[0]['bytes']==3
 reader.seek(0);assert reader.read(3)==b'abc' and reader.total_bytes==3
