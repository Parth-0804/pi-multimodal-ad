"""Tiny synthetic tests of the frozen ViFailback location interfaces."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapter


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


LEGACY_SOURCE = '''from pathlib import Path
import hashlib
PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parent
def resolve(value):
    p = Path(value)
    return p if p.is_absolute() else REPO / p
def code_identity():
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in [PROJECT/'src', PROJECT/'configs']
            for p in sorted(folder.rglob('*')) if p.is_file() and p.suffix in ['.py', '.json']}
'''

REFERENCE_SOURCE = '''from .common import REPO
import hashlib
PHASE = REPO/'26.10.2026_feedback_experiments/source'
BOOTSTRAP = REPO/'parth_ws_bootstrap/source'
DECODER = REPO/'MILLING DATASET/.tools/decoder'
def identities():
    return {str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [PHASE/'phase.py', BOOTSTRAP/'visual.py']}
'''

MATCHED_SOURCE = '''from pathlib import Path
import os
import hashlib
STUDY = Path(__file__).resolve().parents[2]
PROJECT = STUDY.parents[1]
REPO = PROJECT.parent
PROTOCOL_SHA256 = '{protocol_sha}'
def relative(path):
    return os.path.relpath(Path(path).resolve(), REPO)
def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else REPO/p
def code_identity():
    return {{relative(p):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((STUDY/'src').rglob('*.py'))}}
'''


class ViFailbackRelocationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="vif-relocation-synthetic-")
        self.repo = Path(self.temporary.name) / "repository"
        self.project = self.repo / "implementations/VIFAILBACK"
        self.study = self.project / adapter.MATCHED
        self._write(self.project/'src/vifailback/__init__.py', "")
        self._write(self.project/'src/vifailback/common.py', LEGACY_SOURCE)
        self._write(self.project/'src/vifailback/reference.py', REFERENCE_SOURCE)
        self._write(self.project/'configs/experiment.json', '{"historical_root":"DATASET_RESEARCH/VIFAILBACK_VERIFICATION"}\n')
        protocol = self.study/'01_protocol_and_source_evidence/protocol.json'
        self._write(protocol, '{"synthetic":true}\n')
        self._write(self.study/'src/matched_vifailback/__init__.py', "")
        self._write(self.study/'src/matched_vifailback/common.py', MATCHED_SOURCE.format(protocol_sha=sha(protocol)))
        phase = self.repo/adapter.MAPPINGS['26.10.2026_feedback_experiments']/'source/phase.py'
        bootstrap = self.repo/adapter.MAPPINGS['parth_ws_bootstrap']/'source/visual.py'
        self._write(phase, "SYNTHETIC_PHASE = True\n")
        self._write(bootstrap, "SYNTHETIC_VISUAL = True\n")
        self._write(self.repo/adapter.MAPPINGS['MILLING DATASET']/'.tools/decoder', 'synthetic decoder marker\n')
        self._write(self.repo/adapter.MAPPINGS['DATASET_RESEARCH/VIFAILBACK_VERIFICATION']/'marker.txt', 'synthetic metadata\n')
        self._write(self.repo.parent/'datasets/marker.txt', 'synthetic external metadata\n')
        original = {self.logical(p):sha(p) for folder in [self.project/'src',self.project/'configs']
                    for p in folder.rglob('*') if p.is_file() and p.suffix in ['.py','.json']}
        reused = {self.logical(p):sha(p) for p in [phase,bootstrap]}
        matched = {self.logical(p):sha(p) for p in (self.study/'src').rglob('*.py')}
        self._write(self.project/'logs/20261029T004900Z/EXECUTION_PROVENANCE.json',
                    json.dumps({'implementation':original,'reused_source':reused}))
        self._write(self.study/'13_reproducibility/IMPLEMENTATION_FREEZE.json',
                    json.dumps({'implementation':matched,'protocol_sha256':sha(protocol)}))

    def tearDown(self):
        self.temporary.cleanup()

    def _write(self, path, text):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text)

    def logical(self,path):
        relative=path.relative_to(self.repo).as_posix()
        for old,new in sorted(adapter.MAPPINGS.items(),key=lambda pair:len(pair[1]),reverse=True):
            if relative==new or relative.startswith(new+'/'):
                return old+relative[len(new):]
        return relative

    def test_fixed_depth_roots_and_historical_configuration(self):
        with adapter.vifailback_context(self.repo):
            common=importlib.import_module('vifailback.common')
            matched=importlib.import_module('matched_vifailback.common')
            self.assertEqual(common.REPO.parts,self.repo.parts)
            self.assertEqual(common.PROJECT.parts,(self.repo/'VIFAILBACK').parts)
            self.assertEqual(matched.PROJECT.parts,(self.repo/'VIFAILBACK').parts)
            self.assertEqual(matched.REPO.parts,self.repo.parts)
            self.assertEqual(common.resolve('DATASET_RESEARCH/VIFAILBACK_VERIFICATION/marker.txt').read_text(),'synthetic metadata\n')
            self.assertEqual(common.resolve('../datasets/marker.txt').read_text(),'synthetic external metadata\n')

    def test_direct_root_joins_and_pathlib_relative_identity(self):
        with adapter.vifailback_context(self.repo):
            reference=importlib.import_module('vifailback.reference')
            self.assertEqual(reference.DECODER.read_text(),'synthetic decoder marker\n')
            self.assertEqual(set(reference.identities()),{
                '26.10.2026_feedback_experiments/source/phase.py',
                'parth_ws_bootstrap/source/visual.py'})

    def test_os_relpath_preserves_matched_identity_namespace(self):
        with adapter.vifailback_context(self.repo):
            common=importlib.import_module('matched_vifailback.common')
            actual=common.relative(self.study/'src/matched_vifailback/common.py')
            self.assertEqual(actual,'VIFAILBACK/'+adapter.MATCHED+'/src/matched_vifailback/common.py')
            self.assertTrue(all(key.startswith('VIFAILBACK/') for key in common.code_identity()))

    def test_all_saved_identity_dictionaries_match(self):
        result=adapter.verify_source_identities(self.repo)
        self.assertTrue(all(row['exact_match'] for row in result['checks']))

    def test_changed_source_is_rejected_without_refreshing_receipt(self):
        source=self.project/'src/vifailback/reference.py'
        source.write_text(source.read_text()+'\nCHANGED = True\n')
        receipt=self.project/'logs/20261029T004900Z/EXECUTION_PROVENANCE.json'
        before=receipt.read_bytes()
        with self.assertRaisesRegex(ValueError,'changed'):
            adapter.verify_source_identities(self.repo)
        self.assertEqual(receipt.read_bytes(),before)

    def test_changed_protocol_is_rejected(self):
        path=self.study/'01_protocol_and_source_evidence/protocol.json'
        path.write_text('{"synthetic":"changed"}\n')
        with self.assertRaisesRegex(ValueError,'protocol identity changed'):
            adapter.verify_source_identities(self.repo)

    def test_context_restores_globals_and_module_cache(self):
        import pathlib
        import os
        original_path=pathlib.Path
        original_relpath=os.path.relpath
        original_search=sys.path[:]
        with adapter.vifailback_context(self.repo):
            importlib.import_module('vifailback.common')
            self.assertIs(pathlib.Path,original_path)
            self.assertIs(os.path.relpath,original_relpath)
        self.assertEqual(sys.path,original_search)
        self.assertNotIn('vifailback.common',sys.modules)
        self.assertNotIn('vifailback',sys.modules)


if __name__=='__main__':
    unittest.main()
