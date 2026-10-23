
def hms(t, nd=1):
    s = round(t - T0, nd); sign = "-" if s<0 else ""; s=abs(s)
    w = 2 if nd==0 else 3+nd
    return f"{sign}{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:0{w}.{nd}f}"
def single_arc_uniform(rx, tobs, ndraw=20000):
    L = rng.uniform(arc_la.min(), arc_la.max(), ndraw); Lo = np.interp(L, arc_la, arc_lo); c = rng.normal(C, CSD, ndraw)
    timp = tobs + rng.normal(0,SIG_PICK,ndraw) - dist_km(L,Lo,rx)/c
    arr = {r2: timp + dist_km(L,Lo,r2)/c + rng.normal(0,SIG_PICK,ndraw) for r2 in RXL}
    return dict(kind="single-arc-uniform", lat=np.nan, lon=np.nan, t_imp=np.median(timp), lat_q=[L.min(), np.median(L), L.max()],
                t_imp_q=list(np.percentile(timp,[2.5,50,97.5])), ess=0.0, n_rows=0, mass=0.0,
                win={r2:(np.percentile(a,2.5), np.percentile(a,50), np.percentile(a,97.5)) for r2,a in arr.items()}, E_med=np.nan, tau_med=np.nan)
cands = [c for c in cands if c["kind"]=="pair"]
k=1
for _, r in singles.iterrows():
    try: g = single_geometry(r.receiver, r.t_unix)
    except ValueError: g = single_arc_uniform(r.receiver, r.t_unix)
    g.update(name=f"Single {k}: {names[r.receiver]} {r.time_utc}", rx=[r.receiver], t_obs=[r.t_unix], p_obs=[r.p], det=[f"{r.detector} {r.band_hz} Hz"],
             src=r.source, eta_needed_search=r.eta_needed)
    cands.append(g); k+=1
    print(g["name"], g["kind"], np.round(g["lat_q"],2), [hms(x,0) for x in g["t_imp_q"]], round(g["ess"]), round(g["mass"],4))
for c in cands: print(c["name"], {rx:(hms(a,0),hms(b,0)) for rx,(a,_,b) in c["win"].items()})
