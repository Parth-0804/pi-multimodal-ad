"""Tiny CPU-only spawn/order checks; no videos, CNNs, CUDA or training."""
from __future__ import annotations

import os

# Must be set before importing torch, including in spawned worker interpreters.
if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
    raise RuntimeError("Run these preparation tests with CUDA_VISIBLE_DEVICES='' before Python starts")

from dataclasses import FrozenInstanceError, replace
import random

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader, Dataset, IterableDataset

from future_dataloader.loader import build_loader
from future_dataloader.settings import LoaderConfig, PRESETS


IDS = (101, 8, 49, 12, 66, 5, 99, 1, 44, 31, 19, 72, 17, 88, 4, 60, 23)
LABELS = {eid: (index % 3 == 0) for index, eid in enumerate(IDS)}


class TinyEpisodes(Dataset):
    """Non-sorted IDs, 48 camera/time positions and exact FP32 values."""

    def __init__(self, ids=IDS):
        self.ids = tuple(ids)

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, index):
        eid = self.ids[index]
        # Encode ID, camera, time and channel, with no random input values.
        x = torch.arange(3 * 16 * 3 * 2 * 2, dtype=torch.float32).reshape(3, 16, 3, 2, 2)
        return eid, x + eid * 1024


class InvalidIterable(IterableDataset):
    def __iter__(self):
        yield 1, torch.zeros(1)


def _numpy_state_equal(left, right):
    return left[0] == right[0] and np.array_equal(left[1], right[1]) and left[2:] == right[2:]


@pytest.mark.parametrize("name", tuple(PRESETS))
def test_spawn_preserves_ids_values_labels_partial_batch_and_main_rng(name):
    """All presets consume exactly 8+8+1 episodes without RNG or data drift."""
    config = PRESETS[name]
    dataset = TinyEpisodes()
    torch.manual_seed(987)
    random.seed(654)
    np.random.seed(321)
    before_torch = torch.get_rng_state().clone()
    before_python = random.getstate()
    before_numpy = np.random.get_state()
    loader = build_loader({}, IDS, config, dataset=dataset)
    assert loader.batch_size is None and loader.in_order is True
    assert loader.pin_memory is True and loader.persistent_workers is False
    assert loader.multiprocessing_context.get_start_method() == "spawn"
    assert loader.generator.initial_seed() == 314159
    assert loader.num_workers == config.num_workers
    assert loader.prefetch_factor == config.prefetch_factor
    actual = list(loader)
    assert [int(eid) for eid, _ in actual] == list(IDS)
    for index, (eid, pixels) in enumerate(actual):
        expected_id, expected_pixels = dataset[index]
        assert eid == expected_id
        assert pixels.dtype == torch.float32
        assert tuple(pixels.shape) == (3, 16, 3, 2, 2)
        assert torch.equal(pixels, expected_pixels)
        assert LABELS[eid] == (index % 3 == 0)
    chunks = [actual[start:start + 8] for start in range(0, len(actual), 8)]
    assert [len(chunk) for chunk in chunks] == [8, 8, 1]
    assert [[LABELS[eid] for eid, _ in chunk] for chunk in chunks] == [
        [LABELS[eid] for eid in IDS[start:start + 8]] for start in range(0, len(IDS), 8)
    ]
    assert torch.equal(torch.get_rng_state(), before_torch)
    assert random.getstate() == before_python
    assert _numpy_state_equal(np.random.get_state(), before_numpy)


def test_baseline_constructor_matches_current_loader_arguments():
    """Match the frozen factory's settings without importing/patching its code."""
    reference = DataLoader(
        TinyEpisodes(), batch_size=None, num_workers=2, pin_memory=True,
        prefetch_factor=1, persistent_workers=False, multiprocessing_context="spawn",
        generator=torch.Generator().manual_seed(314159),
    )
    actual = build_loader({}, IDS, PRESETS["baseline_w2_p1"], dataset=TinyEpisodes())
    for attribute in ("batch_size", "num_workers", "pin_memory", "prefetch_factor", "persistent_workers", "in_order"):
        assert getattr(actual, attribute) == getattr(reference, attribute)
    assert list(actual.sampler) == list(reference.sampler)
    assert actual.multiprocessing_context.get_start_method() == reference.multiprocessing_context.get_start_method()
    assert torch.equal(actual.generator.get_state(), reference.generator.get_state())


def test_configs_and_presets_are_immutable_and_bounded():
    baseline = PRESETS["baseline_w2_p1"]
    with pytest.raises(FrozenInstanceError):
        baseline.num_workers = 4
    with pytest.raises(TypeError):
        PRESETS["new"] = baseline
    assert {name: config.max_prefetched_episodes for name, config in PRESETS.items()} == {
        "baseline_w2_p1": 2, "w4_p1": 4, "w4_p2": 8, "w2_p4": 8,
    }
    assert baseline.as_dict() == {
        "name": "baseline_w2_p1", "num_workers": 2, "prefetch_factor": 1,
        "pin_memory": True, "persistent_workers": False,
        "multiprocessing_context": "spawn",
    }


@pytest.mark.parametrize("changes", [
    {"name": ""}, {"name": "  "}, {"name": None},
    {"num_workers": 0}, {"num_workers": -1}, {"num_workers": 5},
    {"num_workers": True}, {"num_workers": 2.0},
    {"prefetch_factor": 0}, {"prefetch_factor": -1}, {"prefetch_factor": 5},
    {"prefetch_factor": True}, {"prefetch_factor": 1.0},
    {"num_workers": 4, "prefetch_factor": 4},
    {"pin_memory": False}, {"pin_memory": 1},
    {"persistent_workers": True}, {"persistent_workers": 0},
    {"multiprocessing_context": "fork"}, {"multiprocessing_context": None},
])
def test_unsupported_or_unbounded_settings_are_rejected(changes):
    with pytest.raises(ValueError):
        replace(PRESETS["baseline_w2_p1"], **changes)


def test_dataset_length_and_kind_must_match_ordered_contract():
    with pytest.raises(ValueError, match="length"):
        build_loader({}, IDS[:-1], PRESETS["baseline_w2_p1"], dataset=TinyEpisodes())
    with pytest.raises(TypeError, match="map-style"):
        build_loader({}, [1], PRESETS["baseline_w2_p1"], dataset=InvalidIterable())
    with pytest.raises(TypeError, match="config"):
        build_loader({}, IDS, {"num_workers": 2}, dataset=TinyEpisodes())
