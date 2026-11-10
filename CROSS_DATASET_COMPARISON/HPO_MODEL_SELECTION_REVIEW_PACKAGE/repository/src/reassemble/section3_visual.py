"""Transient pixel corruptions and frozen RT-DETR pooling; no training."""
from pathlib import Path
import math
import time
import cv2
import numpy as np
import pandas as pd
import torch
from .completion_common import config, read, write, storage, seed_for, progress, claim
from .section1_features import cohort, load_visual, sha


def pixel_corruption(image, family, severity, seed):
    if family == 'V1':
        noise = np.random.default_rng(seed).normal(0, severity, image.shape).astype('float32')
        return np.rint(np.clip(image.astype('float32') / 255 + noise, 0, 1) * 255).astype('uint8')
    if family == 'V2':
        size = 2 * math.ceil(3 * severity) + 1
        return cv2.GaussianBlur(image, (size, size), severity, sigmaY=severity, borderType=cv2.BORDER_REFLECT_101)
    return image


def frame_quality(images, requested=16):
    gray = [cv2.cvtColor(cv2.resize(x, (160,120)), cv2.COLOR_BGR2GRAY).astype(float)/255 for x in images]
    brightness = [x.mean() for x in gray]
    focus = [cv2.Laplacian(x, cv2.CV_64F).var() for x in gray]
    motion = [np.abs(b-a).mean() for a,b in zip(gray[:-1], gray[1:])]
    return np.array([len(images)/requested, 1-len(images)/requested, np.mean(brightness), np.std(brightness), np.mean(focus), np.mean(motion)], dtype='float32')


def pooled_frames(images, processor, model):
    batch = processor(images=[cv2.cvtColor(x,cv2.COLOR_BGR2RGB) for x in images], return_tensors='pt')['pixel_values'].cuda()
    with torch.inference_mode(), torch.autocast('cuda',dtype=torch.float16):
        maps = model(batch).feature_maps
        values = torch.cat([m.float().mean((-2,-1)) for m in maps], dim=-1)
        mean = values.mean(0).cpu().numpy()
    return mean, values.cpu().numpy()


def main():
    c = config(); s = read('configs/reassemble/section3_corruptions.json'); base = read('configs/reassemble/section1.json')
    run = Path(s['run_dir']); out = run/'visual'; out.mkdir(exist_ok=True)
    storage(); torch.set_num_threads(2); cv2.setNumThreads(1)
    torch.use_deterministic_algorithms(True); torch.backends.cudnn.benchmark=False
    frame = cohort(base); recordings = pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id')
    processor, model, _ = load_visual(base)
    conditions = [v for v in s['conditions'] if v['family'] in ['clean','V1','V2','V3']]
    names = [v['name'] for v in conditions]
    for count,(rid,rows) in enumerate(frame.groupby('recording_id',sort=True)):
        path = out/(rid+'.npz')
        if path.exists():
            assert sha(path)==read(path.with_suffix('.json'))['sha256']; continue
        lock=claim(path)
        if lock is None:continue
        if path.exists():lock.close();continue
        storage(); started=time.perf_counter()
        source = Path(base['run_dir'])/'features'/(rid+'.npz')
        with np.load(source) as z:
            assert np.array_equal(z['row_index'],rows.index)
            indices=z['frame_indices'].copy(); original=z['visual'].copy()
        audits={x['segment_id']:x for x in read(Path(base['audit_run'])/'records'/(rid+'.json'))['segments']}
        video=Path(base['data_root'])/'cache/encoded_media'/recordings.loc[rid,'sha256']/'hand.mp4'
        cap=cv2.VideoCapture(str(video)); assert cap.isOpened()
        features=np.zeros((len(names),len(rows),896),dtype='float32'); quality=np.zeros((len(names),len(rows),6),dtype='float32')
        clean_difference=0.; quality_difference=0.
        for i,row in enumerate(rows.itertuples()):
            images=[]
            for index in indices[i]:
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(index)); ok,image=cap.read(); assert ok,(rid,index)
                images.append(image)
            clean, per_frame=pooled_frames(images,processor,model)
            clean_difference=max(clean_difference,float(np.max(abs(clean-original[i]))))
            assert clean_difference<=5e-5,('Frozen visual feature parity failed',rid,clean_difference)
            expected=np.array([audits[row.segment_id]['video']['hand'][k] for k in read('configs/reassemble/section2.json')['quality_visual']])
            quality_difference=max(quality_difference,float(np.max(abs(frame_quality(images)-expected))))
            assert quality_difference<=1e-6,('Frozen visual quality parity failed',rid,quality_difference)
            for j,condition in enumerate(conditions):
                family,severity=condition['family'],condition['severity']
                seed=seed_for(s['seed'],rid,row.segment_id,family,severity)
                if family=='clean':
                    features[j,i]=clean; quality[j,i]=frame_quality(images)
                elif family=='V3':
                    drop=int(round(16*severity)); kept=np.sort(np.random.default_rng(seed).permutation(16)[drop:])
                    features[j,i]=per_frame[kept].mean(0); quality[j,i]=frame_quality([images[t] for t in kept])
                else:
                    changed=[pixel_corruption(image,family,severity,seed_for(seed,int(index))) for image,index in zip(images,indices[i])]
                    features[j,i]=pooled_frames(changed,processor,model)[0]; quality[j,i]=frame_quality(changed)
        cap.release()
        np.savez_compressed(path,row_index=rows.index.to_numpy(),features=features,quality=quality,names=np.asarray(names))
        write(path.with_suffix('.json'),{'sha256':sha(path),'input_sha256':sha(source),'conditions':names,'clean_max_feature_difference':clean_difference,'clean_max_quality_difference':quality_difference,'seconds':time.perf_counter()-started,'segments':len(rows)})
        lock.close()
        progress(f'Section 3 visual corruptions: completed recording ordinal {count+1}/148')
    progress('Section 3 visual feature extraction complete')

if __name__=='__main__':main()
