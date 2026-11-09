"""Importable spawn-process fixture: eight synthetic scalar actions only."""
import torch
from torch.utils.data import Dataset


class SyntheticActions(Dataset):
    def __init__(self):
        self.order = torch.arange(8).share_memory_()
        self.decoder = None

    def __len__(self):
        return len(self.order)

    def __getitem__(self, index):
        value = int(self.order[index])
        return torch.tensor([float(value)]), torch.tensor([value % 2.]), str(value), value
