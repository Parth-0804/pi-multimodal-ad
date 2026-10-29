import os
from types import SimpleNamespace
from vifailback import resources
from vifailback.common import sha


def test_gpu_waits_for_verified_whole_study_not_a_between_fit_gap(tmp_path,monkeypatch):
    c={'reassemble_status':str(tmp_path/'PHASE1_C_ONLY_STATUS.json')}
    assert resources.gpu_state(c)['reason']=='SOURCE_STUDY_NOT_COMPLETE'
    metric=tmp_path/'PHASE1_C_ONLY_FINAL_METRICS.json';metric.write_text('{}')
    marker=tmp_path/'PHASE1_C_ONLY_ALL_COMPLETE.json'
    import json
    marker.write_text(json.dumps({'status':'COMPLETE','C_fits':75,'epochs_each':20,'metrics_sha256':'incorrect'}))
    assert resources.gpu_state(c)['reason']=='SOURCE_TERMINAL_IDENTITY_MISMATCH'
    marker.write_text(json.dumps({'status':'COMPLETE','C_fits':75,'epochs_each':20,'metrics_sha256':sha(metric)}))
    monkeypatch.setattr(resources.subprocess,'run',lambda *a,**kw:SimpleNamespace(stdout=f'{os.getpid()}\n999999\n'))
    assert resources.gpu_state(c)['reason']=='OTHER_GPU_WORK_ACTIVE'
    monkeypatch.setattr(resources.subprocess,'run',lambda *a,**kw:SimpleNamespace(stdout=f'{os.getpid()}\n'))
    assert resources.gpu_state(c)['gpu_idle']
