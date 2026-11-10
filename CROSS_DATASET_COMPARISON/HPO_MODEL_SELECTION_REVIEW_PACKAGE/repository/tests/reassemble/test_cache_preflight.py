"""Synthetic metadata fixtures only; no real arrays, video or models loaded."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from reassemble.cache_preflight import PREFIX, PIXEL_RUN, assess, main


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def prefix_fixture(repo):
    root = repo / PREFIX
    save(root / "complete.json", {"segments": 1})
    save(root / "manifest.json", {"files": [{"path": str(PREFIX / "00000.npz"), "bytes": 3}]})
    return root


def pixel_fixture(repo):
    run = repo / PIXEL_RUN
    video = repo / "synthetic/video.mp4"
    video.parent.mkdir(parents=True)
    video.write_bytes(b"synthetic-not-video")
    stat = video.stat()
    save(run / "data_manifests/cohort_and_frames.json", [{
        "pixel_cache": "shared_cache/pixels/r/sample.npz",
        "frames32": list(range(32)), "positions16_in32": list(range(16)),
        "pixel_content_sha256": "a" * 64, "video_path": "synthetic/video.mp4",
        "video_bytes": stat.st_size, "video_mtime_ns": stat.st_mtime_ns,
    }])
    save(run / "config/resolved_config.json", {"weights_dir": "synthetic/weights"})
    for name in ("config.json", "preprocessor_config.json", "model.safetensors"):
        p = repo / "synthetic/weights" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"synthetic-not-weights")
    return video


def test_historical_complete_does_not_hide_missing_arrays(tmp_path, capsys):
    prefix_fixture(tmp_path)
    assert main(["--repo-root", str(tmp_path), "--cache", "prefix"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["checks"][0]["missing_arrays"] == 1
    assert result["checks"][0]["historical_complete_record"]


def test_size_mismatch_blocks_prefix(tmp_path):
    root = prefix_fixture(tmp_path)
    (root / "00000.npz").write_bytes(b"wrong-size")
    assert assess(tmp_path, "prefix")["checks"][0]["size_mismatches"] == 1


def test_present_prefix_is_only_metadata_verified(tmp_path):
    root = prefix_fixture(tmp_path)
    (root / "00000.npz").write_bytes(b"abc")
    result = assess(tmp_path, "prefix")
    assert result["ok"]
    assert result["checks"][0]["status"] == "READY_METADATA_ONLY"


def test_manifest_symlink_escape_is_blocked(tmp_path):
    root = prefix_fixture(tmp_path)
    outside = tmp_path / "outside.npz"
    outside.write_bytes(b"abc")
    (root / "00000.npz").symlink_to(outside)
    result = assess(tmp_path, "prefix")
    assert not result["ok"]
    assert result["checks"][0]["status"] == "BLOCKED_INVALID_OR_MISSING_MANIFEST"


def test_empty_pixel_cache_can_redecode_without_loading_payloads(tmp_path):
    pixel_fixture(tmp_path)
    result = assess(tmp_path, "pixels")
    assert result["ok"]
    assert result["checks"][0]["status"] == "READY_WITH_REDECODING"
    assert result["checks"][0]["samples_needing_decode"] == 1


def test_missing_or_changed_video_blocks_pixel_recovery(tmp_path):
    video = pixel_fixture(tmp_path)
    video.write_bytes(b"changed")
    assert assess(tmp_path, "pixels")["checks"][0]["changed_video_metadata"] == 1
    video.unlink()
    result = assess(tmp_path, "pixels")
    assert not result["ok"]
    assert result["checks"][0]["missing_videos"] == 1
