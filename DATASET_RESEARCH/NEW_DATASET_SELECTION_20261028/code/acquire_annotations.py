"""Acquire original released annotations, never complete media collections."""
import json
from concurrent.futures import ThreadPoolExecutor
from acquisition import ROOT, acquire


def main():
    jobs = []
    # CRIA was withdrawn by the researcher after the initial acquisition.
    for name, dataset in [('robofac','MINT-SJTU/RoboFAC-dataset')]:
        info=json.loads((ROOT/'source_evidence'/name/'dataset_files_with_sizes.json').read_text())
        for item in info['siblings']:
            path=item['rfilename']
            selected = path.endswith('.json') if name=='robofac' else path.endswith(('/annotation.json','/info.json','/episodes.jsonl','/tasks.jsonl'))
            if selected:
                jobs.append((f'https://huggingface.co/datasets/{dataset}/resolve/{info["sha"]}/{path}',name+'/files/'+path,item['size']+1024))
    # Parallel HTTP reads are independent. Their total declared bytes fit far below the cap.
    assert sum(j[2] for j in jobs) < 100_000_000
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda args: acquire(*args),jobs))
    sha='8196217bf52d17fdb7193e57619bd855b1723d4e'
    acquire(f'https://raw.githubusercontent.com/ardai/fino-net/{sha}/src/finonet-rgb-d-a.ipynb','failure_code/finonet-rgb-d-a.ipynb')


if __name__=='__main__':
    main()
