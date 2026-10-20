"""Composer views on run J, pass A: proposal mass per 10 NM bin of 7th-arc position of the 00:19:29 crossing, per 00:19 option,
and the end-of-flight displacement (impact minus 00:19:29 position) under the core D0 mass, per seed. Usage: python arc_q.py SET STRATUM SEED OUT.npz"""
import sys, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import reduce_seed_views as RS, views_common as V
set_, st, k, outp = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
root = RS.X / ('end-of-flight/run-j' if set_ == 'prod' else 'end-of-flight/run-j-both-burst') / st
cells, f4, g = RS.seed_cells(root / f'seed-{k}', RS.X / f'core/run-j/{st}/bto-bfo/seed-{k}/handoff-m0011/handoff.npy')
lat, lon = np.asarray(g('latitude_deg'), float), np.asarray(g('longitude_deg'), float)
bl, bo = np.asarray(g('latent:last_burst_latitude_deg'), float), np.asarray(g('latent:last_burst_longitude_deg'), float)
noburst = ~(np.isfinite(bl) & np.isfinite(bo))          # rows with no 00:19:29 crossing: no arc position (bin NSB), as reduce_seed_views.py
s = np.where(noburst, np.nan, V.arc_s(np.where(noburst, 0.0, bl), np.where(noburst, 0.0, bo))); sb = V.sbin_index(s)
out = {'n_rows': len(lat), 'n_burst_nan': int((~np.isfinite(bl) | ~np.isfinite(bo)).sum()), 'raw_sb': np.bincount(sb, minlength=V.NSB + 1),
       'arc_dist_km': np.histogram(np.abs(np.asarray(g('bto_residual_us:m0019a'))) * 0.15, np.arange(0, 301, 5))[0]}
de = (lon - bo) * 111.32 * np.cos(np.radians(0.5 * (lat + bl))); dn = (lat - bl) * 111.32
for d in RS.DKEYS:
    a = cells[RS.KEY(d)]; fin = np.isfinite(a)
    if not fin.any():
        out[f'{d}|valid'] = 0; continue
    sc = float(a[fin].max()); m = np.where(fin, np.exp(a - sc), 0.0)
    out[f'{d}|valid'] = 1; out[f'{d}|s'] = sc; out[f'{d}|q'] = np.bincount(sb, m, V.NSB + 1)
    if d == 'D0':
        out['disp'] = np.histogram2d(de, dn, [np.arange(-500, 501, 5), np.arange(-500, 501, 5)], weights=m)[0]
        out['disp_out'] = float(m[(np.abs(de) > 500) | (np.abs(dn) > 500)].sum() / m.sum())
np.savez(outp, **out); print(set_, st, k, 'burst nan', out['n_burst_nan'], flush=True)
