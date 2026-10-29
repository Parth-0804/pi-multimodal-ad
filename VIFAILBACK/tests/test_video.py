"""Synthetic time-coded video only; no dataset media in tests."""
import subprocess
import numpy as np
import pytest
from vifailback.video import ffmpeg, positions, inspect_video, rgb_frames
from vifailback.common import sha


def test_uniform_positions_are_time_ordered_and_distinct():
    assert positions(16).tolist() == list(range(16))
    x = positions(101)
    assert x[0] == 0 and x[-1] == 100 and np.all(np.diff(x) > 0)
    with pytest.raises(ValueError): positions(15)


def test_full_decode_pts_and_rgb_contract(tmp_path):
    path = tmp_path / 'synthetic.mp4'
    subprocess.run([str(ffmpeg()), '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=64x48:rate=25:duration=1.6',
                    '-c:v', 'libx264', '-threads', '1', '-pix_fmt', 'yuv420p', str(path)], check=True)
    result = inspect_video(path, expected_frames=40, expected_sha256=sha(path), width=64, height=48)
    assert result['technical_valid'], result['reason']
    assert result['decoded_frames'] == 40 and result['source_width_height'] == [64,48]
    assert result['frame_PTS_seconds'][-1] == 1.56
    assert len(result['selected_RGB_sha256']) == 16
    frames = rgb_frames(path, positions(40), width=64, height=48)
    assert frames.shape == (16,48,64,3)
    invalid = inspect_video(path, expected_frames=41, expected_sha256=sha(path), width=64, height=48)
    assert not invalid['technical_valid'] and 'FRAME_COUNT' in invalid['reason']
    invalid_hash = inspect_video(path, expected_frames=40, expected_sha256='0'*64)
    assert invalid_hash['reason'] == 'SOURCE_HASH_MISMATCH'
