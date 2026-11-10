#!/usr/bin/env python3
"""Independent waveform check of the dataset9 alias, without label input."""
import argparse
from pathlib import Path
import numpy as np
from scipy import signal
from audit_sensors import dump


def main(run):
    z=np.load(run/'cache/imi_vmx30ui_dataset9_audio.npz')
    sos=signal.butter(4,[800,1800],btype='bandpass',fs=4000,output='sos')
    video=signal.sosfiltfilt(sos,z['video_audio']);reference=signal.sosfiltfilt(sos,z['reference_audio'])
    window=4000;sumv=signal.correlate(video,np.ones(window),mode='valid',method='fft')
    sumv2=signal.correlate(video*video,np.ones(window),mode='valid',method='fft');rows=[]
    for center in (12,20,28,36,44,52):
        a=int((center-.5)*4000);template=reference[a:a+window];template=template-template.mean()
        cross=signal.correlate(video,template,mode='valid',method='fft')
        c=cross/np.maximum(np.sqrt(np.maximum(sumv2-sumv*sumv/window,0)*np.dot(template,template)),1e-12)
        best=int(np.argmax(np.abs(c)));idx=np.arange(round(a+15.5*4000),round(a+16.5*4000));old=idx[np.argmax(np.abs(c[idx]))]
        rows.append({'reference_center_s':center,'global_best_video_minus_sensor_s':(best-a)/4000,
                     'global_best_signed_correlation':float(c[best]),'best_abs_correlation_near_exploratory_alias':float(np.abs(c[old]))})
    assert all(49.5<r['global_best_video_minus_sensor_s']<49.85 for r in rows)
    dump(run/'manifests/raw_waveform_alignment_check.json',{'reference':'audio_s0','sample_rate':4000,'band_hz':[800,1800],
          'template_duration_s':1,'labels_not_used':True,'anchors':rows,'interpretation':'Independent global waveform matches corroborate the ~49.7 s offset; phase/sign varies across microphone paths.'})
    print(rows)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);main(p.parse_args().run)
