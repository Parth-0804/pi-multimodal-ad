"""Root discovery, portable paths and source-directory depth regression checks."""
from pathlib import Path
import os

import pytest
from phm2026.repository_paths import find_repository_root
from phm2026.utils.config import ConfigError, ResolvedConfig, find_repository_root as config_root, load_yaml_config
from phm2026.acquisition import phm_download

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('start', [ROOT, ROOT / 'src/phm2026/models/patchtst/model.py',
                                  ROOT / 'scripts/phm2026/training/train_patchtst.py',
                                  ROOT / 'scripts/training/train_patchtst.py'])
def test_root_discovery_from_old_new_and_nested_locations(start):
    assert find_repository_root(start) == ROOT
    assert config_root(start) == ROOT


def test_root_discovery_does_not_depend_on_source_depth(tmp_path):
    root = tmp_path / 'repo'
    root.mkdir()
    (root / '.git').mkdir()
    (root / 'AGENTS.md').write_text('synthetic repository marker')
    nested = root / 'a/b/c/d/e/module.py'
    nested.parent.mkdir(parents=True)
    nested.write_text('# synthetic')
    assert find_repository_root(nested) == root
    assert config_root(nested) == root
    with pytest.raises(ConfigError, match='repository root not found'):
        config_root(tmp_path)


def test_config_and_data_paths_preserve_root_contract_from_other_cwd(tmp_path, monkeypatch):
    cfg = load_yaml_config('configs/datasets/phm2026.yaml', repository_root=ROOT)
    monkeypatch.chdir(tmp_path)
    assert cfg.repository_root == ROOT
    for reference in ['configs', 'data', 'runs', 'artifacts', 'tests/fixtures']:
        assert cfg.resolve_repository_path(reference, field='fixture', must_exist=True) == (ROOT / reference).resolve()
    with pytest.raises(ConfigError, match='escapes'):
        cfg.resolve_repository_path('../outside', field='fixture')
    assert load_yaml_config(ROOT / 'configs/datasets/phm2026.yaml', repository_root=ROOT).sha256 == cfg.sha256


def test_downloader_uses_same_root_and_parser_without_writing_provenance():
    from pi_multimodal_ad.acquisition import phm_download as legacy
    assert legacy is phm_download
    assert phm_download.REPO == ROOT
    assert legacy.parser().format_help() == phm_download.parser().format_help()
