"""Bounded training-side cache reproducibility and resource check, not efficacy."""
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
from msm.models import verified_backbone
from external_eval.features import Decoder
from external_eval.io import write_json,sha,utc


def main():
    root=Path('MSM');config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text())
    plan=json.loads((root/'03_processed_model_inputs/split_manifests/frozen_splits.json').read_text())['primary__group_id']
    permitted=[plan['sample_ids'][i] for i in plan['plan'][0]['train']]
    table=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv').set_index('sample_id')
    folder=root/'03_processed_model_inputs/visual_features/P'
    sample=next(s for s in permitted if (folder/(hashlib.sha256(s.encode()).hexdigest()[:24]+'.npz')).exists())
    cache=folder/(hashlib.sha256(sample.encode()).hexdigest()[:24]+'.npz')
    selected=pd.read_csv(root/'02_labels_and_alignment/alignment_manifest.csv')
    actual=selected[selected.interval_id==sample];expected={int(r.native_frame_index):r.decoded_frame_sha256 for r in actual.itertuples()}
    row=table.loc[sample].to_dict();row['sample_id']=sample
    decoder=Decoder();pixels,_=decoder.frames(row,expected);decoder.close()
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    free,total=torch.cuda.mem_get_info()
    if free<3072*1024**2:raise RuntimeError('GPU reserve gate blocks optional parity check')
    torch.cuda.set_per_process_memory_fraction(.12)
    _,backbone,identity=verified_backbone(config['msm_stage3_configuration']);batch=torch.from_numpy(np.stack(pixels)).permute(0,3,1,2).contiguous()
    values=[];started=time.perf_counter()
    with torch.inference_mode():
        for chunk in batch.split(config['cnn_microbatch']):
            maps=backbone(chunk.to('cuda',dtype=torch.float32).div_(255)).feature_maps
            values.append(torch.cat([m.float().mean((-2,-1)) for m in maps],dim=1).cpu().numpy())
    torch.cuda.synchronize();elapsed=time.perf_counter()-started;value=np.concatenate(values)
    with np.load(cache,allow_pickle=False) as z:previous=z['features'][0]
    diff=float(np.max(abs(value-previous)))
    if diff>1e-6:raise ValueError('FP32 frozen CNN cache reproducibility failed')
    result={'utc':utc(),'sample_id':sample,'sample_role':'outer0 TRAINING ONLY; no assessment outcome used',
        'cache':str(cache),'cache_sha256':sha(cache),'CNN_frames':16,'max_absolute_feature_difference':diff,
        'tolerance':1e-6,'passed':True,'shared_gpu':True,'GPU':torch.cuda.get_device_name(),
        'microbatch':config['cnn_microbatch'],'forward_seconds':elapsed,'frames_per_second_including_startup':16/elapsed,
        'peak_allocated_mib':torch.cuda.max_memory_allocated()/1024**2,
        'frozen_CNN_parameter_gradients_absent':all(p.grad is None and not p.requires_grad for p in backbone.parameters()),
        'input_dtype':'uint8 converted to FP32 /255; no ImageNet normalization','outputs_shape':list(value.shape),
        'pretrained_files':identity['files'],'not_a_model_performance_result':True}
    write_json(root/'04_experiment_protocol/CNN_REPRODUCIBILITY_CHECK.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
