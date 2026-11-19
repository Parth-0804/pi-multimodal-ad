import pandas as pd
import numpy as np
import pytest
from scripts.thesis.final_validity_audit.human_review import sample_cases,blank_sheets,validate_sheet,agreement,interrater,ingest

def synthetic_cohort():
 rows=[]
 for a in ['pick','insert','remove','place']:
  for y in [0,1]:
   for r in range(10):rows.append({'recording_id':'synthetic_'+str(r),'segment_id':a+str(y),'action':a,'failure':y,'fold':r%5,'start':0.,'end':1.})
 return pd.DataFrame(rows)

def ratings():
 key=pd.DataFrame({'review_id':['R1','R2','R3'],'action':['pick']*3,'failure':[0,1,1]})
 a=pd.DataFrame({'review_id':['R1','R2','R3'],'reviewer_id':['SYNTHETIC_A']*3,'judged_outcome':['success','failure','cannot_determine'],'boundary_quality':['acceptable']*3,'visibility':['adequate']*3,'artifact_flag':['none']*3,'short_reason':['synthetic unit test']*3})
 return key,a

def test_recording_spread_and_blind_masking():
 cohort=synthetic_cohort();sample,support=sample_cases(cohort);assert len(sample)==64
 assert all(x['sampled_recordings']==8 for x in support)
 sheets=blank_sheets(sample)
 assert set(sheets['A'].review_id)==set(sheets['B'].review_id)
 assert sheets['A'].review_id.tolist()!=sheets['B'].review_id.tolist()
 for sheet in sheets.values():
  assert not set(sheet)&{'failure','recording_id','segment_id','start','end','fold','p','score','recorded_outcome'}
  assert sheet.judged_outcome.eq('').all()
  assert sheet.clip_file.str.match(r'^R[0-9a-f]{16}\.mp4$').all()

def test_ingestion_validation_and_denominators(tmp_path):
 key,a=ratings();joined=validate_sheet(a,key);v=agreement(joined)[1]
 assert v['cannot_determine']==1 and v['n_determinate']==1 and v['n_presented']==2 and v['agreement_numerator']==1
 bad=a.copy();bad.loc[0,'judged_outcome']=''
 with pytest.raises(ValueError):validate_sheet(bad,key)
 with pytest.raises(ValueError):validate_sheet(a.iloc[:2],key)
 with pytest.raises(ValueError):validate_sheet(pd.concat([a,a.iloc[:1]]),key)
 k=tmp_path/'synthetic_key.csv';f=tmp_path/'synthetic_ratings.csv';key.to_csv(k,index=False);a.to_csv(f,index=False)
 dest=ingest(tmp_path,[f],k)
 assert (dest/'reviewer_1_submitted.csv').read_bytes()==f.read_bytes()
 assert not (dest/'reviewer_1_submitted.csv').stat().st_mode&0o222
 assert (dest/'ADJUDICATION_REQUEST.md').exists()

def test_three_category_agreement_and_undefined_kappa():
 key,a=ratings();b=a.copy();b['reviewer_id']='SYNTHETIC_B'
 x=interrater(a,b);assert x['cohens_kappa']==1 and x['three_category_denominator']==3 and x['both_determinate_denominator']==2
 a['judged_outcome']='success';b['judged_outcome']='success';assert interrater(a,b)['cohens_kappa'] is None
