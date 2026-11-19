from pathlib import Path
import csv,json,hashlib,collections,shutil
from datetime import datetime,timezone
root=Path('artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z')
dest=root/'04_human_review/submissions/2026-09-29T151804.919866_0000_8bd29f60'
original=Path('artifacts/thesis/HUMAN_REVIEW_INTERFACE/reviewer_A_completed_2026-09-29T15-15-37-443Z.csv')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readcsv(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
rows=readcsv(dest/'reviewer_1_submitted.csv')
blank=readcsv(Path('../datasets/REASSEMBLE/cache/final_validity_audit/20260928T032231Z/blind_review/reviewer_A_blank.csv'))
assert [(r['review_id'],r['action'],r['clip_file']) for r in rows]==[(r['review_id'],r['action'],r['clip_file']) for r in blank]
key={r['review_id']:r for r in readcsv(Path('../datasets/REASSEMBLE/cache/final_validity_audit/20260928T032231Z/private/source_label_key.csv'))}
analysis=json.loads((dest/'analysis.json').read_text());reported=analysis['reviewers'][0]
assert digest(original)==digest(dest/'reviewer_1_submitted.csv')==analysis['submission_hashes'][0]['sha256']
counts=collections.Counter();actions={};flags=[]
for r in rows:
 target='failure' if int(float(key[r['review_id']]['failure']))==1 else 'success'
 outcome='indeterminate' if r['judged_outcome']=='cannot_determine' else ('agreement' if r['judged_outcome']==target else 'disagreement')
 counts[outcome]+=1;actions.setdefault(r['action'],collections.Counter())[outcome]+=1
 reasons=[]
 if outcome!='agreement':reasons.append('outcome_'+outcome)
 if r['boundary_quality']!='acceptable':reasons.append('boundary_'+r['boundary_quality'])
 if r['artifact_flag']!='none':reasons.append('artifact_'+r['artifact_flag'])
 if r['visibility']!='adequate':reasons.append('visibility_'+r['visibility'])
 if reasons:flags.append({**r,'follow_up_flags':';'.join(reasons)})
assert counts['agreement']==reported['agreement_numerator'] and counts['indeterminate']==reported['cannot_determine']
for s in reported['strata']:
 subset=[r for r in rows if r['action']==s['action'] and int(float(key[r['review_id']]['failure']))==s['recorded_failure']]
 assert len(subset)==s['n_presented']
 assert sum(r['judged_outcome']==('failure' if s['recorded_failure'] else 'success') for r in subset)==s['agreement_numerator']
protected=json.loads((root/'05_final_review/output_manifest.json').read_text())['files']
for item in protected:
 p=Path(item['path']);assert p.stat().st_size==item['bytes'] and digest(p)==item['sha256'],str(p)
with (dest/'FLAGGED_CASES.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0])+['follow_up_flags']);w.writeheader();w.writerows(flags)
lines=['# Human review receipt — Reviewer A','','**HUMAN_RETURNS_RECEIVED_NOT_ADJUDICATED**','','64 complete ratings received from one real reviewer. No second reviewer has submitted; inter-rater agreement cannot be calculated. Original CSV bytes are preserved as `reviewer_1_submitted.csv`.','','## Outcome agreement','','- 57 / 59 determinate ratings agree with recorded labels (96.6%).','- 2 / 59 determinate ratings disagree (3.4%).','- 5 / 64 outcomes are indeterminate (7.8%).','- Agreement across all presented clips: 57 / 64 (89.1%); the other seven comprise two disagreements and five indeterminate outcomes.','','| Action | Agree | Disagree | Indeterminate | Total |','|---|---:|---:|---:|---:|']
for action in ['pick','insert','remove','place']:
 c=actions[action];lines.append(f"| {action} | {c['agreement']} | {c['disagreement']} | {c['indeterminate']} | {sum(c.values())} |")
lines+=['','## Follow-up','','Boundary ratings: 60 acceptable, 3 questionable, 1 indeterminate. Possible recording/presentation artifacts: 4. Visibility was rated adequate for all 64. Flag categories overlap; '+str(len(flags))+' unique clips need follow-up. See [FLAGGED_CASES.csv](FLAGGED_CASES.csv) for the supplied reasons and exact blind review IDs.','','Adjudication is requested, not completed. Revisit flagged cases against the original clips and annotation boundaries with the researcher. A disagreement does not establish which judgement is correct. Original MP4s can help distinguish browser-copy issues; reasons alone do not establish the cause. No ratings have been repaired or inferred. Keep this analysis and flag list away from any additional reviewer until they finish independently.','','## Interpretation and limits','','This supports substantial reviewer–label agreement on the clips that were judgeable, while identifying two outcome disagreements and several ambiguous or flagged cases. It does not establish population label accuracy, physical ground truth, absence of shortcuts, or validity of every cohort annotation. The sample is balanced and recording-spread, not a population-random sample. One reviewer supplies no independent inter-rater reliability estimate. The author had access to generic assistant-provided wording examples; no assistant-generated clip ratings were substituted.','','Historical performance metrics, labels, predictions and conclusions remain unchanged. Do not resolve discrepancies by removing clips or tuning thresholds. Any correction requires a separate approved protocol.','','## Validation and continuation','','Required fields, enums, unique IDs and reasons passed validation; three existing ingestion tests passed. Original action/clip mapping and order match the blank sheet. Independent standard-library counting reproduced the reported totals and all eight outcome/action strata. '+str(len(protected))+' sealed historical files retain their recorded hashes. Submitted bytes match the original CSV hash.','','The historical audit snapshot still says human review was pending at sealing; it has deliberately not been overwritten. This receipt records the later submission and outstanding adjudication. Next: review FLAGGED_CASES.csv with the researcher; optionally collect reviewer B independently. No model rerun is triggered.']
(dest/'HUMAN_REVIEW_RECEIPT.md').write_text('\n'.join(lines)+'\n')
validation={'UTC':datetime.now(timezone.utc).isoformat(),'counts':dict(counts),'unique_flagged_cases':len(flags),'mapping_and_order_match':True,'submission_sha256':digest(original),'independent_totals_and_strata_match':True,'historical_files_unchanged':len(protected),'ingestion_tests_passed':3,'human_reviewers':1,'adjudication':'PENDING','ratings_modified':False}
(dest/'RECEIPT_VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
shutil.copyfile(__file__,dest/'receipt_checker.py')
manifest=[{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(dest.iterdir()) if p.is_file()]
(dest/'submission_output_manifest.json').write_text(json.dumps({'files':manifest},indent=2)+'\n')
print(json.dumps(validation));print('REPORT',dest/'HUMAN_REVIEW_RECEIPT.md')
