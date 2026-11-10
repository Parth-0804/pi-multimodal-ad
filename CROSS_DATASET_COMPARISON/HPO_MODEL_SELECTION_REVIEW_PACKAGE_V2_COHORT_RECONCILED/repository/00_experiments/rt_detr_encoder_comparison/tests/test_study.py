"""Small CPU checks only; synthetic fixtures are never scientific predictions."""
from pathlib import Path
import os
import sys
sys.dont_write_bytecode=True
STUDY=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(STUDY/'code'))
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
import unittest
from unittest.mock import patch
import tempfile
import numpy as np
import pandas as pd
import torch
from torch import nn
torch.set_num_threads(2)
from common import RUN, read, write, local, signature, sha, config
from data import frame,validate_all,validate_job,KEYS
from features import pool_maps,pool_segments,original,tensor_sha
from fitting import Head,train_raw,predict_head,join_branches,atomic_torch,reload_head,complete_load
from fusion import standardizer,transform,sensor_fit,sensor_predict,stacker,fused,calibrate,calibrated
from evaluation import metrics,paired_bootstrap


class ScientificContracts(unittest.TestCase):
    def test_all_locked_partitions_and_negative_recording_leakage(self):
        f=frame();jobs=read(RUN/'data/fit_partitions.json')
        counts=validate_all(f,jobs);self.assertEqual(len(counts),20)
        j=dict(jobs[0]);j['C']=j['C']+[j['G'][0]]
        with self.assertRaises(AssertionError):validate_job(f,j)
        wrong=f.copy();wrong.loc[1,KEYS]=wrong.loc[0,KEYS].values
        with self.assertRaises(AssertionError):validate_all(wrong,jobs)

    def test_mean_pooling_equal_scale_weights_and_frame_grouping(self):
        a=torch.ones(32,2,8,8);b=torch.ones(32,3,2,2)*7
        values=pool_maps([a,b]);self.assertEqual(tuple(values.shape),(32,5))
        expected=torch.tensor([1.,1.,7.,7.,7.])
        self.assertTrue(torch.equal(values[0],expected))
        values[16:]+=3
        segments=pool_segments(values.reshape(2,16,-1))
        torch.testing.assert_close(segments[0],expected);torch.testing.assert_close(segments[1],expected+3)
        torch.testing.assert_close(pool_segments(values.reshape(2,16,-1).flip(1)),segments)
        with self.assertRaises(AssertionError):pool_segments(values.reshape(2,16,-1)[:,:15])

    def test_raw_training_is_G_only_and_checkpoint_replay(self):
        rng=np.random.default_rng(91);x=rng.normal(size=(9,5)).astype('float32');y=np.array([0,1,0,1,0,1,0,1,0])
        with tempfile.TemporaryDirectory(dir=RUN/'cache',prefix='synthetic_head_') as d:
            p=Path(d);fid='synthetic-only'
            model,state,curves,_=train_raw(x,y,42,'cpu',p/'in_progress.pt',fid)
            self.assertEqual([c['G_presentations'] for c in curves],[9]*5)
            self.assertEqual(curves[-1]['optimizer_updates'],10)  # last partial batch normalized by one
            atomic_torch(p/'model.pt',state);restored,mean,std=reload_head(p/'model.pt','cpu')
            np.testing.assert_allclose(predict_head(model,x,mean,std,'cpu'),predict_head(restored,x,mean,std,'cpu'),atol=0,rtol=0)
            again,_,_,_=train_raw(x,y,42,'cpu',p/'in_progress.pt',fid)
            np.testing.assert_allclose(predict_head(again,x,mean,std,'cpu'),predict_head(model,x,mean,std,'cpu'),atol=0,rtol=0)
            with self.assertRaises(AssertionError):train_raw(x,y,42,'cpu',p/'in_progress.pt','wrong-fit')
            # Held-out values/labels are not accepted by raw trainer; standardizer stays G-only.
            np.testing.assert_allclose(mean,np.mean(x,axis=0),atol=1e-7)

    def test_interrupted_optimizer_checkpoint_resumes_exactly(self):
        rng=np.random.default_rng(17);x=rng.normal(size=(9,4)).astype('float32');y=np.arange(9)%2
        with tempfile.TemporaryDirectory(dir=RUN/'cache',prefix='synthetic_resume_') as d:
            checkpoint=Path(d)/'in_progress.pt'
            with patch('fitting.elapsed',side_effect=[0.,0.,1e10]):
                with self.assertRaisesRegex(RuntimeError,'DEADLINE_CHECKPOINT_SAVED'):
                    train_raw(x,y,19,'cpu',checkpoint,'synthetic-resume')
            resumed,state,_,_=train_raw(x,y,19,'cpu',checkpoint,'synthetic-resume')
            direct,expected,_,_=train_raw(x,y,19,'cpu')
            for key,value in state['head'].items():
                self.assertTrue(torch.equal(value,expected['head'][key]),key)

    def test_standardization_near_zero_and_missing(self):
        x=np.array([[1.,np.nan,3.],[1.,2.,4.],[1.,2.,5.]],dtype='float32')
        mean,std=standardizer(x);self.assertEqual(std[0],1);self.assertEqual(std[1],1)
        z=transform(np.array([[1.,np.nan,np.inf]],dtype='float32'),mean,std)
        self.assertTrue(np.isfinite(z).all());self.assertEqual(z[0,1],0)

    def test_keyed_join_rejects_wrong_rows_and_labels(self):
        a=pd.DataFrame({'recording_id':['r1','r2'],'segment_id':['same','same'],'failure':[0,1],'p_visual':[.2,.7]})
        b=a[KEYS+['failure']].copy();b['p_sensor']=[.3,.8];b['raw_sensor_logit']=[-.3,.8];b['sensor_fit_id']='s'
        z=join_branches(a,b.iloc[::-1]);np.testing.assert_array_equal(z.p_sensor,[.3,.8])
        b.loc[0,'failure']=1
        with self.assertRaises(AssertionError):join_branches(a,b)
        with self.assertRaises(AssertionError):join_branches(a,a)

    def test_small_sensor_calibration_fusion_and_metrics(self):
        rng=np.random.default_rng(2);x=rng.normal(size=(24,3)).astype('float32');y=np.tile([0,1],12)
        m=sensor_fit(x[:12],y[:12],x[12:18],y[12:18]);raw,p=sensor_predict(x[18:],m)
        self.assertTrue(np.isfinite(p).all())
        f2=stacker(np.column_stack([p,p]),y[18:]);fp=fused(np.column_stack([p,p]),f2)
        self.assertAlmostEqual(metrics(y[18:],fp)['Brier'],np.mean((fp-y[18:])**2))
        self.assertEqual(metrics([0,1],[.1,.9])['AP'],1.)
        self.assertIsNone(metrics([0,0],[.1,.2])['AUROC'])
        c=calibrate(raw,y[18:]);self.assertTrue(np.isfinite(calibrated(raw,c)).all())

    def test_paired_cluster_bootstrap_shared_multiplicities(self):
        a=pd.DataFrame({'recording_id':['a','a','b','c','c','c'],'segment_id':['0','1','0','0','1','2'],
                        'failure':[0,1,0,0,1,1],'p_visual':[.2,.8,.3,.4,.7,.9],
                        'p_sensor':[.3,.7,.2,.3,.8,.9],'p_fused':[.2,.9,.3,.3,.8,.9]})
        b=a.copy();out=paired_bootstrap(a,b,30)
        np.testing.assert_array_equal(out.AP_difference.iloc[:2],[0,0])
        np.testing.assert_array_equal(out.lower95.iloc[:2],[0,0]);np.testing.assert_array_equal(out.upper95.iloc[:2],[0,0])
        self.assertEqual(int(out.effective_replicates.iloc[0]+out.skipped_replicates.iloc[0]),30)
        b.loc[0,'p_sensor']=.6
        with self.assertRaises(AssertionError):paired_bootstrap(a,b,2)

    def test_write_boundary_and_completed_hash_rejection(self):
        with self.assertRaises(ValueError):local(STUDY.parent/'forbidden.txt')
        with tempfile.TemporaryDirectory(dir=RUN/'cache',prefix='synthetic_complete_') as d:
            p=Path(d);(p/'identified_branch_predictions.csv').write_text('recording_id,segment_id\nr,0\n')
            write(p/'complete.json',{'fit_id':'x','outputs':{'identified_branch_predictions.csv':sha(p/'identified_branch_predictions.csv')}})
            self.assertIsNotNone(complete_load(p,'x'))
            with self.assertRaises(AssertionError):complete_load(p,'y')
            (p/'identified_branch_predictions.csv').write_text('changed')
            with self.assertRaises(AssertionError):complete_load(p,'x')


class NativeOriginalWeightCPU(unittest.TestCase):
    def test_actual_native_prefix_guards_and_frozen_buffers_on_synthetic_pixels(self):
        """Original checkpoint; CPU 64px synthetic images, NOT real-data preflight."""
        model=original('cpu');before=model.active_state();torch.manual_seed(7)
        pixels=torch.rand(2,3,64,64)
        evidence={'scope':'original checkpoint CPU forward on two synthetic 64x64 images; not real extraction, training, GPU timing or full-resolution preflight','results':[],'loading':model.loading_evidence}
        for c in ['cnn_only','cnn_plus_encoder']:
            model.trace.clear()
            with torch.inference_mode():z=model(pixels,c).numpy().copy()
            trace=dict(model.trace)
            self.assertTrue(any(k.startswith('backbone.') for k in trace))
            if c=='cnn_plus_encoder':
                self.assertTrue(any('.self_attn' in k for k in trace))
                self.assertTrue(any(k.startswith('encoder_input_proj.') for k in trace))
                self.assertTrue(any(k.startswith('encoder.fpn_blocks.') for k in trace))
                self.assertTrue(any(k.startswith('encoder.pan_blocks.') for k in trace))
            else:self.assertFalse(any(k.startswith(('encoder.','encoder_input_proj.')) for k in trace))
            # Ordinary cached array supports head autograd; no pretrained grads.
            head=Head(z.shape[1]);loss=head(torch.from_numpy(z)).sum();loss.backward()
            self.assertTrue(any(torch.count_nonzero(p.grad)>0 for p in head.parameters()))
            self.assertTrue(all(p.grad is None for p in model.parameters()))
            model.train();self.assertTrue(all(not m.training for m in model.modules()))
            self.assertEqual(before,model.active_state())
            evidence['results'].append({'condition':c,'dimension':z.shape[1],'map_shapes':model.shapes[c],
                'executed_modules':trace,'active_frozen_parameters':model.active_parameters(c),
                'head_parameters':sum(p.numel() for p in head.parameters()),'extractor_state_unchanged':True})
        with self.assertRaisesRegex(RuntimeError,'FORBIDDEN_DETECTION_EXECUTION'):model.wrapper(pixel_values=pixels)
        with self.assertRaisesRegex(RuntimeError,'FORBIDDEN_DETECTION_EXECUTION'):model.wrapper.model(pixel_values=pixels)
        with self.assertRaisesRegex(RuntimeError,'FORBIDDEN_DETECTION_EXECUTION'):model.wrapper.model.decoder()
        with self.assertRaisesRegex(RuntimeError,'FORBIDDEN_DETECTION_EXECUTION'):model.wrapper.model.enc_score_head(torch.zeros(1,256))
        evidence['passed']=True;evidence['guarded_modules']=model.forbidden
        write(RUN/'checks/original_weight_CPU_path.json',evidence)


if __name__=='__main__':unittest.main()
