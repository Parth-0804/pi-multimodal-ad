"""Run one EDA notebook in a fresh repository-environment kernel; export offline HTML."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import os
import re
import subprocess
import sys


def main():
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from reassemble_support import identity, digest
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notebook',choices=['01_reassemble_eda.ipynb','02_phm_eda.ipynb','03_intel_welding_eda.ipynb'])
    parser.add_argument('--data-root',help='Optional REASSEMBLE raw root override')
    args=parser.parse_args();root=Path(__file__).resolve().parents[2]
    source=Path(__file__).parent/args.notebook
    domain={'01':'reassemble','02':'phm2026','03':'intel_welding'}[args.notebook[:2]]
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=root/'runs'/domain/(stamp+'-dataset-eda');out.mkdir(parents=True,exist_ok=False)
    (out/'.gitignore').write_text('*\n')
    for folder in ['figures','media','tables','reports','manifests','config','runtime']:(out/folder).mkdir()
    os.environ.update(WALKTHROUGH_OUTPUT=str(out),EDA_OUTPUT=str(out),PYTHONDONTWRITEBYTECODE='1',
                      MPLCONFIGDIR=str(out/'runtime/matplotlib'),IPYTHONDIR=str(out/'runtime/ipython'),
                      JUPYTER_RUNTIME_DIR=str(out/'runtime/jupyter'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',
                      OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    if args.data_root:os.environ['REASSEMBLE_DATA_ROOT']=str(Path(args.data_root).resolve())
    spec=out/'runtime/kernels/eda';spec.mkdir(parents=True)
    (spec/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable,'-B','-m','ipykernel_launcher','-f','{connection_file}'],display_name='Repository EDA',language='python')))
    os.environ['JUPYTER_PATH']=str(out/'runtime')
    nb=nbformat.read(source,as_version=4)
    print('Executing',args.notebook,'->',out.relative_to(root),flush=True)
    try:
        NotebookClient(nb,timeout=240,kernel_name='eda',allow_errors=False,resources={'metadata':{'path':str(root)}}).execute()
    except Exception as exc:
        (out/'reports/execution_failure.txt').write_text(str(exc));raise
    finally:nbformat.write(nb,out/(source.stem+'.executed.ipynb'))
    body,_=HTMLExporter(template_name='basic',exclude_input=True).from_notebook_node(nb)
    body=re.sub(r'<script\b[^>]*>.*?</script>','',body,flags=re.S|re.I)
    assert not re.search(r'<(?:img|script|link|source|video|audio)\b[^>]*(?:src|href)=["\'](?:https?:)?//',body,re.I)
    css='body{font:17px/1.6 system-ui;max-width:1120px;margin:40px auto;padding:0 24px;color:#173247}h2{margin-top:2.5em;border-top:1px solid #ccd;padding-top:16px}table{display:block;overflow:auto;border-collapse:collapse;font-size:14px}td,th{padding:8px;border:1px solid #ccd;text-align:left}img,video{max-width:100%;height:auto}pre{white-space:pre-wrap;font-size:13px;background:#eef3f5;padding:12px}blockquote{border-left:4px solid #c80;padding-left:20px}.anchor-link{display:none}'
    (out/(source.stem+'.html')).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>'+source.stem+'</title><style>'+css+'</style><body>'+body+'</body></html>')
    import importlib.metadata
    versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','matplotlib','nbclient','nbconvert','h5py']}
    provenance=dict(utc=datetime.now(timezone.utc).isoformat(),command=[os.path.relpath(sys.executable,root),'-B',os.path.relpath(__file__,root),*sys.argv[1:]],git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),git_status=subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'],cwd=root,text=True),software=versions,source=identity(source,root,True),helpers=[identity(p,root,True) for p in Path(__file__).parent.glob('*.py')],code_cells=sum(c.cell_type=='code' for c in nb.cells),error_outputs=0,browser_playback_verified=False)
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2))
    files=[identity(p,root,True) for p in out.rglob('*') if p.is_file() and 'runtime' not in p.relative_to(out).parts]
    (out/'manifests/outputs.json').write_text(json.dumps(files,indent=2))
    print('PASS:',out.relative_to(root)/(source.stem+'.html'),flush=True)


if __name__=='__main__':main()
