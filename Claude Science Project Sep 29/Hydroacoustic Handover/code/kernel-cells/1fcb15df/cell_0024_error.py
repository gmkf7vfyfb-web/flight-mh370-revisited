
def hms(t, nd=1):
    s = round(t - T0, nd); sign = "-" if s<0 else ""; s=abs(s)
    return f"{sign}{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:0{3+nd}.{nd}f}"
def wq(x, w, q):
    o = np.argsort(x); cw = np.cumsum(w[o]); cw/=cw[-1]; return np.interp(q, cw, x[o])
def single_geometry(rx, tobs, ndraw=20000):
    d = DS[rx]; sig = np.sqrt((d*CSD/C**2)**2 + SIG_PICK**2)
    z = (st + d/C - tobs)/sig; m = np.abs(z)<4
    w = sw[m]*np.exp(-0.5*z[m]**2)/sig[m]
    ess = w.sum()**2/(w**2).sum()
    # draws for predictive arrivals with c noise and pick noise
    j = rng.choice(np.where(m)[0], size=ndraw, p=w/w.sum()); c = rng.normal(C, CSD, ndraw)
    arr = {r2: st[j] + DS[r2][j]/c + rng.normal(0,SIG_PICK,ndraw) for r2 in RXL}
    lat_med = wq(sl[m], w, 0.5)
    return dict(kind="single", lat=lat_med, lon=wq(so[m],w,0.5), t_imp=wq(st[m],w,0.5),
                lat_q=[wq(sl[m],w,q) for q in (0.025,0.5,0.975)], t_imp_q=[wq(st[m],w,q) for q in (0.025,0.5,0.975)],
                ess=float(ess), n_rows=int(m.sum()), mass=float(sw[m].sum()/sw.sum()),
                win={r2:(np.percentile(a,2.5), np.percentile(a,50), np.percentile(a,97.5)) for r2,a in arr.items()},
                E_med=wq(SE[m],w,0.5), tau_med=wq(STAU[m],w,0.5))
k=1
for _, r in singles.iterrows():
    g = single_geometry(r.receiver, r.t_unix)
    g.update(name=f"Single {k}: {names[r.receiver]} {r.time_utc}", rx=[r.receiver], t_obs=[r.t_unix], p_obs=[r.p], det=[f"{r.detector} {r.band_hz} Hz"],
             src=r.source, eta_needed_search=r.eta_needed)
    cands.append(g); k+=1
    print(g["name"], np.round(g["lat_q"],2), [hms(x,0) for x in g["t_imp_q"]], round(g["ess"]), g["n_rows"], round(g["mass"],4))
    print("   ", {rx2:(hms(a,0),hms(b,0)) for rx2,(a,_,b) in g["win"].items() if rx2 in ("H01W","H08S","3376","3274","3250","SSEIR")})
