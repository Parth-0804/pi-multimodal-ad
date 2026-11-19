"""Handover-specific original aligned-wrench observation-window loading."""
import json
import numpy as np


def source_key(row):return row.sensor_file


def load_source(row,channels):
    x=np.load(row.sensor_file,allow_pickle=False)
    if x.ndim!=2 or x.shape[1]!=len(channels):raise ValueError('Invalid native common wrist wrench dimensions')
    return x


def interval_values(source,row):
    if 'sensor_row_indices_json' in row.index and row.sensor_row_indices_json:
        return source[np.array(json.loads(row.sensor_row_indices_json),int)]
    return source
