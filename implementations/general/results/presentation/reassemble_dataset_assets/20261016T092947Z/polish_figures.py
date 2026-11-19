"""Presentation layout adjustments only, restricted to this new asset directory."""
from pathlib import Path
import os,sys,json,io
OUT=Path(__file__).resolve().parent;REPO=OUT.parents[3]
os.environ['MPLCONFIGDIR']=str(OUT/'plot_cache');sys.path.insert(0,str(REPO/'src'))
import cv2,numpy as np,pandas as pd,h5py,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont
from scipy.signal import spectrogram
from reassemble.media import blob_bytes
cv2.setNumThreads(1)
examples=pd.read_csv(OUT/'selected_examples.csv',dtype={'recording_id':str,'segment_id':str});frames=pd.read_csv(OUT/'frame_selection.csv',dtype={'recording_id':str,'segment_id':str})
fontpath=findfont('DejaVu Sans');large=ImageFont.truetype(fontpath,28);small=ImageFont.truetype(fontpath,21)
for row in examples.itertuples():
    g=frames[(frames.example_id==row.example_id)&(frames.selection_type=='model16')]
    cap=cv2.VideoCapture(str(REPO/row.hand_video_path));assert cap.isOpened()
    canvas=Image.new('RGB',(1980,1752),'white');draw=ImageDraw.Draw(canvas)
    draw.text((24,15),f'{row.action.upper()} | recorded outcome: {"failure" if row.failure else "success"}',fill='#123047',font=large)
    draw.text((24,55),f'{row.recording_id} / segment {row.segment_id} | {row.duration:.3f} s | 16 core-extractor frames',fill='#123047',font=small)
    for i,r in enumerate(g.itertuples()):
        cap.set(cv2.CAP_PROP_POS_FRAMES,r.frame_index);ok,im=cap.read();assert ok
        im=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((480,360),Image.Resampling.LANCZOS)
        x=12+(i%4)*492;y=112+(i//4)*405
        draw.text((x,y),f'{r.relative_position:.0%} | frame {r.frame_index}',fill='#123047',font=small);canvas.paste(im,(x,y+32))
    cap.release();canvas.save(OUT/'contact_sheets'/f'{row.example_id}_16frame.png')
    print('LAYOUT',row.example_id,flush=True)
# Preserve the same excerpt, sample rate, channel count and absolute PSD values;
# use each excerpt's maximum minus 80 dB so low-amplitude recordings are readable.
meta=pd.read_csv(OUT/'audio_metadata.csv');details=json.loads((OUT/'audio_decode_evidence.json').read_text());rid=sorted(examples.recording_id.unique())[0]
row=examples[examples.recording_id==rid].iloc[0];settings=[]
with h5py.File(REPO/row.sensor_source_path,'r') as h:
    for n in ['hama1_audio','hama2_audio','hand_audio']:
        d=next(x for x in details if x['recording_id']==rid and x['stream_name']==n)
        with sf.SoundFile(io.BytesIO(blob_bytes(h[n]))) as audio:
            rate=audio.samplerate;channels=audio.channels;start=d['central_excerpt_start_seconds'];audio.seek(round(start*rate));samples=audio.read(round(10*rate),dtype='float32',always_2d=True)
        spectra=[]
        for j in range(channels):
            freq,t,power=spectrogram(samples[:,j],fs=rate,nperseg=512,noverlap=384,scaling='density');spectra.append(10*np.log10(np.maximum(power,1e-20)))
        vmax=float(max(v.max() for v in spectra));vmin=vmax-80
        fig,axes=plt.subplots(channels,1,figsize=(12,3+channels*2),sharex=True,squeeze=False,layout='constrained')
        for j,ax in enumerate(axes[:,0]):
            im=ax.pcolormesh(t+start,freq/1000,spectra[j],shading='auto',cmap='magma',vmin=vmin,vmax=vmax);ax.set_ylabel(f'Channel {j}\nFrequency (kHz)');fig.colorbar(im,ax=ax,label='PSD dB re 1 amplitude²/Hz')
        axes[-1,0].set_xlabel('Decoded stream time (s; zero at stream start)')
        fig.suptitle('Illustrative raw-recording audio — not verified as action-aligned\n'+n+' | '+rid+'\nColor range: excerpt maximum minus 80 dB to maximum (display only)',fontsize=11)
        fig.savefig(OUT/'audio'/f'{n}_spectrogram.png',dpi=150);plt.close(fig)
        settings.append({'stream_name':n,'recording_id':rid,'excerpt_start_seconds':start,'excerpt_duration_seconds':len(samples)/rate,'nperseg':512,'noverlap':384,'vmin_dB':vmin,'vmax_dB':vmax,'power_floor':1e-20,'rescaling':'Only color limits change; PSD values, samples and excerpt choice unchanged.'})
with (OUT/'figure_presentation_notes.json').open('x') as fp:json.dump({'contact_sheets':'16-frame sheets regenerated with fixed gutters and 480 × 360 RGB thumbnails, same source indices, no crops or content edits. Five-frame sheets retain original layout.','spectrogram_settings':settings},fp,indent=2)
print('PRESENTATION POLISH COMPLETE',flush=True)
