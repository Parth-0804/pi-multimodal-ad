"""Create literal ROI crops, contact sheets, PDF and an offline frame viewer."""
import argparse
import csv
import html
import importlib.metadata
import io
import json
import os
import platform
import subprocess
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image,ImageDraw,ImageFont

from prepare_matched_visual_review import digest,write_json,write_csv,COHORT

# Coordinates in SAR-corrected 270x480 full-display pixels, [left,top,right,bottom).
# Chosen to include tool/workpiece context in both midpoint views, before examining
# labels as visible events. They are approximate context ROIs, not anomaly boxes.
ROI={
 'P01':[75,100,250,350],
 'P02':[70,210,245,405],
 'P03':[90,210,265,415],
 'P04':[75,105,245,330],
 'P05':[75,90,245,350],
}


def font(size=20):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)


def fit_image(im,box):
    im=im.copy();im.thumbnail(box,Image.Resampling.BILINEAR);return im


def contact_sheet(run,cut,frames,kind):
    cols=4;slot_w=300 if kind=='full' else 400;slot_h=540 if kind=='full' else 440
    canvas=Image.new('RGB',(cols*slot_w,170+4*slot_h),'white');d=ImageDraw.Draw(canvas)
    d.text((15,12),f"{cut['cut_id']} | native label {cut['native_label']} | {cut['group_id']}",font=font(23),fill='black')
    d.text((15,48),f"source CSV row {cut['source_row']} | sensor [{cut['start_s']:.3f}, {cut['end_s']:.3f}) s | direction {cut['direction']}",font=font(18),fill='black')
    title='Full camera view (SAR corrected; no crop)' if kind=='full' else 'Fixed tool/workpiece-context ROI, displayed enlarged; occlusion is preserved'
    d.text((15,80),title,font=font(18),fill='black')
    d.text((15,110),f"Alignment +/-{cut['uncertainty_s']:.3f}s; 16 ordered snapshots; optical anomaly visibility UNVERIFIED",font=font(17),fill='#7b3900')
    for i,f in enumerate(frames):
        path=run/f['full_image'] if kind=='full' else run/f['roi_image']
        im=fit_image(Image.open(path), (slot_w-20,slot_h-70))
        x=(i%4)*slot_w+(slot_w-im.width)//2;y=160+(i//4)*slot_h
        canvas.paste(im,(x,y));d.text(((i%4)*slot_w+10,y+slot_h-61),
            f"#{i+1:02d} native {f['native_frame_index']}",font=font(16),fill='black')
        d.text(((i%4)*slot_w+10,y+slot_h-38),f"video {f['video_pts_s']:.3f}s | sensor {f['mapped_sensor_time_s']:.3f}s",font=font(13),fill='black')
    path=run/'figures'/f"{cut['cut_id']}_{kind}_16frames.jpg";canvas.save(path,quality=93)
    return path


def pair_preview(run,pair,cuts,frames):
    # Two columns (normal, abnormal); each contains full view and enlarged ROI.
    canvas=Image.new('RGB',(1400,850),'#f5f7fa');d=ImageDraw.Draw(canvas)
    d.text((15,12),f"{pair['pair_id']} | {pair['group_id']} | frame 08 of each cut",font=font(25),fill='black')
    d.text((15,52),'All recorded numerical settings match. Direction differs: normal DOWN / abnormal UP.',font=font(20),fill='#883d00')
    for n,label in enumerate((0,1)):
        cut=next(c for c in cuts if c['pair_id']==pair['pair_id'] and c['native_label']==label)
        f=next(r for r in frames if r['cut_id']==cut['cut_id'] and r['frame_order']==7)
        x=15+n*700
        d.text((x,95),f"{'NORMAL' if label==0 else 'ABNORMAL'} (native {label}) - row {cut['source_row']}",font=font(23),fill='black')
        im=Image.open(run/f['full_image']);canvas.paste(im,(x,145))
        box=ROI[pair['pair_id']];d.rectangle((x+box[0],145+box[1],x+box[2]-1,145+box[3]-1),outline='#ec7f19',width=3)
        crop=fit_image(Image.open(run/f['roi_image']),(380,600));canvas.paste(crop,(x+290,145))
        d.text((x,755),f"video {f['video_pts_s']:.3f}s | sensor {f['mapped_sensor_time_s']:.3f}s",font=font(17),fill='black')
    d.text((15,800),'ROI = approximate cutting context, not an anomaly localization. No enhancement; visibility remains unverified.',font=font(18),fill='#5b6472')
    path=run/'figures'/f"{pair['pair_id']}_comparison.jpg";canvas.save(path,quality=93)
    return path


def write_viewer(run,pairs,cuts,frames):
    data={'pairs':pairs,'cuts':cuts,'frames':frames,'roi':ROI}
    payload=json.dumps(data,ensure_ascii=False).replace('</','<\/')
    template='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MSM — Five matched normal / abnormal pairs</title>
<style>
:root{color-scheme:light;font-family:system-ui,sans-serif;color:#172333;background:#eef2f7}*{box-sizing:border-box}body{margin:0;padding:24px;max-width:1660px;margin:auto}h1{font-size:28px;margin:0 0 10px}p{line-height:1.5}.muted{color:#556378}.notice{background:#fff4dc;border-left:5px solid #cc8400;padding:14px 18px;border-radius:8px;margin:16px 0}.toolbar,.card,.review{background:white;border:1px solid #d7dfea;border-radius:12px;padding:18px}.toolbar{position:sticky;top:0;z-index:2;box-shadow:0 5px 15px #193b5f10}button,select,input{font:inherit}button,select{padding:8px 13px;border:1px solid #b8c6d8;border-radius:7px;background:white;cursor:pointer}button:hover{background:#e8f1fb}button.active{background:#1c4c80;color:white}.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}.row + .row{margin-top:14px}input[type=range]{flex:1;min-width:200px}.pairs{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:18px 0}.card h2{margin:0 0 6px;font-size:22px}.badge{font-size:13px;padding:4px 8px;border-radius:5px;background:#e9f0f8}.images{display:grid;grid-template-columns:270fr 400fr;gap:12px;align-items:start;margin:16px 0}.fullbox{position:relative}.fullbox img{width:100%;height:auto;display:block}.roi{width:100%;height:auto;display:block;border:2px solid #d87a14}.bbox{position:absolute;border:2px solid #ed8a23;pointer-events:none}figcaption{font-size:13px;color:#556378;margin:6px 0}figure{margin:0}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:7px 10px;border-bottom:1px solid #dfe5ee;text-align:left}a{color:#174f87}.timeline{display:grid;grid-template-columns:repeat(16,1fr);gap:3px}.timeline button{padding:6px 0;font-size:12px}.details{font-size:13px;line-height:1.6}.review{margin:18px 0}.notes{width:100%;min-height:80px;border:1px solid #b8c6d8;border-radius:5px;padding:10px}label{font-size:14px}.review select{max-width:100%}@media(max-width:1050px){.pairs{grid-template-columns:1fr}.toolbar{position:static}}@media print{.toolbar,.review{display:none}.pairs{display:block}.card{break-inside:avoid}}
</style></head><body>
<h1>MSM: five matched normal–abnormal cutting pairs</h1>
<p>10 real cuts · 160 audited native frames · 3 VM20i pairs + 2 VMX30Ui pairs. Version 2. Local files only; no model predictions.</p>
<div class="notice"><strong>Matching limitation:</strong> every pair shares its experiment and all recorded numerical settings, tool category and material. <strong>Cut direction differs in all five pairs: normal DOWN, abnormal UP.</strong> This can confound visual differences. The ROI is an approximate tool/workpiece context, not a defect annotation. Enlargement adds no information hidden by coolant or droplets.</div>
<div class="toolbar"><div id="pairButtons" class="row"></div><div class="row"><button id="prev">← Previous frame</button><button id="play">Play snapshots</button><input id="position" type="range" min="0" max="15" value="7" aria-label="Frame position"><button id="next">Next frame →</button><strong id="counter"></strong></div><div class="row"><label><input type="checkbox" id="box" checked> Show crop rectangle</label><span class="muted">Positions match relative locations inside each cut; they are not simultaneous events. Arrow keys step frames. Playback is a slideshow, not original-time video.</span></div></div>
<h2 id="pairTitle"></h2><p id="settings" class="details"></p><div id="cards" class="pairs"></div>
<div class="review"><h2>Record your observations</h2><p class="muted">Review notes stay in this browser tab. Export JSON to keep them. These are qualitative observations, not new ground-truth labels.</p><div id="reviewControls"></div><div class="row"><button id="export">Download review notes</button><a href="REVIEW_TEMPLATE.csv" download>CSV review template</a><a href="MATCHED_CUT_REVIEW.pdf">Printable PDF: all 160 frames in both views</a><a href="README.md">Guide and provenance</a></div></div>
<details><summary>All cutting parameters and matching limitations</summary><div id="allParameters"></div></details>
<script id="data" type="application/json">__DATA__</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('data').textContent);let pairIndex=0,frameIndex=7,timer=null;const notes={};
const $=id=>document.getElementById(id);const pairs=data.pairs;const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
for(let k=0;k<pairs.length;k++){const b=document.createElement('button');b.textContent=pairs[k].pair_id+' · '+pairs[k].group_id;b.onclick=()=>{pairIndex=k;render()};$('pairButtons').appendChild(b)}
function save(id,key,value){notes[id]??={cut_id:id};notes[id][key]=value}
function question(id,key,label,values){const wrap=document.createElement('label');wrap.textContent=label+' ';const select=document.createElement('select');for(const v of ['',...values]){const o=document.createElement('option');o.value=v;o.textContent=v||'Not reviewed';select.appendChild(o)}select.value=notes[id]?.[key]||'';select.onchange=()=>save(id,key,select.value);wrap.appendChild(select);return wrap}
function render(){const p=pairs[pairIndex];$('position').value=frameIndex;$('counter').textContent=(frameIndex+1)+' / 16';$('pairTitle').textContent=p.pair_id+' — '+p.group_id;
Array.from($('pairButtons').children).forEach((b,k)=>b.classList.toggle('active',k===pairIndex));const s=p.matching_parameters;$('settings').textContent=`Matched: N ${s.N} rpm; ap ${s.ap} mm; ae ${s.ae} mm; F ${s.F} mm/s; Z ${s.Z} teeth; D ${s.D} mm; Tool ${s.Tool}; material ${s.Workpiece}. Direction: normal ${p.normal_direction}, abnormal ${p.abnormal_direction}.`;
$('cards').replaceChildren();$('reviewControls').replaceChildren();
for(const label of [0,1]){const c=data.cuts.find(c=>c.pair_id===p.pair_id&&c.native_label===label);const fs=data.frames.filter(f=>f.cut_id===c.cut_id).sort((a,b)=>a.frame_order-b.frame_order);const f=fs[frameIndex];const box=data.roi[p.pair_id];const card=document.createElement('section');card.className='card';
card.innerHTML=`<h2>${label===0?'Normal':'Abnormal'} <span class="badge">native label ${label}</span></h2><div class="details">${esc(c.interval_id)}<br>Sensor cut [${c.start_s.toFixed(3)}, ${c.end_s.toFixed(3)}) s · ${c.duration_s.toFixed(3)} s · ${esc(c.direction)}<br>Frame ${frameIndex+1}/16 · native index ${f.native_frame_index}<br><strong>Video ${f.video_pts_s.toFixed(3)} s → sensor ${f.mapped_sensor_time_s.toFixed(3)} s</strong> · bound ±${c.uncertainty_s.toFixed(3)} s</div>
<div class="images"><figure><div class="fullbox"><a href="${esc(f.full_image)}" target="_blank" rel="noopener"><img src="${esc(f.full_image)}" alt="Full camera view for ${esc(c.cut_id)}, frame ${frameIndex+1}"></a><div class="bbox" style="display:${$('box').checked?'block':'none'};left:${box[0]/270*100}%;top:${box[1]/480*100}%;width:${(box[2]-box[0])/270*100}%;height:${(box[3]-box[1])/480*100}%"></div></div><figcaption>Full camera view, source SAR corrected. Click to open image.</figcaption></figure><figure><a href="${esc(f.roi_image)}" target="_blank" rel="noopener"><img class="roi" src="${esc(f.roi_image)}" alt="Fixed enlarged cutting-context crop"></a><figcaption>Same fixed context crop for both cuts; 3× display enlargement. No enhancement.</figcaption></figure></div><div class="timeline"></div><p><a href="figures/${c.cut_id}_full_16frames.jpg">All 16 full views</a> · <a href="figures/${c.cut_id}_roi_16frames.jpg">All 16 crops</a></p>`;
const strip=card.querySelector('.timeline');for(let j=0;j<16;j++){const b=document.createElement('button');b.textContent=j+1;b.classList.toggle('active',j===frameIndex);b.onclick=()=>{frameIndex=j;render()};strip.appendChild(b)}$('cards').appendChild(card);
const group=document.createElement('div');group.className='review';const title=document.createElement('strong');title.textContent=c.cut_id+' — '+c.interval_id;group.appendChild(title);const row=document.createElement('div');row.className='row';row.append(question(c.cut_id,'context_visibility','Milling context',['clear','partial','not visible','uncertain']),question(c.cut_id,'contact_visibility','Tool/workpiece contact',['clear','partial','not visible','uncertain']),question(c.cut_id,'visual_distinction','Visually distinguishable from mate',['yes','no','uncertain']),question(c.cut_id,'occlusion','Occlusion',['none','mild','moderate','severe']));group.appendChild(row);const text=document.createElement('textarea');text.className='notes';text.placeholder='Describe what you can actually see; note coolant, reflections, motion, ROI misses and direction effects.';text.value=notes[c.cut_id]?.comments||'';text.oninput=()=>save(c.cut_id,'comments',text.value);group.appendChild(text);$('reviewControls').appendChild(group)} }
$('position').oninput=e=>{frameIndex=Number(e.target.value);render()};$('box').onchange=render;$('prev').onclick=()=>{frameIndex=(frameIndex+15)%16;render()};$('next').onclick=()=>{frameIndex=(frameIndex+1)%16;render()};$('play').onclick=()=>{if(timer){clearInterval(timer);timer=null;$('play').textContent='Play snapshots'}else{timer=setInterval(()=>{frameIndex=(frameIndex+1)%16;render()},800);$('play').textContent='Pause'}};
document.addEventListener('keydown',e=>{if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;if(e.key==='ArrowRight'){$('next').click();e.preventDefault()}if(e.key==='ArrowLeft'){$('prev').click();e.preventDefault()}});
$('export').onclick=()=>{const rows=data.cuts.map(c=>({...c,...(notes[c.cut_id]||{})}));const blob=new Blob([JSON.stringify({dataset_version:2,export_utc:new Date().toISOString(),review_is_qualitative:true,records:rows},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='MSM_matched_cut_review_notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
$('allParameters').innerHTML='<table><tr><th>Pair</th><th>Experiment</th><th>N rpm</th><th>ap mm</th><th>ae mm</th><th>F mm/s</th><th>Z</th><th>D mm</th><th>Tool / material</th><th>Direction 0 → 1</th></tr>'+pairs.map(p=>{const s=p.matching_parameters;return `<tr><td>${p.pair_id}</td><td>${esc(p.group_id)}</td><td>${s.N}</td><td>${s.ap}</td><td>${s.ae}</td><td>${s.F}</td><td>${s.Z}</td><td>${s.D}</td><td>${esc(s.Tool)} / ${esc(s.Workpiece)}</td><td>${esc(p.normal_direction)} → ${esc(p.abnormal_direction)}</td></tr>`}).join('')+'</table>';
render();
</script></body></html>'''
    with (run/'VIEWER.html').open('x') as f:f.write(template.replace('__DATA__',payload))


def build(run):
    plan=json.loads((run/'config/review_plan.json').read_text());pairs=plan['pairs']
    cuts=json.loads((run/'manifests/cuts.json').read_text());frames=pd.read_csv(run/'manifests/frames_full.csv').to_dict('records')
    write_json(run/'config/roi_config.json',{'coordinate_system':'SAR-corrected full display, 270x480 pixels; half-open rectangle',
         'boxes':ROI,'fixed_per_pair':True,'target':'approximate tool/workpiece context; not a verified contact/anomaly location',
         'selection':'Full-view midpoint montage of the ten metadata-selected cuts; same box for both labels and all 16 frames',
         'enlargement':3,'resampling':'Pillow BILINEAR; no enhancement','information_gain':'none; occluded content cannot be recovered'})
    for f in frames:
        full=Image.open(run/f['full_image']);box=ROI[f['pair_id']]
        assert full.size==(270,480) and 0<=box[0]<box[2]<=270 and 0<=box[1]<box[3]<=480
        crop=full.crop(box);native=(run/f['full_image']).with_name(f"frame_{int(f['frame_order'])+1:02d}_roi_pixels.png")
        crop.save(native)
        assert np.array_equal(np.asarray(Image.open(native)),np.asarray(full)[box[1]:box[3],box[0]:box[2]])
        enlarged=crop.resize((crop.width*3,crop.height*3),Image.Resampling.BILINEAR)
        output=native.with_name(f"frame_{int(f['frame_order'])+1:02d}_roi_enlarged.png");enlarged.save(output)
        f.update(roi_image=str(output.relative_to(run)),roi_pixels_image=str(native.relative_to(run)),roi_image_sha256=digest(output),
            roi_pixels_sha256=digest(native),roi_left=box[0],roi_top=box[1],roi_right=box[2],roi_bottom=box[3])
    write_csv(run/'FRAME_MANIFEST.csv',frames)
    flat_cuts=[{**{k:v for k,v in c.items() if k!='parameters'},**c['parameters']} for c in cuts]
    write_csv(run/'CUT_MANIFEST.csv',flat_cuts)
    pair_rows=[{**{k:v for k,v in p.items() if k!='matching_parameters'},**p['matching_parameters']} for p in pairs]
    write_csv(run/'PAIR_MANIFEST.csv',pair_rows)
    write_csv(run/'REVIEW_TEMPLATE.csv',[{'cut_id':c['cut_id'],'pair_id':c['pair_id'],'interval_id':c['interval_id'],
        'native_label':c['native_label'],'reviewer':'','reviewed_utc':'','context_visibility_clear_partial_none_uncertain':'',
        'tool_contact_visibility_clear_partial_none_uncertain':'','visually_distinguishable_from_mate_yes_no_uncertain':'',
        'occlusion_none_mild_moderate_severe':'','crop_covers_relevant_region_yes_no_uncertain':'','comments':''} for c in cuts])
    features=pd.read_csv(COHORT/'manifests/common_mtc_statistics.csv')
    features.loc[features.interval_id.isin([c['interval_id'] for c in cuts])].to_csv(run/'SENSOR_STATISTICS_90.csv',index=False)
    sheets={}
    for cut in cuts:
        fs=sorted([r for r in frames if r['cut_id']==cut['cut_id']],key=lambda r:r['frame_order'])
        sheets[cut['cut_id']]={kind:contact_sheet(run,cut,fs,kind) for kind in ('full','roi')}
    previews=[pair_preview(run,p,cuts,frames) for p in pairs]
    # Scientific PDF uses standard plotting; all 160 source frames appear once in
    # each view: 10 full-view pages + 10 ROI pages, plus guide and parameter pages.
    with PdfPages(run/'MATCHED_CUT_REVIEW.pdf') as pdf:
        fig=plt.figure(figsize=(11.7,16.5));fig.text(.07,.94,'MSM — matched cutting review',fontsize=25,weight='bold')
        intro='''Five normal cuts (native 0) and five abnormal cuts (native 1).
Five same-experiment pairs: three VM20i, two VMX30Ui.
16 previously audited frames per cut = 160 unique source frames.

Every pair matches N, ap, ae, F, Z, D, tool category and material.
IMPORTANT: direction differs in every pair: normal DOWN / abnormal UP.
These examples cannot isolate the causal effect of anomaly from direction.

For each cut, one page shows all 16 full camera views; the next shows
the same frames as enlarged context crops. Follow timestamps and source
row identity; the original half-open sensor interval determines the label.
Uncertainty guards and full-laboratory eligibility remain unchanged.

ROI rectangles are fixed within each pair and include approximate tool/
workpiece context. They are NOT anomaly boxes. Coolant and droplets
can hide contact. Cropping/enlargement adds no hidden information.
No enhancement, deblurring, generated image content or model was used.

Use VIEWER.html to step synchronously through all 16 relative positions,
inspect full-resolution images and export qualitative notes.
Fill REVIEW_TEMPLATE.csv if you prefer a spreadsheet.

These are selected diagnostic examples, not a representative efficacy test.
Visible anomaly observability remains unverified until human review.
The saved native labels were not inferred from the images.

Dataset: manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2
Source cohort: 20261027T015205931708Z-stage5-full-lab-validated.
'''
        fig.text(.07,.87,intro,fontsize=14,va='top',linespacing=1.7);pdf.savefig(fig);plt.close(fig)
        fig=plt.figure(figsize=(11.7,16.5));fig.text(.06,.96,'Pair identities and exact native settings',fontsize=22,weight='bold')
        y=.91
        for p in pairs:
            n=next(c for c in cuts if c['cut_id']==p['normal']);a=next(c for c in cuts if c['cut_id']==p['abnormal']);s=p['matching_parameters']
            text=f"{p['pair_id']}  {p['group_id']}\nNormal row {n['source_row']}: [{n['start_s']:.3f}, {n['end_s']:.3f}) s; DOWN\nAbnormal row {a['source_row']}: [{a['start_s']:.3f}, {a['end_s']:.3f}) s; UP\nN={s['N']} rpm; ap={s['ap']} mm; ae={s['ae']} mm; F={s['F']} mm/s\nZ={s['Z']}; D={s['D']} mm; Tool={s['Tool']}; material={s['Workpiece']}"
            fig.text(.06,y,text,fontsize=13,va='top',linespacing=1.5);y-=.17
        pdf.savefig(fig);plt.close(fig)
        for cut in cuts:
            for kind in ('full','roi'):
                im=Image.open(sheets[cut['cut_id']][kind]);fig=plt.figure(figsize=(11.7,16.5));ax=fig.add_axes([.015,.015,.97,.97]);ax.imshow(im);ax.axis('off');pdf.savefig(fig,dpi=150);plt.close(fig)
    write_viewer(run,pairs,cuts,frames)
    parameters='| Pair | Experiment | Normal row | Abnormal row | N rpm | ap mm | ae mm | F mm/s | Tool / material |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for p in pairs:
        n=next(c for c in cuts if c['cut_id']==p['normal']);a=next(c for c in cuts if c['cut_id']==p['abnormal']);s=p['matching_parameters']
        parameters+=f"| {p['pair_id']} | {p['group_id']} | {n['source_row']} | {a['source_row']} | {s['N']} | {s['ap']} | {s['ae']} | {s['F']} | {s['Tool']} / {s['Workpiece']} |\n"
    readme=f'''# Ten real MSM cutting examples — five matched pairs

Open [VIEWER.html](VIEWER.html) in a browser for synchronized frame stepping, full camera views and enlarged cutting-context crops. The viewer needs no server or internet. Keep the `frames/` and `figures/` folders beside it. Use [MATCHED_CUT_REVIEW.pdf](MATCHED_CUT_REVIEW.pdf) for the complete printable 22-page set.

**Exactly 10 cuts / 160 unique source frames: five label 0, five label 1.** Three pairs come from VM20i and two from VMX30Ui. Every pair is from one experiment; numerical settings and native tool/material descriptions match exactly. **All five pairs differ in native direction: normal DOWN, abnormal UP.** This is a real confound, not an exact all-factor match. No within-experiment complete match including direction was available in the eligible mixed-label pool. This is a descriptive inspection package, not a causal comparison, representative evaluation sample or new ground truth.

{parameters}
All parameter values are copied from the original `label.csv`. N is spindle speed, ap axial depth, ae radial depth, F feed rate, Z teeth and D tool diameter. Units follow the [publication's annotation schema](https://www.nature.com/articles/s41597-026-07255-7). Native Tool strings are categories, not verified unique physical tool IDs.

## Examine the examples

1. Open the viewer and choose P01–P05. Normal is on the left, abnormal on the right.
2. Step through frames 1–16 with the slider, buttons or arrow keys. The two cuts share relative within-cut frame position, not simultaneous physical time. Read each actual video/sensor timestamp.
3. Compare the full camera view with the orange fixed ROI and its enlarged crop. The same rectangle is used for both cuts in a pair and for every frame.
4. Review context visibility, tool/workpiece contact, occlusion and whether any visible distinction survives the direction difference. Use “uncertain” when appropriate. Do not infer a visible defect solely from the label.
5. Record notes in the viewer and download JSON, or fill [REVIEW_TEMPLATE.csv](REVIEW_TEMPLATE.csv). Browser notes are not persisted automatically.

Several images are heavily obscured by coolant/window droplets. They are retained because cuts were chosen by metadata, not by apparent class separability or clear views. ROIs are approximate tool/workpiece-context rectangles, not expert cutting-contact or anomaly localizations. Crops are literal pixel slices from the SAR-corrected full view, with a separate lossless unscaled crop and a threefold bilinear display enlargement. No contrast change, sharpening, deblurring, generated image content or model inference is used. Enlargement does not recover occluded detail.

Full display frames are 270×480, corrected from the delivered video's 720×480 coded pixels and 3:8 sample aspect ratio. Original source MP4 filenames/hashes remain in the manifest; raw media were not changed or copied into this review package. Exactly 160 source frames are represented as multiple views; full/crop copies do not create extra prediction examples.

## Files

- `VIEWER.html`: offline interactive comparison, actual timestamps and optional qualitative notes export.
- `MATCHED_CUT_REVIEW.pdf`: guide, parameter table and all 10 full-camera + 10 ROI contact sheets.
- `figures/P01_comparison.jpg` through `P05_comparison.jpg`: representative frame-08 pair previews.
- `figures/*_full_16frames.jpg` and `*_roi_16frames.jpg`: all 160 frames in each view.
- `frames/`: clean full images, lossless literal crops and enlarged display crops for all 160 frame identities.
- `CUT_MANIFEST.csv`, `PAIR_MANIFEST.csv`, `FRAME_MANIFEST.csv`: source identities, labels, settings, time mapping, frame order and hashes.
- `SENSOR_STATISTICS_90.csv`: previously verified 90-feature vectors for these ten matching sensor intervals; no new classifier.
- `REVIEW_TEMPLATE.csv`: qualitative review form. `config/roi_config.json`: fixed crop coordinates and rationale.

The native label applies to the whole annotated cut. It is not a frame-level defect annotation. All selected examples already passed the full-laboratory timing/16-frame/common-MTC gates. Exact source pixels and presentation times were checked against the saved frame manifest; frame uncertainty stays inside the native half-open interval. VMX30Ui/dataset9 retains the corrected +49.73 s mapping.

Version: `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`. Authoritative cohort: `{COHORT}`. No download, training, CNN extraction, F2 evaluation or interaction with the Phase 1 job occurred. Previous reports/results and the tracked dirty working tree remain unchanged.
'''
    with (run/'README.md').open('x') as f:f.write(readme)
    # All frame derivatives are checked before packaging; no additional raw decode.
    assert len(frames)==160 and len(cuts)==10 and len(pairs)==5
    assert sum(c['native_label']==0 for c in cuts)==sum(c['native_label']==1 for c in cuts)==5
    assert len({(f['group_id'],int(f['native_frame_index'])) for f in frames})==160
    for c in cuts:
        fs=sorted([f for f in frames if f['cut_id']==c['cut_id']],key=lambda f:f['frame_order'])
        assert [int(f['frame_order']) for f in fs]==list(range(16))
        assert len({f['decoded_frame_sha256'] for f in fs})==16 and np.all(np.diff([f['video_pts_s'] for f in fs])>0)
        for f in fs:
            assert digest(run/f['full_image'])==f['full_image_sha256']
            assert np.array_equal(np.asarray(Image.open(run/f['roi_pixels_image'])),np.asarray(Image.open(run/f['full_image']))[f['roi_top']:f['roi_bottom'],f['roi_left']:f['roi_right']])
    from pypdf import PdfReader
    assert len(PdfReader(run/'MATCHED_CUT_REVIEW.pdf').pages)==22
    write_json(run/'validation.json',{'source_cuts':10,'normal':5,'abnormal':5,'same_experiment_pairs':5,
        'verified_native_frames':160,'unique_source_frame_identities':160,'ordered_distinct_frames_per_cut':16,
        'literal_roi_pixel_parity':True,'same_roi_per_pair':True,'native_parameters_exactly_matched':True,
        'direction_matches':0,'pdf_pages':22,'independent_visibility_review':'pending','new_training':False,'passed':True})
    write_json(run/'provenance.json',{'utc':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':sys.argv,'python':platform.python_version(),'software':{p:importlib.metadata.version(p) for p in ['numpy','pandas','Pillow','matplotlib','opencv-python','pypdf']},
        'source_files':[{'path':str(p),'sha256':digest(p)} for p in [Path(__file__),Path(__file__).with_name('prepare_matched_visual_review.py')]],
        'new_raw_downloads':0,'gpu_work':False,'model_training':False,'review_selection':'metadata-matched diagnostics; direction-confounded, not population-representative',
        'portable_render_font':'DejaVu Sans (presentation only; not a dataset path)',
        'incomplete_extraction_note':'Earlier preserved run stopped at a legacy pilot geometry-schema lookup; fresh run uses verified media_probe geometry for that pilot. No source/frame mismatch.'})
    # Archive is portable: relative images/data and offline HTML remain together.
    members=[p for p in sorted(run.rglob('*')) if p.is_file() and p.name!='MSM_MATCHED_CUT_REVIEW.zip']
    with zipfile.ZipFile(run/'MSM_MATCHED_CUT_REVIEW.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in members:z.write(p,p.relative_to(run))
    with zipfile.ZipFile(run/'MSM_MATCHED_CUT_REVIEW.zip') as z:assert z.testzip() is None
    manifest=[{'path':str(p.relative_to(run)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(run.rglob('*')) if p.is_file()]
    write_json(run/'manifests/output_manifest.json',{'self_excluded':True,'files':manifest})
    # Append a separate navigation folder without editing the sealed Stage 5 index.
    findings=Path('MILLING DATASET/PILOT_FINDINGS/06_MATCHED_CUT_REVIEW');findings.mkdir(exist_ok=False)
    rel=os.path.relpath(run,findings)
    with (findings/'README.md').open('x') as f:f.write(f'# Five matched milling pairs\n\nExactly ten real cuts and 160 native frames.\n\n- [Offline viewer]({rel}/VIEWER.html)\n- [Printable 22-page PDF]({rel}/MATCHED_CUT_REVIEW.pdf)\n- [Complete portable ZIP]({rel}/MSM_MATCHED_CUT_REVIEW.zip)\n- [Selection, usage and limits]({rel}/README.md)\n\nEvery pair matches numerical settings within its experiment. **Normal DOWN versus abnormal UP in all pairs is a confound.** Crops are literal tool/workpiece-context views; contact/anomaly observability remains unverified.\n')
    write_json(findings/'PROVENANCE.json',{'authoritative_run':str(run),'output_manifest':str(run/'manifests/output_manifest.json'),
        'output_manifest_sha256':digest(run/'manifests/output_manifest.json'),'existing_stage5_artifacts_unchanged':True})
    print(json.dumps({'run':str(run),'zip_bytes':(run/'MSM_MATCHED_CUT_REVIEW.zip').stat().st_size,
        'pdf_bytes':(run/'MATCHED_CUT_REVIEW.pdf').stat().st_size,'source_frames':160,'pdf_pages':22,'passed':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);build(p.parse_args().run)
