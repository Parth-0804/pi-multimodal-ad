"""Blinded sample/export and human-return ingestion. Never generates human ratings."""
import argparse,csv,json,os,shutil,uuid
from pathlib import Path
import numpy as np
import pandas as pd
import cv2,h5py
from .common import read,write,textfile,csvfile,config_for,freeze_revision,digest,now
from .numerical import load_cohort

RATING_COLUMNS=['review_id','reviewer_id','judged_outcome','boundary_quality','visibility','artifact_flag','short_reason']
ENUMS={'judged_outcome':{'success','failure','cannot_determine'},'boundary_quality':{'acceptable','questionable','cannot_determine'},'visibility':{'adequate','partial','insufficient'},'artifact_flag':{'none','possible','cannot_determine'}}

def sample_cases(frame,seed=20260928):
 rng=np.random.default_rng(seed);selected=[];support=[]
 for action in ['pick','insert','remove','place']:
  for outcome in [0,1]:
   part=frame[(frame.action==action)&(frame.failure==outcome)].sort_values(['recording_id','segment_id']);groups=np.array(sorted(part.recording_id.unique()))
   if len(part)<8:raise ValueError('Insufficient stratum segments: retain blocker, no altered sample')
   chosen=rng.choice(groups,size=min(8,len(groups)),replace=False);indices=[]
   for rid in chosen:
    pool=part[part.recording_id==rid].index.to_numpy();indices.append(int(rng.choice(pool)))
   if len(indices)<8:
    pool=part.index.difference(indices).sort_values().to_numpy();indices+=rng.choice(pool,size=8-len(indices),replace=False).tolist()
   selected.extend(indices);support.append({'action':action,'recorded_failure':outcome,'eligible_segments':len(part),'eligible_recordings':len(groups),'sampled_recordings':part.loc[indices].recording_id.nunique(),'fallback_used':len(groups)<8})
 result=frame.loc[selected].copy().reset_index(drop=True);assert len(result)==64 and not result.duplicated(['recording_id','segment_id']).any()
 rngid=np.random.default_rng(20260929);result['review_id']=['R'+rngid.bytes(8).hex() for _ in range(len(result))];assert result.review_id.nunique()==64
 return result,support

def blank_sheets(sample):
 public=sample[['review_id','action']].copy();public['clip_file']=public.review_id+'.mp4'
 for col in RATING_COLUMNS:
  if col not in public:public[col]=''
 sheets={}
 for name,seed in [('A',20260930),('B',20260931)]:
  sheet=public.iloc[np.random.default_rng(seed).permutation(len(public))].reset_index(drop=True).copy();sheet['reviewer_id']=name;sheets[name]=sheet
 return sheets

def validate_sheet(sheet,key):
 if not set(RATING_COLUMNS)<=set(sheet):raise ValueError('Missing required columns')
 if sheet.review_id.duplicated().any() or set(sheet.review_id)!=set(key.review_id):raise ValueError('Unknown, missing, or duplicate review IDs')
 for col,allowed in ENUMS.items():
  if not set(sheet[col])<=allowed:raise ValueError('Incomplete or invalid ratings: '+col)
 if sheet.reviewer_id.astype(str).str.strip().eq('').any() or sheet.reviewer_id.nunique()!=1:raise ValueError('One named reviewer per complete sheet required')
 if sheet.short_reason.astype(str).str.strip().eq('').any():raise ValueError('Reason required for each case')
 return sheet.merge(key,on='review_id',validate='one_to_one',suffixes=('','_key'))

def wilson(k,n):
 if n==0:return [None,None]
 z=1.959963984540054;p=k/n;d=1+z*z/n;a=(p+z*z/(2*n))/d;b=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [float(a-b),float(a+b)]

def agreement(joined):
 rows=[]
 for (action,failure),q in joined.groupby(['action_key' if 'action_key' in joined else 'action','failure'],sort=True):
  target=np.where(q.failure==1,'failure','success');determinate=q.judged_outcome!='cannot_determine';correct=int((q.judged_outcome.to_numpy()==target).sum());n=len(q);nd=int(determinate.sum())
  rows.append({'action':action,'recorded_failure':int(failure),'n_presented':n,'n_determinate':nd,'cannot_determine':n-nd,'agreement_numerator':correct,'all_cases_denominator':n,'determinate_denominator':nd,'agreement_all_cases':correct/n if n else None,'agreement_determinate':correct/nd if nd else None,'determinate_wilson_descriptive_95':wilson(correct,nd),'boundary_questionable':int((q.boundary_quality=='questionable').sum()),'boundary_cannot_determine':int((q.boundary_quality=='cannot_determine').sum()),'visibility_insufficient':int((q.visibility=='insufficient').sum()),'artifact_possible':int((q.artifact_flag=='possible').sum())})
 return rows

def interrater(a,b):
 x=a[['review_id','judged_outcome']].merge(b[['review_id','judged_outcome']],on='review_id',validate='one_to_one',suffixes=('_A','_B'))
 labels=['success','failure','cannot_determine'];matrix=np.array([[int(((x.judged_outcome_A==u)&(x.judged_outcome_B==v)).sum()) for v in labels] for u in labels]);n=matrix.sum();po=float(np.trace(matrix)/n);pe=float(np.dot(matrix.sum(0),matrix.sum(1))/n**2);kappa=None if np.isclose(pe,1) else (po-pe)/(1-pe)
 det=(x.judged_outcome_A!='cannot_determine')&(x.judged_outcome_B!='cannot_determine');agree=int((x.loc[det,'judged_outcome_A']==x.loc[det,'judged_outcome_B']).sum())
 return {'categories':labels,'matrix':matrix.tolist(),'three_category_numerator':int(np.trace(matrix)),'three_category_denominator':int(n),'three_category_agreement':po,'cohens_kappa':kappa,'both_determinate_agreement_numerator':agree,'both_determinate_denominator':int(det.sum()),'at_least_one_cannot_determine':int((~det).sum()),'kappa_note':'Undefined when expected agreement is1; independent reviewers required; no claim of physical truth.'}

def ingest(run,sheets,key_path):
 key=pd.read_csv(key_path,dtype={'review_id':str,'recording_id':str,'segment_id':str});validated=[]
 for path in sheets:
  sheet=pd.read_csv(path,keep_default_na=False,dtype=str);validated.append(validate_sheet(sheet,key))
 ids=[x.reviewer_id.iloc[0] for x in validated]
 if len(set(ids))!=len(ids):raise ValueError('Two sheets cannot impersonate two independent raters with the same reviewer ID')
 dest=Path(run)/'04_human_review/submissions'/(now().replace(':','').replace('+','_')+'_'+uuid.uuid4().hex[:8]);dest.mkdir(parents=True,exist_ok=False)
 for i,path in enumerate(sheets):
  target=dest/f'reviewer_{i+1}_submitted.csv';shutil.copyfile(path,target);os.chmod(target,0o444)
 summary={'status':'HUMAN_RETURNS_RECEIVED_NOT_ADJUDICATED','reviewers':[{'reviewer_id':x.reviewer_id.iloc[0],'strata':agreement(x),'agreement_numerator':int((x.judged_outcome==np.where(x.failure==1,'failure','success')).sum()),'all_cases_denominator':len(x),'determinate_denominator':int((x.judged_outcome!='cannot_determine').sum()),'presented':len(x),'cannot_determine':int((x.judged_outcome=='cannot_determine').sum())} for x in validated],'interrater':interrater(validated[0],validated[1]) if len(validated)==2 else None,'limitations':'Recording-spread balanced64-case qualitative audit, not a random cohort sample. Wilson intervals are descriptive binomial summaries, not population annotation-error intervals or full clustered uncertainty. Agreement is not physical ground truth. No cohort relabeling or performance re-evaluation.','submission_hashes':[{'original_path':str(p),'sha256':digest(p)} for p in sheets]}
 flags=any(((x.boundary_quality!='acceptable')|(x.judged_outcome!=np.where(x.failure==1,'failure','success'))|(x.artifact_flag!='none')).any() for x in validated);summary['adjudication_requested']=bool(flags)
 write(dest/'analysis.json',summary)
 if flags:textfile(dest/'ADJUDICATION_REQUEST.md','# Adjudication request\n\nSubmitted ratings contain disagreement, indeterminate outcomes, boundary concerns or possible artifacts. Inspect the preserved submissions and private key. Only a separately approved correction protocol may change labels or recompute model performance. No historical prediction or target has been changed.')
 print(str(dest))
 return dest

def prepare(c):
 root=Path(c['run']);out=root/'04_human_review';freeze_revision(root,'human_preparation_before_sample');frame,_=load_cohort(c);sample,support=sample_cases(frame,c['human']['sample_seed'])
 cache=Path(c['data_root'])/'cache/final_validity_audit'/root.name
 cache.mkdir(parents=True,exist_ok=False);private=cache/'private';private.mkdir(mode=0o700);blind=cache/'blind_review';blind.mkdir();clips=blind/'clips';clips.mkdir()
 csvfile(private/'source_label_key.csv',sample.to_dict('records'));os.chmod(private/'source_label_key.csv',0o600)
 sheets=blank_sheets(sample)
 for name,sheet in sheets.items():
  sheet.to_csv(out/f'reviewer_{name}_blank.csv',index=False);sheet.to_csv(blind/f'reviewer_{name}_blank.csv',index=False)
 instructions='''# Independent human review — completed action clips

Please ask the thesis author (reviewer A) and preferably a second technically informed person (reviewer B) to review independently, without reading each other's answers. Use only this blind_review directory; do not consult the source/label key or model scores. The sheets contain the same64 cases in different orders. Action is supplied as task context; recorded outcome and predictions are hidden. No author/expertise credentials are implied by A/B identifiers.

For each in-segment silent clip fill every field:
- judged_outcome: success / failure / cannot_determine.
- boundary_quality: acceptable / questionable / cannot_determine.
- visibility: adequate / partial / insufficient.
- artifact_flag: none / possible / cannot_determine.
- short_reason: brief explanation, including uncertainty or evidence that a boundary is questionable.

Keep review_id unchanged. Use the supplied reviewer_id or replace it consistently with your own identifier. Do not force a success/failure when evidence is insufficient. Playback is a compact copy of the actual hand-camera frames inside the annotated scored interval. No audio, context extension, synthetic image, annotation overlay, predicted score or outcome label is added. A clip cannot establish everything that happened before/after its interval. Failure consequences visible inside the interval may be legitimate evidence for retrospective outcome classification.

Encoding may soften small details. The copy preserves every decoded in-segment frame; playback cadence is set from source timestamps to preserve the observed total duration. Uneven native frame intervals are displayed at their average cadence, so small local timing variations are a limitation. Do not infer exact event timing from the compact copy. Flag decoding/visibility problems; no difficult case has been deliberately replaced.

Blinding is limited: source content or prior familiarity may reveal context. This is a balanced, recording-spread qualitative audit, not a random estimate of population annotation error. Human agreement is not proof of physical ground truth. Do not inspect other reviewers' answers, relabel the model cohort, tune thresholds or remove disputed cases.

Return your completed CSV to the thesis author. The ingestion command listed in HUMAN_REVIEW_STATUS.md validates and preserves submitted bytes. The automated agent will never supply ratings or invent a second reviewer.
'''
 textfile(out/'REVIEWER_INSTRUCTIONS.md',instructions);textfile(blind/'REVIEWER_INSTRUCTIONS.md',instructions)
 repeated=sample.groupby('recording_id').size();csvfile(out/'sample_support.csv',support)
 # Budget estimate uses duration and a conservative 2 Mbit/s presentation estimate.
 duration=float((sample.end-sample.start).sum());estimate=int(duration*2_000_000/8);free=shutil.disk_usage(cache).free
 budget=c['human']['maximum_bytes'];cv2.setNumThreads(1);metadata=[];total=0
 # No ffmpeg/PyAV/libx264 is installed. OpenCV's MPEG4 codec requires no install/GPU.
 encoding_sources=[]
 codec='mp4v';status='READY_FOR_HUMAN_REVIEW' if free>=30*1024**3 and estimate<=budget else 'ENCODING_DEFERRED_RESOURCE_LIMIT'
 records=pd.read_parquet(Path(c['sources']['inventory'])/'recordings.parquet').set_index('recording_id')
 if status=='READY_FOR_HUMAN_REVIEW':
  for row in sample.itertuples():
   if shutil.disk_usage(cache).free<30*1024**3:status='ENCODING_DEFERRED_RESOURCE_LIMIT';break
   rec=records.loc[row.recording_id];source=Path(c['data_root'])/'cache/encoded_media'/rec['sha256']/'hand.mp4'
   with h5py.File(Path(c['data_root'])/'raw/data'/rec['filename'],'r') as h:
    times=np.asarray(h['timestamps/hand'][()],float)
    if times.ndim==2:times=times[:,0]
   ix=np.flatnonzero((times>=row.start)&(times<=row.end));assert len(ix)>1 and np.all(np.diff(ix)==1)
   cap=cv2.VideoCapture(str(source));cap.set(cv2.CAP_PROP_POS_FRAMES,int(ix[0]));sourcefps=float(cap.get(cv2.CAP_PROP_FPS));fps=float((len(ix)-1)/(times[ix[-1]]-times[ix[0]]));width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));scale=min(1.,c['human']['max_width']/width);size=(int(width*scale)//2*2,int(height*scale)//2*2)
   assert cap.isOpened() and int(round(cap.get(cv2.CAP_PROP_POS_FRAMES)))==int(ix[0]),'Source frame seek failed'
   output=clips/(row.review_id+'.mp4');writer=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*codec),fps,size)
   if not writer.isOpened():raise RuntimeError('Installed CPU video encoder unavailable; keep sample and defer encoding')
   written=0;decode_problem=False
   for index in ix:
    if int(round(cap.get(cv2.CAP_PROP_POS_FRAMES)))!=int(index):decode_problem=True;break
    ok,img=cap.read()
    if not ok:decode_problem=True;break
    if size!=(width,height):img=cv2.resize(img,size,interpolation=cv2.INTER_AREA)
    writer.write(img);written+=1
   writer.release();cap.release()
   # Verify exported content length and frame rate without replacing any sampled case.
   verify=cv2.VideoCapture(str(output));n=int(verify.get(cv2.CAP_PROP_FRAME_COUNT));outputfps=float(verify.get(cv2.CAP_PROP_FPS));verify.release()
   good=not decode_problem and n==written==len(ix);total+=output.stat().st_size
   timing=float(np.max(abs((times[ix]-times[ix[0]])-np.arange(len(ix))/fps)))
   encoding_sources.append({'review_id':row.review_id,'source_video':str(source),'raw_recording_sha256':str(rec['sha256']),'first_frame':int(ix[0]),'last_frame':int(ix[-1]),'frame_timestamp_first':float(times[ix[0]]),'frame_timestamp_last':float(times[ix[-1]]),'source_frame_count':len(times)})
   metadata.append({'review_id':row.review_id,'action':row.action,'clip_file':'clips/'+output.name,'sha256':digest(output),'bytes':output.stat().st_size,'frames':written,'codec':codec,'output_fps':outputfps,'presentation_max_timestamp_deviation_seconds':timing,'source_container_fps':sourcefps,'status':'VERIFIED_DECODE_COUNT' if good else 'DECODE_LIMITATION','audio_included':False})
   if not good:status='REVIEW_EXPORT_HAS_DECODING_LIMITATIONS'
   if total>budget:raise RuntimeError('Clip budget exceeded; no deletion/replacement. Stop substantial writes and document.')
   print('REVIEW_CLIP',len(metadata),64,round(total/2**20,1),'MiB',flush=True)
 write(private/'encoding_sources.json',encoding_sources);os.chmod(private/'encoding_sources.json',0o600)
 # Public export omits source recording/timestamps, recorded labels and scores.
 public=[{k:v for k,v in entry.items() if k in ['review_id','action','clip_file','sha256','bytes','frames','status','audio_included']} for entry in metadata]
 write(blind/'review_export_manifest.json',{'cases':public,'expected_cases':64,'export_status':status,'blinding_limit':'Source content/prior familiarity may reveal context; no recorded outcome or model result exported.'})
 write(out/'review_export_manifest.json',{'human_status':'PENDING_HUMAN_REVIEW','export_status':status,'blind_package_path':str(blind),'restricted_key_path':str(private/'source_label_key.csv'),'source_key_not_in_blind_package':True,'expected_cases':64,'encoded_cases':len(metadata),'estimated_bytes':estimate,'actual_bytes':total,'maximum_bytes':budget,'free_GiB_before':free/2**30,'recordings_repeated_across_strata':int((repeated>1).sum()),'maximum_cases_per_recording':int(repeated.max()),'clip_timing_and_identity':metadata,'codec_deviation':'H264/ffmpeg/PyAV encoders unavailable in installed environment. Used installed OpenCV MPEG4 mp4v; no package installation. Every in-segment frame retained with timestamp-derived average cadence, timing deviations recorded.','sample_scheme':'8 per action×recorded-outcome; recording-spread stratified qualitative sample, not population random sample'})
 textfile(out/'HUMAN_REVIEW_STATUS.md','# Human review status\n\n**PENDING_HUMAN_REVIEW**\n\nNo human ratings have been received, invented or inferred by the agent.\n\nBlind package: `'+str(blind)+'`. Reviewer A and B sheets contain the same64 cases in different orders. Share only blind_review with reviewers; its clips and sheets omit recorded labels and model outputs. The separate private key is restricted and outside Git.\n\nExport status: '+status+'. Encoded '+str(len(metadata))+'/64 clips; '+str(round(total/2**20,2))+' MiB.\n\nThe thesis author and preferably one other technically informed person should complete sheets independently. Return workflow (only after actual submissions):\n\n```bash\nOPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. ma_thesis_env/bin/python -B -m scripts.thesis.final_validity_audit.human_review ingest --run '+str(root)+' --key '+str(private/'source_label_key.csv')+' --sheet PATH_TO_COMPLETED_A.csv --sheet PATH_TO_COMPLETED_B.csv\n```\n\nOne real reviewer is accepted and reported as one; do not invent the second. New immutable submissions/analysis are saved in timestamped subdirectories. This does not overwrite the audit snapshot, relabel the cohort, recompute model performance or automatically approve correction. Annotation/boundary disagreements trigger an adjudication request. Automated work continues while human review remains pending.')
 print('HUMAN_EXPORT_PREPARED',str(blind),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);a=sub.add_parser('prepare');a.add_argument('--run',required=True);b=sub.add_parser('ingest');b.add_argument('--run',required=True);b.add_argument('--key',required=True);b.add_argument('--sheet',action='append',required=True);args=p.parse_args()
 if args.mode=='prepare':prepare(config_for(args.run))
 else:
  if len(args.sheet)>2:raise ValueError('At most two independently returned sheets')
  ingest(args.run,args.sheet,args.key)
