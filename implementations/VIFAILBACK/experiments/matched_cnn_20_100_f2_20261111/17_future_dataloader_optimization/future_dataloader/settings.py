"""Bounded, opt-in settings for an independently admitted future loader.

These settings are not imported by the active study or its queued fits.  Only
worker concurrency and per-worker prefetch depth differ among the candidates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class LoaderConfig:
    name: str
    num_workers: int
    prefetch_factor: int
    pin_memory: bool = True
    persistent_workers: bool = False
    multiprocessing_context: str = "spawn"

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Loader configuration requires a nonempty name")
        # bool is an int subclass; reject it rather than accepting True as 1.
        if type(self.num_workers) is not int or not 1 <= self.num_workers <= 4:
            raise ValueError("num_workers must be an integer from 1 to 4")
        if type(self.prefetch_factor) is not int or not 1 <= self.prefetch_factor <= 4:
            raise ValueError("prefetch_factor must be an integer from 1 to 4")
        if self.max_prefetched_episodes > 8:
            raise ValueError("At most eight episodes may be scheduled for prefetch")
        if self.pin_memory is not True:
            raise ValueError("This comparison preserves pin_memory=True")
        if self.persistent_workers is not False:
            raise ValueError("Persistent workers require a separate loader-lifecycle design")
        if self.multiprocessing_context != "spawn":
            raise ValueError("This comparison preserves the spawn start method")

    @property
    def max_prefetched_episodes(self) -> int:
        """Scheduled loader tasks; excludes trainer-held tensors and copies."""
        return self.num_workers * self.prefetch_factor

    def as_dict(self) -> dict:
        return asdict(self)


PRESETS = MappingProxyType({
    "baseline_w2_p1": LoaderConfig("baseline_w2_p1", 2, 1),
    "w4_p1": LoaderConfig("w4_p1", 4, 1),
    "w4_p2": LoaderConfig("w4_p2", 4, 2),
    "w2_p4": LoaderConfig("w2_p4", 2, 4),
})
