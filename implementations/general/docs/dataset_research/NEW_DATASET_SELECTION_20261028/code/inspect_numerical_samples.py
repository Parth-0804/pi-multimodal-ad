"""Check actual small numerical samples, without features or model execution."""
import hashlib
import io
import json
import wave
import zipfile
from collections import Counter
import h5py
import numpy as np
import pandas as pd
from acquisition import ROOT
from inspect_failure_archive import RemoteArchive


def inspect_cria():
    samples=json.loads((ROOT/'checks/cria_numerical_sample_selection.json').read_text())
    rows=[]
    for sample in samples:
        path=ROOT/'source_evidence/cria/files'/sample['parquet'];df=pd.read_parquet(path)
        ann=json.loads((ROOT/'source_evidence/cria/files'/sample['source_annotation']).read_text())['episodes'][f'{int(sample["episode_index"]):06d}']
        expected=np.ones(len(df),dtype=np.int64)
        for start,end in ann['anomaly']['manual']['ranges']:expected[start:end+1]=0
        numeric={};shape_errors=[]
        for key in ['observation.state.q','observation.state.ee_pose','observation.state.gripper_state','observation.state.wrench_raw_chunk','observation.state.wrench_filtered_chunk','action']:
            values=np.stack([np.stack(list(v)) if 'chunk' in key else np.asarray(v) for v in df[key]])
            numeric[key]={'shape':list(values.shape),'nonfinite':int((~np.isfinite(values)).sum()),'min':float(values.min()),'max':float(values.max())}
        dt=np.diff(df['timestamp'].to_numpy(dtype=float));du=np.diff(df['timestamp_us'].to_numpy())
        row={'parquet':sample['parquet'],'frames':len(df),'labels':{str(k):int(v) for k,v in df.frame_label.value_counts().items()},
             'frame_label_vs_manual_range_mismatches':int((expected!=df.frame_label.to_numpy()).sum()),
             'frame_indices_contiguous':bool(np.array_equal(df.frame_index.to_numpy(),np.arange(len(df)))),
             'episode_index_matches':bool((df.episode_index==int(sample['episode_index'])).all()),
             'episode_label_matches':bool((df.episode_label==int(sample['episode_label'])).all()),
             'timestamp_strictly_increasing':bool((dt>0).all()),'timestamp_us_strictly_increasing':bool((du>0).all()),
             'timestamp_delta_min_s':float(dt.min()),'timestamp_delta_max_s':float(dt.max()),
             'timestamp_vs_frame_over30_max_error_s':float(np.max(np.abs(df.timestamp.to_numpy()-np.arange(len(df))/30))),
             'timestamp_us_delta_min':int(du.min()),'timestamp_us_delta_max':int(du.max()),
             'wrench_valid_length_counts':{str(k):int(v) for k,v in df['observation.state.wrench_chunk_valid_len'].value_counts().items()},
             'numeric_arrays':numeric}
        rows.append(row)
    (ROOT/'checks/cria_numerical_sample_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('CRIA samples',len(rows),'rows',sum(x['frames'] for x in rows),'label_mismatches',sum(x['frame_label_vs_manual_range_mismatches'] for x in rows))


def inspect_robofac():
    root=ROOT/'source_evidence/robofac/files'
    path=next(root.rglob('*.h5'));result={'source':str(path.relative_to(root)),'datasets':[]}
    with h5py.File(path,'r') as h:
        def visit(name,obj):
            if isinstance(obj,h5py.Dataset):
                arr=obj[()];result['datasets'].append({'path':name,'shape':list(obj.shape),'dtype':str(obj.dtype),'nonfinite':int((~np.isfinite(arr)).sum()),'attributes':dict(obj.attrs)})
        h.visititems(visit)
        result['success_true_steps']=int(h['traj_0/success'][:].sum())
    (ROOT/'checks/robofac_h5_sample_audit.json').write_text(json.dumps(result,indent=2)+'\n')


def inspect_failure():
    root=ROOT/'source_evidence/failure';target=root/'extracted_samples';target.mkdir(exist_ok=True)
    head=json.loads((ROOT/'checks/failure_archive_head.json').read_text());rows=[]
    with zipfile.ZipFile(RemoteArchive(int(head['headers']['Content-Length']))) as archive:
        names=archive.namelist()
        for action,recording in [('push','5')]:
            wav=f'failnet_dataset/audio/{action}/{recording}.wav'
            images=sorted(n for n in names if n.startswith(f'failnet_dataset/rgb_imgs/{action}/{recording}/') and n.endswith('.png'))
            selected=[wav]+[images[i].removesuffix('.png')+'.txt' for i in [0,len(images)-1]]
            for member in selected:
                dest=target/(action+'_'+recording+'_'+member.split('/')[-1])
                if not dest.exists():dest.write_bytes(archive.read(member))
                raw=dest.read_bytes();row={'member':member,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'extracted_path':str(dest.relative_to(ROOT))}
                if member.endswith('.wav'):
                    with wave.open(io.BytesIO(raw)) as w:
                        row.update(sample_rate_hz=w.getframerate(),channels=w.getnchannels(),sample_width_bytes=w.getsampwidth(),samples=w.getnframes(),duration_s=w.getnframes()/w.getframerate())
                else:row['timestamp_text']=raw.decode().strip()
                rows.append(row)
    (ROOT/'checks/failure_payload_sample_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('FAILURE WAV/timestamp checks',rows)


if __name__=='__main__':
    # CRIA inspection stopped at the researcher's explicit withdrawal.
    inspect_robofac();inspect_failure()
