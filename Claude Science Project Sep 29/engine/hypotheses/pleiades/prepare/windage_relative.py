"""Sensitivity: product-relative windage for GlobCurrent (debris-drift audit F1, 10 Oct 2026).

GlobCurrent's total current already carries about 0.6-0.75 % of the 10 m wind more than GLORYS12 (audit: 0.74 % U10,
12 deg left of downwind). Both products here use the same windage prior, c ~ U(0, 5 %) of ERA5 U10. Under a
product-relative prior the object's wind response relative to GlobCurrent is c_GC = c - dc, with c ~ U(0, 5 %).
The release tables hold windage nodes 0-5 % in 0.25 % steps, so the prior becomes node weights:
  w_k = P(c - dc in node k's cell), and the mass with c < dc goes to node 0 (zero added windage; declared clamp).
GLORYS12 is unchanged.

The surfaces are recomputed from the release tables with the module's own formula (checked against the exported
surfaces when dc = 0), then applied to a branch's flight-posterior maps as in branch_eof289.py.

    python windage_relative.py <runs/pleiades> <module dir> <branch root> <out dir> [--pfamily ...] [--options ...]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from branch_figure import hdr_level  # noqa: E402
from describe import describe_option  # noqa: E402
from option_closeups import load_mixture  # noqa: E402

KM_DEG = 111.195
T_IMP = 1394238300.0
SCENE = {"PHR_4": 1395548640.0, "PHR_2": 1395548640.0, "PHR_1": 1395548880.0, "PHR_3": 1395548880.0}
FITS = [((0.1153, 0.1176), (6.13, 4.20)), ((0.1043, 0.0955), (16.02, 7.64))]
TABLES = ["release-grid", "release-grid-globcurrent-p1d"]


def ou_var_km2(mi, dt):
    se, te = FITS[mi]
    return np.array([2 * s * s * (T * 86400) * (dt - T * 86400 * (1 - np.exp(-dt / (T * 86400)))) / 1e6 + 0.25 for s, T in zip(se, te)])


def node_weights(dc, n=21, step=0.0025):
    """The module's own prior is equal weight 1/n on windage nodes c_j = j*step (0-5 %). Product-relative: each node's
    weight moves to c_j - dc, split linearly between the two neighbouring nodes; anything below 0 goes to node 0
    (declared clamp). dc = 0 gives back the module's prior exactly."""
    w = np.zeros(n)
    for j in range(n):
        x = max(j - dc / step, 0.0)
        k = int(np.floor(x)); f = x - k
        w[k] += (1 - f) / n
        if f > 0:
            w[k + 1] += f / n
    return w


def endpoints(a, ti, LON, LAT):
    x = (LON - 85) / 0.1; y = (LAT + 43) / 0.1
    i = np.floor(x).astype(int); j = np.floor(y).astype(int)
    ok = (i >= 0) & (j >= 0) & (i + 1 < a.shape[1]) & (j + 1 < a.shape[0])
    i = np.clip(i, 0, a.shape[1] - 2); j = np.clip(j, 0, a.shape[0] - 2); fx = x - i; fy = y - j
    out = np.zeros(LAT.shape + (a.shape[2], 2))
    for dj, wy in ((0, 1 - fy), (1, fy)):
        for di, wx in ((0, 1 - fx), (1, fx)):
            out += (wx * wy)[..., None, None] * a[j + dj, i + di, :, ti, :]
    out[~ok] = np.nan
    return out


def gauss(X, y, v):
    de = (y[0] - X[..., 0]) * KM_DEG * np.cos(np.radians((y[1] + X[..., 1]) / 2)); dn = (y[1] - X[..., 1]) * KM_DEG
    return np.exp(-0.5 * (de ** 2 / v[0] + dn ** 2 / v[1])) / (2 * np.pi * np.sqrt(v[0] * v[1]))


def surfaces(runs, M, lat, lon, wk_by_model):
    """L_P and L_C4 (pass-marginalised), per model, on the branch grid, with windage node weights per model."""
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    out = []
    for mi, name in enumerate(TABLES):
        m = json.loads((runs / f"{name}.json").read_text())
        a = np.fromfile(runs / f"{name}.f32", dtype="<f4").reshape(m["nlat"], m["nlon"], m["windage_n"], len(m["out_unix_s"]), 2)
        outs = m["out_unix_s"]; wk = wk_by_model[mi]
        EP = {ti: endpoints(a, ti, LON, LAT) for ti in range(4)}
        LP = 0.0
        for _, r in T5.iterrows():
            ti = 2 if SCENE[r.scene] == outs[2] else 3
            LP = LP + r.w_equal * 500 * (gauss(EP[ti], (r.lon, r.lat), ou_var_km2(mi, SCENE[r.scene] - T_IMP)) * wk).sum(-1)
        LC = 0.0
        for ps in (0, 1):
            v = ou_var_km2(mi, outs[ps] - T_IMP)
            for _, r in Cc.iterrows():
                LC = LC + 0.5 * 0.25 * 500 * (gauss(EP[ps], (r.longitude, r.latitude), v) * wk).sum(-1)
        out.append((LP, LC))
    return out


def summarise(m, area, LAT, LON):
    m = m / m.sum(); dn = m / area
    return dict(hdr50_km2=float(area[dn >= hdr_level(dn, m, 0.5)].sum()), hdr90_km2=float(area[dn >= hdr_level(dn, m, 0.9)].sum()),
                mean_lat=float((m * LAT).sum()), mean_lon=float((m * LON).sum()))


def main(runs, module_dir, root, out, pfam, options):
    runs, M, out = Path(runs), Path(module_dir), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    Z0 = load_mixture(root, options[0], "base", pfam)
    lat, lon, area = Z0["lat"], Z0["lon"], Z0["area"]
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    uni = node_weights(0.0)
    base = surfaces(runs, M, lat, lon, [uni, uni])
    # check against the exported (branch) surface: same up to a constant
    ref = np.nan_to_num(Z0["L_P+C4"]); mine = 0.5 * (base[0][0] * base[0][1] + base[1][0] * base[1][1])
    ok = (ref > 0) & np.isfinite(mine) & (mine > 0)
    chk = float(np.std(np.log(mine[ok]) - np.log(ref[ok])))
    variants = {"same windage (as run)": base}
    for dc in (0.006, 0.0075):
        variants[f"GlobCurrent windage lowered {100 * dc:.2f} % (product-relative)"] = surfaces(runs, M, lat, lon, [uni, node_weights(dc)])
    rows = []
    for opt in options:
        for v in ("base", "oi2018-2025"):
            Z = load_mixture(root, opt, v, pfam)
            for name, S in variants.items():
                for which, L in (("GLORYS12 + GlobCurrent, equal weight", 0.5 * (S[0][0] * S[0][1] + S[1][0] * S[1][1])),
                                 ("GlobCurrent only", S[1][0] * S[1][1])):
                    r = summarise(np.nan_to_num(Z["post"] * L), area, LAT, LON)
                    rows.append(dict(option=describe_option(opt, short=True), search=v, windage=name, models=which, **{k: round(x, 3) for k, x in r.items()}))
    T = pd.DataFrame(rows)
    T.to_csv(out / "windage-relative.csv", index=False)
    (out / "windage-relative.json").write_text(json.dumps(dict(check_sd_lnratio_vs_branch=chk, node_weights={str(d): node_weights(d).round(4).tolist() for d in (0, 0.006, 0.0075)}), indent=1))
    return T, chk


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a_ in ("runs", "module", "root", "out"):
        ap.add_argument(a_)
    ap.add_argument("--pfamily", default=""); ap.add_argument("--options", default="none+alive")
    a = ap.parse_args()
    pf = {k: float(v) for k, v in (x.split("=") for x in a.pfamily.split(",") if x)} or None
    T, chk = main(a.runs, a.module, a.root, a.out, pf, a.options.split(","))
    print("check sd(ln ratio) vs branch surface:", chk)
    print(T.to_string(index=False))
