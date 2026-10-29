"""Resumable raw-input stress tests using frozen clean-trained branch/fusion models."""
import warnings
import joblib
import numpy as np
import torch
from scipy.special import expit

from .common import PROJECT,config,event,read,sha,signature,write
from .cohort import finalize
from .corruptions import SCENARIOS,alter_visual,alter_sensor,visual_quality
from .fusion import visual_root,gate_predict
from .metrics import metrics,independent_check
from .reference import primitives
from .sensors import load_episode,sensor_sources,statistics,quality
from .splits import prepare
from .visual import backbone,make,pixels,features


def training_scale(c,job,lookup,inventory):
    """Observation-weighted noise scale from T measured samples only."""
    path=PROJECT/'07_robustness_experiments/sensor_degradation/runs'/c['run_id']/job['id']/'T_CHANNEL_SCALE.json'
    if path.exists():
        receipt=read(path);assert receipt['split_sha256']==signature(job)
        return np.asarray(receipt['std'],dtype='float32')
    count=0;total=np.zeros(28,dtype='float64');squared=np.zeros(28,dtype='float64')
    for e in job['ids']['T']:
        values,_=load_episode(c,lookup[e],inventory);v=values.astype('float64')
        count+=len(v);total+=v.sum(0);squared+=(v*v).sum(0)
    std=np.sqrt(np.maximum(squared/count-(total/count)**2,0))
    write(path,{'std':std.tolist(),'observations':count,'split_sha256':signature(job),'fit_groups':job['groups']['T']})
    return std.astype('float32')


def run(c=None,conditions=('V1','V2','V3'),device='cuda'):
    c=c or config();rows=finalize(c);lookup={r['episode_index']:r for r in rows};jobs=prepare(c);inventory=sensor_sources(c);source=primitives()
    for condition in conditions:
        for seed in c['seeds']:
            for job in [j for j in jobs if j['inner']==-1]:
                outer=job['outer'];root=PROJECT/'07_robustness_experiments/combined_corruption/runs'/c['run_id']/condition/f'seed{seed}'/f'outer{outer}'
                if (root/'COMPLETE.json').exists():
                    receipt=read(root/'COMPLETE.json');assert sha(root/'predictions.json')==receipt['prediction_sha256'];continue
                vr=visual_root(c,condition,seed,job)
                sr=PROJECT/'06_training_experiments/sensor_baselines/runs'/c['run_id']/f'seed{seed}'/job['id']
                fr=PROJECT/'06_training_experiments/fusion_experiments/runs'/c['run_id']/condition/f'seed{seed}'/f'outer{outer}'
                vreceipt=read(vr/'COMPLETE.json');sreceipt=read(sr/'COMPLETE.json');freceipt=read(fr/'COMPLETE.json')
                assert sha(vr/'BEST_MODEL.pt')==vreceipt['best_checkpoint_sha256']
                assert sha(sr/'S2_MODEL.joblib')==sreceipt['S2_checkpoint_sha256']
                assert sha(sr/'S3_MODEL.json')==sreceipt['S3_checkpoint_sha256']
                assert sha(fr/'QUALITY_GATE.pt')==freceipt['gate_sha256'] and sha(fr/'F2_COEFFICIENTS.json')==freceipt['f2_sha256']
                vmodel=make(c,condition,np.zeros(896),np.ones(896),seed,device)
                checkpoint=torch.load(vr/'BEST_MODEL.pt',map_location='cpu',weights_only=True);vmodel.load_state_dict(checkpoint['model']);vmodel.eval()
                cnn=vmodel.backbone if vmodel.backbone is not None else backbone(c,'V1',device)
                calibrator=read(vr/'CALIBRATOR.json');s3=read(sr/'S3_MODEL.json');s2=joblib.load(sr/'S2_MODEL.joblib')
                s2cal=read(sr/'S2_SELECTION_AND_CALIBRATION.json')['calibrator']
                f2=read(fr/'F2_COEFFICIENTS.json');gate=torch.load(fr/'QUALITY_GATE.pt',map_location='cpu',weights_only=True)
                scale=training_scale(c,job,lookup,inventory)
                prior=float(np.mean([lookup[e]['label'] for e in job['ids']['T']]))
                identity=signature({'visual':vreceipt,'sensor':sreceipt,'fusion':freceipt,'scenarios':SCENARIOS})
                all_predictions=[]
                for number,e in enumerate(job['ids']['A']):
                    out=root/'episodes'/f'{e:06d}.json'
                    if out.exists():
                        receipt=read(out);assert receipt['identity']==identity;all_predictions.extend(receipt['predictions']);continue
                    x=pixels(c,lookup[e]);values,_=load_episode(c,lookup[e],inventory);predictions=[]
                    for scenario in SCENARIOS:
                        name=scenario['name'];altered,va=alter_visual(x,e,scenario);sensor,sa=alter_sensor(values,e,scenario,scale)
                        if not va and not sa:
                            predictions.append({'episode_index':e,'canonical_task_id':lookup[e]['canonical_task_id'],
                               'label':lookup[e]['label'],'scenario':name,'status':'ABSTAIN_BOTH_MISSING','seed':seed,'outer':outer,'condition':condition})
                            continue
                        pv=prior;ps=prior;p2=prior
                        if va:
                            with torch.inference_mode():
                                z=features(cnn,altered.to(device),c['cnn_frame_chunk']).mean(0,keepdim=True)
                                raw=vmodel.head(torch.nan_to_num((z-vmodel.mean)/vmodel.std,nan=0,posinf=0,neginf=0))
                            pv=float(source['calibrated'](raw.cpu().numpy(),calibrator)[0])
                        if sa:
                            with warnings.catch_warnings():
                                warnings.simplefilter('ignore',RuntimeWarning);stats=statistics(sensor)[None,:];sq=quality(sensor)
                            _,sprob=source['sensor_predict'](stats,s3);ps=float(sprob[0])
                            prob=np.clip(s2.predict_proba(stats)[:,1],1e-6,1-1e-6)
                            p2=float(source['calibrated'](np.log(prob/(1-prob)),s2cal)[0])
                        else:sq=np.zeros(5,dtype='float32')
                        probs=np.asarray([[pv,ps]],dtype='float32');context=np.r_[visual_quality(altered),sq][None,:]
                        pg,w=gate_predict(gate,probs,context,np.asarray([[va,sa]],dtype='float32'))
                        # Common deterministic fallback is reported, never credited to learned reliability.
                        average=float(probs.mean()) if va and sa else pv if va else ps
                        pf2=float(source['fused'](probs,f2)[0]) if va and sa else pv if va else ps
                        predictions.append({'episode_index':e,'canonical_task_id':lookup[e]['canonical_task_id'],
                            'label':lookup[e]['label'],'scenario':name,'seed':seed,'outer':outer,'condition':condition,
                            'status':'PREDICTED','visual_available':va,'sensor_available':sa,
                            'visual_probability':pv,'S3_probability':ps,'S2_probability':p2,
                            'F1_average':average,'F2_probability':pf2,'gate_probability':float(pg[0]),'gate_visual_weight':float(w[0,0]),
                            'hardcoded_surviving_branch_fallback':not(va and sa),'absent_unimodal_prior_fallback':prior})
                    write(out,{'identity':identity,'predictions':predictions});all_predictions.extend(predictions)
                    if (number+1)%10==0:event(c,'ROBUSTNESS_EPISODES',condition=condition,seed=seed,outer=outer,episodes=number+1,total=len(job['ids']['A']))
                write(root/'predictions.json',all_predictions);reports={}
                for scenario in SCENARIOS:
                    part=[r for r in all_predictions if r['scenario']==scenario['name'] and r['status']=='PREDICTED']
                    result={'eligible':len(job['ids']['A']),'scored':len(part),'abstained':len(job['ids']['A'])-len(part)}
                    if part:
                        y=np.asarray([r['label'] for r in part])
                        for key in ['visual_probability','S3_probability','S2_probability','F1_average','F2_probability','gate_probability']:
                            p=np.asarray([r[key] for r in part]);report=metrics(y,p);independent_check(y,p,report);result[key]=report
                    reports[scenario['name']]=result
                write(root/'metrics.json',reports)
                write(root/'COMPLETE.json',{'identity':identity,'prediction_sha256':sha(root/'predictions.json'),
                    'training':'clean-trained branches, F2 and gate; no corruption augmentation advantage',
                    'scenarios':SCENARIOS,'hardcoded_fallback_separated':True,'test_labels_used_for_corruption':False})
                del cnn,vmodel
                if str(device).startswith('cuda'):torch.cuda.empty_cache()
