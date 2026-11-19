"""Only original local CNN backbone; mean pooling; final-stage gradients."""
import gc,os,time,random
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
from transformers import RTDetrForObjectDetection
from common import ROOT,REPO,config,read,write,sha,signature,event,resources
from data import load_cohort
from pixel_access import input_pixels as pixels
torch.set_num_threads(4)
torch.backends.cudnn.benchmark=False
torch.backends.cudnn.deterministic=True
torch.backends.cuda.matmul.allow_tf32=False
torch.use_deterministic_algorithms(True)

def original(device='cuda'):
 c=config();folder=REPO/c['weights_dir']
 for name,identity in read(ROOT/'provenance/original_pretrained_identity.json')['weights'].items():assert sha(folder/name)==identity['sha256'],'ORIGINAL_PRETRAINED_DRIFT '+name
 wrapper=RTDetrForObjectDetection.from_pretrained(folder,local_files_only=True)
 backbone=wrapper.model.backbone.model;backbone.eval();backbone.requires_grad_(False)
 assert hasattr(backbone.encoder,'stages') and len(backbone.encoder.stages)==4
 del wrapper
 return backbone.to(device)
def pooled(backbone,x):
 maps=backbone(x).feature_maps
 assert len(maps)>0
 return torch.cat([m.float().mean((-2,-1)) for m in maps],dim=-1)
class Head(nn.Module):
 def __init__(self,width):
  super().__init__();self.projection=nn.Sequential(nn.Linear(width,128),nn.ReLU(),nn.Dropout(.1));self.classifier=nn.Linear(128,1)
 def forward(self,z):return self.classifier(self.projection(z)).squeeze(-1)
class Visual(nn.Module):
 def __init__(self,backbone,width,mean,std,adapted):
  super().__init__();self.backbone=backbone;self.adapted=adapted
  if backbone is not None:
   backbone.requires_grad_(False)
   if adapted:backbone.encoder.stages[-1].requires_grad_(True)
  self.head=Head(width)
  self.register_buffer('mean',torch.as_tensor(mean,dtype=torch.float32));self.register_buffer('std',torch.as_tensor(std,dtype=torch.float32))
 def train(self,mode=True):
  super().train(mode)
  if self.backbone is not None:self.backbone.eval()
  return self
 def forward(self,x):
  if self.backbone is not None:
   B,F=x.shape[:2];z=pooled(self.backbone,x.flatten(0,1)).reshape(B,F,-1).mean(1)
  else:z=x
  return self.head(torch.nan_to_num((z-self.mean)/self.std,nan=0,posinf=0,neginf=0))
def optimizer(model):
 c=config();groups=[{'params':model.head.parameters(),'lr':c['head_lr']}]
 if model.adapted:groups.append({'params':model.backbone.encoder.stages[-1].parameters(),'lr':c['final_stage_lr']})
 return torch.optim.AdamW(groups,weight_decay=c['weight_decay'])
def model_state(model):
 return {'head':{k:v.detach().cpu() for k,v in model.head.state_dict().items()},
         'stage':{k:v.detach().cpu() for k,v in model.backbone.encoder.stages[-1].state_dict().items()} if model.adapted else None,
         'mean':model.mean.detach().cpu(),'std':model.std.detach().cpu()}
def restore_model(state,width,adapted,seed):
 b=original() if adapted else None
 torch.manual_seed(seed)
 m=Visual(b,width,state['mean'],state['std'],adapted).cuda();m.head.load_state_dict(state['head'])
 if adapted:m.backbone.encoder.stages[-1].load_state_dict(state['stage'])
 return m
def snapshot_named(module):return {n:sha_tensor(p) for n,p in module.state_dict().items()}
def sha_tensor(t):
 import hashlib
 return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
def resume_check(model,opt,x,saved,width,job,expected):
 """One additional disposable update, replaying the original second update."""
 c=config();state=read(ROOT/'progress.json');count=state['preflight_optimizer_steps'];assert count<c['preflight_step_cap']
 event('CHECKPOINT_RESUME_PREFLIGHT',preflight_optimizer_steps=count+1)
 d=torch.load(saved,map_location='cpu',weights_only=True)
 replay=restore_model(d['model'],width,True,job['seed']).train();optimizer_replay=optimizer(replay);optimizer_replay.load_state_dict(d['optimizer'])
 assert d['precision']=='float32' and d['next_sample_id']==expected['sample_id'] and d['epoch']==0 and d['next_batch']==1
 torch.set_rng_state(d['torch_rng']);torch.cuda.set_rng_state_all(d['cuda_rng']);random.setstate(d['python_rng'])
 optimizer_replay.zero_grad(set_to_none=True);out=replay(x)
 loss=nn.functional.binary_cross_entropy_with_logits(out,torch.tensor([expected['label']],device='cuda',dtype=torch.float32));loss.backward();nn.utils.clip_grad_norm_(replay.parameters(),c['gradient_clip']);optimizer_replay.step();torch.cuda.synchronize()
 assert snapshot_named(replay)==snapshot_named(model),'RESUME_PARAMETER_MISMATCH'
 for key,value in opt.state_dict()['state'].items():
  for name,v in value.items():
   other=optimizer_replay.state_dict()['state'][key][name]
   assert torch.equal(v.detach().cpu(),other.detach().cpu()) if torch.is_tensor(v) else v==other
 assert torch.equal(torch.get_rng_state(),expected['torch_rng'])
 assert all(torch.equal(a,b) for a,b in zip(torch.cuda.get_rng_state_all(),expected['cuda_rng']))
 result={'passed':True,'sample_id':expected['sample_id'],'optimizer_state_exact':True,'parameter_state_exact':True,'CPU_and_CUDA_rng_exact':True,'epoch':d['epoch'],'next_batch':d['next_batch'],'precision':d['precision'],'extra_disposable_optimizer_steps':1,'checkpoint_sha256':sha(saved)}
 del replay,optimizer_replay,d;gc.collect();torch.cuda.empty_cache();return result
def preflight():
 if (ROOT/'checks/gradient_preflight.json').exists():
  assert read(ROOT/'checks/gradient_preflight.json')['passed'];return
 c=config();frame=load_cohort();jobs=read(ROOT/'data_manifests/fit_partitions.json');job=next(j for j in jobs if j['outer_fold_original']==0 and j['role']=='outer_assessment')
 row=job['G'][0];sample=frame.iloc[row].to_dict();results=[]
 for condition in c['conditions']:
  frames=32 if '32' in condition else 16;adapted=condition.startswith('fine_tuned')
  b=original();x=pixels(sample,frames).unsqueeze(0).cuda()
  with torch.no_grad():feature=pooled(b,x.flatten(0,1));width=feature.shape[-1]
  assert width>0
  torch.manual_seed(job['seed']);m=Visual(b,width,np.zeros(width),np.ones(width),adapted).cuda().train();opt=optimizer(m)
  before=snapshot_named(b);head_before=snapshot_named(m.head);observed=set()
  handles=[mod.register_forward_hook(lambda mod,args,out:observed.add(type(mod).__name__)) for mod in b.modules()]
  torch.cuda.reset_peak_memory_stats();timings=[];grads={};resume_evidence=None
  for step in range(2):
   state=read(ROOT/'progress.json');count=state['preflight_optimizer_steps'];assert count<c['preflight_step_cap']
   event('GRADIENT_PREFLIGHT',condition=condition,preflight_optimizer_steps=count+1)
   torch.cuda.synchronize();t=time.perf_counter();opt.zero_grad(set_to_none=True);out=m(x)
   loss=nn.functional.binary_cross_entropy_with_logits(out,torch.tensor([int(sample['failure'])],device='cuda',dtype=torch.float32));loss.backward()
   assert torch.isfinite(loss)
   grads={n:{'finite':bool(torch.isfinite(p.grad).all()),'nonzero':bool(torch.count_nonzero(p.grad))} for n,p in m.named_parameters() if p.grad is not None}
   assert grads and all(v['finite'] for v in grads.values())
   assert all(n.startswith('head.') or (adapted and n.startswith('backbone.encoder.stages.3.')) for n in grads)
   assert any(v['nonzero'] for n,v in grads.items() if n.startswith('head.'))
   if adapted:assert any(v['nonzero'] for n,v in grads.items() if n.startswith('backbone.encoder.stages.3.'))
   nn.utils.clip_grad_norm_(m.parameters(),c['gradient_clip']);opt.step();torch.cuda.synchronize();timings.append(time.perf_counter()-t)
   if condition=='fine_tuned_32_frames' and step==0:
    resume_path=ROOT/'checks/disposable_resume_after_step1.pt'
    torch.save({'model':model_state(m),'optimizer':opt.state_dict(),'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),'python_rng':random.getstate(),'epoch':0,'next_batch':1,'precision':'float32','next_sample_id':sample['sample_id']},resume_path)
  for h in handles:h.remove()
  after=snapshot_named(b);changed=[n for n in before if before[n]!=after[n]]
  assert all(n.startswith('encoder.stages.3.') for n in changed)
  assert not any('running_' in n or 'num_batches_tracked' in n for n in changed)
  if adapted:assert changed
  else:assert not changed
  assert head_before!=snapshot_named(m.head)
  assert all(not mod.training for mod in b.modules())
  assert not any(any(word in n.lower() for word in ['transformer','attention','decoder']) for n in observed)
  if condition=='fine_tuned_32_frames':
   expected={'sample_id':sample['sample_id'],'label':int(sample['failure']),'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all()}
   resume_evidence=resume_check(m,opt,x,resume_path,width,job,expected);write(ROOT/'checks/checkpoint_resume_preflight.json',resume_evidence)
  # Same model serialized compactly; reload on same training sample, no optimization.
  state=model_state(m);saved=ROOT/'checks'/('disposable_'+condition+'.pt');torch.save(state,saved)
  m.eval()
  with torch.no_grad():expected=m(x).detach().cpu()
  if adapted:reloaded=restore_model(torch.load(saved,map_location='cpu',weights_only=True),width,True,job['seed'])
  else:
   bb=original();torch.manual_seed(job['seed']);reloaded=Visual(bb,width,state['mean'],state['std'],False).cuda();reloaded.head.load_state_dict(state['head'])
  reloaded.eval()
  with torch.no_grad():actual=reloaded(x).detach().cpu()
  error=float((expected-actual).abs().max());assert error<=c['probability_replay_tolerance']
  results.append({'condition':condition,'train_sample_id':sample['sample_id'],'training_only_G':True,'feature_width':width,'observed_forward_classes':sorted(observed),'gradient_parameters':grads,'changed_backbone_names':changed,'head_changed':True,'BN_buffers_unchanged':True,'total_backbone_parameters':sum(p.numel() for p in b.parameters()),'trainable_backbone_parameters':sum(p.numel() for p in b.parameters() if p.requires_grad),'head_parameters':sum(p.numel() for p in m.head.parameters()),'seconds_per_single_segment_update':timings,'peak_cuda_bytes':torch.cuda.max_memory_allocated(),'compact_reload_logit_max_abs':error,'model_path':str(saved.relative_to(ROOT)),'model_sha256':sha(saved)})
  del m,opt,b,x,reloaded,state;gc.collect();torch.cuda.empty_cache()
  write(ROOT/'checks/gradient_preflight_partial.json',{'results':results})
 write(ROOT/'checks/gradient_preflight.json',{'passed':True,'optimizer_steps':read(ROOT/'progress.json')['preflight_optimizer_steps'],'precision':'float32','microbatch_segments':1,'results':results,'checkpoint_resume':read(ROOT/'checks/checkpoint_resume_preflight.json'),'final_stage_name':'backbone.encoder.stages.3','wall_cap_seconds':None,'timing_limit':'Single-segment disposable updates include launch/optimizer overhead; broad full-fit estimate, not completion guarantee','prefix_cache':'NOT_USED; original full CNN recomputed for adapted arm'})
 estimates=[]
 for result in results:
  count=sum(len(j['G'])*c['epochs'] for j in jobs)
  estimates.append({'condition':result['condition'],'planned_visual_fits':len(jobs),'segment_presentations':count,'single_segment_update_mean_seconds':float(np.mean(result['seconds_per_single_segment_update'])),'estimated_raw_fit_seconds_upper_including_per_segment_optimizer_overhead':float(np.mean(result['seconds_per_single_segment_update']))*count,'peak_preflight_cuda_bytes':result['peak_cuda_bytes'],'expected_compact_weights_bytes_all_fits':result['trainable_backbone_parameters']*4*len(jobs)+result['head_parameters']*4*len(jobs)})
 write(ROOT/'checks/training_resource_estimate.json',{'estimates':estimates,'total_planned_visual_fits':len(jobs)*4,'sensor_fits':len(jobs),'wall_cap_seconds':None,'maximum_full_visual_fits':c['full_visual_fit_cap'],'storage_ceiling_bytes':c['new_storage_cap_bytes'],'pixel_disk_cache_cap_bytes':c['pixel_cache_cap_bytes'],'pixel_RAM_cap_bytes':c['pixel_RAM_cap_bytes'],'host_memory_ceiling_bytes':c['host_memory_ceiling_bytes'],'uncertainties':'Training-only one-segment timings include optimizer overhead each segment, unlike accumulated fitting; random decode/cache misses, inference and I/O add variable cost. Estimate is not a completion promise. Final scientific fits always start independently from original pretrained weights.'})
 event('GRADIENT_PREFLIGHT_PASSED',conditions=4)
def extract_features():
 extraction={'cohort_sha256':sha(ROOT/'data_manifests/cohort_and_frames.json'),'config_sha256':sha(ROOT/'config/resolved_config.json'),'weights_identity_sha256':sha(ROOT/'provenance/original_pretrained_identity.json'),'sources':{n:sha(ROOT/'source'/n) for n in ['common.py','data.py','visual_model.py','pixel_access.py']}}
 identity_path=ROOT/'shared_cache/original_feature_extraction_identity.json'
 if identity_path.exists():assert read(identity_path)==extraction,'ORIGINAL_FEATURE_SOURCE_DRIFT'
 else:write(identity_path,extraction)
 extraction_id=signature(extraction)
 if (ROOT/'shared_cache/frozen_features_complete.json').exists():
  d=read(ROOT/'shared_cache/frozen_features_complete.json')
  for name,h in d['hashes'].items():assert sha(ROOT/name)==h
  return
 frame=load_cohort();b=original();rows=[];row_costs=[];started=time.perf_counter();width=None
 for i,s in frame.iterrows():
  p=ROOT/'shared_cache/original_features'/str(s['recording_id'])/(s['sample_id']+'.npz');p.parent.mkdir(parents=True,exist_ok=True)
  metadata=p.with_suffix('.json')
  if p.exists():
   d=read(metadata);assert d['extraction_id']==extraction_id and sha(p)==d['sha256'],'ORIGINAL_FEATURE_ROW_IDENTITY_DRIFT'
   with np.load(p,allow_pickle=False) as z:f16=z['f16'];f32=z['f32']
   cost=d['cost']
  else:
   row_started=time.perf_counter();x=pixels(s.to_dict(),32).cuda();loaded=time.perf_counter();cost={'pixel_loading_cache_transfer_seconds':loaded-row_started}
   # Use each condition's actual frame batch and Torch reduction, matching the
   # live forward path rather than introducing a NumPy/GPU reduction difference.
   with torch.inference_mode():
    start16=time.perf_counter()
    f16=pooled(b,x[s['positions16_in32']]).mean(0).cpu().numpy()
    cost['CNN16_pool_transfer_wall_seconds']=time.perf_counter()-start16;start32=time.perf_counter()
    f32=pooled(b,x).mean(0).cpu().numpy()
    cost['CNN32_pool_transfer_wall_seconds']=time.perf_counter()-start32
   tmp=p.with_suffix('.writing.npz');np.savez_compressed(tmp,f16=f16,f32=f32);os.replace(tmp,p)
   cost['row_total_wall_seconds']=time.perf_counter()-row_started
   write(metadata,{'sample_id':s['sample_id'],'extraction_id':extraction_id,'sha256':sha(p),'cost':cost})
  if width is None:width=len(f16)
  assert len(f16)==len(f32)==width and np.isfinite(f16).all() and np.isfinite(f32).all()
  rows.append((f16,f32));row_costs.append(cost)
  if (i+1)%25==0:event('EXTRACTING_ORIGINAL_FEATURES',rows=i+1,total=len(frame),elapsed_seconds=time.perf_counter()-started,storage=resources())
 for j,n in enumerate([16,32]):np.save(ROOT/f'shared_cache/original_features_{n}.npy',np.stack([x[j] for x in rows]).astype('float32'),allow_pickle=False)
 d={'feature_width':width,'precision':'float32','samples':len(frame),'seconds_this_invocation':time.perf_counter()-started,'seconds':sum(z['row_total_wall_seconds'] for z in row_costs),'cost_totals':{key:sum(z[key] for z in row_costs) for key in row_costs[0]},'CNN_parameters':sum(p.numel() for p in b.parameters()),'feature_selection':list(b.out_features),'pooling':'Same 16/32 frame batch shape and Torch float32 spatial/frame means as live forward','source_sha256':sha(ROOT/'source/visual_model.py'),'hashes':{f'shared_cache/original_features_{n}.npy':sha(ROOT/f'shared_cache/original_features_{n}.npy') for n in [16,32]}}
 write(ROOT/'provenance/original_feature_extraction_cost.json',d)
 write(ROOT/'shared_cache/frozen_features_complete.json',d);del b;gc.collect();torch.cuda.empty_cache()
 event('ORIGINAL_FEATURES_READY',feature_width=width)
