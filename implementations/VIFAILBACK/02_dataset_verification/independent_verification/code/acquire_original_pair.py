"""Retrieve one size-bounded original HDF5 pair to verify conversion fidelity."""
import json
from sources import ROOT,acquire
from original_annotations import ORIGINAL_REV,BASE


if __name__=='__main__':
    selected=json.loads((ROOT/'MATCHED_EXAMPLE_GALLERY/UNBLINDING/SOURCE_LABEL_KEY.json').read_text())
    sizes={}
    for task in sorted({x['source_task'] for x in selected}):
        p=acquire(f'https://huggingface.co/api/datasets/sii-rhos-ai/ViFailback-Dataset/tree/{ORIGINAL_REV}/raw_data/{task}?recursive=false','original_trees/raw_data_'+task+'.json')
        sizes.update({x['path']:x['size'] for x in json.loads(p.read_text()) if x['type']=='file'})
    candidates=[]
    for pair in range(1,11):
        members=[x for x in selected if x['pair']==pair]
        if all(x['source_hdf5'] in sizes and sizes[x['source_hdf5']]<160_000_000 for x in members):
            candidates.append((sum(sizes[x['source_hdf5']] for x in members),pair,members))
    n,pair,members=min(candidates,key=lambda x:x[:2])
    for x in members:
        p=x['source_hdf5'];acquire(f'{BASE}/resolve/{ORIGINAL_REV}/{p}','original/'+p,sizes[p]+1024)
    (ROOT/'checks/original_hdf5_sample_selection.json').write_text(json.dumps(members,indent=2)+'\n')
    print('Original pair acquired; total bytes',n)
