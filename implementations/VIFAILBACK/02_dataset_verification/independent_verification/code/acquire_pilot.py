"""Fetch exactly the twenty declared episodes, three cameras each."""
import json
from concurrent.futures import ThreadPoolExecutor
from sources import ROOT,hf_file


if __name__=='__main__':
    rows=json.loads((ROOT/'MATCHED_EXAMPLE_GALLERY/UNBLINDING/SOURCE_LABEL_KEY.json').read_text())
    sizes={x['rfilename']:x['size'] for x in json.loads((ROOT/'source_evidence/vifailback_files.json').read_text())['siblings']}
    paths=[row[key] for row in rows for key in ['data','video_high','video_left','video_right']]
    assert len(paths)==len(set(paths))==80
    assert sum(sizes[p] for p in paths)<500_000_000
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda p:hf_file(p,sizes[p]+1024),paths))
