"""Consensus of calibration audio templates, allowing partial recording overlap."""
import numpy as np
from scipy import signal


def correlations(video_features, reference_features, window_samples=800, threshold=.75):
    x,y=video_features[0],reference_features[0];n,m=len(x),len(y)
    lags=signal.correlation_lags(n,m);votes=np.zeros(len(lags));strength=np.zeros(len(lags))
    if n<window_samples or m<window_samples:
        return lags,np.full(len(lags),-np.inf)
    sums=signal.correlate(x,np.ones(window_samples),mode='valid',method='fft')
    squares=signal.correlate(x*x,np.ones(window_samples),mode='valid',method='fft')
    # Only even, nonoverlapping reference blocks participate. Odd blocks remain withheld.
    for a in range(0,m-window_samples+1,2*window_samples):
        template=y[a:a+window_samples]-y[a:a+window_samples].mean()
        variance=float(np.dot(template,template))
        if variance<1e-12:continue
        cross=signal.correlate(x,template,mode='valid',method='fft')
        denom=np.sqrt(np.maximum(squares-sums*sums/window_samples,0)*variance)
        coefficient=cross/np.maximum(denom,1e-12)
        indices=np.arange(len(coefficient))-a+m-1;strong=coefficient>=threshold
        votes[indices]+=strong;strength[indices]+=np.where(strong,coefficient,0)
    # First maximize agreeing blocks; use summed Pearson strength only to break ties.
    return lags,votes+.001*strength
