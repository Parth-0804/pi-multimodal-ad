"""Completed-epoch transactional recovery, with two retained generations."""
from pathlib import Path
import os
import random

import numpy as np
import torch

from phase_common import ROOT, sha, read, write, utc


def rng_state():
    return {'python': random.getstate(), 'numpy': np.random.get_state(), 'cpu': torch.get_rng_state(),
            'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_initialized() else []}


def restore_rng(state):
    random.setstate(state['python'])
    np.random.set_state(state['numpy'])
    torch.set_rng_state(state['cpu'])
    if state['cuda']:
        torch.cuda.set_rng_state_all(state['cuda'])


def cpu_tree(value):
    if torch.is_tensor(value):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {k: cpu_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [cpu_tree(v) for v in value]
    if isinstance(value, tuple):
        return tuple(cpu_tree(v) for v in value)
    return value


def atomic_torch_save(path, data):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.writing')
    with temp.open('wb') as stream:
        torch.save(data, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def selected_payloads(folder, best, short_best):
    """Commit selected weights in the same transaction as epoch recovery."""
    result = {}
    for name, selection in [('PHASE1_BEST_MODEL.pt', best), ('PHASE1_MATCHED_SHORT_MODEL.pt', short_best)]:
        if selection is not None:
            payload = torch.load(Path(folder) / name, map_location='cpu', weights_only=True)
            assert payload['selected_epoch'] == selection['epoch']
            result[name] = payload
    return result


def restore_selections(folder, state):
    # An interruption can occur after best-model replacement but before the
    # epoch pointer commits. Restore the weights belonging to the committed
    # boundary, rather than retaining an uncommitted future selection.
    for name, payload in state.get('selected_payloads', {}).items():
        assert name in ('PHASE1_BEST_MODEL.pt', 'PHASE1_MATCHED_SHORT_MODEL.pt')
        atomic_torch_save(Path(folder) / name, payload)


class EpochRecovery:
    def __init__(self, folder, identity):
        self.folder = Path(folder)
        self.identity = identity
        self.pointer = self.folder / 'PHASE1_LATEST_EPOCH.json'

    def save(self, state):
        generation = state['completed_epoch']
        slot = self.folder / ('PHASE1_EPOCH_SLOT_' + str(generation % 2) + '.pt')
        atomic_torch_save(slot, dict(cpu_tree(state), fit_identity=self.identity, random=rng_state(),
                                     boundary='completed_epoch', saved_utc=utc()))
        write(self.pointer, {'slot': slot.name, 'sha256': sha(slot), 'completed_epoch': generation,
                             'fit_identity': self.identity, 'boundary': 'completed_epoch'})

    def load(self):
        if not self.pointer.exists():
            return None
        pointer = read(self.pointer)
        assert pointer['fit_identity'] == self.identity
        slot = self.folder / pointer['slot']
        assert sha(slot) == pointer['sha256'], 'CHECKPOINT_INTEGRITY_FAILURE'
        # This is a study-owned trusted checkpoint, never an untrusted download.
        value = torch.load(slot, map_location='cpu', weights_only=False)
        assert value['boundary'] == 'completed_epoch' and value['fit_identity'] == self.identity
        assert value['completed_epoch'] == pointer['completed_epoch']
        return value
