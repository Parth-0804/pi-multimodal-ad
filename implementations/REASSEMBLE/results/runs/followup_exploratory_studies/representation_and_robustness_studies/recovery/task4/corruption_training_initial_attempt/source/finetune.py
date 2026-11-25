"""Pixel-based final-spatial-stage adaptation; no cached adapted outputs."""
from pathlib import Path
import gc
import time
import json
import hashlib
import cv2
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score,roc_auc_score
from reassemble.section1_features import load_visual,sha
from reassemble.section1_models import sigmoid,calibrate
from reassemble.section1b import index_plan,choose_threshold,guard_partition
from .models import TemporalHead
from .common import config,read,write,storage,identity,progress,setup,inputs
from .reporting import comparison
from .training_recovery import Recovery,TrainingPaused,should_pause,compact_state,load_compact,random_state,restore_random,publish_predictions,publish_selected

class PixelSource:
    """Decode only requested segment frames; retain compressed videos only."""
    def __init__(self,base,frame):
        self.base=base;self.frame=frame;self.indices={};self.videos={}
        records=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id')
        for rid,rows in frame.groupby('recording_id',sort=True):
            with np.load(Path(base['run_dir'])/'features'/(rid+'.npz')) as z:
                assert np.array_equal(z['row_index'],rows.index)
                for row,ii in zip(rows.index,z['frame_indices']):self.indices[row]=ii.copy()
            self.videos[rid]=Path(base['data_root'])/'cache/encoded_media'/records.loc[rid,'sha256']/'hand.mp4'
        self.captures={}
    def images(self,row):
        rid=self.frame.iloc[row].recording_id
        if rid not in self.captures:
            # Bound decoder handles and frame buffers; no decoded-frame collection.
            if len(self.captures)>=8:
                _,cap=self.captures.popitem();cap.release()
            cap=cv2.VideoCapture(str(self.videos[rid]));assert cap.isOpened();self.captures[rid]=cap
        cap=self.captures[rid];images=[]
        for index in self.indices[row]:
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read();assert ok,(rid,int(index))
            images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        return images
    def close(self):
        for cap in self.captures.values():cap.release()
        self.captures.clear()

class FineTunedVisual(torch.nn.Module):
    def __init__(self,backbone,checkpoint):
        super().__init__();self.backbone=backbone
        self.backbone.requires_grad_(False);self.backbone.encoder.stages[3].requires_grad_(True)
        self.head=TemporalHead();self.head.load_state_dict(checkpoint['state_dict'])
        self.register_buffer('mean',checkpoint['normalizer_mean']);self.register_buffer('std',checkpoint['normalizer_std'])
    def train(self,mode=True):
        super().train(mode);self.backbone.eval();return self
    def forward(self,pixels):
        shape=pixels.shape
        with torch.autocast('cuda',dtype=torch.float16):maps=self.backbone(pixels.reshape(-1,*shape[-3:])).feature_maps
        features=torch.cat([m.float().mean((-2,-1)) for m in maps],-1).reshape(shape[0],16,-1)
        return self.head((features-self.mean)/self.std)[0]

def gradient_audit(base,root):
    target=Path(root)/'finetune_gradient_audit.json'
    if target.exists():return read(target)
    storage();processor,backbone,info=load_visual(base);torch.manual_seed(20260927)
    head=TemporalHead();checkpoint=dict(state_dict=head.state_dict(),normalizer_mean=torch.zeros(896),normalizer_std=torch.ones(896))
    model=FineTunedVisual(backbone,checkpoint).cuda().train();before={n:b.clone() for n,b in backbone.named_buffers() if 'running_' in n}
    attempts=[];supported=False
    for micro in [2,1]:
        try:
            torch.cuda.reset_peak_memory_stats();t=time.perf_counter()
            x=torch.rand(micro,16,3,640,640,device='cuda');out=model(x)
            torch.nn.functional.binary_cross_entropy_with_logits(out,torch.arange(micro,device='cuda').float()%2).backward()
            gradients=[n for n,p in model.named_parameters() if p.grad is not None]
            expected=[n for n,p in model.named_parameters() if p.requires_grad]
            assert gradients==expected
            assert all(n.startswith('head.') or n.startswith('backbone.encoder.stages.3.') for n in gradients)
            assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
            assert any(p.grad.abs().sum()>0 for n,p in model.named_parameters() if n.startswith('backbone.encoder.stages.3.') and p.grad is not None)
            assert all(torch.equal(value,dict(backbone.named_buffers())[name]) for name,value in before.items())
            attempts.append(dict(microbatch=micro,success=True,peak_bytes=torch.cuda.max_memory_allocated(),seconds=time.perf_counter()-t));supported=True;break
        except torch.cuda.OutOfMemoryError as exc:
            attempts.append(dict(microbatch=micro,success=False,error=str(exc)));model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache()
    result=dict(supported=supported,attempts=attempts,gradient_parameters=gradients if supported else [],
                trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad),backbone=info,
                precision='fp16 autocast backbone, float32 head and parameters; GradScaler during training',running_statistics_frozen=True)
    write(target,result);del model,backbone;gc.collect();torch.cuda.empty_cache();return result

def fit(path,source,processor,base,checkpoint_path,y,train,valid,seed,epochs=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);c=config();options=c['finetune']
    signature=hashlib.sha256(json.dumps(dict(code=sha(__file__),recovery_code=sha(Path(__file__).with_name('training_recovery.py')),prefix_code=sha(Path(__file__).with_name('prefix_cache.py')) if hasattr(source,'values') else None,cache_manifest=identity(source.folder/'complete.json') if hasattr(source,'folder') else None,initial=identity(checkpoint_path),train=train.tolist(),valid=valid.tolist(),seed=seed,epochs=epochs,options=options,input_mode=type(source).__name__),sort_keys=True).encode()).hexdigest()
    if path.with_suffix('.json').exists():
        info=read(path.with_suffix('.json'));assert info['signature']==signature
        assert identity(path.with_suffix('.pt'))==info['checkpoint'] and identity(path.with_suffix('.npz'))==info['predictions']
        with np.load(path.with_suffix('.npz')) as z:return {key:z[key] for key in z.files},info
    for attempt,micro in enumerate([2,1]):
        try:
            return _fit(path,source,processor,base,checkpoint_path,y,train,valid,seed,epochs,micro,signature)
        except torch.cuda.OutOfMemoryError as exc:
            write(path.parent/(path.name+f'_oom_attempt{attempt}.json'),dict(error=str(exc),microbatch=micro,effective_batch=128))
            gc.collect();torch.cuda.empty_cache()
            if micro==1:raise

def _fit(path,source,processor,base,checkpoint_path,y,train,valid,seed,epochs,micro,signature):
    storage();c=config();options=c['finetune'];torch.manual_seed(seed);started=time.perf_counter()
    _,backbone,_=load_visual(base);checkpoint=torch.load(checkpoint_path,map_location='cpu',weights_only=True)
    if hasattr(source,'values'):
        from .prefix_cache import CachedFineTunedVisual
        model=CachedFineTunedVisual(backbone,checkpoint).cuda()
    else:model=FineTunedVisual(backbone,checkpoint).cuda()
    head=list(model.head.parameters());stage=list(model.backbone.encoder.stages[3].parameters())
    optimizer=torch.optim.AdamW([{'params':head,'lr':options['head_lr']},{'params':stage,'lr':options['pretrained_lr']}],weight_decay=options['weight_decay'])
    amp=torch.amp.GradScaler('cuda');ratio=float((len(train)-y[train].sum())/y[train].sum())
    criterion=torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(ratio,device='cuda'));rng=np.random.default_rng(seed)
    def pixels(rows):
        if hasattr(source,'values'):return source.values(rows)
        images=[image for row in rows for image in source.images(int(row))]
        return processor(images=images,return_tensors='pt')['pixel_values'].reshape(len(rows),16,3,640,640).cuda()
    def predict(rows,order=None):
        model.eval();outputs=[]
        with torch.inference_mode():
            for chunk in np.array_split(rows,max(1,int(np.ceil(len(rows)/micro)))):
                x=pixels(chunk)
                if order is not None:x=tuple(v[:,order] for v in x) if isinstance(x,tuple) else x[:,order]
                outputs.append(model(x).cpu().numpy())
        return np.concatenate(outputs)
    best=-np.inf;best_epoch=0;history=[];maximum=epochs or options['max_epochs'];best_state=None;best_raw=None
    fit_root=Path(c['run_dir'])/'01_temporal_visual/fits/V-FT'
    recovery=Recovery(Path(c['run_dir'])/'01_temporal_visual/training_recovery'/path.relative_to(fit_root)/f'micro{micro}',signature)
    saved=recovery.load();first_epoch=1;resume_order=None;resume_offset=0;resume_loss=0.;elapsed_before=0.;epoch=0
    if saved is not None:
        load_compact(model,saved['model']);optimizer.load_state_dict(saved['optimizer']);amp.load_state_dict(saved['amp'])
        first_epoch=saved['epoch'];resume_order=None if saved['order'] is None else saved['order'].numpy()
        resume_offset=saved['offset'];resume_loss=saved['loss'];history=saved['history'];best=saved['best'];best_epoch=saved['best_epoch']
        best_state=saved['best_state'];best_raw=None if saved['best_raw'] is None else saved['best_raw'].numpy()
        elapsed_before=saved['elapsed_seconds'];epoch=history[-1]['epoch'] if history else 0
        if saved['finished']:first_epoch=maximum+1
        restore_random(saved['random'],rng)
        print('RESUMED FT',path.name,'epoch',first_epoch,'offset',resume_offset,flush=True)
        del saved
    def checkpoint(next_epoch,order,offset,loss,finished=False):
        storage()
        recovery.save(dict(model=compact_state(model),optimizer=optimizer.state_dict(),amp=amp.state_dict(),random=random_state(rng),
            epoch=next_epoch,order=None if order is None else torch.from_numpy(order.copy()),offset=offset,loss=loss,history=history,
            best=best,best_epoch=best_epoch,best_state=best_state,best_raw=None if best_raw is None else torch.from_numpy(best_raw.copy()),
            elapsed_seconds=elapsed_before+time.perf_counter()-started,finished=finished))
        print('CHECKPOINT FT',path.name,'epoch',next_epoch,'offset',offset,'generation',recovery.generation,flush=True)
        if should_pause():raise TrainingPaused('Visual state saved before planned stop/reset')
    for epoch in range(first_epoch,maximum+1):
        storage();model.train()
        if epoch==first_epoch and resume_order is not None:order=resume_order;start_offset=resume_offset;loss_sum=resume_loss
        else:order=rng.permutation(train);start_offset=0;loss_sum=0.
        for offset in range(start_offset,len(order),options['batch_size']):
            effective=order[offset:offset+options['batch_size']];optimizer.zero_grad(set_to_none=True)
            for step in range(0,len(effective),micro):
                rows=effective[step:step+micro];raw=model(pixels(rows));loss=criterion(raw,torch.tensor(y[rows],dtype=torch.float32,device='cuda'))
                assert torch.isfinite(loss);amp.scale(loss*len(rows)/len(effective)).backward();loss_sum+=loss.item()*len(rows)
            amp.unscale_(optimizer);torch.nn.utils.clip_grad_norm_(head+stage,1);amp.step(optimizer);amp.update()
            if recovery.due():checkpoint(epoch,order,min(offset+options['batch_size'],len(order)),loss_sum)
        raw=predict(valid) if epochs is None or epoch==maximum else None
        ap=float(average_precision_score(y[valid],sigmoid(raw))) if epochs is None else None
        auc=float(roc_auc_score(y[valid],raw)) if epochs is None else None
        history.append(dict(epoch=epoch,train_loss=loss_sum/len(train),validation_AP=ap,validation_AUROC=auc,elapsed_seconds=elapsed_before+time.perf_counter()-started))
        write(path.parent/(path.name+'_live.json'),dict(history=history,seed=seed,initial=str(checkpoint_path)),replace=True)
        print('FT',path.name,'epoch',epoch,'elapsed',round(time.perf_counter()-started),flush=True)
        if (epochs is not None and epoch==maximum) or (epochs is None and ap>best):
            if ap is not None:best=ap
            best_epoch=epoch;best_raw=raw.copy();best_state=compact_state(model)
        finished=epoch==maximum or (epochs is None and epoch-best_epoch>=options['patience'])
        checkpoint(epoch+1,None,0,0.,finished)
        if finished:break
    load_compact(model,best_state)
    # Three separate fixed-weight pixel passes; not a prediction ensemble.
    result=dict(raw=best_raw,reverse=predict(valid,np.arange(16)[::-1].copy()),permute=predict(valid,np.random.default_rng(seed+991).permutation(16)))
    publish_predictions(path.with_suffix('.npz'),result)
    # Only adapted stage + head and scaler need storage; immutable prefix remains pinned.
    compact={k:v for k,v in best_state.items() if k.startswith('head.') or k.startswith('backbone.encoder.stages.3.') or k in ['mean','std']}
    publish_selected(path.with_suffix('.pt'),dict(state_dict=compact,initial=identity(checkpoint_path),epoch=best_epoch,seed=seed))
    info=dict(signature=signature,initial=identity(checkpoint_path),seed=seed,train_rows=train.tolist(),assessment_rows=valid.tolist(),best_epoch=best_epoch,stopped_epoch=epoch,cap_reached=epoch==maximum,history=history,input_mode=type(source).__name__,microbatch=micro,effective_batch=128,seconds=elapsed_before+time.perf_counter()-started,recovery_generations=recovery.generation+1,checkpoint=identity(path.with_suffix('.pt')),predictions=identity(path.with_suffix('.npz')))
    write(path.with_suffix('.json'),info);del model,optimizer,backbone;gc.collect();torch.cuda.empty_cache();return result,info

def main():
    c=setup();c,base,frame,arrays,splits=inputs();root=Path(c['run_dir'])/'01_temporal_visual';audit=gradient_audit(base,root)
    if not audit['supported']:
        progress(1,'V-FT blocked: synthetic memory test failed down to microbatch1; frozen variants retained','partially_blocked');return
    processor,backbone,_=load_visual(base);del backbone;torch.cuda.empty_cache()
    if (root/'frozen_prefix/complete.json').exists():
        from .prefix_cache import PrefixSource
        assert read(Path(c['run_dir'])/'00_protocol_and_preservation/prefix_cache_authorization.json')['approved']
        assert read(Path(c['run_dir'])/'00_protocol_and_preservation/frozen_prefix_GPU_equivalence.json')['passed']
        source=PrefixSource(root/'frozen_prefix',base,frame,processor)
    else:source=PixelSource(base,frame)
    y=frame.failure.to_numpy(int);n=len(y);seed_p=np.full((3,n),np.nan);seed_hard=np.zeros((3,n),int);p=np.full(n,np.nan);hard=np.zeros(n,int);fold=np.full(n,-1);reverse=np.full(n,np.nan);permuted=np.full(n,np.nan)
    for outer in splits['folds']:
        k=outer['fold'];plan=index_plan(frame,outer);tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));guard_partition(frame,tr,te,plan);fold[te]=k
        inner_p=[];all_info=[];rev=[];perm=[]
        for s,seed in enumerate(c['seeds']):
            raw=np.full(n,np.nan);epochs=[];info=[]
            for j,(it,iv) in enumerate(plan):
                initial=root/'fits/V-TEMP'/f'outer{k}'/f'inner{j}_seed{seed}.pt'
                out,detail=fit(root/'fits/V-FT'/f'outer{k}'/f'inner{j}_seed{seed}',source,processor,base,initial,y,it,iv,seed)
                raw[iv]=out['raw'];epochs.append(detail['best_epoch']);info.append(detail)
            duration=int(np.floor(np.median(epochs)+.5));initial=root/'fits/V-TEMP'/f'outer{k}'/f'refit_seed{seed}.pt'
            out,detail=fit(root/'fits/V-FT'/f'outer{k}'/f'refit_seed{seed}',source,processor,base,initial,y,tr,te,seed,duration)
            seed_p[s,te],threshold,cal=calibrate(raw[tr],y[tr],out['raw']);seed_hard[s,te]=seed_p[s,te]>=threshold
            inner_p.append(sigmoid(cal['coefficient']*raw[tr]+cal['intercept']));rev.append(sigmoid(cal['coefficient']*out['reverse']+cal['intercept']));perm.append(sigmoid(cal['coefficient']*out['permute']+cal['intercept']))
            all_info.append(dict(seed=seed,calibration=cal,inner=info,refit=detail))
        threshold=choose_threshold(y[tr],np.mean(inner_p,axis=0));p[te]=seed_p[:,te].mean(0);hard[te]=p[te]>=threshold;reverse[te]=np.mean(rev,axis=0);permuted[te]=np.mean(perm,axis=0)
        write(root/f'finetune_outer{k}.json',dict(fold=k,threshold=threshold,seeds=all_info));progress(1,f'V-FT outer {k+1}/5 complete')
    source.close();publish_predictions(root/'V-FT_predictions.npz',dict(y=y,fold=fold,p=p,hard=hard,seed_p=seed_p,seed_hard=seed_hard,reverse=reverse,permute=permuted))
    predictions={'V-FT':dict(p=p,hard=hard,seed_p=seed_p,seed_hard=seed_hard)}
    for name in ['V-TEMP','V-MEAN']:
        with np.load(root/(name+'_predictions.npz')) as z:predictions[name]={key:z[key] for key in ['p','hard','seed_p','seed_hard']}
    comparison(frame,fold,predictions,[('V-FT','V-TEMP'),('V-FT','V-MEAN')],root/'finetune_comparison');progress(1,'All visual variants including V-FT complete; final report pending')

if __name__=='__main__':main()
