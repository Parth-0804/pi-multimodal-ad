"""One preregistered robust F6 variant; no corruption-based model selection."""
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from threadpoolctl import threadpool_limits
from .completion_common import config,read,write,storage,progress
from .section1_features import cohort
from .section1_models import Standardizer,sigmoid
from .section1b import choose_threshold
from .section2_models import DecisionGate,context,logit
from .section2_data import quality_features
from .section3_evaluate import gate_predict
from .cluster_metrics import draws,weighted_metrics,intervals
from .section1_report import metrics,METRICS,table


def fit_dropout(probabilities,quality,action,labels,test_probabilities,test_quality,test_action,settings,seed,path):
    if path.exists():
        checkpoint=torch.load(path,map_location='cpu',weights_only=True)
        p,_=gate_predict(checkpoint,'F6',test_probabilities,test_quality,test_action,np.ones((len(test_quality),2),dtype='float32'))
        return p,checkpoint
    started=time.perf_counter();torch.manual_seed(seed)
    scaler=Standardizer().fit(quality);q=scaler.transform(quality)
    tensor=lambda x:torch.as_tensor(x,dtype=torch.float32,device='cuda')
    quality_tensor=tensor(q);action_tensor=tensor(action);logits=tensor(logit(probabilities));target=tensor(labels)
    model=DecisionGate(action.shape[1]+quality.shape[1]+2,settings['hidden']).cuda()
    optimizer=torch.optim.AdamW(model.parameters(),lr=settings['lr'],weight_decay=settings['weight_decay'])
    generator=torch.Generator(device='cuda').manual_seed(seed)
    mask_generator=torch.Generator(device='cuda').manual_seed(seed+70000)
    losses=[];counts=np.zeros(3,dtype=int)
    for epoch in range(settings['epochs']):
        model.train();total=0.
        for ix in torch.randperm(len(labels),generator=generator,device='cuda').split(128):
            draw=torch.rand(len(ix),generator=mask_generator,device='cuda')
            availability=torch.ones((len(ix),2),device='cuda');availability[draw<.15,0]=0;availability[(draw>=.15)&(draw<.30),1]=0
            qm=quality_tensor[ix].clone();qm[availability[:,0]==0,:6]=0;qm[availability[:,1]==0,6:]=0
            values=torch.cat([action_tensor[ix],qm,availability],1)
            counts+=np.array([int((draw<.15).sum()),int(((draw>=.15)&(draw<.30)).sum()),int((draw>=.30).sum())])
            optimizer.zero_grad(set_to_none=True);raw,_=model(values,logits[ix],availability)
            loss=nn.functional.binary_cross_entropy_with_logits(raw,target[ix]);assert torch.isfinite(loss)
            loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step();total+=float(loss.detach())*len(ix)
        losses.append(total/len(labels))
    checkpoint={'state_dict':model.cpu().state_dict(),'kind':'F6','settings':settings,'seed':seed,'normalizers':{'quality':{'mean':scaler.mean.tolist(),'std':scaler.std.tolist()}},'mask_counts':counts.tolist(),'training_seconds':time.perf_counter()-started,'loss_by_epoch':losses}
    torch.save(checkpoint,path)
    p,_=gate_predict(checkpoint,'F6',test_probabilities,test_quality,test_action,np.ones((len(test_quality),2),dtype='float32'))
    return p,checkpoint


def main():
    c=config();spec=read('configs/reassemble/section3_corruptions.json');root=Path(c['runs']['modality-dropout']);storage()
    assert (Path(c['runs']['section3'])/'results.json').exists(),'Complete clean-trained robustness first'
    base=read('configs/reassemble/section1.json');c2=read('configs/reassemble/section2.json');frame=cohort(base);y=frame.failure.to_numpy(dtype=int);quality,_,_=quality_features(frame,base,c2)
    actions=np.stack([(frame.action==a).to_numpy(dtype='float32') for a in c2['actions']],1);splits=read(base['splits'])
    for folder in ['fits','predictions']:(root/folder).mkdir(exist_ok=True)
    torch.set_num_threads(4);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    clean=np.zeros(len(frame));hard=np.zeros(len(frame),dtype=int);thresholds={};cost={}
    for outer in splits['folds']:
        k=outer['fold'];metadata=read(Path(c['section2'])/'predictions'/f'outer{k}.json')['models']['F6'];settings=metadata['settings']
        tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));inner=np.full((3,len(frame)),np.nan)
        for j in range(4):
            with np.load(Path(c['section2'])/'inputs'/f'outer{k}_inner{j}.npz') as z:
                it=z['train_rows'];iv=z['validation_rows'];train_prob=z['train_probabilities'];test_prob=z['validation_probabilities']
            for s,seed in enumerate(spec['dropout']['seeds']):
                path=root/'fits'/f'outer{k}_inner{j}_s{s}.pt'
                inner[s,iv],_=fit_dropout(train_prob,quality[it],actions[it],y[it],test_prob,quality[iv],actions[iv],settings,seed+1000*k+100*j,path)
        threshold=choose_threshold(y[tr],inner[:,tr].mean(0));thresholds[str(k)]=threshold
        with np.load(Path(c['section1b'])/'stacking'/f'outer{k}.npz') as z:train_prob=z['training_branch_oof'];test_prob=z['test_branch_probabilities']
        values=[];details=[]
        for s,seed in enumerate(spec['dropout']['seeds']):
            p,checkpoint=fit_dropout(train_prob,quality[tr],actions[tr],y[tr],test_prob,quality[te],actions[te],settings,seed+1000*k+99,root/'fits'/f'outer{k}_final_s{s}.pt')
            values.append(p);details.append({name:checkpoint[name] for name in ['mask_counts','training_seconds','seed']})
        clean[te]=np.mean(values,0);hard[te]=clean[te]>=threshold;cost[str(k)]={'settings':settings,'fits':details}
        progress(f'Modality dropout: outer {k+1}/5 complete; no corruption-driven selection')
    if not (root/'training.json').exists():write(root/'training.json',{'thresholds':thresholds,'cost':cost,'mask_probabilities':spec['dropout'],'single_missing_gradient':'zero by construction; test confirms exact surviving-branch predictions'})
    w=draws(frame.recording_id.to_numpy(),2000,spec['bootstrap_seed']);result={};clean_boot=None;ordinary_clean=None
    for name in spec['dropout']['test_conditions']:
        with np.load(Path(c['runs']['section3'])/'predictions'/(name+'.npz')) as z:original={key:z[key] for key in z.files}
        p=np.zeros(len(frame));decision=np.zeros(len(frame),dtype=int);weights=np.zeros((3,len(frame),2));seed_p=np.zeros((3,len(frame)))
        for k in range(5):
            ix=np.flatnonzero(original['fold']==k)
            for s in range(3):
                checkpoint=torch.load(root/'fits'/f'outer{k}_final_s{s}.pt',map_location='cpu',weights_only=True)
                seed_p[s,ix],weights[s,ix]=gate_predict(checkpoint,'F6',original['branch_probabilities'][ix],original['quality'][ix],actions[ix],original['availability'][ix])
            p[ix]=seed_p[:,ix].mean(0);decision[ix]=p[ix]>=thresholds[str(k)]
        if name in ['V4','S5']:
            remaining='U1' if name=='V4' else 'U2'
            assert np.allclose(p,original[remaining+'_p'],atol=1e-6)
            p=original[remaining+'_p'].copy();decision=original[remaining+'_hard'].astype(int)
            assert np.array_equal(p,original['F6_p'])
        boot=weighted_metrics(y,p,decision,w);ordinary=weighted_metrics(y,original['F6_p'],original['F6_hard'],w)
        point=metrics(y,p,decision);opoint=metrics(y,original['F6_p'],original['F6_hard'])
        values={'metrics':intervals(point,boot),'minus_clean_trained_F6':intervals(point-opoint,boot-ordinary)}
        if name=='clean':clean_boot=boot;ordinary_clean=ordinary;clean_point=point;oclean_point=opoint
        else:
            values['degradation_advantage']=intervals((point-clean_point)-(opoint-oclean_point),(boot-clean_boot)-(ordinary-ordinary_clean))
        values['visual_weight_mean']=float(weights[:,:,0].mean());values['sensor_weight_mean']=float(weights[:,:,1].mean())
        result[name]=values
        path=root/'predictions'/(name+'.npz')
        if not path.exists():np.savez_compressed(path,p=p,hard=decision,y=y,fold=original['fold'],weights=weights.mean(0),seed_weights=weights,seed_p=seed_p)
        progress('Modality-dropout comparison complete: '+name)
    write(root/'results.json',{'conditions':result,'cost':cost,'interpretation':'Single-missing conditions are exactly the surviving frozen branch for both variants; only joint-present behavior can change under this gate architecture. All training masks independent of outcomes; no corruption tuning.'})
    text='# Modality-dropout handoff\n\nOne F6 variant, same architecture/settings, three seeds and original folds. Masks .15 visual missing/.15 sensor missing/.70 both available; never both absent.\n\n'+table(['Condition','AUROC','AUPRC','Δ AP vs ordinary F6 [95%]'],[[name,f"{v['metrics']['AUROC']['estimate']:.4f}",f"{v['metrics']['AUPRC']['estimate']:.4f}",f"{v['minus_clean_trained_F6']['AUPRC']['estimate']:.4f} [{v['minus_clean_trained_F6']['AUPRC']['lower_95']:.4f}, {v['minus_clean_trained_F6']['AUPRC']['upper_95']:.4f}]"] for name,v in result.items()])
    text+='\nMissing-modality probabilities are exactly unchanged: with one available branch, masked softmax gives a fixed unit weight and zero gate-parameter gradient. This architecture cannot recover absent information through modality-dropout training. Clean/degraded joint-present trade-offs above are empirical, not universal robustness evidence. Full paired metrics, degradation advantages and seed weights: '+str(root)+'.\n'
    Path('artifacts/reassemble/reports/MODALITY_DROPOUT_HANDOFF.md').write_text(text)
    progress('Modality-dropout phase complete; continue audio feasibility and synthesis')

if __name__=='__main__':
    with threadpool_limits(limits=4,user_api='blas'):main()
