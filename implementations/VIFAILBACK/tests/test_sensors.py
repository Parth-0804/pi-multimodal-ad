"""Preserve the historical statistic contract using tiny synthetic observations."""
import numpy as np
from vifailback.sensors import statistics, quality, CHANNELS, FEATURES
from vifailback.reference import primitives


def test_statistics_are_exact_original_function_and_named_in_original_order():
    time=np.linspace(0,1,32,dtype='float32')
    values=np.stack([time*(i+1) for i in range(28)],axis=1)
    actual=statistics(values)
    assert np.array_equal(actual,primitives()['statistics'](values))
    assert len(CHANNELS)==28 and len(FEATURES)==280
    assert FEATURES[0].endswith('.mean') and FEATURES[28].endswith('.std')
    assert np.isclose(actual[-1],28,atol=1e-5)


def test_quality_distinguishes_placeholder_constancy_and_missingness():
    base=np.zeros((20,28),dtype='float32')
    q=quality(base)
    assert q[0]==1 and q[2]==1
    base[:10,:4]=np.nan
    missing=quality(base)
    assert missing[0]<q[0] and missing[1]==1
