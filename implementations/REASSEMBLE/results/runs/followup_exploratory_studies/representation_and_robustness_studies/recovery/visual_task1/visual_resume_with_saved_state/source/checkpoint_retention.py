"""Recover selected S-6 inner states with one deterministic same-budget replay."""
from pathlib import Path
import numpy as np
from .common import setup, inputs, read, write, identity, progress
from .neural import _fit


def recover_selected_short_states():
    c=setup();c,base,frame,arrays,splits=inputs();root=Path(c['run_dir'])/'02_patchtst_training_budget'
    destination=root/'fits/S-6_selected_checkpoint_replay';y=frame.failure.to_numpy(int);records=[]
    for outer in range(5):
        folder=root/'fits/S-6'/f'outer{outer}';branch=read(folder/'branch.json')
        for seed in branch['seeds']:
            duration=seed['refit_epochs']
            for inner,info in enumerate(seed['inner_fits']):
                original=folder/f'inner{inner}_seed{seed["seed"]}'
                if info['best_epoch']==duration:
                    records.append(dict(original=str(original),selected_epoch=duration,checkpoint=info['checkpoint'],replayed=False));continue
                output=destination/f'outer{outer}_inner{inner}_seed{seed["seed"]}';output.parent.mkdir(parents=True,exist_ok=True)
                if output.with_suffix('.json').exists():
                    replay=read(output.with_suffix('.json'))
                    assert identity(output.with_suffix('.pt'))==replay['checkpoint']
                else:
                    result,replay=_fit(output,'S-6',arrays['sensor'],y,np.array(info['train_rows']),np.array(info['assessment_rows']),base,seed['seed'],duration,info['microbatch'])
                    with np.load(original.with_suffix('.npz')) as saved:
                        error=float(np.max(np.abs(result['raw']-saved[f'raw_epoch{duration}'])))
                    replay.update(reason='Retain state for already-selected3/6 epoch, no new selection or scores',original_fit=identity(original.with_suffix('.json')),original_predictions=identity(original.with_suffix('.npz')),original_selected_epoch=duration,max_logit_error=error)
                    write(output.with_suffix('.json'),replay)
                    assert error<=1e-6,('SELECTED CHECKPOINT REPLAY PARITY',str(output),error)
                assert replay['original_selected_epoch']==duration and replay['max_logit_error']<=1e-6
                records.append(dict(original=str(original),selected_epoch=duration,checkpoint=replay['checkpoint'],replayed=True,max_logit_error=replay['max_logit_error']))
    write(root/'selected_S6_checkpoint_retention.json',dict(records=records,method='Reuse matching states; otherwise one same-seed same-architecture replay to the previously selected3/6 epoch. Require saved-logit parity1e-6. Original predictions and all completed result files unchanged.',replayed_fits=sum(v['replayed'] for v in records)))
    progress(2,'Selected S-6 inner checkpoint retention verified without altering predictions')
