"""All-variant reporting; conditional-on-fit, recording-cluster uncertainty."""
from pathlib import Path
import csv,json,shutil
import numpy as np
from reassemble.section1_report import metrics,METRICS
from reassemble.cluster_metrics import draws,weighted_metrics,intervals
from .common import read,write,identity

NAMES={'V0':'Full-segment mean','V1':'First half + second half','V2':'Early + middle + late','V3':'Last quarter only','V4':'Early + late','V5':'Ordered GRU64 + fixed positions'}
CLASS_NAMES={'A':'TEMPORAL STRUCTURE HELPS','B':'TEMPORAL STRUCTURE HELPS WEAKLY','C':'LATE-SEGMENT SIGNAL ONLY','D':'NO EVIDENCE TEMPORAL POOLING HELPS','E':'TEMPORAL COMPLEXITY HURTS'}

def csvout(path,rows):
 with Path(path).open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def point(y,p,h):return dict(zip(METRICS,map(float,metrics(y,p,h))))
def classify(paired):
 eligible=[k for k,v in paired.items() if v['AUPRC']['simultaneous_lower_95']>0 and v['AUROC']['lower_95']>-.01]
 if eligible==['V3']:return 'C',eligible
 if eligible:return 'A',eligible
 if any(v['AUPRC']['estimate']>0 for v in paired.values()):return 'B',[]
 if paired['V5']['AUPRC']['upper_95']<0:return 'E',[]
 return 'D',[]

def analyse(run,c,frame,fold,predictions):
 if (run/'results.json').exists():return read(run/'results.json')
 y=frame.failure.to_numpy(int);w=draws(frame.recording_id.to_numpy(),2000,c['bootstrap_seed']);boots={};summaries={};points={};paired={};folds=[];seed=[]
 for name,v in predictions.items():
  points[name]=metrics(y,v['p'],v['hard']);boots[name]=weighted_metrics(y,v['p'],v['hard'],w)
  np.testing.assert_allclose(weighted_metrics(y,v['p'],v['hard'],np.ones((1,len(y))))[0],points[name],rtol=0,atol=1e-12)
  summaries[name]=intervals(points[name],boots[name])
  seed.append({'variant':name,'base_seed':c['seed'],**dict(zip(METRICS,map(float,points[name])))})
  for k in range(5):
   m=fold==k;folds.append({'variant':name,'outer_fold':k,'n':int(m.sum()),'failures':int(y[m].sum()),**point(y[m],v['p'][m],v['hard'][m])})
 for name in ['V1','V2','V3','V4','V5']:
  diff=boots[name]-boots['V0'];paired[name]=intervals(points[name]-points['V0'],diff)
  lo,hi=np.quantile(diff[:,1],[.005,.995]);paired[name]['AUPRC'].update(simultaneous_lower_95=float(lo),simultaneous_upper_95=float(hi))
 cls,eligible=classify(paired)
 # A descriptive same-cohort winner, never used to revise grids or action rules.
 best=max(['V1','V2','V3','V4','V5'],key=lambda k:points[k][1]);fusion_variant=max(eligible,key=lambda k:points[k][1]) if cls=='A' else None
 actions=[];selective=[];rescue=[]
 for name in ['V0',best]:
  v=predictions[name]
  for action in ['pick','insert','remove','place']:
   m=(frame.action==action).to_numpy();actions.append({'variant':name,'action':action,'n':int(m.sum()),'failures':int(y[m].sum()),**point(y[m],v['p'][m],v['hard'][m])})
 for name,v in predictions.items():
  for j,level in enumerate([1.,.9,.8]):
   keep=v['retained'][j];supported=int(keep.sum())>0 and len(np.unique(y[keep]))==2
   m=point(y[keep],v['p'][keep],v['hard'][keep]) if supported else {k:None for k in METRICS}
   selective.append({'variant':name,'target_coverage':level,'actual_coverage':float(keep.mean()),'retained':int(keep.sum()),'abstentions':int((~keep).sum()),'retained_failures':int(y[keep].sum()),'failure_recall_all_failures_abstentions_as_misses':float(((y==1)&(v['hard']==1)&keep).sum()/y.sum()),**m})
 baseline=predictions['V0']['hard'];chosen=predictions[best]['hard'];rescued=(y==1)&(baseline==0)&(chosen==1);lost=(y==1)&(baseline==1)&(chosen==0)
 for rid,rows in frame.groupby('recording_id',sort=True):
  ix=rows.index.to_numpy();rescue.append({'recording_id':rid,'failures':int(y[ix].sum()),'V0_missed':int(((y[ix]==1)&(baseline[ix]==0)).sum()),'variant_missed':int(((y[ix]==1)&(chosen[ix]==0)).sum()),'rescued':int(rescued[ix].sum()),'lost':int(lost[ix].sum())})
 failure={'variant':best,'V0_false_negatives':int(((y==1)&(baseline==0)).sum()),'variant_false_negatives':int(((y==1)&(chosen==0)).sum()),'rescued_failures':int(rescued.sum()),'lost_failures':int(lost.sum()),'recordings_with_rescue':sum(r['rescued']>0 for r in rescue),'recordings_with_loss':sum(r['lost']>0 for r in rescue)}
 result={'class':cls,'class_name':CLASS_NAMES[cls],'best_descriptive_variant':best,'eligible_variants':eligible,'fusion_variant':fusion_variant,'metrics':summaries,'paired_differences':paired,'failure_analysis':failure,'fold_metrics':folds,'seed_metrics':seed,'action_metrics':actions,'selective_metrics':selective,'bootstrap_replicates':2000,'bootstrap_seed':c['bootstrap_seed'],'multiplicity':'Bonferroni percentile intervals for five AP contrasts, quantiles .005/.995; AUROC noninferiority uses marginal 95% lower > -0.01. Same-cohort exploratory selection remains.'}
 write(run/'results.json',result)
 for name,rows in [('fold_metrics.csv',folds),('seed_metrics.csv',seed),('action_metrics.csv',actions),('selective_metrics.csv',selective),('failure_rescue_by_recording.csv',rescue)]:csvout(run/name,rows)
 return result

def fusion_analysis(run,c,frame,new,original):
 path=run/'fusion/results.json'
 if path.exists():return read(path)
 y=frame.failure.to_numpy(int);w=draws(frame.recording_id.to_numpy(),2000,c['bootstrap_seed']);p1=metrics(y,new['p'],new['hard']);p0=metrics(y,original['p'],original['hard']);b1=weighted_metrics(y,new['p'],new['hard'],w);b0=weighted_metrics(y,original['p'],original['hard'],w)
 result={'new':intervals(p1,b1),'original_F2':intervals(p0,b0),'paired':intervals(p1-p0,b1-b0),'limitations':'Triggered and selected on same cohort; conditional exploratory follow-up, not independent confirmation. No outer-test OOF used to fit weights.'}
 result['per_fold']=[{'fold':k,'new':point(y[m],new['p'][m],new['hard'][m]),'original_F2':point(y[m],original['p'][m],original['hard'][m])} for k in range(5) if (m:=new['fold']==k).any()]
 write(path,result);return result

def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
def fmt(v):return f"{v['estimate']:.4f} [{v['lower_95']:.4f}, {v['upper_95']:.4f}]"

def finish(run,c,frame,predictions,r,fusion):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,3,figsize=(13,7));curves=[]
 for ax,name in zip(axes.flat,NAMES):
  for k in range(5):
   info=read(run/'fits'/name/f'outer{k}/refit/complete.json');loss=info['loss_by_epoch'];ax.plot(range(1,len(loss)+1),loss,label=f'fold{k}')
   curves.extend({'variant':name,'outer_fold':k,'stage':'refit','epoch':i+1,'training_loss':float(v)} for i,v in enumerate(loss))
  ax.set_title(name+' '+NAMES[name]);ax.set_xlabel('Epoch');ax.set_ylabel('Weighted training BCE')
 axes.flat[0].legend();fig.tight_layout();fig.savefig(run/'learning_curves.png',dpi=140);plt.close(fig)
 if not (run/'learning_curves.csv').exists():csvout(run/'learning_curves.csv',curves)
 params={name:read(run/'branches'/name/'outer0/complete.json')['parameters'] for name in NAMES}
 main=table(['Variant',*METRICS],[[k,*[fmt(r['metrics'][k][m]) for m in METRICS]] for k in NAMES])
 comparison=table(['Variant − V0','Δ AUROC (95%)','Δ AUPRC (95%)','AP simultaneous lower'],[[k,fmt(v['AUROC']),fmt(v['AUPRC']),f"{v['AUPRC']['simultaneous_lower_95']:.4f}"] for k,v in r['paired_differences'].items()])
 best=r['best_descriptive_variant'];f=r['failure_analysis'];cls=r['class'];claim=f"In this separate exploratory study on the same 4,530 segments and recording-disjoint folds, the predeclared temporal-aggregation comparison was classified as {r['class_name']}. The highest pooled AUPRC point estimate among temporal variants was {best}; this descriptive selection is not independent confirmation."
 failures=[p.name for p in run.glob('failure_*.json')]
 sections=[('A. Motivation from human review','Aggregate motivation only: 59/64 judgeable, 57/59 agreement among determinate judgements, 5 indeterminate, two disagreements. Ambiguity was more common among recorded failure cases. Human identities/ratings/flags did not enter any fit, fold, feature, threshold or selection. No adjudication or relabeling is implied.'),('B. Hypothesis','Whole-segment averaging may dilute signals concentrated early/late. This concerns retrospective completed-action classification, not prediction before failure.'),('C. Historical control reproduction',json.dumps(read(run/'control_parity.json'),indent=2)),('D. Temporal aggregation variants',table(['Variant','Definition','Trainable parameters'],[[k,NAMES[k],params[k]] for k in NAMES])),('E. Parameter/training fairness','V0 uses the exact original head/fitter and historical pooled features. V1–V4 use shared 896→128 projection per temporal bin, then concatenate small projected bins; classifier increases by at most 256 weights. All use training-only whole-segment mean moments, weighted BCE, AdamW .001/decay .001, batch128, dropout .1, clipping1. V5 is exactly one GRU64 layer with fixed sinusoidal position, 64-D projection and mean recurrent-output pooling; its inductive bias/capacity differ, so no pure order-causality claim. Fixed epoch grids: V0–V4 [5,10], V5 [5,10,20], mean inner AP selection. Historical single-seed policy retained, with original fold-specific offsets; no three-seed robustness claim. Inner loss histories and AP at candidate budgets, selected/refit checkpoints and predictions are retained under fits/ and branches/.'),('F. Main metrics',main),('G. Paired comparisons',comparison+'\n'+r['multiplicity']+'\nFold-level and historical-single-seed results are in fold_metrics.csv and seed_metrics.csv. Intervals condition on fits and do not include refitting or independent-site uncertainty.'),('H. Action-level analysis',table(['Variant','Action','n','Failures','AUROC','AUPRC'],[[v['variant'],v['action'],v['n'],v['failures'],f"{v['AUROC']:.4f}",f"{v['AUPRC']:.4f}"] for v in r['action_metrics']])+'\nV0 and the highest pooled-AP temporal variant only; descriptive, not action-specific model selection.'),('I. Failure-side rescue analysis',json.dumps(f,indent=2)+'\nPer-recording counts are in failure_rescue_by_recording.csv. No cross-reference to human-reviewed IDs. Failure recall/precision for all variants appear in main metrics.'),('J. Selective-prediction diagnostic','All six models: selective_metrics.csv. Nominal coverage100/90/80%; confidence=|p−0.5|. Cutoffs use outer-training calibrated selected inner-OOF predictions; ties retained. Actual outer coverage can differ. Calibrator/selection uses those training rows, so inner coverage estimates are not unbiased. AUROC/AP and failure recall are reported on retained rows; additional overall failure recall counts abstentions as misses. Abstention is a computational decision, not a human uncertainty label. No claim that it detects the human-reviewed ambiguous clips.'),('K. Fusion follow-up, if triggered',('Exactly one static Section1B stacker follow-up triggered for '+str(r['fusion_variant'])+'. Sensor calibrated probabilities and exact original nested partitions are reused with verified identity. Visual sub-inner selection/refits exclude meta-assessment recordings. Original F2 parity checked before comparing.\n'+table(['Metric','New − original F2'],[[m,fmt(fusion['paired'][m])] for m in ['AUROC','AUPRC']])) if fusion else 'Not triggered: result class is '+cls+', not A. No fusion fit run.'),('L. Failed variants','Every variant is retained above, including deterioration and unresolved differences. Runtime failures retained: '+(', '.join(failures) if failures else 'none')+'. No budgets expanded, architectures added or losing result hidden.'),('M. Interpretation',r['class_name']+'. Class A uses multiplicity-adjusted positive AP lower bound and marginal AUROC lower >−.01. Sole qualifying last-quarter improvement is class C. B includes gains unresolved after multiplicity. These are bounded operational classifications, not universal architecture statements.'),('N. Exact thesis-safe claim',claim),('O. Claims not supported','No prospective warning, physical-event timing accuracy, corrected labels, independently confirmed winner, universal temporal superiority, generalization to unseen objects/sites, validation from reviewer IDs, adaptive gate improvement or audio claim.'),('P. Limitations','Same cohort already examined in completed studies and additional improvements; hypothesis/variants declared before this follow-up’s outcomes, but this is not an independent prospective validation set. The human review is a small balanced qualitative sample. One historical seed; shared scene/day dependence may remain beyond recording groups. More bins preserve both temporal location and extra information, and V5 changes the head family; no causal mechanism attribution. Limited budgets may underfit. GPU-compatible runtime must reproduce historical control. Additional trainable projections introduce a small documented capacity difference.'),('Q. Provenance','Run: `'+str(run)+'`. Exact request: REQUEST.md; config.json; protocol.md; source_signature.json; source/; runtime.json; cache_preflight.json; cohort_identity.csv; control_*parity.json; preservation_before/after.json; output_manifest.json. Historical evidence/source config identities in registration.json. Historical V0 uses frozen mean values (CUDA temporal reduction); cached sequence NumPy re-averaging is checked at existing feature tolerance5e−5, avoiding an unannounced floating-point change to the control. No re-extraction. Raw preservation verifies size/mtime and known audited hashes/timestamps, not a new full HDF5 payload hash. Existing additional-run snapshot begins only after Task4 completes, so its authorized ongoing progress is not mistaken for our modification.'),('R. Recommended thesis placement','Place in an explicitly exploratory follow-up subsection after the frozen core findings and human-review limitations. Keep the completed core results unchanged. '+('Describe the single conditional static-fusion comparison with the same-cohort selection caveat.' if fusion else 'Do not claim a downstream fusion benefit from this experiment.'))]
 text='# Boundary-aware visual pooling handoff\n\n**EXPLORATORY — '+r['class_name']+'**\n\n'+'\n\n'.join('## '+title+'\n\n'+body for title,body in sections)+'\n'
 story='# Boundary-aware visual storyline addendum\n\n'+ '\n\n'.join('## '+h+'\n\n'+v for h,v in [('ASSUMPTION','Whole-segment mean pooling may dilute failure evidence near boundaries.'),('QUESTION','Does one of five fixed temporal alternatives improve on the original mean-pooling branch?'),('WHY IT MATTERED','Aggregate blinded review exposed outcome ambiguity; reviewed identities were never used for modelling.'),('METHOD','Fixed16-frame embeddings; exact frozen cohort/folds/calibration; historical control gate; bounded heads; paired recording bootstrap; multiplicity acknowledged.'),('RESULT',r['class_name']+'; see handoff for all variants and paired intervals.'),('INTERPRETATION',claim),('STATUS','Complete bounded exploratory follow-up; historical studies remain frozen.'),('CONSEQUENCE','Include as exploratory thesis evidence. '+('One static-fusion follow-up was run.' if fusion else 'No fusion follow-up was authorized by the observed class.')+' STOP; no additional architecture or budget search.')])+'\n'
 stat='BOUNDARY-AWARE VISUAL EXPERIMENT COMPLETE\n\n'+f"Best predefined temporal variant by pooled AP: {best}.\nV0: AP {r['metrics']['V0']['AUPRC']['estimate']:.6f}, AUROC {r['metrics']['V0']['AUROC']['estimate']:.6f}.\n{best}: AP {r['metrics'][best]['AUPRC']['estimate']:.6f}, AUROC {r['metrics'][best]['AUROC']['estimate']:.6f}.\nPaired AP: {fmt(r['paired_differences'][best]['AUPRC'])}; AUROC: {fmt(r['paired_differences'][best]['AUROC'])}.\nFailures rescued: {f['rescued_failures']}; lost: {f['lost_failures']}.\nFusion triggered: {fusion is not None}; variant: {r['fusion_variant']}.\nClass {cls}: {r['class_name']}.\nThesis: separate exploratory subsection; preserve historical conclusions.\nRun: {run}\n"
 reports={'BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md':text,'BOUNDARY_AWARE_VISUAL_STORYLINE_ADDENDUM.md':story,'BOUNDARY_AWARE_VISUAL_STATUS.md':stat}
 for name,content in reports.items():
  for p in [run/name,Path('artifacts/reassemble/reports')/name]:
   if p.exists():assert p.read_text()==content,'Existing final report differs'
   else:p.write_text(content)
