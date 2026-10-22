"""User-authorized lossless cache of the immutable spatial prefix, never adapted outputs."""
from pathlib import Path
import io
import argparse
import time
import shutil
import numpy as np
import torch
from reassemble.section1_features import cohort,load_visual
from .common import setup,read,write,identity,storage,progress
from .finetune import FineTunedVisual,PixelSource
from .models import TemporalHead

@torch.no_grad()
def prefix(backbone,pixels):
    with torch.autocast('cuda',dtype=torch.float16):
        z=backbone.embedder(pixels);lower=[]
        for stage in range(3):
            z=backbone.encoder.stages[stage](z)
            if stage>=1:lower.append(z.float().mean((-2,-1)))
    return z,torch.cat(lower,-1)

class CachedFineTunedVisual(FineTunedVisual):
    def forward(self,inputs):
        if not isinstance(inputs,tuple):return super().forward(inputs)
        value,lower=inputs;segments=value.shape[0]
        with torch.autocast('cuda',dtype=torch.float16):
            adapted=self.backbone.encoder.stages[3](value.reshape(-1,*value.shape[-3:]))
        features=torch.cat([lower.reshape(-1,384),adapted.float().mean((-2,-1))],-1).reshape(segments,16,896)
        return self.head((features-self.mean)/self.std)[0]

class PrefixSource:
    def __init__(self,folder,base,frame,processor):
        from concurrent.futures import ThreadPoolExecutor
        self.folder=Path(folder);self.pixels=PixelSource(base,frame);self.processor=processor
        self.pool=ThreadPoolExecutor(max_workers=2)
    def values(self,rows):
        if len(rows)==1:
            # Match original16-image convolution kernels for singleton microbatches.
            return self.processor(images=self.pixels.images(int(rows[0])),return_tensors='pt')['pixel_values'].reshape(1,16,3,640,640).cuda()
        assert len(rows)==2
        def load(row):
            with np.load(self.folder/f'{int(row):05d}.npz') as z:return z['prefix'],z['lower']
        values=list(self.pool.map(load,rows))
        return torch.tensor(np.stack([v[0] for v in values]),device='cuda'),torch.tensor(np.stack([v[1] for v in values]),device='cuda')
    def close(self):self.pool.shutdown();self.pixels.close()

def audit():
    c=setup();root=Path(c['run_dir']);authorization=read(root/'00_protocol_and_preservation/prefix_cache_authorization.json');assert authorization['approved']
    target=root/'00_protocol_and_preservation/frozen_prefix_GPU_equivalence.json'
    if target.exists():return read(target)
    free,_=torch.cuda.mem_get_info();assert free>10*2**30,'Wait for GPU memory headroom before the bounded synthetic audit'
    base=read(c['section1_config']);processor,backbone,info=load_visual(base);torch.manual_seed(913)
    head=TemporalHead();cp=dict(state_dict=head.state_dict(),normalizer_mean=torch.zeros(896),normalizer_std=torch.ones(896))
    model=CachedFineTunedVisual(backbone,cp).cuda().train();x=torch.rand(2,16,3,640,640,device='cuda')
    # Match the actual32-image forward kernel of two-segment fine-tuning.
    z,m=prefix(backbone,x.reshape(32,3,640,640))
    values=z.reshape(2,16,256,40,40).cpu().numpy();means=m.reshape(2,16,384).cpu().numpy()
    stream=io.BytesIO();np.savez_compressed(stream,prefix=values,lower=means);stream.seek(0)
    with np.load(stream) as saved:cached=(torch.tensor(saved['prefix'],device='cuda'),torch.tensor(saved['lower'],device='cuda'))
    target_y=torch.tensor([0.,1.],device='cuda');torch.manual_seed(444)
    direct=model(x);torch.nn.functional.binary_cross_entropy_with_logits(direct,target_y).backward();grad={n:p.grad.clone() for n,p in model.named_parameters() if p.grad is not None}
    model.zero_grad(set_to_none=True);torch.manual_seed(444)
    reused=model(cached);torch.nn.functional.binary_cross_entropy_with_logits(reused,target_y).backward()
    prediction_error=float((direct-reused).abs().max().detach());errors={n:float((grad[n]-p.grad).abs().max()) for n,p in model.named_parameters() if p.grad is not None}
    gradient_error=max(errors.values());assert prediction_error<=1e-5 and gradient_error<=1e-5,(prediction_error,gradient_error)
    assert all(n.startswith('head.') or n.startswith('backbone.encoder.stages.3.') for n in grad)
    result=dict(passed=True,lossless_npz=True,cached_dtype=str(cached[0].dtype),prediction_max_abs=prediction_error,gradient_max_abs=gradient_error,gradient_errors=errors,
                gradient_parameters=list(grad),extraction_batch_frames=32,synthetic_segments=2,image_shape=[3,640,640],GPU_free_before_bytes=free,
                cache_boundary='after encoder.stages.2; before trainable encoder.stages.3',backbone=info,
                precision='unchanged float16 autocast convolutions; store actual float32 prefix activations/earlier means losslessly',same_trainable_parameters=True)
    write(target,result);print(result['prediction_max_abs'],result['gradient_max_abs'],flush=True);return result

def extract():
    c=setup();root=Path(c['run_dir']);authorization=read(root/'00_protocol_and_preservation/prefix_cache_authorization.json');assert authorization['approved']
    equivalence=read(root/'00_protocol_and_preservation/frozen_prefix_GPU_equivalence.json');assert equivalence['passed']
    base=read(c['section1_config']);frame=cohort(base);out=root/'01_temporal_visual/frozen_prefix';out.mkdir(exist_ok=True)
    storage(large=True);processor,backbone,info=load_visual(base);source=PixelSource(base,frame);write(out/'model.json',info)
    # A predeclared ten-recording sample estimates disk demand before allocating the full cache.
    sample=frame.groupby('recording_id',sort=True).head(1).index.to_numpy()[np.linspace(0,147,10).round().astype(int)]
    byte_counts=[];done=set()
    order=list(map(int,sample))+[i for i in range(len(frame)) if i not in set(sample)]
    started=time.perf_counter()
    for offset in range(0,len(order),2):
        pair=order[offset:offset+2];assert len(pair)==2
        if any(not (out/f'{row:05d}.npz').exists() for row in pair):
            storage(large=True)
            images=[image for row in pair for image in source.images(row)]
            pixels=processor(images=images,return_tensors='pt')['pixel_values'].cuda()
            value,means=prefix(backbone,pixels);assert value.shape==(32,256,40,40) and value.dtype==torch.float32
            value=value.reshape(2,16,256,40,40).cpu().numpy();means=means.reshape(2,16,384).cpu().numpy()
        for position,row in enumerate(pair):
            ordinal=offset+position;path=out/f'{row:05d}.npz';meta=path.with_suffix('.json')
            if path.exists():assert identity(path)==read(meta)['output'];size=path.stat().st_size
            else:
                np.savez_compressed(path,prefix=value[position],lower=means[position]);size=path.stat().st_size;rid=frame.iloc[row].recording_id
                write(meta,dict(output=identity(path),row=row,recording_id=rid,segment_id=frame.iloc[row].segment_id,extraction_batch_frames=32,
                     original_frame_features=identity(root/'01_temporal_visual/features'/(rid+'.npz')),model=identity(out/'model.json'),equivalence=identity(root/'00_protocol_and_preservation/frozen_prefix_GPU_equivalence.json')))
            if ordinal<10:byte_counts.append(size)
            if ordinal==9:
                expected=np.mean(byte_counts)*len(frame);conservative=max(byte_counts)*len(frame);free=shutil.disk_usage(out).free
                estimate=dict(sample_rows=sample.tolist(),sample_compressed_bytes=byte_counts,estimated_total_GiB=expected/2**30,conservative_total_GiB=conservative/2**30,free_GiB=free/2**30,
                              required_remaining_GiB=30,approved=free+sum(byte_counts)-conservative>=30*2**30)
                write(out/'storage_estimate.json',estimate)
                if not estimate['approved']:raise RuntimeError('Prefix cache storage estimate cannot preserve30GiB; preserve sampled files and use authorized pixel-based FT fallback')
        if (offset+2)%50==0:progress(1,f'Approved frozen-prefix cache {offset+2}/{len(frame)} segments complete')
    source.close()
    entries=[read(out/f'{row:05d}.json')['output'] for row in range(len(frame))]
    write(out/'manifest.json',dict(files=entries))
    write(out/'complete.json',dict(segments=len(frame),seconds=time.perf_counter()-started,manifest=identity(out/'manifest.json'),model=identity(out/'model.json'),equivalence=identity(root/'00_protocol_and_preservation/frozen_prefix_GPU_equivalence.json')))
    progress(1,'Approved lossless frozen-prefix cache complete; trainable final stage remains live')

def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['audit','extract']);a=p.parse_args()
    if a.operation=='audit':audit()
    else:extract()

if __name__=='__main__':main()
