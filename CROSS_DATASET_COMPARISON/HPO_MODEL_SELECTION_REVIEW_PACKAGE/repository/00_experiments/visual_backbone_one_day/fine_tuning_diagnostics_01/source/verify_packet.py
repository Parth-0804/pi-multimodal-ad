"""Separate stdlib-only arithmetic and preservation self-check, without fitting or model imports."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import json
import math
import subprocess

OUT=Path(__file__).resolve().parents[1]
REPO=Path(__file__).resolve().parents[4]
CFG=json.loads((OUT/'config/analysis_config.json').read_text())
STUDY=REPO/CFG['study_root']


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def exact_ap(records, column):
    # Independent implementation: integrate precision against recall increments
    # over complete groups of equal predicted score, using only the standard library.
    ordered=sorted(records,key=lambda r:-float(r[column]))
    positives=sum(int(r['failure']) for r in ordered)
    tp=0;previous_tp=0;answer=0.
    for index,row in enumerate(ordered,1):
        tp+=int(row['failure'])
        if index==len(ordered) or float(ordered[index][column])!=float(row[column]):
            answer+=(tp-previous_tp)*tp/index/positives
            previous_tp=tp
    return answer


def main():
    manifest=json.loads((OUT/'provenance/input_manifest.json').read_text())
    for name,meta in manifest.items():
        data=(REPO/name).read_bytes()
        assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
    metrics=rows(OUT/'tables/assessment_metrics.csv')
    checks=[];paired={}
    for condition in CFG['conditions']:
        data=[]
        for fold in range(1,6):
            data+=rows(STUDY/condition/f'fold_{fold:02}'/'assessment_predictions.csv')
        assert len(data)==len({r['sample_id'] for r in data})==4530
        assert sum(int(r['failure']) for r in data)==509
        assert len({r['recording_id'] for r in data})==148
        paired[condition]={r['sample_id']:r for r in data}
        for branch,col in [('visual','p_visual'),('sensor','p_sensor'),('F2','p_fused')]:
            score=exact_ap(data,col)
            brier=sum((float(r[col])-int(r['failure']))**2 for r in data)/len(data)
            target=next(r for r in metrics if r['condition']==condition and r['scope']=='pooled' and r['branch']==branch)
            assert abs(score-float(target['AP']))<1e-12
            assert abs(brier-float(target['Brier']))<1e-12
            checks.append({'condition':condition,'branch':branch,'AP':score,'Brier':brier})
    changes=rows(OUT/'tables/paired_AP_and_Brier_changes.csv')
    for filename in ['recording_AP_contributions.csv','action_AP_contributions.csv']:
        data=rows(OUT/'tables'/filename)
        for frames in [16,32]:
            for branch in ['visual','F2']:
                actual=sum(float(r[branch+'_AP_contribution_change']) for r in data if int(r['frames'])==frames)
                target=next(float(r['AP_change']) for r in changes if int(r['frames'])==frames and r['branch']==branch and r['scope']=='pooled')
                assert abs(actual-target)<1e-12
    def selected(data,col,fraction):
        selected_ids=set()
        for fold in range(1,6):
            group=[r for r in data if r['fold_name']==f'fold_{fold:02}']
            selected_ids.update(r['sample_id'] for r in sorted(group,key=lambda r:(-float(r[col]),r['sample_id']))[:math.ceil(len(group)*fraction)])
        return selected_ids
    budgets=rows(OUT/'tables/fixed_budget_complementarity.csv')
    for row in budgets:
        frames=int(row['frames']);fraction=float(row['top_fraction_within_fold']);col='p_visual' if row['branch']=='visual' else 'p_fused'
        a=list(paired[f'frozen_{frames}_frames'].values());b=list(paired[f'fine_tuned_{frames}_frames'].values())
        pos={r['sample_id'] for r in a if int(r['failure'])==1}
        sensor=selected(a,'p_sensor',fraction);frozen=selected(a,col,fraction);tuned=selected(b,col,fraction)
        assert len(pos&frozen)==int(row['frozen_captured_failures'])
        assert len(pos&tuned)==int(row['fine_tuned_captured_failures'])
        assert len((pos-sensor)&frozen)==int(row['frozen_captured_sensor_missed_failures'])
        assert len((pos-sensor)&tuned)==int(row['fine_tuned_captured_sensor_missed_failures'])
    before=json.loads((OUT/'provenance/study_file_metadata_before.json').read_text())
    after={str(p.relative_to(STUDY)):{'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in STUDY.rglob('*') if p.is_file()}
    assert before==after,'Original study file metadata changed'
    status=subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'],cwd=REPO)
    (OUT/'provenance/git_status_after.txt').write_bytes(status)
    diff=subprocess.check_output(['git','diff','--stat'],cwd=REPO)
    (OUT/'provenance/git_diff_stat_after.txt').write_bytes(diff)
    prefix=str(OUT.relative_to(REPO))+'/'
    def unrelated_status(data):
        return [line for line in data.decode().splitlines() if prefix not in line]
    assert unrelated_status(status)==unrelated_status((OUT/'provenance/git_status_before.txt').read_bytes()),'Unrelated Git status changed'
    assert diff==(OUT/'provenance/git_diff_stat_before.txt').read_bytes(),'Tracked diff stat changed'
    proc=subprocess.run(['git','diff','--check'],cwd=REPO,capture_output=True,text=True)
    (OUT/'checks/git_diff_check.log').write_text(proc.stdout+proc.stderr+f'Exit code: {proc.returncode}\n')
    assert proc.returncode==0
    new_bytes=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    assert new_bytes<CFG['limits']['maximum_new_bytes']
    result={'passed':True,'review_type':'Second implementation self-check; not independent scientific review',
        'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'input_files_hash_verified':len(manifest),
        'pooled_metrics_independently_reproduced':checks,'all_AP_group_contributions_reconcile':True,
        'all_rank_budget_counts_independently_reproduced':True,'original_study_files_metadata_unchanged':len(before),
        'unrelated_Git_status_unchanged':True,'tracked_diff_stat_unchanged':True,'git_diff_check_exit':0,'diagnostic_bytes_before_final_manifest':new_bytes,
        'scope':'No models or raw data loaded; CPU saved-result arithmetic only',
        'limits':'Metadata preservation is not a full hash scan of unread large historical artifacts.'}
    (OUT/'checks/final_self_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
