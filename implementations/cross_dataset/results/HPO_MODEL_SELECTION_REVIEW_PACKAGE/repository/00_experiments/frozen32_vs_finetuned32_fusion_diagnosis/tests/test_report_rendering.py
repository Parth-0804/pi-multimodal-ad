"""Synthetic report integration check; never touches the active scientific state."""
from pathlib import Path
import json
import os
import sys
import unittest
from unittest.mock import patch
import pandas as pd
HERE=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'results'/'matplotlib_cache'))
sys.path.insert(0,str(HERE/'code'))
import analysis

class ReportRenderingTests(unittest.TestCase):
    def test_reporting_failure_cannot_leave_false_complete_state(self):
        root=HERE/'tests'/'synthetic_report_fixture'/'failed_report'/'results'
        with patch.object(analysis,'ROOT',root),patch.object(analysis,'event') as event, \
             patch.object(analysis,'_report',side_effect=ValueError('synthetic package failure')):
            with self.assertRaisesRegex(ValueError,'synthetic package failure'):
                analysis.report('COMPLETE')
            self.assertTrue((root/'provenance/reporting_error_receipt.json').exists())
            self.assertEqual(event.call_args.args[0],'REPORTING_BLOCKED')
            self.assertFalse(event.call_args.kwargs['finished'])

    def test_interval_plot_allows_point_outside_percentile_interval(self):
        root=HERE/'tests'/'synthetic_report_fixture'/'interval_plot'/'results'
        metrics=pd.DataFrame([{'seed':42,'condition':analysis.CONDITIONS[0],
                              'branch':'visual','scope':'fold_01','AP':.2}])
        stable=pd.DataFrame([{'seed':42,'branch':'visual','pooled_AP_difference':.1,
                             'percentile95_low':.11,'percentile95_high':.2}])
        with patch.object(analysis,'ROOT',root):
            analysis.plot_results(metrics,pd.DataFrame(),stable,pd.DataFrame())
        self.assertTrue((root/'comparison/plots/paired_AP_differences_with_intervals.png').exists())

    def test_complete_and_partial_synthetic_reports(self):
        work=HERE/'tests'/'synthetic_report_fixture'
        for scenario in ['complete','partial']:
            root=work/scenario;results=root/'results';(results/'comparison').mkdir(parents=True,exist_ok=True)
            if scenario=='complete':
                (results/'provenance').mkdir(exist_ok=True)
                (results/'provenance/resolved_training_progress_gap.json').write_text(json.dumps({'update_gap_seconds':60}))
            (root/'SYNTHETIC_TEST_ONLY.md').write_text('Synthetic rendering fixture, not experimental evidence.\n')
            coverage=[{'seed':s,'matched_folds':[f'fold_{i:02}' for i in range(1,6)] if scenario=='complete' else [],'count':5 if scenario=='complete' else 0,'complete':scenario=='complete'} for s in [42,20261023]]
            stable=[];oo=[];comp=[]
            if scenario=='complete':
                for seed in [42,20261023]:
                    for branch in ['visual','uniform','F2']:
                        stable.append({'seed':seed,'branch':branch,'frozen_pooled_AP':.2,'finetuned_pooled_AP':.3,'pooled_AP_difference':.1,'percentile95_low':-.02,'percentile95_high':.2,'frozen_mean_fold_AP':.21,'finetuned_mean_fold_AP':.31})
                    for fold in coverage[0]['matched_folds']:
                        for condition,ap in zip(analysis.CONDITIONS,[.2,.3]):
                            for role in ['inner_OOF','outer_assessment']:oo.append({'seed':seed,'fold':fold,'condition':condition,'evaluation_role':role,'AP':ap})
                    comp.append({'seed':seed,'scope':'pooled','group':'sensor_missed_failure','samples':3,'visual_Brier_change':-.01,'visual_log_loss_change':-.01,'uniform_Brier_change':-.01,'F2_Brier_change':.01,'F2_log_loss_change':.01})
                pd.DataFrame(oo).to_csv(results/'comparison/oof_vs_assessment.csv',index=False)
                pd.DataFrame(comp).to_csv(results/'comparison/complementarity.csv',index=False)
            causes=[{'candidate':'Synthetic only','evidence_for':'Synthetic','evidence_against_or_limit':'Synthetic','status':'Unresolved'}]
            with patch.object(analysis,'ROOT',results),patch.object(analysis,'STUDY',root),patch.object(analysis,'event') as event:
                analysis.write_reports('COMPLETE' if scenario=='complete' else 'PARTIAL_NEW_SEED',coverage,pd.DataFrame(),pd.DataFrame(stable),causes,[],[])
                self.assertTrue((results/'comparison/RESULTS_SUMMARY.md').exists())
                self.assertIn('CAUSE_NOT_RESOLVED',(root/'README_FIRST.md').read_text())
                if scenario=='complete':
                    self.assertIn('progress-update gap lasted 1.00 minutes',(results/'comparison/RESULTS_SUMMARY.md').read_text())
                event.assert_called_once()

if __name__=='__main__':unittest.main(verbosity=2)
