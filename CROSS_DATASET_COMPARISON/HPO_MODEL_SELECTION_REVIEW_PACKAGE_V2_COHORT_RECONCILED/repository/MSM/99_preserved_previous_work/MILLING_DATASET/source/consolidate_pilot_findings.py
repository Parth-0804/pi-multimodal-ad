"""Copy compact evidence without changing authoritative historical files."""
import json
import os
from pathlib import Path

from prepare_full_lab import sha256,write


def consolidate(final,cfg,summary,decision):
    root=Path('MILLING DATASET/PILOT_FINDINGS')
    root.mkdir(exist_ok=False)
    stages=[
      ('01_DATASET_AND_LABEL_AUDIT',Path(cfg['stage1']),
       ['MSM_STAGE1_ACQUISITION_REPORT.md','MSM_LABEL_AUDIT.md','MSM_FILE_AVAILABILITY.md',
        'manifests/experiment_summary.csv','manifests/reference_date_groups.csv','manifests/audit_summary.json']),
      ('02_VIDEO_ALIGNMENT_AND_MODALITIES',Path(cfg['stage2']),
       ['MSM_STAGE2_MODALITY_AUDIT.md','MSM_VIDEO_ALIGNMENT_REPORT.md','METHODOLOGY_CORRECTION.md',
        'config/alignment_protocol_final.json','config/quality_contract.json','manifests/pilot_summary.json',
        'manifests/visibility_review.json','manifests/native_video_audit.json']),
      ('03_ARCHITECTURE_IMPLEMENTATION_SMOKE',Path(cfg['stage3']),
       ['MSM_STAGE3_EXPERIMENT_PROTOCOL.md','MSM_ARCHITECTURE_ADAPTATION.md','MSM_IMPLEMENTATION_VALIDATION.md',
        'config/protocol_lock.json','manifests/readiness.json','manifests/smoke_validation.json']),
      ('04_BLOCKED_EVALUATION_AND_TRANSFER',Path(cfg['stage4']),
       ['MSM_STAGE4_MODEL_RESULTS.md','MSM_CNN_WEIGHT_TRANSFER.md','MSM_GENERALIZATION_EVALUATION.md',
        'manifests/cohort_by_experiment.csv','manifests/split_gate.json','manifests/execution_status.json']),
      ('05_FULL_LABORATORY_FEASIBILITY',final,
       ['MSM_FULL_LAB_COHORT_AUDIT.md','MSM_ALIGNMENT_FEASIBILITY_REPORT.md','MSM_INDEPENDENCE_AND_SPLIT_GATE.md',
        'MSM_RESEARCH_DECISION.md','REVIEW_HANDOFF.md','manifests/cohort_summary.json',
        'manifests/split_feasibility.json','manifests/experiment_summary.csv'])]
    entries=[]
    for sub,authoritative,names in stages:
        dest=root/sub;dest.mkdir()
        for name in names:
            source=authoritative/name
            if not source.exists():continue
            target=dest/name
            item={'authoritative_path':str(source),'source_sha256':sha256(source),'bytes':source.stat().st_size,
                  'index_relative_path':os.path.relpath(source,dest)}
            if source.stat().st_size<=750_000:
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as f:f.write(source.read_bytes())
                assert sha256(target)==item['source_sha256']
                item.update(copied_to=str(target),status='verbatim_copy')
            else:item['status']='index_only_large_artifact'
            entries.append(item)
        # Authoritative original location also resolves internal links in verbatim report copies.
        text=f'# {sub.replace("_"," ")}\n\nAuthoritative run: [{authoritative.name}]({os.path.relpath(authoritative,dest)}).\n\n'
        text+='Copies are byte-identical snapshots. Relative links embedded in copied historical reports were preserved; use the authoritative run for those links.\n\n'
        for item in entries:
            if str(item['authoritative_path']).startswith(str(authoritative)+'/'):
                text+=f'- [{Path(item["authoritative_path"]).name}]({item["index_relative_path"]}) — SHA-256 `{item["source_sha256"]}`.\n'
        (dest/'SOURCE_INDEX.md').write_text(text)
    # Compact native-geometry contact sheets for all new experiments; previous pilot atlases indexed.
    metadata=json.loads((final/'manifests/metadata_relationships.json').read_text())
    diagnostics=root/'05_FULL_LABORATORY_FEASIBILITY/diagnostics';diagnostics.mkdir()
    diag_index='# Representative visual diagnostics\n\nNew contact sheets preserve display aspect ratio. They are samples for review, not a certification of interval visibility or anomaly observability.\n\n'
    for m in metadata:
        group=m['machine']+'/'+m['experiment'];paths=[Path(p) for p in m['representative_diagnostic_paths']]
        diag_index+=f'- **{group}**: '
        for n,source in enumerate(paths):
            item={'authoritative_path':str(source),'source_sha256':sha256(source),'bytes':source.stat().st_size}
            if n==0 and source.stat().st_size<=750_000:
                target=diagnostics/(group.replace('/','_')+source.suffix)
                with target.open('xb') as f:f.write(source.read_bytes())
                item.update(copied_to=str(target),status='verbatim_diagnostic_copy')
                diag_index+=f'[contact sheet]({os.path.relpath(target,diagnostics)}); '
            else:
                item['status']='index_only_diagnostic'
                diag_index+=f'[original {n+1}]({os.path.relpath(source,diagnostics)}); '
            entries.append(item)
        diag_index+='\n'
    (diagnostics/'README.md').write_text(diag_index)
    # Large interval/frame tables and raw media are referenced, never copied.
    for name in ['MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv','MSM_DOWNLOAD_MANIFEST.csv','manifests/selected_frame_manifest.csv','manifests/common_mtc_statistics.csv']:
        p=final/name;entries.append({'authoritative_path':str(p),'source_sha256':sha256(p),'bytes':p.stat().st_size,
             'status':'index_only_table','index_relative_path':os.path.relpath(p,root)})
    write(root/'SOURCE_PROVENANCE.json',{'self_excluded':True,'entries':entries})
    primary=summary['targets']['stable_negative'];counts=primary['class_counts']
    new=summary['acquisition']
    readme=f'''# MSM pilot findings

**Current decision: {decision}.** Full laboratory data validation is complete; model evaluation remains unperformed. Read the [research decision](05_FULL_LABORATORY_FEASIBILITY/MSM_RESEARCH_DECISION.md) and [researcher handoff](05_FULL_LABORATORY_FEASIBILITY/REVIEW_HANDOFF.md) first.

MSM was selected as an independent milling domain with native interval annotations, laboratory video and synchronized sensor recordings. It can test portability of the REASSEMBLE architecture and, later, trained CNN weights. Its existence alone provides no evidence of successful transfer, fusion benefit or missing/corrupted-modality robustness.

The official dataset has 69 experiment folders: 37 VM20i, 19 VMX30Ui and 13 industrial VF10. The 56 laboratory folders contain 2,512 native cuts: 1,877 label 0, 458 label 1 and 177 label 2. Label 2 means stable cutting with a defective tool; the primary frozen target is intervention-worthy cutting abnormality (1 versus 0/2), with a separate 1-versus-0 sensitivity. Dataset: `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`.

| Evidence stage | What was established | Scientific status |
| --- | --- | --- |
| [1: dataset and labels](01_DATASET_AND_LABEL_AUDIT/SOURCE_INDEX.md) | Official identity/version, all 69 label files and native meanings | Completed audit |
| [2: alignment and modalities](02_VIDEO_ALIGNMENT_AND_MODALITIES/SOURCE_INDEX.md) | Corrected label-blind audio synchronization; 116 timing/frame-valid and 114 paired pilot intervals | Completed restricted pilot; no predictive result |
| [3: architecture and smoke](03_ARCHITECTURE_IMPLEMENTATION_SMOKE/SOURCE_INDEX.md) | 16-frame CNN and 90-statistic sensor adapters, new heads and leakage-safe F2 pipeline work | Bounded development smoke only; no independent efficacy evidence |
| [4: evaluation and transfer](04_BLOCKED_EVALUATION_AND_TRANSFER/SOURCE_INDEX.md) | Evaluation correctly stopped: two positive pilot groups could not support three outer folds; completed canonical R source was absent | Failed prerequisites; zero held-out results, not a negative ML finding |
| [5: full laboratory feasibility](05_FULL_LABORATORY_FEASIBILITY/SOURCE_INDEX.md) | {new['new_files']} additional minimal files; {summary['joint_technical_pass']} paired technically eligible intervals; date/session and visibility limitations audited | Completed data audit; future model experiments require review |

The current joint technical cohort has **{summary['joint_technical_pass']} intervals**: {counts.get('0',0)} native 0, {counts.get('1',0)} native 1, {counts.get('2',0)} native 2; **{primary['groupings']['group_id']['groups']} nominal folders**, **{primary['groupings']['group_id']['positive_groups']} positive-containing folders**. Technical eligibility is not evidence that an anomaly is optically observable. Independent visibility review remains pending for all these examples; the original pilot has only the previously documented Codex coarse-context review.

The partial-overlap correction is essential: VMX30Ui/dataset9 uses **+49.73 s**, not the rejected exploratory +16.04 s alias. The corrected calibration-template estimator uses independent withheld anchors and support limits. See the preserved [methodology correction](02_VIDEO_ALIGNMENT_AND_MODALITIES/METHODOLOGY_CORRECTION.md). New ambiguous mappings were excluded rather than resolved from class labels.

Machine/experiment folders do not establish independent physical sessions. Date relationships, repeated program hashes and generic tool/material descriptions remain potential dependencies. See the [split gate](05_FULL_LABORATORY_FEASIBILITY/MSM_INDEPENDENCE_AND_SPLIT_GATE.md). Target definition and grouping require researcher approval before final splits are frozen.

Reusable components are the verified CNN extractor/pooling, head constructor and pipeline infrastructure. MSM requires its own visual head, sensor classifier/scalers and OOF-fitted F2 coefficients. No full-cohort CNN extraction, new training, F2 evaluation or source checkpoint inspection occurred in this stage. The ongoing Phase 1 job was not queried or changed. No MSM CNN-transfer result exists.

**Next proposed experiment:** a blinded visual-observability review of the technically eligible 16-frame sequences, sampled across native classes and date/session clusters. Do not launch model evaluation before review and target/group approval.

All originals remain in their authoritative versioned runs. [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json) records exact original paths, SHA-256 hashes and copy/index status. Large tables, videos, audio, checkpoints and caches are referenced rather than duplicated. This folder supersedes no historical result and does not convert smoke checks into test performance.
'''
    (root/'README.md').write_text(readme)
    return root
