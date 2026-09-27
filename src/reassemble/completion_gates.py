"""Secondary audio timing and physical-object generalization feasibility gates."""
from pathlib import Path
import json
import h5py
import numpy as np
import pandas as pd
from .completion_common import config,read,write,storage,progress
from .section1_features import cohort,sha
from .section1_report import table


def main():
    c=config();storage();base=read('configs/reassemble/section1.json');frame=cohort(base)
    assert (Path(c['runs']['modality-dropout'])/'results.json').exists(),'Complete ordered preceding phases first'
    inventory=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id')
    streams={};clock_records=[];rows=[]
    for rid,group in frame.groupby('recording_id',sort=True):
        record_path=Path(base['audit_run'])/'records'/(rid+'.json');record=read(record_path);meta=record['recording'];segments={x['segment_id']:x for x in record['segments']}
        path=Path(base['data_root'])/'raw/data'/inventory.loc[rid,'filename'];st=path.stat()
        assert st.st_size==inventory.loc[rid,'size_bytes'] and st.st_mtime_ns==inventory.loc[rid,'mtime_ns']
        with h5py.File(path,'r') as h:
            audio_attrs={name:{str(k):str(v) for k,v in h[name].attrs.items()} for name in meta['audio_streams']}
            timestamp_names=list(h['timestamps'].keys())
        clock_records.append({'recording_id':rid,'audio_dataset_attributes':audio_attrs,'timestamp_names':timestamp_names,'inventory_sha256':sha(record_path)})
        for row in group.itertuples():
            for name in meta['audio_streams']:
                q=segments[row.segment_id]['audio'].get(name,{})
                media=meta['media'].get(name,{})
                decodable=bool(q.get('decodable',False));coverage=float(q.get('nominal_coverage',0))
                valid=decodable and coverage>=.9 and float(q.get('valid_duration_ratio',0) or 0)>=.9
                # A verified clock anchor could suffice; per-sample timestamps are not mandatory.
                explicit=bool(media.get('alignment_verified',False))
                rows.append({'recording_id':rid,'segment_id':row.segment_id,'failure':int(row.failure),'stream':name,'decodable':decodable,'nominal_coverage':coverage,'nominal_valid':valid,'verified_interval':valid and explicit,'duration':float(media.get('duration',0)),'reported_frames':media.get('reported_frames'),'decoded_frames':media.get('frames'),'silence_fraction':q.get('silence_fraction')})
    data=pd.DataFrame(rows)
    for name,g in data.groupby('stream'):
        streams[name]={'segments':len(g),'decodable':int(g.decodable.sum()),'nominal_valid_segments':int(g.nominal_valid.sum()),'nominal_valid_percent':float(100*g.nominal_valid.mean()),'nominal_valid_failures':int(g.loc[g.failure==1,'nominal_valid'].sum()),'nominal_valid_failure_percent':float(100*g.loc[g.failure==1,'nominal_valid'].mean()),'nominal_valid_recordings':int(g.loc[g.nominal_valid,'recording_id'].nunique()),'verified_segments':int(g.verified_interval.sum()),'verified_failures':int(g.loc[g.failure==1,'verified_interval'].sum()),'verified_recordings':int(g.loc[g.verified_interval,'recording_id'].nunique()),'reported_vs_decoded_frame_mismatch_recordings':int(g.loc[g.reported_frames!=g.decoded_frames,'recording_id'].nunique()),'nearly_silent_segments':int((g.silence_fraction.fillna(0)>=.99).sum())}
    nonempty_attrs=[r for r in clock_records if any(r['audio_dataset_attributes'].values())]
    result={'streams':streams,'recordings_audited':len(clock_records),'nonempty_audio_attribute_recordings':nonempty_attrs,'alignment_requirement':'Reliable segment start/end transfer is sufficient; frame-perfect alignment and per-sample timestamps are not required. No independently documented start offset/drift or segment anchor was found in available evidence.','decoding_evidence':'Reuse prior full-stream decoding and per-segment checks from immutable inventory; raw sizes/mtime and audited-record hashes verified. Header inspection repeated now; no new audio payload cache.','decision':'AUDIO NOT INCLUDED — SEGMENT-ALIGNMENT OR COVERAGE PRECONDITION FAILED','reason':'Nominal origin is inferred from the earliest non-audio timestamp, not a measured audio clock mapping. Decoder-reported and actually decoded sample counts can disagree. Nominal overlap does not establish correct action-segment association.'}
    if nonempty_attrs or any(v['verified_segments'] for v in streams.values()):
        write(Path(c['runs']['audio-gate'])/'clock_review_required.json',{'records':clock_records})
        raise RuntimeError('New possible audio clock evidence requires inspection before gate decision; do not silently exclude or train')
    root=Path(c['runs']['audio-gate']);write(root/'results.json',result);write(root/'clock_metadata.json',clock_records);data.to_csv(root/'segment_coverage.csv',index=False)
    text='# Audio feasibility handoff\n\n**'+result['decision']+'**\n\nThe intended AST would aggregate independently within each high-level segment. Frame-perfect synchronization was not required. The missing prerequisite is a trustworthy mapping from annotation clock to the decoded waveform interval. No stream has an independently verified mapping; this is not evidence that audio lacks predictive signal.\n\n'+table(['Stream','Nominal valid %','Failure valid %','Recordings','Verified segments','Frame-count mismatch recordings'],[[name,f"{v['nominal_valid_percent']:.2f}",f"{v['nominal_valid_failure_percent']:.2f}",v['nominal_valid_recordings'],v['verified_segments'],v['reported_vs_decoded_frame_mismatch_recordings']] for name,v in streams.items()])
    text+='\nNo AST, tri-modal fusion or audio-corruption model was trained because the segment-alignment gate failed. This is a completed gate-based exclusion, not unfinished modelling. Prior full decoding was reused after verifying immutable source metadata; actual audio dataset attributes and timestamp-key availability were rechecked. Details: '+str(root)+'.\n'
    Path('artifacts/reassemble/reports/AUDIO_FEASIBILITY_HANDOFF.md').write_text(text)
    progress('Audio feasibility complete: alignment gate failed; continue final study without audio')
    # Objects are annotation categories, not automatically distinct physical instances.
    support=frame.groupby('object_annotation',dropna=False).agg(segments=('failure','size'),failures=('failure','sum'),recordings=('recording_id','nunique')).reset_index()
    object_sets={rid:set(g.object_annotation.fillna('<missing>').astype(str)) for rid,g in frame.groupby('recording_id')}
    parent={rid:rid for rid in object_sets}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    owner={}
    for rid,objects in object_sets.items():
        for obj in objects:
            if obj in owner:parent[find(rid)]=find(owner[obj])
            else:owner[obj]=rid
    components={}
    for rid in object_sets:components.setdefault(find(rid),[]).append(rid)
    object_result={'annotation_categories':len(support),'physical_instance_identity_verified':False,'support':support.where(pd.notna(support),None).to_dict('records'),'recording_object_connected_components':len(components),'component_recording_counts':sorted(map(len,components.values()),reverse=True),'decision':'NOT RUN — GATE FAILED','reason':'Object annotations are categories/targets without verified physical-instance identity. Shared object categories connect recordings; a stress test preserving both recording and object disjointness lacks validated independent groups. Do not substitute a category label for physical object identity.'}
    root=Path(c['runs']['object-feasibility']);write(root/'results.json',object_result);support.to_csv(root/'object_support.csv',index=False)
    Path('artifacts/reassemble/reports/OBJECT_GENERALIZATION_FEASIBILITY.md').write_text('# Object-generalization feasibility\n\n**NOT RUN — GATE FAILED.**\n\n'+object_result['reason']+'\n\nAnnotation categories: '+str(len(support))+'. Recording/object connected components: '+str(len(components))+'. Counts: '+str(object_result['component_recording_counts'])+'.\n\n'+table(['Annotation','Segments','Failures','Recordings'],support.values.tolist())+'\nNo new object-disjoint model or architecture search was run. No unseen-object claim is supported.\n')
    progress('Object generalization feasibility documented; continue efficiency and synthesis')

if __name__=='__main__':main()
