"""Static source checks only. Does not replace XeLaTeX/Biber or PDF inspection."""
from pathlib import Path
from collections import Counter
import re,json,csv,hashlib,shutil
R=Path.cwd();B=R/'00_thesis_writing_tracking/Thesis/LaTeX_Project';O=R/'00_thesis_writing_tracking/empirical_revision_20261127_01'
files=set();missing=[]
def clean(s):
 s=re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}','',s,flags=re.S)
 return re.sub(r'(?<!\\)%[^\n]*','',s)
def visit(p):
 if p in files:return
 files.add(p);s=clean(p.read_text())
 for kind,target in re.findall(r'\\(input|include|includegraphics|addbibresource)(?:\[[^\]]*\])?\{([^{}]+)\}',s):
  if '\\' in target or '#' in target:continue
  options=[B/target]
  if not Path(target).suffix:options += [B/(target+e) for e in (['.pdf','.png','.jpg','.jpeg'] if kind=='includegraphics' else ['.tex'])]
  found=next((q for q in options if q.is_file()),None)
  if found is None:missing.append({'file':str(p.relative_to(B)),'target':target})
  elif kind in ['input','include']:visit(found)
visit(B/'main.tex')
text='\n'.join(clean(p.read_text()) for p in files)
labels=re.findall(r'\\label\{([^}]+)\}',text);refs=re.findall(r'\\(?:ref|pageref|autoref|eqref)\{([^}]+)\}',text)
ids=set(re.findall(r'\\EvidenceFile\{(E\d+)\}',text));uses=re.findall(r'\\EvidenceRef(?:\[[^]]*\])?\{(E\d+)\}',text)
keys=set()
for p in B.glob('*.bib'):keys.update(re.findall(r'@\w+\s*\{\s*([^,]+),',p.read_text()))
cites=[]
for group in re.findall(r'\\(?:[a-zA-Z]*cite[a-zA-Z]*)(?:\[[^]]*\])*\{([^}]+)\}',text):cites.extend(x.strip() for x in group.split(','))
envs=[];braces=[]
for p in files:
 if p.name in ['evidence_links.tex','thesis-formatting.tex','main.tex','review-settings.tex']:continue # macros/conditional environments intentionally split
 s=clean(p.read_text());stack=[]
 for typ,name in re.findall(r'\\(begin|end)\{([^}]+)\}',s):
  if typ=='begin':stack.append(name)
  elif not stack or stack.pop()!=name:envs.append(str(p.relative_to(B)))
 if stack:envs.append(str(p.relative_to(B)))
 depth=0
 for m in re.finditer(r'(?<!\\)[{}]',s):
  depth+=1 if m[0]=='{' else -1
  if depth<0:break
 if depth!=0:braces.append({'file':str(p.relative_to(B)),'balance':depth})
index=list(csv.DictReader((B/'tables/evidence_source_index.csv').open()));new=[]
for row in index:
 if int(row['file_id'][1:])>=134:
  p=R/row['current_repository_path'];new.append({'id':row['file_id'],'exists':p.is_file(),'hash_match':p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row['current_sha256']})
result={'scope':'Static main.tex dependency closure; no TeX expansion, typesetting or rendered checks. Macro definitions excluded from simple balance check.','active_tex_files':len(files),'labels':len(labels),'evidence_ids':len(ids),'missing_inputs':missing,'duplicate_labels':[k for k,v in Counter(labels).items() if v>1],'undefined_refs':sorted(set(refs)-set(labels)),'undefined_evidence':sorted(set(uses)-ids),'undefined_citations':sorted(set(cites)-keys),'environment_errors':envs,'brace_errors':braces,'new_evidence_paths':new,'toolchain':{x:shutil.which(x) for x in ['latexmk','xelatex','biber','pdftoppm']}}
(O/'static_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
