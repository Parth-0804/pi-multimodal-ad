"""Synthetic timing and frame-selection checks; no dataset examples are test fixtures."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

path = Path(__file__).parents[1] / "source/stage2"
sys.path.insert(0,str(path))
from frame_contract import select_frames
from align_audio import estimate_mapping


def test_exactly_16_ordered_frames_keep_uncertainty_inside_one_label():
    pts = np.arange(300)/30
    result = select_frames(pts,2.,3.,.25,.08,[[0,10]])
    assert result["accepted"] and len(result["indices"]) == 16
    assert len(set(result["indices"])) == 16
    assert np.all(np.diff(result["video_pts_s"])>0)
    assert min(result["sensor_pts_s"])-.08 >= 2.
    assert max(result["sensor_pts_s"])+.08 < 3.


def test_short_intervals_are_rejected_instead_of_repeating_frames():
    result = select_frames(np.arange(300)/30,2.,2.5,0.,.08,[[0,10]])
    assert not result["accepted"]
    assert "fewer_than_16_distinct_native_frames" in result["reasons"]


def test_missing_video_coverage_and_unsupported_alignment_are_rejected():
    result = select_frames(np.arange(60)/30,2.,3.,0.,.08,[[2.2,3]])
    assert not result["accepted"]
    assert "outside_validated_audio_support" in result["reasons"]
    assert "video_does_not_cover_interval" in result["reasons"]


def test_repeated_native_pts_are_rejected():
    pts = np.arange(300)/30; pts[50] = pts[49]
    assert not select_frames(pts,2.,3.,0.,.08,[[0,10]])["accepted"]


def test_label_blind_alignment_recovers_known_offset_and_heldout_windows():
    rng = np.random.default_rng(42)
    # A smooth synthetic changing acoustic feature, copied with a known time shift.
    from scipy.ndimage import gaussian_filter1d
    reference = gaussian_filter1d(rng.normal(size=(3,6400)),sigma=5,axis=1)
    video = np.pad(reference,((0,0),(124,100)))
    protocol={"local_window_s":8,"anchor_stride_s":8,"local_lag_search_half_width_s":.5,
              "local_min_correlation":.75,"inlier_tolerance_s":.1,"min_calibration_anchors":3,
              "min_validation_anchors":3,"min_anchor_span_s":30}
    mapping = estimate_mapping(video,reference,protocol)
    assert mapping["accepted"]
    assert abs(mapping["offset_s"]-1.24) < .011
    assert mapping["validation_anchors"] >= 3
    assert all(a["role"] == ("calibration" if a["anchor_index"]%2==0 else "validation") for a in mapping["anchors"])


def test_partial_overlap_does_not_force_a_false_smaller_offset():
    rng=np.random.default_rng(471)
    from scipy.ndimage import gaussian_filter1d
    reference=gaussian_filter1d(rng.normal(size=(3,12800)),sigma=5,axis=1)
    video=gaussian_filter1d(rng.normal(size=(3,12200)),sigma=5,axis=1)
    video[:,4900:]=reference[:,:7300]
    protocol={"coarse_method":"calibration_consensus_v2","local_window_s":8,"anchor_stride_s":8,
              "local_lag_search_half_width_s":.5,"local_min_correlation":.75,"inlier_tolerance_s":.1,
              "min_calibration_anchors":3,"min_validation_anchors":3,"min_anchor_span_s":30}
    mapping=estimate_mapping(video,reference,protocol)
    assert mapping['accepted']
    assert abs(mapping['offset_s']-49.)<.011


def test_coarse_consensus_never_reads_validation_reference_blocks():
    from calibration_consensus import correlations
    rng=np.random.default_rng(81)
    reference=rng.normal(size=(1,6400));video=np.pad(reference,((0,0),(50,0)))
    a,b=correlations(video,reference)
    changed=reference.copy()
    for start in range(800,6400,1600):changed[:,start:start+800]=rng.normal(size=(1,800))*100
    c,d=correlations(video,changed)
    assert np.array_equal(a,c) and np.array_equal(b,d)


def test_mtc_time_gap_and_empty_cut_are_rejected():
    from finalize_pilot import assess_mtc
    assert not assess_mtc(np.arange(0,2,.1),.1,1.1)[2]
    assert 'insufficient_mtc_rows' in assess_mtc(np.array([0.,4.]),1.,2.)[2]
    assert 'mtc_time_gap_exceeds_0.5s' in assess_mtc(np.array([0.,.1,.2,.3,1.8,1.9]),0.,2.)[2]
