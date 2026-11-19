"""Synthetic safety checks; never contact Kaggle or copy real dataset rows."""
import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("download_msm", Path(__file__).parents[1] / "source/download_msm.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
HANDLE = "synthetic/test/versions/2"
BODY = b"start,end,label\n0,1,0\n"


@pytest.mark.parametrize("path", ["../label.csv", "/label.csv", "a//label.csv", "a/./label.csv", "a\\label.csv"])
def test_reject_path_traversal(path):
    with pytest.raises(Exception):
        module.valid_dataset_path(path)


def test_public_backend_pins_version_and_bounds_response(monkeypatch):
    def response(url, timeout):
        assert "datasetVersionNumber=2" in url
        assert "fileName=m%2Fdataset1%2Flabel.csv" in url
        return io.BytesIO(BODY)
    monkeypatch.setattr(module.urllib.request, "urlopen", response)
    assert module.public_label_bytes(HANDLE, "m/dataset1/label.csv", len(BODY)) == BODY
    with pytest.raises(ValueError, match="size"):
        module.public_label_bytes(HANDLE, "m/dataset1/label.csv", len(BODY) - 1)


def test_public_backend_rejects_html_and_media(monkeypatch):
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"<html>"))
    with pytest.raises(ValueError, match="annotation"):
        module.public_label_bytes(HANDLE, "m/dataset1/label.csv", 6)
    with pytest.raises(ValueError, match="limited"):
        module.public_label_bytes(HANDLE, "m/dataset1/video.mp4", 6)


def invoke(monkeypatch, tmp_path, extra=()):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"handle": HANDLE, "dataset_id": 8392825,
                                     "files": [{"name": "m/dataset1/label.csv", "bytes": len(BODY)}]}))
    monkeypatch.setattr(module, "EXPERIMENT_COUNTS", {"m": 1})
    monkeypatch.setattr(sys, "argv", ["download_msm.py", "--handle", HANDLE, "--dest", str(tmp_path / "raw"),
                                    "--mode", "labels", "--backend", "public-api", "--inventory", str(inventory), *extra])
    return module.main()


def test_preview_has_no_network_or_data_writes(monkeypatch, tmp_path):
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **k: pytest.fail("Unexpected network"))
    assert invoke(monkeypatch, tmp_path) == 0
    assert not (tmp_path / "raw").exists()


@pytest.mark.parametrize("content", [b"", b"preserve corrupt annotation"])
def test_existing_mismatch_is_preserved_without_network(monkeypatch, tmp_path, content):
    target = tmp_path / "raw/m/dataset1/label.csv"
    target.parent.mkdir(parents=True)
    target.write_bytes(content)
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **k: pytest.fail("Unexpected network"))
    assert invoke(monkeypatch, tmp_path, ["--run", "--min-free-gb", "0"]) == 1
    assert target.read_bytes() == content


def test_download_and_resume_never_refetch(monkeypatch, tmp_path):
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(BODY))
    assert invoke(monkeypatch, tmp_path, ["--run", "--min-free-gb", "0"]) == 0
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **k: pytest.fail("Unexpected refetch"))
    assert invoke(monkeypatch, tmp_path, ["--run", "--min-free-gb", "0"]) == 0
