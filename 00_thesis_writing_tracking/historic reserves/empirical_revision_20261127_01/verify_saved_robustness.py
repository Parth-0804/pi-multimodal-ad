"""Read only selected saved prediction arrays; never imports experiment code.
Run from repository root. Output goes to a new requested receipt, never source artifacts.
"""
import argparse,ast,hashlib,json,math,struct,zipfile
from pathlib import Path

def array(z,name):
    with z.open(name+'.npy') as f:
        assert f.read(6)==b'\x93NUMPY'
        version=f.read(2);width=2 if version[0]==1 else 4
        size=struct.unpack('<H' if width==2 else '<I',f.read(width))[0]
        header=ast.literal_eval(f.read(size).decode('latin1'))
        assert not header['fortran_order'] and len(header['shape'])==1
        code={'<i8':'q','<f8':'d'}[header['descr']]
        values=list(struct.unpack('<'+str(header['shape'][0])+code,f.read()))
        return values

def ap(y,p):
    # Threshold-group precision weighted by the increase in recall; ties kept together.
    pairs=sorted(zip(p,y),reverse=True);positive=sum(y);assert positive
    tp=0;seen=0;score=0.;i=0
    while i<len(pairs):
        j=i;add=0
        while j<len(pairs) and pairs[j][0]==pairs[i][0]:
            add+=pairs[j][1];j+=1
        seen+=j-i;tp+=add;score+=(add/positive)*(tp/seen);i=j
    return score

def metrics(y,p):
    assert len(y)==len(p) and all(math.isfinite(v) and 0<=v<=1 for v in p)
    bins=[[] for _ in range(15)]
    for target,prob in zip(y,p):bins[min(int(prob*15),14)].append((target,prob))
    ece=sum(abs(sum(prob-target for target,prob in bucket)) for bucket in bins)/len(y)
    return {'AUPRC':ap(y,p),'Brier':sum((prob-target)**2 for target,prob in zip(y,p))/len(y),'ECE':ece}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);assert not out.exists(),'Preserve existing verification receipt'
    # Tiny synthetic checks cover score ties and ranking direction.
    assert ap([0,1],[.5,.5])==.5 and ap([0,1],[0,1])==1 and ap([0,1],[1,0])==.5
    base=Path('implementations/REASSEMBLE/results/runs/missing_degraded_modality_robustness')
    summary=json.loads((base/'results.json').read_text())['conditions'];records={};reference=None;maxerr=0.
    for condition in ['clean','V1_0.1','V2_4.0','V3_0.5','S1_1.0','S2_0.5','S3_0.5','S4','V4','S5']:
        p=base/'predictions'/(condition+'.npz');sha=hashlib.sha256(p.read_bytes()).hexdigest()
        assert sha==json.loads(p.with_suffix('.json').read_text())['sha256']
        with zipfile.ZipFile(p) as z:
            y=array(z,'y');fold=array(z,'fold');assert len(y)==4530 and sum(y)==509
            if reference is None:reference=(y,fold)
            assert (y,fold)==reference
            models=['F2','F5','F6']+(['U1','U2'] if condition=='clean' else [])
            measured={}
            for m in models:
                pvalues=array(z,m+'_p');got=metrics(y,pvalues);expected=summary[condition]['metrics'][m]
                errors={k:abs(v-expected[k]['estimate']) for k,v in got.items()}
                maxerr=max(maxerr,*errors.values());assert max(errors.values())<1e-12,(condition,m,errors)
                measured[m]=got
        records[condition]={'path':str(p),'sha256':sha,'metrics':measured}
    receipt={'classification':'VERIFIED','scope':'Independent stdlib arithmetic from selected saved y/fold/probability arrays; source NPZ hashes match companion metadata. No training, inference, bootstrap refitting or raw input access. Row-label and fold parity checked; no new recording-ID audit.','metric':'failure-positive pooled average precision, Brier, 15-bin equal-width ECE','max_absolute_error':maxerr,'conditions':records}
    out.write_text(json.dumps(receipt,indent=2)+'\n');print('10 conditions; 32 model rows; AP/Brier/ECE match within',maxerr)
if __name__=='__main__':main()
