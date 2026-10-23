
print(C[C.key.duplicated(keep=False)][["key","p","p_B","source"]])
C=C.drop_duplicates("key").reset_index(drop=True)
ANCH=R.ETA_ANCHOR
def label_of(p):
    for th,l in P.LABELS:
        if p<th: return l
    return "none"
def score_set(cs, bearing_override=None):
    """cs: list of candidate dicts at distinct receivers -> dict of scores"""
    if any(c["rx"] not in R.RECEIVERS for c in cs):
        return dict(lnN=-np.inf, ln_ftime=np.nan, lnB=np.sum([np.log(c["p"]/R.WINDOW_S) for c in cs]), blocked=True)
    rows=rows_for(cs[0]["rx"],cs[0]["t_unix"])
    for c in cs[1:]:
        tpc=PP["tp"][c["rx"]][rows]; rows=rows[(np.abs(tpc-c["t_unix"])<=WIN)&np.isfinite(PP["base"][c["rx"]][rows])]
    if len(rows)==0:
        return dict(lnN=-np.inf, ln_ftime=-np.inf, lnB=np.sum([np.log(c["p"]/R.WINDOW_S) for c in cs]), blocked=False, n_rows=0)
    Fp=np.ones((len(rows),len(ETA))); Kp=np.ones(len(rows)); allb=[]
    for c in cs:
        F,K,brs=factor(c,rows,bearing_override if (bearing_override is not None and c["rx"]=="H01W") else None); Fp*=F; Kp*=K; allb+=brs
    fm=Fp.mean(1); out=dict(blocked=False, n_rows=int((Kp>0).sum()), bearings=";".join(f"{b:.2f}" for b in allb))
    for o in ["D0","D2","D3","D4"]:
        w=Wt[o][rows]; out[f"lnN_{o}"]=np.log(max((w*fm).sum(),1e-300)); 
    w=w0[rows]; N=(w*fm).sum(); ft=(w*Kp).sum()
    out.update(lnN=np.log(N) if N>0 else -np.inf, ln_ftime=np.log(ft) if ft>0 else -np.inf,
               lnB=np.sum([np.log(c["p"]/R.WINDOW_S) for c in cs]),
               lnB_pB=np.sum([np.log((c["p_B"] if np.isfinite(c["p_B"]) else c["p"])/R.WINDOW_S) for c in cs]))
    if N>0:
        ww=w*fm/N; out.update(src_lat=float((ww*lat[rows]).sum()), src_lon=float((ww*lon[rows]).sum()), src_t=float((ww*t[rows]).sum()),
            src_E_med=float(np.interp(0.5,np.cumsum(ww[np.argsort(E[rows])]),np.sort(E[rows]))),
            eta_post_med=float(10**np.interp(0.5,np.cumsum((w[:,None]*Fp).sum(0))/(w[:,None]*Fp).sum(),np.log10(ETA))),
            baz_H01W=float(np.degrees(np.angle((ww*np.exp(1j*np.radians(baz[rows]))).sum()))%360))
    return out
def hms(u): s=u-T0; return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:04.1f}"
t0=time.time(); rows=[]
for i,c in C.iterrows():
    c=c.to_dict(); s=score_set([c]); rows.append({**c,**s})
SG=pd.DataFrame(rows); print(round(time.time()-t0,1))
SG["lnLR"]=SG.lnN-SG.lnB; SG["lnLR_pB"]=SG.lnN-SG.get("lnB_pB",SG.lnB)
for o in ["D2","D3","D4"]: SG[f"lnLR_{o}"]=SG[f"lnN_{o}"]-SG.lnB
SG["ln_f_amp_given_time"]=SG.lnN-SG.ln_ftime
print(SG.sort_values("lnLR",ascending=False)[["rx","time_utc","det","band","p","p_B","lnLR","ln_ftime","ln_f_amp_given_time","lnB","eta_level_ref","n_rows","bearings"]].head(20).to_string())
