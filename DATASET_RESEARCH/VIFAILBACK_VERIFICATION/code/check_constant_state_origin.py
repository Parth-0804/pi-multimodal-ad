"""Check suspect qpos provenance with tiny HDF5 byte ranges, no raw-video reads."""
import io,json
import h5py,numpy as np,pandas as pd
from sources import ROOT,acquire
from original_annotations import BASE,ORIGINAL_REV


class RangedHDF5(io.RawIOBase):
    def __init__(self,url,size,name):self.url=url;self.size=size;self.position=0;self.name=name
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        self.position=offset if whence==0 else self.position+offset if whence==1 else self.size+offset
        if not 0<=self.position<=self.size:raise ValueError('Outside immutable HDF5 source')
        return self.position
    def read(self,count=-1):
        count=self.size-self.position if count<0 else min(count,self.size-self.position)
        if count==0:return b''
        if count>1_000_000:raise RuntimeError('Refuse large HDF5 read')
        begin=self.position;end=begin+count-1
        path=acquire(self.url,f'original_range_checks/{self.name}/{begin}_{end}.bin',count+1,{'Range':f'bytes={begin}-{end}'})
        data=path.read_bytes();assert len(data)==count;self.position+=len(data);return data
    def readinto(self,b):
        data=self.read(len(b));b[:len(data)]=data;return len(data)


if __name__=='__main__':
    ann={x['episode_index']:x for x in [json.loads(l) for l in (ROOT/'source_evidence/vifailback/meta/vifailback_annotations.jsonl').open()]}
    samples=json.loads((ROOT/'checks/constant_state_actual_sample_audit.json').read_text());out=[]
    for sample in samples:
        eid=sample['episode_index'];native=ann[eid];task=native['source_task']
        path=acquire(f'https://huggingface.co/api/datasets/sii-rhos-ai/ViFailback-Dataset/tree/{ORIGINAL_REV}/raw_data/{task}?recursive=false','original_trees/raw_data_'+task+'.json')
        entry=next(x for x in json.loads(path.read_text()) if x['path']==native['source_hdf5']);url=f'{BASE}/resolve/{ORIGINAL_REV}/{entry["path"]}'
        converted=pd.read_parquet(ROOT/'source_evidence/vifailback'/sample['source']);checks=[]
        with h5py.File(RangedHDF5(url,entry['size'],str(eid)),'r') as h:
            for feature,key in [('observation.state','observations/qpos'),('observation.velocity','observations/qvel'),('observation.effort','observations/effort')]:
                a=h[key][:];b=np.stack(converted[feature]);checks.append({'feature':feature,'shape':list(a.shape),'source_varying_channels':int((np.ptp(a,axis=0)>1e-8).sum()),'max_abs_conversion_error':float(np.max(np.abs(a-b)))})
        out.append({'episode_index':eid,'source_hdf5':native['source_hdf5'],'original_bytes_not_fully_downloaded':entry['size'],'source_lfs_identity':entry.get('lfs'),'checks':checks})
    (ROOT/'checks/constant_state_origin_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Constant-state provenance checked for',len(out),'episodes using bounded metadata/numerical ranges')
