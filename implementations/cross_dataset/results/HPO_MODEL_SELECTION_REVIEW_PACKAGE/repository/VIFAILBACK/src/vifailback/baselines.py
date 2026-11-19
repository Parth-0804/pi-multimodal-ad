"""Source-exact S1=S3 and validation-selected nonlinear S2; fit-local transforms."""
import time
import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from .common import PROJECT,config,event,read,sha,signature,write
from .cohort import finalize
from .metrics import metrics,independent_check
from .reference import primitives,identities
from .sensors import prepare as prepare_sensors
from .splits import prepare as prepare_splits


def run(c=None):
    c=c or config();rows=finalize(c);jobs=prepare_splits(c);feature_receipt=prepare_sensors(c)
    from .common import resolve
    data=np.load(resolve(feature_receipt['path']),allow_pickle=False)
    order={int(e):i for i,e in enumerate(data['episode_ids'])};labels={r['episode_index']:r['label'] for r in rows}
    source=primitives()
    import torch
    torch.set_num_threads(c['cpu_threads'])
    result=[]
    for seed in c['seeds']:
        for job in jobs:
            root=PROJECT/'06_training_experiments/sensor_baselines/runs'/c['run_id']/f'seed{seed}'/job['id']
            done=root/'COMPLETE.json'
            if done.exists():
                receipt=read(done)
                assert sha(root/'predictions.json')==receipt['prediction_sha256']
                result.append(receipt);continue
            assert not (root/'predictions.json').exists(),'INCOMPLETE_OUTPUT_REQUIRES_REVIEW'
            arrays={p:data['features'][[order[e] for e in ids]] for p,ids in job['ids'].items()}
            target={p:np.asarray([labels[e] for e in ids]) for p,ids in job['ids'].items()}
            started=time.perf_counter()
            s3=source['sensor_fit'](arrays['T'],target['T'],arrays['C'],target['C'])
            s3_training_seconds=time.perf_counter()-started;predict_started=time.perf_counter()
            s3raw,s3prob=source['sensor_predict'](arrays['A'],s3)
            s3_inference_seconds=time.perf_counter()-predict_started
            candidates=[];selected=None
            for leaves in [7,15,31]:
                model=HistGradientBoostingClassifier(max_iter=200,max_leaf_nodes=leaves,learning_rate=.05,
                      l2_regularization=.1,min_samples_leaf=20,early_stopping=False,class_weight='balanced',random_state=seed)
                model.fit(arrays['T'],target['T'])
                score=metrics(target['V'],model.predict_proba(arrays['V'])[:,1])['macro_AP']
                candidates.append({'max_leaf_nodes':leaves,'V_macro_AP':score})
                if selected is None or score>selected[0]:selected=(score,model,leaves)
            s2=selected[1]
            rawC=np.clip(s2.predict_proba(arrays['C'])[:,1],1e-6,1-1e-6)
            cal=source['calibrate'](np.log(rawC/(1-rawC)),target['C'])
            s2_training_validation_calibration_seconds=time.perf_counter()-started-s3_training_seconds-s3_inference_seconds
            predict_started=time.perf_counter();rawA=np.clip(s2.predict_proba(arrays['A'])[:,1],1e-6,1-1e-6)
            rawA=np.log(rawA/(1-rawA));s2prob=source['calibrated'](rawA,cal)
            s2_inference_seconds=time.perf_counter()-predict_started
            root.mkdir(parents=True,exist_ok=True)
            write(root/'S3_MODEL.json',s3);joblib.dump(s2,root/'S2_MODEL.joblib',compress=3)
            write(root/'S2_SELECTION_AND_CALIBRATION.json',{'candidates':candidates,'selected_max_leaf_nodes':selected[2],'calibrator':cal})
            predictions=[{'episode_index':e,'fit_id':job['id'],'outer':job['outer'],'inner':job['inner'],'seed':seed,
                          'label':labels[e],'S3_probability':float(p3),'S3_raw':float(r3),
                          'training_prevalence_probability':float(target['T'].mean()),
                          'S2_probability':float(p2),'S2_raw':float(r2)} for e,p3,r3,p2,r2 in zip(job['ids']['A'],s3prob,s3raw,s2prob,rawA)]
            write(root/'predictions.json',predictions)
            report={name:metrics(target['A'],p) for name,p in [('S3',s3prob),('S2',s2prob)]}
            report['T_prevalence_reference']=metrics(target['A'],np.full(len(target['A']),target['T'].mean()))
            for name,p in [('S3',s3prob),('S2',s2prob)]:independent_check(target['A'],p,report[name])
            write(root/'metrics.json',report)
            receipt={'seed':seed,'fit_id':job['id'],'split_sha256':signature(job),'feature_sha256':feature_receipt['sha256'],
                     'source_code':identities(),'S1_equals_S3':True,'seconds':time.perf_counter()-started,
                     'S3_training_calibration_seconds':s3_training_seconds,'S3_assessment_inference_seconds':s3_inference_seconds,
                     'S2_training_validation_calibration_seconds':s2_training_validation_calibration_seconds,
                     'S2_assessment_inference_seconds':s2_inference_seconds,'assessment_examples':len(job['ids']['A']),
                     'inference_scope':'cached280statistics to calibrated probability; raw-table/statistics cost separate',
                     'prediction_sha256':sha(root/'predictions.json'),'S3_checkpoint_sha256':sha(root/'S3_MODEL.json'),
                     'S2_checkpoint_sha256':sha(root/'S2_MODEL.joblib')}
            write(done,receipt);result.append(receipt);event(c,'SENSOR_FIT_COMPLETE',seed=seed,fit_id=job['id'])
    return result
