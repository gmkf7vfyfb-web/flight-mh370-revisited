
_cache={}
def imos_record(i):
    if i in _cache: return _cache[i]
    r = rec.iloc[i]; f = RS.IMOS_ROOT / r.file
    x500 = N.decimate(N.read_volts(f)); upa = 1/np.sqrt(imos_div(r.logger))
    x100, e10 = D.imos_series(x500)
    tm, rho = D.m1b_env(e10, BANK)
    tl1, lev = D.band_levels_1s(x500*upa, 500, [(5.0,40.0)])
    out = dict(t0=r.t_start, x100_pa=x100*upa*1e-6, x500=x500*upa*1e-6, m1b_t=tm, m1b=rho, lev_t=tl1, lev=lev[(5.0,40.0)], logger=r.logger, file=r.file)
    _cache[i]=out; return out
o = imos_record(103); print(np.median(o["lev"]), np.percentile(o["lev"],[5,95]), np.abs(o["x100_pa"]).max())
# cross-check M1b window max vs imos_windows at this record
iw = pd.read_csv(f"{SR}/imos/imos_windows.csv", dtype={"receiver":str})
print(iw[(iw.file==o["file"])&(iw.detector=="M1b")][["time_utc","statistic","p"]].to_string())
ws, sc, tmx = D.window_scores(o["m1b_t"], o["m1b"], len(o["x100_pa"])/100); print(np.round(sc,4), [hms(o["t0"]+t) for t in tmx])
