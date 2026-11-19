"""Read-only presentation extraction. Run with repository Python -B; no model imports."""
import ast, hashlib, io, json, os, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent
REPO=OUT.parents[3]
os.environ['MPLCONFIGDIR']=str(OUT/'plot_cache')
os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.path.insert(0,str(REPO/'src'))
import cv2, h5py, numpy as np, pandas as pd, soundfile as sf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from reassemble.alignment import interval_indices,resample_progress,timestamps_1d,action_from_text
from reassemble.media import blob_bytes
cv2.setNumThreads(1)
plt.rcParams.update({'font.size':10,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})

def clean(v):
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [clean(x) for x in v]
    if isinstance(v,np.ndarray):return clean(v.tolist())
    if isinstance(v,np.generic):return clean(v.item())
    if isinstance(v,Path):return str(v)
    if isinstance(v,float) and not np.isfinite(v):return None
    return v

def write(name,value):
    with (OUT/name).open('x') as f:json.dump(clean(value),f,indent=2,allow_nan=False);f.write('\n')

def csv(name,rows):pd.DataFrame(rows).to_csv(OUT/name,index=False,mode='x')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return os.path.relpath(p,REPO)
def stat(p):
    s=p.stat();return {'path':rel(p),'size_bytes':s.st_size,'mtime_ns':s.st_mtime_ns}
def save(fig,name):fig.savefig(OUT/name,dpi=150,bbox_inches='tight');plt.close(fig)
def scalar(d):
    x=d[()];return x.decode('utf-8') if isinstance(x,bytes) else clean(x)

CONFIG=REPO/'configs/reassemble/section1.json';config=json.loads(CONFIG.read_text())
ROOT=REPO/config['data_root'];AUDIT=REPO/config['audit_run'];CORE=REPO/'runs/reassemble/20260927T154732Z-section1'
COHORT=CORE/'cohort.parquet';ELIG=AUDIT/'tables_v2/cohort.parquet';GATE=REPO/'runs/reassemble/20260927T204649Z-audio-gate/results.json'
f=pd.read_parquet(COHORT);elig=pd.read_parquet(ELIG);recordings=pd.read_parquet(AUDIT/'recordings.parquet')
for d in [f,elig,recordings]:
    for k in ['recording_id','segment_id']:
        if k in d:d[k]=d[k].astype(str)
assert (len(f),int(f.failure.sum()),f.recording_id.nunique())==(4530,509,148),'STOP: frozen cohort mismatch'
assert set(f.action)=={'pick','insert','remove','place'}
assert not f.duplicated(['recording_id','segment_id']).any()
rec=recordings.set_index('recording_id');eligible=elig.set_index(['recording_id','segment_id'])
rule='Within frozen action/failure stratum: duration=end-start; sort abs(duration-median_duration), recording_id (string), segment_id (string); take first.'
selected=[];selection_details=[]
for action in ['pick','insert','remove','place']:
    for failure in [0,1]:
        g=f[(f.action==action)&(f.failure==failure)].copy();g['duration']=g.end-g.start;median=g.duration.median();g['distance']=(g.duration-median).abs()
        row=g.sort_values(['distance','recording_id','segment_id'],kind='stable').iloc[0].to_dict()
        rid=row['recording_id'];r=rec.loc[rid];eid=action+'_'+('failure' if failure else 'success')
        selected.append({k:row[k] for k in ['recording_id','segment_id','action','failure','start','end','duration']}|{'example_id':eid,'success':1-failure,'source_recording_filename':r.filename,'hand_video_path':str(Path(config['data_root'])/'cache/encoded_media'/r.sha256/'hand.mp4'),'sensor_source_path':str(Path(config['data_root'])/'raw/data'/r.filename),'selection_rule':rule})
        selection_details.append({'example_id':eid,'stratum_count':len(g),'median_duration':median,'absolute_difference':row['distance']})
selected=pd.DataFrame(selected)[['example_id','recording_id','segment_id','action','success','failure','start','end','duration','source_recording_filename','hand_video_path','sensor_source_path','selection_rule']]
csv('selected_examples.csv',selected.to_dict('records'));write('selection_details.json',{'rule':rule,'strata':selection_details,'ids_are_strings':True})
counts=[]
for action in ['pick','insert','remove','place']:
    g=f[f.action==action];fail=int(g.failure.sum());counts.append({'action':action,'success':len(g)-fail,'failure':fail,'total':len(g),'failure_prevalence':fail/len(g)})
csv('action_outcome_counts.csv',counts)
inputs=[COHORT,ELIG,CONFIG,AUDIT/'recordings.parquet',GATE,REPO/'configs/reassemble/audit.json',REPO/'src/reassemble/alignment.py',REPO/'src/reassemble/section1_features.py',REPO/'src/reassemble/media.py',REPO/'src/reassemble/inventory.py',REPO/'src/reassemble/completion_gates.py',REPO/'docs/reassemble/AUDIT_METHODS.md']
input_manifest=[stat(p)|{'sha256':sha(p)} for p in inputs]
write('input_manifest.json',input_manifest);write('config_snapshot.json',config)
# Execute only the exact pure statistics definition and exact frame-index expression.
# No feature extraction entry point, training module, model loader or transformer import.
feature_path=REPO/'src/reassemble/section1_features.py';tree=ast.parse(feature_path.read_text())
stat_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='statistics')
namespace={'np':np};exec(compile(ast.Module(body=[stat_node],type_ignores=[]),str(feature_path),'exec'),namespace);statistics=namespace['statistics']
choose_node=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='chosen' for t in n.targets))
choose_code=compile(ast.Expression(choose_node),str(feature_path),'eval')
write('function_execution.json',{'statistics':'Executed unmodified AST function definition from src/reassemble/section1_features.py::statistics with np as its only supplied global. No module-level model imports executed.','model16':'Evaluated unmodified chosen assignment expression from the current Section 1 extractor.','feature_source_sha256':sha(feature_path),'alignment':'Imported existing interval_indices and resample_progress; positions=512, gap_multiple=5; concatenated stream order; float32 as current extractor.'})
raw_paths=[ROOT/'raw/data'/r.filename for r in recordings.itertuples()]
raw_before=[stat(p) for p in raw_paths if p.exists()]
missing=[rel(p) for p in raw_paths if not p.exists()]
video_paths=[REPO/p for p in selected.hand_video_path.unique()]
media_before=[stat(p) for p in video_paths if p.exists()]
write('source_preservation_before.json',{'raw_files':raw_before,'selected_encoded_videos':media_before,'missing_raw_files':missing})
for sub in ['contact_sheets','sensors','audio']:(OUT/sub).mkdir()
streams=config['sensor']['channels'];audio_names=['hama1_audio','hama2_audio','hand_audio']
assert streams==['measured_force','measured_torque','gripper_positions','joint_efforts','joint_velocities']
assert config['sensor']['positions']==512 and config['visual']['frames']==16
widths={};schema=[];frame_rows=[];shape_rows=[];label_cards=[];video_rows=[];audio_rows=[];decode_details=[];checks=[];warnings=[]
all_modalities={k:sorted({v for x in recordings[k] for v in json.loads(x)}) for k in ['video_streams','audio_streams','event_streams']}
all_modalities['sensor_streams']=sorted({v for x in recordings.sensor_streams for v in json.loads(x)})
audio_plot_rid=sorted(selected.recording_id.unique())[0]
write('dataset_summary.json',{'total_raw_inventory_recordings':len(recordings),'raw_files_present':len(raw_before),'frozen_cohort_recordings':f.recording_id.nunique(),'segment_count':len(f),'success_count':int((f.failure==0).sum()),'failure_count':int(f.failure.sum()),'counts_by_action_outcome':counts,'available_modality_names':all_modalities,'core_modalities':['hand video','five robot_state sensor groups'],'configured_selected_visual_frames':16,'sensor_progress_positions':512,'total_sensor_scalar_channels':22,'audio_stream_names':audio_names,'source_paths_and_sha256':input_manifest,'audio_example_recording_id':audio_plot_rid,'audio_example_selection_rule':'Lexicographically first recording_id among the eight deterministically selected examples; central ten seconds independently per full stream, without consulting action labels.'})

for row in selected.itertuples(index=False):
    print('BUILD',row.example_id,row.recording_id,row.segment_id,flush=True)
    rid=row.recording_id;entry=rec.loc[rid];source=REPO/row.sensor_source_path;video=REPO/row.hand_video_path
    assert source.exists(),str(source)
    before=stat(source);assert before['size_bytes']==int(entry.size_bytes) and before['mtime_ns']==int(entry.mtime_ns),'Source differs from inventory'
    e=eligible.loc[(rid,row.segment_id)];assert e.primary_task and e.dual_complete
    for key in ['start','end','action','failure']:assert e[key]==getattr(row,key)
    with h5py.File(source,'r') as h:
        vt=timestamps_1d(h['timestamps/hand'][()]);ii=interval_indices(vt,row.start,row.end)
        chosen=eval(choose_code,{'np':np,'ii':ii});expected=ii[np.linspace(0,len(ii)-1,16).round().astype(int)]
        assert np.array_equal(chosen,expected) and len(np.unique(chosen))==16
        display=ii[np.linspace(0,len(ii)-1,5).round().astype(int)]
        arrays=[];names=[];stream_shapes={};stream_selected={};stream_totals={};timeline_streams={}
        for n in streams:
            ds=h['robot_state'][n];t=timestamps_1d(h['timestamps'][n][()]);a=np.asarray(ds[()],dtype=np.float64);idx=interval_indices(t,row.start,row.end)
            k=a.shape[1] if a.ndim==2 else 1;widths[n]=k
            stream_shapes[n]=list(a.shape);stream_totals[n]=len(t);stream_selected[n]=len(idx)
            names.extend([n+':'+str(j) for j in range(k)])
            arrays.append(resample_progress(t,a,row.start,row.end,512,5))
            timeline_streams[n]={'timestamp_start':t[0],'timestamp_end':t[-1],'in_interval_sample_count':len(idx),'selected_timestamp_start':t[idx[0]],'selected_timestamp_end':t[idx[-1]]}
            if len(schema)<22 and row.example_id=='pick_success':
                unit=ds.attrs.get('unit',ds.attrs.get('units','NOT_AVAILABLE'))
                if isinstance(unit,bytes):unit=unit.decode()
                for j in range(k):schema.append({'stream_name':n,'component_index':j,'generated_channel_name':n+':'+str(j),'source_shape':json.dumps(list(a.shape)),'scalar_channel_count':k,'unit_if_present':str(unit),'recording_id':rid})
        x=np.concatenate(arrays,axis=1).astype('float32');assert x.shape==(512,22)
        np.save(OUT/'sensors'/f'{row.example_id}_512x22.npy',x,allow_pickle=False)
        shape_rows.append({'example_id':row.example_id,'raw_stream_sample_counts':json.dumps(stream_totals),'raw_stream_shapes':json.dumps(stream_shapes),'resampled_shape':'[512, 22]','finite_fraction':np.isfinite(x).mean(),'missing_channel_count':int((~np.isfinite(x).any(axis=0)).sum()),'duration':row.duration,'actual_selected_timestamp_counts':json.dumps(stream_selected),'video_interval_timestamp_count':len(ii)})
        # Compare only label-independent sensor and frame arrays from retained extraction.
        feature=CORE/'features'/f'{rid}.npz';cached_match=None;cached_sensor_match=None
        if feature.exists():
            index=int(f.index[(f.recording_id==rid)&(f.segment_id==row.segment_id)][0])
            with np.load(feature,allow_pickle=False) as z:
                j=int(np.flatnonzero(z['row_index']==index)[0]);cached_match=bool(np.array_equal(z['frame_indices'][j],chosen));cached_sensor_match=bool(np.array_equal(z['sensor'][j],x,equal_nan=True))
            assert cached_match and cached_sensor_match,'Existing extractor arrays differ'
        checks.append({'example_id':row.example_id,'shape':list(x.shape),'model16_matches_current_source':bool(np.array_equal(chosen,expected)),'model16_matches_retained_cache':cached_match,'sensor_matches_retained_cache':cached_sensor_match,'all_indices_inside_interval':bool(np.all((vt[np.r_[chosen,display]]>=row.start)&(vt[np.r_[chosen,display]]<=row.end)))})
        scale=np.nanstd(x,axis=0);scaled=(x-np.nanmean(x,axis=0))/np.where(scale>0,scale,1)
        fig,ax=plt.subplots(figsize=(12,7));im=ax.imshow(scaled.T,aspect='auto',origin='upper',extent=[0,100,21.5,-.5],cmap='RdBu_r',vmin=-3,vmax=3)
        ax.set_yticks(range(22),names,fontsize=8);ax.set_xlabel('Normalized action progress (%)');ax.set_ylabel('Scalar channels (source component indices)')
        off=0
        for n in streams:
            off+=widths[n]
            if off<22:ax.axhline(off-.5,color='black',lw=.7)
        fig.colorbar(im,ax=ax,label='Within-example channel z-score; color clipped at ±3')
        ax.set_title(f'{row.example_id} | 512 × 22 sensor values\nper-channel visualization scaling only — not model preprocessing',fontsize=11)
        save(fig,f'sensors/{row.example_id}_heatmap.png')
        fig,axes=plt.subplots(5,1,figsize=(12,10),sharex=True);off=0
        for ax,n in zip(axes,streams):
            for j in range(widths[n]):ax.plot(np.linspace(0,100,512),x[:,off+j],lw=.9,label=str(j))
            ax.set_ylabel(n.replace('_','\n'),fontsize=9);ax.legend(title='Component',ncol=widths[n],loc='upper right',fontsize=8,title_fontsize=8);ax.grid(alpha=.2);off+=widths[n]
        axes[-1].set_xlabel('Normalized action progress (%)');fig.suptitle(f'{row.example_id}: resampled sensor channels in source values\nUnits absent from dataset attributes; gaps remain missing (NaN)',fontsize=12);fig.tight_layout(rect=[0,0,1,.95]);save(fig,f'sensors/{row.example_id}_grouped_lines.png')
        label=h['segments_info'][row.segment_id];original={k:scalar(label[k]) for k in ['text','start','end','success','index'] if k in label}
        assert original['start']==row.start and original['end']==row.end and int(not original['success'])==row.failure and action_from_text(original['text'])==row.action
        fields={k:clean(e[k]) for k in ['valid_interval','visual_usable','sensor_usable','primary_task','dual_complete','audio_nominal_usable','audio_usable','tri_complete']}
        for k in ['sensor_sample_counts','video_coverage','audio_coverage','available_modalities']:fields[k]=json.loads(e[k])
        label_cards.append({'example_id':row.example_id,'recording_id':rid,'segment_id':row.segment_id,'original_annotation_text':original['text'],'source_annotation_dataset':row.sensor_source_path+'::/segments_info/'+row.segment_id,'original_annotation_fields':original,'parsed_action':row.action,'start':row.start,'end':row.end,'duration':row.duration,'recorded_success':original['success'],'derived_failure':row.failure,'eligibility_fields':fields,'task_note':'Retrospective completed-action classification; run/recording identity and timing are not predictions.'})
        if video.exists():
            cap=cv2.VideoCapture(str(video));assert cap.isOpened()
            count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);fourcc=int(cap.get(cv2.CAP_PROP_FOURCC));codec=''.join(chr((fourcc>>(8*i))&255) for i in range(4))
            video_rows.append({'recording_id':rid,'path':row.hand_video_path,'codec':codec,'width':int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),'height':int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),'fps':fps,'frame_count':count,'duration_seconds':count/fps if fps else 'NOT_AVAILABLE','timestamp_count':len(vt),'timestamp_start':vt[0],'timestamp_end':vt[-1],'frame_count_matches_timestamp_count':count==len(vt),'duration_method':'encoded frame_count / fps (not timestamp span)'})
            assert count==len(vt)
            decoded={}
            for index in sorted(set(np.r_[display,chosen].tolist())):
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read();assert ok,f'Cannot decode {rid} frame {index}';decoded[index]=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            cap.release()
            for typ,indices,ncols in [('display5',display,5),('model16',chosen,4)]:
                nrows=1 if typ=='display5' else 4;fig,axes=plt.subplots(nrows,ncols,figsize=(16,3.8) if nrows==1 else (14,12));axes=np.asarray(axes).reshape(-1)
                for ax,index,pos in zip(axes,indices,np.linspace(0,1,len(indices))):
                    ax.imshow(decoded[int(index)]);ax.axis('off');ax.set_title(f'{pos:.0%} | frame {index}',fontsize=10)
                    frame_rows.append({'example_id':row.example_id,'recording_id':rid,'segment_id':row.segment_id,'relative_position':pos,'frame_index':int(index),'frame_timestamp':float(vt[index]),'inside_interval':bool(row.start<=vt[index]<=row.end),'selection_type':typ})
                fig.suptitle(f'{row.action.upper()} | recorded outcome: {"failure" if row.failure else "success"} | {rid} / segment {row.segment_id}\n{row.duration:.3f} s completed action • {"5 display frames" if nrows==1 else "16 frames selected by core extractor"}',fontsize=13)
                fig.tight_layout(rect=[0,0,1,.91 if nrows==1 else .95]);save(fig,f'contact_sheets/{row.example_id}_{5 if nrows==1 else 16}frame.png')
        else:missing.append(row.hand_video_path)
        if row.example_id=='insert_failure':
            values=statistics(x);assert values.shape==(220,)
            statnames=['mean','std_population','median','min','max','q25','q75','range','rms','slope_per_normalized_progress']
            statrows=[]
            for si,s in enumerate(statnames):
                for ci,name in enumerate(names):statrows.append({'stream_name':name.split(':')[0],'channel_name':name,'statistic':s,'value':float(values[si*22+ci])})
            csv('statistics_insert_failure.csv',statrows)
            matrix=values.reshape(10,22).T;den=np.nanmax(np.abs(matrix),axis=1,keepdims=True);viz=matrix/np.where(den>0,den,1)
            fig,ax=plt.subplots(figsize=(12,8));im=ax.imshow(viz,aspect='auto',cmap='RdBu_r',vmin=-1,vmax=1);ax.set_yticks(range(22),names,fontsize=8);ax.set_xticks(range(10),[s.replace('_','\n') for s in statnames],fontsize=8);off=0
            for n in streams:
                off+=widths[n]
                if off<22:ax.axhline(off-.5,color='black',lw=1)
            ax.set_title('Insert / failure: 22 channels × 10 statistics = 220 features\nColors divided by each channel’s largest absolute statistic for display only');fig.colorbar(im,ax=ax,label='Visualization scaling only; exact original values in CSV');save(fig,'statistics_insert_failure.png')
            alignment={'example_id':row.example_id,'recording_id':rid,'segment_id':row.segment_id,'action_interval':{'start':row.start,'end':row.end},'annotation_clock':'Absolute Unix-style seconds as stored in segments_info/<id>/start and end; no additional hardware clock synchronization is inferred.','video':{'timestamp_start':vt[0],'timestamp_end':vt[-1],'selected_frame_timestamps':vt[chosen],'selected_frame_indices':chosen,'display_frame_timestamps':vt[display]},'sensor_streams':timeline_streams,'audio_alignment_status':'unverified','audio_nominal_ranges':{},'action_aligned_audio_samples':None}
        # Open existing encoded datasets in memory; decode bounded probes only except the
        # deterministic illustration streams, counted blockwise without retaining audio.
        media=json.loads(entry.media)
        for n in audio_names:
            d=h[n];old=media[n];origin=float(entry.nominal_audio_origin)
            detail={'recording_id':rid,'stream_name':n,'source_dtype':str(d.dtype),'encoded_dataset_shape':list(d.shape),'dataset_attributes':dict(d.attrs),'explicit_audio_timestamp_dataset_present':n in h['timestamps']}
            try:
                with sf.SoundFile(io.BytesIO(blob_bytes(d))) as audio:
                    rate=audio.samplerate;channels=audio.channels;header=len(audio);container=audio.format+'/'+audio.subtype
                    count=int(old['frames']);count_method='Prior full decode from inventory; size/mtime checked; current header and bounded beginning/central probes decoded'
                    initial=audio.read(min(rate,4096),dtype='float32',always_2d=True);assert len(initial)>0
                    actual_count=None
                    if rid==audio_plot_rid:
                        audio.seek(0);actual_count=0
                        while True:
                            block=audio.read(262144,dtype='float32',always_2d=True)
                            if not len(block):break
                            actual_count+=len(block)
                        if actual_count!=count:warnings.append(f'{rid}/{n}: decoded count differs from inventory ({count} vs {actual_count})')
                        count=actual_count;count_method='Current blockwise full count; only central ten seconds retained in memory for figures'
                    duration=count/rate;excerpt_start=max(0,(duration-10)/2);audio.seek(int(excerpt_start*rate));samples=audio.read(min(int(10*rate),count),dtype='float32',always_2d=True);assert len(samples)>0
                    assert rate==old['sample_rate'] and channels==old['channels']
                    detail.update({'header_reported_sample_frames':header,'inventory_decoded_sample_frames':old['frames'],'current_fully_decoded_sample_frames':actual_count,'sample_count_evidence':count_method,'bounded_probe_frames':len(initial),'central_probe_frames':len(samples),'central_excerpt_start_seconds':int(excerpt_start*rate)/rate,'central_excerpt_duration_seconds':len(samples)/rate,'container':container})
                    audio_rows.append({'recording_id':rid,'stream_name':n,'source_path_or_dataset':row.sensor_source_path+'::/'+n,'container_or_dtype':container+'; stored '+str(d.dtype),'sample_rate_if_available':rate,'channels':channels,'sample_count':count,'duration_seconds':duration,'nominal_start_source':'inventory.nominal_audio_origin = minimum first non-audio timestamp; inferred, unverified','nominal_end':origin+duration,'decoded_successfully':True,'independently_verified_annotation_offset':False,'independently_verified_drift':False,'independently_verified_action_intervals':0,'nominal_start':origin,'sample_count_definition':'decoded sample frames per channel','sample_count_evidence':count_method,'header_reported_sample_frames':header})
                    if row.example_id=='insert_failure':alignment['audio_nominal_ranges'][n]={'nominal_start':origin,'nominal_end':origin+duration,'alignment_status':'unverified','origin_source':'earliest non-audio timestamp; inferred'}
                    if rid==audio_plot_rid:
                        title='Illustrative raw-recording audio — not verified as action-aligned'
                        times=(np.arange(len(samples))+int(excerpt_start*rate))/rate
                        fig,axes=plt.subplots(channels,1,figsize=(12,3+channels),sharex=True,squeeze=False)
                        # Min/max envelopes in ~3000 bins preserve peaks without giant raster plots.
                        edges=np.linspace(0,len(samples),3001).astype(int)
                        for j,ax in enumerate(axes[:,0]):
                            lo=np.array([samples[a:b,j].min() for a,b in zip(edges[:-1],edges[1:]) if b>a]);hi=np.array([samples[a:b,j].max() for a,b in zip(edges[:-1],edges[1:]) if b>a]);tt=times[edges[:-1]]
                            ax.fill_between(tt,lo,hi,alpha=.7,color='#2166ac');ax.set_ylabel(f'Channel {j}\nDecoded amplitude');ax.grid(alpha=.2)
                        axes[-1,0].set_xlabel('Decoded stream time (s; zero at stream start)');fig.suptitle(title+'\n'+n+' | '+rid,fontsize=12);fig.tight_layout(rect=[0,0,1,.91]);save(fig,f'audio/{n}_waveform.png')
                        fig,axes=plt.subplots(channels,1,figsize=(12,3+channels*2),sharex=True,squeeze=False)
                        for j,ax in enumerate(axes[:,0]):
                            freq,tm,power=spectrogram(samples[:,j],fs=rate,nperseg=512,noverlap=384,scaling='density');db=10*np.log10(np.maximum(power,1e-14));im=ax.pcolormesh(tm+int(excerpt_start*rate)/rate,freq/1000,db,shading='auto',cmap='magma',vmin=-100,vmax=-20);ax.set_ylabel(f'Channel {j}\nFrequency (kHz)');fig.colorbar(im,ax=ax,label='PSD dB re 1 amplitude²/Hz')
                        axes[-1,0].set_xlabel('Decoded stream time (s; zero at stream start)');fig.suptitle(title+'\n'+n+' | '+rid,fontsize=12);fig.tight_layout(rect=[0,0,1,.91]);save(fig,f'audio/{n}_spectrogram.png')
            except (RuntimeError,ValueError,OSError) as error:
                warnings.append(f'Audio unavailable: {rid}/{n}: {error}');missing.append(row.sensor_source_path+'::/'+n)
                audio_rows.append({'recording_id':rid,'stream_name':n,'source_path_or_dataset':row.sensor_source_path+'::/'+n,'container_or_dtype':str(d.dtype),'sample_rate_if_available':'NOT_AVAILABLE','channels':'NOT_AVAILABLE','sample_count':'NOT_AVAILABLE','duration_seconds':'NOT_AVAILABLE','nominal_start_source':'NOT_AVAILABLE','nominal_end':'NOT_AVAILABLE','decoded_successfully':False,'independently_verified_annotation_offset':False,'independently_verified_drift':False,'independently_verified_action_intervals':0})
                detail['error']=str(error)
            decode_details.append(detail)

assert sum(widths.values())==22 and len(schema)==22
csv('sensor_channel_schema.csv',schema);csv('sensor_shapes.csv',shape_rows);csv('frame_selection.csv',frame_rows);csv('video_metadata.csv',video_rows);csv('audio_metadata.csv',audio_rows)
write('sample_label_cards.json',label_cards);write('sample_alignment_timeline.json',alignment);write('audio_decode_evidence.json',decode_details)
gate=json.loads(GATE.read_text());expected={'hama1_audio':(97.31,96.46),'hama2_audio':(96.20,95.48),'hand_audio':(100.,100.)};discrepancies=[]
for n,(a,b) in expected.items():
    v=gate['streams'][n]
    if (round(v['nominal_valid_percent'],2),round(v['nominal_valid_failure_percent'],2),v['nominal_valid_recordings'],v['verified_segments'])!=(a,b,148,0):discrepancies.append(n)
write('audio_alignment_status.json',{'source_path':rel(GATE),'source_sha256':sha(GATE),'actual_source_values':gate,'requested_rounded_percentages':expected,'discrepancies':discrepancies,'audio_alignment_status':'unverified','independently_verified_annotation_offset':False,'independently_verified_drift':False,'independently_verified_action_intervals':0,'action_clock':'Absolute Unix-style timestamps stored in segments_info start/end; video and robot_state are indexed with their timestamps datasets. Hardware clock provenance is not independently established here.','nominal_audio_origin':'Inventory nominal_audio_origin: minimum first timestamp across available non-audio timestamp arrays (src/reassemble/inventory.py). This is an inferred origin, not an audio-to-annotation clock calibration.','why_unverified':'No audio timestamp arrays or dataset clock attributes establish an independently documented offset, drift correction, or action-segment anchor. Header sample counts can disagree with decoded counts. A zero-based decoded sample clock plus an assumed recording origin cannot verify action identity.','why_excluded':'Nominal overlap measures coverage under an assumed origin; it does not prove label-safe extraction of each completed action. Audio was excluded by the timing/coverage prerequisite, not by a predictive-model result.','illustration_recording':audio_plot_rid,'illustration_rule':'Central 10 seconds of each full decoded stream of the lexicographically first selected recording, independent of action timing; no exported audio files.'})
write('recording_contents.json',{'recording_id':selected.iloc[0].recording_id,'filename':selected.iloc[0].source_recording_filename,'top_level_keys':json.loads(rec.loc[selected.iloc[0].recording_id,'top_level_keys']),'available_streams':all_modalities,'one_recording_contains':'Encoded multi-camera video, three encoded audio datasets, timestamp arrays, robot_state sensor arrays, event streams, and segments_info high-level annotations (some with low_level subannotations).','selected_model_input':'One completed action: 16 hand-camera frames and 512 progress positions × 22 sensor scalar channels.','sensor_channel_breakdown':widths,'sensor_schema_recording_id':selected.iloc[0].recording_id,'not_exported':['full recordings','event payloads','audio payloads','private human-review mappings']})
# Confirm preservation across all inventoried raw recording files plus selected encoded media.
raw_after=[stat(p) for p in raw_paths if p.exists()];media_after=[stat(p) for p in video_paths if p.exists()]
assert raw_before==raw_after and media_before==media_after
assert all(sha(REPO/i['path'])==i['sha256'] for i in input_manifest)
write('source_preservation_after.json',{'raw_files':raw_after,'selected_encoded_videos':media_after,'all_unchanged':True})
validation={'cohort_counts_match':True,'deterministic_examples_selected':len(selected),'exactly_eight_action_outcome_strata':len(selected)==8,'selected_identities':selected[['example_id','recording_id','segment_id']].to_dict('records'),'all_displayed_frames_in_interval':all(r['inside_interval'] for r in frame_rows),'frame_selection_rows':len(frame_rows),'expected_frame_selection_rows':168,'example_checks':checks,'every_resampled_array_512x22':all(r['shape']==[512,22] for r in checks),'sensor_scalar_channels':sum(widths.values()),'statistics_values':220,'all_audio_unverified':all(not a['independently_verified_annotation_offset'] and not a['independently_verified_drift'] and a['independently_verified_action_intervals']==0 for a in audio_rows),'raw_source_size_mtime_unchanged':raw_before==raw_after,'raw_files_checked':len(raw_before),'encoded_media_size_mtime_unchanged':media_before==media_after,'input_hashes_unchanged':True,'source_labels_match_frozen_cohort':True,'audio_gate_values_match_requested_rounded_values':not discrepancies,'privacy_review':'PENDING visual inspection before packaging','missing_assets':missing,'warnings':warnings,'training_run':False,'model_inference_run':False,'label_changes':False,'task4_executed':False}
write('validation_pending.json',validation)
write('provenance.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'git_status_at_start':subprocess.check_output(['git','status','--short','--untracked-files=no'],cwd=REPO,text=True).strip(),'command':'ma_thesis_env/bin/python -B '+rel(Path(__file__)),'software_versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'h5py':h5py.__version__,'opencv':cv2.__version__,'matplotlib':matplotlib.__version__,'soundfile':sf.__version__},'raw_data_mode':'HDF5 r; existing encoded videos read-only; audio decoded in memory','write_root':rel(OUT),'source_code_changes':False,'models_imported_or_run':False,'existing_worktree_note':'Pre-existing deletion: src/shared/README.md; left unchanged.'})
print('ASSETS BUILT; privacy review and packaging pending',flush=True)
print(json.dumps({'output':rel(OUT),'channel_breakdown':widths,'video_metadata':video_rows,'audio_records':len(audio_rows),'missing':missing,'warnings':warnings},default=clean),flush=True)
