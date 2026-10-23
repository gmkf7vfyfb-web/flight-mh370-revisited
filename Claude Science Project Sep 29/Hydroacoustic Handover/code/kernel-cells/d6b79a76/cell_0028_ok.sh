cd kh && python3 - <<'E'
s=open('flight_leg_worker.py').read()
old_start=s.index('def reduce_masses(')
old_end=s.index('def logbincount(')
new='''def reduce_masses(lm, regions, par, f4):
    """lm: per-row log mass (already including ln P/K); regions: name -> row index array (None = all rows).
    Returns per region ln S1, ln S2, family ln S1/S2 (A1, A2, B), ln sum_p M_p^2 and parents with positive mass."""
    fin = np.isfinite(lm)
    if not fin.any():
        z = {'l1': -np.inf, 'l2': -np.inf, 'fam1': [-np.inf] * 3, 'fam2': [-np.inf] * 3, 'par2': -np.inf, 'npar': 0}
        return {rn: dict(z) for rn in regions}
    s = float(lm[fin].max()); e = np.where(fin, np.exp(lm - s), 0.0)
    L = lambda v, k=1: float(np.log(v) + k * s) if v > 0 else -np.inf
    out = {}
    for rn, ix in regions.items():
        ee = e if ix is None else e[ix]; ff = f4 if ix is None else f4[ix]; pp = par if ix is None else par[ix]
        fb = np.nan_to_num(ff, nan=0).astype(np.int64)
        f1 = np.bincount(fb, ee, 4); f2 = np.bincount(fb, ee * ee, 4)
        M = np.bincount(pp, ee)
        out[rn] = {'l1': L(ee.sum()), 'l2': L((ee * ee).sum(), 2), 'fam1': [L(f1[c]) for c in (1, 2, 3)], 'fam2': [L(f2[c], 2) for c in (1, 2, 3)],
                   'par2': L((M * M).sum(), 2), 'npar': int((M > 0).sum())}
    return out


'''
s=s[:old_start]+new+s[old_end:]
# region index sets
s=s.replace("""    lnL, z2 = acoustic(t, d, db)""","""    lnL, z2 = acoustic(t, d, db)
    RIX = {rn: (None if rn == 'all' else np.nonzero(mk)[0]) for rn, mk in masks.items()}""")
s=s.replace("res['prior'][k] = reduce_masses(lm[k], masks, par, f4)","res['prior'][k] = reduce_masses(lm[k], RIX, par, f4)")
s=s.replace("reduce_masses(lm[k] + lnL[vn], {'all': masks['all'], 'strip': masks['strip'], 'X200': masks['X200'], 'H200': masks['H200']}, par, f4)",
            "reduce_masses(lm[k] + lnL[vn], {r_: RIX[r_] for r_ in ('all', 'strip', 'X200', 'H200')}, par, f4)")
s=s.replace("""        for rn in HREG:
            x = np.where(masks[rn], lm[k], -np.inf)
            hk[rn] = {'t': logbincount(ti, x, len(TB)), 'fo': logbincount(fi, x, len(FB)), 'aloft': logbincount(ai, x, len(AB) + 1)}""",
"""        for rn in HREG:
            ix = RIX[rn]; x = lm[k] if ix is None else lm[k][ix]; s_ = (lambda a: a) if ix is None else (lambda a, ix=ix: a[ix])
            hk[rn] = {'t': logbincount(s_(ti), x, len(TB)), 'fo': logbincount(s_(fi), x, len(FB)), 'aloft': logbincount(s_(ai), x, len(AB) + 1)}""")
open('flight_leg_worker.py','w').write(s)
E
grep -n "RIX" flight_leg_worker.py | head