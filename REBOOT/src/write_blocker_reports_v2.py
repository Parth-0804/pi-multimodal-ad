"""Write new V2 reports from measured evidence; no modelling or historical edits."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[2]
BASE = PROJECT / 'REBOOT'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', required=True, type=Path)
    args = p.parse_args()
    run = args.run.resolve()
    relrun = str(run.relative_to(PROJECT))
    groups = json.loads((BASE / '06_evaluation_feasibility/VERIFIED_SPLIT_FEASIBILITY.json').read_text())
    package = json.loads((run / 'reports/VISUAL_PACKAGE_VALIDATION.json').read_text())
    usb = json.loads((run / 'reports/USBC_INDEPENDENT_IDENTITY_VERIFICATION.json').read_text())
    history = json.loads((run / 'reports/HF_HISTORY_SUMMARY.json').read_text())
    receipts = [json.loads(x) for x in (run / 'manifests/source_fetch_receipts.jsonl').read_text().splitlines()]
    space = shutil.disk_usage(PROJECT)
    allocated = int(subprocess.run(['du', '-sx', '-B1', str(BASE)], check=True, text=True, capture_output=True).stdout.split()[0])
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used,memory.total,utilization.gpu', '--format=csv,noheader'], text=True, capture_output=True).stdout.strip()
    gpu_processes = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv,noheader'], text=True, capture_output=True).stdout.strip()
    measurement = {'utc': datetime.now(timezone.utc).isoformat(), 'filesystem_free_bytes': space.free,
                   'REBOOT_allocated_bytes': allocated, 'budget_bytes': 40_000_000_000, 'reserve_bytes': 20_000_000_000,
                   'gpu_readonly_query': gpu, 'gpu_processes_readonly_query': gpu_processes,
                   'gpu_work_launched': False, 'training_interrupted': False}
    with (run / 'reports/RESOURCE_MEASUREMENT.json').open('x') as f:
        json.dump(measurement, f, indent=2)
    header = f'Investigation: `{relrun}`. Snapshot: {measurement["utc"]}. Original pilot and published bytes remain unchanged.\n\n'

    def report(rel, text):
        dest = BASE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('x') as f:
            f.write(text)
        mirror = run / 'reports' / rel
        mirror.parent.mkdir(parents=True, exist_ok=True)
        with mirror.open('xb') as f:
            f.write(dest.read_bytes())

    report('02_labels_and_annotations/ORIGINAL_SOURCE_HISTORY_AUDIT_V2.md', '# Original annotation sources and release history\n\n' + header + f'''
All 38 current Hugging Face heads match the original pilot pins. The new audit inspected {sum(e['history_count'] for e in history)} author-branch commits/trees across those repositories, their published tags/branches, and 37 automatic `convert/parquet` trees. HF responses had no remaining pagination links; trees were below the requested 1,000-entry limit. Converted branches contain episode data exports, not additional native annotations; the defective USB-C collection has no conversion branch. No unexpected root JSON/CSV/archive or metadata annotation candidate was left uninspected in these trees.

Only two historical annotation paths were located. They are identical bytes, not complementary coverage:

| Original source | Revision / path | Bytes | SHA-256 | Coverage |
|---|---|---:|---|---|
| [Current sample annotation](https://huggingface.co/datasets/REBOOT26/sample_recovery-demonstration/resolve/0633573d0438be1185bddebdf1a2c8f5505f7b2a/meta/phase.json) | `0633573d0438be1185bddebdf1a2c8f5505f7b2a`, `meta/phase.json` | 60,992 | `1d61ff591ff9f52628c49e71a0435ab83a62c87a4d607ae91a50478dbaf5813b` | 60 recovery records, episode IDs 00–59 |
| [Earlier root-level upload](https://huggingface.co/datasets/REBOOT26/sample_recovery-demonstration/resolve/56c6303fc95bd8d76c31fb39c3406e028f65f8a0/phase.json) | `56c6303fc95bd8d76c31fb39c3406e028f65f8a0`, `phase.json` | 60,992 | same SHA-256 | Same 60 records |

The earlier file was deleted in `b34ff92ee55142cb1a9f87b922bb97a84aeb704a`, then uploaded under `meta/`. The v3.0 tag predates both annotation uploads. No richer or corrected annotation revision was found. Raw historical responses and originals, URL/revision/size/hash receipts and per-repository histories are in this run's `evidence/history/`, `reports/history/`, `reports/HF_HISTORY_SUMMARY.json` and `manifests/source_fetch_receipts.jsonl`. Current files retain the earlier pilot's independent source receipts as well.

The author-linked [code fork](https://github.com/anon-robo-account/REBOOT) was inspected at depth `269d53958caf32913104c5a93f8ee4ed84704a0f` and main `a0e52d52fe7404cf392ebd538b96b36ad6cd7fc4`. Complete current trees, the nine depth-branch author commits relative to main, and all nine public patches reveal depth handling, trimming, visualization and generic upstream LeRobot SARM tooling; no REBOOT phase/session corpus or replacement index. The first 100 commits of each branch include upstream history and are retained; the entire unrelated upstream LeRobot history was not exhaustively searched. No tags, releases or fork issues provided a correction.

The [official project-site repository](https://github.com/NanaYawOA/REBOOT) at `0266140b29ae207c07c79a27a28ddf419fd22170` has 40 published commits: 39 complete trees plus the initial-commit patch, and 27 distinct historical README/index byte versions were inspected. They link the same dataset, fork and generic visualizer, with illustrative YouTube media rather than an annotation download. A public API 403 on the initial tree was resolved by reading its public patch: it only creates README.md. This was a network API limit, not a repository safety approval rejection.

An existing [open annotation request](https://github.com/NanaYawOA/REBOOT/issues/1) dated 2026-08-29 has zero comments at this snapshot and asks for the unreleased recovery annotations. This is corroborating community evidence, not an author correction or proof of private-source absence. USB-C HF discussions are empty; the sample's sole discussion is an automatic conversion notice. No message was sent and no issue was created.

The [official arXiv v1 source](https://arxiv.org/src/2609.22591v1) was downloaded (21,258,980 bytes; SHA-256 `0bdff6b88da98fe4df56dbf67bf1225e049d45587cb300bac0db8cf4b805edf0`). Its 20 archive members contain the paper, bibliography/style and illustrations, with no standalone annotation supplement. `main.tex` SHA-256 is `d3e74845d750206dbc020f9de28144a41a24e6d022b1d6433fda3861d7669bf5`; member names, bounded text and hashes are retained in `reports/PAPER_SOURCE_MEMBER_INVENTORY.json`. The current abstract lists v1 only. Its additional Drive link is explicitly Trossen assembly drawings/kinematic models, not REBOOT supervision; the public folder response was retained. The generic HF visualizer is an interface to the same datasets, not a separate annotation release.

The paper's Appendix example contains `t_f=210`, `t_r=420`, `t_s=612` for RCA episode 09, but is an illustrative listing with no dataset revision. The corresponding published RCA index says 898 rows while the listing declares 897. It is recorded separately in `reports/PAPER_ILLUSTRATIVE_ANNOTATION.json`, not counted as a verified extra episode label or used to fill sample fields. The paper distinguishes failure onset, first corrective action and successful continuation; these three events cannot be silently replaced with the sample's two differently named fields. [Definitions and example](https://arxiv.org/html/2609.22591v1#A3).

Search limits: this covers the named public author sources, reachable published revisions, article/source supplement and linked official documentation at the recorded snapshot. Unpublished/private annotations, detached/unadvertised commits and future corrections cannot be ruled out. No credentials or private sessions were read. Dataset cards say Apache-2.0 while the project/source text says CC-BY-4.0; licensing clarification remains separate from scientific label admission.
''')

    report('02_labels_and_annotations/USBC_METADATA_DEFECT_V2.md', '# USB-C metadata defect: identity partially resolved\n\n' + header + f'''
`REBOOT26/usbc_recovery_install` remains excluded from aligned supervised evaluation. Its published identity is now independently corroborated for 33 episodes; the corrupt original episode index was not repaired or replaced.

The three author revisions are current/tag v3.0 `0ef0b37f0601fbafcc3bab07195a1fb5e756c6b4`, initial data upload `d13a81e0b11e74ba30d82775126965ce9f811191`, and initial commit `dd78adcd42aa63b1226f1e41f07bc68334f91361`. The two revisions containing the index expose identical 196,608-byte LFS content, SHA-256 `c2edd7790273c14ba3ff63d7dbb1d0368d8ca3086503e66277c0edd3de2af160`. Neither contains a valid replacement. The original local file and previous parse/tail failure evidence are preserved. [Pinned index](https://huggingface.co/datasets/REBOOT26/usbc_recovery_install/blob/0ef0b37f0601fbafcc3bab07195a1fb5e756c6b4/meta/episodes/chunk-000/file-000.parquet).

New bounded reads inspect the actual `episode_index`, `frame_index`, `timestamp`, global `index` and `task_index` columns in every original `data/chunk-000/file-000.parquet` through `file-032.parquet`. All 33 parse successfully. They contain episode IDs 0–32, exactly 29,633 rows, zero-based contiguous frames within episodes, contiguous global indices 0–29,632 and strictly increasing finite native timestamps. These independently corroborate all 33 entries declared by `meta/info.json`. The maximum nominal 30 Hz residual is below one microsecond. Task index 0 is independently bound to the original tasks metadata; no phase, failure, operator or session annotations are present.

The published collection additionally contains `data/chunk-000/file-033.parquet` (291,766,272 bytes; official whole-file SHA-256 reference `4a14e0662e32208e022c8b409e55b22988218b756cc8afde80caed79df6ddebd`). Its separately fetched 65,536-byte tail also lacks a valid Parquet footer. Its identity/content cannot be admitted as a 34th episode. No depth arrays or full recording files were downloaded. This additional release defect is new evidence, not evidence that the first 33 data files are corrupt.

Total transfer for all 34 files: **{usb['total_range_bytes']:,} bytes**, capped at 1 MB per file; each request required exact HTTP206 status, Content-Range and byte count. Original fragments and their SHA-256s are retained in `evidence/usbc_identity_ranges/`. `reports/USBC_INDEPENDENT_IDENTITY_VERIFICATION.json` records every origin URL, revision, whole-file LFS reference, byte range, fragment hash, footer/column result and failure. Whole-file hashes of depth-heavy Parquets have **not** been independently recomputed; fragment hashes do not claim that verification.

Identity recovery does not restore the original four-camera video offsets, per-episode index statistics or missing annotation corpus. No corrected original index was synthesized. The separate `usbc_recovery_install2` release describes different original media and is not a replacement for this collection's identities. Excluding this collection reduces the alias-collapsed inventory ceiling from 2,076 to 2,043; both figures describe inventories, not eligible training examples (still zero). An author-supplied corrected index, clarification of file-033, original labels and recording/session bindings are needed for admission. Numeric-only timing diagnostics for the verified first 33 episodes can proceed with this explicit limitation.
''')

    report('02_labels_and_annotations/FINAL_TARGET_FEASIBILITY.md', '# Final normal/failure target feasibility\n\n' + header + '''
**NO-GO for the requested supervised abnormal-state versus normal-state experiment.** No additional authoritative label coverage or correction was located. Sixty authentic native recovery annotation records are verified as source bytes; zero normal windows, zero fully verified abnormal windows and zero matched pairs are admitted for training. Zero admitted examples means insufficient evidence, not absence of physical failures.

`VERIFIED_LABEL_COVERAGE.csv` enumerates all 2,136 repository episode entries, including 60 marked sample/full aliases. The 2,076 alias-collapsed inventory upper bound includes 33 USB-C identities verified from original numeric columns despite its corrupt episode index. It is not a download count or training cohort. The CSV keeps every binary target blank and verification false. Source identity, revision, annotation binding, metadata availability, grouping limits and exclusion reason remain explicit.

The one byte-distinct annotation file supplies 60 recovery records for one cylinder-install task: five phase names, six boundaries, native failure phase/mode/description, induction and recovery-start frames, and operator/session strings. All records are preserved. It supplies no independently defined per-frame success predicate, recovery-success frame, certified expert-phase normal interval, pair registry or annotation confidence. Earlier/current uploads have the same SHA-256. The paper's separate RCA listing is illustrative and revision-unbound; it is retained without adding a certified training record. See `ORIGINAL_SOURCE_HISTORY_AUDIT_V2.md` for pinned sources and hashes.

| Desired segment | Existing evidence | Admission |
|---|---|---|
| A: normal approach | Frames before induction can be located under an assumed frame convention | Not certified normal; approach can include a developing off-nominal condition, task/phase mismatch or incomplete phase success |
| B: failure state | Native induction frame and recovery-start frame exist | The proposed `[induction,recovery_start)` interval is not automatically the paper's `[t_f,t_r)`; onset semantics and contradictory records require clarification |
| C: recovery action | Recovery-start field and language description | End of corrective action / success transition is absent; cannot label the entire remainder as abnormal or normal |
| D: successful continuation | Narrative completion claims in descriptions | No machine-released success boundary; cannot delimit a valid continuation target |
| Expert normal control | Same-object expert-named recordings with RGB/state | No released expert phase bounds or independently verified clean phase success; collection membership does not certify every frame |

The paper's phase text uses one-based phases and an endpoint convention starting at one; its example starts at zero. The released sample starts at zero and declares duration 897 for actual 898/899-row recordings. Two native phase values (0 and 21), three induction/recovery-order violations and one nonmonotonic phase sequence remain uncorrected. Under a tested one-based occurrence interpretation, 38 onsets are outside the named phase. That is a semantic diagnostic, not proof that all 38 annotations are false. All 60 durations disagree with row counts. No offset/phase-number repair or truncation was applied.

Technical alignment and annotation correctness are separate. In the existing ten diagnostic demonstrations, original zero-based frame indices, elapsed state timestamps and pinned episode/video offsets support numerical-to-video lookup across all four views. Sixteen distinct selected frames per view give 640 decoded frames; the maximum nominal encoded-PTS residual is 1.22343 microseconds. This verifies the tested software mapping, not hardware exposure/feedback latency, event truth, or absolute collection time. Native induction/recovery values can be mapped as candidates within valid source bounds, but cannot be renamed as verified `t_f/t_r/t_s`; `t_s` is absent in the sample. No extrapolation to every remote episode is claimed.

The researcher-created alternative is a separately versioned retrospective visible-event annotation study: freeze task, camera, phase definition, causal/retrospective horizon and uncertainty rules; obtain independent reviewers for event onset, corrective action, success/clean control and visibility; retain provenance, disagreements and adjudication; do not overwrite original labels. Use fresh physically identified holdouts after developing that protocol on B001–B010. Such new labels would be human-derived, not original dataset ground truth. The present package prepares this work; no human annotation or validation was completed and no labels were invented from an LLM video interpretation.

The author clarification checklist is in `../07_research_decision/UNRESOLVED_EVIDENCE.md`. All requested modelling remains blocked until target, identity and visual-review gates pass.
''')

    report('02_labels_and_annotations/NORMAL_FAILURE_MATCHING_REPORT.md', '# Normal/failure matching assessment\n\n' + header + '''
No trustworthy matched normal/failure pair is currently established. The diagnostic pilot contains eight native-recovery candidates and two expert-collection candidates, all cylinder/install. Their source identities and exact windows are preserved in the original selection and separate review key; they are not ten binary-labelled examples.

| Matching variable | Evidence / remaining defect |
|---|---|
| Task and object | Cylinder-install is shared between sample recovery and expert candidates; other tasks lack machine-released phase/failure annotations |
| Phase | Recovery originating-phase candidates 1–4 have counts 14/13/4/14; onset-inside-phase diagnostic counts 2/12/3/5. Expert phase boundaries are absent; valid paired support is 0 in every phase |
| Camera | Same four camera keys, 640×480 and nominal 30 Hz for inspected examples; keys alone do not establish unchanged extrinsic calibration across sessions |
| Observation horizon | Diagnostic recovery windows include pre-induction and post-recovery-start context; expert candidates use whole episodes. Their durations differ and permit collection/phase/recovery-behaviour confounds |
| Physical collection / pairing | Recovery strings cover one dated session plus `initial`; expert sessions/pair IDs are absent. Equal episode numbers are not a matched pair |
| State measurements | Fourteen observed positions are available, distinct from fourteen commanded actions. Fixed feature extraction is technically possible but cannot create a target |

Do not train on the existing mismatched diagnostic windows. A future retrospective recognition protocol must freeze one window duration and index convention, compare the same object/task/phase/view and validate phase success for normal controls. If early warning is the intended endpoint, the observation horizon must end before the event and exclude recovery/future-action cues. Do not select per-class window lengths, camera crops or thresholds after examining holdout labels.

Exclude unresolved boundary/order records, unreviewed fine-contact or occluded events, missing expert phase controls, unresolved USB-C video offsets and unknown recording/pair bindings until corrected evidence is versioned. Record exclusion reasons rather than deleting source files. The original annotations are retained verbatim; no rejected record is silently repaired. Original-source absence and reviewer uncertainty are different statuses.

The human-derived alternative would require two independent reviewers, predefined normal/failure/uncertain criteria, time intervals with uncertainty, adjudication and agreement reporting. Negative windows must receive explicit clean phase-success verification. The prepared forty-row sheet collects visibility judgments; it is not by itself a complete binary event-annotation protocol or a replacement for physical-session metadata.
''')

    task_lines = '\n'.join(f"| {t['task_name_inference']} | {t['inventory_episodes']} | {t['roles_not_binary_labels'].get('expert_candidate', 0)} / {t['roles_not_binary_labels'].get('recovery', 0)} | {t['native_annotation_episode_aliases']} | 0 / 0 / {t['unknown_binary_targets']} |" for t in groups['task_inventory'])
    report('06_evaluation_feasibility/GROUP_INDEPENDENCE_AUDIT.md', '# Independent grouping audit\n\n' + header + f'''
**No scientifically admissible supervised split can be constructed.** The verified binary cohort has 0 examples, 0 positive, 0 negative and 0 eligible groups. The richer inventory now includes independently verified identities for the defective-index USB-C collection; it does not establish labels or physical independence.

Across all parseable original episode indexes, exact signatures combine the original four video LFS hashes, per-view start/end timestamps and episode length. There are exactly 60 alias clusters of size two: sample episodes 0–59 and the full cylinder-recovery copies. All 18 sample chunks are shared. No additional exact episode-signature alias was detected in the 2,103 parseable entries. The 33 independently recovered USB-C identities lack original video-offset metadata and cannot be included in that media-alias test. Alias-collapsed inventory ceiling: 2,076 (1,090 expert-name candidates and 986 recovery-name candidates; these are not class labels). Full numeric trajectory equality was not tested across this terabyte-scale release, so further repetitions/near-duplicates remain unknown.

There are {groups['shared_video_chunk_hashes']} original video hashes referenced by more than one episode identity. A connected-component audit binds all episodes sharing any camera's original chunk, including aliases, into {groups['original_chunk_components']} conservative components over parseable index entries. Different adjacent episodes in a shared media chunk are not necessarily duplicates; they must remain bound in a conservative source-chunk split unless actual physical recording boundaries are established. Component IDs are derived bookkeeping, not inferred collection sessions. USB-C's 33 identities are not assigned fabricated chunk groups. Evidence: run `reports/EXACT_EPISODE_MEDIA_ALIASES.json`, `ORIGINAL_CHUNK_COMPONENTS.json` and row-level coverage CSV.

Sixty unique annotated recordings carry two operator strings: `op-01`=58 and `op-00`=2. Native session strings are `2026-04-15`=59 and `initial`=1. `initial` is not a verified recording date/session. Two thousand sixteen other inventory identities have no session string. These strings do not establish independent physical acquisitions, and neither upload date, commit date, elapsed frame timestamp, task name nor local filename may substitute. Expert/recovery pair IDs and repeated-rollout identities are absent. Thus verified physical sessions and verified expert/recovery pairings are both 0, rather than a claim that all recordings came from one session.

The 18 task names below are object/direction normalization of repository/native descriptions. They are plausible task inventory groups, not sessions. Distinct language prompts are not automatically distinct physical tasks. Only one task has native machine-readable annotations; it still has no admitted binary classes.

| Inferred task | Inventory ceiling | Expert-name / recovery-name | Native annotated unique | Verified + / − / unknown |
|---|---:|---:|---:|---:|
{task_lines}

| Candidate protocol | Eligible examples (+/−) | Eligible groups | Every-fold class support | Overlap / conclusion |
|---|---:|---:|---|---|
| Session-disjoint | 0 (0/0) | 0 physical | Cannot evaluate: no folds | Physical overlap unknown; two native strings cannot establish independence |
| Task-disjoint | 0 (0/0) | 0 labelled; 18 inventory | Cannot evaluate: no folds | Task-name partition could have zero name overlap, physical overlap remains unknown |
| Leave one task out | 0 (0/0) | 0 labelled; 18 inventory | Each prospective task has 0 admitted positive and negative test examples; remaining tasks have 0 admitted train examples | No valid LOTO experiment; future task generalization claim differs from session generalization |
| 3 outer × 2 inner grouped CV | 0 (0/0) | 0 verified eligible | No outer/inner class support can be certified | No folds materialized, hence overlap is undefined rather than invented as zero |

`VERIFIED_SPLIT_FEASIBILITY.json` records counts and admission failures for all protocols plus each prospective held-out task's zero eligible class support. `per_fold_class_support` and actual fold overlap are null because no legitimate folds exist; zeros would falsely imply executed empty splits. No random frame split, substituted group identity, fold reduction or seed search was used. The 58 source-chunk components do not rescue absent labels or certify session independence.
''')

    report('06_evaluation_feasibility/PROPOSED_EVALUATION_PROTOCOL.md', '# Evaluation protocol after evidence resolution\n\n' + header + '''
Status: proposed only; no split IDs or modelling results are materialized.

1. Freeze a target specification with independently verifiable normal and abnormal intervals, source revision, phase semantics, inclusive/exclusive endpoints, event-success boundary, view and observation horizon. Resolve original-source defects or explicitly approve a separate human-derived visible-event study. Record uncertain/excluded cases. Original annotation bytes remain authoritative historical evidence.
2. Obtain a signed recording registry binding episode aliases, original chunks, operator, actual physical collection session/date, task/object, expert/recovery pair and repeated trajectories. Keep every window/view of a physical acquisition and its aliases/pairs in one group. Use source-chunk components as a conservative additional constraint, never as a session surrogate.
3. Treat B001–B010 as development examples exposed during feasibility work. Complete independent visual review, freeze camera/preprocessing and target eligibility before selecting fresh holdouts. Confirm that the target is visible at the chosen sensor/visual horizon.
4. Evaluate actual group/class support before any feature/model fitting. Prefer three outer folds with two group-disjoint inner folds only if both classes occur in every train, inner-validation and outer-test partition and enough independent groups remain. Assert alias, chunk, pair, recording and session disjointness appropriate to the claim; store class/group counts and zero known overlap for each executed partition. Reject the design if these assertions fail. Fixed seeds 42, 123, 20261023 do not repair insufficient support.
5. A valid alternative is a preregistered fresh-session holdout, with separate development sessions for fitting and group-aware inner OOF F2. Its test set and each OOF training/validation partition still require both classes. If fewer than the necessary class-supported independent groups exist, report descriptive visible-event evidence only; do not estimate supervised generalization. A future task-disjoint/LOTO design needs labelled normal and abnormal events in multiple tasks and states a task-generalization claim; operator/session overlap must remain disclosed.
6. If all gates pass: use the frozen pinned RT-DETR R18vd CNN backbone, last-three-map spatial means (896), sixteen-frame temporal mean and new 896→128→1 head. Build fourteen-feedback-channel features with mean, population standard deviation, RMS, min, max, peak-to-peak (84). Exclude action commands from the primary sensor branch. Fit standardization only on training data. Train a balanced logistic sensor model and a fixed stronger nonlinear sensor baseline; include prevalence, visual only and arithmetic probability averaging.
7. Fit F2 logistic late fusion using only genuine group-inner-OOF visual and sensor probabilities from the outer training set. No in-sample probabilities, pooled outer-test tuning, transferred source fusion coefficients or test threshold fitting. Generate outer predictions once after choices freeze. Define calibration/threshold use on training/OOF data before execution. Report AP/AUROC, prevalence, thresholded errors, per-group/seed outcomes and group-aware uncertainty only from actual held-out predictions.
8. Quality-aware/robustness experiments require sufficient extra OOF support, fixed label-free quality variables, exposure-matched static controls and explicit absent-branch fallback. Start with clean unimodal/averaging/F2 controls. Frozen CNN temporal averaging is order-invariant, so do not claim temporal-order modelling or force anomaly detection from joint positions. Collection-role recognition is a different, confounded endpoint and is not substituted here.

Compute and storage remain gates: use no busy REASSEMBLE GPU, interrupt no job, keep total REBOOT allocation below 40 GB and filesystem free space above 20 GB at every acquisition/training boundary. Under current evidence steps 1–4 remain blocked; only source curation, metadata/timing diagnostics and independent visibility review can proceed.
''')

    report('05_architecture_compatibility/FUSION_READINESS_V2.md', '# Fusion readiness after blocker investigation\n\n' + header + f'''
| Gate | Evidence | Status |
|---|---|---|
| Original target semantics | 60 source records, no new content in earlier upload, missing successful-continuation/normal-control labels | BLOCKED |
| Synchronized modalities | Prior ten-demo pilot: four views, 640 selected frames with sixteen distinct contents per view, 8,980 numeric rows, 14 observed positions; nominal encoded-time mapping verified | Technical pilot passes; hardware latency and semantic event mapping unverified |
| Example counts | 10 diagnostics; 2,076 inventory ceiling; 0 admitted binary windows | BLOCKED |
| Independent splits | Sample/full aliases bound; session/pair identities missing; no class-supported folds | BLOCKED |
| Visibility | Package ready; forty human example/view ratings blank | BLOCKED pending independent review |
| Storage | {allocated:,} allocated bytes in REBOOT; {space.free:,} bytes free at measured snapshot | PASS for bounded work; total 40 GB / reserve 20 GB respected |
| Compute | `{gpu}` | GPU occupied by existing REASSEMBLE work; protected, no GPU work launched |

Architecture portability was already established in the original compatibility report and actual repository sources. Reusing its 896-dimensional frozen CNN embedding and a new head, 84 observed-state statistics, logistic/strong nonlinear sensor baselines, averaging and train-OOF F2 is technically feasible. It is not a validated REBOOT experiment. All supervised branches, prevalence performance, clean/robustness F2 and quality-aware fitting remain stopped because their common target/split prerequisites fail. No CNN inference, classifier fit, fusion training, simulated score or empty model-performance table is produced.

Observed position can encode phase or human recovery behavior. A model must use the same frozen, appropriate horizon in both modalities; no command-as-measurement substitution, future recovery cues for early warning, or source-role target is authorized by this evidence. Existing source-domain negative/neutral fusion findings remain intact; architectural compatibility does not imply F2 improvement.
''')

    unresolved = '''
| Evidence needed | Current observation | Exact resolution needed / affected work |
|---|---|---|
| Complete original annotation release | One byte-distinct 60-record cylinder sample; no richer history/supplement found | Author-published revision-pinned phase/failure/expert-normal corpus and episode registry; all supervised models blocked |
| Frame/phase convention | Native durations 897 vs 898/899 rows; phases 0 and 21; one nonmonotonic sequence | Explain frame count vs last index, zero/one origin, exclusive/inclusive endpoints, invalid IDs and any trim-induced offsets; preserve correction history |
| Onset/recovery semantics | Sample has induction/recovery-start; paper illustrates onset/recovery/success | Author mapping of native fields to event definitions; supply success frame and resolve three order contradictions and 38 occurrence-interpretation discrepancies |
| Trustworthy clean controls | Expert name/success narrative lacks phase windows | Released expert phase success bounds or a separate reviewer-signed human target protocol; no all-expert-normal shortcut |
| Physical independence | 60 annotation records have 59 dated strings + one `initial`; 2,016 inventory episodes have none | Actual session/date/operator/acquisition/pair registry and repeats; no use of upload dates as collection dates |
| USB-C episode index | Two published copies have identical corrupt bytes | Corrected original four-view offset/index file; clarify corrupt data file-033. Numeric IDs 0–32 are independently corroborated, but aligned supervised use remains excluded |
| Visual observability | Four views decoded; no completed independent human review | Fill forty blinded rows, record reviewer identity/uncertainty, then unblind. An LLM opinion is not a completed human review or original ground truth |
| Cohort accounting | 2,136 entries, 60 known aliases, ceiling 2,076 vs advertised 2,160 | Author accounting of missing/repeated/extra records, task coverage and recording identities; do not pad the cohort |
| Source licence | Cards Apache-2.0 vs project/source CC-BY-4.0 | Author clarification for use/distribution beyond the present local evidence package |
| Hardware timing / state units | Nominal elapsed mapping; position names without channel-unit/calibration registry | Document acquisition clocks, exposure/feedback latency, calibration and units before physical/early-warning interpretation |

No author was contacted in this task. These are precise handoff requests, not inferred corrections. Lack of a public file in the searched snapshot is not proof it never existed privately. No additional model run is currently supported. Keep the entire original pilot, all negative findings, the corrupt files and new source fragments.
'''
    report('07_research_decision/UNRESOLVED_EVIDENCE.md', '# Remaining research evidence\n\n' + header + unresolved)

    report('07_research_decision/REBOOT_RESEARCH_DECISION_V2.md', '# REBOOT research decision V2\n\n' + header + f'''
**NO-GO for the requested supervised normal/abnormal multimodal fusion evaluation on the verified public evidence.** Source curation, bounded numeric/video timing diagnostics and an independent visibility review can continue. This is stricter than the original pilot's CONDITIONAL GO for investigation: the additional investigation did not resolve the mandatory target and independence gates. It is not a claim that REBOOT has no research value.

New evidence resolves the annotation-history question: all 38 dataset heads are unchanged; 139 author revisions, 37 conversion trees, author-code changes, 40 project-site commits and the actual arXiv source supplement yielded no extra machine-readable label corpus. The earlier root-level phase upload has exactly the same 60,992 bytes and SHA-256 as current `meta/phase.json`. The paper's RCA illustration is retained separately, without assuming that its example is release-bound ground truth. An existing public annotation request has no author response at this snapshot.

The defective USB-C index has no valid published revision. However, exact original numeric-column reads independently verified episode IDs 0–32 and all 29,633 frames using only {usb['total_range_bytes']:,} transferred bytes. A further original data Parquet, file-033, has an invalid footer. Four-view offset metadata and all native supervision for that collection remain missing; it stays out of aligned supervised use. No index was synthesized and no original bytes were modified.

Inventory is now 2,136 identity-backed repository entries (2,103 parseable original indexes plus 33 numeric corroborations), with 60 exact sample/full media aliases. The remaining ceiling is 2,076, not a proof of full uniqueness or a local download total. Only 60 unique cylinder-install episodes have the released annotation file. There are **0 admitted abnormal windows, 0 normal windows, 0 matched pairs and 0 eligible supervised groups**. Native operator/session strings and 18 task inventory names do not certify physical independence. No valid three-outer/two-inner, session-disjoint or task-disjoint supervised folds can be materialized.

The independent-review ZIP is ready: **{package['blinded_archive']['bytes']:,} bytes**, 80 full/context contact sheets, 640 larger region frames, 40 motion previews, 10 sensor timelines, forty blank human review rows and offline HTML. Its SHA-256 is `{package['blinded_archive']['sha256']}`. Source identities and native labels are withheld from that main ZIP and supplied in the separate `INDEPENDENT_VISUAL_REVIEW_UNBLINDING.zip` and expanded `UNBLINDING/` directory. All 640 copied region-frame hashes match the existing pilot manifest. Independent human review remains pending; no certified camera ranking or visibility rate is claimed. Coarse motion can be inspected in wrist/full views; fine contact/occlusion requires actual review and may remain uncertain.

The frozen R18vd CNN/head, observed-position statistics/classifier, stronger sensor control, averaging and genuine OOF F2 are technically portable. Their target, group and visual-review gates fail. **No training, CNN feature computation, fusion fitting, robustness evaluation or performance estimation was performed. No empty or simulated performance results were created.** Existing REASSEMBLE GPU training was observed only and remained running.

Resource snapshot: REBOOT allocation {allocated:,} bytes ({allocated/1e9:.3f} GB), filesystem free {space.free:,} bytes ({space.free/1e9:.3f} GB), well within the 40 GB total REBOOT budget and 20 GB reserve. Full remote release is about 1.014 TB and cannot fit the budget. No bulk dataset or model download was needed. Final post-validation storage is recorded in the run's `validation.json`.

The next concrete step is to complete the prepared independent review and obtain the source corrections/recording registry listed in `UNRESOLVED_EVIDENCE.md`, or explicitly establish a separately named human-derived annotation study. Reassess the gates after that evidence exists; current labels must not be manufactured to enable modelling.
''')

    report('07_research_decision/RESEARCHER_HANDOFF_V2.md', '# Researcher handoff V2\n\n' + header + f'''
1. **Missing original annotations located?** No additional content. The earlier phase upload is identical to the known file; current/historical official datasets, project/code and source supplement expose no complete original annotation corpus. A paper illustration is separately preserved, not promoted to labels.
2. **Trustworthy normal/abnormal windows?** No. The admitted counts are 0 normal, 0 abnormal and 0 matched pairs. Native recovery and expert-name membership do not define frame-level classes.
3. **Original event timestamps mapped to both modalities?** The ten-demo software mapping of native frame/time to four RGB views and observed positions is verified by the original pilot. Candidate induction/recovery values can be located under stated conventions, but semantic correspondence to onset/recovery/success remains unresolved and the sample has no success timestamp. Hardware latency is unverified.
4. **Valid examples?** Ten diagnostic demonstrations, 640 selected RGB frames and 8,980 numeric rows are locally reviewed technically. Release inventory has 2,136 entries and a 2,076 alias-collapsed ceiling; this includes 33 newly corroborated USB-C numeric identities. None is currently admitted as a binary model example. The USB-C collection remains excluded from aligned supervised use; file-033 has an additional invalid-footer defect.
5. **Independent groups?** Zero verified eligible physical groups. Metadata contains two operator strings, two session strings (one `initial`) on 60 unique annotated episodes, eighteen inferred task names across the inventory and 58 conservative shared-media components over parseable entries. These different counts must not be substituted for physical independence.
6. **Grouped evaluation possible now?** No supervised protocol passes. See `VERIFIED_SPLIT_FEASIBILITY.json` for counts, unknown overlap and per-task absence of class support. A future fresh-session holdout with valid group-OOF development support is a defensible alternative if a 3×2 design remains unsupported.
7. **Useful camera views?** All four views are technically available. The right-wrist view contains inspectable coarse motion in existing preliminary material, but no human-certified ranking exists. Fine mating/contact and occlusions remain uncertain. Obtain independent ratings from the portable package before choosing a camera or asserting target observability.
8. **Can the architecture legitimately be tested?** Technical adaptation is possible; a supervised scientific test is blocked by targets, independence and outstanding visual review. Observed joint/gripper position is the sensor domain, not measured force/torque.
9. **Which experiments may proceed under established evidence?** Public-source/metadata curation, bounded identity/timing diagnostics and independent visibility assessment. No supervised visual, sensor, prevalence-performance, averaging, F2 or quality-aware model run. A human-derived target study is a separate possible protocol requiring its own frozen definitions and completed annotations.
10. **Final research decision?** NO-GO for the requested supervised experiment; source investigation and review preparation are complete. No models were trained and there are no new performance results.

Open `../08_visual_examples_and_eda/INDEPENDENT_VISUAL_REVIEW_PACKAGE/index.html` or upload the main review ZIP ({package['blinded_archive']['bytes']/1e6:.1f} MB). Keep `INDEPENDENT_VISUAL_REVIEW_UNBLINDING.zip` and expanded `UNBLINDING/` private until the reviewer saves the forty-row sheet. An independent ChatGPT/LLM assessment must be labelled as such and does not satisfy a human-review requirement.

Deliverables:

- `REBOOT/07_research_decision/REBOOT_RESEARCH_DECISION_V2.md`
- `REBOOT/07_research_decision/RESEARCHER_HANDOFF_V2.md`
- `REBOOT/02_labels_and_annotations/FINAL_TARGET_FEASIBILITY.md`
- `REBOOT/02_labels_and_annotations/VERIFIED_LABEL_COVERAGE.csv`
- `REBOOT/02_labels_and_annotations/NORMAL_FAILURE_MATCHING_REPORT.md`
- `REBOOT/06_evaluation_feasibility/GROUP_INDEPENDENCE_AUDIT.md`
- `REBOOT/06_evaluation_feasibility/VERIFIED_SPLIT_FEASIBILITY.json`
- `REBOOT/06_evaluation_feasibility/PROPOSED_EVALUATION_PROTOCOL.md`
- `REBOOT/08_visual_examples_and_eda/INDEPENDENT_VISUAL_REVIEW_PACKAGE.zip`
- `REBOOT/08_visual_examples_and_eda/INDEPENDENT_VISUAL_REVIEW_UNBLINDING.zip`
- `{relrun}/` (public-source bytes, hashes, ranges, report snapshots, configuration, source, validation)

All previous REBOOT files and unrelated work are preserved. No source dataset was deleted or rewritten, no REASSEMBLE job was interrupted, and nothing was staged or committed. Remaining author/researcher evidence is itemized in `UNRESOLVED_EVIDENCE.md`.
''')
    print(json.dumps(measurement, indent=2))


if __name__ == '__main__':
    main()
