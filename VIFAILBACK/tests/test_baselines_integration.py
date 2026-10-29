import numpy as np
from vifailback import baselines,common
from vifailback.splits import plans


def test_native_methods_pipeline_fits_T_selects_V_calibrates_C_and_predicts_A(tmp_path,monkeypatch):
    c=common.config();c['seeds']=[42];c['run_id']='synthetic'
    rows=[{'episode_index':2*g+y,'canonical_task_id':g,'label':y} for g in range(33) for y in [0,1]]
    file=tmp_path/'features.npz';rng=np.random.default_rng(42)
    np.savez(file,episode_ids=np.arange(66),features=rng.normal(size=(66,280)).astype('float32'))
    receipt={'path':str(file),'sha256':common.sha(file)}
    monkeypatch.setattr(common,'PROJECT',tmp_path);monkeypatch.setattr(baselines,'PROJECT',tmp_path)
    monkeypatch.setattr(baselines,'finalize',lambda c:rows)
    monkeypatch.setattr(baselines,'prepare_splits',lambda c:plans(rows,42))
    monkeypatch.setattr(baselines,'prepare_sensors',lambda c:receipt)
    result=baselines.run(c);assert len(result)==12 and all(r['S1_equals_S3'] for r in result)
    assert result==baselines.run(c)
