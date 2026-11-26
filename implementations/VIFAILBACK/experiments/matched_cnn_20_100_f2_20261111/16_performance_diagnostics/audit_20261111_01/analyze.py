"""Summarize OS counters; does not import the training stack or load data/models."""
import hashlib
import json
import os
from pathlib import Path
import statistics as st

OUT = Path(__file__).resolve().parent
STUDY = OUT.parents[1]
REPO = STUDY.parents[2]
GIB = 1024 ** 3


def stats(values):
    values = sorted(values)
    return dict(mean=st.mean(values), min=values[0], max=values[-1],
                median=st.median(values), p95=values[round(.95 * (len(values) - 1))])


def busy(core):
    return 100 - core['idle'] - core.get('iowait', 0)


def delta_process(first, last, seconds):
    a, b = first['cpu_times'], last['cpu_times']
    own = sum(b[k]-a[k] for k in ['user', 'system'])
    children = sum(b.get(k, 0)-a.get(k, 0) for k in ['children_user', 'children_system'])
    return dict(name=last['name'], pid=last['pid'], seconds=seconds,
                own_CPU_percent_one_core_100=100*own/seconds,
                reaped_children_CPU_percent_one_core_100=100*children/seconds,
                rss_GiB=last['memory']['rss']/GIB, threads=last['threads'],
                affinity=last['affinity'], read_bytes=last['io']['read_bytes']-first['io']['read_bytes'],
                write_bytes=last['io']['write_bytes']-first['io']['write_bytes'])


def pressure_total(text, kind):
    line = next(x for x in text.splitlines() if x.startswith(kind+' '))
    return int(line.split('total=')[1])


def main():
    assert (OUT / 'end.json').exists(), 'Wait for collection completion'
    rows = [json.loads(x) for x in (OUT / 'samples.jsonl').read_text().splitlines()]
    a, b = rows[0], rows[-1]
    seconds = b['monotonic'] - a['monotonic']
    intervals = rows[1:]
    gpus = [r['gpu'][0] for r in rows]
    util = [float(x['utilization.gpu']) for x in gpus]
    runs, run = [], 0
    for v in util + [101]:
        if v == 0:
            run += 1
        elif run:
            runs.append(run*2)
            run = 0
    first = {p['pid']: p for p in a['processes']}
    last = {p['pid']: p for p in b['processes']}
    stable = [delta_process(first[p], last[p], seconds) for p in first.keys() & last.keys()]
    ff = [p for r in rows for p in r['processes'] if p['name'].startswith('ffmpeg')]
    io = {}
    for device in ['sda']:
        da, db = a['disk'][device], b['disk'][device]
        dd = {k: db[k]-da[k] for k in da}
        io[device] = dict(delta=dd, read_MiB_per_s=dd['read_bytes']/1024**2/seconds,
                         write_MiB_per_s=dd['write_bytes']/1024**2/seconds,
                         busy_percent=dd['busy_time']/1000/seconds*100,
                         read_await_ms=dd['read_time']/dd['read_count'] if dd['read_count'] else None,
                         write_await_ms=dd['write_time']/dd['write_count'] if dd['write_count'] else None)
    hist = json.loads((OUT / 'history_end.json').read_text())
    timings = [json.loads((STUDY / '06_full100/seed42/outer0_inner0' / f'TIMING_EPOCH_{e:03d}.json').read_text())
               for e in range(1, len(hist)+1)]
    epoch10 = json.loads((STUDY / '06_full100/seed42/outer0_inner0/GPU_TELEMETRY_EPOCH_010.json').read_text())
    result = dict(window=dict(start=a['utc'], end=b['utc'], seconds=seconds, samples=len(rows),
                             interval_seconds=2, start_batch=a['batch'], end_batch=b['batch']),
        gpu=dict(kernel_busy_percent=stats(util), zero_samples=sum(v==0 for v in util),
                 zero_fraction=sum(v==0 for v in util)/len(util),
                 at_least_95_percent_fraction=sum(v>=95 for v in util)/len(util),
                 sampled_zero_run_seconds=runs,
                 power_W=stats([float(g['power.draw']) for g in gpus]),
                 power_limit_W=sorted(set(float(g['power.limit']) for g in gpus)),
                 driver_used_MiB=stats([float(g['memory.used']) for g in gpus]),
                 driver_free_MiB=stats([float(g['memory.free']) for g in gpus]),
                 temperature_C=stats([float(g['temperature.gpu']) for g in gpus]),
                 sm_clock_MHz=stats([float(g['clocks.sm']) for g in gpus]),
                 epoch10_training_utilization=stats([v['GPU_utilization_percent'] for v in epoch10])),
        cpu=dict(host_busy_percent=stats([st.mean(busy(c) for c in r['cpu_per_core']) for r in intervals]),
                 per_core_mean_busy_percent=[st.mean(busy(r['cpu_per_core'][i]) for r in intervals) for i in range(len(a['cpu_per_core']))],
                 host_iowait_percent=stats([st.mean(c.get('iowait',0) for c in r['cpu_per_core']) for r in intervals]),
                 host_steal_percent=stats([st.mean(c.get('steal',0) for c in r['cpu_per_core']) for r in intervals]),
                 stable_processes=stable,
                 ffmpeg_unique_pids=len(set(p['pid'] for p in ff)),
                 ffmpeg_threads=sorted(set(p['threads'] for p in ff)),
                 ffmpeg_concurrent_counts=stats([sum(p['name'].startswith('ffmpeg') for p in r['processes']) for r in rows]),
                 worker_counts=sorted(set(sum(p['name']=='pt_data_worker' for p in r['processes']) for r in rows)),
                 collector=delta_process(a['collector'], b['collector'], seconds)),
        memory=dict(total_GiB=a['memory']['total']/GIB,
                    available_GiB=stats([r['memory']['available']/GIB for r in rows]),
                    used_GiB=stats([r['memory']['used']/GIB for r in rows]),
                    swap_used_bytes=stats([r['swap']['used'] for r in rows]),
                    swap_in_delta=b['swap']['sin']-a['swap']['sin'], swap_out_delta=b['swap']['sout']-a['swap']['sout']),
        pressure={name: {kind+'_stall_percent': (pressure_total(b['pressure'][name],kind)-pressure_total(a['pressure'][name],kind))/1e6/seconds*100
                         for kind in ['some','full']} for name in ['cpu','memory','io']},
        disk=io, free_disk_GiB=stats([r['free_bytes']/GIB for r in rows]),
        epochs=dict(count=len(hist), train_seconds=stats([r['training_seconds'] for r in hist]),
                    validation_seconds=stats([r['validation_seconds'] for r in hist]),
                    combined_seconds=stats([r['epoch_seconds'] for r in hist]),
                    checkpoint_seconds=stats([r['checkpoint_seconds'] for r in timings]),
                    validation_fraction=sum(r['validation_seconds'] for r in hist)/sum(r['epoch_seconds'] for r in hist),
                    peak_torch_allocated_GiB=max(r['peak_GPU_bytes'] for r in hist)/GIB),
        warnings=['Two-second GPU samples are device kernel-busy estimates, not SM occupancy or exact batch waits.',
                  'CPU percent is host-average across16CPUs; process CPU percent uses100%=onecore.',
                  'Exited FFmpeg CPU is accounted through worker reaped-children counters; transient process counts can be missed.',
                  'Summed RSS double-counts shared mappings; memory available is the host-capacity measure.',
                  'Live PyTorch allocated/reserved memory and per-loader waiting are not instrumented.',
                  'Six-minute window covers training only; validation overhead uses completed epoch receipts.'])
    with (OUT / 'summary.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/vifailback_performance_mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    x = [(r['monotonic']-a['monotonic'])/60 for r in rows]
    fig, ax = plt.subplots(4, 1, figsize=(11, 9), sharex=True, constrained_layout=True)
    ax[0].plot(x, util, linewidth=1);ax[0].set_ylabel('GPU kernel-busy (%)');ax[0].set_ylim(-3,103)
    ax[1].plot(x, [float(g['power.draw']) for g in gpus], color='#d97706');ax[1].set_ylabel('GPU power (W)')
    ax[2].plot(x[1:], [st.mean(busy(c) for c in r['cpu_per_core']) for r in intervals], color='#147d64')
    ax[2].set_ylabel('Host CPU busy (%)')
    ax[3].step(x, [sum(p['name'].startswith('ffmpeg') for p in r['processes']) for r in rows], where='mid', color='#7c3aed')
    ax[3].set_ylabel('FFmpeg processes');ax[3].set_yticks([0,1,2]);ax[3].set_xlabel('Minutes from '+a['utc'])
    for panel in ax:panel.grid(alpha=.25)
    fig.suptitle('Full100 read-only live audit — two-second samples; no per-batch attribution')
    fig.savefig(OUT/'resource_timeline.png', dpi=150)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
