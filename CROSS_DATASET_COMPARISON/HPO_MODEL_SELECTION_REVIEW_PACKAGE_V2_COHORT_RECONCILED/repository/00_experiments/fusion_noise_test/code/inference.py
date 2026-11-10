"""Selected-model clean replay then 50 fixed corruption/absence realizations."""
import os,time,gc
import numpy as np
import pandas as pd
import torch
from common import RUN,REPO,config,read,write,csv,local,sha,signature,budget,event,elapsed
from selection import KEYS,validate_job
from corruptions import schedule,survivors,sensor_fault,statistics_for,routing
from inputs import Inputs,scales_for
from pipeline import Pipeline


def destination(job,fold):return RUN/'predictions'/job['family']/job['level']/f"repeat_{job['repeat']:02d}"/fold

def load_done(job,fold,identity):
    p=destination(job,fold)
    if not (p/'complete.json').exists():return None
    d=read(p/'complete.json');assert d['identity']==identity and sha(p/'predictions.csv')==d['predictions_sha256'],'COMPLETED_JOB_DRIFT'
    return pd.read_csv(p/'predictions.csv',dtype={k:str for k in KEYS})

def cache_frames(path,features,identity):
    local(path);tmp=local(path.with_suffix('.writing.npy'));np.save(tmp,features,allow_pickle=False);os.replace(tmp,path)
    write(path.with_suffix('.json'),{'identity':identity,'sha256':sha(path)})


def execute(selected):
    lock=read(RUN/'model_selection/selection_lock.json');assert sha(RUN/'model_selection/selected_model.json')==lock['selected_model_sha256']
    assert sha(RUN.parent.parent/'config.json')==lock['corruption_config_sha256']
    identity=signature(lock);f=pd.DataFrame(read(RUN/'data/cohort_and_frames.json'));jobs=read(RUN/'data/fit_partitions.json');inputs=Inputs()
    upstream=pd.read_csv(RUN/'model_selection/clean_predictions'/(selected['condition']+'.csv'),dtype={k:str for k in KEYS})
    all_jobs=schedule();clean_job=all_jobs[0];outer={fold:next(j for j in jobs if j['fold_name']==fold and j['role']=='outer_assessment') for fold in selected['folds']}
    # Finish EVERY clean fold before any new corrupted assessment input.
    benchmarks=[]
    for fold in selected['folds']:
        budget();j=outer[fold];validate_job(f,j)
        if load_done(clean_job,fold,identity) is not None:continue
        model=Pipeline(selected,fold);model.extractor.trace.clear()
        sample=f.iloc[j['G'][0]].to_dict();images=inputs.images(sample,selected['frames']);x,_=inputs.process(images)
        model.frames(x);torch.cuda.synchronize();start=time.perf_counter();model.frames(x);torch.cuda.synchronize()
        measured_seconds=time.perf_counter()-start
        benchmarks.append({'fold':fold,'training_sample_key':[sample[k] for k in KEYS],'frames':len(images),'clean_extraction_seconds':measured_seconds})
        # Training-only invariance/no-op checks before any corrupted assessment
        # inference. They validate reuse of the untouched modality explicitly.
        from prefix import tensor_sha
        from corruptions import image_fault
        import hashlib
        streams,names,units=inputs.streams(sample)
        sensor_before=[hashlib.sha256(a.tobytes()).hexdigest() for _,_,a in streams]
        image_before=[hashlib.sha256(a.tobytes()).hexdigest() for a in images]
        ids=sample['frames32'] if selected['frames']==32 else sample['frames16']
        no_op,_=inputs.process(images,'image_noise',0.,271828,[sample[k] for k in KEYS],ids)
        assert torch.equal(x,no_op),'REAL_PROCESSOR_NOOP'
        inputs.process(images,'image_noise',.02,271828,[sample[k] for k in KEYS],ids)
        assert sensor_before==[hashlib.sha256(a.tobytes()).hexdigest() for _,_,a in streams]
        sensor_fault(streams,names,'sensor_time_loss',.1,271828,[sample[k] for k in KEYS],sample['start'],sample['end'])
        assert image_before==[hashlib.sha256(a.tobytes()).hexdigest() for a in images]
        assert sensor_before==[hashlib.sha256(a.tobytes()).hexdigest() for _,_,a in streams]
        write(RUN/'checks/invariance'/fold/'training_inputs.json',{'passed':True,'training_sample_key':[sample[k] for k in KEYS],'processor_noop_bitwise':True,'sensor_input_unchanged_by_image_fault':True,'image_input_unchanged_by_sensor_fault':True,'native_inputs_never_mutated':True})
        write(RUN/'checks/training_input_timing.json',{'rows':benchmarks,'scope':'Fixed first G sample, not selected by outcome; no damaged assessment AP inspected'})
        estimated=measured_seconds*len(f.iloc[j['predict']])*13
        if estimated>config()['wall_seconds']-elapsed()-config()['report_reserve_seconds']:raise RuntimeError('INSUFFICIENT_INFERENCE_BUDGET')
        table=[];diff=[];t0=time.perf_counter()
        for i in j['predict']:
            budget(2**20);s=f.iloc[i].to_dict();key=[s[k] for k in KEYS]
            images=inputs.images(s,selected['frames']);x,_=inputs.process(images);features=model.frames(x);rv,pv=model.visual(features)
            streams,names,units=inputs.streams(s);clean_streams=[(n,t,x,np.zeros(x.shape,bool)) for n,t,x in streams]
            statistics=statistics_for(clean_streams,s['start'],s['end']);rs,ps=model.sensor_predict(statistics);pf,_=routing(pv,ps,model.stacker)
            expected=upstream.loc[(upstream.recording_id==s['recording_id'])&(upstream.segment_id==s['segment_id'])].iloc[0]
            errors=[abs(pv-expected.p_visual),abs(ps-expected.p_sensor),abs(pf-expected.p_fused)]
            diff.append(dict(zip(KEYS,key),max_probability_abs=max(errors),visual_abs=errors[0],sensor_abs=errors[1],fused_abs=errors[2],visual_logit_abs=abs(rv-expected.raw_visual_logit),sensor_logit_abs=abs(rs-expected.raw_sensor_logit),decision_disagreements=int((pv>=.5)!=(expected.p_visual>=.5))+int((ps>=.5)!=(expected.p_sensor>=.5))+int((pf>=.5)!=(expected.p_fused>=.5))))
            if max(errors)>config()['probability_replay_tolerance']:
                attempt=read(RUN/'progress.json').get('failures',{}).get('inference',0)+1
                csv(RUN/'checks/replay'/fold/f'failed_attempt_{attempt:02d}_differences.csv',pd.DataFrame(diff))
                csv(RUN/'checks/replay'/fold/f'failed_attempt_{attempt:02d}_partial_predictions.csv',pd.DataFrame(table))
                raise AssertionError('CLEAN_REPLAY_FAILURE')
            path=RUN/'cache/clean_frame_features'/fold/(s['sample_id']+'.npy');cache_frames(path,features,{'selection':identity,'sample_key':key,'frames':s['frames32'] if selected['frames']==32 else s['frames16']})
            table.append(row(s,fold,selected,clean_job,rv,rs,pv,ps,pf,len(images),len(names),'F2',True,True,{}))
        output=pd.DataFrame(table);csv(RUN/'checks/replay'/fold/'differences.csv',pd.DataFrame(diff));model.assert_frozen()
        write(RUN/'checks/replay'/fold/'trace_and_freeze.json',{'passed':True,'executed_modules':model.extractor.trace,'guarded_modules':model.extractor.forbidden,'parameters_and_buffers_unchanged':True})
        save_job(clean_job,fold,output,identity,time.perf_counter()-t0);del model;gc.collect();torch.cuda.empty_cache()
    from sklearn.metrics import average_precision_score
    clean=pd.concat([load_done(clean_job,fold,identity) for fold in selected['folds']],ignore_index=True)
    discrepancy=float(average_precision_score(clean.failure,clean.p_fused)-selected['clean_AP'])
    write(RUN/'checks/clean_replay.json',{'passed':True,'all_selected_rows_replayed':len(clean),'AP_difference_from_saved':discrepancy,'probability_tolerance':config()['probability_replay_tolerance']})
    # If replay can change the empirical winner, stop before noisy inference.
    comparison=pd.read_csv(RUN/'model_selection/clean_comparison.csv');eligible=comparison.loc[comparison.eligible==True]
    new_ap=float(average_precision_score(clean.failure,clean.p_fused))
    others=eligible.loc[eligible.condition!=selected['condition']].fused_AP
    if len(others) and others.max()>new_ap+1e-12:raise RuntimeError('CLEAN_REPLAY_UNDERMINES_SELECTION')
    for job in all_jobs[1:]:
        for fold in selected['folds']:
            budget()
            if load_done(job,fold,identity) is not None:continue
            j=outer[fold];model=Pipeline(selected,fold);base=load_done(clean_job,fold,identity).set_index(KEYS);t0=time.perf_counter();table=[]
            scale=scales_for(f,j,inputs,identity) if job['family']=='sensor_noise' else None
            for i in j['predict']:
                budget(2**20);s=f.iloc[i].to_dict();key=[s[k] for k in KEYS];original=base.loc[tuple(key)]
                rv=float(original.raw_visual_logit);rs=float(original.raw_sensor_logit);pv=float(original.p_visual);ps=float(original.p_sensor)
                frames=selected['frames'];channels=int(original.effective_channels);details={};va=True;sa=True;status='OK'
                family=job['family'];seed=job['seed'] or 0
                if family in ['image_noise','image_blur']:
                    images=inputs.images(s,frames);ids=s['frames32'] if frames==32 else s['frames16']
                    x,detail=inputs.process(images,family,job['severity'],seed,key,ids);rv,pv=model.visual(model.frames(x));details={'images':detail}
                    assert ps==float(original.p_sensor) and rs==float(original.raw_sensor_logit)
                elif family=='frame_loss':
                    path=RUN/'cache/clean_frame_features'/fold/(s['sample_id']+'.npy');metadata=read(path.with_suffix('.json'))
                    assert metadata['identity']['selection']==identity and metadata['identity']['sample_key']==key and sha(path)==metadata['sha256']
                    features=np.load(path,allow_pickle=False);keep,lost=survivors(frames,job['severity'],seed,key,family);rv,pv=model.visual(features[keep]);frames=len(keep);details={'removed_positions':lost.tolist()}
                elif family.startswith('sensor_'):
                    streams,names,units=inputs.streams(s)
                    try:
                        scales=np.array([np.nan if x is None else x for x in scale['population_sd']]) if scale else None
                        if scale:assert names==scale['names'] and units==scale['units']
                        altered,details=sensor_fault(streams,names,family,job['severity'],seed,key,s['start'],s['end'],scales)
                        rs,ps=model.sensor_predict(statistics_for(altered,s['start'],s['end'],details['time_bounds']));channels=details['channels_remaining']
                        assert pv==float(original.p_visual) and rv==float(original.raw_visual_logit)
                    except ValueError as exc:
                        if str(exc) not in ['UNDEFINED_RAW_TRAINING_SCALE','INSUFFICIENT_SUPPORT']:raise
                        status='UNSUPPORTED';details={'reason':str(exc)};ps=np.nan;rs=np.nan
                elif family=='missing_modality':
                    va=job['level']!='image_absent';sa=job['level']!='sensor_absent'
                    if not va:rv=pv=np.nan;frames=0
                    if not sa:rs=ps=np.nan;channels=0
                if status=='OK' and ((va and not np.isfinite(pv)) or (sa and not np.isfinite(ps))):
                    status='NUMERICAL_FAILURE';details['reason']='Nonfinite available branch probability'
                if status=='OK':pf,policy=routing(pv,ps,model.stacker,va,sa)
                else:pf=np.nan;policy='unsupported_no_prediction'
                item=row(s,fold,selected,job,rv,rs,pv,ps,pf,frames,channels,policy,va,sa,details);item['status']=status
                if va and sa and status=='OK':
                    item['delta_visual_logit_contribution']=model.stacker['coefficient'][0]*(pv-float(original.p_visual));item['delta_sensor_logit_contribution']=model.stacker['coefficient'][1]*(ps-float(original.p_sensor))
                table.append(item)
            model.assert_frozen();save_job(job,fold,pd.DataFrame(table),identity,time.perf_counter()-t0);del model;gc.collect();torch.cuda.empty_cache()
    inputs.close();event('COMPLETE' if len(selected['folds'])==5 else 'COMPLETE_ON_PILOT_COVERAGE',selected_condition=selected['condition'])


def row(s,fold,selected,job,rv,rs,pv,ps,pf,frames,channels,policy,va,sa,details):
    import json
    result={k:s[k] for k in ['recording_id','segment_id','sample_id','failure','action','start','end']}
    result.update(fold_name=fold,selected_condition=selected['condition'],fold_components_hash=signature(selected['components'][fold]),family=job['family'],level=job['level'],severity=job['severity'],repeat=job['repeat'],realization_seed=job['seed'],raw_visual_logit=rv,raw_sensor_logit=rs,p_visual=pv,p_sensor=ps,p_fused=pf,effective_frames=frames,effective_channels=channels,visual_available=va,sensor_available=sa,fallback_policy=policy,status='OK',corruption_metadata=json.dumps(details,sort_keys=True))
    for b in ['visual','sensor','fused']:
        value=result['p_'+b];threshold=selected['thresholds'][b];result['threshold_'+b]=threshold;result['decision_'+b]=int(value>=threshold) if np.isfinite(value) else None
    return result


def save_job(job,fold,table,identity,seconds):
    dest=destination(job,fold);csv(dest/'predictions.csv',table)
    write(dest/'complete.json',{'job':job,'fold':fold,'identity':identity,'predictions_sha256':sha(dest/'predictions.csv'),'rows':len(table),'seconds':seconds,'failed_rows':int((table.status!='OK').sum())})
    p=read(RUN/'progress.json');completed=p.get('completed_jobs',[]);completed.append({'job':job,'fold':fold,'path':str((dest/'predictions.csv').relative_to(RUN))})
    event('INFERENCE_JOB_COMPLETE',completed_jobs=completed,job=job,fold=fold)
