"""Saved-prediction figures and fixed post-fit disagreement examples."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import hashlib
import json
import sys
from pathlib import Path
os.environ['MPLCONFIGDIR'] = str(Path(__file__).resolve().parents[1]/'09_reproducibility/.matplotlib_cache')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from sklearn.metrics import precision_recall_curve

from common import ROOT, REPO, STUDY, RUN, read, write, sha, relative, cohort, job
from evaluate import NAMES


def main():
    saved = read(ROOT/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.json')
    scores = read(ROOT/'07_evaluation_results/ALL_MODEL_METRICS.json')
    bootstrap = read(ROOT/'07_evaluation_results/BOOTSTRAP_METRIC_DRAWS.json')
    paired = read(ROOT/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json')
    train = read(ROOT/'07_evaluation_results/TRAINING_SIDE_DIAGNOSTIC_METRICS.json')['scores']
    y = np.array([r['failure'] for r in saved])
    out = ROOT/'07_evaluation_results/figures';out.mkdir(exist_ok=True)
    figures = []

    def finish(filename, fig, sources):
        fig.tight_layout();fig.savefig(out/filename, dpi=170);plt.close(fig)
        figures.append({'path': relative(out/filename), 'sha256': sha(out/filename),
                        'sources': [{'path': relative(p), 'sha256': sha(p)} for p in sources]})

    source_metrics = ROOT/'07_evaluation_results/ALL_MODEL_METRICS.json'
    source_pred = ROOT/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.json'
    names = list(NAMES)
    values = [scores[n]['AP'] for n in names]
    errors = np.array([np.quantile(bootstrap[n]['AP'], [.025, .975]) for n in names])
    fig, ax = plt.subplots(figsize=(10, 5.4))
    colors = ['#4977b8', '#235345', '#727272', '#75a3dc', '#54a889', '#c3d4ed', '#a8d4bf']
    ax.bar(np.arange(7), values, color=colors)
    # Percentile intervals need not contain their point estimate; draw endpoints.
    ax.vlines(np.arange(7), errors[:, 0], errors[:, 1], color='black', lw=1.2)
    ax.scatter(np.arange(7), errors[:, 0], marker='_', color='black')
    ax.scatter(np.arange(7), errors[:, 1], marker='_', color='black')
    ax.axhline(y.mean(), color='brown', ls=':', label=f'Prevalence {y.mean():.3f}')
    ax.set_xticks(np.arange(7), [NAMES[n] for n in names], rotation=25, ha='right')
    ax.set_ylabel('Average precision');ax.set_title('Same 753 actions / 26 recordings; conditional recording-bootstrap95% intervals')
    ax.legend();finish('ALL_MODELS_AP.png', fig, [source_metrics, source_pred, ROOT/'07_evaluation_results/BOOTSTRAP_METRIC_DRAWS.json'])
    focus = ['M3_sensor', 'M4_F2_frozen', 'M5_F2_finetuned']
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar([NAMES[n] for n in focus], [scores[n]['AP'] for n in focus], color=['#727272', '#4977b8', '#54a889'])
    for k, n in enumerate(focus):ax.text(k, scores[n]['AP']+.006, f"{scores[n]['AP']:.4f}", ha='center')
    ax.set_ylabel('Average precision');ax.set_title('Primary question: sensors alone versus frozen/fine-tuned F2')
    finish('PRIMARY_SENSOR_AND_F2_COMPARISON.png', fig, [source_metrics])
    fig, ax = plt.subplots(figsize=(8, 5))
    for n, color in zip(names, colors):
        precision, recall, _ = precision_recall_curve(y, [r[n] for r in saved])
        ax.plot(recall, precision, label=f'{NAMES[n]} (AP {scores[n]["AP"]:.3f})', color=color)
    ax.axhline(y.mean(), ls=':', color='black');ax.set(xlabel='Recall', ylabel='Precision', xlim=(0, 1), ylim=(0, 1))
    ax.legend(fontsize=8);ax.set_title('Identical held-out actions; no test-derived thresholds')
    finish('PRECISION_RECALL_CURVES.png', fig, [source_pred, source_metrics])
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(3);base = ['M1_frozen100', 'M2_finetuned100', 'M3_sensor']
    ax.bar(x-.18, [train[n]['AP'] for n in base], width=.36, label='Training-side base-model holdout (920)')
    ax.bar(x+.18, [scores[n]['AP'] for n in base], width=.36, label='Outer assessment (753)')
    ax.set_xticks(x, [NAMES[n] for n in base]);ax.set_ylabel('Average precision');ax.legend(fontsize=8)
    ax.set_title('Different cohorts: descriptive behavior, not paired improvement')
    finish('TRAINING_SIDE_VS_OUTER_BRANCH_AP.png', fig, [ROOT/'07_evaluation_results/TRAINING_SIDE_DIAGNOSTIC_METRICS.json', source_metrics])
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for k, arm in enumerate(['frozen', 'finetuned']):
        prefix = 'M4_F2_frozen' if arm == 'frozen' else 'M5_F2_finetuned'
        ax.bar(k-.25, train[prefix+'_apparent_fit']['AP'], width=.25, color='#d6b46c', label='F2 apparent fitting score' if k == 0 else None)
        ax.bar(k, train[prefix+'_meta_crossfit']['AP'], width=.25, color='#8498b0', label='F2 group meta-crossfit diagnostic' if k == 0 else None)
        ax.bar(k+.25, scores[prefix]['AP'], width=.25, color='#548c75', label='Fixed outer assessment' if k == 0 else None)
    ax.set_xticks([0, 1], ['Frozen CNN + F2', 'Fine-tuned CNN + F2']);ax.set_ylabel('Average precision')
    ax.set_title('Fitting optimism and cohort transfer: distinct roles');ax.legend(fontsize=8)
    finish('F2_FITTING_AND_HELDOUT_BEHAVIOR.png', fig, [ROOT/'07_evaluation_results/TRAINING_SIDE_DIAGNOSTIC_METRICS.json', source_metrics])
    fig, ax = plt.subplots(figsize=(8, 5))
    pairs = list(paired['differences']);d = paired['differences']
    for k, name in enumerate(pairs):
        v = d[name]['AP'];ax.hlines(k, v['lower95'], v['upper95'], color='#325d83')
        ax.scatter(v['estimate'], k, color='#325d83')
    ax.axvline(0, color='black', ls=':');ax.set_yticks(range(len(pairs)), [p.split('_', 1)[1].replace('_', ' ') for p in pairs])
    ax.set_xlabel('Paired AP difference with 95% conditional recording-bootstrap interval')
    finish('PAIRED_AP_DIFFERENCES.png', fig, [ROOT/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json'])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, arm, visual, fused in zip(axes, ['Frozen', 'Fine-tuned'], ['M1_frozen100', 'M2_finetuned100'], ['M4_F2_frozen', 'M5_F2_finetuned']):
        pv = np.array([r[visual] for r in saved]);ps = np.array([r['M3_sensor'] for r in saved])
        scatter = ax.scatter(pv, ps, c=y, cmap='coolwarm', s=13, alpha=.6, vmin=0, vmax=1)
        ax.plot([0, 1], [0, 1], color='gray', ls=':');ax.set(xlabel=arm+' visual probability', ylabel='Same static sensor probability', xlim=(0, 1), ylim=(0, 1))
    fig.colorbar(scatter, ax=axes.ravel().tolist(), label='Native failure label', shrink=.8)
    fig.subplots_adjust(right=.85, wspace=.3)
    fig.savefig(out/'BRANCH_DISAGREEMENTS.png', dpi=170);plt.close(fig)
    figures.append({'path': relative(out/'BRANCH_DISAGREEMENTS.png'), 'sha256': sha(out/'BRANCH_DISAGREEMENTS.png'), 'sources': [{'path': relative(source_pred), 'sha256': sha(source_pred)}]})
    fig, ax = plt.subplots(figsize=(7, 5))
    for n in focus+['M1_frozen100', 'M2_finetuned100']:
        bins = [b for b in scores[n]['calibration_bins'] if b['count']]
        ax.plot([b['mean_probability'] for b in bins], [b['fraction_failure'] for b in bins], marker='o', ms=3, label=NAMES[n])
    ax.plot([0, 1], [0, 1], color='gray', ls=':');ax.set(xlabel='Mean predicted failure probability', ylabel='Observed failure fraction', xlim=(0, 1), ylim=(0, 1))
    ax.set_title('15 fixed bins; sparse-bin estimates are descriptive');ax.legend(fontsize=8)
    finish('CALIBRATION.png', fig, [source_metrics])
    write(ROOT/'07_evaluation_results/FIGURE_SOURCE_MANIFEST.json', figures)
    diagnostics(saved)


def diagnostics(saved):
    """Post-fit selections cover correct/incorrect disagreements; no retraining."""
    rows = cohort();by_id = {r['sample_id']: r for r in rows}
    native_metrics = read(ROOT/'07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json')
    selected = {}
    support = []
    for arm, visual, fused in [('frozen', 'M1_frozen100', 'M4_F2_frozen'),
                                ('finetuned', 'M2_finetuned100', 'M5_F2_finetuned')]:
        for label in [0, 1]:
            for direction in ['sensor_high_visual_low', 'visual_high_sensor_low']:
                pool = [r for r in saved if r['failure'] == label and
                        ((r['M3_sensor'] >= .5 and r[visual] < .5) if direction == 'sensor_high_visual_low'
                         else (r[visual] >= .5 and r['M3_sensor'] < .5))]
                rule = f'{arm};label={label};{direction};largest_absolute_probability_gap;tie_sample_id'
                support.append({'rule': rule, 'available_cases': len(pool)})
                if pool:
                    pick = sorted(pool, key=lambda r: (-abs(r[visual]-r['M3_sensor']), r['sample_id']))[0]
                    selected.setdefault(pick['sample_id'], {'row': pick, 'rules': []})['rules'].append(rule)
            # Include both fusion corrections and regressions relative to sensor.
            for change in ['fusion_corrects_sensor', 'fusion_harms_sensor']:
                pool = [r for r in saved if r['failure'] == label and
                        (((r[fused] >= .5) == label and (r['M3_sensor'] >= .5) != label)
                         if change == 'fusion_corrects_sensor' else
                         ((r[fused] >= .5) != label and (r['M3_sensor'] >= .5) == label))]
                rule = f'{arm};label={label};{change};largest_absolute_fusion_sensor_gap;tie_sample_id'
                support.append({'rule': rule, 'available_cases': len(pool)})
                if pool:
                    pick = sorted(pool, key=lambda r: (-abs(r[fused]-r['M3_sensor']), r['sample_id']))[0]
                    selected.setdefault(pick['sample_id'], {'row': pick, 'rules': []})['rules'].append(rule)
    write(ROOT/'08_visual_diagnostics/SELECTION_RULES_AND_SUPPORT.json',
          {'post_fit_only': True, 'used_for_model_selection': False, 'selection_uses_common_threshold': .5, 'rules': support,
           'unavailable_categories': [r for r in support if r['available_cases'] == 0]})
    sys.path.insert(0, str(REPO/'26.10.2026_feedback_experiments/source'))
    from isolated_decode import IsolatedDecoder
    config = read(STUDY/'config/resolved_config.json')
    decoder = IsolatedDecoder(REPO, config['weights_dir'], config['rescale_factor'], decoder_threads=1)
    image_root = ROOT/'08_visual_diagnostics/frames';image_root.mkdir(exist_ok=True)
    items = []
    for sample_id, item in sorted(selected.items()):
        native = by_id[sample_id];folder = image_root/sample_id;folder.mkdir(exist_ok=True)
        pixels = decoder(dict(native, frames32=native['frames16']))
        assert hashlib.sha256(pixels.tobytes()).hexdigest() == native['selected16_sha256']
        sheet = Image.new('RGB', (640, 4*180), 'white');draw = ImageDraw.Draw(sheet)
        frame_receipts = []
        for n, pixel in enumerate(pixels):
            im = Image.fromarray(np.moveaxis(pixel, 0, -1));path = folder/f'frame_{n:02d}.png';im.save(path)
            tile = im.resize((160, 160));x, yy = (n%4)*160, (n//4)*180
            sheet.paste(tile, (x, yy));draw.text((x+2, yy+162), f"frame {native['frames16'][n]}", fill='black')
            frame_receipts.append({'frame_index': native['frames16'][n], 'timestamp': native['timestamps16'][n],
                                   'path': relative(path), 'sha256': sha(path)})
        contact = folder/'contact_sheet.png';sheet.save(contact)
        output = {**item['row'], 'selection_rules': item['rules'], 'source_path': native['source_path'],
                  'source_recorded_sha256': native['source_recorded_sha256'], 'video_path': native['video_path'],
                  'source_original_start': native['start'], 'source_original_end': native['end'],
                  'selected16_original_pixel_sha256': native['selected16_sha256'], 'frame_receipts': frame_receipts,
                  'contact_sheet': relative(contact), 'contact_sheet_sha256': sha(contact),
                  'interpretation': 'Native label is the reference; probabilities and images are descriptive post-fit diagnostics, not evidence of a mechanical cause.'}
        items.append(output)
    write(ROOT/'08_visual_diagnostics/HELDOUT_DISAGREEMENT_EXAMPLES.json', items)
    html = ['<!doctype html><meta charset="utf-8"><style>body{font:16px system-ui;margin:2rem;max-width:1200px}img{max-width:640px}td,th{padding:.4rem;border:1px solid #ddd}table{border-collapse:collapse}</style>',
            '<h1>Fixed-model held-out disagreements</h1><p>Post-fit examples include correct and incorrect predictions under predefined rules. Unavailable categories are reported separately. None was used for fitting, calibration or model choice. Native labels are shown.</p>']
    for r in items:
        html += [f"<h2>{r['sample_id']} — native failure={r['failure']}</h2>",
                 f"<p>Recording {r['recording_id']}; segment {r['segment_id']}; action {r['action']}; source interval {r['start']}–{r['end']}.</p>",
                 '<table><tr><th>Model</th><th>Failure probability</th><th>Prediction at0.5</th><th>Correct at0.5?</th><th>Original native threshold</th><th>Native prediction</th><th>Native correct?</th></tr>']
        for name in NAMES:
            h = int(r[name] >= .5)
            threshold = native_metrics[name]['threshold'];hn = int(r[name] >= threshold)
            html.append(f'<tr><td>{NAMES[name]}</td><td>{r[name]:.6f}</td><td>{h}</td><td>{h == r["failure"]}</td><td>{threshold:.2f}</td><td>{hn}</td><td>{hn == r["failure"]}</td></tr>')
        html += ['</table>', '<p>Selection: '+'; '.join(r['selection_rules'])+'</p>',
                 f'<img src="frames/{r["sample_id"]}/contact_sheet.png">']
    (ROOT/'08_visual_diagnostics/HELDOUT_DISAGREEMENTS.html').write_text('\n'.join(html))
    print('PLOTS_AND_DIAGNOSTICS_COMPLETE', len(items), 'real examples', flush=True)


if __name__ == '__main__':main()
