"""Composer views on run J, step 1: per-seed reduction (numpy). One call = one (set, stratum, seed).

Row mass per 00:19 option: end of flight's option_table_0019.seed_terms UNCHANGED (only its final reduction replaced, as the drift
stand-in's compose_drift_runj.py), cells 'D<d> total q=0.333 (C2 silent)' (headline cause model: competing causes, prior odds
q = 1/3, other cause silent).
Factors per row (relative scale within a factor; all position-only):
  drift   run A rebuilt node surfaces, 50 km kernel, bilinear in L over evaluated corners, per ocean model (GLORYS12, GlobCurrent);
          h100 kernel as the model-error-doubled sensitivity; Australian populated-coast term (RECONSTRUCTED, sensitivity) as
          L' = L exp(Delta_pop) at nodes (prep_nodes.py).
  Pleiades joint-surface-rho0.25-gcrel (P + COSMO F1-F4), per ocean model, cell lookup as pleiades/finds-test/reduce_seed.py.
  searches seabed_loglik.py transcription (composer pass 1; rho 0.05, Phase 2 q 0.945, Bluefin-21 q 0.9, shared miss), point
          target at the IMPACT point (no run J settling resample); rho 0.10 as the model-error-doubled sensitivity.
  hydro   0 by ruling (no P_D): contributes nothing; no column.
Not computed rows (NaN) of any factor: carried at the (seed, option) weighted mean of that factor's computed rows under the core
row mass, per ocean model (ruling 15 Oct 2026); never excluded. Shares reported.
Ocean model shared by drift and Pleiades: marginalised JOINTLY per row, Lambda = 0.5 (D_G P_G + D_C P_C).
Usage: python reduce_seed_views.py SET STRATUM SEED OUT.npz      (SET = prod | both)
"""
import sys, os, pathlib, inspect, json, time, importlib.util
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; PROJ = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(PROJ / 'engine/hypotheses/end-of-flight/smoke'))
import views_common as V
import displacement_hist as DH
DH.SATCOM_CSV = (PROJ / 'engine/data/satcom-observations.csv').resolve()
import option_table_0019 as OT
OT.SATCOM_CSV = DH.SATCOM_CSV
_src = inspect.getsource(OT.seed_terms); _src = _src[:_src.index('    out = {}')] + '    return cells, f4, g\n'
_ns = dict(OT.__dict__); exec(_src, _ns); seed_cells = _ns['seed_terms']
_spec = importlib.util.spec_from_file_location('seabed_loglik', str(PROJ / 'results/composer-pass1-run-c/seabed_loglik.py'))
SL = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SL); SL.COV = PROJ / 'engine/hypotheses/seabed-search/coverage'

X = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
WORK = X / 'composer/run-j-views/work'
LREF = -125.0
DKEYS = [f'D{d}' for d in range(6)]
KEY = lambda d: f'{d} total q=0.333 (C2 silent)'
FAMS = {'A1': (1,), 'A2': (2,), 'B': (3, 6)}

# products: name -> (drift variant or None, use Pleiades, searches variant or None)
PRODUCTS = {
    'core': (None, False, None), 'D': ('h50', False, None), 'S': (None, False, 's05'), 'P': (None, True, None),
    'DS': ('h50', False, 's05'), 'DP': ('h50', True, None), 'SP': (None, True, 's05'), 'DSP': ('h50', True, 's05'),
    'A': ('pop', False, None), 'AS': ('pop', False, 's05'), 'AP': ('pop', True, None), 'ASP': ('pop', True, 's05'),
    'D100': ('h100', False, None), 'D100S': ('h100', False, 's05'), 'S10': (None, False, 's10'), 'DS10': ('h50', False, 's10'),
    'DG': ('h50G', False, None), 'DC': ('h50C', False, None), 'DGS': ('h50G', False, 's05'), 'DCS': ('h50C', False, 's05'),
}
# arc-uniform views (a)(ii): prior uniform per NM along the arc span (arc_r.py), same end-of-flight impact model
UPRODUCTS = {'U': (None, None), 'UD': ('h50', None), 'US': (None, 's05'), 'UP': ('P', None), 'UA': ('pop', None), 'UD100': ('h100', None), 'US10': (None, 's10')}
KL_PAIRS = [('D', 'core'), ('S', 'core'), ('P', 'core'), ('A', 'core'), ('DS', 'core'), ('DS', 'S'), ('DS', 'D'),
            ('DSP', 'core'), ('DSP', 'SP'), ('DSP', 'DP'), ('DSP', 'DS'), ('AS', 'core'), ('AS', 'S'), ('AS', 'A'),
            ('ASP', 'core'), ('ASP', 'SP'), ('ASP', 'AP'), ('ASP', 'AS'), ('DP', 'D'), ('DP', 'P'), ('SP', 'S'), ('SP', 'P'),
            ('AP', 'A'), ('AP', 'P'), ('D100S', 'S'), ('D100', 'core'), ('S10', 'core'), ('DS10', 'D')]


def main(set_, st, k, outp, base=None):
    t0 = time.time()
    root = X / ('end-of-flight/run-j' if set_ == 'prod' else 'end-of-flight/run-j-both-burst') / st
    sd = root / f'seed-{k}'
    cells, f4, g = seed_cells(sd, X / f'core/run-j/{st}/bto-bfo/seed-{k}/handoff-m0011/handoff.npy')
    keep = {d: cells[KEY(d)] for d in DKEYS}; del cells
    lat = np.asarray(g('latitude_deg'), float); lon = np.asarray(g('longitude_deg'), float); n = len(lat)
    fam = np.zeros(n, np.int8)
    for fi, (nm, codes) in enumerate(FAMS.items()):
        fam[np.isin(f4, codes)] = fi
    famok = np.isin(f4, sum(FAMS.values(), ()))
    sub = V.sub_index(lat); cell = V.cell_index(lat, lon)
    # 7th-arc position of the 00:19:29 crossing; rows without one get no arc position and weight 0 in the arc-uniform views
    bl, bo = np.asarray(g('latent:last_burst_latitude_deg'), float), np.asarray(g('latent:last_burst_longitude_deg'), float)
    noburst = ~(np.isfinite(bl) & np.isfinite(bo))
    sarc = np.where(noburst, np.nan, V.arc_s(np.where(noburst, 0.0, bl), np.where(noburst, 0.0, bo)))
    sb = V.sbin_index(sarc); RR = np.load(WORK / 'arc-r.npz')
    # ---- factors (raw, NaN = not computed)
    N = np.load(WORK / 'nodes.npz')
    inside, nid, W = V.drift_corners(lat, lon)
    raw = {}
    for mod, tag in (('glorys12', 'G'), ('globcurrent', 'C')):
        for bw in ('h50', 'h100'):
            raw[f'{bw}{tag}'] = V.drift_lookup(inside, nid, W, np.exp(N[f'{mod}_{bw}'] - LREF))
        raw[f'pop{tag}'] = V.drift_lookup(inside, nid, W, np.exp(N[f'{mod}_h50'] + N[f'{mod}_dpop'] - LREF))
    del inside, nid, W
    meta = {}
    for line in (X / 'pleiades/run-i/surfaces/joint-surface-rho0.25-gcrel.toml').read_text().splitlines():
        kk, vv = line.split(' = ', 1); meta[kk] = vv
    nl, nn = int(meta['nlat']), int(meta['nlon']); plat0, plon0, pst = float(meta['lat0']), float(meta['lon0']), float(meta['step_deg'])
    J = np.fromfile(X / 'pleiades/run-i/surfaces/joint-surface-rho0.25-gcrel.f32', '<f4').reshape(2, nl, nn).astype(float)
    PREF = float(np.nanmax(np.where(np.isfinite(J), J, np.nan)))
    pi = np.floor((lat - (plat0 - pst / 2)) / pst).astype(np.int64); pj = np.floor((lon - (plon0 - pst / 2)) / pst).astype(np.int64)
    pin = (pi >= 0) & (pi < nl) & (pj >= 0) & (pj < nn)
    for mi, tag in ((0, 'G'), (1, 'C')):
        v = np.full(n, np.nan); v[pin] = J[mi, pi[pin], pj[pin]]; raw[f'P{tag}'] = np.where(np.isfinite(v), np.exp(v - PREF), np.nan)
    del J
    if SL._R is None:
        SL._R = [(SL.decode(SL.COV / f'{nm}.cov'), q) for nm, q in SL.CAMPAIGNS]
    cov = [SL.coverage(Rr, lat, lon) for Rr, q in SL._R]
    miss = np.ones(n)
    for (Rr, q), c in zip(SL._R, cov):
        miss *= (1.0 - c * q)
    cunion = 1.0 - (1.0 - cov[0]) * (1.0 - cov[1]); del cov
    LS = {'s05': 0.05 + 0.95 * miss, 's10': 0.10 + 0.90 * miss}
    chk_sl = float(np.nanmax(np.abs(np.log(LS['s05'][:200000]) - SL.loglik(lat[:200000], lon[:200000]))))
    # drift export check (waypoints production only): my lookup against the module's own per-impact columns
    exp_chk = {}
    dpath = X / f'debris-drift/run-j/{st}/seed-{k}/drift-lnL.npy'
    if set_ == 'prod' and dpath.exists():
        Aexp = np.load(dpath, mmap_mode='r'); assert len(Aexp) == n
        for mod, tag in (('glorys12', 'G'), ('globcurrent', 'C')):
            sc = np.asarray(Aexp[f'state_{mod}_h50']) == 1; le = np.asarray(Aexp[f'lnL_{mod}_h50'], float)
            mine = np.log(raw[f'h50{tag}']) + LREF; both = sc & np.isfinite(mine)
            exp_chk[mod] = {'state_mismatch': int((sc != np.isfinite(mine)).sum()), 'max_abs_dlnL': float(np.max(np.abs(mine[both] - le[both])))}
        lnm = np.asarray(Aexp['lnL_mean_h50'], float); scm = np.isfinite(lnm)
        Lexp = np.where(scm, np.exp(np.where(scm, lnm, LREF) - LREF), 0.0)
    else:
        Aexp = None
    out = {'n_rows': n, 'chk_seabed_max_abs': chk_sl, 'exp_chk': json.dumps(exp_chk), 'PREF': PREF, 'LREF': LREF,
           'NSUB': V.NSUB, 'NY': V.NY, 'NX': V.NX, 'n_outside_grid': int((cell == V.NY * V.NX).sum()), 'n_outside_sub': int((sub == V.NSUB).sum()), 'n_fam_other': int((~famok).sum())}
    nc1 = V.NY * V.NX + 1
    if base is not None:   # U-only mode: keep every non-arc-uniform array of an earlier run of this script
        prev = dict(np.load(base)); out = {kk: v for kk, v in prev.items() if not any(kk.startswith(f'{d}|{u}|') for d in DKEYS for u in UPRODUCTS)}; out['U_only_recomputed'] = 1
    raw_cnt = np.bincount(sub, minlength=V.NSUB + 1); out['raw_count_sub'] = raw_cnt
    out['raw_lon_sub'] = np.bincount(sub, lon, V.NSUB + 1)
    for d in DKEYS:
        a = keep[d]; fin = np.isfinite(a)
        if not fin.any():
            out[f'{d}|valid'] = 0; continue
        s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0); out[f'{d}|valid'] = 1; out[f'{d}|s'] = s
        M = m.sum(); out[f'{d}|M'] = M
        # carried factors under this option's core mass
        F = {}
        for nm_, arr in raw.items():
            ok = np.isfinite(arr); den = m[ok].sum()
            bar = (m[ok] * arr[ok]).sum() / den if den > 0 else 1.0
            F[nm_] = np.where(ok, arr, bar); out[f'{d}|nc|{nm_}'] = float(m[~ok].sum() / M)
        out[f'{d}|lon_sub'] = np.bincount(sub, m * lon, V.NSUB + 1)
        out[f'{d}|noburst_share'] = float(m[noburst].sum() / M)
        rr = np.r_[RR[f'head|{d}|r'], 0.0][sb]; mu = m * rr      # arc-uniform base: r = u / q per 10 NM arc bin (arc_r.py)
        FU = {}
        for nm_, arr in raw.items():
            ok = np.isfinite(arr); den = mu[ok].sum()
            FU[nm_] = np.where(ok, arr, (mu[ok] * arr[ok]).sum() / den if den > 0 else 1.0)
        LAM, LNL = {}, {}
        for pn, (dv, usep, sv) in (PRODUCTS.items() if base is None else []):
            if dv is None and not usep:
                lam = np.ones(n)
            elif dv in ('h50G', 'h50C'):
                lam = F[dv].copy() * (F['P' + dv[-1]] if usep else 1.0)
            else:
                dG = F[dv + 'G'] if dv else 1.0; dC = F[dv + 'C'] if dv else 1.0
                pG = F['PG'] if usep else 1.0; pC = F['PC'] if usep else 1.0
                lam = 0.5 * (dG * pG + dC * pC) * np.ones(n)
            if sv is not None:
                lam = lam * LS[sv]
            LAM[pn] = lam
            with np.errstate(divide='ignore'):
                LNL[pn] = np.log(lam)
            w = m * lam
            out[f'{d}|{pn}|S1'] = np.bincount(sub, w, V.NSUB + 1)
            out[f'{d}|{pn}|S2'] = np.bincount(sub, w * w, V.NSUB + 1)
            out[f'{d}|{pn}|IN'] = np.bincount(sub, w * cunion, V.NSUB + 1)
            out[f'{d}|{pn}|FAM'] = np.stack([np.bincount(sub[fam == i], w[fam == i], V.NSUB + 1) for i in range(3)])
            out[f'{d}|{pn}|FAM2'] = np.stack([np.bincount(sub[fam == i], (w * w)[fam == i], V.NSUB + 1) for i in range(3)])
            mp = np.zeros((4, nc1), np.float64); mp[0] = np.bincount(cell, w, nc1)
            for i in range(3):
                mp[i + 1] = np.bincount(cell[fam == i], w[fam == i], nc1)
            out[f'{d}|{pn}|MAP'] = mp[:, :-1].astype(np.float32)
            out[f'{d}|{pn}|wlnL'] = float(np.sum(np.where(w > 0, w * LNL[pn], 0.0)))
            out[f'{d}|{pn}|SB'] = np.bincount(sb, w, V.NSB + 1)
        for (pp, bb) in (KL_PAIRS if base is None else []):
            w = m * LAM[pp]
            out[f'{d}|KL|{pp}|{bb}'] = float(np.sum(np.where(w > 0, w * (LNL[pp] - LNL[bb]), 0.0)))
            out[f'{d}|KLfam|{pp}|{bb}'] = np.array([float(np.sum(np.where((w > 0) & (fam == i), w * (LNL[pp] - LNL[bb]), 0.0))) for i in range(3)])
        for pn, (dv, sv) in UPRODUCTS.items():
            if dv is None:
                lam = np.ones(n)
            elif dv == 'P':
                lam = 0.5 * (FU['PG'] + FU['PC'])
            else:
                lam = 0.5 * (FU[dv + 'G'] + FU[dv + 'C'])
            if sv is not None:
                lam = lam * LS[sv]
            w = mu * lam
            out[f'{d}|{pn}|S1'] = np.bincount(sub, w, V.NSUB + 1); out[f'{d}|{pn}|S2'] = np.bincount(sub, w * w, V.NSUB + 1)
            out[f'{d}|{pn}|IN'] = np.bincount(sub, w * cunion, V.NSUB + 1); out[f'{d}|{pn}|SB'] = np.bincount(sb, w, V.NSB + 1)
            out[f'{d}|{pn}|FAM'] = np.stack([np.bincount(sub[fam == i], w[fam == i], V.NSUB + 1) for i in range(3)])
            out[f'{d}|{pn}|FAM2'] = np.stack([np.bincount(sub[fam == i], (w * w)[fam == i], V.NSUB + 1) for i in range(3)])
            mp = np.zeros((4, nc1)); mp[0] = np.bincount(cell, w, nc1)
            for i in range(3):
                mp[i + 1] = np.bincount(cell[fam == i], w[fam == i], nc1)
            out[f'{d}|{pn}|MAP'] = mp[:, :-1].astype(np.float32); out[f'{d}|{pn}|wlnL'] = 0.0
        if Aexp is not None and base is None:   # reproduction of the drift stand-in (two-model export column, joint not-computed set, carry)
            Lb = (m * Lexp)[scm].sum() / m[scm].sum(); w = m * np.where(scm, Lexp, Lb)
            li = np.clip(np.searchsorted(OT.LAT, lat), 0, len(OT.LAT) - 1)
            out[f'{d}|rep|q1'] = w.sum(); out[f'{d}|rep|q2'] = (w * w).sum(); out[f'{d}|rep|lat1'] = (w * lat).sum(); out[f'{d}|rep|nc'] = m[~scm].sum()
            out[f'{d}|rep|hq'] = np.bincount(li, w, len(OT.LAT)); out[f'{d}|rep|hp'] = np.bincount(li, m, len(OT.LAT))
            out[f'{d}|rep|p2'] = (m * m).sum(); out[f'{d}|rep|lat0'] = (m * lat).sum()
        del LAM, LNL, F, FU
    np.savez_compressed(outp, **out)
    print(f'{set_} {st} seed-{k} rows {n} {time.time() - t0:.0f}s seabed_chk {chk_sl:.2e} drift_chk {exp_chk}', flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
