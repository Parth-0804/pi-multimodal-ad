"""Verify pilot arrays/media and build a blinded three-camera source gallery."""
import hashlib,html,json,re,subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2,numpy as np,pandas as pd
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sources import ROOT

VIEWS=['cam_high','cam_left_wrist','cam_right_wrist']
FFMPEG=ROOT.parents[1]/'MILLING DATASET/.tools/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
GALLERY=ROOT/'MATCHED_EXAMPLE_GALLERY'
CSS='body{font:16px system-ui;margin:24px;max-width:1500px;background:#f4f6f8;color:#17212b}a{color:#155aa0}img{max-width:100%;height:auto}section{background:white;padding:16px;margin:16px 0;border-radius:10px}.views{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.views img,.views canvas{width:100%}input{width:100%}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:8px}'


def read_rows():return json.loads((GALLERY/'UNBLINDING/SOURCE_LABEL_KEY.json').read_text())


def decode_one(job):
    row,key,view=job;source=ROOT/'source_evidence/vifailback'/row[key]
    directory=GALLERY/'assets'/row['blind_id']/view;directory.mkdir(parents=True,exist_ok=True)
    n=int(row['num_frames']);indices=[k*(n-1)//15 for k in range(16)]
    assert len(set(indices))==16
    paths=[directory/f'frame_{j:02d}.png' for j in range(16)]
    log=directory/'decode.log'
    if not all(p.exists() for p in paths):
        assert not any(p.exists() for p in paths),'Partial decode preserved; inspect before retry'
        expression='select='+ '+'.join(f'eq(n\\,{i})' for i in indices)+',showinfo'
        command=[str(FFMPEG),'-hide_banner','-loglevel','info','-n','-hwaccel','none','-threads','1','-i',str(source),
            '-filter_threads','1','-vf',expression,'-vsync','0','-frames:v','16','-start_number','0',str(directory/'frame_%02d.png')]
        run=subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
        log.write_text(run.stderr);assert run.returncode==0,source
    stderr=log.read_text();pts=[float(x) for x in re.findall(r'\bn:\s*\d+.*?pts_time:([\d.eE+-]+)',stderr)]
    assert len(pts)==16 and np.all(np.diff(pts)>0),(row['blind_id'],view,pts)
    cap=cv2.VideoCapture(str(source));count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
    assert count==n and abs(fps-25)<1e-8
    frames=[Image.open(p).convert('RGB') for p in paths]
    assert all(x.size==(640,480) for x in frames)
    for crop in [False,True]:
        sheet=Image.new('RGB',(1280,4*270+35),'white');draw=ImageDraw.Draw(sheet)
        draw.text((8,8),row['blind_id']+' '+view+(' fixed-region enlargement' if crop else ' full source view'),fill='black')
        for j,(frame,index,time) in enumerate(zip(frames,indices,pts)):
            shown=frame.crop((128,96,512,384)) if crop else frame.copy()
            shown=shown.resize((320,240));x=(j%4)*320;y=35+(j//4)*270
            sheet.paste(shown,(x,y));draw.text((x+3,y+243),f'{j+1:02d}: source frame {index}, {time:.3f}s',fill='black')
        sheet.save(directory/('region_sequence.jpg' if crop else 'full_sequence.jpg'),quality=93)
    hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    return {'blind_id':row['blind_id'],'view':view,'source':row[key],'source_frame_count':count,'fps':fps,'frame_indices':indices,'PTS_seconds':pts,
        'distinct_selected_file_positions':len(set(indices)),'unique_selected_decoded_images':len(set(hashes)),
        'image_sha256':hashes,'decoder_reports_error':bool(re.search(r'Error while|Invalid data|corrupt',stderr,re.I))}


def sensor_audit(row,views,offset):
    df=pd.read_parquet(ROOT/'source_evidence/vifailback'/row['data']);n=len(df);indices=views[0]['frame_indices']
    assert n==int(row['num_frames']) and np.array_equal(df.frame_index,np.arange(n))
    assert (df.episode_index==int(row['episode_index'])).all() and (df.task_index==int(row['task_index'])).all()
    assert np.array_equal(df['index'].to_numpy(),np.arange(offset,offset+n))
    time=df.timestamp.to_numpy(dtype=float);assert np.all(np.diff(time)>0)
    flags=np.stack(df['complementary_info.vifailback_flags'].to_numpy());assert flags.shape==(n,3)
    assert (flags[:,0]==(row['episode_success']=='failure')).all()
    for i,kind in [(1,'avoid'),(2,'correct')]:assert np.flatnonzero(flags[:,i]).tolist()==json.loads(row[kind+'_keyframe_indices'])
    arrays={};summary={}
    for key in ['observation.state','observation.velocity','observation.effort']:
        a=np.stack(df[key].to_numpy()).astype(float);assert a.shape==(n,14)
        arrays[key]=a;summary[key]={'shape':list(a.shape),'nonfinite':int((~np.isfinite(a)).sum()),
            'channel_peak_to_peak':np.ptp(a,axis=0).tolist(),'channel_std':np.std(a,axis=0).tolist(),
            'varying_channels':int((np.ptp(a,axis=0)>1e-8).sum()),'all_zero_channels':np.flatnonzero((a==0).all(axis=0)).tolist()}
    assert all(x['nonfinite']==0 for x in summary.values())
    fig,axes=plt.subplots(3,1,figsize=(13,8),sharex=True)
    for ax,(key,a) in zip(axes,arrays.items()):
        ax.plot(time,a,linewidth=.65);ax.set_ylabel(key.removeprefix('observation.')+' (native units)');ax.grid(alpha=.2)
        for t in time[indices]:ax.axvline(t,color='gray',alpha=.2,linewidth=.6)
    axes[0].set_title(row['blind_id']+' measured observation streams; grey lines = uniformly selected frames')
    axes[-1].set_xlabel('Episode time (seconds)');fig.tight_layout();fig.savefig(GALLERY/'assets'/row['blind_id']/'sensor_timeline.png',dpi=130);plt.close(fig)
    max_error=max(float(np.max(np.abs(time[indices]-np.asarray(v['PTS_seconds'])))) for v in views)
    assert max_error<1e-4
    return {'blind_id':row['blind_id'],'episode_index':int(row['episode_index']),'parquet':row['data'],'frames':n,
        'timestamp_vs_index_over25_max_error_s':float(np.max(np.abs(time-np.arange(n)/25))),
        'video_sensor_selected_timestamp_max_error_s':max_error,'arrays':summary,'frame_flags_native_metadata_consistent':True,
        'global_index_offset':offset,'source_columns':list(df.columns)}


def build_page(row,views,instruction):
    bid=row['blind_id'];n=int(row['num_frames']);indices=views[0]['frame_indices']
    frames=[{'index':i,'time':round(i/25,6)} for i in indices]
    content=f'<h1>Blind case {bid}</h1><p><a href="index.html">All cases</a></p><p>{html.escape(instruction)}</p><p>Outcome, failure category, pair and original episode ID are withheld. Sixteen positions span the complete episode; no annotated failure keyframes were used.</p><section><label id="stamp"></label><input id="step" type="range" min="0" max="15" value="0"><div class="views">'
    for view in VIEWS:content+=f'<div><h3>{view}</h3><img id="{view}" alt="Full camera frame"><canvas id="crop_{view}" width="640" height="480"></canvas></div>'
    content+='</div><p>Top: complete source view. Below: the same fixed center region (20–80% in x and y), enlarged for both classes. A crop may miss a relevant object; the full view remains authoritative.</p></section>'
    for view in VIEWS:content+=f'<section><h2>{view}: all sixteen full views</h2><a href="assets/{bid}/{view}/full_sequence.jpg"><img loading="lazy" src="assets/{bid}/{view}/full_sequence.jpg"></a><details><summary>Enlarged region sequence</summary><img loading="lazy" src="assets/{bid}/{view}/region_sequence.jpg"></details></section>'
    content+=f'<section><h2>Measured numerical streams</h2><img src="assets/{bid}/sensor_timeline.png"><p>Channels 0–6: left six joints plus gripper; 7–13: right six joints plus gripper. Physical calibration/units remain unverified; commands and outcome flags are excluded from these plots.</p></section>'
    content+=f'<script>const frames={json.dumps(frames)}, views={json.dumps(VIEWS)};function update(){{const k=Number(document.getElementById("step").value);document.getElementById("stamp").textContent=`Selected position ${{k+1}}/16; source frame ${{frames[k].index}}; ${{frames[k].time.toFixed(3)}} s`;for(const v of views){{let im=document.getElementById(v);im.onload=()=>{{let c=document.getElementById("crop_"+v).getContext("2d");c.drawImage(im,128,96,384,288,0,0,640,480)}};im.src=`assets/{bid}/${{v}}/frame_${{String(k).padStart(2,"0")}}.png`;}}}}document.getElementById("step").addEventListener("input",update);update();</script>'
    (GALLERY/(bid+'.html')).write_text('<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+bid+'</title><style>'+CSS+'</style><body>'+content+'</body></html>')
    sheet=Image.new('RGB',(1920,4*150+35),'white');draw=ImageDraw.Draw(sheet);draw.text((8,8),bid+' blinded overview: each cell has high / left wrist / right wrist',fill='black')
    for j,index in enumerate(indices):
        x=(j%4)*480;y=35+(j//4)*150
        for k,view in enumerate(VIEWS):
            im=Image.open(GALLERY/'assets'/bid/view/f'frame_{j:02d}.png').convert('RGB').resize((160,120));sheet.paste(im,(x+k*160,y))
        draw.text((x+3,y+122),f'frame {index}; {index/25:.2f}s',fill='black')
    sheet.save(GALLERY/'assets'/bid/'BLINDED_OVERVIEW.jpg',quality=94)


if __name__=='__main__':
    cv2.setNumThreads(1);rows=read_rows()
    jobs=[(row,key,view) for row in rows for key,view in zip(['video_high','video_left','video_right'],VIEWS)]
    with ThreadPoolExecutor(max_workers=2) as pool:media=list(pool.map(decode_one,jobs))
    episodes=[json.loads(l) for l in (ROOT/'source_evidence/vifailback/meta/episodes.jsonl').open()]
    offsets={};offset=0
    for ep in episodes:offsets[ep['episode_index']]=offset;offset+=ep['length']
    tasks={x['task_index']:x['task'] for x in [json.loads(l) for l in (ROOT/'source_evidence/vifailback/meta/tasks.jsonl').open()]}
    sensors=[]
    for row in rows:
        views=[x for x in media if x['blind_id']==row['blind_id']]
        sensors.append(sensor_audit(row,views,offsets[int(row['episode_index'])]));build_page(row,views,tasks[int(row['task_index'])])
    (ROOT/'checks/pilot_media_audit.json').write_text(json.dumps(media,indent=2)+'\n')
    (ROOT/'checks/pilot_numerical_audit.json').write_text(json.dumps(sensors,indent=2)+'\n')
    body='<h1>ViFailback: initial blinded visual examination</h1><p>20 original executions; 16 uniform timestamps each; all three source cameras. Review independently before opening the source key. These pages contain no outcome labels or native failure keyframes.</p><p>For each case record visibility of objects/gripper, apparent execution outcome, physical evidence, and uncertainty. Absence of visible failure is not proof of success. This gallery is a feasibility screen, not a model benchmark.</p>'
    for row in rows:
        bid=row['blind_id'];body+=f'<section><h2><a href="{bid}.html">Case {bid}: synchronized views, zoom and sensors</a></h2><img loading="lazy" src="assets/{bid}/BLINDED_OVERVIEW.jpg"></section>'
    body+='<p>After recording judgments, open <a href="UNBLINDING/index.html">the separate source identity and native label key</a>. Do not change frame selection after unblinding.</p>'
    (GALLERY/'index.html').write_text('<!doctype html><html><meta charset="utf-8"><title>ViFailback blind review</title><style>'+CSS+'</style><body>'+body+'</body></html>')
    # The original source identity is intentionally available only in this separate key.
    key='<h1>UNBLINDING: native labels and original identities</h1><p>Open only after saving independent observations.</p><table><tr><th>Blind ID</th><th>Pair</th><th>Episode</th><th>Original identity</th><th>Native outcome</th><th>Failure category</th></tr>'
    for row in rows:key+='<tr>'+''.join('<td>'+html.escape(str(row[k]))+'</td>' for k in ['blind_id','pair','episode_index','source_hdf5','episode_success','failure_type'])+'</tr>'
    (GALLERY/'UNBLINDING/index.html').write_text('<!doctype html><meta charset="utf-8"><style>'+CSS+'</style>'+key+'</table>')
    print('Gallery complete: 20 episodes, 60 videos, 960 RGB source frames; exact numerical/media audit saved.')
