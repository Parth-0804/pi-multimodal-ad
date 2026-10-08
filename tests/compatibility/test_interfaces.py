"""The frozen migration map defines the legacy import/serialization contract."""
from pathlib import Path
import ast
import csv
import importlib
import os
import pickle
import subprocess
import sys
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
ROWS = list(csv.DictReader((ROOT / 'docs/repository_restructure/path_mapping.csv').open()))
SOURCE_ROWS = [r for r in ROWS if r['status'] == 'moved' and r['old_path'].startswith('src/pi_multimodal_ad/')]
SCRIPT_ROWS = [r for r in ROWS if r['status'] == 'moved' and r['old_path'].startswith('scripts/')]


def module_name(path):
    return path[4:-3].replace('/', '.').removesuffix('.__init__')


@pytest.mark.parametrize('row', SOURCE_ROWS, ids=lambda r: module_name(r['old_path']))
def test_every_legacy_module_forwards_canonical_objects(row):
    legacy = importlib.import_module(module_name(row['old_path']))
    canonical = importlib.import_module(module_name(row['new_path']))
    if Path(row['old_path']).name != '__init__.py':
        assert legacy is canonical
    names = getattr(canonical, '__all__', [
        n for n, v in vars(canonical).items()
        if not n.startswith('__') and not isinstance(v, ModuleType)
    ])
    for name in names:
        assert getattr(legacy, name) is getattr(canonical, name), name


def test_package_child_imports_follow_remapped_model_locations():
    from pi_multimodal_ad.models import patchtst, rtdetr_regression, late_fusion
    from phm2026.models.patchtst import model
    from phm2026.models.rtdetr import regression
    from phm2026.fusion import late_fusion as fusion
    assert patchtst is model
    assert rtdetr_regression is regression
    assert late_fusion is fusion


def test_manifest_mapping_is_complete_and_not_invented():
    from pi_multimodal_ad._mapping import IMPORT_MAP
    assert IMPORT_MAP == {module_name(r['old_path']): module_name(r['new_path']) for r in SOURCE_ROWS}
    for row in SOURCE_ROWS + SCRIPT_ROWS:
        assert (ROOT / row['old_path']).is_file()
        assert (ROOT / row['new_path']).is_file()
    expected = {r['old_path'] for r in SCRIPT_ROWS}
    actual = {str(p.relative_to(ROOT)) for folder in ['dataset', 'features', 'targets', 'training', 'results']
              for p in (ROOT / 'scripts' / folder).glob('*.py')}
    assert expected == actual


def test_thin_forwarders_cannot_accumulate_scientific_implementation():
    for row in SOURCE_ROWS + SCRIPT_ROWS:
        p = ROOT / row['old_path']
        tree = ast.parse(p.read_text())
        assert len(p.read_text().splitlines()) <= 20, p
        assert not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                      ast.For, ast.While, ast.ListComp, ast.DictComp)) for n in ast.walk(tree)), p
        allowed = {'importlib', 'sys', 'runpy', 'pathlib', 'pi_multimodal_ad._forward'}
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        imports |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        assert imports <= allowed, p
        calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
        assert calls <= {'_forward_package', 'globals', '_runpy.run_module',
                         '_importlib.import_module', 'Path', 'Path(__file__).resolve',
                         'runpy.run_path', 'str'}, (p, calls)
    helper = ROOT / 'src/pi_multimodal_ad/_forward.py'
    tree = ast.parse(helper.read_text())
    assert len(helper.read_text().splitlines()) <= 55
    assert not any(isinstance(n, (ast.ClassDef, ast.BinOp)) and
                   not (isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.BitOr)))
                   for n in ast.walk(tree))
    calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert calls <= {'import_module', 'list', 'getattr', 'vars', 'vars(canonical).items',
                     'name.startswith', 'isinstance', 'get_attribute', 'sorted', 'set', 'dir'}
    mapping_tree = ast.parse((ROOT / 'src/pi_multimodal_ad/_mapping.py').read_text())
    assert not any(isinstance(n, (ast.Call, ast.FunctionDef, ast.ClassDef)) for n in ast.walk(mapping_tree))


def test_editable_imports_work_without_pythonpath_from_outside_repository(tmp_path):
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    code = ('import phm2026, pi_multimodal_ad, intel_welding, reassemble; '
            'from pi_multimodal_ad.models.patchtst import PatchTSTConfig as O; '
            'from phm2026.models.patchtst.model import PatchTSTConfig as N; assert O is N')
    result = subprocess.run([sys.executable, '-B', '-c', code], cwd=tmp_path,
                            env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('legacy,canonical,symbol', [
    ('pi_multimodal_ad.models.patchtst', 'phm2026.models.patchtst.model', 'PatchTSTConfig'),
    ('pi_multimodal_ad.features.sensor_minutes', 'phm2026.features.sensor_minutes', 'ChannelSpec'),
    ('pi_multimodal_ad.preprocessing.timeseries', 'phm2026.preprocessing.timeseries', 'FeatureNormalizer'),
    ('pi_multimodal_ad.utils.config', 'phm2026.utils.config', 'ResolvedConfig'),
])
def test_historical_pickle_global_reference_resolves_to_canonical(legacy, canonical, symbol):
    # A self-authored protocol-0 GLOBAL fixture; no historical/untrusted pickle is loaded.
    payload = f'c{legacy}\n{symbol}\n.'.encode('ascii')
    assert pickle.loads(payload) is getattr(importlib.import_module(canonical), symbol)


def test_historical_pickle_instance_metadata_roundtrip():
    from dataclasses import asdict
    from phm2026.models.patchtst.model import PatchTSTConfig
    original = PatchTSTConfig(input_channels=2)
    payload = pickle.dumps(original, protocol=2)
    # Protocol-2 GLOBAL references are line terminated, so no length/header surgery.
    old = b'phm2026.models.patchtst.model\n'
    assert old in payload
    legacy_payload = payload.replace(old, b'pi_multimodal_ad.models.patchtst\n')
    restored = pickle.loads(legacy_payload)
    assert type(restored) is PatchTSTConfig
    assert asdict(restored) == asdict(original)
