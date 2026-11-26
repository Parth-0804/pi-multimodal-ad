"""Ordered finite epochs extending the validated cooperative GPU-audit loader."""
import hashlib
import multiprocessing as mp
import sys
import uuid

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from phase_common import AUDIT, STUDY, EXEC, EVIDENCE, REPO, read, config, write
sys.path.insert(0, str(AUDIT / 'source'))
from isolated_decode import IsolatedDecoder
from managed_loader import ManagedLoader, CooperativeDataset, IteratorGuard
from gpu_audit import worker_init


class ActionDataset(Dataset):
    def __init__(self, order):
        self.rows = read(EVIDENCE / 'PHASE1_INPUT_IDENTITY_MANIFEST.json')
        self.order = torch.tensor(order, dtype=torch.int64).share_memory_()
        self.decoder = None

    def __len__(self):
        return len(self.order)

    def __getitem__(self, index):
        row = self.rows[int(self.order[index])]
        if self.decoder is None:
            original = read(STUDY / 'config/resolved_config.json')
            self.decoder = IsolatedDecoder(REPO, original['weights_dir'], original['rescale_factor'], decoder_threads=2)
        pixels = self.decoder(dict(row, frames32=row['frames16']))
        assert pixels.shape == (16, 3, 640, 640) and pixels.dtype == np.uint8
        assert hashlib.sha256(pixels.tobytes()).hexdigest() == row['selected16_sha256'], ('PIXEL_DRIFT', row['sample_id'])
        x = torch.from_numpy(pixels.astype('float32') * np.float32(1 / 255))
        return x, torch.tensor([row['failure']], dtype=torch.float32), row['sample_id'], int(self.order[index])


class PhaseIteratorGuard(IteratorGuard):
    def _shutdown_workers(self):
        if self.closed:
            return
        self.closed = True
        self.stop.set()
        drained = 0
        try:
            for _ in self.raw:
                drained += 1
        finally:
            self.raw._shutdown_workers()
        codes = [worker.exitcode for worker in self.raw._workers]
        write(self.run / '26102026_checks' / (self.name + '_shutdown_' + uuid.uuid4().hex[:8] + '.json'),
              {'worker_exitcodes': codes, 'prefetched_actions_drained_without_training': drained,
               'passed': all(code == 0 for code in codes)})
        assert all(code == 0 for code in codes), ('UNCLEAN_WORKER_SHUTDOWN', codes)


class EpochLoader(ManagedLoader):
    """Reset the same guard/raw iterator, rather than nesting guards each epoch."""
    def __init__(self, rows, folder, role, workers=None, mapped=None, pin_memory=True):
        c = config()
        workers = c['loader_workers'] if workers is None else workers
        assert workers > 0
        self.mapped = ActionDataset(rows) if mapped is None else mapped
        self.stop_event = mp.get_context('spawn').Event()
        super().__init__(CooperativeDataset(self.mapped, self.stop_event), self.stop_event, folder, role,
            batch_size=None, num_workers=workers, pin_memory=pin_memory, persistent_workers=True,
            prefetch_factor=c['prefetch_factor'], multiprocessing_context='spawn',
            generator=torch.Generator().manual_seed(91427), worker_init_fn=worker_init)

    def set_order(self, order):
        assert len(order) == len(self.mapped.order)
        self.mapped.order.copy_(torch.as_tensor(order, dtype=torch.int64))

    def __iter__(self):
        if self._iterator is None:
            raw = DataLoader.__iter__(self)
            self._iterator = PhaseIteratorGuard(raw, self.stop_event, self.audit_run, self.audit_name)
        else:
            assert not self._iterator.closed, 'Closed loader cannot be restarted'
            self._iterator.raw._reset(self)
        return self._iterator

    def close(self):
        if self._iterator is not None:
            self._iterator._shutdown_workers()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def epoch_order(rows, seed, epoch):
    return np.asarray(rows, dtype=int)[np.random.default_rng(seed + 100003 * epoch).permutation(len(rows))]
