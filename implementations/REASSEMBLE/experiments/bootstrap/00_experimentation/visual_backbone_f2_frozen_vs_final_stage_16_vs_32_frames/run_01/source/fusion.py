"""F2 stacker and calibrated statistics branch. Labels are fit-local arguments."""
import warnings,numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from common import signature
def sigmoid(x):return expit(x)
def standardizer(x):
 mean=np.nanmean(x,axis=0).astype('float32');std=np.nanstd(x,axis=0).astype('float32')
 mean=np.nan_to_num(mean,nan=0);std=np.where(np.isfinite(std)&(std>1e-6),std,1)
 return mean.astype('float32'),std.astype('float32')
def transform(x,mean,std):return np.nan_to_num((x-mean)/std,nan=0,posinf=0,neginf=0).astype('float32')
def fit_logistic(x,y,balanced=False):
 assert len(x)==len(y) and set(np.unique(y))=={0,1}
 with warnings.catch_warnings():
  warnings.simplefilter('error',ConvergenceWarning)
  m=LogisticRegression(C=1.,class_weight='balanced' if balanced else None,max_iter=2000,random_state=42).fit(x,y)
 return {'coefficient':m.coef_.reshape(-1).tolist(),'intercept':float(m.intercept_[0]),'iterations':m.n_iter_.tolist(),'C':1.,'balanced':balanced}
def linear(x,m):return np.asarray(x)@np.asarray(m['coefficient'])+m['intercept']
def calibrate(raw,y):return fit_logistic(np.asarray(raw).reshape(-1,1),y,False)
def calibrated(raw,cal):return sigmoid(linear(np.asarray(raw).reshape(-1,1),cal))
def sensor_fit(xG,yG,xC,yC):
 mean,std=standardizer(xG);raw=fit_logistic(transform(xG,mean,std),yG,True);cal=calibrate(linear(transform(xC,mean,std),raw),yC)
 return {'mean':mean.tolist(),'std':std.tolist(),'raw':raw,'calibrator':cal}
def sensor_predict(x,model):
 raw=linear(transform(x,np.asarray(model['mean'],dtype='float32'),np.asarray(model['std'],dtype='float32')),model['raw'])
 return raw,calibrated(raw,model['calibrator'])
def stacker(p,y):
 assert np.asarray(p).ndim==2 and np.asarray(p).shape[1]==2
 assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
 return fit_logistic(p,y,False)
def fused(p,model):return sigmoid(linear(p,model))
