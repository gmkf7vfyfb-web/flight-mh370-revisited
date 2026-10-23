
print({rx: round(v,1) for rx,v in M.bmed.items()})
T_ = np.load(RS.TEMPLATES); BANK, _ = D.bank_env(T_, RS.IMOS_BANK_RANGES, 100)
cal = pd.read_csv(os.path.join(MOD,"results-data/imos1d/calibration_gain.csv"), dtype={"logger":str})
NULLS = {lg: np.load(f"{SR}/null/null_{lg}.npz") for lg in ("3376","3274","3250")}
def imos_div(lg):
    g = cal[cal.logger==lg]; Gd = 10*np.log10(np.mean([10**(g[g.band==b].gain_db.iloc[0]/10) for b in ("5-10","10-20","20-40")]))
    return 10**((Gd + meta[lg]["sens_db"])/10)
_cache={}
def imos_record(i):
    if i in _cache: return _cache[i]
    r = rec.iloc[i]; f = RS.IMOS_ROOT / r.file
    x500 = N.decimate(N.read_volts(f)); upa = np.sqrt(imos_div(r.logger))
    x100, e10 = D.imos_series(x500)
    tm, rho = D.m1b_env(e10, BANK)
    tl1, lev = D.band_levels_1s(x500*upa, 500, [(5.0,40.0)])
    out = dict(t0=r.t_start, x100_pa=x100*upa*1e-6, x500=x500*upa*1e-6, m1b_t=tm, m1b=rho, lev_t=tl1, lev=lev[(5.0,40.0)], logger=r.logger, file=r.file)
    _cache[i]=out; return out
i = rec[(rec.logger=="3376")&(rec.t_start<=hms2u("00:53:20"))&(rec.t_end>=hms2u("00:53:20"))].index
print(i, rec.loc[i,["file","t_start"]].assign(ts=lambda d: d.t_start.map(hms)).to_string())
o = imos_record(i[0]); print(np.median(o["lev"]), np.percentile(o["lev"],[5,95]), o["m1b"].max(), len(o["x100_pa"])/100)
nl = NULLS["3376"]["M1b"]; print("thr", [round(np.quantile(nl,1-a),3) for a in (0.3,0.1,0.05)])
