"""Refresh review receipts against preserved working-copy baselines; never edits thesis sources."""
from pathlib import Path
import csv,difflib,hashlib,json,re,subprocess
from datetime import datetime,timezone
R=Path.cwd();B=R/'00_thesis_writing_tracking/Thesis/LaTeX_Project';O=R/'00_thesis_writing_tracking/empirical_revision_20261127_01'
m=json.loads((O/'baseline_manifest.json').read_text()); patches=[];stats=[];unchanged=[]
def baseline(rel):
 q=O/'baseline_extra'/rel
 return q if q.is_file() else O/'baseline'/Path(rel).relative_to(B.relative_to(R))
for rel,record in m.items():
 before=baseline(rel);assert before.is_file(),rel
 assert hashlib.sha256(before.read_bytes()).hexdigest()==record['sha256'],rel
 old=before.read_text().splitlines(keepends=True);new=(R/rel).read_text().splitlines(keepends=True)
 patch=list(difflib.unified_diff(old,new,fromfile='baseline/'+rel,tofile=rel))
 if patch:
  patches.extend(patch);stats.append([rel,sum(x.startswith('+') and not x.startswith('+++') for x in patch),sum(x.startswith('-') and not x.startswith('---') for x in patch)])
 else:unchanged.append(rel)
(O/'revision_only.diff').write_text(''.join(patches));(O/'revision_only_stat.json').write_text(json.dumps(stats,indent=2)+'\n')
idxrel=str((B/'tables/evidence_source_index.csv').relative_to(R))
a=list(csv.DictReader(baseline(idxrel).open()));b=list(csv.DictReader((R/idxrel).open()));assert b[:len(a)]==a
sections={}
for file,count in [('05_phm.tex',7),('06_reassemble.tex',8),('07_msm.tex',8),('08_vifailback.tex',6)]:
 s=(B/'chapters'/file).read_text(); sections[file]=len(re.findall(r'\\section\{',s));assert sections[file]==count
source_errors=[]
for rel,item in json.loads((O/'source_manifest.json').read_text()).items():
 p=R/rel
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:source_errors.append(rel)
assert not source_errors
mds=[O/'VERIFICATION.md',B/'README.md',R/'docs/THESIS_CODE_MAP.md'];link_checks=[]
for p in mds:
 def missing(s):
  result=[]
  for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s):
   target=target.strip('<>').split('#',1)[0]
   if not target or re.match(r'\w+://',target):continue
   if not (p.parent/target).exists() and (p.parent/target).resolve() != (O/'final_integrity_checks.json').resolve():result.append(target)
  return sorted(set(result))
 now=missing(p.read_text());rel=str(p.relative_to(R));previous=missing(baseline(rel).read_text()) if rel in m else []
 added=sorted(set(now)-set(previous));link_checks.append({'path':rel,'missing_links':now,'new_missing_links':added});assert not added,(rel,added)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head==(O/'initial_head.txt').read_text().strip()
receipts={}
for key,args in [('git_diff_check',['git','diff','--check']),('git_diff_check_crlf',['git','-c','core.whitespace=cr-at-eol','diff','--check']),('git_diff_stat',['git','diff','--stat']),('git_status',['git','status','--short','--branch','--untracked-files=all'])]:
 proc=subprocess.run(args,text=True,capture_output=True);(O/(key+'.txt')).write_text(proc.stdout+proc.stderr);receipts[key]={'exit_code':proc.returncode,'lines':len((proc.stdout+proc.stderr).splitlines())}
(O/'git_check_results.json').write_text(json.dumps(receipts,indent=2)+'\n');assert receipts['git_diff_check_crlf']['exit_code']==0
result={'checked_utc':datetime.now(timezone.utc).isoformat(),'head':head,'baseline_files_hash_verified':len(m),'existing_files_changed_by_this_revision':len(stats),'unchanged_baseline_files':unchanged,'original_evidence_rows_preserved':len(a),'new_evidence_rows':len(b)-len(a),'section_counts':sections,'source_hash_errors':source_errors,'markdown_navigation':link_checks,'git_checks':receipts,'scope':'Static/source integrity and task diff only; no typesetting, new training or experimental rerun.'}
(O/'final_integrity_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
