"""Correlation of GDP-replay residuals between drifter PAIRS (Pleiades request, 9 Oct ~22:40 UTC).

Pairs are two segments of different drifters with the same start time (the replay starts every segment on
the 6-hourly grid, so "same start" means the same 6 h fix), both undrogued, both starting in the search
box 80-110 E, 45-20 S in March-May, initial separation <= 100 km. The residual (model minus drifter, km)
of each member is taken per component at leads 13 and 15 d. Same-lead correlation pools both member
orders; the cross-lag value pairs one member at 13 d with the other at 15 d, both orders. Pearson r per
component and separation bin (0-25, 25-50, 50-100 km), with pair counts and a drifter-block bootstrap
(resample drifters with replacement; a pair enters with the product of its members' multiplicities).
Two wider sets are reported because the strict set is small: undrogued pairs anywhere in the domain with
the same start, and with starts within 2 days.

python replay_pairs.py <segments.json> <out.json> name=sep.f32 [...]
"""
import json, sys
from datetime import datetime, timezone
import numpy as np

S = json.load(open(sys.argv[1])); seg = S["segments"]; L = S["fixes"] - 1; dt_d = S["step_s"] / 86400
ids = np.array([s["id"] for s in seg]); drog = np.array([s["drogued"] for s in seg])
t0 = np.array([s["t0"] for s in seg]); lon = np.array([s["lon"][0] for s in seg]); lat = np.array([s["lat"][0] for s in seg])
mon = np.array([datetime.fromtimestamp(x, timezone.utc).month for x in t0])
box = (lon >= 80) & (lon <= 110) & (lat >= -45) & (lat <= -20)
R = 6371.0088
def dist(i, j):
    p1, p2 = np.radians(lat[i]), np.radians(lat[j]); dl = np.radians(lon[j] - lon[i])
    h = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(h))
def pairs(sel, max_dt_s):
    k = np.where(sel)[0]; k = k[np.argsort(t0[k])]; out = []
    for a in range(len(k)):
        for b in range(a + 1, len(k)):
            i, j = k[a], k[b]
            if t0[j] - t0[i] > max_dt_s: break
            if ids[i] != ids[j]:
                d = dist(i, j)
                if d <= 100: out.append((i, j, d))
    return out
I13, I15 = int(round(13 / dt_d)) - 1, L - 1
BINS = [(0, 25), (25, 50), (50, 100), (0, 100)]
rng = np.random.default_rng(1308)
def corr(x, y, w=None):
    ok = np.isfinite(x) & np.isfinite(y)
    if w is not None: w = w[ok]
    x, y = x[ok], y[ok]
    if len(x) < 3 or (w is not None and w.sum() < 3): return np.nan, int(ok.sum())
    if w is None: w = np.ones_like(x)
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    c = np.average((x - mx) * (y - my), weights=w); vx = np.average((x - mx) ** 2, weights=w); vy = np.average((y - my) ** 2, weights=w)
    return float(c / np.sqrt(vx * vy)), int(len(x))
def stats(d, P, B=1000):
    res = {}
    for lo, hi in BINS:
        Q = [(i, j) for i, j, s in P if lo <= s < hi or (hi == 100 and s == 100)]
        if not Q: res[f"{lo}-{hi}km"] = dict(pairs=0); continue
        a = np.array([q[0] for q in Q]); b = np.array([q[1] for q in Q])
        drs = np.unique(np.concatenate([ids[a], ids[b]]))
        row = dict(pairs=len(Q), drifters=int(len(drs)))
        for name, (la, lb) in {"same_13d": (I13, I13), "same_15d": (I15, I15), "cross_13_15d": (I13, I15)}.items():
            for c, cn in ((0, "east"), (1, "north")):
                x = np.concatenate([d[a, la, c], d[b, la, c]]); y = np.concatenate([d[b, lb, c], d[a, lb, c]])
                r, n = corr(x, y)
                bs = []
                for _ in range(B):
                    pick = rng.choice(drs, len(drs)); cnt = {k: 0 for k in drs}
                    for k in pick: cnt[k] += 1
                    w = np.array([cnt[ids[i]] * cnt[ids[j]] for i, j in zip(a, b)], float)
                    rb, _ = corr(x, y, np.concatenate([w, w]))
                    if np.isfinite(rb): bs.append(rb)
                ci = [round(float(v), 3) for v in np.percentile(bs, [2.5, 97.5])] if len(bs) > 50 else None
                row[f"{name}_{cn}"] = dict(r=None if not np.isfinite(r) else round(r, 3), n=n, boot95=ci)
        res[f"{lo}-{hi}km"] = row
    return res
strict = (~drog) & box & np.isin(mon, [3, 4, 5])
relaxed = ~drog
P_strict, P_same, P_relaxed = pairs(strict, 0.0), pairs(relaxed, 0.0), pairs(relaxed, 2 * 86400.0)
out = dict(definition=__doc__.split("python ")[0].strip(), lead_days=[13, 15], strict_pairs=len(P_strict), same_start_domain_pairs=len(P_same), relaxed_pairs=len(P_relaxed), configs={})
for arg in sys.argv[3:]:
    name, path = arg.split("=", 1)
    d = np.fromfile(path, "<f4").reshape(len(seg), L, 2).astype(float)
    out["configs"][name] = dict(strict_undrogued_boxMAM_same_start=stats(d, P_strict), domain_undrogued_same_start=stats(d, P_same), relaxed_undrogued_domain_start_within_2d=stats(d, P_relaxed))
json.dump(out, open(sys.argv[2], "w"), indent=1)
print("pairs strict", len(P_strict), "same-start domain", len(P_same), "relaxed", len(P_relaxed))
for name, c in out["configs"].items():
    for setn, st in c.items():
        for b, row in st.items():
            if row.get("pairs"):
                f = lambda k: f"{row[k]['r']}{row[k]['boot95']}" if row[k]['r'] is not None else "nan"
                print(f"{name:26s} {setn[:7]} {b:9s} pairs {row['pairs']:4d} dr {row['drifters']:3d} | 13d e {f('same_13d_east')} n {f('same_13d_north')} | 15d e {f('same_15d_east')} n {f('same_15d_north')} | x13-15 e {f('cross_13_15d_east')} n {f('cross_13_15d_north')}")
