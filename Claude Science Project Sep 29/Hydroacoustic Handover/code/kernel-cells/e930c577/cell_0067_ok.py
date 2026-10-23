
import pandas as pd, numpy as np
from scipy import signal
d="hrepo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces/kadri-2024-figure9-panel-c-H01W.csv"
x=pd.read_csv(d).sort_values('plotted_time_s'); tg=np.arange(0,600,1/40); p=np.interp(tg,x.plotted_time_s,x.pressure_pa)
sos=signal.butter(4,[2,19.5],btype='band',fs=40,output='sos'); pf=signal.sosfiltfilt(sos,p); env=np.abs(signal.hilbert(pf))
w=int(6*40); mx=np.array([env[i:i+w].max() for i in range(0,len(env)-w,w)])
t0=47*60; iT=int((52*60+3-t0)*40); iC=int((54*60+30-t0)*40)
print("rms all",pf.std().round(3),"env median",np.median(env).round(3),"6s-window max median",np.median(mx).round(3),"q90",np.quantile(mx,0.9).round(3),"n",len(mx))
print("T window max",env[iT-120:iT+120].max().round(3),"C",env[iC-120:iC+120].max().round(3))
# excess amplitude over noise (in quadrature with median window max)
for nm,v in (("T",env[iT-120:iT+120].max()),("C",env[iC-120:iC+120].max())):
    print(nm, "excess quad over median window max", np.sqrt(max(v**2-np.median(mx)**2,0)).round(3), "over rms", np.sqrt(max(v**2-(2*pf.std())**2,0)).round(3))
