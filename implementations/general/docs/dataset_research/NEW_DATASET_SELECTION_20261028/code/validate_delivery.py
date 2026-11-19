"""Meaningful independent consistency checks on retained active-candidate sources."""
import csv
import hashlib
import io
import json
import math
import shutil
import zipfile
from collections import Counter,defaultdict
from pathlib import Path
from acquisition import ROOT


if __name__=='__main__':
    results=[]
    def check(name, condition, evidence=None):
        results.append({'check':name,'passed':bool(condition),'evidence':evidence})
        if not condition:raise AssertionError(name)
    evidence=ROOT/'source_evidence'
    for name,dataset in [('robofac','MINT-SJTU/RoboFAC-dataset')]:
        info=json.loads((evidence/name/'dataset_files_with_sizes.json').read_text());verified=0;unavailable=[]
        for item in info['siblings']:
            path=evidence/name/'files'/item['rfilename']
            if not path.exists():continue
            data=path.read_bytes();check('source size: '+item['rfilename'],len(data)==item['size'])
            if 'lfs' in item:
                digest=hashlib.sha256(data).hexdigest();expected=item['lfs']['sha256']
            else:
                digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();expected=item['blobId']
            check('official source content identity: '+item['rfilename'],digest==expected);verified+=1
        check('all 727 original RoboFAC JSON annotations retained',sum(1 for p in info['siblings'] if p['rfilename'].endswith('.json') and (evidence/name/'files'/p['rfilename']).exists())==727)
    for directory in ['robofac','robofac_code','failure','failure_code','papers']:
        for receipt in (evidence/directory).rglob('*.receipt.json'):
            if receipt.name.startswith('MAIA_'):continue
            r=json.loads(receipt.read_text());source=receipt.with_name(receipt.name.removesuffix('.receipt.json'))
            if r.get('status')!='ACQUIRED':continue
            check('receipt hash: '+str(source.relative_to(evidence)),source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256'])
            if r.get('request_range'):
                check('HTTP byte range honored: '+str(source.relative_to(evidence)),r['http_status']==206 and bool(r.get('content_range')))
    with zipfile.ZipFile(evidence/'failure/annotation.zip') as z:
        native=[]
        for member in z.namelist():
            for row in csv.DictReader(io.StringIO(z.read(member).decode())):
                native.append((member.removesuffix('_annotation.txt'),row['name'],int(row['label'])))
    check('independent FAILURE annotation recount',Counter(v[2] for v in native)=={1:163,0:89})
    check('unique composite native annotation identities',len({v[:2] for v in native})==252)
    inv=json.loads((ROOT/'checks/failure_archive_inventory.json').read_text());names={x['name'] for x in inv};eligible=[]
    for action,recording,label in native:
        prefix=f'failnet_dataset/rgb_imgs/{action}/{recording}/'
        rgb=[n for n in names if n.startswith(prefix) and n.endswith('.png')]
        depth_ok=all(n.replace('/rgb_imgs/','/depth_imgs/').removesuffix('.png')+'.tiff' in names for n in rgb)
        time_ok=all(n.removesuffix('.png')+'.txt' in names for n in rgb)
        if rgb and depth_ok and time_ok and f'failnet_dataset/audio/{action}/{recording}.wav' in names:
            eligible.append((action,recording,label,len(rgb)))
    check('independent complete-modality count',len(eligible)==229)
    check('independent joined class counts',Counter(v[2] for v in eligible)=={1:147,0:82})
    check('sixteen distinct stored RGB positions available',all(v[3]>=16 for v in eligible))
    endpoints=json.loads((ROOT/'checks/failure_recording_endpoint_audit.json').read_text())
    check('endpoints cover exact eligible identities',{(x['action'],x['recording_id']) for x in endpoints}=={v[:2] for v in eligible})
    check('endpoint finiteness and order',all(math.isfinite(x['first_timestamp']) and math.isfinite(x['last_timestamp']) and x['first_timestamp']<x['last_timestamp'] for x in endpoints))
    dates=defaultdict(set)
    for x in endpoints:dates[x['first_timestamp_date_UTC']].add(x['native_label'])
    check('seven candidate dates with both labels',len(dates)==7 and all(v=={0,1} for v in dates.values()))
    pilots=json.loads((ROOT/'checks/FAILURE_PROPOSED_PILOT.json').read_text())
    check('pilot is ten distinct source recordings',len(pilots)==len({(x['action'],x['recording_id']) for x in pilots})==10)
    for pair in range(1,6):
        a=[x for x in pilots if x['pair']==pair]
        check('pilot pair label/date/action integrity '+str(pair),len(a)==2 and {x['native_label'] for x in a}=={0,1} and len({x['action'] for x in a})==len({x['first_timestamp_date_UTC'] for x in a})==1)
    check('pilot has not been acquired',not (ROOT/'pilot_data').exists())
    required=['README.md','DATASET_COMPARISON.md','ROBOFAC_LABEL_AUDIT.md','FAILURE_LABEL_AUDIT.md','NATIVE_LABEL_EXAMPLES.csv','GROUP_INDEPENDENCE_SCREENING.md','VISUAL_FEASIBILITY_SCREENING.md','FINAL_DATASET_RECOMMENDATION.md','RESEARCHER_HANDOFF.md']
    check('active-scope required reports exist',all((ROOT/n).is_file() for n in required))
    check('no CRIA report under withdrawn scope',not (ROOT/'CRIA_LABEL_AUDIT.md').exists())
    check('storage reserve at least 20 GiB',shutil.disk_usage(ROOT).free>=20*1024**3)
    output={'passed':all(x['passed'] for x in results),'checks':len(results),'results':results,'limitations':['No full HDF5 corpus check','No full image/audio payload verification','No packet-level synchronization audit','No trained models or performance measurements']}
    (ROOT/'checks/validation.json').write_text(json.dumps(output,indent=2)+'\n')
    print('VALIDATED',len(results),'checks; active candidates RoboFAC and FAILURE only')
