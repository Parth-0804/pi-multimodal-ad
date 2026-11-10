"""Frozen clean-trained predictions under the preregistered test-time conditions."""
from pathlib import Path
import numpy as np
import torch
import joblib
from threadpoolctl import threadpool_limits
from .completion_common import config,read,write,storage,progress
from .section1_features import cohort,sha
from .section1_models import VisualHead,sigmoid
from .section2_data import quality_features
from .section2_models import DecisionGate,context,logit
from .section3_sensor import sensor_probability


def gate_predict(checkpoint,kind,probabilities,quality,action,availability):
    params=checkpoint['normalizers']['quality'];mean=np.asarray(params['mean'],dtype='float32');std=np.asarray(params['std'],dtype='float32')
    q=quality.copy()
    q[availability[:,0]==0,:6]=mean[:6];q[availability[:,1]==0,6:]=mean[6:]
    q=np.nan_to_num((q-mean)/std,nan=0,posinf=0,neginf=0).astype('float32')
    values=context(kind,action,q,availability)
    model=DecisionGate(values.shape[1],checkpoint['settings']['hidden']);model.load_state_dict(checkpoint['state_dict']);model.eval()
    with torch.inference_mode():
        raw,w=model(torch.from_numpy(values),torch.from_numpy(logit(probabilities)),torch.from_numpy(availability.astype('float32')))
    p=sigmoid(raw.numpy());weights=w.numpy()
    for absent,remaining in [(0,1),(1,0)]:
        rows=availability[:,absent]==0
        # Availability is an exact fallback, not a numerically different surrogate.
        if rows.any():
            assert np.all(weights[rows,absent]==0) and np.all(weights[rows,remaining]==1)
            assert np.allclose(p[rows],probabilities[rows,remaining],atol=1e-6)
            p=p.astype('float64');p[rows]=probabilities[rows,remaining]
    return p,weights


def extract_arrays(folder,key,n,width):
    paths=sorted(Path(folder).glob('*.npz'));assert len(paths)==148,('Incomplete extraction',str(folder),len(paths))
    arrays={};quality={};seen=[]
    for path in paths:
        assert sha(path)==read(path.with_suffix('.json'))['sha256']
        with np.load(path) as z:
            ix=z['row_index'];seen.extend(ix.tolist())
            for i,name in enumerate(z['names']):
                name=str(name)
                if name not in arrays:arrays[name]=np.zeros((n,width),dtype='float32');quality[name]=np.zeros((n,z['quality'].shape[-1]),dtype='float32')
                arrays[name][ix]=z[key][i];quality[name][ix]=z['quality'][i]
    assert sorted(seen)==list(range(n))
    return arrays,quality


def main():
    c=config();s=read('configs/reassemble/section3_corruptions.json');base=read('configs/reassemble/section1.json');c2=read('configs/reassemble/section2.json')
    root=Path(s['run_dir']);out=root/'predictions';out.mkdir(exist_ok=True);storage();torch.set_num_threads(4)
    frame=cohort(base);n=len(frame);clean_quality,_,_=quality_features(frame,base,c2);actions=np.stack([(frame.action==a).to_numpy(dtype='float32') for a in c2['actions']],axis=1)
    with np.load(Path(c['section2'])/'predictions/oof.npz') as z:clean={k:z[k] for k in z.files}
    visual,vq=extract_arrays(root/'visual','features',n,896);sensor,sq=extract_arrays(root/'sensor','statistics',n,220)
    heads={};scalers={};sensor_models={};gates={};metadata={};static={};branch_cal={}
    for k in range(5):
        checkpoint=torch.load(Path(c['section1'])/'checkpoints'/f'rtdetr_fold{k}.pt',map_location='cpu',weights_only=True)
        head=VisualHead(checkpoint['width'],base);head.load_state_dict(checkpoint['state_dict']);head.eval();heads[k]=head
        scalers[k]=(checkpoint['normalizer_mean'].numpy(),checkpoint['normalizer_std'].numpy())
        sensor_models[k]=joblib.load(root/'branches'/f'sensor_fold{k}.joblib')
        metadata[k]=read(Path(c['section2'])/'predictions'/f'outer{k}.json')
        static[k]=read(Path(c['section1b'])/'stacking'/f'outer{k}.json')['stacker']
        branch_cal[k]={kind:read(Path(c['section1'])/'predictions'/f'{kind}_perm00_fold{k}.json')['calibration'] for kind in ['rtdetr','sensor_statistics']}
        for kind in ['F5','F6']:
            for seed in range(3):gates[k,kind,seed]=torch.load(Path(c['section2'])/'fits'/f'{kind}_outer{k}_final_s{seed}.pt',map_location='cpu',weights_only=True)
    for condition in s['conditions']:
        name,family=condition['name'],condition['family'];path=out/(name+'.npz')
        if path.exists():continue
        probabilities=np.column_stack([clean['U2_p'],clean['U1_p']]);quality=clean_quality.copy();availability=np.ones((n,2),dtype='float32')
        if family in ['V1','V2','V3']:quality[:,:6]=vq[name]
        if family in ['S1','S2','S3','S4']:quality[:,6:]=sq[name]
        if family=='V4':availability[:,0]=0;probabilities[:,0]=.5
        if family=='S5':availability[:,1]=0;probabilities[:,1]=.5
        for k in range(5):
            ix=np.flatnonzero(clean['fold']==k)
            if family in ['V1','V2','V3']:
                mean,std=scalers[k];x=np.nan_to_num((visual[name][ix]-mean)/std,nan=0,posinf=0,neginf=0).astype('float32')
                with torch.inference_mode():raw=heads[k](torch.from_numpy(x))[0].numpy()
                cal=branch_cal[k]['rtdetr'];probabilities[ix,0]=sigmoid(raw*cal['coefficient']+cal['intercept'])
            if family in ['S1','S2','S3','S4']:
                probabilities[ix,1]=sensor_probability(sensor_models[k],sensor[name][ix])
        result={'y':clean['y'],'fold':clean['fold'],'branch_probabilities':probabilities,'quality':quality,'availability':availability}
        for kind in s['models']:
            p=np.full(n,np.nan);hard=np.full(n,np.nan);weights=np.full((3,n,2),np.nan);seed_p=np.full((3,n),np.nan)
            for k in range(5):
                ix=np.flatnonzero(clean['fold']==k);probs=probabilities[ix];mask=availability[ix]
                if kind in ['U1','U2']:
                    col=1 if kind=='U1' else 0
                    if not mask[:,col].any():continue
                    p[ix]=probs[:,col];threshold=branch_cal[k]['sensor_statistics' if kind=='U1' else 'rtdetr']['threshold']
                elif kind=='F1':p[ix]=(probs*mask).sum(1)/mask.sum(1);threshold=metadata[k]['uniform_threshold']
                elif kind=='F2':p[ix]=sigmoid(probs@np.asarray(static[k]['coefficient'])+static[k]['intercept']);threshold=static[k]['threshold']
                else:
                    for seed in range(3):
                        seed_p[seed,ix],weights[seed,ix]=gate_predict(gates[k,kind,seed],kind,probs,quality[ix],actions[ix],mask)
                    p[ix]=seed_p[:,ix].mean(0);threshold=metadata[k]['models'][kind]['threshold']
                if kind not in ['U1','U2'] and family in ['V4','S5']:
                    col=1 if family=='V4' else 0;p[ix]=probs[:,col]
                    threshold=branch_cal[k]['sensor_statistics' if col==1 else 'rtdetr']['threshold']
                hard[ix]=p[ix]>=threshold
            if family=='clean':
                assert np.allclose(p,clean[kind+'_p'],atol=1e-5,rtol=0),('clean model parity',kind,np.max(abs(p-clean[kind+'_p'])))
                assert np.array_equal(hard,clean[kind+'_hard']),('clean threshold parity',kind)
                p=clean[kind+'_p'].copy();hard=clean[kind+'_hard'].copy()
            result[kind+'_p']=p;result[kind+'_hard']=hard
            if kind in ['F5','F6']:
                result[kind+'_seed_p']=seed_p;result[kind+'_seed_weights']=weights;result[kind+'_weights']=weights.mean(0)
        np.savez_compressed(path,**result)
        write(path.with_suffix('.json'),{'condition':condition,'sha256':sha(path),'unavailable_unimodal':'U2' if family=='V4' else 'U1' if family=='S5' else None})
        progress('Section 3 frozen predictions complete: '+name)
    progress('Section 3 all single-modality predictions complete')

if __name__=='__main__':
    with threadpool_limits(limits=4,user_api='blas'):main()
