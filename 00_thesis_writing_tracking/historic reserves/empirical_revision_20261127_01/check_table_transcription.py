"""Compare added numeric table cells with the retained revision inputs; no model execution."""
from pathlib import Path
import json,re
R=Path.cwd(); O=R/'00_thesis_writing_tracking/empirical_revision_20261127_01'
B=R/'00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters'
d=json.loads((O/'verified_table_inputs.json').read_text()); checks=[]
def rows(file,label):
 s=(B/file).read_text(); loc=s.index('\\label{'+label+'}'); start=s.rfind('\\begin{table}',0,loc); end=s.index('\\end{table}',loc)
 return [r.strip() for r in s[start:end].splitlines() if '&' in r]
def check(file,label,prefix,values,skip=1):
 found=[x for x in rows(file,label) if x.startswith(prefix+' &')]; assert len(found)==1,(label,prefix,found)
 cells=found[0].split('&')[skip:]; actual=[re.split(r'\\\\',x)[0].strip() for x in cells]
 expected=['--' if x is None else f'{float(x):.4f}' for x in values]
 assert actual==expected,(label,prefix,actual,expected)
 checks.append({'table':label,'row':prefix,'numeric_cells':sum(x is not None for x in values)})
labels=['Pixel noise ($\\sigma=.10$)','Blur ($\\sigma=4$)','Frame removal (8/16)','Sensor noise ($1\\,\\mathrm{SD}$)','Channel removal (11/22)','Temporal block (50\\%)','Stuck force/torque (6)','Vision absent','Sensors absent']
for label,v in zip(labels,d['REASSEMBLE_high_severity'].values()):check('06_reassemble.tex','tab:reassemble-corruption',label,list(v.values()))
labels=['Primary, experiment','Primary, machine/date','Primary, calendar date','Exclude 2, experiment','Exclude 2, machine/date','Exclude 2, calendar date']
for label,v in zip(labels,d['MSM_sensitivity'].values()):check('07_msm.tex','tab:msm-sensitivity',label,list(v.values()))
labels=['Blur ($\\sigma=4$)','Brightness/contrast (0.2)','Occlusion (40\\%)','Frame omission (12/16)','Sensor noise ($1\\,\\mathrm{SD}$)','Zeroed channels (50\\%)','Missing channels (50\\%)','Vision absent','Sensors absent']
for label,v in zip(labels,d['MSM_robustness']):check('07_msm.tex','tab:msm-robustness',label,list(v['values'].values()))
for label,key in [('Three-view V1','V1'),('High-camera control','V1_high_only'),('Clean quality gate','Gate_V1'),('Availability-only gate','Gate_static_V1'),('Logistic sensor','S3')]:
 values=[next(r[6] for r in d['ViFailback_reported_controls'] if r[0]==key and r[1]==seed and r[2]=='pooled') for seed in ['42','123','20261023']]
 check('08_vifailback.tex','tab:vif-controls',label,values)
for r in d['ViFailback_reported_calibration_rows']:
 if r[2]=='0' and float(r[3])<0:
  check('08_vifailback.tex','tab:vif-calibration',r[0]+' & '+r[1],r[3:6],skip=2)
result={'scope':'Numeric transcription from revision input receipt, not new scientific verification of source reports. Follow-up narrative table reviewed separately.','rows_checked':len(checks),'numeric_cells_checked':sum(x['numeric_cells'] for x in checks),'checks':checks,'status':'PASS'}
(O/'table_transcription_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
