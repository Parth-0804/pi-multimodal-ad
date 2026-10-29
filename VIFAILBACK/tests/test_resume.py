import random
import numpy as np
import torch
from vifailback.training import rng_state,restore_rng


def test_checkpoint_rng_and_optimizer_reproduce_next_update():
    torch.manual_seed(42);random.seed(42);np.random.seed(42)
    model=torch.nn.Sequential(torch.nn.Linear(3,4),torch.nn.Dropout(.2),torch.nn.Linear(4,1))
    opt=torch.optim.AdamW(model.parameters(),lr=.001)
    x=torch.randn(2,3)
    def step():
        opt.zero_grad();loss=model(x).square().mean();loss.backward();opt.step();return loss.detach()
    step()
    import io
    stream=io.BytesIO();torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'rng':rng_state()},stream)
    expected=step();parameters={n:p.detach().clone() for n,p in model.named_parameters()}
    stream.seek(0);state=torch.load(stream,weights_only=True);model.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);restore_rng(state['rng'])
    assert torch.equal(step(),expected)
    assert all(torch.equal(p,parameters[n]) for n,p in model.named_parameters())
