#!/usr/bin/env python3
"""Render the reviewed 2026-09-27 snapshot; reject different audit measurements.

Refuses overwrite. Reads derived tables only; never reads raw signals or trains.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pandas as pd


def write(path, content):
    with path.open('x') as f:
        f.write(content.rstrip() + '\n')


def markdown(frame, include_index=False):
    if include_index:
        frame = frame.reset_index()
    rows = [list(frame.columns)] + frame.astype(str).values.tolist()
    lines = ['| ' + ' | '.join(map(str, rows[0])) + ' |', '| ' + ' | '.join(['---'] * len(rows[0])) + ' |']
    lines.extend('| ' + ' | '.join(row) + ' |' for row in rows[1:])
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', required=True)
    args = ap.parse_args()
    run = Path(args.run)
    if hashlib.sha256((run / 'dataset_summary.json').read_bytes()).hexdigest() != 'e351309b117e3a9ed450f1a71e8d98be2749b0d9b6da3448c4908b12ac7301f7':
        raise ValueError('Snapshot differs: review report narrative before rendering')
    s = json.loads((run / 'dataset_summary.json').read_text())
    inv = pd.read_parquet(run / 'dataset_inventory.parquet')
    gates = json.loads((run / 'leakage_tests.json').read_text())
    disposition = json.loads((run / 'split_disposition.json').read_text())
    full = inv.groupby('CATEGORY').agg(samples=('SUBDIRS', 'size'), sessions=('session_id', 'nunique'))
    complete = inv[inv.complete_readable].groupby('CATEGORY').agg(readable=('SUBDIRS', 'size'), readable_sessions=('session_id', 'nunique'))
    table = full.join(complete).fillna(0).astype(int)
    categories = markdown(table, include_index=True)
    modality = markdown(pd.DataFrame([{'modality': m, 'present': int(inv['has_' + m].sum()),
        'missing_percent': round(s['missing_percent'][m], 2),
        'present_failing_probe': s['unreadable_present'][m]} for m in ['audio', 'video', 'sensor']]))
    csv_schema = ', '.join(json.loads(inv.sensor_columns.dropna().iloc[0]))
    evidence = f"Evidence directory: `{run.as_posix()}`. Manifest SHA256: `{s['manifest_sha256']}`."
    integrity = f'''# Dataset integrity and missingness

{evidence}

All {s['samples']} manifest rows and {s['sessions']} session directories were
inventoried. All on-disk modality files map to the manifest; no extra sample
directories or missing sample directories were found. Empty/incomplete sample
directories still count as manifest samples.

{modality}

All three deployable files exist for {s['complete_present']} samples (67.40%).
Structural readability probes pass for {s['complete_readable']} samples (67.00%).
This is an audit flag, not an approved exclusion rule. At least 1,333 samples
(33.00%) have a missing deployable file or fail a probe, exceeding the 5% trigger.
Class and session missingness tables were generated before any exclusion.

All present FLAC files were decoded and all CSVs parsed. All 113 available images
decoded. Video probes decode first/middle/last frames only: 16 files fail, all in
Porosity_w_Excessive_Penetration. OpenCV/FFmpeg also emitted damaged-block/VLC
warnings. Error concealment may return a frame; 2,707 probe passes do not certify
that every frame is undamaged. A full video decode has not been completed.

Only 24 samples have any post-weld images; 22 have five, one has one, and one has
two. The remaining 4,016 have none. Image availability is concentrated in Warping
(97 images) and Porosity_w_Excessive_Penetration (16). No Good sample has images;
an offline binary teacher is unsupported by this local copy.

## Label support and selective missingness

{categories}

The full manifest has Good 819/55 sessions and non-Good 3,221/181 sessions.
The readable subset has Good 819/55 sessions and non-Good 1,888/114 sessions.
Spatter, Undercut and Warping each retain only one session with deployable data.
Their absence is strongly class-dependent. A complete-case restriction changes
the target population and cannot be silently applied or generalized to all twelve
conditions. The local copy's incompleteness is not proof that the hosted dataset
is incomplete.

## Identity and duplicates

Full SHA256 was computed for all {s['file_count']} modality files
({s['file_bytes']:,} bytes); zero exact-byte duplicate groups were found, including
images. No exact duplicates cross the proposed dev/test boundary or CV folds.
Near-duplicates and re-encodings remain untested. Sample SUBDIRS are unique, but
20 basename identifiers occur in two different Overlap sessions (FE410 and BSK46).
Use `(session_id, sample_id)` or SUBDIRS as the primary key, not basename alone.
The differing materials and file hashes do not independently certify physical
session independence; retain this grouping question for researcher review.

## Measurement details

Audio: all 2,723 files are 16 kHz. Video: all are 960×600; 1,495 report 30 FPS
and 1,228 report 31 FPS. The 31 FPS files are deviations from nominal documentation,
not automatically corrupt. Sensor CSVs: {csv_schema}. All 2,725 parse, with
195–666 rows. Thirty-two files have invalid/nonmonotone timing; 68 adjacent steps
are nonpositive. Parsed numeric channels, constants, missing-cell counts, paths,
sizes and per-file errors are retained in the inventory. Part No, Date, Time and
Remarks must be excluded from predictors; relative time may be used for alignment.

Files: dataset_inventory.parquet, file_inventory.parquet, dataset_summary.json,
category_missingness.csv, session_summary.csv, duplicate_files.csv.
'''
    alignment = f'''# Temporal-alignment feasibility audit

{evidence}

Status: CONDITIONAL / NOT VALIDATED. No temporal cross-attention is enabled.
This is a structural feasibility audit, not a measured cross-modal alignment.
Envelope/lag estimation is deferred because the final-holdout gate has failed.

| measurement | median | range / caveat |
|---|---:|---|
| audio duration | 38.000 s | 25–38 s, 2,723 files |
| video duration | 35.800 s | 21–43.033 s, container metadata |
| sensor duration | 36.617 s | 21.794–188.344 s, 2,693 valid timestamp series |
| sensor nominal adjacent-step rate | 8.621 Hz | 8.621–9.091 Hz; not guaranteed uniform |
| absolute audio–video duration gap | 2.355 s | maximum 16.233 s |
| absolute audio–sensor duration gap | 1.659 s | maximum 150.344 s |
| absolute video–sensor duration gap | 0.449 s | maximum 154.215 s |

These gaps are not lag estimates. They can reflect clipping, duration differences,
recording starts/stops, sensor interruptions or metadata problems. Thirty-two
sensor series contain nonpositive timestamp steps and cannot safely be interpolated
without an explicitly reviewed policy. No interpolation, resampling, scaling,
trimming, offset correction or synchronization claim is made here.

After holdout recovery, specify a development-only test of RMS audio energy,
video arc/luminance/motion and current/voltage activity envelopes, timestamps,
common-grid resolution, admissible lag range, minimum overlap, peak sharpness,
flat-envelope handling, boundary rejection, confidence and session stability.
Predeclare thresholds before inspecting those results. Low-rate sensor data
limits temporal resolution. Validate the estimator on synthetic shifted and flat
signals. A measurable stable lag may justify temporal fusion; otherwise sample-
level fusion remains the permitted option after unimodal gates pass.

No estimated lags, confidence values or lag plots exist yet. Do not replace them
with duration differences. A feasibility audit alone cannot pass Gate 4.
'''
    label = f'''# Label, session, process and supplied-SPLIT audit

{evidence}

CATEGORY describes intended conditions, not expert-verified physical defects.
Every one of the 236 sessions has one category. Session sizes range from 1 to 20
(median 20). DIRECTORY is the documented grouping unit; within-session label
constancy reinforces the need for grouped evaluation.

{categories}

The supplied split has 576 TRAIN, 1,732 VAL and 1,732 TEST samples. A total of
216/236 sessions cross supplied splits; only 20 are confined to one split.
Reject this protocol for the primary and conditional secondary comparisons.
No model was evaluated on it in this pass.

All seven legitimate manifest process fields have complete category crosstabs
(`category_*.csv`). `session_category.csv` retains the full session–category map.
Every category occurs at one thickness: Good uses 7 mm; Burnthrough,
Excessive_Penetration and Porosity_w_Excessive_Penetration use 3 mm; the remaining
conditions use 7 mm. Thickness alone cannot separate all Good/non-Good samples,
but is an obvious recipe shortcut for some categories.

Across the full manifest, 164 of 175 distinct seven-field recipes map to one
category, and 11 map to two. In the complete-present subset, 122 of 125 recipes
map to one category. These are descriptive associations, not validated predictive
performance. No fields were selected or dropped based on model outcomes.

The prior context report contains model scores over the complete-present
population. Its script lacks a development-only filter. Do not reuse those
scores as valid development-only or final-test results. The current deliverable
is the unexecuted context specification in
`docs/intel_welding/context_baseline_specification.md`.
'''
    split_text = f'''# Proposed split disposition and holdout incident

The existing proposal has {disposition['n_dev_sessions']} development sessions
(2,191 samples) and {disposition['n_test_sessions']} final-test sessions
(532 samples), based on complete-present data. Its ID hash is
`{disposition['existing_id_hash']}`. Its full JSON SHA256 is
`{disposition['existing_split_sha256']}`. Original files remain unchanged.

Membership is session-disjoint; all five folds exclude proposed final sessions,
cover development, and separate train/validation groups. Full-content hashes
show no exact duplicate crossings. Multiclass coverage fails for single-session
categories: Spatter, Warping and Undercut each occur in a validation fold without
training support. No performance-based split search was performed by this audit.

**Disposition: INVALIDATED_FINAL_HOLDOUT.** The pre-existing context report
and code cover all 2,723 complete samples across all 169 eligible sessions,
including the 32 subsequently proposed final-test sessions. OOF predictions and
complete provenance are missing, so this is a conservative exposure finding from
saved evidence, not a reconstructed execution trace. No pristine-test claim is
credible. The new configuration and disposition keep `allow_final_test: false`.
This is an audit lock status; no general-purpose final-evaluation CLI is implemented.

A fresh random partition of the exposed sessions cannot restore independence.
All 55 Good sessions in the manifest already belong to that exposed population.
The 67 sessions without complete data contain no additional Good sessions;
finishing this local download alone cannot produce a pristine binary test cohort.
A clean test requires genuinely unexposed physical sessions with both classes,
or a researcher-approved development-only protocol that abandons untouched-test
claims. Do not silently choose the latter or claim an immutable valid split now.

Recommended exact next action: review the exposure record and decide whether to
obtain independent Good/non-Good sessions. Resolve the physical grouping of
colliding sample IDs and the missing/corrupt-file policy, then freeze a new
preregistered evaluation contract before training. Until then all modelling stays
blocked. No replacement split or new model was created.
'''
    gate_rows = [
      ('0 Data access','PASS','Local manifest plus representative audio/video/CSV/images readable; no credentials inspected or download attempted.','GATE_0_DATA_ACCESS.md','Inventory permitted; complete hosted access not asserted.'),
      ('1 Integrity','CONDITIONAL','2,707 probe-readable triplets; 1,317 missing audio/video; 16 failed video probes; 113 images.','dataset_integrity.md','Missingness analysis completed; population/repair policy unresolved.'),
      ('2 Label support','CONDITIONAL','55 Good and 114 non-Good sessions with triplets; three conditions have one session each.','label_session_process_audit.md','Binary support exists; full twelve-class evaluation unsupported locally.'),
      ('3 Split leakage / test protection','FAIL','Proposed 32-session holdout included in prior all-population context study; 216 supplied-split crossings.','split_disposition.md; leakage_tests.json','No modelling or final-test claims; no replacement seed search.'),
      ('4 Temporal alignment','CONDITIONAL','32 invalid timestamp series; median audio/video duration gap 2.355 s; lag unmeasured.','alignment_audit.md','Temporal cross-attention disabled; sample-level option only after other gates.'),
      ('5A Audio signal','CONDITIONAL','Not evaluated; 0 new models.','provenance.json','Blocked by Gate 3; no positive or negative signal conclusion.'),
      ('5B Video signal','CONDITIONAL','Not evaluated; 0 new models.','provenance.json','Blocked by Gate 3.'),
      ('5C Sensor signal','CONDITIONAL','Not evaluated; 0 new models.','provenance.json','Blocked by Gate 3.'),
      ('6 Fusion prerequisite','CONDITIONAL','0 modalities have validated development signal evidence.','provenance.json','Fusion prohibited; absence of evidence is not evidence of no signal.'),
      ('7 Gate input use','CONDITIONAL','No gated model or positive control run.','provenance.json','Not reached; no robustness interpretation.'),
      ('8 Robustness claim','CONDITIONAL','No clean/corrupted model comparisons.','provenance.json','Not reached; SQ3 remains unanswered.'),
      ('9 Final test unlock','FAIL','Holdout invalidated; allow_final_test=false.','split_disposition.json','No final evaluation; new preregistration and valid holdout required.')]
    gate_table = '| Gate | Status | Evidence / numbers | Files in run | Consequence |\n|---|---|---|---|---|\n' + '\n'.join('| ' + ' | '.join(row) + ' |' for row in gate_rows)
    report = f'''# Phase 1 foundation gate report

**Decision: NO-GO for unimodal modelling.** The primary blocker is prior
final-holdout exposure, compounded by selective missingness and unresolved
video/timestamp integrity. No model was trained in this pass. PHM work, raw data,
existing Intel outputs and the original proposed split were preserved.

{evidence}

## Repository audit

Starting HEAD: `ea4a76f64887fd590fd1f93cc83a726192dcfecb` on main, three commits
ahead of origin/main. That commit already contains the research contract and
separate Intel package directories. Ten untracked Intel files existed at entry:
three scripts, three audit files and four split files; an ignored inventory
parquet also existed. They were not overwritten or committed by this audit.
`docs/restructuring/TASKS.md` is referenced by policy but absent; no
`pyproject.toml` was found. Repository environment is available.

The first sandbox command failed during initialization; read/write commands ran
through approved escalation. No credentials, authentication session files or
PHM raw payloads were read. No downloads, package installs, extraction, raw writes,
model training or commits occurred. The user's current Intel request provides
the dataset-scope authorization; no PHM migration was performed.

## Delivered foundations

1. Repository protection/audit and committed-contract verification.
2. Local data access verified; see GATE_0_DATA_ACCESS.md.
3. All 4,040 rows inventoried; all 8,284 modality files fully hashed.
4. Full and readable-subset label/session support, process crosstabs and
   systematic missingness quantified.
5. Supplied SPLIT rejected: 216/236 sessions cross its partitions.
6. Existing proposed split audited and invalidated; evidence and IDs preserved.
   No scientifically valid replacement can be manufactured from exposed sessions.
7. Structural temporal feasibility measured; cross-modal lag estimation deferred.
8. Context-only baseline specified, not trained.

## Main measurements

{modality}

{categories}

Files with all deployable modalities: 2,723; passing structural probes: 2,707.
Only 22 samples have all five post-weld images. Zero exact-byte duplicate groups,
but 20 repeated basename IDs require composite keys and grouping review.
Sensor cadence median is approximately 8.62 Hz; video metadata reports 30/31 FPS.
Duration agreement is insufficient for alignment; 32 CSV timestamp series fail
monotonicity. All conclusions describe the present local copy.

## Protocol and interpretation

Use intended-condition terminology. Do not equate recipe prediction with
physical-defect detection. Read `label_session_process_audit.md` and
`docs/intel_welding/FOUNDATION_PROTOCOL_ADDENDUM.md` for corrected assumptions.
The public [Intel dataset card](https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset)
supports session grouping, intended-label caveats and the need to measure
synchronization; actual availability/rates above were measured locally.

The existing context scores are not used as valid results. They demonstrate a
protocol exposure problem, not a successful model comparison. All Good sessions
were included in the prior complete-population audit, so recovering missing
files cannot alone yield a pristine binary final test. See split_disposition.md.

## Checks and limits

Six synthetic tests passed: full hashing beyond the old prefix limit, timestamp
rollover/nonmonotonicity, safe paths, missing-modality flags, duplicate crossings
including images/CV, and overwrite refusal. Repository pip check passed. Full
video decoding, perceptual duplicates, physical grouping verification, alignment
lags, context retraining and any model comparison remain unperformed. This run
is traceable but not claimed to be clean-environment reproduction validated.
The initial audit invocation failed on relative-path handling before producing
inventory; its config-only run directory was retained, the bug fixed and the
full run succeeded in a fresh directory.

## Phase boundary and next action

New code: `04_foundations.py`, `05_foundation_report.py`, foundation config and
six synthetic tests. New documentation: protocol addendum, baseline specification,
foundation/failed-gate review and these versioned audit reports/tables/manifests.
Existing untracked work is retained. `git diff --stat` has no tracked-file changes;
new files are untracked and therefore absent from that statistic. No bulk outputs
were staged. The versioned run contains config, hashes and provenance.

Exact next action: researcher review of the holdout incident and choice of a
compliant recovery path, followed by explicit phase approval. Under AGENTS.md,
“Work one approved restructuring phase at a time” and “then wait for approval.”
This pause also follows the user's failed-gate and first-execution boundaries.
No dependent experiment will run before recovery and approval.

## Every gate

CONDITIONAL for future gates means **not evaluated / prerequisite unresolved**,
not a provisional pass.

{gate_table}

**NO-GO for unimodal modelling.**
'''
    access = f'''# Gate 0 — data access

PASS for local representative access, not for completeness.
Expected dataset: IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset.
Located at repository-relative `data/Full Dataset/`. Searched repository data
entries and workspace sibling directories; /mnt and /media contained no mounts.
Further searches/downloads were unnecessary once the copy was found.

Manifest is readable: 4,040 records, SHA256 `{s['manifest_sha256']}`.
Representative and subsequently all present audio/CSV/image files were readable;
video decode probes identified 16 failures. License file present: Intel Research
Use License Agreement. No authentication state was inspected or used; no network
payload download or acceptance of access terms occurred. The public dataset card
is accessible, while hosted payload access requires agreeing to conditions:
https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset

Blocker at Gate 0: none for local audit. Local completeness, video integrity,
physical grouping and holdout contamination are separate downstream blockers.
'''
    reports = {'dataset_integrity.md': integrity, 'alignment_audit.md': alignment,
        'label_session_process_audit.md': label, 'split_disposition.md': split_text,
        'GATE_0_DATA_ACCESS.md': access, 'PHASE_1_GATE_REPORT.md': report}
    for name, text in reports.items():
        write(run / name, text)
    # Top-level requested paths contain pointers; historical files are never replaced.
    base = Path('artifacts/intel_welding/audits')
    for name in ['GATE_0_DATA_ACCESS.md', 'PHASE_1_GATE_REPORT.md', 'dataset_integrity.md', 'alignment_audit.md']:
        write(base / name, reports[name] if name == 'PHASE_1_GATE_REPORT.md' else
              f'# {name.removesuffix(".md")}\n\n[Versioned audit report]({run.relative_to(base).as_posix()}/{name}).\n\nStatus and evidence are preserved in that run; existing historical outputs were not overwritten.')
    inventory = [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                 for p in sorted(run.iterdir()) if p.is_file()]
    write(run / 'report_output_manifest.json', json.dumps({'timestamp_utc': datetime.now(timezone.utc).isoformat(),
          'command': ['ma_thesis_env/bin/python', '-B', 'scripts/intel_welding/05_foundation_report.py', '--run', str(run)],
          'report_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'outputs': inventory}, indent=2))
    print(base / 'PHASE_1_GATE_REPORT.md')

if __name__ == '__main__':
    main()
