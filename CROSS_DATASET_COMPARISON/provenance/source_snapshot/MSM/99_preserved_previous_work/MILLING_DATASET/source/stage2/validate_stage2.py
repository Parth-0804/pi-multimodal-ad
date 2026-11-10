#!/usr/bin/env python3
"""Independently verify the final cohort, preservation, provenance, and deliverables."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
import pandas as pd

from audit_sensors import COMMON_MTC,dump


def sha(path):
    d=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):d.update(chunk)
    return d.hexdigest()


def main(run):
    cfg=json.loads((run/'config/resolved_config.json').read_text());acquisition=Path(cfg['acquisition_run']);raw=Path(cfg['data_root'])
    for filename in ('protected_stage1_sha256.json','exploratory_run_sha256.json'):
        hashes=json.loads((run/'evidence'/filename).read_text())
        assert all(sha(Path(p))==digest for p,digest in hashes.items()),filename
    receipts=[acquisition/'evidence/download_receipt.json',*sorted((acquisition/'evidence').glob('_msm_download_receipt_*.json'))]
    assert len(receipts)==3
    inputs={}
    for receipt in receipts:
        r=json.loads(receipt.read_text());assert r['failures']==0 and r['handle']==cfg['handle']
        for f in r['results']:
            path=raw/f['path'];assert path.stat().st_size==f['bytes'] and sha(path)==f['sha256']
            inputs[f['path']]={'dataset_relative_path':f['path'],'path':str(path),'bytes':f['bytes'],'sha256':f['sha256'],'acquisition_status':f['status']}
    assert len(inputs)==41
    assert sum(f['bytes'] for f in inputs.values() if f['acquisition_status']=='downloaded')==1196411398
    assert sum(f['acquisition_status']=='downloaded' for f in inputs.values())==35
    dump(run/'manifests/input_manifest.json',list(inputs.values()))
    p=pd.read_csv(run/'MSM_PILOT_SAMPLE_MANIFEST.csv');frames=pd.read_csv(run/'manifests/selected_frame_manifest.csv')
    mappings=json.loads((run/'manifests/video_alignment_final.json').read_text());summary=json.loads((run/'manifests/pilot_summary.json').read_text())
    assert len(p)==127 and p.verified_multimodal_example.sum()==114 and p.frame_contract_pass.sum()==116
    assert p[p.verified_multimodal_example].native_label.value_counts().to_dict()=={0:93,2:11,1:10}
    assert p.separate_video_acc_contract_pass.sum()==39 and len(frames)==116*16
    assert len(p[p.verified_multimodal_example & (p.native_label==1)].group_id.unique())==2
    all_mtc={g:pd.read_csv(next((raw/g).glob('*_mtc.csv'))) for g in cfg['selected_groups']}
    features=pd.read_csv(run/'manifests/common_mtc_statistics.csv').set_index('interval_id')
    assert features.shape==(114,92) # group + native label + 90 actual numerical statistics
    max_stat_error=0.
    for _,row in p.iterrows():
        labels=pd.read_csv(raw/row.group_id/'label.csv');native=labels.iloc[int(row.source_row)-2]
        assert abs(native.start-row.start_s)<1e-9 and abs(native.end-row.end_s)<1e-9 and native.label==row.native_label
        source=all_mtc[row.group_id];inside=source[(source.time>=row.start_s)&(source.time<row.end_s)]
        gap=float(np.diff(np.r_[row.start_s,inside.time.to_numpy(),row.end_s]).max())
        sensor_ok=all(c in inside.columns for c in COMMON_MTC) and len(inside)>=5 and gap<=.5
        assert sensor_ok==bool(row.common_mtc_sensor_gate_pass)
        assert bool(row.verified_multimodal_example)==(bool(row.frame_contract_pass) and sensor_ok)
        if row.frame_contract_pass:
            f=frames[frames.interval_id==row.interval_id].sort_values('frame_order');assert len(f)==16
            assert f.native_frame_index.nunique()==16 and f.decoded_frame_sha256.nunique()==16
            assert np.all(np.diff(f.video_pts_s)>0)
            assert np.all(f.mapped_sensor_time_s-row.alignment_uncertainty_s>=row.start_s-1e-10)
            assert np.all(f.mapped_sensor_time_s+row.alignment_uncertainty_s<row.end_s+1e-10)
            pts=np.load(run/'cache'/(row.group_id.replace('/','_')+'_native_pts.npy'))
            assert np.allclose(pts[f.native_frame_index.astype(int)],f.video_pts_s,atol=1e-9)
        if row.verified_multimodal_example:
            vector=features.loc[row.interval_id]
            for c in COMMON_MTC:
                y=inside[c].to_numpy(dtype=float);assert np.isfinite(y).all()
                stats={'mean':y.mean(),'std':y.std(ddof=0),'rms':np.sqrt(np.mean(y*y)),'min':y.min(),'max':y.max(),'peak_to_peak':np.ptp(y)}
                for stat,value in stats.items():
                    error=abs(float(vector[c+'__'+stat])-value);max_stat_error=max(max_stat_error,error)
                    assert np.isclose(float(vector[c+'__'+stat]),value,rtol=1e-7,atol=.002),(row.interval_id,c,stat,error)
    for g,m in mappings.items():
        if not m['accepted']:continue
        assert m['coarse_score_kind']=='calibration_template_consensus'
        assert m['calibration_anchors']>=3 and m['validation_anchors']>=3
    assert abs(mappings['imi_vmx30ui/dataset9']['offset_s']-49.73)<1e-10
    assert mappings['imi_vmx30ui/dataset9']['uncertainty_s']==.1
    for e in json.loads((run/'manifests/diagnostic_examples.json').read_text()):
        assert (run/e['figure']).exists() and e['tensor_shape']==[16,3,224,224] and e['all_native_hashes_match']
    for report in run.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',report.read_text()):
            if not target.startswith(('https://','http://','#')):assert (run/target).exists(),target
    assert '26 passed' in (run/'logs/all_msm_tests.log').read_text()
    assert 'FAILED' in (acquisition/'logs/partial_overlap_regression_before.log').read_text()
    assert '6 passed' in (run/'logs/frame_regression_after.log').read_text()
    assert 'No broken requirements found.' in (run/'logs/pip_check.log').read_text()
    assert subprocess.run(['git','diff','--check']).returncode==0
    assert not subprocess.check_output(['git','ls-files','--',str(raw)],text=True).strip()
    assert all(subprocess.run(['git','check-ignore','-q',f['path']]).returncode==0 for f in inputs.values())
    assert all(subprocess.run(['git','check-ignore','-q',str(f)]).returncode==0 for f in (run/'figures').rglob('*') if f.is_file())
    source=Path('MILLING DATASET/source');tests=Path('MILLING DATASET/tests')
    for f in [*source.rglob('*.py'),*tests.glob('*.py')]:ast.parse(f.read_text(encoding='utf-8-sig'),filename=str(f))
    validation={'validated_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','tests':'26 passed',
        'partial_overlap_regression':'failing before / passing after','raw_input_hashes_match_receipts':True,
        'stage1_and_exploratory_evidence_preserved':True,'primary_examples':114,'primary_class_counts':{0:93,1:10,2:11},
        'primary_exclusions':13,'frame_eligible_intervals':116,'native_sampled_frames_checked':1856,
        'separate_video_acc_examples':39,'primary_positive_groups':2,'independent_mtc_statistic_max_absolute_error':max_stat_error,
        'native_label_association_and_frame_order_verified':True,'source_ast':'passed','pip_check':'passed','git_diff_check':'passed',
        'raw_and_generated_media_ignored':True,'model_training_performed':False,
        'remaining_limits':['coarse context visibility only','no external camera timing fiducial','unknown internal MTC aggregation latency','physical experiment independence unresolved','only two positive pilot groups'],
        'next_action':'Stop for researcher review; do not train or download additional data'}
    dump(run/'validation.json',validation)
    sys.path.insert(0,str(Path('MILLING DATASET/.tools')))
    import imageio_ffmpeg
    versions={}
    for name in ('numpy','pandas','scipy','matplotlib','Pillow','opencv-python','soundfile','pytest','imageio-ffmpeg'):
        versions[name]=importlib.metadata.version(name)
    dump(run/'provenance.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'git_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),'python':platform.python_version(),'packages':versions,
        'ffmpeg_version':imageio_ffmpeg.get_ffmpeg_version(),'ffmpeg_binary_sha256':sha(Path(imageio_ffmpeg.get_ffmpeg_exe())),
        'source_sha256':{str(f):sha(f) for f in source.rglob('*.py')},'test_sha256':{str(f):sha(f) for f in tests.glob('*.py')},
        'resolved_config':str(run/'config/resolved_config.json'),'acquisition_run':str(acquisition),'analysis_revision':2,
        'storage_free_bytes_after':shutil.disk_usage(run).free,'duplicate_policy':'preserve raw and source rows; report repeated video content; never pad selected frames',
        'methodology':'calibration_consensus_v2; native cutting intervals; fixed shared-MTC statistics; separate raw-ACC contract','training':False})
    (run/'evidence/git_status_after.txt').write_text(subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'],text=True))
    (run/'evidence/git_diff_stat.txt').write_text(subprocess.check_output(['git','diff','--stat'],text=True))
    print(json.dumps(validation,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);main(p.parse_args().run)
