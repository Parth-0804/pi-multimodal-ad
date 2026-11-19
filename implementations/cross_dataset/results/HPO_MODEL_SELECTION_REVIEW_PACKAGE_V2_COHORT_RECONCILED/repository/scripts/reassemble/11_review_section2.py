"""Post-hoc descriptive paired contrasts for final review; no fitting or tuning."""
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
import numpy as np
from reassemble.section1_features import cohort
from reassemble.section1_report import metrics, METRICS


def main():
    config = json.loads(Path('configs/reassemble/section2.json').read_text())
    run = Path(config['run_dir'])
    destination = run / 'assessment/review_comparisons.json'
    if destination.exists():
        raise FileExistsError('Preserve completed review evidence: ' + str(destination))
    frame = cohort(json.loads(Path(config['section1_config']).read_text()))
    with np.load(run / 'predictions/oof.npz') as z:
        p = {key: z[key] for key in z.files}
    y = p['y']
    models = ['F1', 'F2', 'F3', 'F4', 'F5']
    pairs = [('F1', 'F2'), ('F3', 'F2'), ('F4', 'F5')]
    point = np.stack([metrics(y, p[m+'_p'], p[m+'_hard']) for m in models])
    groups, gi = np.unique(frame.recording_id, return_inverse=True)
    rng = np.random.default_rng(config['seed'] + 50000)
    boot = []
    for _ in range(2000):
        w = np.bincount(rng.integers(len(groups), size=len(groups)), minlength=len(groups))[gi]
        boot.append(np.stack([metrics(y, p[m+'_p'], p[m+'_hard'], w) for m in models]))
    boot = np.stack(boot)
    results = {}
    for a, b in pairs:
        i, j = models.index(a), models.index(b)
        low, high = np.quantile(boot[:, i] - boot[:, j], [.025, .975], axis=0)
        results[a+'-'+b] = {m: {'estimate': float(point[i,k]-point[j,k]), 'lower_95': float(low[k]), 'upper_95': float(high[k])} for k, m in enumerate(METRICS)}
    artifact = {'status': 'Post-hoc descriptive review contrasts; not predeclared additional claims, no model fitting or selection changes', 'bootstrap_replicates': 2000, 'bootstrap_seed': config['seed']+50000, 'paired': results}
    with destination.open('x') as f:
        json.dump(artifact, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
