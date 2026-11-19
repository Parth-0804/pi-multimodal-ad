#!/usr/bin/env python3
"""Join timing, visual review, and fixed-channel statistics into the final pilot cohort."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from audit_sensors import COMMON_MTC, csv_output, dump


def assess_mtc(times, start, end, min_samples=5, max_gap=.5):
    inside = times[(times >= start) & (times < end)]
    gap = float(np.diff(np.r_[start, inside, end]).max())
    reasons = []
    if len(inside) < min_samples: reasons.append("insufficient_mtc_rows")
    if gap > max_gap: reasons.append("mtc_time_gap_exceeds_0.5s")
    return len(inside), gap, reasons


def main(run):
    cfg = json.loads((run / "config/resolved_config.json").read_text()); raw = Path(cfg["data_root"])
    contract = json.loads((run / "config/quality_contract.json").read_text())
    frame = json.loads((run / "manifests/frame_contract.json").read_text())
    sensor = json.loads((run / "manifests/sensor_audit.json").read_text())
    mapping = json.loads((run / "manifests/video_alignment_final.json").read_text())
    visibility = json.loads((run / "manifests/visibility_review.json").read_text())
    stats = pd.read_csv(run / "manifests/sensor_interval_statistics.csv")
    mtc = {g: pd.read_csv(next((raw / g).glob("*_mtc.csv"))) for g in cfg["selected_groups"]}
    rows, feature_rows = [], []
    for rec in frame:
        group, interval_id = rec["group_id"], rec["interval_id"]
        problems = list(rec["reasons"])
        if interval_id in visibility["context_visibility_rejections"]: problems.append("visual_context_not_recognizable")
        subset = stats[(stats.interval_id == interval_id) & (stats.modality == "mtc")]
        n, gap, mtc_problems = assess_mtc(mtc[group].time.to_numpy(), rec["start_s"], rec["end_s"],
                                       contract["minimum_finite_samples_per_channel"],contract["maximum_within_cut_mtc_gap_s"])
        if set(subset.channel) != set(COMMON_MTC): mtc_problems.append("common_mtc_schema_absent")
        if len(subset) and (subset.n.min() < contract["minimum_finite_samples_per_channel"] or subset.missing.sum()):
            if "insufficient_mtc_rows" not in mtc_problems: mtc_problems.append("missing_or_nonfinite_mtc_values")
        primary = rec["accepted"] and not problems and not mtc_problems
        acc_rows = stats[(stats.interval_id == interval_id) & (stats.modality == "acc")]
        acc_eligible = bool(rec["accepted"] and not problems and set(acc_rows.channel) == {"acc0","acc1"} and acc_rows.n.min() >= 5 and acc_rows.missing.sum() == 0)
        label_path = raw / group / "label.csv"
        m = mapping[group]
        row = {"dataset_id":8392825,"dataset_version":2,"dataset_handle":cfg["handle"],"group_id":group,
               "machine":group.split("/")[0],"experiment":group.split("/")[1],"source_row":rec["source_row"],"interval_id":interval_id,
               "native_label":rec["native_label"],"start_s":rec["start_s"],"end_s":rec["end_s"],
               "label_file":str(label_path),"label_file_sha256":hashlib.sha256(label_path.read_bytes()).hexdigest(),
               "video_file":str(next((raw/group).glob('*.mp4'),'')),"video_minus_sensor_s":m.get('offset_s',''),
               "alignment_reference":m.get('reference',''),"alignment_uncertainty_s":m.get('uncertainty_s',''),
               "frame_contract_pass":rec["accepted"],"selected_frames":16 if rec["accepted"] else 0,
               "frame_indices_json":json.dumps(rec.get('indices',[]) if rec["accepted"] else []),
               "video_pts_s_json":json.dumps(rec.get('video_pts_s',[]) if rec["accepted"] else []),
               "mapped_sensor_pts_s_json":json.dumps(rec.get('sensor_pts_s',[]) if rec["accepted"] else []),
               "frame_temporal_coverage_fraction":rec.get('temporal_coverage_fraction',''),
               "visibility":"partial_coolant_occlusion_context_recognizable" if rec["accepted"] else 'not_eligible_for_visual_pair',
               "mtc_rows_inside_cut":n,"mtc_max_coverage_gap_s":gap,"common_mtc_sensor_gate_pass":not mtc_problems,
               "verified_multimodal_example":bool(primary),"primary_exclusion_reasons":";".join(problems+mtc_problems),
               "separate_video_acc_contract_pass":acc_eligible,"do_not_mix_sensor_contracts":True}
        rows.append(row)
        if primary:
            vector = {"interval_id":interval_id,"group_id":group,"native_label":rec['native_label']}
            for channel in COMMON_MTC:
                v = subset[subset.channel == channel].iloc[0]
                for stat in contract["stats"]:vector[channel+'__'+stat] = float(v[stat])
            assert all(np.isfinite(v) for k,v in vector.items() if '__' in k)
            feature_rows.append(vector)
    csv_output(run / "MSM_PILOT_SAMPLE_MANIFEST.csv",rows)
    csv_output(run / "manifests/common_mtc_statistics.csv",feature_rows)
    counts = {}
    for g in cfg['selected_groups']:
        subset = [r for r in rows if r['group_id']==g]; admitted=[r for r in subset if r['verified_multimodal_example']]
        counts[g] = {'native_intervals':len(subset),'frame_contract_pass':sum(r['frame_contract_pass'] for r in subset),
                     'verified_multimodal_examples':len(admitted),'excluded':len(subset)-len(admitted),
                     'class_counts':dict(collections.Counter(r['native_label'] for r in admitted)),
                     'separate_video_acc_examples':sum(r['separate_video_acc_contract_pass'] for r in subset)}
    summary={'recommendation':'LIMITED GO','primary_contract':'16 ordered aspect-corrected RGB frames plus a fixed 90-value vector (15 common MTC channels x six statistics)',
             'pilot_intervals':len(rows),'frame_contract_pass':sum(r['frame_contract_pass'] for r in rows),
             'verified_multimodal_examples':sum(r['verified_multimodal_example'] for r in rows),
             'excluded_primary_examples':sum(not r['verified_multimodal_example'] for r in rows),
             'primary_class_counts':dict(collections.Counter(r['native_label'] for r in rows if r['verified_multimodal_example'])),
             'primary_positive_experiment_groups':sorted({r['group_id'] for r in rows if r['verified_multimodal_example'] and r['native_label']==1}),
             'separate_video_acc_examples':sum(r['separate_video_acc_contract_pass'] for r in rows),
             'separate_video_acc_class_counts':dict(collections.Counter(r['native_label'] for r in rows if r['separate_video_acc_contract_pass'])),
             'by_group':counts,'exclusion_reason_counts_nonexclusive':dict(collections.Counter(x for r in rows if not r['verified_multimodal_example'] for x in r['primary_exclusion_reasons'].split(';') if x)),
             'warning':'Counts verify data construction and coarse scene context, not label visibility, causal signal information, independent physical trials, or classifier performance.',
             'no_training':True}
    dump(run / "manifests/pilot_summary.json",summary);print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);main(parser.parse_args().run)
