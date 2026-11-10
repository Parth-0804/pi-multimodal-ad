"""Read-only native inputs and G-only raw-channel perturbation scales."""
import hashlib
import numpy as np
import h5py,cv2,torch
from common import RUN,REPO,config,read,write,sha,budget,signature
from corruptions import image_fault,statistics_for


def timestamps(x):
    x=np.asarray(x,dtype='float64')
    if x.ndim==2:
        assert np.allclose(x,x[:,:1],rtol=0,atol=1e-9,equal_nan=True);x=x[:,0]
    assert x.ndim==1 and np.isfinite(x).all() and np.all(np.diff(x)>0)
    return x


class Inputs:
    def __init__(self):
        from transformers import RTDetrImageProcessor
        cv2.setNumThreads(1)
        self.processor=RTDetrImageProcessor.from_pretrained(REPO/config()['weights_dir'],local_files_only=True)
        self.base=read(RUN/'provenance/base_config.json');self.capture=None;self.video=None;self.h5=None;self.source=None;self.native_cache=None
        self.policy=read(RUN/'checks/processor_noop.json')['policy']

    def images(self,sample,frames):
        path=REPO/sample['video_path'];st=path.stat()
        assert (st.st_size,st.st_mtime_ns)==(sample['video_bytes'],sample['video_mtime_ns']),'VIDEO_DRIFT'
        if self.video!=str(path):
            if self.capture is not None:self.capture.release()
            self.capture=cv2.VideoCapture(str(path));assert self.capture.isOpened();self.video=str(path)
        cap=self.capture;images=[]
        # Decode original32 to verify saved prepared pixel identity; select exact16 afterward.
        for index in sample['frames32']:
            current=int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if index<current or index-current>64:cap.set(cv2.CAP_PROP_POS_FRAMES,index)
            else:
                for _ in range(index-current):cap.grab()
            ok,img=cap.read();assert ok,('LOCKED_FRAME_DECODE_FAILURE',sample['sample_id'],index)
            images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        pixels=self.processor(images=images,return_tensors='np')['pixel_values']
        u=np.rint(pixels/(1/255)).astype('uint8')
        assert hashlib.sha256(u.tobytes()).hexdigest()==sample['pixel_content_sha256'],'PIXEL_IDENTITY_DRIFT'
        return images if frames==32 else [images[i] for i in sample['positions16_in32']]

    def process(self,images,family='clean',severity=0.,seed=0,key=(),ids=None):
        if family=='clean':return self.processor(images=images,return_tensors='pt')['pixel_values'],[]
        changed=[];metadata=[]
        for image,index in zip(images,ids):
            out,meta=image_fault(image,family,severity,seed,key,index);changed.append(out);metadata.append(meta)
        if self.policy=='float_domain':
            value=self.processor(images=changed,do_rescale=False,return_tensors='pt')['pixel_values']
        else:
            quantized=[np.rint(x*255).astype('uint8') for x in changed]
            value=self.processor(images=quantized,return_tensors='pt')['pixel_values']
        return value,metadata

    def streams(self,sample):
        path=REPO/sample['source_path'];st=path.stat()
        assert (st.st_size,st.st_mtime_ns)==(sample['source_bytes'],sample['source_mtime_ns']),'RAW_INPUT_DRIFT'
        if self.source!=str(path):
            if self.h5 is not None:self.h5.close()
            self.h5=h5py.File(path,'r');self.source=str(path);self.native_cache=None
        if self.native_cache is not None:return self.native_cache
        streams=[];names=[];units=[]
        for name in self.base['sensor']['channels']:
            ds=self.h5['robot_state'][name];x=np.asarray(ds[()],float)
            if x.ndim==1:x=x[:,None]
            t=timestamps(self.h5['timestamps'][name][()]);assert len(t)==len(x)
            streams.append((name,t,x))
            unit=ds.attrs.get('units',ds.attrs.get('unit','unspecified native source units'))
            if isinstance(unit,bytes):unit=unit.decode('utf-8')
            for c in range(x.shape[1]):names.append(f'{name}[{c}]');units.append(str(unit))
        self.native_cache=(streams,names,units)
        return self.native_cache

    def close(self):
        if self.h5 is not None:self.h5.close()
        if self.capture is not None:self.capture.release()


def processor_check():
    from transformers import RTDetrImageProcessor
    p=RTDetrImageProcessor.from_pretrained(REPO/config()['weights_dir'],local_files_only=True)
    generator=np.random.default_rng(123);images=[generator.integers(0,256,(47,61,3),dtype='uint8'),np.zeros((51,43,3),dtype='uint8')]
    a=p(images=images,return_tensors='np')['pixel_values']
    b=p(images=[x.astype('float32')/255. for x in images],do_rescale=False,return_tensors='np')['pixel_values']
    delta=float(np.max(abs(a-b)));policy='float_domain' if delta<=1e-7 else 'round_nearest_uint8_after_float_corruption'
    quant=[np.rint((x.astype('float32')/255.)*255).astype('uint8') for x in images]
    c=p(images=quant,return_tensors='np')['pixel_values'];assert np.array_equal(a,c)
    write(RUN/'checks/processor_noop.json',{'passed':True,'scope':'synthetic native RGB processor check, not model replay',
        'float_noop_max_abs':delta,'uint8_roundtrip_bitwise_equal':True,'policy':policy,
        'reason':'Prefer float domain only if it preserves upstream clean pixels; otherwise record required quantization to original uint8 processor route.',
        'processor_config':p.to_dict(),'quantization':'nearest integer RGB*255 after clipping, only if float no-op differs'})


def scales_for(f,job,inputs,selection_hash):
    path=RUN/'data/raw_training_scales'/job['fold_name']/'scales.json'
    identity={'selection':selection_hash,'G_keys':f.iloc[job['G']][['recording_id','segment_id']].to_dict('records'),'source':'native in-interval finite raw values, population SD; each G action contributes its interval samples once'}
    if path.exists():
        d=read(path);assert d['identity']==identity;return d
    counts=None;means=None;m2=None;order=None;units=None
    for number,i in enumerate(job['G']):
        if number%25==0:budget()
        sample=f.iloc[i].to_dict();streams,names,unit=inputs.streams(sample)
        if order is None:order=names;units=unit;counts=np.zeros(len(names),dtype='int64');means=np.zeros(len(names));m2=np.zeros(len(names))
        assert names==order and unit==units,'CHANNEL_ORDER_OR_UNITS_DRIFT'
        offset=0
        for name,t,x in streams:
            inside=(t>=sample['start'])&(t<=sample['end'])
            for col in range(x.shape[1]):
                values=x[inside,col];values=values[np.isfinite(values)];j=offset+col;n=len(values)
                if not n:continue
                mu=float(values.mean());second=float(np.sum((values-mu)**2));total=counts[j]+n;delta=mu-means[j]
                m2[j]+=second+delta**2*counts[j]*n/total;means[j]+=delta*n/total;counts[j]=total
            offset+=x.shape[1]
    sd=np.sqrt(np.divide(m2,counts,out=np.full_like(m2,np.nan),where=counts>0))
    d={'identity':identity,'names':order,'units':units,'finite_counts':counts.tolist(),'population_sd':[float(v) if np.isfinite(v) else None for v in sd],
       'zero_scale_channels':[order[i] for i in np.flatnonzero(sd==0)],'undefined_channels':[order[i] for i in np.flatnonzero(~np.isfinite(sd))],
       'assessment_excluded':True,'calibration_excluded':True,'predictor_refitted':False}
    write(path,d);return d
