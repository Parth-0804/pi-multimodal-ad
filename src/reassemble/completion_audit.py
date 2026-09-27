"""Final numerical, preservation and claim inventory audit; seal only after review."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import importlib.metadata
import json
import re
import subprocess
import sys
import numpy as np
import pandas as pd
import torch
from .completion_common import config,read,write,storage,progress
from .section1_features import cohort,sha
from .section1_report import metrics,METRICS

REPORTS=['SECTION_3_ROBUSTNESS_HANDOFF','MODALITY_DROPOUT_HANDOFF','AUDIO_FEASIBILITY_HANDOFF','EFFICIENCY_HANDOFF','OBJECT_GENERALIZATION_FEASIBILITY','FINAL_REASSEMBLE_HANDOFF','CROSS_STUDY_SYNTHESIS_HANDOFF','THESIS_STORYLINE_ADDENDUM','THESIS_FIGURE_INDEX','THESIS_TABLE_INDEX','FINAL_EVIDENCE_MAP']


def preservation(c):
    checks={}
    for key,name in [('section1','final_output_manifest.json'),('section1b','output_manifest.json'),('section2','output_manifest.json')]:
        manifest=Path(c[key])/name;items=read(manifest)['files']
        for item in items:
            path=Path(item['path']);assert path.stat().st_size==item['bytes'],str(path)
            assert sha(path)==item['sha256'],str(path)
        checks[str(manifest)]=len(items)
    protected=read('/tmp/phm_retirement_protected_before.json')
    for item in protected:
        st=Path(item['path']).lstat()
        assert (st.st_size,st.st_mtime_ns,st.st_mode)==(item['size'],item['mtime_ns'],item['mode']),item['path']
    records=pd.read_parquet('runs/reassemble/20260927T141645Z-inventory/recordings.parquet')
    for row in records.itertuples():
        p=Path(c['data_root'])/'raw/data'/row.filename;st=p.stat()
        assert (st.st_size,st.st_mtime_ns)==(row.size_bytes,row.mtime_ns),str(p)
    blob='284ccffbfe2b61f2abc91d97f5db0d0ee7abd628'
    assert int(subprocess.check_output(['git','cat-file','-s',blob]))==14047735808
    return {'prior_manifests':checks,'protected_metadata_unchanged':len(protected),'raw_metadata_unchanged':len(records),'historical_git_blob_retained':blob,'scope':'SHA256 prior evidence; lstat protected PHM/environment; size/mtime raw HDF5. Raw payloads were read-only; full raw rehash not repeated.'}


def audit(c):
    root=Path(c['runs']['final-synthesis']);spec=read('configs/reassemble/section3_corruptions.json');base=read('configs/reassemble/section1.json');frame=cohort(base)
    result={'preservation':preservation(c),'free_GiB':storage(),'timestamp_UTC':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    s3=Path(c['runs']['section3']);robust=read(s3/'results.json');drop=Path(c['runs']['modality-dropout']);dr=read(drop/'results.json')
    with np.load(Path(c['section2'])/'predictions/oof.npz') as z:clean={k:z[k] for k in z.files}
    assert len(frame)==4530 and frame.failure.sum()==509 and frame.recording_id.nunique()==148
    for k,g in frame.assign(fold=clean['fold']).groupby('recording_id'):assert g.fold.nunique()==1,k
    counts={};warnings=0
    for name in ['visual','sensor']:
        paths=sorted((s3/name).glob('*.npz'));assert len(paths)==148;counts[name]=len(paths)
        for p in paths:
            meta=read(p.with_suffix('.json'));assert sha(p)==meta['sha256']
            for key,value in meta.items():
                if key.startswith('clean_') and 'difference' in key:assert value<=5e-5,(str(p),key,value)
            warnings+=meta.get('expected_NaN_statistic_warnings',0)
    metric_checks=0
    for item in spec['conditions']:
        name,family=item['name'],item['family'];path=s3/'predictions'/(name+'.npz')
        assert sha(path)==read(path.with_suffix('.json'))['sha256']
        with np.load(path) as z:p={k:z[k] for k in z.files}
        assert np.array_equal(p['y'],frame.failure) and np.array_equal(p['fold'],clean['fold'])
        if family.startswith('V'):assert np.array_equal(p['U1_p'],clean['U1_p'])
        if family.startswith('S'):assert np.array_equal(p['U2_p'],clean['U2_p'])
        for m in spec['models']:
            values=robust['conditions'][name]['metrics'][m]
            if values is None:
                assert (family,m) in [('V4','U2'),('S5','U1')] and np.isnan(p[m+'_p']).all();continue
            point=metrics(p['y'],p[m+'_p'],p[m+'_hard']);expected=[values[key]['estimate'] for key in METRICS]
            assert np.allclose(point,expected,atol=1e-12,rtol=0),(name,m);metric_checks+=len(METRICS)
            if family=='clean':
                assert np.array_equal(p[m+'_p'],clean[m+'_p']) and np.array_equal(p[m+'_hard'],clean[m+'_hard'])
            if m in ['F5','F6']:
                assert np.allclose(p[m+'_weights'],p[m+'_seed_weights'].mean(0),atol=1e-12)
                assert np.allclose(p[m+'_weights'].sum(1),1,atol=2e-7)
                assert np.allclose(p[m+'_p'],p[m+'_seed_p'].mean(0),atol=1e-5,rtol=0)
            if m.startswith('F') and family in ['V4','S5']:
                branch='U1' if family=='V4' else 'U2';absent=0 if family=='V4' else 1
                assert np.array_equal(p[m+'_p'],p[branch+'_p']) and np.array_equal(p[m+'_hard'],p[branch+'_hard'])
                if m in ['F5','F6']:assert np.all(p[m+'_seed_weights'][:,:,absent]==0)
    fits=list((drop/'fits').glob('*.pt'));assert len(fits)==75
    split=read(base['splits'])
    mask_counts=np.zeros(3,dtype=int)
    for outer in split['folds']:
        k=outer['fold'];tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']))
        with np.load(Path(c['section1b'])/'stacking'/f'outer{k}.npz') as z:
            assert np.array_equal(z['train_rows'],tr) and np.array_equal(z['test_rows'],te)
        seen=[]
        for j in range(4):
            with np.load(Path(c['section2'])/'inputs'/f'outer{k}_inner{j}.npz') as z:
                it=z['train_rows'];iv=z['validation_rows'];seen.extend(iv.tolist())
            assert not set(frame.recording_id.iloc[it])&set(frame.recording_id.iloc[iv]);assert set(it)|set(iv)==set(tr)
            for s in range(3):
                cp=torch.load(drop/'fits'/f'outer{k}_inner{j}_s{s}.pt',weights_only=True,map_location='cpu')
                assert sum(cp['mask_counts'])==len(it)*cp['settings']['epochs'];mask_counts+=cp['mask_counts']
        assert sorted(seen)==tr.tolist()
        for s in range(3):
            cp=torch.load(drop/'fits'/f'outer{k}_final_s{s}.pt',weights_only=True,map_location='cpu')
            assert sum(cp['mask_counts'])==len(tr)*cp['settings']['epochs'];mask_counts+=cp['mask_counts']
    for name in spec['dropout']['test_conditions']:
        with np.load(drop/'predictions'/(name+'.npz')) as z:p={k:z[k] for k in z.files}
        assert np.array_equal(p['y'],clean['y']) and np.array_equal(p['fold'],clean['fold'])
        assert np.allclose(p['p'],p['seed_p'].mean(0),atol=1e-6)
        assert np.allclose(metrics(p['y'],p['p'],p['hard']),[dr['conditions'][name]['metrics'][m]['estimate'] for m in METRICS],atol=1e-12,rtol=0);metric_checks+=8
        if name in ['V4','S5']:
            with np.load(s3/'predictions'/(name+'.npz')) as z:assert np.array_equal(p['p'],z['F6_p']) and np.array_equal(p['hard'],z['F6_hard'])
    final=read(root/'results.json');trace=read(root/'metric_traceability.json');assert final['master_clean']==trace['master_clean_rows']
    for row in final['master_clean']:
        if row['AUROC'] is None:continue
        data=read(row['source'])
        for key in row['source_key'].split('.'):data=data[key]
        for m in METRICS:
            for suffix,key in [('', 'estimate'),('_lower_95','lower_95'),('_upper_95','upper_95')]:assert row[m+suffix]==data[m][key];metric_checks+=1
    index=read(root/'figure_index.json');assert len(index)==14
    for fig in index:
        for p in fig['outputs']:assert Path(p).stat().st_size>1000,p
        for p in fig['sources']:assert Path(p).exists(),p
    reportpaths=[Path('artifacts/reassemble/reports')/(name+'.md') for name in REPORTS]
    for p in reportpaths:assert p.stat().st_size>200,p
    handoff=reportpaths[5].read_text()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':assert '\n## '+letter+'. ' in handoff,letter
    story=Path('artifacts/reassemble/reports/THESIS_STORYLINE_ADDENDUM.md').read_text()
    for field in ['ASSUMPTION','QUESTION','METHOD','RESULT','INTERPRETATION','STATUS','CONSEQUENCE']:assert field in story,field
    claims=[];terms=['proves','optimal','best in general','robust','process-aware','reliability-aware','significant','ground truth','real-time','generalizes']
    for path in reportpaths:
        for line,text in enumerate(path.read_text().splitlines(),1):
            found=[t for t in terms if t in text.lower()]
            if found:claims.append({'path':str(path),'line':line,'terms':found,'text':text,'review':'PENDING: scope, negation and direct evidence to be inspected'})
    write(root/'claim_inventory.json',claims)
    checks={}
    for name,cmd in [('pytest',[sys.executable,'-B','-m','pytest','tests/reassemble','-q']),('pip_check',[sys.executable,'-B','-m','pip','check']),('git_diff_check',['git','diff','--check'])]:
        done=subprocess.run(cmd,text=True,capture_output=True);checks[name]={'command':cmd,'exit_code':done.returncode,'stdout':done.stdout,'stderr':done.stderr};assert done.returncode==0,checks[name]
    result.update({'checks':checks,'extraction_counts':counts,'expected_dropout_NaN_warnings':warnings,'metric_source_equalities':metric_checks,'dropout_checkpoints':len(fits),'dropout_training_mask_counts':mask_counts.tolist(),'figures':len(index),'required_reports':len(reportpaths),'claim_inventory_entries':len(claims),'claim_review':'pending independent narrative inspection before seal','scientific_validation':'passed'})
    write(root/'validation.json',result)
    progress('All numerical/preservation checks passed; final claim and figure review before sealing')


def seal(c):
    root=Path(c['runs']['final-synthesis']);validation=read(root/'validation.json');review=read(root/'claim_review.json')
    assert validation['scientific_validation']=='passed' and review['status']=='passed'
    final=read(root/'results.json');preserved=preservation(c);storage()
    reports=Path('artifacts/reassemble/reports');status='REASSEMBLE STUDY COMPLETE\n\n'
    status+='All authorized core phases are finished; audio and physical-object modelling have completed feasibility exclusions. No core experiment is pending.\n\n'
    context=read(root/'synthesis_context.json')
    summaries=[('Strongest unimodal representation','Engineered sensor statistics; PatchTST remains a bounded negative architecture result.'),('Clean fusion','SIMPLE FUSION SUFFICIENT; learned static F2 is the primary reference, with uniform fusion a simple alternative.'),('Robustness',context['robustness_answer']),('Modality dropout',context['dropout_answer']),('Audio',final['audio_decision']+'; AST/tri-modal modelling intentionally excluded.'),('SQ1',final['SQ']['SQ1']),('SQ2',final['SQ']['SQ2']),('SQ3',final['SQ']['SQ3']),('SQ4',final['SQ']['SQ4']),('Main RQ',context['main_RQ']),('Main limitations','Adaptive reuse of the same cohort/folds, recording/scene/day/object dependence, artificial single-realization corruptions, retrospective classification, unverified audio timing and VM-specific timing. '+final['object_decision']+' for physical-object OOD.'),('Optional future work only','Independent cohort/site evaluation, trustworthy audio anchors, reliable object identity, and any new architecture under a fresh preregistration. No further tuning is required to complete this study.')]
    for i,(name,value) in enumerate(summaries,1):status+=f'{i}. **{name}:** '+value+'\n'
    status+='\nValidation: all numerical/source, preservation, test, dependency and claim checks passed. Evidence: `'+str(root/'validation.json')+'`; main handoff: `artifacts/reassemble/reports/FINAL_REASSEMBLE_HANDOFF.md`; figures/tables: `'+str(root)+'`. Configuration: `configs/reassemble/completion.json`.\n'
    write(root/'seal.json',{'timestamp_UTC':datetime.now(timezone.utc).isoformat(),'preservation':preserved,'claim_review':review,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'status':'complete'})
    with (reports/'REASSEMBLE_COMPLETION_STATUS.md').open('x') as f:f.write(status)
    Path('docs/reassemble/AUTONOMOUS_CONTINUATION.md').write_text('# REASSEMBLE — completed handoff\n\n'+status+'\nNo worker should be restarted. Final audit is sealed. Historical evidence and raw data are unchanged. All source implementations are under `src/reassemble/`; scripts 12–22 implement this completion sequence.\n')
    sources=list(Path('src/reassemble').glob('*.py'))+list(Path('scripts/reassemble').glob('*.py'))+[Path('configs/reassemble/completion.json'),Path('configs/reassemble/section3_corruptions.json'),Path('docs/reassemble/SECTION_3_CORRUPTION_PROTOCOL.md')]
    for phase,folder in c['runs'].items():
        folder=Path(folder);paths=[p for p in folder.rglob('*') if p.is_file() and p.name!='output_manifest.json' and p.suffix not in ['.lock','.log']]
        if phase=='final-synthesis':paths += sources+[reports/(n+'.md') for n in REPORTS]+[reports/'REASSEMBLE_COMPLETION_STATUS.md',Path('docs/reassemble/AUTONOMOUS_CONTINUATION.md')]
        items=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths))]
        write(folder/'output_manifest.json',{'scope':'Completed phase evidence; excludes mutable execution logs, locks and manifest itself; bulk numerical arrays remain ignored by Git','files':items})
    print('REASSEMBLE STUDY COMPLETE',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seal',action='store_true');args=parser.parse_args();c=config()
    seal(c) if args.seal else audit(c)

if __name__=='__main__':main()
