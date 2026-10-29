"""Plot existing numerical payloads only; no frame extraction or model fitting."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent


if __name__ == '__main__':
    records = json.loads((RUN / 'provenance/SENSOR_TABLE_INVENTORY.json').read_text())
    paths = {int(row['path'].split('episode_')[1].split('.')[0]): SOURCE / row['local_path'] for row in records}
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for ax, eid, channel in zip(axes.flat, [775, 2791, 3034, 5080], [0, 0, 4, 2]):
        data = pd.read_parquet(paths[eid])
        time = data.timestamp.to_numpy()
        pos = np.stack(data['observation.state']).astype(float)
        vel = np.stack(data['observation.velocity']).astype(float)
        if eid in [775, 2791]:
            derivative = np.gradient(pos[:, channel]) * 25
            measured = vel[:, channel]
            for array, name in [(derivative, 'Finite difference of position'), (measured, 'Published observation.velocity')]:
                scaled = (array - array.mean()) / max(array.std(), 1e-12)
                ax.plot(time, scaled, label=name, linewidth=1)
            correlation = np.corrcoef(derivative, measured)[0, 1]
            ax.set_title(f'Episode {eid}, channel {channel}; signed correlation {correlation:.3f}')
            ax.set_ylabel('Within-trace z score; no physical unit equivalence assumed')
        else:
            array = pos[:, channel] if eid == 3034 else vel[:, channel]
            ax.plot(time, array, linewidth=1)
            ax.set_title(f'Episode {eid}, channel {channel}; gross native-value spike')
            ax.set_ylabel('Position (native units)' if eid == 3034 else 'Velocity (native units)')
        ax.set_xlabel('Converted episode time (seconds)')
        ax.grid(alpha=.25)
        if eid in [775, 2791]: ax.legend(fontsize=8)
    fig.suptitle('Input-only sensor QC diagnostics — no outcome labels used or corrected')
    fig.tight_layout()
    dest = RUN / '03_SENSOR_QUALITY/SENSOR_ANOMALY_DIAGNOSTICS.png'
    assert not dest.exists()
    fig.savefig(dest, dpi=140)
    plt.close(fig)
    print(dest)
