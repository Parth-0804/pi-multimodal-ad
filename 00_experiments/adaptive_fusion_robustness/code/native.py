"""Strict native scalar and timestamp validation, without process side effects."""
import numpy as np
def success_value(x):
 a=np.asarray(x)
 if a.shape!=():raise ValueError('success must be scalar')
 v=a.item()
 if a.dtype.kind=='b':return int(v)
 if a.dtype.kind in 'iu' and v in (0,1):return int(v)
 raise ValueError('unsupported success datatype/value')
def times(a):
 a=np.asarray(a,dtype=np.float64)
 if a.ndim==2:
  if not np.allclose(a,a[:,:1],atol=1e-9,rtol=0):raise ValueError('per-channel clock disagreement')
  a=a[:,0]
 if a.ndim!=1 or not np.isfinite(a).all() or np.any(np.diff(a)<=0):raise ValueError('invalid timestamps')
 return a
