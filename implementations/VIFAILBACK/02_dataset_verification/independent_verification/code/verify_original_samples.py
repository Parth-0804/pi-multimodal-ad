"""Compare original robot observations and images to the converted pilot."""
import json
from pathlib import Path
import cv2,h5py,numpy as np,pandas as pd
from PIL import Image
from sources import ROOT


if __name__=='__main__':
    selected=json.loads((ROOT/'checks/original_hdf5_sample_selection.json').read_text());reports=[]
    for row in selected:
        df=pd.read_parquet(ROOT/'source_evidence/vifailback'/row['data']);numeric=[];image_checks=[]
        with h5py.File(ROOT/'source_evidence/original'/row['source_hdf5'],'r') as h:
            attrs={k:(bool(v) if isinstance(v,(bool,np.bool_)) else str(v)) for k,v in h.attrs.items()}
            for key,original in [('observation.state','observations/qpos'),('observation.velocity','observations/qvel'),('observation.effort','observations/effort')]:
                actual=np.stack(df[key]);native=h[original][:];error=float(np.max(np.abs(actual-native)))
                assert actual.shape==native.shape and error==0
                numeric.append({'feature':key,'source_dataset':original,'shape':list(native.shape),'max_abs_error':error})
            indices=[k*(len(df)-1)//15 for k in range(16)]
            for camera in ['cam_high','cam_left_wrist','cam_right_wrist']:
                dataset=h['observations/images/'+camera]
                assert len(dataset)==len(df)
                for position in [0,7,15]:
                    encoded=bytes(dataset[indices[position]])
                    # The author states JPEGs were stored in RGB byte order.
                    original=cv2.imdecode(np.frombuffer(encoded,np.uint8),cv2.IMREAD_COLOR)
                    converted=np.asarray(Image.open(ROOT/'MATCHED_EXAMPLE_GALLERY/assets'/row['blind_id']/camera/f'frame_{position:02d}.png').convert('RGB'))
                    assert original.shape==converted.shape
                    mse=float(np.mean((original.astype(float)-converted.astype(float))**2));psnr=float(10*np.log10(255**2/max(mse,1e-12)))
                    image_checks.append({'camera':camera,'frame_index':indices[position],'source_shape':list(original.shape),'MSE_after_lossy_conversion':mse,'PSNR_dB':psnr})
            datasets=[]
            h.visititems(lambda name,obj:datasets.append({'name':name,'shape':list(obj.shape),'dtype':str(obj.dtype)}) if isinstance(obj,h5py.Dataset) else None)
        reports.append({'episode_index':int(row['episode_index']),'source_hdf5':row['source_hdf5'],'attributes':attrs,
            'numeric_comparisons':numeric,'image_comparisons':image_checks,'datasets':datasets,
            'explicit_hardware_timestamps_found':any('timestamp' in x['name'].lower() for x in datasets)})
    (ROOT/'checks/original_hdf5_conversion_audit.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Original source observation arrays match exactly in both episodes; image PSNR range',min(x['PSNR_dB'] for r in reports for x in r['image_comparisons']),max(x['PSNR_dB'] for r in reports for x in r['image_comparisons']))
