#!/usr/bin/env python3
"""Render real 16-frame sequences with synchronized label/sensor timelines."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageOps

from probe_media import corrected_frame
from audit_sensors import dump

COLORS={0:"#81b59b",1:"#dc6b62",2:"#d9b44a"}


def shade_labels(ax, labels, low, high):
    for _, label in labels.iterrows():
        if label.end < low or label.start > high: continue
        ax.axvspan(label.start,label.end,color=COLORS[int(label.label)],alpha=.2)


def main(run):
    cfg=json.loads((run/'config/resolved_config.json').read_text());raw=Path(cfg['data_root'])
    alignment=json.loads((run/'manifests/video_alignment_final.json').read_text());media=json.loads((run/'manifests/media_probe.json').read_text())
    frames=pd.read_csv(run/'manifests/selected_frame_manifest.csv');pilot=pd.read_csv(run/'MSM_PILOT_SAMPLE_MANIFEST.csv')
    summaries=[];(run/'figures/examples').mkdir(exist_ok=False);cv2.setNumThreads(1)
    for group in cfg['selected_groups']:
        key=group.replace('/','_');labels=pd.read_csv(raw/group/'label.csv');mapping=alignment[group]
        traces={m:np.load(run/'cache'/(key+'_'+m+'_trace.npz')) for m in ('mtc','acc','ct') if (run/'cache'/(key+'_'+m+'_trace.npz')).exists()}
        if mapping.get('accepted'):
            cache=np.load(run/'cache'/(key+('_alignment_audio.npz' if mapping['reference']=='audio_s2' else '_audio.npz')))
            ref=cache['reference_features'][2];vf=cache['video_features'][2];rt=np.arange(len(ref))/.1/1000+.032
            offset=mapping['offset_s'];vt=np.arange(len(vf))/100+.032-offset
        else:
            import soundfile as sf
            from scipy import signal
            from probe_media import envelope
            audio,fs=sf.read(next((raw/group).glob('*_s0.wav')),dtype='float32');ref=envelope(signal.resample_poly(audio,4000,fs))[2];rt=np.arange(len(ref))/100+.032;vf=None
        fig,axs=plt.subplots(4,1,figsize=(14,9),layout='constrained',sharex=True)
        axs[0].plot(rt,ref,lw=.6,label='reference microphone, 800–1800 Hz log energy')
        if vf is not None:axs[0].plot(vt,vf,lw=.5,alpha=.7,label='mapped smartphone AAC')
        axs[0].set_ylabel('Audio log energy');axs[0].legend(fontsize=8)
        mt=traces['mtc'];channel='smarms' if 'smarms' in mt.files else 's_load'
        axs[1].plot(mt['time'],mt[channel],'.-',ms=2,lw=.5);axs[1].set_ylabel(channel+'\n(native units)')
        if 'acc' in traces:
            a=traces['acc'];axs[2].plot(a['time'],a['acc0'],lw=.5);axs[2].set_ylabel('acc0 RMS / 0.1 s\nmm/s²')
        elif 'ct' in traces:
            a=traces['ct'];axs[2].plot(a['time'],a['value'],'o',ms=3);axs[2].set_ylabel('CT value\n(native units; no interpolation)')
        else:
            axs[2].plot(mt['time'],mt['watt'],'.-',ms=2,lw=.5);axs[2].set_ylabel('Power (W)')
        for _,label in labels.iterrows():axs[3].plot([label.start,label.end],[label.label,label.label],lw=5,color=COLORS[int(label.label)])
        axs[3].set(yticks=[0,1,2],ylabel='Native cutting label',xlabel='Sensor time (s)')
        for ax in axs:
            shade_labels(ax,labels,0,float(labels.end.max()+10));ax.grid(alpha=.2)
        axs[0].set_xlim(0,max(float(labels.end.max()+10),float(rt[-1])))
        fig.suptitle(group+' — actual data; labels: 0 stable, 1 abnormal, 2 stable defective-tool')
        fig.savefig(run/'figures'/(key+'_sensor_label_timeline.png'),dpi=145);plt.close(fig)
        if not mapping.get('accepted'):continue
        # Show one sequence per native class present, plus the two observed MTC-gap cuts.
        eligible=pilot[(pilot.group_id==group)&pilot.frame_contract_pass]
        examples=[int(a.iloc[0].source_row) for _,a in eligible.groupby('native_label')]
        examples += [int(a.source_row) for _,a in eligible.iterrows() if not a.common_mtc_sensor_gate_pass]
        examples=sorted(set(examples))
        cap=cv2.VideoCapture(media[group]['video'],cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1])
        for source_row in examples:
            record=eligible[eligible.source_row==source_row].iloc[0];selected=frames[(frames.group_id==group)&(frames.source_row==source_row)].sort_values('frame_order')
            fig=plt.figure(figsize=(16,11.5),layout='constrained');grid=fig.add_gridspec(4,8,height_ratios=[2.8,2.8,1.1,1.1]);tensor=[]
            for order,(_,frame_rec) in enumerate(selected.iterrows()):
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(frame_rec.native_frame_index));ok,frame=cap.read();assert ok
                assert hashlib.sha256(frame.tobytes()).hexdigest()==frame_rec.decoded_frame_sha256
                image=corrected_frame(frame,*media[group]['sample_aspect_ratio']);rgb=Image.fromarray(image)
                tensor.append(np.asarray(ImageOps.pad(rgb,(224,224),color='black')).transpose(2,0,1))
                ax=fig.add_subplot(grid[order//8,order%8]);ax.imshow(image);ax.axis('off')
                ax.set_title(f"{order+1:02d}: v={frame_rec.video_pts_s:.3f}s\ns={frame_rec.mapped_sensor_time_s:.3f}s",fontsize=8)
            tensor=np.stack(tensor);assert tensor.shape==(16,3,224,224) and tensor.dtype==np.uint8
            np.save(run/'cache'/(key+f'_row{source_row}_tensor.npy'),tensor)
            low,high=record.start_s-2,record.end_s+2
            ax=fig.add_subplot(grid[2,:]);ax.plot(rt,ref,lw=.8,label='reference audio')
            ax.plot(vt,vf,lw=.7,alpha=.7,label='mapped video audio');ax.set_xlim(low,high);ax.set_ylabel('Audio log energy');ax.legend(fontsize=8)
            ax2=fig.add_subplot(grid[3,:],sharex=ax)
            if 'acc' in traces:a=traces['acc'];ax2.plot(a['time'],a['acc0'],lw=.8,label='acc0 RMS / 0.1 s (mm/s²)')
            else:ax2.plot(mt['time'],mt['smarms'],'o-',ms=3,lw=.7,label='spindle acceleration RMS (mm/s²)')
            twin=ax2.twinx();twin.plot(mt['time'],mt['S_Axis_Load'],'.-',ms=3,lw=.6,color='tab:purple',label='spindle load (%)');twin.set_ylabel('Load (%)',color='tab:purple')
            for axis in (ax,ax2):
                shade_labels(axis,labels,low,high)
                for t in selected.mapped_sensor_time_s:axis.axvline(t,color='black',alpha=.2,lw=.5)
                axis.axvline(record.start_s,color='black',ls='--',lw=.8);axis.axvline(record.end_s,color='black',ls='--',lw=.8);axis.grid(alpha=.2)
            ax2.set(xlabel='Sensor time (s); vertical lines are the 16 actual frame times',ylabel='Sensor activity');ax2.legend(fontsize=8)
            fig.suptitle(f"{group}, CSV row {source_row}: native label {record.native_label}; [{record.start_s:.3f}, {record.end_s:.3f}) s\n"
                         f"video = sensor {offset:+.3f}s; ±{mapping['uncertainty_s']:.3f}s empirical alignment bound; common-MTC eligible={record.verified_multimodal_example}",fontsize=12)
            path=run/'figures/examples'/(key+f'_row{source_row}_16frames.png');fig.savefig(path,dpi=140);plt.close(fig)
            summaries.append({'interval_id':record.interval_id,'figure':str(path.relative_to(run)),'tensor_shape':list(tensor.shape),'dtype':'uint8','all_native_hashes_match':True})
        cap.release()
    dump(run/'manifests/diagnostic_examples.json',summaries);print('Representative sequences',len(summaries))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);main(parser.parse_args().run)
