"""Milling-specific, read-only native MTC interval loading."""
import numpy as np
import pandas as pd


def source_key(row):return row.mtc_file


def load_source(row,channels):
    table=pd.read_csv(row.mtc_file,usecols=['time',*channels])
    t=table.time.to_numpy(float);x=table[channels].to_numpy(float)
    if not np.isfinite(t).all() or np.any(np.diff(t)<=0):raise ValueError('Invalid native MTC clock')
    return t,x


def interval_values(source,row):
    t,x=source;a,b=np.searchsorted(t,[row.start_s,row.end_s],side='left')
    return x[a:b]
