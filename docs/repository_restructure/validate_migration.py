from pathlib import Path
import json,csv,hashlib,os,tarfile,ast,re,subprocess,datetime
out=Path('docs/repository_restructure');rows=list(csv.DictReader((out/'path_mapping.csv').open()))
protected=json.loads((out/'baseline/protected_files.json').read_text());changes=[]
for row in protected:
 p=Path(row['path'])
 try:
  st=p.lstat()
  if st.st_size!=row['bytes'] or st.st_mtime_ns!=row['mtime_ns']:changes.append({'path':str(p),'reason':'stat changed'})
  if 'sha256' in row and hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:changes.append({'path':str(p),'reason':'hash changed'})
 except FileNotFoundError:changes.append({'path':str(p),'reason':'missing'})
current=set()
for root in ['runs','artifacts','experiments','archive','data','gtc-data-experiment']:
 for parent,dirs,files in os.walk(root,followlinks=False):current.update(str(Path(parent)/name) for name in files)
added=sorted(current-{r['path'] for r in protected})
preservation={'checked_files':len(protected),'small_evidence_hashes':sum('sha256' in r for r in protected),'changes':changes,'added_files':added,'scope':'lstat identity for all listed protected files; SHA256 for small evidence text; no bulk raw payload hashing'}
(out/'preservation_check.json').write_text(json.dumps(preservation,indent=2));print('preservation',preservation['checked_files'],'changes',len(changes),'new files',len(added))
# Check all pre-existing source/script/test/config identities against the explicit map.
identities=json.loads((out/'baseline/source_identities.json').read_text());mapping={r['old_path']:r['new_path'] for r in rows};changed=[]
for old,h in identities.items():
 new=mapping.get(old,old);p=Path(new)
 if not p.exists():changed.append({'old':old,'new':new,'status':'MISSING'})
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append({'old':old,'new':new,'status':'edited'})
(out/'source_changes.json').write_text(json.dumps(changed,indent=2))
# Compare ASTs to baseline preimages, permitting classified path/import and bootstrap changes only.
pathmap={r['old_path']:r['new_path'] for r in rows if r['old_path']!=r['new_path']}
modulemap={a[4:-3].replace('/','.').removesuffix('.__init__'):b[4:-3].replace('/','.').removesuffix('.__init__') for a,b in pathmap.items() if a.startswith('src/') and a.endswith('.py')}
patterns={**pathmap,**modulemap}
pattern=re.compile('|'.join(re.escape(s) for s in sorted(patterns,key=len,reverse=True)))
def normtext(s):
 s=pattern.sub(lambda m:patterns[m.group()],s)
 return s.replace('pi_multimodal_ad','phm2026')
class Normalizer(ast.NodeTransformer):
 def visit_Import(self,node):return None
 def visit_ImportFrom(self,node):return None
 def visit_Constant(self,node):
  if isinstance(node.value,str):node.value=normtext(node.value)
  return node
 def visit_Expr(self,node):
  # Only the newly added entry-point source-root bootstrap has these aliases.
  if isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='_sys.path.insert':return None
  return self.generic_visit(node)
 def visit_Subscript(self,node):
  if ast.unparse(node.value)=='Path(__file__).resolve().parents':node.slice=ast.Constant(value='REPOSITORY_ROOT_DEPTH')
  return self.generic_visit(node)
results=[]
with tarfile.open('docs/repository_restructure/baseline/source_preimages.tar.gz') as tar:
 for item in changed:
  old,new=item['old'],item['new']
  if not old.endswith('.py'):continue
  before=tar.extractfile(old).read().decode();after=Path(new).read_text()
  a=ast.dump(Normalizer().visit(ast.parse(before)),include_attributes=False);b=ast.dump(Normalizer().visit(ast.parse(after)),include_attributes=False)
  results.append({'old':old,'new':new,'equivalent_except_imports_paths_bootstrap':a==b})
(out/'ast_equivalence.json').write_text(json.dumps(results,indent=2));print('AST comparisons',len(results),'unexplained',sum(not x['equivalent_except_imports_paths_bootstrap'] for x in results))
for x in results:
 if not x['equivalent_except_imports_paths_bootstrap']:print('AST REVIEW',x['new'])
# Full bounded text reference audit: no environment, credentials, sessions, caches or binary payload reads.
refs=[];excluded=[];suffixes={'.py','.md','.rst','.txt','.yaml','.yml','.json','.toml','.cfg','.ini','.sh','.ipynb','.csv'}
needles=re.compile(r'pi_multimodal_ad|src/pi_multimodal_ad|scripts/(?:features|targets|training|dataset|results)|tests/unit')
for parent,dirs,files in os.walk('.',followlinks=False):
 dirs[:]=[d for d in dirs if not d.startswith('.') and d not in ['ma_thesis_env','__pycache__','node_modules','gtc-data-experiment','data','venv','env']]
 for name in files:
  p=Path(parent)/name;s=str(p)
  if p.suffix not in suffixes or any(x in name.lower() for x in ['cookie','credential','private_key','session','token']) or name.startswith('.env'):continue
  if s.startswith('docs/repository_restructure/'):continue
  if p.is_symlink() or p.stat().st_size>5_000_000:excluded.append(s);continue
  for i,line in enumerate(p.read_text(errors='replace').splitlines(),1):
   matches=sorted(set(needles.findall(line)))
   if not matches:continue
   if p.parts[0] in ['runs','artifacts','experiments','archive','presentation_assets']:category='valid historical reference'
   elif p.suffix in ['.md','.rst','.txt'] or p.parts[0]=='docs':category='documentation reference'
   elif p.parts[0]=='tutorials' and p.suffix not in ['.py','.sh','.ipynb']:category='valid historical reference'
   else:category='error requiring correction'
   refs.append({'path':s,'line':i,'matched_reference':';'.join(matches),'category':category})
with (out/'legacy_reference_audit.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','line','matched_reference','category']);w.writeheader();w.writerows(refs)
(out/'reference_audit_scope.json').write_text(json.dumps({'text_file_limit_bytes':5_000_000,'skipped_large_or_symlink_text':excluded,'excluded_roots':['hidden directories','ma_thesis_env','node_modules','raw data','caches'],'excluded_names':'credentials, cookies, private keys, sessions, tokens, .env','migration_documentation':'excluded because it intentionally records old paths'},indent=2))
errors=[r for r in refs if r['category']=='error requiring correction'];print('legacy references',len(refs),'errors',len(errors));print(json.dumps(errors[:20],indent=2))
for r in rows:
 if r['status']=='planned_move':r['status']='moved' if Path(r['new_path']).exists() and not Path(r['old_path']).is_file() else 'ERROR'
with (out/'path_mapping.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'validation_summary.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preservation_changes':len(changes),'protected_new_files':len(added),'ast_unexplained':sum(not x['equivalent_except_imports_paths_bootstrap'] for x in results),'legacy_reference_errors':len(errors),'mapping_errors':sum(r['status']=='ERROR' for r in rows),'moved_files':sum(r['status']=='moved' for r in rows)},indent=2))
allowed='artifacts/phm2026/downloads/20261005T130258188699Z-a8b31e9c.json'
assert not changes and added==[allowed]
audit=json.loads(Path(allowed).read_text())
assert audit['mode']=='parse' and audit['exit_code']==0 and audit['bytes_downloaded']==0
assert not audit['completed'] and not audit['resolved_files'] and not audit['failed']
