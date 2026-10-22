#!/usr/bin/env python3
"""Versioned pre-noise selection after encoder completion; preserves run_01.

Same fixed predictor/corruption protocol and original cumulative budgets.
Only the evidence available for clean selection and the output run change.
"""
from pathlib import Path
import importlib.util
import io
import os
import sys
STUDY=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('noise_entry',STUDY/'run_experiment.py')
entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
import common
RUN=STUDY/'results/run_02'
common.RUN=RUN;entry.RUN=RUN
original_code_identity=common.code_identity

def active_code_identity():
    return original_code_identity()|{name:common.sha(STUDY/name) for name in ['run_after_encoder.py','run02_input_adapter.py']}

common.code_identity=active_code_identity;entry.code_identity=active_code_identity
for key,name in [('TMPDIR','tmp'),('MPLCONFIGDIR','matplotlib'),('XDG_CACHE_HOME','xdg'),('HF_HOME','huggingface')]:
    p=RUN/'cache'/name;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)



# Keep generated resume instructions and current status bound to run_02.
import reporting
base_report=reporting.report

def report_here():
    if (RUN/'progress.json').exists():
        state=common.read(RUN/'progress.json')
        if state.get('status')=='WAITING_FOR_PREVIOUS_RESULTS':
            state['blocker']='Encoder results are still changing; clean selection deferred. The visual task is checkpoint-paused by user request.'
            common.write(RUN/'progress.json',state)
    base_report()
    for relative in ['README_FIRST.md','how_to_resume.md','model_selection/selection_report.md','comparison/RESULTS_SUMMARY.md']:
        path=RUN/relative
        if path.exists():
            text=path.read_text().replace('fusion_noise_test/run_experiment.py','fusion_noise_test/run_after_encoder.py')
            text+='\n\nVersioned pre-noise decision: run_02 uses the same fixed scientific protocol and original cumulative budgets after encoder completion. The earlier incomplete run_01 selection is preserved. No corrupted assessment predictions existed when this revision was prepared. Selection still requires terminal, stable inputs and uses the original eligibility, whole-fold coverage, AP and tie rules.\n'
            common.write_text(path,text)

reporting.report=report_here
sys.path.insert(0,str(STUDY))
import run02_input_adapter
run02_input_adapter.install()

def main():
    if len(sys.argv)>1 and sys.argv[1]=='test':
        import unittest
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(STUDY/'tests'))
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        index=len(list((RUN/'checks').glob('test_attempt_*.txt')))+1
        common.write_text(RUN/'checks'/f'test_attempt_{index:02d}.txt',stream.getvalue())
        common.write(RUN/'checks/tests.json',{'passed':result.wasSuccessful(),'returncode':0 if result.wasSuccessful() else 1,'command':sys.argv,'source_identity':active_code_identity(),'scope':'CPU tests in the new output run; no scientific model selection, training or GPU inference'})
        print(stream.getvalue());raise SystemExit(0 if result.wasSuccessful() else 1)
    entry.main()


if __name__=='__main__':main()
