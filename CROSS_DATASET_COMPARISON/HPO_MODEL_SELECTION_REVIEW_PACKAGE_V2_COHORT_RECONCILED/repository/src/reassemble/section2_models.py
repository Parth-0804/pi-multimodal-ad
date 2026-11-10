"""Small clean-fusion heads; context reaches the output only via gate weights."""
import time
import numpy as np
import torch
from torch import nn
from .section1_models import Standardizer


class ConcatHead(nn.Module):
    def __init__(self, sensor_width, hidden, dropout):
        super().__init__()
        self.visual = nn.Sequential(nn.Linear(128, 128), nn.ReLU())
        self.sensor = nn.Sequential(nn.Linear(sensor_width, 128), nn.ReLU())
        self.head = nn.Sequential(nn.LayerNorm(256), nn.Linear(256, hidden),
                                  nn.ReLU(), nn.Dropout(dropout), nn.Linear(hidden, 1))

    def forward(self, visual, sensor):
        return self.head(torch.cat([self.visual(visual), self.sensor(sensor)], -1)).squeeze(-1)


class DecisionGate(nn.Module):
    def __init__(self, width, hidden):
        super().__init__()
        self.gate = nn.Sequential(nn.Linear(width, hidden), nn.ReLU(), nn.Linear(hidden, 2))

    def forward(self, context, logits, availability):
        if not bool(availability.bool().any(dim=1).all()):
            raise ValueError('No branch available; no unsupported fallback prediction')
        allocation = self.gate(context).masked_fill(~availability.bool(), -torch.inf)
        weights = torch.softmax(allocation, dim=-1)
        safe_logits = torch.where(availability.bool(), logits, torch.zeros_like(logits))
        return (weights * safe_logits).sum(-1), weights


def logit(p, clip=1e-6):
    p = np.clip(p, clip, 1 - clip)
    return np.log(p / (1 - p)).astype('float32')


def context(kind, action, quality, availability):
    parts = []
    if kind in ['F4', 'F6']:
        parts.append(action)
    if kind in ['F5', 'F6']:
        parts.append(quality)
    return np.concatenate(parts + [availability], axis=1).astype('float32')


def fit_head(kind, train_data, test_data, labels, settings, config, seed, ablations=None, save=None):
    """No assessment labels accepted. Normalizers are fitted exclusively to train_data."""
    torch.manual_seed(seed)
    started = time.perf_counter()
    tensor = lambda a: torch.as_tensor(np.asarray(a), dtype=torch.float32, device='cuda')
    scalers = {}
    if kind == 'F3':
        for key in ['visual', 'statistics']:
            scalers[key] = Standardizer().fit(train_data[key])
        train = [tensor(scalers[k].transform(train_data[k])) for k in ['visual', 'statistics']]
        test = [tensor(scalers[k].transform(test_data[k])) for k in ['visual', 'statistics']]
        model = ConcatHead(train[1].shape[1], settings['hidden'], config['dropout']).cuda()
    else:
        scalers['quality'] = Standardizer().fit(train_data['quality'])
        def gate_inputs(data, change=None):
            action = data['action'].copy()
            quality = scalers['quality'].transform(data['quality'])
            if change == 'action_zero':
                action[:] = 0
            elif change == 'action_permuted':
                action = action[ablations['permutation']]
            elif change == 'quality_neutral':
                quality[:] = 0
            return [tensor(context(kind, action, quality, data['availability'])),
                    tensor(logit(data['probabilities'], config['probability_clip'])),
                    tensor(data['availability'])]
        train = gate_inputs(train_data)
        test = gate_inputs(test_data)
        model = DecisionGate(train[0].shape[1], settings['hidden']).cuda()
    target = tensor(labels)
    positive_weight = tensor((len(labels) - np.sum(labels)) / np.sum(labels)) if kind == 'F3' else None
    criterion = nn.BCEWithLogitsLoss(pos_weight=positive_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=settings['lr'], weight_decay=settings['weight_decay'])
    generator = torch.Generator(device='cuda').manual_seed(seed)
    losses = []
    for epoch in range(settings['epochs']):
        model.train()
        total = 0.
        for ix in torch.randperm(len(labels), generator=generator, device='cuda').split(config['batch_size']):
            optimizer.zero_grad(set_to_none=True)
            output = model(*[a[ix] for a in train])
            raw = output if kind == 'F3' else output[0]
            loss = criterion(raw, target[ix])
            assert torch.isfinite(loss)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.)
            optimizer.step()
            total += float(loss.detach()) * len(ix)
        losses.append(total / len(labels))
    torch.cuda.synchronize()
    training_seconds = time.perf_counter() - started
    model.eval()
    def predict(inputs):
        with torch.inference_mode():
            output = model(*inputs)
            if kind == 'F3':
                return {'raw': output.cpu().numpy()}
            return {'raw': output[0].cpu().numpy(), 'weights': output[1].cpu().numpy()}
    result = predict(test)
    # Warm batch timing, excluding branches, transfer and preprocessing.
    with torch.inference_mode():
        torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(20):
            model(*test)
        torch.cuda.synchronize()
    elapsed = (time.perf_counter() - start) / 20
    if ablations and kind != 'F3':
        result['ablations'] = {name: predict(gate_inputs(test_data, name)) for name in ablations['names']}
    metadata = {'seed': seed, 'parameters': sum(p.numel() for p in model.parameters()),
                'training_seconds': training_seconds, 'inference_batch_seconds': elapsed,
                'inference_batch_rows': len(test_data['action']),
                'loss_by_epoch': losses,
                'normalizers': {k: {'mean': s.mean.tolist(), 'std': s.std.tolist()} for k, s in scalers.items()}}
    if save is not None:
        torch.save({'state_dict': model.cpu().state_dict(), 'kind': kind, 'settings': settings,
                    'normalizers': metadata['normalizers'], 'seed': seed}, save)
    return result, metadata
