cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
w=open("worker.py").read()
w=w.replace('''    tau90 = np.asarray(z["tau90_s"], float)
    t = g("unix_s"); lat = g("latitude_deg"); lon = g("longitude_deg"); fam = g("family4_code")
    E = g("latent:impact_energy_transferred_j"); Efb = 0.5 * g("mass_kg") * (g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    fb = ~np.isfinite(E) & np.isfinite(Efb); E = np.where(fb, Efb, E)''','''    tau90 = np.asarray(z["tau90_s"], float)
    t = g("unix_s"); lat = g("latitude_deg"); lon = g("longitude_deg"); fam = g("family4_code")
    # E = contact kinetic energy: the tau90 sidecar's energy_transferred_j (impacts32's latent:impact_energy_transferred_j is NaN in
    # run J; amendment A1, plumbing only), then the impacts32 column, then 0.5 m v^2 (counted)
    E = np.asarray(z["energy_transferred_j"], float); E2 = g("latent:impact_energy_transferred_j"); E = np.where(np.isfinite(E), E, E2)
    Efb = 0.5 * g("mass_kg") * (g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    fb = ~np.isfinite(E) & np.isfinite(Efb); E = np.where(fb, Efb, E)''')
open("worker.py","w").write(w)
p=open("prereg.py").read()
p=p.replace("AMENDMENTS (disclosed below this line as they occur; none at commit).\n",
"AMENDMENTS (disclosed below this line as they occur; none at commit).\nA1 (22 Oct, before any seed was run; plumbing only): E is read from the tau90 sidecar's energy_transferred_j (the impacts32 column\n   latent:impact_energy_transferred_j is NaN in run J), then that column, then 0.5 m v^2; CHUNK_ROWS 1 M -> 500 k (memory). No value change.\n")
open("prereg.py","w").write(p); print("ok")
EOF
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python - <<'EOF' 2>&1 | grep -v Warn
import time, numpy as np, sys
sys.path.insert(0,'.'); sys.path.insert(0,'..')
import prereg as R, run_j_windows as W
from common import Machinery
M=Machinery()
sd=R.RUN_J/"run-j-waypoints"/"seed-1"; g,meta,n=W.load_seed(sd)
idx=np.arange(0,n,n//20000)[:20000]
z=np.load(sd/"tau90_v1.npz"); t=g("unix_s")[idx]; lat=g("latitude_deg")[idx]; lon=g("longitude_deg")[idx]; E=z["energy_transferred_j"][idx].astype(float); tau=z["tau90_s"][idx].astype(float)
ok=np.isfinite(t)&np.isfinite(lat)&np.isfinite(E)&np.isfinite(tau)&(E>0)&(tau>0); print("ok share", ok.mean(), "E q GJ", np.round(np.quantile(E[ok],[.05,.5,.95])/1e9,2), "tau q", np.round(np.quantile(tau[ok],[.05,.5,.95]),2))
idx2=np.where(ok)[0]
t1=time.time(); PP=M.prep(t[idx2],lat[idx2],lon[idx2],E[idx2],tau[idx2]); print("prep 20k rows", round(time.time()-t1,2),"s")
print("scored share per rx", {rx: round(float(PP["sc"][rx].mean()),3) for rx in R.RECEIVERS})
print("base median per rx (dB re bg median at eta=1)", {rx: round(float(np.nanmedian(PP["base"][rx])),1) for rx in R.RECEIVERS})
Lcal=np.random.default_rng(1).normal(0,10,len(idx2))
for a in R.ALPHAS:
    t1=time.time(); lnL,lnP,nsc=M.lnL_grid(PP,Lcal,a,R.RECEIVERS_GATED); li,lpi,_=M.lnL_grid(PP,Lcal,a,R.RECEIVERS_PROXY)
    lm=M.marg(lnL); print(f"alpha {a}: {time.time()-t1:.2f}s  lnL_marg q", np.round(np.quantile(lm,[0,.01,.5,.99,1]),3), " fixed 2.1e-4 q", np.round(np.quantile(M.fixed(lnL,'eta2.1e-4'),[0,.5,1]),3), " ims marg q", np.round(np.quantile(M.marg(lnL+li),[0,.5,1]),3))
    k=np.argmin(abs(M.eta_eval-1e-2)); print("   Pnd(1e-2) mean", round(float(np.exp(lnP[:,k]).mean()),3), " at anchor", round(float(np.exp(lnP[:,M.n_grid+1]).mean()),3), " share any scored", round(float((nsc>0).mean()),3))
EOF