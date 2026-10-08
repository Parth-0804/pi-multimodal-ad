# Recording and segment inventory

149 HDF5 recordings, 4863 high-level annotations; 10201 low-level annotations.

Actual key/shape/dtype schemas, full SHA256s, sensor rates, media metadata, quality
and per-recording warnings are in the versioned records/*.json files.
1 warning records; no undocumented schema coercion.

Primary camera: `hand`. Candidate microphone: `hand_audio`; audio is secondary
until its clock origin and drift can be independently verified.

{
  "primary_camera": "hand",
  "camera_usable_counts": {
    "hama1": 4550,
    "hama2": 4550,
    "hand": 4542
  },
  "candidate_microphone": "hand_audio",
  "audio_nominal_counts": {
    "hama1_audio": 4424,
    "hama2_audio": 4374,
    "hand_audio": 4551
  },
  "audio_primary_eligible": false,
  "audio_verified_counts": {
    "hama1_audio": 0,
    "hama2_audio": 0,
    "hand_audio": 0
  },
  "audio_reason": "Decoded sample clock lacks sufficient verified timing/support; primary audio deferred. Nominal zero-based quality measured using official visualization convention.",
  "selection_rule": "Coverage, decoding and overlap first; within 1 percentage point prefer wrist/hand proximity, otherwise lexical name; no model performance.",
  "cohort": "visual_sensor",
  "sensor_streams": [
    "measured_force",
    "measured_torque",
    "gripper_positions",
    "joint_efforts",
    "joint_velocities"
  ],
  "support": {
    "all_annotations": {
      "segments": 4863,
      "failures": 517,
      "successes": 4346,
      "recordings": 149,
      "failure_recordings": 131,
      "success_recordings": 149
    },
    "primary_actions": {
      "segments": 4551,
      "failures": 516,
      "successes": 4035,
      "recordings": 149,
      "failure_recordings": 131,
      "success_recordings": 148
    },
    "dual_complete": {
      "segments": 4530,
      "failures": 509,
      "successes": 4021,
      "recordings": 148,
      "failure_recordings": 130,
      "success_recordings": 147
    },
    "tri_complete": {
      "segments": 0,
      "failures": 0,
      "successes": 0,
      "recordings": 0,
      "failure_recordings": 0,
      "success_recordings": 0
    }
  }
}

Video quality uses 16 deterministic in-segment frames at 160x120 for brightness,
focus and motion proxies; it is not exhaustive frame-by-frame decoding. Sensor
quality uses in-segment finite data; MAD outliers are descriptive within-segment
quality, not globally fitted preprocessing. Clipping/SNR are null when no
defensible reference exists. Encoded media cache is outside Git.
