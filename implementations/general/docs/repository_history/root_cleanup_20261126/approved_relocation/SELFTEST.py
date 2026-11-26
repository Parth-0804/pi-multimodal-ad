"""Tiny synthetic-only tests; all test roots remain inside this phase directory."""
import contextlib
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import subprocess

PHASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('approved_relocate', PHASE / 'RELOCATE.py')
tool = importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
BASE = PHASE / ('selftest_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
BASE.mkdir()
results = []


def fixture(name):
    root = BASE / name;root.mkdir()
    (root / 'AGENTS.md').write_text('Synthetic fixture only.\n')
    (root / 'pyproject.toml').write_text('[project]\nname="synthetic"\nversion="0.0.0"\n')
    (root / '.gitignore').write_text('*.bin\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    phase = root / 'phase';phase.mkdir();tool.ROOT=root;tool.HERE=phase
    for _, old, new in tool.GROUPS:
        p=root/old;p.mkdir(parents=True,exist_ok=True);(p/'synthetic.bin').write_bytes(b'tiny synthetic fixture\n')
        (root/new).parent.mkdir(parents=True,exist_ok=True)
    # Verify merge, collision preservation, proxy replacement and raw-link repair.
    (root/'VIFAILBACK/README.md').write_text('Original synthetic workspace.\n')
    (root/'VIFAILBACK/src').mkdir();(root/'VIFAILBACK/src/module.py').write_text('synthetic = True\n')
    (root/'VIFAILBACK/02_dataset_verification').mkdir(exist_ok=True)
    canonical=root/'implementations/VIFAILBACK';canonical.mkdir(exist_ok=True)
    (canonical/'README.md').write_text('Canonical synthetic guide.\n')
    (canonical/'src').symlink_to('../../VIFAILBACK/src')
    if (canonical/'02_dataset_verification').exists():
        (canonical/'02_dataset_verification').rmdir()  # empty synthetic setup parent
    (canonical/'02_dataset_verification').symlink_to('../../VIFAILBACK/02_dataset_verification')
    raw=root/'MILLING DATASET/data/raw/msm/versions/2';raw.mkdir(parents=True)
    (raw/'one.bin').write_bytes(b'synthetic raw fixture\n')
    legacy=root/'implementations/MSM/experiments/legacy';legacy.mkdir(exist_ok=True)
    policy='/data/\n'
    (legacy/'.gitignore').write_text(policy);(root/'MILLING DATASET/.gitignore').write_text(policy)
    target=root/'implementations/MSM/01_raw_dataset';target.mkdir(parents=True);(target/'official_dataset').symlink_to('../../MILLING DATASET/data/raw/msm/versions/2')
    link=root/'implementations/HANDOVER/experiments/common_support_v2';link.mkdir(parents=True);(link/'01_raw_dataset').symlink_to('../../../../HANDOVER/01_raw_dataset')
    (root/'HANDOVER/.gitignore').write_text('/01_raw_dataset/\n')
    (root/'REBOOT/.gitignore').write_text('/01_raw_dataset/\n/runs/\n')
    (root/'CROSS_DATASET_COMPARISON/.gitignore').write_text('/logs/\n')
    tool.dump(phase/'APPROVAL.json',{'scope':[{'old':a,'new':b} for _,a,b in tool.GROUPS]})
    tool.dump(phase/'GPU_GATE_BEFORE.json',{'returncode':0,'stdout':''})
    return root, phase


def gate(directory, groups):
    report=tool.HERE/'adapter.json';tool.dump(report,{'status':'PASS','frozen_source_unchanged':True,'no_resume':True,'groups':list(tool.FROZEN)})
    file=tool.HERE/'gate.json';tool.dump(file,{'preflight':str(directory.relative_to(tool.ROOT)),'groups':[g[0] for g in groups],'process_gate_passed':True,'scientific_jobs_will_not_be_resumed':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'adapter_gates':{g:str(report.relative_to(tool.ROOT)) for g in tool.FROZEN}})
    return file


root, phase=fixture('roundtrip')
with contextlib.redirect_stdout(io.StringIO()):
    preflight=tool.prepare(tool.GROUPS);file=gate(preflight,tool.GROUPS)
    tool.apply(preflight,file)
    tool.recover(preflight,execute=True)
assert all((root/old).exists() for _,old,_ in tool.GROUPS)
assert (root/'implementations/VIFAILBACK/src').is_symlink()
results.append({'name':'all-group merge/proxy/link/preservation/recovery roundtrip','status':'PASS'})
root, phase=fixture('conflict')
(root/'implementations/HANDOVER/01_raw_dataset').write_text('independent synthetic destination\n')
info=tool.plan(tool.select('handover_raw'))
assert any('Independent destination' in c['reason'] for c in info['conflicts'])
assert (root/'HANDOVER/01_raw_dataset/synthetic.bin').exists()
results.append({'name':'independent destination conflict blocks planning without overwrite','status':'PASS'})
root, phase=fixture('source_changed')
with contextlib.redirect_stdout(io.StringIO()):preflight=tool.prepare(tool.select('handover_raw'))
file=gate(preflight,tool.select('handover_raw'))
(root/'HANDOVER/01_raw_dataset/synthetic.bin').write_bytes(b'changed synthetic fixture\n')
try:tool.apply(preflight,file)
except RuntimeError as exc:assert 'Source changed since preflight' in str(exc)
else:raise AssertionError('Source identity drift did not fail')
assert not (preflight/'ACTIONS.jsonl').exists()
results.append({'name':'changed source identity blocks before first mutation','status':'PASS'})
root, phase=fixture('ignore_exposure')
(root/'.gitignore').write_text('/HANDOVER/01_raw_dataset/\n')
(root/'HANDOVER/.gitignore').write_text('# no additional policy\n')
with contextlib.redirect_stdout(io.StringIO()):preflight=tool.prepare(tool.select('handover_raw'))
status=json.loads((preflight/'STATUS.json').read_text());assert status['ignore_audit']['ignored_to_exposed']==1
file=gate(preflight,tool.select('handover_raw'))
try:tool.apply(preflight,file)
except RuntimeError as exc:assert 'ignore exposure' in str(exc)
else:raise AssertionError('Ignore exposure did not fail')
assert not (preflight/'ACTIONS.jsonl').exists()
results.append({'name':'ignored-to-exposed policy regression blocks before first mutation','status':'PASS'})
root, phase=fixture('alternate_worktree_policy')
shadow=phase/'policy_shadow';shadow.mkdir();(shadow/'.gitignore').write_text('/shadow_only/\n')
original=tool.git_ignored(['shadow_only/synthetic.txt'],root)
alternate=tool.git_ignored(['shadow_only/synthetic.txt'],shadow,shadow)
assert original.get('shadow_only/synthetic.txt',{}).get('ignored',False) is False
assert alternate['shadow_only/synthetic.txt']['ignored'] is True
results.append({'name':'alternate worktree uses shadow-only .gitignore; original worktree leaves same path visible','status':'PASS'})
(PHASE/'SELFTEST_RESULTS.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'status':'PASS','synthetic_fixture_root':str(BASE),'tests':results,'real_source_payloads_read_or_modified':False,'real_relocation_executed':False},indent=2)+'\n')
print(json.dumps(results,indent=2))
