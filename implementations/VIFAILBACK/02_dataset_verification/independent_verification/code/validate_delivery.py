"""Validate scientific input/output contracts from preserved real evidence."""
import ast,csv,hashlib,json,shutil
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import numpy as np,pandas as pd
from sources import ROOT,MAX_BYTES,MIN_FREE


class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ['src','href']:self.links.append(value)


if __name__=='__main__':
    results=[]
    def check(name,condition,details=None):
        results.append({'check':name,'passed':bool(condition),'details':details})
        if not condition:raise AssertionError(name)
    source=ROOT/'source_evidence';downloaded=0
    for receipt in source.rglob('*.receipt.json'):
        info=json.loads(receipt.read_text());path=receipt.with_name(receipt.name.removesuffix('.receipt.json'))
        check('source acquisition complete '+str(path.relative_to(source)),info.get('status','ACQUIRED')=='ACQUIRED' and path.exists())
        data=path.read_bytes();check('source receipt SHA-256 '+str(path.relative_to(source)),hashlib.sha256(data).hexdigest()==info['sha256'])
        downloaded+=info['bytes']
        if info.get('request_headers',{}).get('Range'):
            begin,end=map(int,info['request_headers']['Range'].removeprefix('bytes=').split('-'))
            check('bounded range exact response '+str(path.relative_to(source)),info['http_status']==206 and info['content_range'].startswith(f'bytes {begin}-{end}/') and len(data)==end-begin+1)
    check('bounded source acquisition budget',downloaded<MAX_BYTES,downloaded)
    check('20 GiB reserve',shutil.disk_usage(ROOT).free>=MIN_FREE,shutil.disk_usage(ROOT).free)
    inventory=json.loads((source/'vifailback_files.json').read_text());files={x['rfilename']:x for x in inventory['siblings']}
    for path in (source/'vifailback').rglob('*'):
        if not path.is_file() or path.name.endswith('.receipt.json'):continue
        name=str(path.relative_to(source/'vifailback'));entry=files[name];raw=path.read_bytes()
        check('official converted size '+name,len(raw)==entry['size'])
        digest=hashlib.sha256(raw).hexdigest() if 'lfs' in entry else hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        expected=entry['lfs']['sha256'] if 'lfs' in entry else entry['blobId']
        check('official converted content identity '+name,digest==expected)
    native=[json.loads(l) for l in (source/'vifailback/meta/vifailback_annotations.jsonl').open()]
    check('native outcome recount',Counter(a['annotation']['failure_detection'] for a in native)=={'yes':4545,'no':657})
    original={}
    for path in (source/'original/annotated_data').rglob('*.json'):
        if path.name.endswith('.receipt.json'):continue
        for a in json.loads(path.read_text()):
            check('unique original native video '+a['video'],a['video'] not in original);original[a['video']]=a
    check('5202 original annotations',len(original)==5202)
    for a in native:check('complete original label identity '+str(a['episode_index']),original.get(a['annotation']['video'])==a['annotation'])
    for name,expected_rows in [('class_counts_by_task.csv',100),('class_counts_by_source_task.csv',109)]:
        data=list(csv.DictReader((ROOT/'checks'/name).open()));check('task table rows '+name,len(data)==expected_rows)
        check('task table class totals '+name,sum(int(x['success']) for x in data)==657 and sum(int(x['failure']) for x in data)==4545)
    taskrows=list(csv.DictReader((ROOT/'checks/class_counts_by_task.csv').open()));check('100 tasks both outcomes',all(int(x['success'])>0 and int(x['failure'])>0 for x in taskrows))
    key=json.loads((ROOT/'MATCHED_EXAMPLE_GALLERY/UNBLINDING/SOURCE_LABEL_KEY.json').read_text());check('twenty distinct pilot source executions',len(key)==len({x['episode_index'] for x in key})==20)
    check('ten per native outcome',Counter(x['episode_success'] for x in key)=={'success':10,'failure':10})
    for pair in range(1,11):
        members=[x for x in key if x['pair']==pair]
        check('matched task and outcomes pair '+str(pair),len(members)==2 and len({x['source_task'] for x in members})==1 and len({x['task_index'] for x in members})==1 and {x['episode_success'] for x in members}=={'success','failure'})
    media=json.loads((ROOT/'checks/pilot_media_audit.json').read_text());numerical=json.loads((ROOT/'checks/pilot_numerical_audit.json').read_text())
    check('60 complete pilot video audits',len(media)==60);check('20 actual pilot sensor audits',len(numerical)==20)
    for v in media:
        indices=v['frame_indices'];check('16 ordered distinct positions '+v['blind_id']+v['view'],len(indices)==len(set(indices))==16 and indices==sorted(indices) and indices[0]==0 and indices[-1]==v['source_frame_count']-1)
        expected=[k*(v['source_frame_count']-1)//15 for k in range(16)];check('label-blind frame formula '+v['blind_id']+v['view'],indices==expected)
        check('16 decoded distinct images '+v['blind_id']+v['view'],v['unique_selected_decoded_images']==16)
        for i,digest in enumerate(v['image_sha256']):
            path=ROOT/'MATCHED_EXAMPLE_GALLERY/assets'/v['blind_id']/v['view']/f'frame_{i:02d}.png'
            check('decoded image source hash '+str(path.relative_to(ROOT)),hashlib.sha256(path.read_bytes()).hexdigest()==digest)
    for row in numerical:
        check('pilot finite observations '+row['blind_id'],all(x['nonfinite']==0 and x['shape']==[row['frames'],14] for x in row['arrays'].values()))
        check('converted PTS alignment '+row['blind_id'],row['video_sensor_selected_timestamp_max_error_s']<1e-5)
    lock=json.loads((ROOT/'checks/blind_screen_lock.json').read_text());check('initial blind screen remains frozen',hashlib.sha256((ROOT/lock['file']).read_bytes()).hexdigest()==lock['sha256'])
    for path in (ROOT/'MATCHED_EXAMPLE_GALLERY').glob('B*.html'):
        text=path.read_text();check('native label key absent from blind case '+path.name,all(k not in text for k in ['episode_success','failure_detection','source_hdf5','is_avoid_keyframe']))
    for path in (ROOT/'MATCHED_EXAMPLE_GALLERY').rglob('*.html'):
        parser=Links();parser.feed(path.read_text())
        for target in parser.links:
            if target.startswith(('http:','https:','#','data:')):continue
            check('gallery local link '+path.name+' '+target,(path.parent/target.split('#')[0]).is_file())
    for row in json.loads((ROOT/'checks/original_hdf5_conversion_audit.json').read_text()):
        check('original sim flag false '+str(row['episode_index']),row['attributes']['sim'] is False)
        check('exact original observation arrays '+str(row['episode_index']),all(x['max_abs_error']==0 for x in row['numeric_comparisons']))
        check('original/converted image fidelity '+str(row['episode_index']),all(x['PSNR_dB']>35 for x in row['image_comparisons']))
        check('hardware timestamps not invented '+str(row['episode_index']),row['explicit_hardware_timestamps_found'] is False)
    for row in json.loads((ROOT/'checks/constant_state_origin_audit.json').read_text()):
        check('upstream constant-state defect '+str(row['episode_index']),row['checks'][0]['source_varying_channels']==0 and all(x['max_abs_conversion_error']==0 for x in row['checks']))
    secondary=json.loads((ROOT/'checks/secondary_bounded_native_audit.json').read_text());check('secondary archive explicitly partial',secondary['archive_complete'] is False)
    check('two actual secondary native annotations',len(secondary['metadata_members'])==2)
    for m in secondary['metadata_members']:
        raw=(source/'secondary_native_members'/m['name']).read_bytes();check('secondary native member bytes '+m['name'],hashlib.sha256(raw).hexdigest()==m['sha256'])
        obj=json.loads(raw);check('secondary native interval schema '+m['name'],isinstance(obj['Outcomes'],list) and all(isinstance(v,int) for interval in obj['Anomalies'] for v in interval))
    for path in (ROOT/'code').glob('*.py'):ast.parse(path.read_text())
    required=['README.md','NATIVE_LABEL_AUDIT.md','MODALITY_AND_ALIGNMENT_AUDIT.md','GROUP_INDEPENDENCE_AUDIT.md','VISUAL_OBSERVABILITY_REVIEW.md','SECONDARY_CANDIDATE_AUDIT.md','FINAL_RESEARCH_DECISION.md','RESEARCHER_HANDOFF.md']
    check('required reports present',all((ROOT/p).exists() for p in required))
    result={'passed':True,'checks':len(results),'source_acquisition_bytes':downloaded,'free_bytes':shutil.disk_usage(ROOT).free,
        'scope':'Source audit, selected modalities, real gallery and integrity; no neural network training or model performance tests','results':results}
    (ROOT/'checks/validation.json').write_text(json.dumps(result,indent=2)+'\n');print('Validated',len(results),'checks; acquired source bytes',downloaded)
