"""Tiny synthetic checks; no real study/model/raw inputs are imported or read."""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ADAPTER = Path(__file__).resolve().parents[1] / "src/reassemble/relocation.py"
SPEC = importlib.util.spec_from_file_location("reassemble_relocation_under_test", ADAPTER)
relocation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(relocation)


class RelocationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.old = "legacy/bootstrap/run"
        self.new = "implementations/example/experiments/bootstrap/run"
        self.scope = self.repo / self.new / "source"
        self.scope.mkdir(parents=True)
        self.mappings = {self.old: self.new,
                         "configs/example": "implementations/example/configs"}
        self.config = self.repo / "implementations/example/configs/frozen.json"
        self.config.parent.mkdir(parents=True)
        self.config.write_text('{"seed": 42}\n')

    def source(self, name, body):
        path = self.scope / (name + ".py")
        path.write_text(body)
        return path

    def test_fixed_depth_filesystem_and_relative_identity(self):
        state = relocation.Relocation(self.repo, self.mappings)
        P = state.Path
        source = P(self.scope / "common.py")
        root = source.resolve().parents[1]
        repo = root.parents[2]
        self.assertEqual(str(repo), str(self.repo))
        self.assertEqual(root.parts, (self.repo / self.old).parts)
        self.assertEqual(str(root), str(self.repo / self.new))
        self.assertEqual(os.fspath(root), str(self.repo / self.new))
        self.assertEqual(str(root.relative_to(repo)), self.old)
        self.assertEqual(state.relpath(root, repo), self.old)
        self.assertEqual((repo / "configs/example/frozen.json").read_text(), '{"seed": 42}\n')
        relative_input = P("configs/example/frozen.json")
        self.assertEqual(str(relative_input), str(self.config))
        self.assertEqual(relative_input.read_text(), '{"seed": 42}\n')
        self.assertEqual(str(relative_input.relative_to(P("configs/example"))), "frozen.json")
        self.assertFalse((self.repo / "legacy").exists())

    def test_original_source_keys_and_hashes_and_tamper_rejection(self):
        original = self.source("synthetic_identity", """from pathlib import Path
import hashlib, json, os
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
def identities():
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / 'source').glob('*.py')}
def check(expected):
    assert identities() == expected, 'SOURCE_DRIFT'
def config():
    return json.loads((REPO / 'configs/example/frozen.json').read_text())
def os_identity():
    return os.path.relpath(ROOT.resolve(), REPO)
""")
        digest = hashlib.sha256(original.read_bytes()).hexdigest()
        expected = {self.old + "/source/synthetic_identity.py": digest}
        real_path_class, real_relpath = Path, os.path.relpath
        before_path = list(sys.path)
        with relocation.relocation_context(self.repo, self.mappings, [self.scope]):
            sys.path.insert(0, str(self.scope))
            module = importlib.import_module("synthetic_identity")
            self.assertEqual(module.identities(), expected)
            self.assertEqual(module.config(), {"seed": 42})
            self.assertEqual(module.os_identity(), self.old)
            module.check(expected)
            original.write_text(original.read_text() + "# deliberate synthetic drift\n")
            with self.assertRaisesRegex(AssertionError, "SOURCE_DRIFT"):
                module.check(expected)
            self.assertIs(Path, real_path_class)
            self.assertIs(os.path.relpath, real_relpath)
        self.assertNotIn("synthetic_identity", sys.modules)
        self.assertEqual(sys.path, before_path)

    def test_package_and_explicit_import_loader(self):
        package = self.scope / "synthetic_package"
        package.mkdir()
        (package / "__init__.py").write_text("")
        (package / "common.py").write_text("from pathlib import Path\nHERE=Path(__file__).resolve()\n")
        self.source("synthetic_explicit", """from pathlib import Path
import importlib.util
def load():
    path = Path(__file__).resolve().parent / 'synthetic_package/common.py'
    spec = importlib.util.spec_from_file_location('synthetic_loaded_common', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
""")
        with relocation.relocation_context(self.repo, self.mappings, [self.scope]):
            sys.path.insert(0, str(self.scope))
            common = importlib.import_module("synthetic_package.common")
            explicit = importlib.import_module("synthetic_explicit").load()
            logical = self.repo / self.old / "source/synthetic_package/common.py"
            self.assertEqual(common.HERE.parts, logical.parts)
            self.assertEqual(explicit.HERE.parts, logical.parts)
        self.assertNotIn("synthetic_package.common", sys.modules)

    def test_stop_record_retained_and_no_implicit_execution(self):
        stop = self.repo / self.new / "STOP.json"
        stop.write_text('{"requested":"stop"}\n')
        original = stop.read_bytes()
        with relocation.relocation_context(self.repo, self.mappings, [self.scope]) as state:
            self.assertEqual((state.Path(self.repo / self.old) / "STOP.json").read_bytes(), original)
            self.assertEqual(state.loaded, set())
        self.assertEqual(stop.read_bytes(), original)

    def test_reject_ambiguous_or_escaping_mappings(self):
        for bad in ({"a": "same", "b": "same"}, {"../outside": "inside"},
                    {"a": "b", "b": "c"}):
            with self.assertRaises(ValueError):
                relocation.Relocation(self.repo, bad)

    def test_preimported_scope_is_rejected(self):
        self.source("synthetic_preloaded", "value=1\n")
        sys.path.insert(0, str(self.scope))
        try:
            importlib.import_module("synthetic_preloaded")
            with self.assertRaisesRegex(RuntimeError, "before importing"):
                with relocation.relocation_context(self.repo, self.mappings, [self.scope]):
                    pass
        finally:
            sys.path.remove(str(self.scope))
            sys.modules.pop("synthetic_preloaded", None)


if __name__ == "__main__":
    unittest.main()
