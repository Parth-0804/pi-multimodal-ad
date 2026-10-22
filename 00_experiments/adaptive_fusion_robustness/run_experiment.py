"""Bounded foreground entry point for this controlled adaptive-fusion study."""
import argparse,os,sys,subprocess,json,fcntl,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['PYTHONDONTWRITEBYTECODE']='1'
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[n]='8'
for name,leaf in [('HF_HOME','huggingface'),('TORCH_HOME','torch'),('XDG_CACHE_HOME','xdg'),('MPLCONFIGDIR','matplotlib'),('TMPDIR','tmp')]:
 p=ROOT/'results/run_01/cache'/leaf;p.mkdir(parents=True,exist_ok=True);os.environ[name]=str(p)
cpus=list(range(4,12));assert set(cpus)<=os.sched_getaffinity(0);os.sched_setaffinity(0,cpus)
sys.path.insert(0,str(ROOT/'code'))
from common import *
def tests():
 command=[sys.executable,'-B','-m','unittest','discover','-s',str(STUDY/'tests'),'-v'];p=subprocess.run(command,cwd=REPO,text=True,capture_output=True);(RUN/'checks/focused_tests.txt').write_text(p.stdout+p.stderr)
 from study import source_identity
 write(RUN/'checks/tests.json',{'passed':p.returncode==0,'command':['ma_thesis_env/bin/python','-B','-m','unittest','discover','-s','00_experiments/adaptive_fusion_robustness/tests','-v'],'returncode':p.returncode,'sources':source_identity()});assert p.returncode==0,p.stderr

def lock_protocol():
 from study import source_identity
 path=RUN/'config/protocol_lock.json'
 if path.exists():
  from study import check_lock
  check_lock();return
 assert read(RUN/'checks/audit_decision.json')['passed'];t=read(RUN/'checks/tests.json');assert t['passed'] and t['sources']==source_identity()
 a=read(RUN/'checks/workload_admission.json');prefix=a['selected_prefix'];assert prefix,'NO_COMPLETE_FOLD_WITHIN_BUDGET';estimate=next(x for x in a['estimates'] if x['fold_prefix']==prefix);assert estimate['seconds_with_30pct_margin']<remaining(),'WORKLOAD_NO_LONGER_FITS'
 assert not list((RUN/'predictions').glob('**/predictions.csv')) and not list((RUN/'fusion_fits').glob('**/components.json'))
 c=config();c.update(status='PROTOCOL_LOCKED',locked_folds=prefix,coverage='PARTIAL_COVERAGE_PILOT' if len(prefix)<5 else 'FIVE_FOLDS',initial_assessment_generated=False);write(RUN/'config/resolved_config.json',c)
 text=f'''# Locked controlled adaptive-fusion protocol

Exploratory, DEVELOPMENT-EXPOSED completed high-level action failure classification. Native failure=1-success. Cohort is the exact 4,530-row encoder-study common cohort; no relabeling or exclusions. Locked assessment folds: {prefix}. This prefix was chosen exclusively from verified artifact availability and G-only CPU end-to-end timings, before new assessment. Other folds are untested. Exact rows/frames/roles are in provenance/cohort_and_frames.json and fit_partitions.json.

Use all saved CNN-only inner and outer roles from the completed encoder study. Original frozen 16-frame CNN, pooled representation, sensor statistics/classifier, normalizers and calibrators remain fixed. No encoder/fine-tuning/detector/decoder/temporal-transformer execution. Reuse historical clean-trained F2 per selected fold. Inner OOF prediction recordings exclude each role's G and C, and all exclude outer E. Do not reuse old noise assessment predictions for training. Each fold trains separately on its own T only.

Three new unweighted-class logistic models, C=1, lbfgs, max_iter=2000, tol=1e-4, random_state=42, threshold=.5, no fusion calibrator: static_augmented=[pV,pS]; quality_additive=[pV,pS,q]; quality_interaction=[pV,pS,q,pV*q,pS*q]. Eight exact quality formulas and their missing-data behavior are frozen in config/quality_definitions.json and code/quality_fusion.py. Weighted q normalizer fitted only on that fold's augmented OOF rows, SD<=1e-6 replaced by1, standardized q clipped[-10,10]; branch probabilities unstandardized. These are observable input proxies, not validated reliability or causal trust percentages.

Each T action supplies three variants with total weight1: clean .5, image .25, sensor .25. Training seed50101 deterministically hashes sample identity and modality to a uniform family/level choice: image Gaussian .02/.05/.10 or frame loss .1/.3/.5; sensor Gaussian .1/.5/1 or channel loss .1/.3/.5. The model never receives corruption name, severity, seed, identity, correctness, pristine counterpart or labels as quality input. Corruption acts on received native pixels/signals. Image Gaussian clipped[0,1] then nearest uint8 conversion before original processor; blur reflect radius ceil(3sigma). Native missing-time masks cannot be interpolated away. Sensor Gaussian scales are population SD from the applicable branch G intervals only; each action contributes its finite interval once. All variants retain their parent's partition.

Assessment seeds60101,60102,60103, disjoint from training. Primary image/sensor Gaussian families each have3 severities x3 realizations. Secondary blur sigma1/2/4 once and sensor time loss .1/.3/.5 x3 realizations, excluded from augmentation fitting. Clean once. Image absence -> saved sensor branch, sensor absence -> saved visual branch for every fusion model; both absent -> explicit unavailable, separately reported. Total34 realization rows per E action. Unchanged branches must match exactly; do not drop failed cases. Frozen features can be cached only with exact source/input, transform, weights, processor and applicable scale identities.

Fit all selected per-fold fusion components and hash their lock BEFORE assessment. No settings/folds/models selected from new scores. No hyperparameter/architecture search or response to unfavorable results. Primary: AP(quality_interaction)-AP(static_augmented), independently per fold/family/severity/repeat, average repeats -> severities -> families -> matched folds equally. Pooled outer AP separately. Secondary: interaction-minus-additive, augmented-static-minus-historical, clean differences against both static baselines, per-family/severity, unimodal context, AUROC/Brier/precision/recall/confusion at .5, worst-family AP. Paired2000 recording-cluster draws within folds, seed314159; same multiplicities for all models/variants, no repeated corruptions treated as independent subjects. Conditional fixed-fit/fixed-realization uncertainty; secondary intervals unadjusted. Zero clean degradation margin for a no-clean-cost claim; nonsignificance is not no harm.

Resources: new immutable24h clock, initial audit allowance120s deducted, final3h reporting reserve, CPU-only8 threads on cores4..11, no GPU allocation, no interruption of the running workflow. Monitored16GiB process RSS,30GiB study storage,10GiB filesystem reserve. All caches/output stay in this study. No packages/data/weights downloaded or installed. At most two documented technical repairs, no scientific setting changes or deadline extension. Stop fitting/inference at scientific cutoff and report actual partial coverage. Never change older deadlines or STOP markers. Historical Task4 excluded.

Conclusions restricted to fixed fitted branches, chosen pilot recordings, augmentation and faults. No independent-dataset, online/early-detection, deployment, causal or universal robustness claim. A positive primary interval supports only the predefined mixture; coefficient-interaction evidence additionally requires comparison to additive quality.
'''
 (RUN/'PROTOCOL.md').write_text(text)
 write(path,{'locked_utc':utc(),'config_sha256':sha(RUN/'config/resolved_config.json'),'protocol_sha256':sha(RUN/'PROTOCOL.md'),'quality_definitions_sha256':sha(RUN/'config/quality_definitions.json'),'sources':source_identity(),'upstream_fit_audit_sha256':sha(RUN/'checks/fitted_component_audit.json'),'clock_sha256':sha(RUN/'config/clock.json'),'assessment_existing':False,'fusion_models_existing':False});state('PROTOCOL_LOCKED',locked_folds=prefix,coverage=c['coverage'])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['audit','test','benchmark','lock','run','resume','evaluate','report','package','status']);args=parser.parse_args()
 if args.command=='status':print(json.dumps(read(RUN/'progress.json'),indent=2));return
 with (RUN/'writer.lock').open('a') as owner:
  fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   if args.command=='audit':
    from audit import main as audit
    from audit_images import main as images
    audit();images()
   elif args.command=='test':tests()
   elif args.command=='benchmark':
    from benchmark_workload import main as benchmark
    benchmark()
   elif args.command=='lock':lock_protocol()
   elif args.command in ['run','resume']:
    lock_protocol()
    from study import run
    from metrics import evaluate
    from recalculate import main as recalculate
    from report import report,package
    run();evaluate();recalculate();state('COMPLETE_ON_PILOT_COVERAGE' if len(config()['locked_folds'])<5 else 'COMPLETE',new_training_started=True,new_fusion_models=3*len(config()['locked_folds']));report();package()
   elif args.command=='evaluate':
    from metrics import evaluate
    evaluate()
   elif args.command=='report':
    from report import audit_report,report
    audit_report();report()
   elif args.command=='package':
    from report import package
    package()
  except BaseException as exc:
   failures=read(RUN/'progress.json').get('technical_failures',[]);failures.append({'utc':utc(),'command':args.command,'exception':repr(exc)});state('BLOCKED',technical_failures=failures,blocker=repr(exc));traceback.print_exc();raise
if __name__=='__main__':main()
