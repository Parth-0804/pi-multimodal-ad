"""Paired corruption outcomes, clean-relative degradation, and gate mechanism tests."""
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from threadpoolctl import threadpool_limits
from .completion_common import config,read,write,progress
from .section1_features import cohort
from .section1_report import metrics,METRICS,table
from .cluster_metrics import draws,weighted_metrics,intervals


def assess():
    c=config();spec=read('configs/reassemble/section3_corruptions.json');run=Path(spec['run_dir']);out=run/'assessment';out.mkdir(exist_ok=True)
    frame=cohort(read('configs/reassemble/section1.json'));w=draws(frame.recording_id.to_numpy(),2000,spec['bootstrap_seed']);totals=w.sum(1)
    results={};boots={};points={};predictions={}
    for condition in spec['conditions']:
        name=condition['name'];cache=out/(name+'.json');numerical=out/(name+'_bootstrap.npz')
        with np.load(run/'predictions'/(name+'.npz')) as z:p={k:z[k] for k in z.files}
        predictions[name]=p;y=p['y'];boot={};point={}
        if cache.exists():
            results[name]=read(cache)
            with np.load(numerical) as z:boot={m:z[m] for m in z.files}
            point={m:np.array([results[name]['metrics'][m][k]['estimate'] for k in METRICS]) for m in boot}
        else:
            result={'condition':condition,'metrics':{},'paired':{},'degradation':{},'degradation_advantage':{},'weights':{},'unavailable':[]}
            for m in spec['models']:
                if not np.isfinite(p[m+'_p']).all():result['metrics'][m]=None;result['unavailable'].append(m);continue
                point[m]=metrics(y,p[m+'_p'],p[m+'_hard']);boot[m]=weighted_metrics(y,p[m+'_p'],p[m+'_hard'],w)
                result['metrics'][m]=intervals(point[m],boot[m])
                if name!='clean':result['degradation'][m]=intervals(point[m]-points['clean'][m],boot[m]-boots['clean'][m])
            for a,b in [('F5','F2'),('F6','F2'),('F2','U1')]:
                if a not in boot or b not in boot:continue
                result['paired'][a+'-'+b]=intervals(point[a]-point[b],boot[a]-boot[b])
                if name!='clean':result['degradation_advantage'][a+'-'+b]=intervals((point[a]-points['clean'][a])-(point[b]-points['clean'][b]),(boot[a]-boots['clean'][a])-(boot[b]-boots['clean'][b]))
            for m in ['F5','F6']:
                allocation=p[m+'_weights'];base=predictions['clean'][m+'_weights'] if name!='clean' else allocation
                change=allocation[:,0]-base[:,0];sample=(w@change)/totals;lo,hi=np.quantile(sample,[.025,.975])
                result['weights'][m]={'visual_mean':float(allocation[:,0].mean()),'sensor_mean':float(allocation[:,1].mean()),'visual_std':float(allocation[:,0].std()),'sensor_std':float(allocation[:,1].std()),'entropy':float(-(allocation*np.log(np.clip(allocation,1e-12,1))).sum(1).mean()),'visual_quantiles':np.quantile(allocation[:,0],[.05,.25,.5,.75,.95]).tolist(),'visual_shift':{'estimate':float(change.mean()),'lower_95':float(lo),'upper_95':float(hi)},'sensor_shift':{'estimate':float(-change.mean()),'lower_95':float(-hi),'upper_95':float(-lo)}}
            write(cache,result);np.savez_compressed(numerical,**boot);results[name]=result
        points[name]=point;boots[name]=boot
        progress('Section 3 clustered assessment: '+name)
    mechanism={}
    for family in ['V1','V2','V3','S1','S2','S3']:
        conditions=sorted([x for x in spec['conditions'] if x['family']==family],key=lambda x:x['severity']);column=0 if family[0]=='V' else 1
        high=conditions[-1]['name'];mechanism[family]={}
        for m in ['F5','F6']:
            names=['clean']+[x['name'] for x in conditions];severity=np.repeat([0]+[x['severity'] for x in conditions],len(frame))
            weight=np.concatenate([predictions[n][m+'_weights'][:,column] for n in names]);rho=float(spearmanr(severity,weight).statistic)
            shift=results[high]['weights'][m]['visual_shift' if column==0 else 'sensor_shift']
            advantage=results[high]['degradation_advantage'][m+'-F2'];absolute=results[high]['paired'][m+'-F2']
            adaptation=shift['upper_95']<0 and rho<0;outcome=advantage['AUPRC']['lower_95']>0 and advantage['AUROC']['lower_95']>-.01
            absolute_win=absolute['AUPRC']['lower_95']>0
            if adaptation and outcome:classification='ROBUSTNESS-A'
            elif adaptation:classification='ROBUSTNESS-B'
            elif absolute['AUPRC']['upper_95']<0:classification='ROBUSTNESS-D'
            else:classification='ROBUSTNESS-C'
            mechanism[family][m]={'ordered_severity_spearman':rho,'high_severity':high,'degraded_modality_weight_shift':shift,'adaptation_supported':adaptation,'smaller_degradation_supported':outcome,'absolute_AP_superiority_supported':absolute_win,'classification':classification,'level_mean_weights':[float(predictions[n][m+'_weights'][:,column].mean()) for n in names]}
    final={'conditions':results,'mechanism':mechanism,'bootstrap_replicates':2000,'conditional_on':'fixed fitted models and one deterministic corruption realization per condition','missingness':'Exact remaining-branch fallback; no information recovery; unavailable unimodal metrics undefined','claims':'Family-specific exploratory intervals; no universal or independent confirmatory claim'}
    write(run/'results.json',final)
    rows=[]
    for name,result in results.items():
        for m,values in result['metrics'].items():
            if values is None:continue
            rows.append([name,m]+[f"{values[k]['estimate']:.4f}" for k in METRICS])
    text='# SECTION 3 — Frozen-model robustness handoff\n\nSame frozen cohort/folds; clean-trained models, no corruption fitting.\n\n'+table(['Condition','Model']+METRICS,rows)
    text+='\n## Mechanism and outcome\n\nA positive mechanism requires a negative ordered-severity correlation and a negative clustered high-severity weight shift; a robustness outcome requires a positive AP degradation advantage with compatible AUROC. Absolute corrupted performance remains a separate comparison. Marginal family-specific intervals are exploratory.\n\n'
    text+=table(['Family','Gate','Spearman','Degraded weight shift [95%]','Class','Absolute AP superiority'],[[family,m,f"{x['ordered_severity_spearman']:.3f}",f"{x['degraded_modality_weight_shift']['estimate']:.4f} [{x['degraded_modality_weight_shift']['lower_95']:.4f}, {x['degraded_modality_weight_shift']['upper_95']:.4f}]",x['classification'],x['absolute_AP_superiority_supported']] for family,models in mechanism.items() for m,x in models.items()])
    text+='\n## Missing modalities\n\nEvery available fusion model returns the surviving calibrated branch, with its frozen branch threshold. This is explicit fallback, not learned reliability awareness. An unavailable unimodal model abstains. Modality-loss weight changes are enforced by the mask, not evidence of learned adaptation.\n\n## Provenance and limitations\n\nProtocol: docs/reassemble/SECTION_3_CORRUPTION_PROTOCOL.md. Config: configs/reassemble/section3_corruptions.json. Run: '+str(run)+'. Full paired intervals, clean-relative deltas and difference-in-degradation intervals are in results.json; every sample/seed weight is in predictions/. One seeded realization per severity; synthetic degradation is not a field-failure distribution. Same-cohort adaptive exploratory study; no tuning against corruption outcomes.\n'
    Path('artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md').write_text(text)
    progress('Section 3 robustness assessment complete; continue modality dropout automatically')

if __name__=='__main__':
    with threadpool_limits(limits=4,user_api='blas'):assess()
