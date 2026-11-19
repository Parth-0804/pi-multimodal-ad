"""Read-only metric verification from the exported CSV; no CNN/data download."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import csv
import json
import numpy as np
from common import ROOT, read
from evaluate import NAMES, independent_metrics


def main():
    with (ROOT/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len({r['sample_id'] for r in rows}) == 753
    y = np.array([int(r['failure']) for r in rows])
    expected = read(ROOT/'07_evaluation_results/ALL_MODEL_METRICS.json')
    actual = {}
    for name in NAMES:
        values = independent_metrics(y, [float(r[name]) for r in rows], threshold=.5)
        assert max(abs(value-expected[name][key]) for key,value in values.items()) < 1e-12
        actual[name] = values
    paired = read(ROOT/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json')
    draws = read(ROOT/'07_evaluation_results/BOOTSTRAP_METRIC_DRAWS.json')
    for contrast in paired['differences'].values():
        for metric in ['AP', 'AUROC']:
            distribution = np.array(draws[contrast['treatment']][metric])-np.array(draws[contrast['control']][metric])
            bounds = np.quantile(distribution, [.025, .975])
            assert np.max(abs(bounds-[contrast[metric]['lower95'], contrast[metric]['upper95']])) < 1e-12
    print(json.dumps({'passed': True, 'implementation': 'Separate NumPy/tie-group AP and rank-AUROC formulas',
                      'CSV_actions': len(rows), 'positive_failures': int(y.sum()),
                      'absolute_tolerance': 1e-12, 'metrics': actual,
                      'paired_interval_recalculation_from_saved_draws': 'PASS',
                      'files_modified': False}, indent=2))


if __name__ == '__main__':main()
