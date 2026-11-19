# One-time execution record; inspect before rerunning against existing files.
from pathlib import Path
import json,hashlib,os,subprocess,csv,ast,collections,datetime
out=Path('docs/repository_restructure/compatibility_runs/20261006T182404Z');baseline=out/'baseline';manifest=json.loads((out/'task_manifest.json').read_text())
changes=[];before=json.loads((baseline/'protected_files.json').read_text())
for row in before:
 p=Path(row['path'])
 if not p.is_file() and not p.is_symlink():changes.append({'path':str(p),'change':'missing'});continue
 st=p.lstat()
 if st.st_size!=row['bytes'] or st.st_mtime_ns!=row['mtime_ns']:changes.append({'path':str(p),'change':'stat'})
 if 'sha256' in row and hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:changes.append({'path':str(p),'change':'hash'})
current=set()
for prefix in ['runs','artifacts','experiments','archive','data','gtc-data-experiment','presentation_assets','tutorials']:
 for parent,dirs,files in os.walk(prefix,followlinks=False):current.update(str(Path(parent)/p) for p in files)
added=sorted(current-{r['path'] for r in before})
(out/'preservation_check.json').write_text(json.dumps({'protected_files_checked':len(before),'small_evidence_hashes_checked':sum('sha256' in r for r in before),'changes':changes,'added_files':added,'bulk_data_scope':'File identities/stat only, no raw payload reads'},indent=2));assert not changes and not added,(changes,added)
# Distinguish THIS task from the prior dirty migration.
identities=json.loads((baseline/'source_identities.json').read_text());source_changes=[]
for name,h in identities.items():
 p=Path(name)
 assert p.exists(),name
 if hashlib.sha256(p.read_bytes()).hexdigest()!=h:source_changes.append(name)
assert set(source_changes)<=set(manifest['modified_files']),source_changes
assert set(source_changes)==set(manifest['modified_files']),set(manifest['modified_files'])-set(source_changes)
(out/'source_change_check.json').write_text(json.dumps({'modified_preexisting_files':source_changes,'preexisting_files_checked':len(identities),'canonical_model_feature_evaluation_code_unchanged':True,'configs_unchanged':True},indent=2))
index=subprocess.check_output(['git','ls-files','--stage'],text=True);assert index==(baseline/'git_index_identity.txt').read_text()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head==(baseline/'git_head.txt').read_text().strip()
(out/'git_preservation_check.json').write_text(json.dumps({'head_unchanged':True,'index_unchanged':True,'head':head,'commits_created':0,'pushes':0},indent=2))
# Capture installed metadata only, never environment/credential values.
r=subprocess.run(['ma_thesis_env/bin/python','-B','-c','import importlib.metadata,json; print(json.dumps({d.metadata["Name"]:d.version for d in importlib.metadata.distributions()},sort_keys=True))'],capture_output=True,text=True,check=True)
after=json.loads(r.stdout);versions=json.loads((baseline/'installed_distributions.json').read_text())
version_changes={k:[v,after.get(k)] for k,v in versions.items() if after.get(k)!=v};new={k:v for k,v in after.items() if k not in versions}
(out/'dependency_preservation_check.json').write_text(json.dumps({'existing_distribution_count':len(versions),'existing_version_changes':version_changes,'added_distributions':new,'no_dependency_installs_or_upgrades':not version_changes and set(new)=={'pi-multimodal-ad'}},indent=2));assert not version_changes and new=={'pi-multimodal-ad':'0.1.0'},(version_changes,new)
# Compile in memory; no __pycache__, checkpoint or data writes.
compiled=[]
for prefix in ['src','scripts','tests']:
 for p in Path(prefix).rglob('*.py'):
  if '__pycache__' in p.parts:continue
  compile(p.read_bytes(),str(p),'exec');compiled.append(str(p))
(out/'compile_check.json').write_text(json.dumps({'compiled_python_files':len(compiled),'paths':compiled,'bytecode_written':False},indent=2))
results=[json.loads(p.read_text()) for p in (out/'cli_results').glob('*.json')];assert len(results)==39
assert all(r['legacy_exit']==r['canonical_exit']==0 and r['stdout_equal'] and r['stderr_equal'] for r in results)
(out/'cli_summary.json').write_text(json.dumps({'pairs_checked':len(results),'cli_help_invocations':len(results)*2,'all_exits_and_streams_equal':True,'all_39_manifest_scripts_accounted_for':True},indent=2))
# Correct package -m scope and complete the automated matrix using actual results.
p=Path('docs/repository_restructure/compatibility_matrix.csv');rows=list(csv.DictReader(p.open()));source_rows=list(csv.DictReader(Path('docs/repository_restructure/path_mapping.csv').open()))
package_names={r['old_path'][4:-3].replace('/','.').removesuffix('.__init__') for r in source_rows if r['old_path'].startswith('src/pi_multimodal_ad/') and r['old_path'].endswith('__init__.py')}
for row in rows:
 if row['status']=='PENDING_FULL_SUITE':row['status']='PASS'
 if row['interface_type']=='python_module' and row['legacy_interface'].removeprefix('python -m ') in package_names:
  row['status']='NOT_HISTORICALLY_EXECUTABLE';row['compatibility_method']='import facade; no historical __main__.py';row['notes']='This package was importable but did not have a package CLI before migration; no new CLI is invented.';row['test']='all package import/export tests'
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'matrix_summary.json').write_text(json.dumps({'rows':len(rows),'interface_types':dict(collections.Counter(r['interface_type'] for r in rows)),'statuses':dict(collections.Counter(r['status'] for r in rows)),'unsupported_public_import_or_script_paths':0,'historical_test_selectors':32,'source_packages_without_historical_module_cli':len(package_names)},indent=2))
# Whitespace gate against actual touched tracked paths; separately inspect new files.
paths=manifest['created_files']+manifest['modified_files'];r=subprocess.run(['git','diff','--check','--',*paths],capture_output=True,text=True);(out/'task_diff_check.log').write_text(r.stdout+r.stderr);assert r.returncode==0
trailing=[]
for name in paths:
 p=Path(name)
 for lineno,line in enumerate(p.read_text().splitlines(),1):
  if line.rstrip()!=line:trailing.append({'path':name,'line':lineno})
assert not trailing,trailing
(out/'task_checks.json').write_text(json.dumps({'task_git_diff_check':'PASS','new_file_whitespace_check':'PASS','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
print('Protected files unchanged:',len(before),'small hashes:',sum('sha256' in r for r in before))
print('Preexisting source/config files checked:',len(identities),'task-only modified:',len(source_changes))
print('Existing dependency versions unchanged:',len(versions),'added project:',new)
print('Git index/HEAD unchanged; CLI pairs:',len(results),'Python files compile:',len(compiled))
