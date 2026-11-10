"""Owned-job completion must be accepted when its process has already exited."""
import sys
from pathlib import Path
sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
from external_eval import run_all


def test_completed_feature_receipt_wins_over_process_exit(tmp_path,monkeypatch):
    done=tmp_path/'03_processed_model_inputs/visual_features/P/complete.json';done.parent.mkdir(parents=True)
    seen=[]
    def owned(*args):
        seen.append(True);return 123 if len(seen)==1 else None
    monkeypatch.setattr(run_all,'owned_running',owned)
    monkeypatch.setattr(run_all.time,'sleep',lambda seconds:done.write_text('{}'))
    monkeypatch.setattr(run_all,'invoke',lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('Existing extraction must not restart')))
    run_all.gpu_features(tmp_path,'P')
    assert done.exists() and len(seen)==1
