"""Survivor diagnosis (Searched Areas item ii, 9 Oct): where the parents carrying the two-burst arms sit against the
prior support of the descent latents. Run from engine/ on the reference-289 sweep; writes /tmp/survivors.json."""
import json, pathlib, numpy as np
from displacement_hist import option_posteriors
B=1394237969.416
L=["takeover_altitude_ft","latent:max_descent_rate_fpm","latent:max_mach","latent:impact_bank_deg","latent:ld_max_clean","latent:windmilling_per_engine","latent:time_descending_s","latent:spiral_doubling_s","latent:profile_shape","latent:control_realised","latent:onset_mechanism","latent:max_altitude_ft","latent:impact_vertical_speed_mps"]
arms=["both_no-offset__other","both_startup-offset__other","both_inflated__other","r1200_no-offset__other"]
acc={a:{k:[] for k in L+["loss","fo","wt"]} for a in arms}; prior={k:[] for k in L+["loss","fo"]}
for s in range(1,5):
    run=pathlib.Path(f"runs/eof-289-full-s{s}"); sd=run/f"bto-bfo/seed-{s}"
    meta=json.loads((run/"run.json").read_text()); cols={c:i for i,c in enumerate(meta["impact_columns"])}
    X=np.load(sd/"impacts.npy",mmap_mode="r"); g=lambda k: np.array(X[:,cols[k]],float)
    V={k:g(k) for k in L}; V["loss"]=g("latent:onset_unix_s")+g("latent:free_dynamics_started_s")-B; V["fo"]=g("latent:realised_flameout_unix_s")-B
    w=g("weight"); w=w/w.sum(); pick=np.random.default_rng(s).choice(len(w),20000,p=w)
    for k in prior: prior[k].append(V[k][pick])
    for k,p,c in option_posteriors(run,sd):
        if k in arms:
            top=np.argsort(p)[::-1][:400]
            for kk in V: acc[k][kk].append(V[kk][top])
            acc[k]["wt"].append(p[top]/4)
res={}
for a in arms:
    wt=np.concatenate(acc[a]["wt"]); wt=wt/wt.sum(); res[a]={}
    for k in L+["loss","fo"]:
        x=np.concatenate(acc[a][k]); pr=np.concatenate(prior[k]); f=np.isfinite(x)&(wt>0); pf=pr[np.isfinite(pr)]
        if f.sum()==0 or len(pf)==0: continue
        o=np.argsort(x[f]); cw=np.cumsum(wt[f][o])/wt[f].sum(); qs=[x[f][o][min(np.searchsorted(cw,u),f.sum()-1)] for u in (0.05,0.5,0.95)]
        res[a][k]=dict(post_q05_50_95=[float(v) for v in qs], post_finite_share=float(wt[f].sum()), prior_min=float(pf.min()), prior_q01=float(np.quantile(pf,0.01)), prior_q50=float(np.median(pf)), prior_q99=float(np.quantile(pf,0.99)), prior_max=float(pf.max()))
json.dump(res,open("/tmp/survivors.json","w"),indent=1)
for k in L+["loss","fo"]:
    r=res["both_no-offset__other"].get(k); r2=res["both_startup-offset__other"].get(k)
    if r: print(f"{k[7:] if k.startswith('latent') else k:28s} prior[min q01 q50 q99 max] {r['prior_min']:8.1f} {r['prior_q01']:8.1f} {r['prior_q50']:8.1f} {r['prior_q99']:8.1f} {r['prior_max']:8.1f} | H2 {np.round(r['post_q05_50_95'],1)} | H1 {np.round(r2['post_q05_50_95'],1) if r2 else '-'}")
print("---- edge shares (posterior weight, top-400 rows per seed)")
for a in arms:
    wt=np.concatenate(acc[a]["wt"]); wt=wt/wt.sum()
    ta=np.concatenate(acc[a]["takeover_altitude_ft"]); mm=np.concatenate(acc[a]["latent:max_mach"]); dr=np.concatenate(acc[a]["latent:max_descent_rate_fpm"]); bk=np.concatenate(acc[a]["latent:impact_bank_deg"])
    pta=np.concatenate(prior["takeover_altitude_ft"])
    print(f"{a:28s} alt<=25000 post {wt[ta<=25000.5].sum():.3f} prior {np.mean(pta<=25000.5):.3f} | alt>=43000 post {wt[ta>=42999.5].sum():.3f} prior {np.mean(pta>=42999.5):.3f} | mach>=1.05 {wt[mm>=1.05].sum():.3f} | rate>=60k {wt[dr>=60000].sum():.3f} | bank>=89.9 {wt[bk>=89.9].sum():.3f}")
