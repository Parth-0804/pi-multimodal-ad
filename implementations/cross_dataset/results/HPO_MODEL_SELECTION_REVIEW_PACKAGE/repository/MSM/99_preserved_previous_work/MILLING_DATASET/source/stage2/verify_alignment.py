#!/usr/bin/env python3
"""Re-estimate timing with validation reference blocks masked out of coarse fitting."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy import signal

import align_audio
from audit_sensors import dump


def calibration_only_correlations(video_features, reference_features, window_samples=800):
    x,y=video_features[0],reference_features[0];n,m=len(x),len(y)
    # The final incomplete block is omitted from coarse fitting too.
    index=np.arange(m);weight=((index//window_samples)%2==0).astype(float)
    weight[(m//window_samples)*window_samples:]=0
    count=signal.correlate(np.ones(n),weight,method='fft')
    xy=signal.correlate(x,y*weight,method='fft')
    sx=signal.correlate(x,weight,method='fft');sy=signal.correlate(np.ones(n),y*weight,method='fft')
    sxx=signal.correlate(x*x,weight,method='fft');syy=signal.correlate(np.ones(n),y*y*weight,method='fft')
    denom=np.sqrt(np.maximum(sxx-sx*sx/np.maximum(count,1),0)*np.maximum(syy-sy*sy/np.maximum(count,1),0))
    scores=(xy-sx*sy/np.maximum(count,1))/np.maximum(denom,1e-12)
    scores[count<.7*weight.sum()]=-np.inf
    return signal.correlation_lags(n,m),scores


def main(run):
    cfg=json.loads((run/'config/resolved_config.json').read_text());protocol=json.loads((run/'config/alignment_protocol_final.json').read_text())
    previous=json.loads((run/'manifests/video_alignment_final.json').read_text());out={}
    align_audio.lag_correlations=calibration_only_correlations
    for group,old in previous.items():
        if not old['accepted']:continue
        key=group.replace('/','_');cache=np.load(run/'cache'/(key+('_alignment_audio.npz' if old['reference']=='audio_s2' else '_audio.npz')))
        new=align_audio.estimate_mapping(cache['video_features'],cache['reference_features'],protocol)
        assert new['accepted'],group
        delta=abs(new['offset_s']-old['offset_s'])
        assert delta<=.01, (group,delta)
        assert new['support_sensor_s']==old['support_sensor_s'],group
        assert all(abs(a['video_minus_sensor_s']-old['offset_s'])+.04<=old['uncertainty_s']+1e-8 for a in new['anchors'] if a.get('accepted') and a['role']=='validation'),group
        out[group]={'validation_reference_audio_excluded_from_coarse_fitting':True,'reference':old['reference'],
                    'calibration_only_estimate':new,'offset_difference_from_frame_mapping_s':delta,
                    'support_identical':True,'old_uncertainty_covers_heldout_residuals':True}
        print(group,'calibration-only offset',new['offset_s'],'difference',delta,'support identical',flush=True)
    dump(run/'manifests/calibration_only_alignment_validation.json',out)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);main(parser.parse_args().run)
