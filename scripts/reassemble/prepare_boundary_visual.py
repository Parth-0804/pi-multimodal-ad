"""Register and validate a new boundary-aware visual run without starting training."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,shutil
from reassemble.boundary_visual.common import write,identity,status
from reassemble.boundary_visual.runner import signature
from reassemble.boundary_visual.preflight import load
from reassemble.boundary_visual.models import make

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--request',type=Path,required=True);a=parser.parse_args()
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=Path('runs/reassemble/additional_improvements_executed')/stamp/'boundary_aware_visual';run.mkdir(parents=True,exist_ok=False)
 config={'run_dir':str(run),'section1_config':'configs/reassemble/section1.json','sequence_cache':'runs/reassemble/additional_improvements_executed/20260928T000346Z/01_temporal_visual/features','task4_dependency':'runs/reassemble/additional_improvements_executed/20260928T000346Z','seed':20260927,'epochs':{f'V{i}':([5,10,20] if i==5 else [5,10]) for i in range(6)},'bootstrap_seed':20260927+50000,'bootstrap_replicates':2000,'probability_parity_tolerance':1e-5,'feature_parity_tolerance':5e-5,'minimum_free_GiB':20,'large_copy_or_extraction':False,'variants':{'V0':'Historical mean+128 head','V1':'shared128 projection: means [0:8],[8:16]','V2':'shared128 projection: means [0:4],[4:12],[12:16]','V3':'shared128 projection: mean [12:16]','V4':'shared128 projection: means [0:4],[12:16]','V5':'896->64 ReLU/dropout0.1; fixed sinusoidal position; one GRU64 layer; mean outputs -> binary linear'},'multiple_seeds':'Historical Section1 one-base-seed policy with original fold offsets; not later 3-seed Task1 policy','decision':'Five AP contrasts Bonferroni percentile .005/.995 positive; marginal AUROC lower95 > -0.01. Sole qualifying V3 -> C; otherwise eligible -> A; unresolved positive point -> B; no positive point and V5 upper95 AP < 0 -> E; else D. Exactly one static fusion only for A.','selection':'All models reported. Highest pooled outer AP is descriptive strongest; for conditional fusion choose highest pooled AP among A-eligible variants, fixed name order for ties. Selection on this previously viewed cohort is exploratory and not independent confirmation.','selective':'abs(p-0.5), training selected inner-OOF calibrated p cutoffs at quantiles0,.1,.2; >= retains ties; actual outer coverage reported','human_case_inputs':[],'estimated_additional_disk_GiB_upper_budget':2,'automatic_boot_restart':False}
 write(run/'config.json',config);shutil.copyfile(a.request,run/'REQUEST.md')
 refs=['AGENTS.md','configs/reassemble/section1.json','configs/reassemble/section1b.json','configs/reassemble/section2.json','artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md','artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md','artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md','artifacts/reassemble/reports/FINAL_REASSEMBLE_HANDOFF.md']
 write(run/'registration.json',{'UTC':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'dirty_worktree':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),'request':identity(run/'REQUEST.md'),'read_evidence':[identity(Path(p)) for p in refs],'human_motivation_aggregate_only':{'presented':64,'determinate':59,'agreement_determinate':57,'indeterminate':5,'disagreement_determinate':2},'parameters':{'V0':114945,**{f'V{i}':sum(p.numel() for p in make(f'V{i}').parameters()) for i in range(1,6)}},'scope':'Separate exploratory follow-up; do not restart paused Task1 or alter running Task4.'})
 protocol='''# Preregistered boundary-aware visual experiment

The exact user request is REQUEST.md. This registration precedes this follow-up’s trained model outcomes. Prior same-cohort results have already been seen, so this is exploratory, not an independently prospective validation study.

## Fixed implementation

V0 is the unchanged Section1 VisualHead fitter on historical GPU-reduced means. Cache identities, frame indices/timestamps, row/segment mapping, source audited hashes, model weights/preprocessing and 5×4 fold identities must pass preflight. Sequence re-averaging uses NumPy for variants and is checked at the existing5e-5 feature tolerance. The historical control uses exact original means so floating-point reduction does not silently redefine it. V0 must reproduce probabilities within1e-5, selected budgets and hard predictions exactly, and metrics within1e-5 across all five folds before any variant runs.

V1 means[0:8],[8:16]; V2[0:4],[4:12],[12:16]; V3[12:16]; V4[0:4],[12:16]. V1–V4 share a896→128 ReLU/dropout.1 projection across bins, followed by concatenation and a binary linear classifier; at most256 additional parameters over V0. V5 is one GRU64 layer, 896→64 projection, fixed sinusoidal positional encoding, mean recurrent-output pooling, binary linear classifier; one architecture only. All standardization uses fitting-partition whole-segment mean moments; no fitted statistics from assessment rows.

Historical weighted BCE, AdamW lr.001/weight decay.001, batch128, clipping1, float32 training, deterministic CUDA, torch threads4 and BLAS16. Epoch grids V0–V4[5,10]; V5[5,10,20]. Mean four-inner-fold AP selects budget; exact historical one-base-seed policy and fold offsets retained. No extra epochs even if caps are selected. Calibrator and balanced-accuracy threshold use selected training inner-OOF logits only. Loss curves, candidate-validation AP, folds, raw/calibrated predictions, normalization and checkpoint identities are saved. No human-review identities, scores, flags or ratings enter the modelling code.

## Analysis and gate

All4530 segments and509 failures from148 recordings; failure positive. Original2000 paired recording bootstrap draws with seed20260927+50000, fixed15-bin ECE. Eight metrics, all five temporal-versus-V0 contrasts, per-fold and single-seed evidence. Five AP contrasts additionally receive Bonferroni percentile intervals at.005/.995. A variant is eligible only if adjusted AP lower>0 and marginal AUROC lower95>−.01; the latter margin follows the earlier noninferiority convention. If onlyV3 is eligible, classC; other eligible sets classA; otherwise any positive AP point estimate givesB (possibly unresolved only after multiplicity), otherwise significantly negative V5 AP givesE, elseD. Report marginal95% intervals too, and explain classification; do not call a positive point estimate confirmed. AP gain.01 is an optional contextual practical reference, not a post-hoc tuning criterion.

The strongest temporal variant for descriptive action/rescue analysis is the highest pooled AP amongV1–V5. No action-specific selection. Failure rescue and lost-failure counts use original training-selected decision thresholds, broken down by recording. No reviewed-case cross-reference. Selective predictions for all models use |p−.5| cutoffs at outer-training selected/calibrated inner-OOF confidence quantiles0/.1/.2, retain ties, report realized coverage, retained-case metrics and all-failure recall treating abstentions as missed. These cutoffs do not identify human-rated ambiguity and their training coverage is not an unbiased estimate.

Exactly one conditional Section1B C=1 static logistic stacker comparison runs only for classA, choosing highest pooled AP among eligible variants (fixed name order for ties). Original sensor branch probabilities and the exact saved sub-inner recording partitions are reused. New visual branch predictions for fusion training come from full sub-inner selection/calibration/refit excluding the assessed inner recording. No existing outer-test OOF scores fit weights. Reproduce original F2 first. Conditional choice remains same-cohort exploratory selection, not independent confirmation. No new gates or combined winners from other tasks.

## Resource, preservation and stopping

CPU preflight is allowed during Task4. Training waits for Task4’s successful completion receipt and released coordinator lock. Task1 stays paused. No cache extraction, fine-tuning, audio, sensor refitting, new folds or annotation changes. Budget up to2GiB new output, free space>=20GiB. Fits checkpoint into this new run; completed artifacts have identity/signature guards. Incomplete attempt subdirectories are retained and retried in a fresh subdirectory. Pause between fit/stage units at05:30 Europe/Berlin or SIGTERM; an individual fit may run past that boundary. A hard daily VM reset cannot be survived in memory; no boot automation is claimed. Run continuation and exact resume command are saved.

Snapshot all pre-existing completed evidence and the existing additional-improvements run only after Task4 ends, separating authorized Task4 mutations from this experiment. Small files are hashed; large cache/checkpoint/raw payloads use size/mtime, plus exact cache/model source hashes in preflight. This is not a fresh full raw-HDF5 content rehash. No source files or artifacts of past experiments are modified. Stop on cache mismatch, control mismatch, invalid split, failed Task4 dependency, numerical failure, low storage or preservation mismatch. Do not silently change tolerance or protocol.

Publish handoff sectionsA–R, storyline addendum and final COMPLETE status only after all required stages and preservation checks pass. Otherwise retain an explicit blocked/paused status. Stop after the bounded report. External master Reasoning Record remains untouched.
'''
 (run/'protocol.md').write_text(protocol)
 try:
  status(run,'PREFLIGHT','Checking existing sequence cache on CPU; no training started')
  load(run,publish=True)
 except Exception as e:
  status(run,'BLOCKED_REQUIRES_REVIEW',repr(e));write(run/'preflight_failure.json',{'type':type(e).__name__,'error':str(e)});print('RUN',run,flush=True);raise
 sig=signature();write(run/'source_signature.json',sig);(run/'source').mkdir()
 for item in sig:
  target=run/'source'/item['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(item['path'],target)
 shutil.copyfile(__file__,run/'source/prepare_boundary_visual.py')
 status(run,'READY_TO_QUEUE','Cache preflight passed; training must wait for successful Task4 completion')
 print('RUN',run,flush=True)
if __name__=='__main__':main()
