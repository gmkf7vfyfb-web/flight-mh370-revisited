
C, CSD = 1.482, 0.006
SIG_PICK = np.hypot(RC.SIGMA_INJ_S, RC.SIGMA_CLOCK_S)   # injection 3 s + clock 2 s
fine_la = np.linspace(arc_la.min(), arc_la.max(), 4201); fine_lo = np.interp(fine_la, arc_la, arc_lo)
RXL = list(RX.keys())
Dfine = {rx: dist_km(fine_la, fine_lo, rx) for rx in RXL}
def hms2u(s): h,m,x = s.split(":"); return T0+3600*int(h)+60*int(m)+float(x)
S_ = np.load(f"{SR}/geometry/sample.npz")
samp = {k:S_[k] for k in ["lat","lon","t_unix","E_j","tau90_s","w_D0"]}
okS = samp["w_D0"]>0
def prior_mass_lat(L, half=1.0):
    m = okS & (np.abs(samp["lat"]-L)<=half); return samp["w_D0"][m].sum()/samp["w_D0"][okS].sum()
def roots(lag_curve, target):
    s = np.sign(lag_curve-target); i = np.where(np.diff(s)!=0)[0]
    return [float(np.interp(target, [lag_curve[k],lag_curve[k+1]], [fine_la[k],fine_la[k+1]])) if lag_curve[k+1]!=lag_curve[k] else fine_la[k] for k in i]
rng = np.random.default_rng(20261022)
def pair_geometry(rxa, ta, rxb, tb, n=4000):
    lagc = (Dfine[rxb]-Dfine[rxa])/C; target = tb-ta
    L0 = roots(lagc, target)
    if not L0: return None
    masses = [prior_mass_lat(L) for L in L0]; Lp = L0[int(np.argmax(masses))]
    # MC
    c = rng.normal(C, CSD, n); ea = rng.normal(0, SIG_PICK, n); eb = rng.normal(0, SIG_PICK, n)
    lats = np.full(n, np.nan)
    for i in range(n):
        lc = (Dfine[rxb]-Dfine[rxa])/c[i]; r = roots(lc, (tb+eb[i])-(ta+ea[i]))
        if r: lats[i] = r[int(np.argmin(np.abs(np.array(r)-Lp)))]
    ok = np.isfinite(lats); lats=lats[ok]; c=c[ok]; ea=ea[ok]
    lons = np.interp(lats, arc_la, arc_lo)
    timp = (ta+ea) - dist_km(lats,lons,rxa)/c
    arr = {rx: timp + dist_km(lats,lons,rx)/c + rng.normal(0,SIG_PICK,len(c)) for rx in RXL}
    lo0 = float(np.interp(Lp, arc_la, arc_lo)); ti0 = ta - dist_km(Lp,lo0,rxa)[0]/C
    return dict(kind="pair", loci=list(zip(L0,masses)), lat=Lp, lon=lo0, t_imp=ti0, lat_q=np.percentile(lats,[2.5,50,97.5]),
                t_imp_q=np.percentile(timp,[2.5,50,97.5]), n_ok=int(ok.sum()), n=n,
                win={rx:(np.percentile(a,2.5), np.percentile(a,50), np.percentile(a,97.5)) for rx,a in arr.items()})
cands=[]
def add_pair(r, name):
    g = pair_geometry(r.rx_a, hms2u(r.t_a), r.rx_b, hms2u(r.t_b))
    g.update(name=name, rx=[r.rx_a, r.rx_b], t_obs=[hms2u(r.t_a), hms2u(r.t_b)], p_obs=[r.p_a, r.p_b], det=[r.det_a, r.det_b],
             lag=r.lag_s, lag_rule=(r.lag_lo_s, r.lag_hi_s), max_p=r.max_p, p_perm=r.p_perm, n_pairs_obs=r.n_pairs_obs)
    cands.append(g); return g
strong = pm[(pm.rx_a=="H01W")&(pm.rx_b=="H08S")&(pm.t_a=="00:52:04")&(pm.t_b=="01:12:49")].iloc[0]
g = add_pair(strong, "Pair 1 (strongest): Cape Leeuwin 00:52:04 + Diego Garcia South 01:12:49")
print(g["loci"], g["lat"], g["lon"], hms(g["t_imp"]), g["lat_q"], [hms(x) for x in g["t_imp_q"]], g["n_ok"])
for rx in RXL: print(rx, [hms(x) for x in g["win"][rx]])
