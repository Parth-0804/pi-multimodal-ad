import numpy as np
from vifailback import common,fusion,training
from vifailback.splits import plans


def test_real_meta_pipeline_uses_only_group_held_out_records(tmp_path,monkeypatch):
    c=common.config();c['seeds']=[42];c['run_id']='synthetic'
    rows=[{'episode_index':2*g+y,'canonical_task_id':g,'label':y} for g in range(33) for y in [0,1]]
    jobs=plans(rows,42)
    for module in [common,fusion,training]:monkeypatch.setattr(module,'PROJECT',tmp_path)
    monkeypatch.setattr(fusion,'finalize',lambda c:rows);monkeypatch.setattr(fusion,'prepare',lambda c:jobs)
    monkeypatch.setattr(fusion,'quality_matrix',lambda c,rs:{r['episode_index']:np.ones(11,dtype='float32') for r in rs})
    labels={r['episode_index']:r['label'] for r in rows}
    def records(c,condition,seed,job):
        return ([{'episode_index':e,'fit_id':job['id'],'label':labels[e],
                  'visual_probability':.2+.6*labels[e],'sensor_probability':.3+.4*labels[e]} for e in job['ids']['A']],
                {'visual':'synthetic','sensor':'synthetic'})
    monkeypatch.setattr(fusion,'paired_records',records)
    receipts=fusion.run(c,('V1',));assert len(receipts)==3
    assert all(r['group_safe_OOF_verified'] for r in receipts)
    for receipt in receipts:
        assert receipt['meta_rows']==44 and receipt['outer_rows']==22
    assert fusion.run(c,('V1',))==receipts
