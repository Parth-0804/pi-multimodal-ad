"""Fit-local heads and calibration; matched per-segment gradient accumulation.

Head/standardizer/seed policy attributed to the pinned predecessor source.
No held-out labels are arguments to raw training helpers.
"""
import os
import time
import numpy as np
import pandas as pd
import torch
from torch import nn
from common import RUN, REPO, config, read, write, save_csv, sha, signature, event, budget, elapsed, consume, prior, local
from data import META, KEYS, validate_job
from fusion import standardizer, transform, calibrate, calibrated, sensor_fit, sensor_predict, stacker, fused


class Head(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.projection = nn.Sequential(nn.Linear(width,128),nn.ReLU(),nn.Dropout(.1))
        self.classifier = nn.Linear(128,1)

    def forward(self, x):
        return self.classifier(self.projection(x)).squeeze(-1)


def atomic_torch(path, value):
    p = local(path); tmp = local(p.with_suffix('.writing.pt'))
    torch.save(value, tmp); os.replace(tmp,p)


def folder_for(condition, j):
    return RUN/condition/j['fold_name']/('outer_assessment' if j['role']=='outer_assessment' else 'fusion_training/'+j['role'])


def fit_identity(identity, j, component):
    return signature({'inputs':identity, 'job':j, 'component':component})


def predict_head(model, x, mean, std, device):
    model.eval(); out=[]
    with torch.no_grad():
        for offset in range(0,len(x),256):
            z=torch.from_numpy(transform(x[offset:offset+256],mean,std)).to(device)
            out.extend(model(z).cpu().numpy().tolist())
    return np.array(out)


def train_raw(xG, yG, seed, device, checkpoint=None, fit_id=None):
    """Only G features/labels; checkpoint is bound to an exact scientific fit."""
    assert len(xG)==len(yG) and set(np.unique(yG))=={0,1}
    mean,std=standardizer(xG)
    torch.manual_seed(seed)
    if device=='cuda': torch.cuda.manual_seed_all(seed)
    model=Head(xG.shape[1]).to(device)
    opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.001)
    criterion=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((yG==0).sum()/(yG==1).sum()),device=device))
    xx=torch.from_numpy(transform(xG,mean,std)).to(device)
    yy=torch.tensor(yG,dtype=torch.float32,device=device)
    curves=[]; epoch0=0; offset0=0; updates=0; loss_sum=0.; seen=0; prior_seconds=0.
    if checkpoint and checkpoint.exists():
        d=torch.load(checkpoint,map_location='cpu',weights_only=True)
        assert d['fit_id']==fit_id and torch.equal(d['mean'],torch.from_numpy(mean)) and torch.equal(d['std'],torch.from_numpy(std))
        model.load_state_dict(d['head']);opt.load_state_dict(d['optimizer'])
        epoch0=d['epoch'];offset0=d['offset'];curves=d['curves'];updates=d['updates'];loss_sum=d['loss_sum'];seen=d['seen'];prior_seconds=d['seconds']
        torch.set_rng_state(d['cpu_rng'])
        if device=='cuda':torch.cuda.set_rng_state(d['cuda_rng'])
    start=time.perf_counter()
    def save(epoch,offset):
        if checkpoint:
            atomic_torch(checkpoint,dict(fit_id=fit_id,head={k:v.detach().cpu() for k,v in model.state_dict().items()},
                optimizer=opt.state_dict(),mean=torch.from_numpy(mean),std=torch.from_numpy(std),epoch=epoch,offset=offset,
                curves=curves,updates=updates,loss_sum=loss_sum,seen=seen,seconds=prior_seconds+time.perf_counter()-start,
                cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state() if device=='cuda' else None))
    for epoch in range(epoch0,5):
        order=np.random.default_rng(seed+epoch).permutation(len(xG))
        model.train()
        for offset in range(offset0 if epoch==epoch0 else 0,len(order),8):
            if checkpoint and elapsed()>config()['wall_seconds']-config()['report_reserve_seconds']:
                save(epoch,offset);raise RuntimeError('DEADLINE_CHECKPOINT_SAVED')
            ix=order[offset:offset+8];opt.zero_grad(set_to_none=True)
            for row in ix:
                loss=criterion(model(xx[row:row+1]),yy[row:row+1])
                assert bool(torch.isfinite(loss)), 'NONFINITE_LOSS'
                (loss/len(ix)).backward();loss_sum+=float(loss.detach());seen+=1
            norm=nn.utils.clip_grad_norm_(model.parameters(),1.)
            assert bool(torch.isfinite(norm)) and all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in model.parameters())
            opt.step();updates+=1
            if checkpoint and updates%100==0:
                budget(8*2**20);save(epoch,offset+len(ix))
        curves.append({'epoch':epoch+1,'training_BCE_mean':loss_sum/seen,'G_presentations':seen,'optimizer_updates':updates})
        loss_sum=0.;seen=0;offset0=0;save(epoch+1,0)
    state={'head':{k:v.detach().cpu() for k,v in model.state_dict().items()},'mean':torch.from_numpy(mean),'std':torch.from_numpy(std)}
    return model,state,curves,prior_seconds+time.perf_counter()-start


def reload_head(path,device):
    state=torch.load(path,map_location='cpu',weights_only=True)
    m=Head(len(state['mean'])).to(device);m.load_state_dict(state['head']);m.eval()
    return m,state['mean'].numpy(),state['std'].numpy()


def reuse_source(j,component):
    """No scores consulted. Only source- and membership-identifiable prior fits."""
    if component=='visual':
        p=prior()/'frozen_16_frames'/j['fold_name']/('outer_assessment' if j['role']=='outer_assessment' else 'fusion_training/'+j['role'])/'visual_fit'
    else:
        p=prior()/'sensor_reference'/j['fold_name']/j['role']
    if not (p/'complete.json').exists(): return None,'No complete predecessor fit'
    d=read(p/'complete.json')
    if d.get('job')!=j: return None,'Different exact saved memberships or seed'
    identity=read(RUN/'provenance/input_identity.json')['prior_files']
    old=d.get('identities',{})
    required={'cohort':'data_manifests/cohort_and_frames.json','partitions':'data_manifests/fit_partitions.json','sensor_statistics':'shared_cache/sensor_statistics.npy','config':'config/resolved_config.json','original_pretrained_identity':'provenance/original_pretrained_identity.json'}
    for k,name in required.items():
        if old.get(k)!=identity[name]:return None,'Unverified identity '+k
    for name in ['data.py','fusion.py','visual_model.py','training.py']:
        if old.get('sources',{}).get(name)!=identity.get('source/'+name): return None,'Prior fit source not equal pinned source '+name
    predictions=p/'identified_branch_predictions.csv'
    if sha(predictions)!=d['predictions_sha256']:raise RuntimeError('PRIOR_PREDICTION_DRIFT')
    if component=='visual':
        if d.get('epochs_complete')!=5 or d.get('frames')!=16 or d.get('final_stage_trainable') is not False:return None,'Incompatible head settings'
        if sha(p/'model.pt')!=d['model_sha256']: raise RuntimeError('PRIOR_MODEL_DRIFT')
    return (p,d),'Exact protocol, source and keyed role verified'


def predictions_frame(f,j,raw,p,component,fid):
    pred=f.iloc[j['predict']][META].copy()
    pred['raw_'+component+'_logit']=raw;pred['p_'+component]=p;pred[component+'_fit_id']=fid
    return pred


def complete_load(folder,fid):
    done=folder/'complete.json'
    if not done.exists():return None
    d=read(done);assert d['fit_id']==fid,'COMPLETED_FIT_IDENTITY_DRIFT'
    for name,h in d['outputs'].items():assert sha(folder/name)==h,'COMPLETED_FIT_OUTPUT_DRIFT'
    return pd.read_csv(folder/'identified_branch_predictions.csv',dtype={'recording_id':str,'segment_id':str}),d


def record_complete(folder,fid,status,outputs,**extra):
    d={'fit_id':fid,'status':status,'outputs':{n:sha(folder/n) for n in outputs},**extra}
    write(folder/'complete.json',d);return d


def sensor_job(f,j,stats,identity):
    validate_job(f,j);folder=folder_for('sensor_reference',j);fid=fit_identity(identity,j,'sensor')
    existing=complete_load(folder,fid)
    if existing:return existing
    budget(16*2**20);local(folder/'complete.json')
    compatible,reason=reuse_source(j,'sensor');start=time.perf_counter()
    G,C,V=[np.array(j[k],int) for k in ('G','C','predict')]
    if compatible:
        p,old=compatible;model=read(p/'model_and_calibrator.json');status='REUSED'
        origin={'path':str(p.relative_to(REPO)),'complete_sha256':sha(p/'complete.json')}
    else:
        consume('sensor',fid)
        model=sensor_fit(stats[G],f.iloc[G].failure.to_numpy(),stats[C],f.iloc[C].failure.to_numpy());status='NEW';origin=None
        d=read(RUN/'progress.json');d['calibrator_fits']+=1;write(RUN/'progress.json',d)
    raw,prob=sensor_predict(stats[V],model);pred=predictions_frame(f,j,raw,prob,'sensor',fid)
    if compatible:
        oldpred=pd.read_csv(p/'identified_branch_predictions.csv',dtype={'recording_id':str,'segment_id':str})
        assert pred[KEYS].values.tolist()==oldpred[KEYS].values.tolist()
        assert np.max(abs(prob-oldpred.p_sensor.to_numpy()))<=1e-5,'SENSOR_REUSE_REPLAY'
    write(folder/'model_and_calibrator.json',model);save_csv(folder/'identified_branch_predictions.csv',pred)
    info=record_complete(folder,fid,status,['model_and_calibrator.json','identified_branch_predictions.csv'],job=j,reuse_reason=reason,origin=origin,seconds=time.perf_counter()-start)
    return pred,info


def visual_job(f,j,c,x,identity,device='cuda'):
    validate_job(f,j);folder=folder_for(c,j);fid=fit_identity(identity,j,c)
    existing=complete_load(folder,fid)
    if existing:return existing
    budget(32*2**20);local(folder/'complete.json')
    compatible,reason=reuse_source(j,'visual') if c=='cnn_only' else (None,'New encoder representation')
    G,C,V=[np.array(j[k],int) for k in ('G','C','predict')]
    write(folder/'memberships.json',validate_job(f,j))
    if compatible:
        p,old=compatible
        state=torch.load(p/'model.pt',map_location='cpu',weights_only=True)
        assert state.get('stage') is None and len(state['mean'])==x.shape[1]
        mean,std=standardizer(x[G]);np.testing.assert_array_equal(mean,state['mean'].numpy());np.testing.assert_array_equal(std,state['std'].numpy())
        atomic_torch(folder/'model.pt',state)
        model,mean,std=reload_head(folder/'model.pt',device)
        cal=read(p/'calibrator.json');status='REUSED';curves=pd.read_csv(p/'learning_curve.csv').to_dict('records')
        seconds=0.;origin={'path':str(p.relative_to(REPO)),'complete_sha256':sha(p/'complete.json'),'original_training_seconds':old['training_wall_seconds']}
    else:
        consume('visual',fid);event('FITTING_HEAD',condition=c,fold=j['fold_name'],role=j['role'])
        model,state,curves,seconds=train_raw(x[G],f.iloc[G].failure.to_numpy(),j['seed'],device,folder/'in_progress.pt',fid)
        atomic_torch(folder/'model.pt',state);mean=state['mean'].numpy();std=state['std'].numpy()
        rawC=predict_head(model,x[C],mean,std,device)
        cal=calibrate(rawC,f.iloc[C].failure.to_numpy());status='NEW';origin=None
        d=read(RUN/'progress.json');d['calibrator_fits']+=1;write(RUN/'progress.json',d)
        held=f.iloc[C][META].copy();held['raw_visual_logit']=rawC;save_csv(folder/'calibration_holdout_logits.csv',held)
    raw=predict_head(model,x[V],mean,std,device);prob=calibrated(raw,cal)
    pred=predictions_frame(f,j,raw,prob,'visual',fid)
    if compatible:
        op=pd.read_csv(p/'identified_branch_predictions.csv',dtype={'recording_id':str,'segment_id':str})
        assert pred[KEYS].values.tolist()==op[KEYS].values.tolist()
        assert np.max(abs(prob-op.p_visual.to_numpy()))<=1e-5,'CNN_REUSE_REPLAY'
    saved,mu,sd=reload_head(folder/'model.pt',device)
    error=float(np.max(abs(calibrated(predict_head(saved,x[V[:3]],mu,sd,device),cal)-prob[:3])))
    assert error<=config()['probability_replay_tolerance'],'HEAD_REPLAY'
    save_csv(folder/'identified_branch_predictions.csv',pred);write(folder/'calibrator.json',cal)
    save_csv(folder/'learning_curve.csv',pd.DataFrame(curves))
    info=record_complete(folder,fid,status,['model.pt','identified_branch_predictions.csv','calibrator.json','learning_curve.csv'],
        job=j,epochs=5,seed=j['seed'],dimension=x.shape[1],head_parameters=sum(p.numel() for p in model.parameters()),
        seconds=seconds,origin=origin,reuse_reason=reason,replay_probability_max_abs=error)
    return pred,info


def join_branches(visual,sensor):
    assert set(KEYS+['failure','raw_sensor_logit','p_sensor','sensor_fit_id']).issubset(sensor.columns), 'SENSOR_SCHEMA'
    assert not visual.duplicated(KEYS).any() and not sensor.duplicated(KEYS).any()
    assert set(map(tuple,visual[KEYS].values))==set(map(tuple,sensor[KEYS].values)),'PREDICTION_COVERAGE'
    z=visual.merge(sensor[KEYS+['failure','raw_sensor_logit','p_sensor','sensor_fit_id']],on=KEYS,validate='one_to_one',suffixes=('','_sensor'))
    assert np.array_equal(z.failure,z.failure_sensor),'LABEL_JOIN_MISMATCH'
    return z.drop(columns='failure_sensor')


def live_replay(f,j,c,extractor,pixels,expected,stack_model):
    folder=folder_for(c,j);m,mean,std=reload_head(folder/'model.pt','cuda');cal=read(folder/'calibrator.json')
    rows=[]
    for i in j['predict'][:3]:
        s=f.iloc[i].to_dict();x=pixels(s).cuda()
        with torch.inference_mode(): z=extractor.segment(x,c).cpu().numpy().copy()[None,:]
        v=float(calibrated(predict_head(m,z,mean,std,'cuda'),cal)[0])
        record=expected.loc[(expected.recording_id==s['recording_id'])&(expected.segment_id==s['segment_id'])].iloc[0]
        s_model=read(folder_for('sensor_reference',j)/'model_and_calibrator.json')
        stats=np.load(RUN/'cache/sensor_statistics.npy',mmap_mode='r')
        _,sensor=sensor_predict(stats[i:i+1],s_model)
        p=float(fused(np.array([[v,sensor[0]]]),stack_model)[0])
        error=max(abs(v-record.p_visual),abs(sensor[0]-record.p_sensor),abs(p-record.p_fused))
        assert error<=config()['probability_replay_tolerance'],'FULL_OUTER_REPLAY'
        rows.append(dict(recording_id=s['recording_id'],segment_id=s['segment_id'],max_probability_abs=float(error)))
    write(folder/'full_saved_model_replay.json',{'passed':True,'tolerance':config()['probability_replay_tolerance'],'rows':rows,'path':'original pixels -> frozen prefix -> saved head/normalizer/calibrators -> saved stacker'})


def run_folds(f,jobs,arrays,extractor,pixels,identity):
    stats=np.load(RUN/'cache/sensor_statistics.npy',allow_pickle=False)
    for k in range(5):
        budget()
        # Later paired blocks use measured NEW head costs with a 2x margin;
        # never reduce epochs/cohort/folds to manufacture completion.
        observed=[read(p).get('seconds',0.) for c in config()['conditions'] for p in (RUN/c).glob('fold_*/**/complete.json') if read(p).get('status')=='NEW']
        if observed and 20*max(observed)+120 > config()['wall_seconds']-elapsed()-config()['report_reserve_seconds']:
            raise RuntimeError('NEXT_PAIRED_FOLD_UNLIKELY_WITHIN_BUDGET')
        js=[j for j in jobs if j['outer_fold_original']==k];outer=next(j for j in js if j['role']=='outer_assessment');inner=[j for j in js if j['role']!='outer_assessment']
        sensors={j['role']:sensor_job(f,j,stats,identity) for j in js}
        for c in config()['conditions']:
            dest=RUN/c/outer['fold_name'];done=dest/'condition_complete.json'
            if done.exists():
                d=read(done);assert d['identity']==identity and sha(dest/'assessment_predictions.csv')==d['predictions_sha256'];continue
            parts=[];statuses=[]
            for j in inner:
                v,info=visual_job(f,j,c,arrays[c],identity);parts.append(join_branches(v,sensors[j['role']][0]));statuses.append(info['status'])
            oof=pd.concat(parts,ignore_index=True)
            assert not oof.duplicated(KEYS).any() and set(oof.sample_id)==set(f.iloc[outer['T']].sample_id)
            save_csv(dest/'fusion_training/identified_oof_branch_probabilities.csv',oof)
            sid=fit_identity(identity,outer,c+'_F2')
            sp=dest/'F2_stacker.json'
            if sp.exists():
                sd=read(sp);assert sd['fit_id']==sid and sd['oof_sha256']==sha(dest/'fusion_training/identified_oof_branch_probabilities.csv');sm=sd['model']
            else:
                consume('stacker',sid);t=time.perf_counter();sm=stacker(oof[['p_visual','p_sensor']].to_numpy(),oof.failure.to_numpy())
                write(sp,{'fit_id':sid,'model':sm,'oof_sha256':sha(dest/'fusion_training/identified_oof_branch_probabilities.csv'),
                          'training_sample_keys':oof[KEYS].to_dict('records'),'seconds':time.perf_counter()-t,'status':'NEW'})
            v,info=visual_job(f,outer,c,arrays[c],identity);statuses.append(info['status'])
            out=join_branches(v,sensors['outer_assessment'][0]);out['p_fused']=fused(out[['p_visual','p_sensor']].to_numpy(),sm)
            for branch in ['visual','sensor','fused']:out['decision_'+branch]=(out['p_'+branch]>=.5).astype(int)
            out['threshold']=.5;out['fold_name']=outer['fold_name'];out['outer_fold_original']=k;out['stacker_fit_id']=sid
            out['status']='REUSED+NEW' if 'REUSED' in statuses else 'NEW'
            out['membership_manifest']='data/memberships/'+outer['fold_name']+'/outer_assessment.json'
            save_csv(dest/'assessment_predictions.csv',out)
            live_replay(f,outer,c,extractor,pixels,out,sm)
            write(done,{'identity':identity,'predictions_sha256':sha(dest/'assessment_predictions.csv'),'visual_fit_statuses':statuses,'rows':len(out),'full_replay_passed':True})
        a=pd.read_csv(RUN/'cnn_only'/outer['fold_name']/'assessment_predictions.csv')
        b=pd.read_csv(RUN/'cnn_plus_encoder'/outer['fold_name']/'assessment_predictions.csv')
        assert a[KEYS].values.tolist()==b[KEYS].values.tolist() and np.array_equal(a.p_sensor,b.p_sensor),'SHARED_SENSOR_DRIFT'
        event('PAIRED_FOLD_COMPLETE',fold=outer['fold_name'])
        # Save a usable paired partial report after every completed block.
        from evaluation import evaluate
        evaluate(bootstrap=False)
