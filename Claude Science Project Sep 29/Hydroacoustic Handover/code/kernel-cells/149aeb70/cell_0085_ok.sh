cd /Users/pete/Downloads/mh370-exchange/end-of-flight && python3 - <<'PY'
import numpy as np, json
T=19*60+37
for run in ["run-i","run-i-dive"]:
    cols=json.load(open(f"{run}/next-i-free/seed-1/run.json"))["impact_columns"]; ix={c:i for i,c in enumerate(cols)}
    a=np.load(f"{run}/next-i-free/seed-1/impacts32.npy",mmap_mode="r")
    n=a.shape[0]; g=lambda c: np.asarray(a[:,ix[c]],dtype=np.float64)
    w=g("weight"); w/=w.sum()
    pe,pd_=g("latent:pushover_eligible"),g("latent:pushover_drawn")
    qe,qd=g("latent:pitchdown_eligible"),g("latent:pitchdown_drawn")
    fpa=g("flight_path_angle_deg"); t=g("t_impact_s")
    tau=np.load(f"{run}/next-i-free/seed-1/tau90_v1.npz")["tau90_s"].astype(np.float64)
    pk=np.load(f"{run}/next-i-free/seed-1/tau90_v1.npz")["peak_rate_w"].astype(np.float64)
    def wm(mask, v):
        ww=w[mask]; 
        if ww.sum()<=0: return float('nan')
        o=np.argsort(v[mask]); c=np.cumsum(ww[o])/ww.sum()
        return float(v[mask][o][np.searchsorted(c,0.5)])
    print(f"=== {run}  (seed-1 free, n={n})")
    print(f"  P(pushover eligible)={float((w*pe).sum()):.4f}  P(pushover drawn)={float((w*pd_).sum()):.4f}"
          f"   P(pitchdown eligible)={float((w*qe).sum()):.4f}  P(pitchdown drawn)={float((w*qd).sum()):.4f}")
    for nm,m in [("pushover drawn",pd_>0.5),("pitchdown drawn",qd>0.5),("neither",(pd_<0.5)&(qd<0.5))]:
        if m.sum()==0: print(f"  {nm:16s} none"); continue
        wm_=w[m].sum()
        print(f"  {nm:16s} weight={wm_:.4f}  med fpa={wm(m,fpa):6.2f}  frac fpa>45={float((w[m]*(fpa[m]>45)).sum()/wm_):.3f}"
              f"  med tau90={wm(m,tau):7.3f}  frac impact<3min={float((w[m]*((t[m]-T)<180)).sum()/wm_):.3f}")
    print(f"  overall: frac fpa 10-45 deg = {float((w*((fpa>=10)&(fpa<45))).sum()):.4f}   frac fpa>45 = {float((w*(fpa>45)).sum()):.4f}")
PY