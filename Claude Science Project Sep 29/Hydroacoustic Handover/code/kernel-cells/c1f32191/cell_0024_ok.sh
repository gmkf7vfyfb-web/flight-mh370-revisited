cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python - <<'EOF' 2>&1 | grep -v Warning
import time, numpy as np, sys
sys.path.insert(0,'.'); sys.path.insert(0,'..')
import prereg as R, run_j_windows as W
from common import Machinery
t0=time.time(); M=Machinery(); print("init", round(time.time()-t0,1),"s")
print("pd_missing", M.pd_missing)
print("windows", {rx: len(v) for rx,v in M.windows.items()})
print("cands", {f"{rx}|{a}": len(M.cands[(rx,a)]) for rx in R.RECEIVERS for a in R.ALPHAS})
print("bmed", {k: round(v,1) for k,v in M.bmed.items()}); print("teff", {k: np.round(v,2).tolist() for k,v in M.teff.items()})
sd=R.RUN_J/"run-j-waypoints"/"seed-1"; g,meta,n=W.load_seed(sd); print("n",n)
idx=np.arange(0,n,n//2000)[:2000]
t=g("unix_s")[idx]; lat=g("latitude_deg")[idx]; lon=g("longitude_deg")[idx]; E=g("latent:impact_energy_transferred_j")[idx]
tau=np.load(sd/"tau90_v1.npz")["tau90_s"][idx].astype(float)
ok=np.isfinite(t)&np.isfinite(lat)&np.isfinite(E)&np.isfinite(tau)&(E>0)&(tau>0); print("ok share", ok.mean(), "E q", np.nanquantile(E[ok],[.05,.5,.95])/1e9, "tau q", np.quantile(tau[ok],[.05,.5,.95]))
idx2=np.where(ok)[0]
t1=time.time(); PP=M.prep(t[idx2],lat[idx2],lon[idx2],E[idx2],tau[idx2]); print("prep", round(time.time()-t1,2))
print("scored share per rx", {rx: round(PP["sc"][rx].mean(),3) for rx in R.RECEIVERS})
print("base median per rx (dB re bg median at eta=1)", {rx: round(float(np.nanmedian(PP["base"][rx])),1) for rx in R.RECEIVERS})
Lcal=np.zeros(len(idx2))
for a in R.ALPHAS:
    t1=time.time(); lnL,lnP,nsc=M.lnL_grid(PP,Lcal,a,R.RECEIVERS_GATED); li,lpi,_=M.lnL_grid(PP,Lcal,a,R.RECEIVERS_PROXY)
    lm=M.marg(lnL); print(f"alpha {a}: {time.time()-t1:.2f}s  lnL_marg q", np.round(np.quantile(lm,[0,.01,.5,.99,1]),3), " fixed 2.1e-4 q", np.round(np.quantile(M.fixed(lnL,'eta2.1e-4'),[0,.5,1]),3), " ims marg q", np.round(np.quantile(M.marg(lnL+li),[0,.5,1]),3))
    k=np.argmin(abs(M.eta_eval-1e-2)); print("   Pnd(1e-2) mean", round(float(np.exp(lnP[:,k]).mean()),3), " at anchor", round(float(np.exp(lnP[:,M.n_grid+1]).mean()),3))
EOF