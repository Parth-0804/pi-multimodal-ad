"""Build a portable blinded review UI from public blank sheets only."""
import argparse,csv,hashlib,json,shutil,subprocess,zipfile
from datetime import datetime,timezone
from pathlib import Path
import cv2

def identity(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return {'name':p.name,'bytes':p.stat().st_size,'sha256':h.hexdigest()}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 source=args.source;out=args.output;out.mkdir(parents=True,exist_ok=False)
 cv2.setNumThreads(1);(out/'clips').mkdir();(out/'originals').mkdir();(out/'source').mkdir()
 template=Path(__file__).with_name('review.html').read_text();sheets={};inputs=[];copies=[]
 for reviewer in ['A','B']:
  p=source/f'reviewer_{reviewer}_blank.csv';inputs.append((p,identity(p)))
  with p.open(newline='') as f:rows=list(csv.DictReader(f))
  assert len(rows)==64 and len({r['review_id'] for r in rows})==64
  for r in rows:
   assert all(not r[c] for c in ['judged_outcome','boundary_quality','visibility','artifact_flag','short_reason'])
   assert r['clip_file']==r['review_id']+'.mp4' and Path(r['clip_file']).name==r['clip_file']
  sheets[reviewer]=rows
  payload={'package_id':'reassemble-20260928T032231Z-review-ui-v1','reviewer':reviewer,'rows':rows}
  (out/f'review_{reviewer}.html').write_text(template.replace('__DATA__',json.dumps(payload).replace('<','\\u003c')))
 assert {r['review_id'] for r in sheets['A']}=={r['review_id'] for r in sheets['B']}
 for i,row in enumerate(sheets['A']):
  p=source/'clips'/row['clip_file'];inputs.append((p,identity(p)));shutil.copyfile(p,out/'originals'/p.name)
  cap=cv2.VideoCapture(str(p));assert cap.isOpened();fps=cap.get(cv2.CAP_PROP_FPS);n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  dest=out/'clips'/(row['review_id']+'.webm');writer=cv2.VideoWriter(str(dest),cv2.VideoWriter_fourcc(*'VP80'),fps,(w,h));assert writer.isOpened();count=0
  while True:
   ok,frame=cap.read()
   if not ok:break
   writer.write(frame);count+=1
  cap.release();writer.release();assert count==n
  check=cv2.VideoCapture(str(dest));decoded=0
  while check.read()[0]:decoded+=1
  outfps=check.get(cv2.CAP_PROP_FPS);check.release();assert decoded==n and abs(outfps-fps)<0.02
  copies.append({'review_id':row['review_id'],'frames':n,'source_fps':fps,'playback_fps':outfps,'source':identity(p),'webm':identity(dest)})
  print('PLAYBACK_COPY',i+1,64,flush=True)
 for p in [Path(__file__),Path(__file__).with_name('review.html')]:shutil.copyfile(p,out/'source'/p.name)
 p=source/'REVIEWER_INSTRUCTIONS.md';inputs.append((p,identity(p)));shutil.copyfile(p,out/p.name)
 assert all(identity(p)==before for p,before in inputs)
 (out/'START_HERE.md').write_text('''# Human review — quick start

1. Download and extract the entire ZIP; keep its folders together.
2. Open `review_A.html` in Chrome, Edge, or Firefox. No server or installation is needed.
3. Watch a clip, select four ratings, write a short reason, and choose Next.
4. Use “Download progress backup” when taking a break. Restore it if changing browser/device.
5. When all 64 clips are complete, download the completed CSV and return it to the thesis author.

A second reviewer can use `review_B.html` independently, preferably on their own device. The sheets preserve their original independent orders. Do not share answers before completing reviews. All ratings start blank. One actual reviewer is accepted; never invent another reviewer.

Browser storage is best effort, especially for local files or private browsing. Keep downloaded backups. No ratings are sent to a server. The completed CSV preserves the existing ingestion schema; downloading does not submit or adjudicate it.

Original silent MP4s are retained in `originals/`. Additional VP8/WebM copies support browser playback, using all decoded frames at the original resolution/cadence. Additional lossy encoding may soften details; originals remain available beside playback. No labels, scores, private key, or source recording identities were accessed or packaged. No extra context, audio, model predictions, or suggested ratings are provided. Read REVIEWER_INSTRUCTIONS.md for interpretation limits.
''')
 manifest={'UTC':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'opencv_version':cv2.__version__,'human_ratings':'NONE_GENERATED','input_preservation_passed':True,'source_directory':str(source),'inputs':[x for _,x in inputs],'copies':copies,'files':[{'path':str(p.relative_to(out)),**identity(p)} for p in sorted(out.rglob('*')) if p.is_file()]}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(out.with_suffix('.zip'),'x',compression=zipfile.ZIP_STORED) as z:
  for p in sorted(out.rglob('*')):
   if p.is_file():z.write(p,Path(out.name)/p.relative_to(out))
 print('PACKAGE',out,'ZIP_BYTES',out.with_suffix('.zip').stat().st_size,flush=True)
if __name__=='__main__':main()
