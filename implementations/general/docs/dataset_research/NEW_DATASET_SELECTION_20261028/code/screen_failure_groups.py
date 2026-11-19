"""Bounded original timestamp-member reads; dates are candidate groups, not sessions."""
import csv
import json
import struct
import zlib
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from acquisition import ROOT,acquire


def read_timestamp(member):
    start=member['header_offset'];count=512
    path=acquire('http://160.75.159.4/data/failure.zip',f'failure/timestamp_ranges/{start}_{start+count-1}.bin',count+1,f'bytes={start}-{start+count-1}')
    raw=path.read_bytes();header=struct.unpack('<4s5H3I2H',raw[:30]);assert header[0]==b'PK\x03\x04'
    position=30+header[-2]+header[-1]
    payload=raw[position:position+member['compressed_bytes']]
    if len(payload)!=member['compressed_bytes']:raise ValueError('Bounded member did not fit')
    text=zlib.decompress(payload,-15) if header[3]==8 else payload
    assert f'{zlib.crc32(text):08x}'==member['crc32']
    return float(text)


if __name__=='__main__':
    inventory=json.loads((ROOT/'checks/failure_archive_inventory.json').read_text());by=defaultdict(list)
    for item in inventory:
        parts=item['name'].split('/')
        if len(parts)==5 and parts[1]=='rgb_imgs' and parts[-1].endswith('.txt'):
            by[(parts[2],parts[3])].append(item)
    native=list(csv.DictReader((ROOT/'checks/failure_native_annotation_records.csv').open()))
    selected=[row for row in native if row['complete_modalities']=='True']
    def check(row):
        items=sorted(by[(row['action'],row['recording_id'])],key=lambda x:x['name'])
        begin,end=read_timestamp(items[0]),read_timestamp(items[-1])
        return {'action':row['action'],'recording_id':row['recording_id'],'native_label':int(row['label']),
            'first_timestamp':begin,'last_timestamp':end,'span_seconds':end-begin,
            'first_timestamp_date_UTC':datetime.fromtimestamp(begin,timezone.utc).date().isoformat(),
            'first_source_member':items[0]['name'],'last_source_member':items[-1]['name'],
            'monotone_endpoints':end>begin}
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,selected))
    (ROOT/'checks/failure_recording_endpoint_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
    groups=defaultdict(Counter)
    for row in rows:groups[row['first_timestamp_date_UTC']][str(row['native_label'])]+=1
    (ROOT/'checks/failure_candidate_date_groups.json').write_text(json.dumps(groups,indent=2)+'\n')
    print('endpoint rows',len(rows),'candidate date groups',dict(groups))
