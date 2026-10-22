"""Synthetic CPU checks only: no optimizer steps or scientific selection."""
from pathlib import Path
import sys,os,tempfile,ast
sys.dont_write_bytecode=True
STUDY=Path(__file__).resolve().parents[1];sys.path.insert(0,str(STUDY/'code'))
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='2'
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import torch
torch.set_num_threads(2)
from common import RUN,read,write,sha,local,signature
from selection import rank,validate_job,collect,component_paths
from corruptions import rng,image_fault,survivors,sensor_fault,resample,statistics,statistics_for,routing,schedule
from evaluation import metrics,paired_interval
from inputs import scales_for
from prefix import original


def bank(fold=1,good=False):
    y=np.tile([0,1],4)
    return pd.DataFrame({'recording_id':[f'f{fold}r{i//2}' for i in range(8)],'segment_id':[str(i%2) for i in range(8)],'failure':y,
        'p_fused':np.where(y==1,.8,.2) if good else [.3,.2,.8,.6,.5,.4,.9,.7],
        'p_visual':np.where(y==1,.7,.3),'p_sensor':np.where(y==1,.6,.4)})

def candidate(folds=(1,),good=False,eligible=True,frames=16,parameters=10):
    return {'eligible':eligible,'frames':frames,'parameters':parameters,'folds':{f'fold_{i:02d}':bank(i,good) for i in folds}}

class SelectionTests(unittest.TestCase):
    def test_superior_no_improvement_ineligible_and_noisy_fields(self):
        c={'frozen_16_frames':candidate(),'fine_tuned_16_frames':candidate(good=True)}
        self.assertEqual(rank(c)['winner'],'fine_tuned_16_frames')
        c['fine_tuned_16_frames']['eligible']=False
        self.assertEqual(rank(c)['winner'],'frozen_16_frames')
        c['fine_tuned_16_frames']=candidate();c['fine_tuned_16_frames']['noise_AP']=1e6
        self.assertEqual(rank(c)['winner'],'frozen_16_frames')
        with self.assertRaisesRegex(RuntimeError,'WAITING'):rank(c,terminal=False)

    def test_tie_precedence_reference_frames_parameters_alphabetical(self):
        c={'frozen_16_frames':candidate(),'fine_tuned_32_frames':candidate(frames=32),'cnn_plus_encoder':candidate(frames=16)}
        with patch('selection.average_precision_score',side_effect=[.7,.7,.7]):self.assertEqual(rank(c)['winner'],'frozen_16_frames')
        with patch('selection.average_precision_score',side_effect=[.5,.8,.8]):self.assertEqual(rank(c)['winner'],'cnn_plus_encoder')
        c['fine_tuned_32_frames']['frames']=16;c['fine_tuned_32_frames']['parameters']=1
        with patch('selection.average_precision_score',side_effect=[.5,.8,.8]):self.assertEqual(rank(c)['winner'],'fine_tuned_32_frames')
        c['fine_tuned_32_frames']['parameters']=None
        with patch('selection.average_precision_score',side_effect=[.5,.8,.8]):self.assertEqual(rank(c)['winner'],'cnn_plus_encoder')

    def test_alias_whole_fold_intersection_and_empty_coverage(self):
        c={'frozen_16_frames':candidate((1,2)),'fine_tuned_16_frames':candidate((2,),True),'cnn_only':candidate((1,2),True)}
        r=rank(c);self.assertEqual(r['folds'],['fold_02']);self.assertEqual(r['coverage'],'PARTIAL_COVERAGE_PILOT');self.assertNotIn('cnn_only',r['scores'])
        c['fine_tuned_16_frames']=candidate((3,),True)
        with self.assertRaisesRegex(RuntimeError,'NO_COMMON'):rank(c)
        c['fine_tuned_16_frames']=candidate((),True)
        self.assertEqual(rank(c)['winner'],'frozen_16_frames')

    def test_actual_missing_checkpoint_excluded_before_scores(self):
        original_paths=component_paths
        def missing(*args,**kwargs):
            d=original_paths(*args,**kwargs);d['head']=RUN/'cache/definitely_missing_checkpoint.pt';return d
        with patch('selection.component_paths',side_effect=missing):
            candidates,_=collect(rank_allowed=True)
        self.assertEqual(len(candidates['frozen_16_frames']['folds']),0)
        self.assertTrue(any('missing' in x for x in candidates['frozen_16_frames']['reasons']))

    def test_real_memberships_and_negative_key_contracts(self):
        f=pd.DataFrame(read(RUN/'data/cohort_and_frames.json'));jobs=read(RUN/'data/fit_partitions.json')
        for j in jobs:self.assertTrue(validate_job(f,j))
        bad=dict(jobs[0]);bad['C']=bad['C']+[bad['G'][0]]
        with self.assertRaises(AssertionError):validate_job(f,bad)
        c={'frozen_16_frames':candidate(),'fine_tuned_16_frames':candidate(good=True)}
        c['fine_tuned_16_frames']['folds']['fold_01'].loc[0,'segment_id']='wrong'
        with self.assertRaises(AssertionError):rank(c)

class TransformTests(unittest.TestCase):
    def test_schedule_counts_and_seed_stability(self):
        jobs=schedule();self.assertEqual(len(jobs),51)
        self.assertEqual(sum(j['family']=='image_noise' for j in jobs),9)
        self.assertEqual(sum(j['family']=='missing_modality' for j in jobs),2)
        a=rng(271828,['r','s'],'image_noise',3).normal(size=20);b=rng(271828,['r','s'],'image_noise',3).normal(size=20)
        np.testing.assert_array_equal(a,b)
        self.assertFalse(np.array_equal(a,rng(271829,['r','s'],'image_noise',3).normal(size=20)))

    def test_image_zero_common_draws_clipping_blur_no_channel_mix(self):
        x=np.full((64,64,3),.5,dtype='float32');key=['r','s']
        zero,_=image_fault(x,'image_noise',0,271828,key,7);np.testing.assert_array_equal(zero,x)
        mild,_=image_fault(x,'image_noise',.02,271828,key,7);medium,_=image_fault(x,'image_noise',.05,271828,key,7)
        np.testing.assert_allclose((mild-x)/.02,(medium-x)/.05,rtol=0,atol=3e-6)
        again,_=image_fault(x,'image_noise',.02,271828,key,7);np.testing.assert_array_equal(mild,again)
        clipped,meta=image_fault(np.zeros_like(x),'image_noise',.1,271828,key,7);self.assertGreater(meta['clipped_fraction'],.4);self.assertGreaterEqual(clipped.min(),0)
        color=np.zeros((17,17,3),dtype='float32');color[:,:,0]=1
        blurred,_=image_fault(color,'image_blur',2,0,key,7);np.testing.assert_array_equal(color,blurred)
        np.testing.assert_array_equal(x,np.full_like(x,.5))

    def test_frame_channel_nested_count_and_chronology(self):
        previous=set()
        for fraction,count in [(.1,2),(.3,5),(.5,8)]:
            keep,lost=survivors(16,fraction,271828,['r','s'],'frame_loss')
            self.assertEqual(len(lost),count);self.assertTrue(previous<=set(lost));self.assertTrue(np.all(np.diff(keep)>0));previous=set(lost)
        t=np.linspace(0,1,101);x=np.ones((101,5));streams=[('a',t,x)];names=list('abcde');previous=set()
        for fraction in [.1,.3,.5]:
            out,info=sensor_fault(streams,names,'sensor_channel_loss',fraction,271828,['r','s'],.2,.8)
            self.assertTrue(previous<=set(info['affected_channels']));previous=set(info['affected_channels'])
            np.testing.assert_array_equal(out[0][2][t<.2],x[t<.2])
        with self.assertRaises(ValueError):survivors(1,.1,271828,['r','s'],'frame_loss')

    def test_native_sensor_noise_zero_sd_missingness_and_time_gap(self):
        t=np.linspace(0,1,101);x=np.column_stack([t,t]);x[30,0]=np.nan;names=['a','b'];streams=[('stream',t,x)]
        a,_=sensor_fault(streams,names,'sensor_noise',.1,271828,['r','s'],.2,.8,np.array([1.,0.]))
        b,_=sensor_fault(streams,names,'sensor_noise',.5,271828,['r','s'],.2,.8,np.array([1.,0.]))
        np.testing.assert_array_equal(np.isnan(a[0][2]),np.isnan(x));np.testing.assert_array_equal(a[0][2][:,1],x[:,1])
        valid=np.isfinite(x[:,0]);np.testing.assert_allclose((a[0][2][valid,0]-x[valid,0])/.1,(b[0][2][valid,0]-x[valid,0])/.5,atol=1e-14)
        previous=None
        for fraction in [.1,.3,.5]:
            altered,meta=sensor_fault(streams,names,'sensor_time_loss',fraction,271828,['r','s'],.2,.8)
            lo,hi=meta['time_bounds']
            if previous:self.assertLessEqual(lo,previous[0]);self.assertGreaterEqual(hi,previous[1])
            previous=(lo,hi);grid=np.linspace(.2,.8,512)
            z=resample(t,altered[0][2],.2,.8,explicit_mask=altered[0][3],time_block=(lo,hi))
            self.assertTrue(np.isnan(z[(grid>=lo)&(grid<=hi)]).all())
            np.testing.assert_array_equal(altered[0][2][t>.8],x[t>.8])

    def test_clean_statistics_regression_and_all_missing_imputation(self):
        # Isolate only pure reference functions via AST, avoiding upstream imports/side effects.
        source=RUN/'provenance/source_snapshots/visual_data.py';tree=ast.parse(source.read_text());wanted={'times','resample','statistics'}
        module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted],type_ignores=[]);space={'np':np};exec(compile(module,str(source),'exec'),space)
        t=np.linspace(0,2,401);x=np.column_stack([np.sin(t),t*t]);x[25:28,0]=np.nan
        native=space['resample'](t,x,.1,1.8);actual=resample(t,x,.1,1.8)
        np.testing.assert_array_equal(native,actual);np.testing.assert_array_equal(space['statistics'](native),statistics(actual))
        # Original prepare casts concatenated resampled streams to float32 BEFORE statistics.
        native32=native.astype('float32')
        np.testing.assert_array_equal(space['statistics'](native32),statistics(native32))
        np.testing.assert_array_equal(space['statistics'](native32),statistics_for([('s',t,x,np.zeros(x.shape,bool))],.1,1.8))
        missing=statistics(np.full((512,3),np.nan));self.assertTrue(np.isnan(missing).all())
        from pipeline import transform
        np.testing.assert_array_equal(transform(missing[None,:],np.ones(30),np.ones(30)),np.zeros((1,30),dtype='float32'))

    def test_scales_use_only_G_and_native_channels(self):
        f=pd.DataFrame({'recording_id':['g','c','e'],'segment_id':['0','0','0'],'start':[0.,0.,0.],'end':[1.,1.,1.]})
        class Fake:
            def __init__(self):self.seen=[]
            def streams(self,s):
                self.seen.append(s['recording_id']);assert s['recording_id']=='g'
                return [('s',np.array([0.,.5,1.]),np.array([[1.],[2.],[3.]]))],['s[0]'],['native']
        fake=Fake()
        with tempfile.TemporaryDirectory(dir=RUN/'cache',prefix='synthetic_scales_') as d:
            with patch('inputs.RUN',Path(d)):
                scale=scales_for(f,{'G':[0],'C':[1],'predict':[2],'fold_name':'fold_01'},fake,'synthetic')
            self.assertEqual(fake.seen,['g']);self.assertEqual(scale['finite_counts'],[3]);self.assertAlmostEqual(scale['population_sd'][0],np.std([1,2,3]))

    def test_fallback_zero_is_present_and_partial_stays_f2(self):
        m={'coefficient':[2.,3.],'intercept':-1.}
        self.assertEqual(routing(0,.8,m,False,True),(.8,'sensor_only_fallback'))
        self.assertEqual(routing(.3,0,m,True,False),(.3,'visual_only_fallback'))
        self.assertEqual(routing(0,.8,m)[1],'F2')
        with self.assertRaisesRegex(ValueError,'ABSTAIN'):routing(0,0,m,False,False)

class EvidenceTests(unittest.TestCase):
    def test_metrics_paired_clusters_and_repeat_average(self):
        clean=bank(good=True);bad=bank();bad2=bank();bad2.p_fused=1-bad2.p_fused
        interval=paired_interval(clean,[bad,bad2],replicates=30)
        expected=metrics(clean.failure,clean.p_fused)['AP']-np.mean([metrics(x.failure,x.p_fused)['AP'] for x in [bad,bad2]])
        self.assertAlmostEqual(interval['difference'],expected);self.assertEqual(interval['realizations'],2)
        self.assertEqual(interval['effective_replicates']+interval['skipped_replicates'],30)
        zero=paired_interval(clean,[clean,clean,clean],replicates=10);self.assertEqual(zero['lower95'],0);self.assertEqual(zero['upper95'],0)
        self.assertEqual(metrics([0,1],[.1,.9])['AP'],1);self.assertIsNone(metrics([0,0],[.2,.1])['AUROC'])

    def test_native_original_weight_inference_only_guards(self):
        model=original('cpu').eval();before=model.active_state();x=torch.rand(2,3,64,64);traces={}
        with torch.inference_mode():
            for condition in ['cnn_only','cnn_plus_encoder']:
                model.trace.clear();out=model(x,condition);self.assertTrue(torch.isfinite(out).all());traces[condition]=dict(model.trace)
        self.assertEqual(before,model.active_state());self.assertTrue(all(not m.training for m in model.modules()))
        self.assertTrue(all(not p.requires_grad and p.grad is None for p in model.parameters()))
        self.assertTrue(any('.self_attn' in x for x in traces['cnn_plus_encoder']))
        self.assertFalse(any(x.startswith('encoder.') for x in traces['cnn_only']))
        with self.assertRaisesRegex(RuntimeError,'FORBIDDEN'):model.wrapper(pixel_values=x)
        with self.assertRaisesRegex(RuntimeError,'FORBIDDEN'):model.wrapper.model.decoder()
        write(RUN/'checks/original_weight_CPU_inference.json',{'passed':True,'scope':'unselected prefix on synthetic64px CPU inputs only; not scientific replay or selected corrupted inference','traces':traces,'state_unchanged':True,'no_gradients':True,'optimizer_steps':0,'loading':model.loading_evidence})

    def test_no_training_calls_and_write_boundary(self):
        for name in ['pipeline.py','inference.py','prefix.py']:
            tree=ast.parse((STUDY/'code'/name).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,['fit','fit_transform','backward','step'])
        with self.assertRaises(ValueError):local(STUDY.parent/'forbidden.txt')

if __name__=='__main__':unittest.main()
