"""Matched corruption-trained meta controls using genuine inner-held-out branches."""
import gc
import warnings
import numpy as np
import torch

from .common import PROJECT,config,read,sha,signature,write,code_identity,event
from .cohort import finalize
from .corruptions import SCENARIOS,alter_visual,alter_sensor,visual_quality
from .fusion import augmentation_root,visual_root,quality_matrix,fit_gate,gate_predict
from .metrics import metrics,independent_check
from .reference import primitives
from .robustness import training_scale
from .sensors import load_episode,sensor_sources,statistics,quality
from .splits import prepare,require_oof
from .training import atomic_checkpoint
from .visual import make,backbone,pixels,features

TRAIN_SCENARIOS=['blur_5','occlusion_0.25','missing_channels_0.25','noise_0.5','combined_partial']


def chosen_scenario(episode):
    index=int(signature(['meta_augmentation',int(episode)])[:16],16)%len(TRAIN_SCENARIOS)
    name=TRAIN_SCENARIOS[index]
    return next(s for s in SCENARIOS if s['name']==name)


def run(c=None,condition='V1',device='cuda'):
    c=c or config();rows=finalize(c);lookup={r['episode_index']:r for r in rows};jobs=prepare(c)
    qualities=quality_matrix(c,rows);inventory=sensor_sources(c);source=primitives()
    for seed in c['seeds']:
        for outer in range(c['outer_folds']):
            out=augmentation_root(c,condition,seed,outer)
            if (out/'COMPLETE.json').exists():
                receipt=read(out/'COMPLETE.json');assert sha(out/'predictions.json')==receipt['prediction_sha256'];continue
            clean_root=PROJECT/'06_training_experiments/fusion_experiments/runs'/c['run_id']/condition/f'seed{seed}'/f'outer{outer}'
            original_receipt=read(clean_root/'COMPLETE.json')
            assert sha(clean_root/'META_TRAINING_PREDICTIONS.json')==original_receipt['meta_training_sha256']
            assert sha(clean_root/'predictions.json')==original_receipt['prediction_sha256']
            clean=read(clean_root/'META_TRAINING_PREDICTIONS.json');require_oof(jobs,outer,clean)
            clean_index={r['episode_index']:r for r in clean};augmented={};lineage={}
            for job in [j for j in jobs if j['outer']==outer and j['inner']>=0]:
                if str(device).startswith('cuda'):
                    from .resources import wait_for_gpu
                    wait_for_gpu(c)
                vr=visual_root(c,condition,seed,job);vi=read(vr/'COMPLETE.json')
                assert sha(vr/'BEST_MODEL.pt')==vi['best_checkpoint_sha256']
                sr=PROJECT/'06_training_experiments/sensor_baselines/runs'/c['run_id']/f'seed{seed}'/job['id'];si=read(sr/'COMPLETE.json')
                assert sha(sr/'S3_MODEL.json')==si['S3_checkpoint_sha256']
                identity=signature({'config':c,'visual_checkpoint':vi['best_checkpoint_sha256'],'sensor_checkpoint':si['S3_checkpoint_sha256'],
                                    'split':job,'training_scenarios':TRAIN_SCENARIOS,'implementation':code_identity()})
                lineage[job['id']]={'visual_checkpoint':vi['best_checkpoint_sha256'],'sensor_checkpoint':si['S3_checkpoint_sha256'],'split_sha256':signature(job)}
                missing=[e for e in job['ids']['A'] if not (out/'augmented_oof'/f'{e:06d}.json').exists()]
                if missing:
                    model=make(c,condition,np.zeros(896),np.ones(896),seed,device)
                    payload=torch.load(vr/'BEST_MODEL.pt',map_location='cpu',weights_only=True);model.load_state_dict(payload['model']);model.eval()
                    cnn=model.backbone if model.backbone is not None else backbone(c,'V1',device)
                    cal=read(vr/'CALIBRATOR.json');s3=read(sr/'S3_MODEL.json');scale=training_scale(c,job,lookup,inventory)
                for number,e in enumerate(job['ids']['A']):
                    file=out/'augmented_oof'/f'{e:06d}.json'
                    if file.exists():
                        receipt=read(file);assert receipt['identity']==identity;augmented[e]=receipt['record'];continue
                    assert e in clean_index and clean_index[e]['fit_id']==job['id']
                    scenario=chosen_scenario(e);base=clean_index[e];pvisual=base['visual_probability'];psensor=base['sensor_probability']
                    vq=qualities[e][:6];sq=qualities[e][6:]
                    if scenario['visual']!='none':
                        x,_=alter_visual(pixels(c,lookup[e]),e,scenario);vq=visual_quality(x)
                        with torch.inference_mode():
                            z=features(cnn,x.to(device),c['cnn_frame_chunk']).mean(0,keepdim=True)
                            raw=model.head(torch.nan_to_num((z-model.mean)/model.std,nan=0,posinf=0,neginf=0))
                        pvisual=float(source['calibrated'](raw.cpu().numpy(),cal)[0])
                    if scenario['sensor']!='none':
                        values,_=load_episode(c,lookup[e],inventory);values,_=alter_sensor(values,e,scenario,scale)
                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore',RuntimeWarning);stats=statistics(values)[None,:];sq=quality(values)
                        _,prob=source['sensor_predict'](stats,s3);psensor=float(prob[0])
                    record={'episode_index':e,'fit_id':job['id'],'label':base['label'],'visual_probability':pvisual,'sensor_probability':psensor,
                            'scenario':scenario['name'],'quality':np.r_[vq,sq].astype('float32').tolist()}
                    write(file,{'identity':identity,'record':record});augmented[e]=record
                    if (number+1)%50==0:event(c,'MATCHED_META_AUGMENTATION',condition=condition,seed=seed,outer=outer,fit_id=job['id'],episodes=number+1)
                if missing:
                    del model,cnn;gc.collect()
                    if str(device).startswith('cuda'):torch.cuda.empty_cache()
            aug=[augmented[r['episode_index']] for r in clean];require_oof(jobs,outer,aug)
            combined=clean+aug
            p=np.asarray([[r['visual_probability'],r['sensor_probability']] for r in combined],dtype='float32')
            y=np.asarray([r['label'] for r in combined]);q=np.stack([qualities[r['episode_index']] for r in clean]+[np.asarray(r['quality'],dtype='float32') for r in aug])
            f2=source['stacker'](p,y)
            # 20x2N presentations matches the clean gate's40xN presentations.
            gate=fit_gate(p,q,y,seed,epochs=20);neutral=fit_gate(p,np.zeros_like(q),y,seed,epochs=20)
            gate['augmentation_training']=neutral['augmentation_training']=True
            common={'clean_and_augmented_meta_records':len(combined),'independent_native_meta_episodes':len(clean),
                    'warning':'Augmented rows are repeated views of the same native episodes, not additional independent examples'}
            gate.update(common);neutral.update(common)
            test=read(clean_root/'predictions.json');pt=np.asarray([[r['visual_probability'],r['sensor_probability']] for r in test],dtype='float32')
            qt=np.stack([qualities[r['episode_index']] for r in test]);pf=source['fused'](pt,f2);pg,_=gate_predict(gate,pt,qt);pn,_=gate_predict(neutral,pt,np.zeros_like(qt))
            predictions=[{**r,'F2_aug_probability':float(f),'gate_aug_probability':float(g),'gate_static_aug_probability':float(n)} for r,f,g,n in zip(test,pf,pg,pn)]
            write(out/'F2_AUGMENTED.json',f2);atomic_checkpoint(out/'GATE_AUGMENTED.pt',gate);atomic_checkpoint(out/'GATE_STATIC_AUGMENTED.pt',neutral)
            write(out/'AUGMENTED_OOF_RECORDS.json',aug);write(out/'predictions.json',predictions)
            yt=np.asarray([r['label'] for r in test]);reports={}
            for name,prob in [('F2_aug',pf),('Gate_aug',pg),('Gate_static_aug',pn)]:
                reports[name]=metrics(yt,prob);independent_check(yt,prob,reports[name])
            write(out/'metrics.json',reports)
            write(out/'COMPLETE.json',{'condition':condition,'seed':seed,'outer':outer,'source_inner_checkpoints':lineage,
                    'group_safe_OOF_verified_clean_and_corrupt_separately':True,'training_scenarios':TRAIN_SCENARIOS,
                    'gate_epochs':20,'clean_gate_equivalent_episode_presentations':True,**common,
                    'prediction_sha256':sha(out/'predictions.json'),'augmented_oof_sha256':sha(out/'AUGMENTED_OOF_RECORDS.json'),
                    'F2_sha256':sha(out/'F2_AUGMENTED.json'),'gate_sha256':sha(out/'GATE_AUGMENTED.pt'),'gate_static_sha256':sha(out/'GATE_STATIC_AUGMENTED.pt')})
