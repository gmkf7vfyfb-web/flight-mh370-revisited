"""Per-draw seabed field extent from settling's wreckage elements (settling, 10 Oct 2026). Usage: python3 field_extent.py <dir with A_impacts.f64, A_elements.f64>"""
import sys, json, numpy as np
D = sys.argv[1]; FA = ["intact", "broken", "fragmented"]
E = np.fromfile(f"{D}/A_elements.f64", "<f8").reshape(-1, 8); T = np.fromfile(f"{D}/A_impacts.f64", "<f8").reshape(-1, 14)
E = E[E[:, 4] == 0]; row = E[:, 0].astype(np.int64); lat0, lon0 = T[row, 1], T[row, 2]
x = (E[:, 6] - lon0) * 111195 * np.cos(np.radians(lat0)); y = (E[:, 5] - lat0) * 111195; m = E[:, 7]
o = np.argsort(row, kind="stable"); row, x, y, m, fam, cls = row[o], x[o], y[o], m[o], E[o, 2], E[o, 3]
u, start = np.unique(row, return_index=True); stop = np.r_[start[1:], len(row)]; n = stop - start
M = np.add.reduceat(m, start); cx = np.add.reduceat(m * x, start) / M; cy = np.add.reduceat(m * y, start) / M
r = np.hypot(x - np.repeat(cx, n), y - np.repeat(cy, n)); g = np.repeat(np.arange(len(u)), n)
def radius(mask, q):
    mm = np.where(mask, m, 0.0); oo = np.lexsort((r, g)); rs, ms, gs = r[oo], mm[oo], g[oo]
    cm = np.cumsum(ms); tot = np.add.reduceat(mm, start); base = np.concatenate([[0], cm[stop - 1][:-1]])
    fr = (cm - base[gs]) / np.where(tot[gs] > 0, tot[gs], np.nan)
    idx = np.searchsorted(fr + gs * 2.0, np.arange(len(u)) * 2.0 + q); out = rs[np.minimum(idx, len(rs) - 1)]; out[tot <= 0] = np.nan; return out
allm = np.ones_like(m, bool); R50, R90, Rs90 = radius(allm, 0.5), radius(allm, 0.9), radius(np.isin(cls, [0, 1, 2, 3]), 0.9)
Rmax = np.maximum.reduceat(r, start); famd = fam[start].astype(int); res = {}
for name, s in [(FA[f], famd == f) for f in range(3)] + [("all", np.ones(len(u), bool))]:
    res[name] = {"draws": int(s.sum()), **{k: np.nanpercentile(v[s], [10, 50, 90]).round(0).tolist() for k, v in
                 [("R50_all_mass_m", R50), ("R90_all_mass_m", R90), ("R90_structural_mass_m", Rs90), ("Rmax_any_settled_piece_m", Rmax)]}}
print(json.dumps(res, indent=1))
