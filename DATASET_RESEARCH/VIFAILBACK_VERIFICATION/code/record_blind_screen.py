"""Record the initial masked-key analyst screen before inspecting outcomes."""
import hashlib,json
from datetime import datetime,timezone
from sources import ROOT

RATINGS=[
('B01','VISIBLE','none','Marker transfer into the opened drawer is visible; no definite failure observed.'),
('B02','PARTIALLY VISIBLE','possible','Marker pickup and return are visible; the required line stroke cannot be judged confidently at these fixed temporal samples.'),
('B03','VISIBLE','clear','The book moves during interaction while the cup does not appear placed onto it; wrong-object/contact or placement deviation is visible.'),
('B04','VISIBLE','none','Spoon goes into the pot and the lid is placed over it.'),
('B05','PARTIALLY VISIBLE','none','Pouring and material in the receiving basket are visible; complete material transfer cannot be verified from these samples.'),
('B06','VISIBLE','clear','Blue cube appears outside the basket on the tabletop after the handoff/placement attempt; dropping or failed placement is visible.'),
('B07','VISIBLE','clear','No completed pour; food remains on the green plate, and the neighboring basket is displaced/lifted.'),
('B08','VISIBLE','clear','Marker stays on the tabletop despite a grasp attempt; drawer operation does not complete the requested transfer.'),
('B09','VISIBLE','clear','Tube remains beside the rack after an apparent empty/unsuccessful grasp; no upright placement is visible.'),
('B10','VISIBLE','none','Marker is lifted, a dark line is visible, and the marker returns to the cup; detailed stroke semantics remain a limitation.'),
('B11','VISIBLE','none','Wrist view shows the plug approaching and apparently seating in the socket; electrical connection is not independently measured.'),
('B12','VISIBLE','none','Cube handoff followed by the cube being inside the basket is visible.'),
('B13','VISIBLE','none','Tube is lifted and an upright tube is visible at the rack after release.'),
('B14','VISIBLE','none','Cup is lifted and placed on the closed book.'),
('B15','VISIBLE','clear','Gripper approaches the tube but the tube remains in the source cup; no successful transfer occurs.'),
('B16','VISIBLE','none','Mouse is moved from the tray into the basket.'),
('B17','VISIBLE','none','Tube is lifted from the cup and placed into the rack.'),
('B18','VISIBLE','clear','The plug remains on the work surface rather than being successfully grasped/inserted; fine connector contact is partly occluded.'),
('B19','VISIBLE','clear','Spoon is placed onto the white plate rather than into the red pot; the requested lid closure is not completed.'),
('B20','VISIBLE','clear','Human hands enter and interfere with the task; the robot does not complete the requested transfer.'),
]


if __name__=='__main__':
    target=ROOT/'MATCHED_EXAMPLE_GALLERY/INITIAL_BLINDED_SCREEN.json'
    assert not target.exists()
    rows=[]
    for bid,visibility,evidence,notes in RATINGS:
        p=ROOT/'MATCHED_EXAMPLE_GALLERY/assets'/bid/'BLINDED_OVERVIEW.jpg'
        rows.append({'blind_id':bid,'interaction_visibility':visibility,'physical_failure_evidence':evidence,'notes':notes,'overview_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    report={'recorded_utc':datetime.now(timezone.utc).isoformat(),'method':'AI-assisted initial analyst screen with per-example identities/outcomes masked; not independent human validation',
        'access_before_recording':'All 20 three-camera uniform-frame overviews and label-free task instructions; additional full sequences B09 high, B11 left wrist, B18 left wrist, B02 high',
        'source_key_opened_for_this_screen':False,'selection_balance_known':'10 success/failure pairs; per-case mappings masked',
        'limitations':'One observer; coarse uniform samples; no inter-rater reliability; apparent task outcomes are observations, not replacement labels','ratings':rows}
    target.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'checks/blind_screen_lock.json').write_text(json.dumps({'file':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'utc':report['recorded_utc']},indent=2)+'\n')
    print('Initial masked-key observations locked for all 20 cases; no source key read.')
