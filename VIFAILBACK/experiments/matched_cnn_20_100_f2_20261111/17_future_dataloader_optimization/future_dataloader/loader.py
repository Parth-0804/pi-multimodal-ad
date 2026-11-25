"""Opt-in future loader using the unchanged study episode/frame implementation."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

import torch
from torch.utils.data import DataLoader, Dataset, IterableDataset

from .settings import LoaderConfig


def build_loader(
    ctx: Mapping,
    ids: Iterable[int],
    config: LoaderConfig,
    *,
    dataset: Dataset | None = None,
) -> DataLoader:
    """Preserve caller episode order and the original ``(episode_id, pixels)``.

    Production loading reuses the frozen study's ``Episodes`` class, including
    all source/frame integrity checks and its original FP32 preprocessing.  The
    optional map-style dataset exists for isolated CPU contract tests.  It must
    have exactly one item per supplied ID, in that order.

    No global RNG, CPU affinity, thread count, active protocol or controller is
    changed.  The separate generator matches the original seed and protects the
    main-process CPU dropout RNG from DataLoader worker-seeding draws.
    """
    if not isinstance(config, LoaderConfig):
        raise TypeError("config must be a validated LoaderConfig")
    ordered_ids = tuple(int(eid) for eid in ids)
    if dataset is None:
        # Lazy import keeps synthetic CPU tests independent of trainer imports.
        from matched_vifailback.training import Episodes

        dataset = Episodes(ctx["config"], [ctx["lookup"][eid] for eid in ordered_ids])
    if not isinstance(dataset, Dataset) or isinstance(dataset, IterableDataset):
        raise TypeError("An ordered map-style Dataset is required")
    if len(dataset) != len(ordered_ids):
        raise ValueError("Dataset length must equal the requested episode-ID count")
    return DataLoader(
        dataset,
        batch_size=None,
        shuffle=False,
        num_workers=config.num_workers,
        prefetch_factor=config.prefetch_factor,
        pin_memory=config.pin_memory,
        persistent_workers=config.persistent_workers,
        multiprocessing_context=config.multiprocessing_context,
        generator=torch.Generator().manual_seed(314159),
        # Explicitly retain the installed DataLoader's original default.  The
        # baseline trainer relies on the same ordered-delivery behavior.
        in_order=True,
    )
