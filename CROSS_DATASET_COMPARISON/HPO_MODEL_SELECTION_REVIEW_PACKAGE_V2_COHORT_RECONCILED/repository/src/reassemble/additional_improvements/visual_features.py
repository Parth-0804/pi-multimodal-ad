"""Re-extract genuine frame sequences using precisely the sealed image pipeline."""
from pathlib import Path
import time
import h5py
import cv2
import numpy as np
import pandas as pd
from reassemble.alignment import timestamps_1d
from reassemble.section1_features import cohort, load_visual, sha
from reassemble.section3_visual import pooled_frames
from .common import setup, read, write, storage, progress, identity

def main():
    c=setup(); base=read(c['section1_config']); root=Path(c['run_dir'])
    storage(large=True)
    frame=cohort(base)
    records=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id')
    out=root/'01_temporal_visual/features';out.mkdir(exist_ok=True)
    processor, model, info=load_visual(base)
    write(out/'pretrained_model.json',info)
    write(out/'cache_estimate.json',dict(uncompressed_feature_bytes=len(frame)*16*896*4,
          mask_timestamp_index_bytes=len(frame)*16*17, permanent_decoded_images=False))
    for ordinal,(rid,rows) in enumerate(frame.groupby('recording_id',sort=True)):
        dest=out/(rid+'.npz'); meta=dest.with_suffix('.json')
        if dest.exists():
            assert read(meta)['output']['sha256']==sha(dest)
            continue
        storage();t0=time.perf_counter()
        old=Path(base['run_dir'])/'features'/(rid+'.npz')
        with np.load(old) as z:
            assert np.array_equal(z['row_index'],rows.index)
            indices=z['frame_indices'].copy(); means=z['visual'].copy()
        source=Path(base['data_root'])/'raw/data'/records.loc[rid,'filename']
        st=source.stat()
        assert st.st_size==int(records.loc[rid,'size_bytes']) and st.st_mtime_ns==int(records.loc[rid,'mtime_ns'])
        with h5py.File(source,'r') as h: timestamps=timestamps_1d(h['timestamps/hand'][()])
        video=Path(base['data_root'])/'cache/encoded_media'/records.loc[rid,'sha256']/'hand.mp4'
        cap=cv2.VideoCapture(str(video));assert cap.isOpened()
        seq=np.empty((len(rows),16,896),np.float32);maximum=0.
        for i in range(len(rows)):
            images=[]
            for index in indices[i]:
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read()
                assert ok,(rid,int(index));images.append(img)
            mean,seq[i]=pooled_frames(images,processor,model)
            maximum=max(maximum,float(np.max(abs(mean-means[i]))))
            assert maximum<=5e-5,('SOURCE PARITY FAILURE',rid,maximum)
        cap.release()
        np.savez_compressed(dest,row_index=rows.index.to_numpy(),features=seq,
                            frame_indices=indices,timestamps=timestamps[indices],valid=np.ones(indices.shape,bool))
        write(meta,dict(output=identity(dest),input_features=identity(old),source_sha256=records.loc[rid,'sha256'],
                        video_path=str(video),model_identity=identity(out/'pretrained_model.json'),
                        mean_parity_max_abs=maximum,seconds=time.perf_counter()-t0))
        progress(1,f'Per-frame extraction {ordinal+1}/148 recordings complete')
    progress(1,'Per-frame extraction complete; neural fits pending')

if __name__=='__main__':main()
