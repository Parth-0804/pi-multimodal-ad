import sys,io,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
import h5py
import numpy as np
import soundfile as sf
from reassemble.inventory import audit_recording
from reassemble.media import inspect_audio

def test_actual_schema_inventory_and_resume(tmp_path):
    path=tmp_path/'synthetic.h5'
    with h5py.File(path,'w') as f:
        g=f.create_group('segments_info/0')
        for key,value in {'start':0.,'end':1.,'success':False,'text':'Pick synthetic item'}.items():g[key]=value
        g.create_group('low_level/0')
        f['robot_state/measured_force']=np.ones((101,3))
        f['timestamps/measured_force']=np.linspace(0,1,101)
        f['events']=np.zeros((0,3))
    config={'primary_sensors':['measured_force'],'sensor_positions':512,'gap_multiple':5,'coverage_threshold':.9,'video_frames':16}
    task=(str(path),config,str(tmp_path/'run'),str(tmp_path/'cache'))
    output=audit_recording(task);data=json.loads(Path(output).read_text())
    assert data['recording']['segment_count']==1
    assert data['segments'][0]['failure']==1
    assert data['segments'][0]['action']=='pick'
    assert data['segments'][0]['sensor']['measured_force']['channels']==3
    before=Path(output).stat().st_mtime_ns
    assert audit_recording(task)==output
    assert Path(output).stat().st_mtime_ns==before

def test_audio_decoding_does_not_invent_alignment(tmp_path):
    buffer=io.BytesIO();sf.write(buffer,np.zeros(8000),8000,format='WAV')
    with h5py.File(tmp_path/'audio.h5','w') as f:
        f['audio']=np.frombuffer(buffer.getvalue(),dtype=np.uint8)
        meta,quality=inspect_audio(f['audio'],[{'segment_id':'s','start':.1,'end':.9}])
    assert meta['sample_rate']==8000
    assert quality['s']['nominal_coverage']==1
    assert quality['s']['silence_fraction']==1
    assert not quality['s']['usable']
    assert not meta['alignment_verified']


def test_explicit_per_sample_audio_timestamps_enable_alignment(tmp_path):
    buffer=io.BytesIO();sf.write(buffer,np.zeros(8000),8000,format='WAV')
    with h5py.File(tmp_path/'timed.h5','w') as f:
        f['audio']=np.frombuffer(buffer.getvalue(),dtype=np.uint8)
        meta,quality=inspect_audio(f['audio'],[{'segment_id':'s','start':10.1,'end':10.9}],10+np.arange(8000)/8000)
    assert meta['alignment_verified']
    assert quality['s']['usable']
    assert quality['s']['sample_count']<=6401


def test_video_uses_only_segment_indices_and_checks_frame_count(tmp_path):
    import cv2
    from reassemble.media import inspect_video
    path=tmp_path/'synthetic.avi'
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),20,(32,24))
    assert writer.isOpened()
    for i in range(40):writer.write(np.full((24,32,3),10 if 10<=i<=30 else 240,np.uint8))
    writer.release()
    with h5py.File(tmp_path/'video.h5','w') as f:
        f['video']=np.frombuffer(path.read_bytes(),dtype=np.uint8)
        meta,quality=inspect_video(f['video'],np.arange(40)/20,[{'segment_id':'s','start':.5,'end':1.5}],tmp_path/'cache'/'stream.mp4')
    assert meta['frame_count_matches']
    assert quality['s']['usable']
    assert quality['s']['mean_brightness']<.1


def test_official_integer_bytes_and_absolute_clock_origin(tmp_path):
    buffer=io.BytesIO();sf.write(buffer,np.zeros(8000),8000,format='WAV')
    with h5py.File(tmp_path/'absolute.h5','w') as f:
        f['audio']=np.frombuffer(buffer.getvalue(),dtype=np.uint8).astype(np.int64)
        meta,quality=inspect_audio(f['audio'],[{'segment_id':'s','start':1700000000.1,'end':1700000000.9}],time_origin=1700000000.)
    assert quality['s']['nominal_coverage']==1
    assert quality['s']['decodable']
    assert not quality['s']['usable']


def test_actual_audio_length_is_decoded_not_trusted_from_header():
    from reassemble.media import decoded_frame_count
    class OverstatedAudio:
        def __init__(self):self.position=0
        def __len__(self):return 100
        def read(self,n,**kwargs):
            result=np.zeros((max(0,10-self.position),1));self.position=10;return result
        def seek(self,n):self.position=n
    stream=OverstatedAudio()
    assert decoded_frame_count(stream)==10
    assert stream.position==0


def test_official_last_action_excludes_trailing_idle():
    from reassemble.audit_report import final_manipulation
    rows=[{'segment_id':'1','action':'insert','end':10.},{'segment_id':'2','action':'other','end':12.}]
    assert final_manipulation(rows)['segment_id']=='1'


def test_markdown_table_has_no_optional_dependency_and_escapes_cells():
    import pandas as pd
    from reassemble.audit_report import table
    text=table(pd.DataFrame({'item':['a|b\nc'],'n':[2]}))
    assert r'a\|b<br>c' in text
    assert '| item | n |' in text
