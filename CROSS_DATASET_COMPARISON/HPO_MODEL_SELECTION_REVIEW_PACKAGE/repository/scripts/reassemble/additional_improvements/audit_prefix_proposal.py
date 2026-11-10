from pathlib import Path
import io,json,time
import numpy as np
import torch
from transformers import RTDetrForObjectDetection
from reassemble.additional_improvements.common import config,read,write
from reassemble.additional_improvements.models import TemporalHead
from reassemble.section1_features import cohort
from reassemble.additional_improvements.finetune import PixelSource
from transformers import RTDetrImageProcessor
c=config();base=read(c['section1_config']);root=Path(c['run_dir']);folder=Path(base['data_root'])/'cache/section1_models'/base['visual']['revision']
torch.set_num_threads(2);torch.manual_seed(123)
b=RTDetrForObjectDetection.from_pretrained(folder,local_files_only=True).model.backbone.model.eval();b.requires_grad_(False);b.encoder.stages[3].requires_grad_(True)
h=TemporalHead().eval();x=torch.rand(16,3,64,64)
def prefix(x):
 with torch.no_grad():
  z=b.embedder(x);lower=[]
  for i in range(3):
   z=b.encoder.stages[i](z)
   if i>=1:lower.append(z.float().mean((-2,-1)))
 return z,torch.cat(lower,-1)
def pooled(maps):return torch.cat([m.float().mean((-2,-1)) for m in maps],-1).reshape(1,16,896)
z,lower=prefix(x)
ref=h(pooled(b(x).feature_maps))[0];ref.sum().backward();grad={n:p.grad.clone() for n,p in b.encoder.stages[3].named_parameters()};b.zero_grad(set_to_none=True);h.zero_grad(set_to_none=True)
buf=io.BytesIO();np.savez_compressed(buf,prefix=z.numpy(),lower=lower.numpy());buf.seek(0)
with np.load(buf) as a:z2=torch.from_numpy(a['prefix']);lower2=torch.from_numpy(a['lower'])
alt=h(torch.cat([lower2,b.encoder.stages[3](z2).float().mean((-2,-1))],-1).reshape(1,16,896))[0];alt.sum().backward()
error=float((ref-alt).abs().max().detach());gerror=max(float((grad[n]-p.grad).abs().max()) for n,p in b.encoder.stages[3].named_parameters());assert error<1e-7 and gerror<1e-7
source=PixelSource(base,cohort(base));image=source.images(0)[0];source.close();processor=RTDetrImageProcessor.from_pretrained(folder,local_files_only=True)
pixels=processor(images=[image],return_tensors='pt')['pixel_values'];actual,means=prefix(pixels);out=io.BytesIO();np.savez_compressed(out,prefix=actual.numpy(),lower=means.numpy())
result=dict(proposal_only=True,not_authorized_or_used_in_fits=True,changed_architecture=False,lossless_storage=True,only_cached='unchanged frozen prefix activations before trainable encoder.stages.3, plus earlier spatial means',trainable_stage='recomputed with gradients at every update',synthetic_CPU_prediction_max_abs=error,synthetic_CPU_gradient_max_abs=gerror,sample_shape=list(actual.shape),sample_dtype=str(actual.dtype),sample_compressed_bytes=len(out.getvalue()),cohort_estimated_compressed_GiB=len(out.getvalue())*4530*16/2**30,cohort_uncompressed_GiB=(actual.numel()*actual.element_size()+means.numel()*means.element_size())*4530*16/2**30,required_additional_validation='GPU autocast forward/gradient parity and multi-recording cache estimate before any use')
write(root/'00_protocol_and_preservation/frozen_prefix_cache_proposal.json',result);print(result)
