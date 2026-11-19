"""Drain prefetched decoding before joining persistent DataLoader workers.

Each worker traverses a disjoint stride, preserving DataLoader's global FIFO
sample order. A shared stop event ends iteration after the current decode and
closes video handles before process shutdown. No scientific update is added.
"""
import gc
import multiprocessing
import uuid

from torch.utils.data import DataLoader, IterableDataset, get_worker_info

import gpu_audit as audit


class CooperativeDataset(IterableDataset):
    def __init__(self, mapped, stop):
        self.mapped, self.stop = mapped, stop

    def __iter__(self):
        worker = get_worker_info()
        index, stride = (worker.id, worker.num_workers) if worker else (0, 1)
        try:
            while index < len(self.mapped) and not self.stop.is_set():
                yield self.mapped[index]
                index += stride
        finally:
            decoder = getattr(self.mapped, "decoder", None)
            if decoder is not None:
                for capture in decoder.captures.values():
                    capture.release()
                decoder.captures.clear()
                self.mapped.decoder = None
            gc.collect()


class IteratorGuard:
    def __init__(self, raw, stop, run, name):
        self.raw, self.stop, self.run, self.name = raw, stop, run, name
        self.closed = False

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.raw)

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def _shutdown_workers(self):
        if self.closed:
            return
        self.closed = True
        self.stop.set()
        drained = 0
        for _ in self.raw:
            drained += 1
        self.raw._shutdown_workers()
        codes = [w.exitcode for w in self.raw._workers]
        audit.write(self.run / "checks" / (self.name + "_worker_shutdown_" + uuid.uuid4().hex[:8] + ".json"),
                    {"worker_exitcodes": codes, "prefetched_actions_drained_without_training": drained,
                     "passed": all(c == 0 for c in codes), "method": "cooperative iteration exhaustion, decoder release, join"})
        assert all(c == 0 for c in codes), ("UNCLEAN_WORKER_SHUTDOWN", codes)


class ManagedLoader(DataLoader):
    def __init__(self, dataset, stop, run, name, **kwargs):
        self.audit_stop, self.audit_run, self.audit_name = stop, run, name
        super().__init__(dataset, **kwargs)

    def __iter__(self):
        raw = super().__iter__()
        guard = IteratorGuard(raw, self.audit_stop, self.audit_run, self.audit_name)
        self._iterator = guard
        return guard


def loader(run, setting, repeats=1000):
    import torch

    assert setting["workers"] > 0 and setting["persistent_workers"]
    stop = multiprocessing.get_context("spawn").Event()
    mapped = audit.PixelDataset(run, repeats)
    return ManagedLoader(
        CooperativeDataset(mapped, stop), stop, run, setting["name"],
        batch_size=None, num_workers=setting["workers"],
        pin_memory=setting["pin_memory"], persistent_workers=True,
        prefetch_factor=setting["prefetch_factor"], multiprocessing_context="spawn",
        generator=torch.Generator().manual_seed(91427), worker_init_fn=audit.worker_init,
    )
