"""Warm VM-specific component measurements; no production latency claim."""
from pathlib import Path
import time
import cv2
import h5py
import joblib
import numpy as np
import torch
from .completion_common import config,read,write,storage,progress
from .section1_features import cohort,load_visual,statistics
from .section1_models import VisualHead,sigmoid
from .section3_sensor import sensor_probability
from .section2_models import DecisionGate,context,logit
from .section2_data import quality_features
from .alignment import timestamps_1d,resample_progress,sensor_quality
from .section3_visual import frame_quality
from .section1_report import table


def timed(fn,repeat=100,warmup=10,gpu=False):
    for _ in range(warmup):fn()
    values=[]
    for _ in range(repeat):
        if gpu:torch.cuda.synchronize()
        start=time.perf_counter();fn()
        if gpu:torch.cuda.synchronize()
        values.append(time.perf_counter()-start)
    return {'mean_seconds':float(np.mean(values)),'std_seconds':float(np.std(values)),'median_seconds':float(np.median(values)),'repetitions':repeat,'warmup':warmup,'throughput_per_second':float(1/np.mean(values))}


def main():
    c=config();storage();base=read('configs/reassemble/section1.json');c2=read('configs/reassemble/section2.json');root=Path(c['runs']['efficiency'])
    assert (Path(c['runs']['audio-gate'])/'results.json').exists()
    torch.set_num_threads(4);cv2.setNumThreads(1)
    frame=cohort(base);quality,_,_=quality_features(frame,base,c2)
    with np.load(Path(c['section2'])/'predictions/oof.npz') as z:clean={k:z[k] for k in z.files}
    # Fixed seed and one segment from each of three distinct recordings; benchmarking only.
    selected=frame.groupby('recording_id',sort=True).head(1).sample(3,random_state=20260927).sort_index()
    processor,backbone,backbone_info=load_visual(base)
    records=[];models={};gate_checkpoints={};torch.cuda.reset_peak_memory_stats()
    backbone_bytes=(Path(base['data_root'])/'cache/section1_models'/base['visual']['revision']/'model.safetensors').stat().st_size
    for row in selected.itertuples():
        k=int(clean['fold'][row.Index]);record=read(Path(base['audit_run'])/'records'/(row.recording_id+'.json'))['recording']
        sensor=joblib.load(Path(c['runs']['section3'])/'branches'/f'sensor_fold{k}.joblib')
        with h5py.File(Path(base['data_root'])/'raw/data'/record['filename'],'r') as h:
            streams={n:(timestamps_1d(h['timestamps'][n][()]),np.asarray(h['robot_state'][n][()],dtype=float)) for n in base['sensor']['channels']}
        def sensor_pre():return statistics(np.concatenate([resample_progress(t,x,row.start,row.end,512,5) for t,x in streams.values()],axis=1).astype('float32'))
        feature=sensor_pre()[None];sensor_prep=timed(sensor_pre,10,2)
        sensor_head=timed(lambda:sensor_probability(sensor,feature),100,10)
        def sensor_q():return [sensor_quality(t,x,row.start,row.end,512,5) for t,x in streams.values()]
        sensor_quality_time=timed(sensor_q,5,1)
        with np.load(Path(base['run_dir'])/'features'/(row.recording_id+'.npz')) as z:
            indices=z['frame_indices'][np.flatnonzero(z['row_index']==row.Index)[0]]
        cap=cv2.VideoCapture(str(Path(base['data_root'])/'cache/encoded_media'/record['sha256']/'hand.mp4'))
        def decode():
            images=[]
            for index in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read();assert ok;images.append(img)
            return images
        images=decode();decode_time=timed(decode,3,1);cap.release()
        def preprocess():return processor(images=[cv2.cvtColor(im,cv2.COLOR_BGR2RGB) for im in images],return_tensors='pt')['pixel_values'].cuda()
        batch=preprocess();preprocess_time=timed(preprocess,5,2,True)
        checkpoint=torch.load(Path(c['section1'])/'checkpoints'/f'rtdetr_fold{k}.pt',map_location='cpu',weights_only=True)
        head=VisualHead(checkpoint['width'],base).cuda();head.load_state_dict(checkpoint['state_dict']);head.eval()
        mean=checkpoint['normalizer_mean'].cuda();std=checkpoint['normalizer_std'].cuda()
        cal=read(Path(c['section1'])/'predictions'/f'rtdetr_perm00_fold{k}.json')['calibration']
        def visual_infer():
            with torch.inference_mode(),torch.autocast('cuda',dtype=torch.float16):
                maps=backbone(batch).feature_maps;z=torch.cat([m.float().mean((-2,-1)) for m in maps],dim=-1).mean(0)
            with torch.inference_mode():raw=head(((z-mean)/std)[None])[0]
            return torch.sigmoid(raw*cal['coefficient']+cal['intercept']).item()
        visual_time=timed(visual_infer,10,3,True);visual_quality_time=timed(lambda:frame_quality(images),5,2)
        probs=np.array([[clean['U2_p'][row.Index],clean['U1_p'][row.Index]]]);static=read(Path(c['section1b'])/'stacking'/f'outer{k}.json')['stacker']
        overhead={'F1':timed(lambda:probs.mean(1),200,20),'F2':timed(lambda:sigmoid(probs@np.asarray(static['coefficient'])+static['intercept']),200,20)}
        gate_parameters={};gate_sizes={}
        for name,folder in [('F5',Path(c['section2'])/'fits'),('F6',Path(c['section2'])/'fits'),('D6',Path(c['runs']['modality-dropout'])/'fits')]:
            built=[];params=0;sizes=0
            for seed in range(3):
                path=folder/(f'outer{k}_final_s{seed}.pt' if name=='D6' else f'{name}_outer{k}_final_s{seed}.pt')
                cp=torch.load(path,map_location='cpu',weights_only=True);kind='F6' if name=='D6' else name
                n=cp['normalizers']['quality'];q=np.nan_to_num((quality[[row.Index]]-np.asarray(n['mean']))/np.asarray(n['std']),nan=0).astype('float32')
                action=np.array([[float(row.action==a) for a in c2['actions']]],dtype='float32');availability=np.ones((1,2),dtype='float32')
                x=context(kind,action,q,availability);gate=DecisionGate(x.shape[1],cp['settings']['hidden']);gate.load_state_dict(cp['state_dict']);gate.eval()
                built.append((gate,torch.from_numpy(x),torch.from_numpy(logit(probs)),torch.from_numpy(availability)))
                params+=sum(p.numel() for p in gate.parameters());sizes+=path.stat().st_size
            def infer_gate():
                with torch.inference_mode():return np.mean([torch.sigmoid(m(x,l,a)[0]).item() for m,x,l,a in built])
            overhead[name]=timed(infer_gate,100,10);gate_parameters[name]=params;gate_sizes[name]=sizes
        records.append({'recording_id':row.recording_id,'segment_id':row.segment_id,'fold':k,'sensor_preprocessing':sensor_prep,'sensor_head':sensor_head,'sensor_quality':sensor_quality_time,'video_decode':decode_time,'visual_preprocessing':preprocess_time,'visual_inference':visual_time,'visual_quality':visual_quality_time,'fusion_overhead':overhead,'gate_parameters':gate_parameters,'gate_checkpoint_bytes':gate_sizes,'sensor_checkpoint_bytes':(Path(c['runs']['section3'])/'branches'/f'sensor_fold{k}.joblib').stat().st_size,'visual_head_bytes':(Path(c['section1'])/'checkpoints'/f'rtdetr_fold{k}.pt').stat().st_size})
    avg=lambda key:float(np.mean([r[key]['mean_seconds'] for r in records]))
    sensor_total=avg('sensor_preprocessing')+avg('sensor_head');visual_total=avg('video_decode')+avg('visual_preprocessing')+avg('visual_inference')
    visual_parameters=int(backbone_info['backbone_parameters'])+114945+2;sensor_parameters=220+1+2
    models['U1']={'total_parameters':sensor_parameters,'trainable_parameters':sensor_parameters,'checkpoint_bytes_mean':float(np.mean([r['sensor_checkpoint_bytes'] for r in records])),'preprocessing_seconds':avg('sensor_preprocessing'),'inference_seconds':avg('sensor_head'),'sequential_component_sum_seconds':sensor_total}
    models['U2']={'total_parameters':visual_parameters,'trainable_parameters':114945+2,'checkpoint_bytes_mean':backbone_bytes+float(np.mean([r['visual_head_bytes'] for r in records])),'preprocessing_seconds':avg('video_decode')+avg('visual_preprocessing'),'inference_seconds':avg('visual_inference'),'sequential_component_sum_seconds':visual_total}
    for name in ['F1','F2','F5','F6','D6']:
        overhead=float(np.mean([r['fusion_overhead'][name]['mean_seconds'] for r in records]));parameters=0 if name=='F1' else 3 if name=='F2' else 3*max(read(Path(c['section2'])/'assessment/results.json')['cost']['F6' if name=='D6' else name]['parameters_per_seed_by_fold'])
        qtime=avg('sensor_quality')+avg('visual_quality') if name in ['F5','F6','D6'] else 0.
        models[name]={'total_parameters':visual_parameters+sensor_parameters+parameters,'trainable_parameters':114945+2+sensor_parameters+parameters,'fusion_parameters':parameters,'checkpoint_bytes_mean':models['U1']['checkpoint_bytes_mean']+models['U2']['checkpoint_bytes_mean']+(24 if name=='F2' else 0 if name=='F1' else float(np.mean([r['gate_checkpoint_bytes'][name] for r in records]))),'preprocessing_seconds':models['U1']['preprocessing_seconds']+models['U2']['preprocessing_seconds']+qtime,'inference_seconds':models['U1']['inference_seconds']+models['U2']['inference_seconds']+overhead,'sequential_component_sum_seconds':sensor_total+visual_total+qtime+overhead,'cached_branch_fusion_overhead_seconds':overhead}
    for values in models.values():values['estimated_sequential_throughput_per_second']=1/values['sequential_component_sum_seconds']
    for name,value in models.items():
        value['estimated_segments_per_second']=1/value['sequential_component_sum_seconds']
        value['CPU_threads']=4
        value['GPU_required']=name!='U1'
        value['benchmark_peak_GPU_allocated_bytes']=torch.cuda.max_memory_allocated() if name!='U1' else 0
    result={'models':models,'measurements':records,'GPU':torch.cuda.get_device_name(),'peak_GPU_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_GPU_reserved_bytes':torch.cuda.max_memory_reserved(),'CPU_threads':4,'timing_scope':'warm VM measurements on 3 deterministic segments from distinct recordings; raw sensor arrays already in RAM; video decoding from existing cache measured separately; sequential component sums are estimates, not measured production end-to-end latency','checkpoint_scope':'RT-DETR source safetensors includes unused detection components; bytes reflect stored deployment source plus heads. Gate parameter totals use maximum ensemble size over all five outer folds. Frozen backbone contributes total but not trainable parameters. Trainable means fitted somewhere in pipeline, not fine-tuned in robustness.'}
    write(root/'results.json',result)
    Path('artifacts/reassemble/reports/EFFICIENCY_HANDOFF.md').write_text('# Efficiency and practical usability\n\n'+result['timing_scope']+'. No real-time or production claim.\n\n'+table(['Model','Total parameters','Trainable','Checkpoint MiB','Preprocessing ms','Inference ms','Component-sum ms'],[[name,v['total_parameters'],v['trainable_parameters'],f"{v['checkpoint_bytes_mean']/2**20:.3f}",f"{v['preprocessing_seconds']*1000:.3f}",f"{v['inference_seconds']*1000:.3f}",f"{v['sequential_component_sum_seconds']*1000:.3f}"] for name,v in models.items()])+'\nEstimated sequential throughput (segments/s): '+', '.join(name+' '+format(v['estimated_segments_per_second'],'.2f') for name,v in models.items())+'. Four CPU threads; visual-containing models use the T4. Peak is the shared visual benchmark allocation, not separate per-model isolated profiling.\nPeak GPU allocated bytes: '+str(result['peak_GPU_allocated_bytes'])+'. '+result['checkpoint_scope']+'\n\nLate fusion permits independent branch replacement, but replacement score distributions require training-only revalidation/recalibration of fusion. Static/gated fusion need no backbone joint retraining; their heads must be refitted when interfaces change. Missing modalities reduce exactly to the surviving branch.\n')
    progress('Efficiency measurements complete; final synthesis next')

if __name__=='__main__':main()
