"""Acquire the original author annotation files via verified directory listings."""
import json
from concurrent.futures import ThreadPoolExecutor
from sources import ROOT,acquire

ORIGINAL_REV='21df46c2585c52e5a62df5f4b946bae6cbc6fed7'
BASE='https://huggingface.co/datasets/sii-rhos-ai/ViFailback-Dataset'


def one(item):
    task=item['path'].split('/')[-1]
    tree=acquire(f'https://huggingface.co/api/datasets/sii-rhos-ai/ViFailback-Dataset/tree/{ORIGINAL_REV}/annotated_data/{task}?recursive=false','original_trees/annotated_data_'+task+'.json')
    entries=json.loads(tree.read_text());found=[]
    for x in entries:
        if x['type']=='file' and x['path'].endswith('.json'):
            acquire(f'{BASE}/resolve/{ORIGINAL_REV}/{x["path"]}','original/'+x['path'],x['size']+1024);found.append(x['path'])
    return found


if __name__=='__main__':
    tree=json.loads((ROOT/'source_evidence/original_annotated_data_tree.json').read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:paths=sum(pool.map(one,[x for x in tree if x['type']=='directory']),[])
    (ROOT/'checks/original_annotation_paths.json').write_text(json.dumps(paths,indent=2)+'\n')
    print('Original native annotation files acquired',len(paths))
