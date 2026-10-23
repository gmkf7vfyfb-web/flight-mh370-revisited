W=$PWD; cd work/standin-scripts; PYTHONPATH=. OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 W=$W python - <<'E' 2>&1 | grep -v Warning | grep -v "lev = \|self.spl"
import os, time, numpy as np
W=os.environ["W"]; import lhyd
M=W+"/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
K=W+"/repo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-table1-transients.csv"
t=time.time(); m=lhyd.Model(M, W+"/work/imos_events_searched.json", K); print("init", round(time.time()-t,1), "teff", m.teff, "xs", m.xs)
X=np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/next-free/seed-1/impacts.npy", mmap_mode="r")
idx=np.arange(0, 200000, 10); A=np.asarray(X[idx][:, [0,5,6,7,11,13,14]], float)
w,t_,la,lo,fpa,KE,VKE=A.T
B=m.B; rng=np.random.default_rng(1); tau=10**rng.uniform(np.log10(.05),1,3000)
err=max(np.max(np.abs(np.interp(np.log10(tau),np.log10(lhyd.TAU_GRID),m.Sb[fc])-B.band_fraction(fc,1/tau,2))/np.maximum(B.band_fraction(fc,1/tau,2),1e-30)) for fc in m.F.BANDS)
print("band_fraction max rel err", err)
for sc in "ABC":
    t=time.time(); o=m.station_terms(t_, la, lo, KE, np.random.default_rng(7), sc)
    print(sc, round(time.time()-t,2), {k: (round(float(np.mean(v)),4), round(float(np.min(v)),3), round(float(np.max(v)),3)) for k,v in o.items()})
p=m.predict(t_,la,lo,KE,np.random.default_rng(7))
print({k:(round(float(np.average(v['pd'],weights=w)),3) if 'pd' in v else None) for k,v in p.items()})
print("lat range", la.min(), la.max(), "frac clamped", np.mean((la< m.xs.min())|(la>m.xs.max())))
E