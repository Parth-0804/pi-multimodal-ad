"""Unaltered source-frame contact sheets; no inference or model execution."""
import json
import subprocess
import shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
from acquisition import ROOT


if __name__=='__main__':
    out=ROOT/'visual_screening';out.mkdir(exist_ok=True)
    videos=json.loads((ROOT/'checks/robofac_source_preview_selection.json').read_text())
    records=[]
    cv2.setNumThreads(1)
    for index,relative in enumerate(videos):
        path=ROOT/'source_evidence/robofac/files'/relative
        probe=(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
               if shutil.which('ffprobe') else {'status':'ffprobe unavailable on PATH; OpenCV source properties only'})
        cap=cv2.VideoCapture(str(path));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
        indices=np.unique(np.linspace(0,n-1,8,dtype=int)).tolist();frames=[]
        cap.release()
        # The installed OpenCV decoder cannot decode AV1. Reuse the existing
        # repository FFmpeg binary on CPU; never request hardware acceleration.
        ffmpeg=shutil.which('ffmpeg') or str(ROOT.parents[1]/'MILLING DATASET/.tools/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2')
        frame_dir=out/f'RoboFAC_source_{index+1:02d}_frames';frame_dir.mkdir(exist_ok=True)
        expected=[frame_dir/f'frame_{j+1:02d}.png' for j in range(len(indices))]
        if not all(p.exists() for p in expected):
            expression='select='+ '+'.join(f'eq(n\\,{i})' for i in indices)
            subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-n','-hwaccel','none','-threads','1','-i',str(path),
                '-filter_threads','1','-vf',expression,'-vsync','0','-frames:v',str(len(indices)),str(frame_dir/'frame_%02d.png')],check=True)
        frames=[Image.open(p).convert('RGB') for p in expected]
        tile=(400,320);sheet=Image.new('RGB',(tile[0]*4,tile[1]*2+50),'white');draw=ImageDraw.Draw(sheet)
        draw.text((8,8),'UNBLINDED SOURCE SCREEN: '+relative.split('/')[0]+' / '+Path(relative).name,fill='black')
        for j,(i,frame) in enumerate(zip(indices,frames)):
            frame.thumbnail((400,285));x=(j%4)*400;y=50+(j//4)*320
            sheet.paste(frame,(x,y));draw.text((x+5,y+290),f'frame {i}; t={i/fps:.3f}s',fill='black')
        dest=out/f'RoboFAC_source_{index+1:02d}.jpg';sheet.save(dest,quality=90)
        records.append({'dataset':'RoboFAC','source':relative,'frames':n,'fps':fps,'sample_indices':indices,'contact_sheet':str(dest.relative_to(ROOT)),'ffprobe':probe})
    for name in ['pour_s','pour_f']:
        relative='failure_code/assets/'+name+'.gif';path=ROOT/'source_evidence'/relative
        gif=Image.open(path);indices=np.unique(np.linspace(0,gif.n_frames-1,8,dtype=int)).tolist()
        sheet=Image.new('RGB',(4*224,2*260+35),'white');draw=ImageDraw.Draw(sheet)
        draw.text((5,5),'Official FAILURE demonstration; recording ID not provided: '+name,fill='black')
        for j,i in enumerate(indices):
            gif.seek(i);frame=gif.convert('RGB');frame.thumbnail((224,224));x=(j%4)*224;y=35+(j//4)*260
            sheet.paste(frame,(x,y));draw.text((x+3,y+228),f'GIF frame {i}',fill='black')
        dest=out/f'FAILURE_official_{name}.jpg';sheet.save(dest,quality=92)
        records.append({'dataset':'FAILURE','source':relative,'frames':gif.n_frames,'sample_indices':indices,'contact_sheet':str(dest.relative_to(ROOT))})
    (ROOT/'checks/source_preview_audit.json').write_text(json.dumps(records,indent=2)+'\n')
