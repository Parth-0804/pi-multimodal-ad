from pathlib import Path
import ast,csv,subprocess,json,re,sys,importlib.util
OUT=Path('docs/repository_restructure')
rows=list(csv.DictReader((OUT/'path_mapping.csv').open()))
tracked=set(subprocess.check_output(['git','ls-files'],text=True).splitlines())
def move(old,new):
 a,b=Path(old),Path(new); assert a.is_file() and not b.exists(),(old,new);b.parent.mkdir(parents=True,exist_ok=True)
 if old in tracked:subprocess.run(['git','mv','--',old,new],check=True)
 else:a.rename(b)
 with (OUT/'moves.jsonl').open('a') as f:f.write(json.dumps({'old':old,'new':new})+'\n')
def files():
 for root in ['src','scripts','tests','tutorials']:
  for p in Path(root).rglob('*.py'):
   if '__pycache__' not in p.parts and not any(x in p.parts for x in ['outputs','runs']):yield p
 yield Path('download.py')
def rewrite(p,text):
 old=p.read_text()
 if old!=text:
  p.write_text(text)
  with (OUT/'edits.jsonl').open('a') as f:f.write(json.dumps({'phase':sys.argv[1],'path':str(p)})+'\n')
def replace_refs(text,mapping):
 for old,new in sorted(mapping.items(),key=lambda kv:-len(kv[0])):text=re.sub(re.escape(old)+r'(?![A-Za-z0-9_])',lambda _:new,text)
 return text
phase=sys.argv[1]
if phase=='namespace':
 for row in rows:
  if row['old_path'].startswith('src/pi_multimodal_ad/'):
   move(row['old_path'],row['old_path'].replace('src/pi_multimodal_ad/','src/phm2026/'))
 for p in files():rewrite(p,p.read_text().replace('pi_multimodal_ad','phm2026'))
elif phase=='models':
 modulemap={}
 for row in rows:
  if row['old_path'].startswith('src/pi_multimodal_ad/models/'):
   old=row['old_path'].replace('src/pi_multimodal_ad/','src/phm2026/')
   if old!=row['new_path']:
    modulemap[old[4:-3].replace('/','.')]=row['new_path'][4:-3].replace('/','.')
 # Convert relative imports in moved files and their parent package before relocation.
 for p in Path('src/phm2026/models').glob('*.py'):
  text=p.read_text();lines=text.splitlines(keepends=True)
  package='phm2026.models'
  changes=[]
  for node in ast.walk(ast.parse(text)):
   if isinstance(node,ast.ImportFrom) and node.level:
    absolute=importlib.util.resolve_name('.'*node.level+(node.module or ''),package)
    original='.'*node.level+(node.module or '')
    changes.append((node.lineno-1,original,absolute))
  for index,old,new in changes:lines[index]=lines[index].replace('from '+old+' import','from '+new+' import',1)
  rewrite(p,''.join(lines))
 for row in rows:
  if row['old_path'].startswith('src/pi_multimodal_ad/models/'):
   old=row['old_path'].replace('src/pi_multimodal_ad/','src/phm2026/')
   if old!=row['new_path']:move(old,row['new_path'])
 for path,content in {
  'src/phm2026/models/rtdetr/__init__.py':'"""PHM RT-DETR pipelines and model components."""\n',
  'src/phm2026/models/patchtst/__init__.py':'"""PHM PatchTST model and regression pipeline."""\nfrom .model import PatchTSTConfig, PatchTSTRegressor\n\n__all__ = ["PatchTSTConfig", "PatchTSTRegressor"]\n',
  'src/phm2026/fusion/__init__.py':'"""PHM sensor and visual fusion implementations."""\n'}.items():Path(path).write_text(content)
 pathmap={a.replace('.','/')+'.py':b.replace('.','/')+'.py' for a,b in modulemap.items()}
 for p in files():rewrite(p,replace_refs(replace_refs(p.read_text(),modulemap),pathmap))
elif phase=='scripts':
 for row in rows:
  if row['old_path'].startswith('scripts/') and row['old_path']!=row['new_path']:move(row['old_path'],row['new_path'])
 pathmap={r['old_path']:r['new_path'] for r in rows if r['old_path']!=r['new_path']}
 for p in files():
  text=replace_refs(p.read_text(),pathmap)
  if str(p).startswith('scripts/phm2026/') and len(p.parts)==4:
   # A relocated script is three parents below repository root. All existing
   # parent indexing here is repository root discovery (audited beforehand).
   text=re.sub(r'Path\(__file__\)\.resolve\(\)\.parents\[[12]\]', 'Path(__file__).resolve().parents[3]',text)
   if 'phm2026' in text and 'sys.path.insert' not in text:
    tree=ast.parse(text);nodes=list(tree.body);index=0
    if nodes and isinstance(nodes[0],ast.Expr) and isinstance(nodes[0].value,ast.Constant) and isinstance(nodes[0].value.value,str):index=nodes[0].end_lineno
    for node in nodes:
     if isinstance(node,ast.ImportFrom) and node.module=='__future__':index=node.end_lineno
    lines=text.splitlines(keepends=True)
    lines.insert(index,'\n# Source-tree entry point; no installed package is required.\nimport sys as _sys\nfrom pathlib import Path as _Path\n_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))\n\n')
    text=''.join(lines)
  # Existing presentation root was also one level too shallow.
  if str(p)=='scripts/presentation/generate_professor_presentation.py':text=text.replace('Path(__file__).resolve().parents[1]','Path(__file__).resolve().parents[2]')
  rewrite(p,text)
elif phase=='tests':
 for row in rows:
  if row['old_path'].startswith('tests/unit/'):move(row['old_path'],row['new_path'])
else:raise ValueError(phase)
print('completed',phase)
