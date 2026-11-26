"""Select ten matched task pairs, freeze label-blind uniform frame sampling."""
import csv,json,random
from pathlib import Path
from sources import ROOT


if __name__=='__main__':
    rows=list(csv.DictReader((ROOT/'checks/all_native_episode_records.csv').open()))
    requested=[('hold_socket_plug','gripper 6d-pose'),('grasp_cube_place_shelf','gripper state'),
        ('pick_cube_transfer_place_basket_ep1','gripper state'),('pick_test_tube_place_left_slot','gripper 6d-pose'),
        ('stack_cup_on_book','gripper 6d-pose'),('pour_sausage_into_basket','gripper 6d-pose'),
        ('open_drawer_put_marker','gripper state'),('pick_marker_draw_line','task planning'),
        ('place_spoon_into_pot_cover_lid','task planning'),('put_mouse_basket_from_tray_ep1','human intervention')]
    selected=[]
    for pair,(task,category) in enumerate(requested,1):
        local=[x for x in rows if x['source_task']==task]
        candidates=[(abs(int(a['num_frames'])-int(b['num_frames'])),int(a['episode_index']),int(b['episode_index']),a,b)
            for a in local for b in local if a['episode_success']=='success' and b['failure_type']==category]
        *_,a,b=min(candidates,key=lambda x:x[:3])
        for row in [a,b]:selected.append({**row,'pair':pair,'physical_object_matching':'Task object identity inferred from same task; visually unverified'})
    random.Random(20261028).shuffle(selected)
    for i,row in enumerate(selected,1):row['blind_id']=f'B{i:02d}'
    out=ROOT/'MATCHED_EXAMPLE_GALLERY/UNBLINDING';out.mkdir(parents=True,exist_ok=True)
    (out/'SOURCE_LABEL_KEY.json').write_text(json.dumps(selected,indent=2)+'\n')
    policy={'seed':20261028,'matching':'same original task directory; nearest frame length; tie by source episode index',
        'frame_policy':'16 uniformly spaced frame positions including first and last, floor(k*(N-1)/15) for k=0..15',
        'camera_policy':'same 16 indices in all three views','crop_policy':'same fixed normalized center ROI per camera and class; supplementary to full view',
        'label_use':'outcomes/categories used only to balance pilot case selection, never select frames/crops/offsets',
        'example_count':20,'matched_pairs':10,'RGB_images':960,'frames_per_episode_per_view':16,
        'estimated_converted_download_bytes':sum(int(x['listed_pilot_bytes']) for x in selected),'no_training':True}
    (ROOT/'config/pilot_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    print('Selected ten task pairs, twenty distinct episodes; total listed converted pilot bytes',policy['estimated_converted_download_bytes'])
