"""Plan, do not acquire, ten original action-level examples for blind review."""
import csv
import json
from collections import defaultdict
import numpy as np
from acquisition import ROOT


if __name__=='__main__':
    inventory=json.loads((ROOT/'checks/failure_archive_inventory.json').read_text());by=defaultdict(list)
    for item in inventory:
        parts=item['name'].split('/')
        if len(parts)==5 and parts[1]=='rgb_imgs' and parts[-1].endswith('.png'):
            by[(parts[2],parts[3])].append(item)
    endpoints=json.loads((ROOT/'checks/failure_recording_endpoint_audit.json').read_text());selected=[];members=[]
    for pair,action in enumerate(['push','place','pour','put_in','put_on'],1):
        local=[x for x in endpoints if x['action']==action]
        candidates=[(abs(a['span_seconds']-b['span_seconds']),a,b) for a in local for b in local
            if a['native_label']==0 and b['native_label']==1 and a['first_timestamp_date_UTC']==b['first_timestamp_date_UTC']]
        _,normal,failed=min(candidates,key=lambda x:(x[0],int(x[1]['recording_id']),int(x[2]['recording_id'])))
        for row in [normal,failed]:
            rgb=sorted(by[(action,row['recording_id'])],key=lambda x:x['name'])
            indices=np.linspace(0,len(rgb)-1,16,dtype=int);assert len(set(indices))==16
            video_members=[rgb[i] for i in indices]
            timestamps=[x['name'].removesuffix('.png')+'.txt' for x in video_members]
            audio=next(x for x in inventory if x['name']==f'failnet_dataset/audio/{action}/{row["recording_id"]}.wav')
            source_names={x['name'] for x in video_members}|set(timestamps)|{audio['name']}
            chosen=[x for x in inventory if x['name'] in source_names]
            selected.append(dict(pair=pair,**row,rgb_frames_listed=len(rgb),proposed_rgb_frames=16,
                compressed_payload_bytes=sum(x['compressed_bytes'] for x in chosen),uncompressed_payload_bytes=sum(x['bytes'] for x in chosen),
                frame_indices_are_positions_in_stored_sequence=indices.tolist(),object_match='UNKNOWN; must be reviewed blind',
                exact_temporal_audio_alignment='UNVERIFIED; full-action classification only'))
            members.extend({'pair':pair,'action':action,'recording_id':row['recording_id'],**x} for x in chosen)
    (ROOT/'checks/FAILURE_PROPOSED_PILOT.json').write_text(json.dumps(selected,indent=2)+'\n')
    (ROOT/'checks/FAILURE_PROPOSED_PILOT_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n')
    print('planned examples',len(selected),'RGB frames',sum(x['proposed_rgb_frames'] for x in selected),
        'compressed payload bytes',sum(x['compressed_payload_bytes'] for x in selected),
        'extracted bytes',sum(x['uncompressed_payload_bytes'] for x in selected))
