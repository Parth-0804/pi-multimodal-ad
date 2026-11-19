# One-time execution record; inspect before rerunning against existing files.
from pathlib import Path
import json,ast,csv
out=Path('docs/repository_restructure/compatibility_runs/20261006T182404Z');interfaces=json.loads((out/'interfaces.json').read_text());paths={}
for name in ['src/phm2026','scripts/phm2026','src/pi_multimodal_ad','scripts/training','scripts/features','scripts/targets','scripts/dataset','scripts/results']:
 for p in Path(name).rglob('*.py'):paths[str(p)]=ast.parse(p.read_text())
roots=[];execution=[];serialization=[]
for name,t in paths.items():
 for n in ast.walk(t):
  if isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,int) and ('__file__' in ast.unparse(n.value) or 'parents' in ast.unparse(n.value)):
   roots.append({'path':name,'line':n.lineno,'expression':ast.unparse(n),'classification':'tested fixed-depth source bootstrap' if name.startswith('scripts/') else 'source-local indexing; review context'})
  if isinstance(n,ast.Call):
   func=ast.unparse(n.func)
   if any(x in func for x in ['subprocess.','runpy.','_runpy.']):execution.append({'path':name,'line':n.lineno,'call':func})
   if any(x in func for x in ['pickle','torch.save','torch.load','joblib','cloudpickle']):serialization.append({'path':name,'line':n.lineno,'call':func,'argument_expressions':[ast.unparse(a) for a in n.args]})
(out/'static_path_execution_serialization_audit.json').write_text(json.dumps({'root_expressions':roots,'subprocess_module_execution':execution,'serialization':serialization,'decisions':{'path_roots':'Reuse marker-based utility; consolidate acquisition/config roots. Fixed-depth canonical script bootstraps retained and tested; runpy supplies canonical __file__.','subprocess':'Existing PHM subprocess calls collect Git/GPU metadata; no old script string remains in executable canonical source.','serialization':'PatchTST/RT-DETR writers store tensors plus plain dictionaries. Legacy aliases preserve qualified object lookup. No historical checkpoint loaded or rewritten.'}},indent=2))
# Matrix draft lists all old executable/import paths, plus previous test-file locations as historical filesystem references.
rows=list(csv.DictReader(Path('docs/repository_restructure/path_mapping.csv').open()));matrix=[]
for r in rows:
 if r['status']!='moved':continue
 old,new=r['old_path'],r['new_path']
 if old.startswith('src/pi_multimodal_ad/'):
  legacy=old[4:-3].replace('/','.').removesuffix('.__init__');canonical=new[4:-3].replace('/','.').removesuffix('.__init__')
  matrix.append(dict(legacy_interface=legacy,canonical_interface=canonical,interface_type='python_import',compatibility_method='package attribute forwarding' if old.endswith('__init__.py') else 'canonical module-object alias',test='tests/compatibility/test_interfaces.py::test_every_legacy_module_forwards_canonical_objects',status='PASS',notes='Public and private canonical objects retain identity; legacy module files contain forwarding only.'))
  matrix.append(dict(legacy_interface='python -m '+legacy,canonical_interface='python -m '+canonical,interface_type='python_module',compatibility_method='runpy canonical module execution',test='in-memory compile + representative module subprocess tests',status='REPRESENTATIVE_TESTED',notes='Original source modules have no __main__ workflow. Passive module execution preserved; no new CLI added.'))
 elif old.startswith('scripts/'):
  matrix.append(dict(legacy_interface=old,canonical_interface=new,interface_type='script_path',compatibility_method='runpy canonical script forwarding',test='tests/compatibility/test_cli.py::test_every_old_new_script_help_has_equal_output_and_exit',status='PENDING_FULL_SUITE',notes='Original argv/exit behavior forwarded; canonical __file__ and argv[0]; command execution remains repository-root based.'))
  matrix.append(dict(legacy_interface='python -m '+old[:-3].replace('/','.'),canonical_interface='python -m '+new[:-3].replace('/','.'),interface_type='python_module',compatibility_method='same script wrapper under repository namespace',test='representative script module subprocess test + wrapper audit',status='REPRESENTATIVE_TESTED',notes='Namespace script module execution requires repository cwd, as before. Scripts are not installed as distribution packages.'))
 elif old.startswith('tests/'):
  matrix.append(dict(legacy_interface=old,canonical_interface=new,interface_type='filesystem_path',compatibility_method='historical test-layout reference; use canonical path',test='full suite at canonical test locations',status='HISTORICAL_REFERENCE_ONLY',notes='Old pytest file selectors are not restored. Canonical tests remain domain-owned; no duplicate test collection.'))
for path in ['configs','data','runs','artifacts','tests/fixtures']:
 matrix.append(dict(legacy_interface=path,canonical_interface=path,interface_type='filesystem_path' if path!='configs' else 'config_path',compatibility_method='unchanged repository-relative path resolution',test='tests/compatibility/test_paths.py::test_config_and_data_paths_preserve_root_contract_from_other_cwd',status='PASS',notes='No filesystem data change; root discovery tested from legacy/canonical source and script paths.'))
for legacy,canonical in interfaces['modules'].items():
 matrix.append(dict(legacy_interface=legacy+'.<historical_object>',canonical_interface=canonical+'.<same_object>',interface_type='serialization_reference',compatibility_method='legacy qualified-name resolution via forwarding',test='all import identities; four synthetic pickle GLOBAL fixtures and one config-instance roundtrip',status='REPRESENTATIVE_TESTED',notes='Supports historical references to exported canonical objects; no claim about arbitrary pickle format/dependency drift or moved full model objects. No historical checkpoint loaded.'))
fields=['legacy_interface','canonical_interface','interface_type','compatibility_method','test','status','notes']
p=Path('docs/repository_restructure/compatibility_matrix.csv');assert not p.exists()
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(matrix)
m=json.loads((out/'task_manifest.json').read_text());m['created_files'].append(str(p));(out/'task_manifest.json').write_text(json.dumps(m,indent=2))
print('Static audit and matrix written:',len(matrix),'interfaces')
