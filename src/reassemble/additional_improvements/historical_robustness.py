"""Evaluate sealed clean checkpoints on new realized faults, without refitting."""
from pathlib import Path
import numpy as np
import torch
from reassemble.section1_features import cohort
from reassemble.section1_models import sigmoid
from reassemble.section2_data import quality_features
from reassemble.section3_evaluate import gate_predict
from .models import AnchoredAdjustment,modality_fallback
from .robust_fusion import pack
from .common import config,read,write,identity,progress

def main():
    c=config();torch.set_num_threads(1);root=Path(c['run_dir']);task=root/'04_corruption_training';base=read(c['section1_config']);c2=read(c['section2_config']);frame=cohort(base)
    quality,_,_=quality_features(frame,base,c2);actions=np.stack([(frame.action==a).to_numpy(np.float32) for a in c2['actions']],axis=1)
    with np.load(Path(c2['run_dir'])/'predictions/oof.npz') as z:original={k:z[k] for k in z.files}
    with np.load(root/'03_static_anchored_adaptation/predictions.npz') as z:task3={k:z[k] for k in z.files}
    for k in range(5):
        bank=pack(c,frame,quality,actions,f'outer{k}','test');rows=bank['rows'];v=len(bank['names']);f2=read(Path(c2['section1b_run'])/'stacking'/f'outer{k}.json')['stacker'];section2=read(Path(c2['run_dir'])/'predictions'/f'outer{k}.json')
        for label in ['HIST_F2','HIST_F6','TASK3_A']:
            dest=task/f'outer{k}_{label}.npz'
            if dest.exists():continue
            predictions=[];weights=[];sources=[]
            if label=='HIST_F2':
                probabilities=sigmoid(bank['p']@np.array(f2['coefficient'])+f2['intercept']);predictions=[probabilities];weights=[np.broadcast_to(np.array(f2['coefficient']),(*probabilities.shape,2)).copy()];threshold=f2['threshold'];expected=original['F2_p'][rows];expected_hard=original['F2_hard'][rows]
                sources=[identity(Path(c2['section1b_run'])/'stacking'/f'outer{k}.json')]
            elif label=='HIST_F6':
                for seed in range(3):
                    path=Path(c2['run_dir'])/'fits'/f'F6_outer{k}_final_s{seed}.pt';cp=torch.load(path,map_location='cpu',weights_only=True);ps=[];ws=[]
                    for i in range(v):
                        prob,w=gate_predict(cp,'F6',bank['p'][i],bank['u'][i,:,4:40],bank['u'][i,:,:4],bank['u'][i,:,-2:]);ps.append(prob);ws.append(w)
                    predictions.append(np.stack(ps));weights.append(np.stack(ws));sources.append(identity(path))
                threshold=section2['models']['F6']['threshold'];expected=original['F6_p'][rows];expected_hard=original['F6_hard'][rows]
            else:
                for seed in c['seeds']:
                    path=root/'03_static_anchored_adaptation/fits'/f'outer{k}_A-ADAPTIVE_refit_seed{seed}.pt';cp=torch.load(path,map_location='cpu',weights_only=True);model=AnchoredAdjustment(cp['coefficient'],cp['intercept']);model.load_state_dict(cp['state_dict']);model.eval();ps=[];ws=[]
                    for i in range(v):
                        context=bank['u'][i].copy();context[:,4:40]=np.nan_to_num((context[:,4:40]-cp['mean'].numpy())/cp['std'].numpy(),nan=0,posinf=0,neginf=0)
                        with torch.no_grad():raw,_,effective=model(torch.tensor(bank['p'][i],dtype=torch.float32),torch.tensor(context,dtype=torch.float32))
                        ps.append(sigmoid(raw.numpy()));ws.append(effective.numpy())
                    predictions.append(np.stack(ps));weights.append(np.stack(ws));sources.append(identity(path))
                threshold=read(root/'03_static_anchored_adaptation'/f'outer{k}.json')['models']['A-ADAPTIVE']['threshold'];expected=task3['A-ADAPTIVE_p'][rows];expected_hard=task3['A-ADAPTIVE_hard'][rows]
            seedp=np.stack(predictions).astype(float);seedhard=(seedp>=threshold).astype(float)
            for s in range(len(seedp)):
                for i in range(v):seedp[s,i],seedhard[s,i]=modality_fallback(seedp[s,i],seedhard[s,i],bank['p'][i],bank['branch_thresholds'],bank['u'][i,:,-2:])
            p=seedp.mean(0);hard=(p>=threshold).astype(float);difference=float(np.max(abs(p[0]-expected)));assert difference<1e-5,(label,k,difference)
            assert np.array_equal(hard[0],expected_hard),(label,k,'clean decision parity')
            p[0]=expected;hard[0]=expected_hard
            for i in range(v):p[i],hard[i]=modality_fallback(p[i],hard[i],bank['p'][i],bank['branch_thresholds'],bank['u'][i,:,-2:])
            np.savez_compressed(dest,rows=rows,names=bank['names'],p=p,hard=hard,seed_p=seedp,seed_hard=seedhard,weights=np.mean(weights,axis=0),seed_weights=np.stack(weights),branch_p=bank['p'],branch_thresholds=bank['branch_thresholds'])
            write(dest.with_suffix('.json'),dict(label=label,fold=k,threshold=threshold,source_checkpoints=sources,clean_max_abs=difference,output=identity(dest),training='none; sealed fitted checkpoint evaluated on new fault realizations'))
    progress(4,'Sealed F2/F6 and Task3 checkpoint references evaluated on identical new fault banks')

if __name__=='__main__':main()
