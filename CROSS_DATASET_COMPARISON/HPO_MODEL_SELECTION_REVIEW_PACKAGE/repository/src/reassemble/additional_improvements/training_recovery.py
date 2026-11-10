"""Atomic, bounded transient recovery state; never a scientific selected checkpoint."""
from datetime import datetime, timezone
from pathlib import Path
import os
import random
import time
import numpy as np
import torch
from .common import identity, read, write

PAUSE_REQUESTED = False


class TrainingPaused(Exception):
    pass


def request_pause(*unused):
    global PAUSE_REQUESTED
    PAUSE_REQUESTED = True


def should_pause():
    deadline = os.environ.get('REASSEMBLE_VISUAL_PAUSE_AT')
    return PAUSE_REQUESTED or bool(deadline and datetime.now(timezone.utc) >= datetime.fromisoformat(deadline))


def random_state(generator):
    state = np.random.get_state()
    return dict(torch=torch.get_rng_state(), cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
                numpy=(state[0], state[1].tolist(), int(state[2]), int(state[3]), float(state[4])),
                generator=generator.bit_generator.state, python=random.getstate())


def restore_random(state, generator):
    torch.set_rng_state(state['torch'])
    if state['cuda']:torch.cuda.set_rng_state_all(state['cuda'])
    n=state['numpy'];np.random.set_state((n[0],np.array(n[1],dtype=np.uint32),n[2],n[3],n[4]))
    generator.bit_generator.state=state['generator'];random.setstate(state['python'])


def compact_state(model):
    return {k:v.detach().cpu().clone() for k,v in model.state_dict().items()
            if k.startswith('head.') or k.startswith('backbone.encoder.stages.3.') or k in ['mean','std']}


def load_compact(model, state):
    expected=set(compact_state(model))
    if set(state)!=expected:raise ValueError('Recovery trainable/buffer state keys differ')
    result=model.load_state_dict(state,strict=False)
    if result.unexpected_keys:raise ValueError('Unexpected recovery keys')


class Recovery:
    """Two replaceable slots plus an atomic commit pointer; partial writes are ignored."""
    def __init__(self, folder, signature):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.signature=signature;self.pointer=self.folder/'committed.json'
        self.generation=-1;self.last_saved=time.monotonic()

    def load(self):
        if not self.pointer.exists():return None
        meta=read(self.pointer)
        if meta['signature']!=self.signature:raise ValueError('Recovery signature mismatch; preserve and inspect')
        if identity(meta['checkpoint']['path'])!=meta['checkpoint']:raise ValueError('Recovery checkpoint hash mismatch')
        result=torch.load(meta['checkpoint']['path'],map_location='cpu',weights_only=True)
        if result['signature']!=self.signature:raise ValueError('Recovery payload signature mismatch')
        self.generation=meta['generation']
        return result['state']

    def due(self):
        return self.generation<0 or time.monotonic()-self.last_saved>=300 or should_pause()

    def save(self, state):
        generation=self.generation+1
        target=self.folder/f'slot{generation%2}.pt'
        temporary=self.folder/f'slot{generation%2}.pending.{os.getpid()}.{time.time_ns()}'
        with temporary.open('xb') as handle:
            torch.save(dict(signature=self.signature,state=state),handle)
            handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,target)
        write(self.pointer,dict(signature=self.signature,generation=generation,checkpoint=identity(target),
                               UTC=datetime.now(timezone.utc).isoformat()),replace=True)
        with self.pointer.open('rb') as handle:os.fsync(handle.fileno())
        fd=os.open(self.folder,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
        self.generation=generation;self.last_saved=time.monotonic()


def publish_predictions(path, values):
    path=Path(path)
    if path.exists():
        with np.load(path,allow_pickle=False) as saved:
            if set(saved.files)!=set(values) or any(not np.array_equal(saved[k],v,equal_nan=True) for k,v in values.items()):
                raise ValueError('Existing final prediction artifact differs; preserve and inspect')
        return
    temporary=path.with_name(path.name+f'.pending.{os.getpid()}.{time.time_ns()}')
    with temporary.open('xb') as handle:
        np.savez_compressed(handle,**values);handle.flush();os.fsync(handle.fileno())
    os.replace(temporary,path)


def publish_selected(path, values):
    path=Path(path)
    if path.exists():
        saved=torch.load(path,map_location='cpu',weights_only=True)
        if set(saved)!=set(values) or set(saved['state_dict'])!=set(values['state_dict']):raise ValueError('Selected state keys differ')
        if any(not torch.equal(v,saved['state_dict'][k]) for k,v in values['state_dict'].items()):raise ValueError('Selected state tensors differ')
        if any(saved[k]!=v for k,v in values.items() if k!='state_dict'):raise ValueError('Selected checkpoint metadata differs')
        return
    temporary=path.with_name(path.name+f'.pending.{os.getpid()}.{time.time_ns()}')
    with temporary.open('xb') as handle:
        torch.save(values,handle);handle.flush();os.fsync(handle.fileno())
    os.replace(temporary,path)
