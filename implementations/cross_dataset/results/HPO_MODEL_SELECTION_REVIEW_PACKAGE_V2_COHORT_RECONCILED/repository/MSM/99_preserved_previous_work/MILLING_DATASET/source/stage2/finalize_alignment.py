#!/usr/bin/env python3
"""Choose the microphone by calibration support, then apply held-out timing checks."""
import argparse
import json
from pathlib import Path

import numpy as np

from align_audio import estimate_mapping
from audit_sensors import dump, csv_output


def main(run):
    config = json.loads((run / "config/resolved_config.json").read_text())
    protocol = json.loads((run / "config/alignment_protocol_final.json").read_text())
    primary = json.loads((run / "manifests/audio_alignment.json").read_text())
    final, anchors = {}, []
    for group in config["selected_groups"]:
        mapping = primary[group]
        if mapping.get("reason") == "no_video_provided":
            final[group] = mapping; continue
        reference = "audio_s2"
        rejected_candidates = []
        # The reference-channel choice uses calibration support, never validation labels or anomaly labels.
        if mapping.get("calibration_anchors", 0) < protocol["min_calibration_anchors"]:
            rejected_candidates.append({"reference": "audio_s2", "reason": "insufficient_calibration_anchors",
                                        "calibration_anchors": mapping.get("calibration_anchors", 0)})
            cache = np.load(run / "cache" / (group.replace("/", "_")+"_audio.npz"))
            mapping = estimate_mapping(cache["video_features"], cache["reference_features"], protocol)
            reference = "audio_s0"
        secondary_check = None
        if config.get("analysis_revision") == 2 and reference == "audio_s2":
            cache = np.load(run / "cache" / (group.replace("/", "_")+"_audio.npz"))
            secondary = estimate_mapping(cache["video_features"], cache["reference_features"], protocol)
            secondary_check = {"reference": "audio_s0", "mapping": secondary}
            if secondary.get("accepted"):
                disagreement = abs(secondary["offset_s"]-mapping["offset_s"])
                secondary_check["offset_disagreement_s"] = disagreement
                if disagreement > .10:
                    mapping = {**mapping, "accepted": False, "reason": "cross_microphone_alignment_disagreement"}
                else:
                    mapping = {**mapping, "uncertainty_s": max(mapping["uncertainty_s"], round(disagreement+.04,6))}
        final[group] = {**mapping, "reference": reference, "secondary_microphone_check": secondary_check,
                        "rejected_reference_candidates": rejected_candidates,
                        "reference_choice_policy": "prefer ambient S2; fall back to S0 only if S2 has fewer than three calibration anchors; validate after choice"}
        anchors.extend({"group_id": group, "reference": reference, **a} for a in mapping["anchors"])
        print(group, reference, mapping.get("accepted"), mapping.get("offset_s"), mapping.get("support_sensor_s"), flush=True)
    dump(run / "manifests/video_alignment_final.json", final)
    csv_output(run / "manifests/final_audio_alignment_anchors.csv", anchors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--run", type=Path, required=True); main(parser.parse_args().run)
