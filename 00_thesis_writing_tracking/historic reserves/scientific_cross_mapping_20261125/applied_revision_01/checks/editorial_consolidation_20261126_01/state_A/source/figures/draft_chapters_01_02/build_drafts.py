#!/usr/bin/env python3
"""Build this draft review set from the thesis root; no manuscript edits or fitting.
Uses an existing XeLaTeX/Biber/Poppler installation on PATH. --run-dir must be new.
"""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json,re,shutil,subprocess,datetime,sys
D=Path(__file__).resolve().parent
B=D.parents[1]
R=next(q for q in B.parents if (q/'pyproject.toml').is_file())
L=R/'00_thesis_writing_tracking/Thesis/References/literature_review'
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def load(q):return json.loads(q.read_text())
def source_state():
 return {str(q.relative_to(B)):sha(q) for q in B.rglob('*') if q.is_file() and not q.is_relative_to(D) and 'build' not in q.relative_to(B).parts}
def run(args,log):
 with log.open('w') as f:subprocess.run(args,cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True)
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--run-dir',type=Path,required=True);args=a.parse_args()
 out=(B/args.run_dir).resolve();assert out.is_relative_to(B/'build/figures')
 out.mkdir(parents=True,exist_ok=False);before=source_state()
 with (L/'historical/candidate_screening.csv').open(newline='') as f:screen=list(csv.DictReader(f))
 decisions=Counter(row['Decision'] for row in screen);assert decisions=={'INCLUDE':39,'EXCLUDE':37,'MAYBE':44},decisions
 history=load(L/'historical/evidence.json');labels=Counter(row['label'] for row in history.values());assert labels=={'F':37,'A':2},labels
 expansion=load(L/'normalized_expansion_appraisals.json')['papers'];matrix=load(L/'expanded_comparison_matrix.json');counts=load(L/'review_counts.json')
 initial=[r for r in matrix if r['work_id'].startswith('F')];later=[r for r in matrix if r['work_id'].startswith('P')]
 assert len(screen)==120 and len(matrix)==94 and len(initial)==37 and len(later)==len(expansion)==57
 assert len({r['work_id'] for r in matrix})==len({r['citation_key'] for r in matrix})==94
 assert {r['citation_key'] for r in initial}=={r['citation_key'] for r in history.values() if r['label']=='F'}
 aliases=load(L/'citation_key_aliases.json')
 assert {r['citation_key'] for r in later}=={aliases[r['file_id']] for r in expansion}
 norm=lambda s:re.sub(r'\W','',str(s).lower())
 for field in ['DOI','title']:
  assert not ({norm(r[field]) for r in initial if r.get(field)}&{norm(r[field]) for r in later if r.get(field)})
 assert counts['new_input_files']==59 and counts['new_distinct_PDFs']==57 and counts['expanded_unique_appraised_works']==94
 app2=load(L/'appraisal_P021_P040.json');app3=load(L/'appraisal_P041_P059.json')
 pair1=next(r for r in app2['duplication'] if r['file_id']=='P039');base1=next(r for r in app2['papers'] if r['file_id']=='P038')
 assert pair1['duplicate_of']=='P038' and base1['pdf_sha256'] in pair1['reason']
 pair2=next(r for r in app3['papers'] if r['file_id']=='P047');base2=next(r for r in app3['papers'] if r['file_id']=='P046')
 assert pair2['duplicate_of']=='P046' and pair2['pdf_sha256']==base2['pdf_sha256']

 abstract_only={k:v['citation_key'] for k,v in history.items() if v['label']=='A'};assert abstract_only=={'19':'Zhang2026A','36':'Liu2024Advancing'},abstract_only
 macros=(B/'tables/review_counts.tex').read_text();assert r'\newcommand{\ReviewWorkCount}{94}' in macros and r'\newcommand{\ExpandedPDFCount}{57}' in macros
 # Preserve the original count and document the separately added methodological reference.
 assert 'Ting1999Issues' in (B/'references_additions.bib').read_text()
 content=''.join((D/n).read_text() for n in ['draft_captions.tex','draft_review.tex'])
 keys={k.strip() for c in re.findall(r'\\cite\w*(?:\[[^\]]*\]){0,2}\{([^}]+)\}',content) for k in c.split(',')}
 bibkeys=set(re.findall(r'@\w+\{([^,]+),','\n'.join(q.read_text() for q in B.glob('*.bib'))));assert keys<=bibkeys,keys-bibkeys
 values={'ScreenedCount':len(screen),'IncludedCount':decisions['INCLUDE'],'ExcludedCount':decisions['EXCLUDE'],'MaybeCount':decisions['MAYBE'],'InitialCount':len(initial),'AbstractOnlyCount':labels['A'],'InputPDFCount':counts['new_input_files'],'ExpansionCount':len(later),'TotalWorkCount':len(matrix)}
 (D/'corpus_counts.tex').write_text('% Generated from existing corpus records by build_drafts.py.\n'+''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in values.items()))
 details={}
 for name in ['fig01_research_framework','fig02_literature_gap_map','fig03_literature_appraisal_flow','tab01_requirements_traceability_preview','draft_review']:
  src=D/(name+'.tex');cmd=['latexmk','-xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir='+str(out),str(src.relative_to(B))]
  run(cmd,out/(name+'_console.txt'))
  log=(out/(name+'.log')).read_text(errors='replace');bad=[s for s in log.splitlines() if re.search(r'undefined|multiply defined|Overfull|Missing character|^!',s,re.I)]
  if bad:raise RuntimeError((name,bad))
  blg=out/(name+'.blg')
  if blg.exists():assert not re.search(r'WARN|ERROR',blg.read_text()),name
  pdf=out/(name+'.pdf');shutil.copy2(pdf,D/pdf.name)
  info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);n=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]);(out/(name+'_pdfinfo.txt')).write_text(info)
  if name!='draft_review':assert n==1,(name,n)
  else:assert n==4,n
  fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True);(out/(name+'_fonts.txt')).write_text(fonts)
  assert all(re.search(r'\s+yes\s+yes\s+(yes|no)\s+\d+\s+\d+\s*$',line) for line in fonts.splitlines()[2:]),fonts
  # Individual diagrams at 150 dpi; packet previews include captions and notes.
  if n==1:
   subprocess.run(['pdftoppm','-r','150','-png','-singlefile',str(pdf),str(out/name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   shutil.copy2(out/(name+'.png'),D/(name+'.png'))
  else:
   subprocess.run(['pdftoppm','-r','150','-png',str(pdf),str(out/name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   for q in out.glob(name+'-*.png'):shutil.copy2(q,D/q.name)
  subprocess.run(['pdftotext','-layout',str(pdf),str(out/(name+'.txt'))],check=True)
  details[name]={'pages':n,'pdf_sha256':sha(pdf),'fonts_embedded':True,'compile_command':cmd}
 assert before==source_state(),'Source outside draft/build directories changed during generation'
 record={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Draft figures only; no manuscript edits, model operations, new literature search or environment changes.','counts':values,'abstract_only_inclusions':abstract_only,'source_hashes':{str(q.relative_to(R)):sha(q) for q in [L/'historical/candidate_screening.csv',L/'historical/evidence.json',L/'normalized_expansion_appraisals.json',L/'expanded_comparison_matrix.json',L/'review_counts.json',L/'citation_key_aliases.json',L/'appraisal_P021_P040.json',L/'appraisal_P041_P059.json',B/'chapters/01_introduction.tex',B/'chapters/02_literature_review.tex',B/'chapters/03_foundations.tex',B/'chapters/04_methodology.tex',B/'appendices/A_literature.tex',B/'figures/VISUAL_STYLE.md',B/'figures/tikz_style.tex']},'existing_project_files_unchanged':before,'builds':details,'visual_inspection':'Required after opening generated previews; not certified by this script.'}
 (out/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'run_dir':str(out.relative_to(B)),'counts':values,'builds':{k:v['pages'] for k,v in details.items()}},indent=2))
if __name__=='__main__':main()
