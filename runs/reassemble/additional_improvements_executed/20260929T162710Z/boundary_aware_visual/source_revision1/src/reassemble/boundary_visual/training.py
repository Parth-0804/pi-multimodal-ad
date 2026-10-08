"""Fixed bounded heads, historical seed policy, training-only scaling/calibration."""
from pathlib import Path
import json,time
import numpy as np,torch
from torch import nn
from sklearn.metrics import average_precision_score
from reassemble.section1_models import Standardizer,neural_fit,calibrate,sigmoid
from reassemble.section1b import guard_partition
from .models import make,aggregate
from .common import read,write,identity,sha,atomic_npz,storage

def fit(run,location,variant,x,mean,y,train,test,candidates,base,seed,pause):
 pause();folder=run/'fits'/location;folder.mkdir(parents=True,exist_ok=True)
 signature={'variant':variant,'seed':seed,'train':train.tolist(),'predict':test.tolist(),'candidates':candidates,'config':sha(run/'config.json'),'implementation':read(run/'source_signature.json')}
 final=folder/'complete.json'
 if final.exists():
  info=read(final);assert info['signature']==signature
  for item in info['files']:assert identity(item['path'])==item
  with np.load(info['predictions']['path']) as z:outputs={e:z['raw_'+str(e)] for e in candidates}
  return outputs,info
 storage(run);attempt=folder/f'attempt{len(list(folder.glob("attempt*"))):03d}';attempt.mkdir(exist_ok=False);start=time.perf_counter()
 if variant=='V0':
  output,info=neural_fit('rtdetr',mean,y,train,test,candidates,base,seed,attempt/'checkpoint.pt')
  outputs={e:output[e][0] for e in candidates};losses=info['loss_by_epoch'];parameters=info['parameters']
 else:
  torch.manual_seed(seed);np.random.seed(seed);normalizer=Standardizer().fit(mean[train])
  values=torch.from_numpy(normalizer.transform(x)).cuda();labels=torch.tensor(y,dtype=torch.float32,device='cuda');model=make(variant).cuda()
  vc=base['visual'];optimizer=torch.optim.AdamW(model.parameters(),lr=vc['learning_rate'],weight_decay=vc['weight_decay'])
  criterion=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((len(train)-y[train].sum())/y[train].sum()),device='cuda'))
  generator=torch.Generator(device='cuda').manual_seed(seed);indices=torch.tensor(train,device='cuda');outputs={};losses=[];parameters=sum(p.numel() for p in model.parameters())
  for epoch in range(1,max(candidates)+1):
   model.train();order=indices[torch.randperm(len(indices),generator=generator,device='cuda')];total=0.
   for batch in order.split(vc['batch_size']):
    optimizer.zero_grad(set_to_none=True);raw=model(values[batch]);loss=criterion(raw,labels[batch]);assert torch.isfinite(loss)
    loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step();total+=float(loss.detach())*len(batch)
   losses.append(total/len(train))
   if epoch in candidates:
    model.eval();scores=[]
    with torch.inference_mode():
     for b in np.array_split(test,max(1,int(np.ceil(len(test)/256)))):scores.append(model(values[b]).cpu().numpy())
    outputs[epoch]=np.concatenate(scores)
    torch.save({'state_dict':{k:v.detach().cpu() for k,v in model.state_dict().items()},'normalizer_mean':torch.tensor(normalizer.mean),'normalizer_std':torch.tensor(normalizer.std),'variant':variant,'epoch':epoch,'seed':seed},attempt/f'checkpoint_epoch{epoch}.pt')
  del model,values,labels,optimizer;torch.cuda.empty_cache()
 pred=attempt/'predictions.npz';atomic_npz(pred,**{'raw_'+str(e):v for e,v in outputs.items()})
 info={'signature':signature,'seconds':time.perf_counter()-start,'parameters':parameters,'loss_by_epoch':losses,'predictions':identity(pred),'files':[identity(p) for p in sorted(attempt.iterdir())]}
 write(final,info);pause();return outputs,info

def branch(run,location,variant,seq,mean,y,frame,train,test,plan,base,seed_base,refit_seed,pause):
 guard_partition(frame,train,test,plan);folder=run/'branches'/location;folder.mkdir(parents=True,exist_ok=True);final=folder/'complete.json'
 signature={'variant':variant,'train':train.tolist(),'test':test.tolist(),'plan':[[a.tolist(),b.tolist()] for a,b in plan],'seed_base':seed_base,'refit_seed':refit_seed,'source':read(run/'source_signature.json'),'config':sha(run/'config.json')}
 if final.exists():
  info=read(final);assert info['signature']==signature and identity(info['predictions']['path'])==info['predictions']
  with np.load(info['predictions']['path']) as z:return {k:z[k] for k in z.files},info
 x=mean if variant=='V0' else aggregate(seq,variant)
 candidates=read(run/'config.json')['epochs'][variant];inner={e:np.full(len(y),np.nan) for e in candidates};scores={e:[] for e in candidates};logs=[]
 for j,(it,iv) in enumerate(plan):
  out,info=fit(run,location+f'/inner{j}',variant,x,mean,y,it,iv,candidates,base,seed_base+j,pause)
  for e in candidates:inner[e][iv]=out[e];scores[e].append(float(average_precision_score(y[iv],sigmoid(out[e]))))
  logs.append({'path':str(run/'fits'/location/f'inner{j}/complete.json'),'inner_fold':j,'AP':{str(e):scores[e][-1] for e in candidates}})
 selected=max(candidates,key=lambda e:np.mean(scores[e]));assert np.isfinite(inner[selected][train]).all()
 out,refit=fit(run,location+'/refit',variant,x,mean,y,train,test,[selected],base,refit_seed,pause)
 p,threshold,cal=calibrate(inner[selected][train],y[train],out[selected]);inner_p=sigmoid(cal['coefficient']*inner[selected][train]+cal['intercept'])
 # Calibrated training-OOF scores determine selective coverage thresholds only.
 # These are not independent inner performance estimates after selection/calibration.
 confidence=abs(inner_p-.5);cutoffs=[0.,float(np.quantile(confidence,.1)),float(np.quantile(confidence,.2))]
 values={'train_rows':train,'test_rows':test,'raw':out[selected],'p':p,'hard':(p>=threshold).astype(int),'inner_raw':inner[selected][train],'inner_p':inner_p,'coverage_cutoffs':np.array(cutoffs)}
 target=folder/'predictions.npz';atomic_npz(target,**values)
 info={'signature':signature,'selected':selected,'inner_AP':{str(e):v for e,v in scores.items()},'inner_fits':logs,'calibration':cal,'threshold':threshold,'coverage_levels':[1.,.9,.8],'confidence':'abs(calibrated probability - 0.5); training-selected cutoffs, ties retained','coverage_cutoffs':cutoffs,'parameters':refit['parameters'],'refit':str(run/'fits'/location/'refit/complete.json'),'predictions':identity(target)}
 write(final,info);return values,info
