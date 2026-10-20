"""Architecture stand-in for the Pléiades module (hydroacoustic test of the Pléiades hypothesis, architecture.md
~20:00 / ~20:10 UTC 10 Oct 2026). Builds, on end of flight's core (b) impacts:

  1. <out>/<stratum>/seed-<k>/pleiades-lnL.npy  per-impact ln L columns, row-aligned with impacts.npy
  2. <out>/sources*.npz                         defensive-mixture source package per 00:19 option
  3. <work>/summary.json                        ESS, per-family 00:19 evidence factors, reproduction check

    python build_columns.py <impacts root> <pleiades clone root> <surface dir> <out root> <work dir>

The Pléiades likelihood is the module's own: its hook's surfaces exported on the 0.05 deg grid
(lib.rs pleiades_export_likelihood_surface / pleiades_export_cosmo_surface), read and combined with
branch_eof289.load_fields / build_branch, and each impact is given the value of the grid cell it falls in, with the
same bin edges branch_eof289.histograms uses. That IS how the module scores end-of-flight impacts (it never evaluates
the likelihood at an exact impact position). Weights per 00:19 option are the module's (branch_eof289: EoF's
option_posteriors for derived options, impact weight x exp(loglik) x EoF's constraint factor otherwise).
Nothing in the module or in end of flight's code is modified; both are imported read-only.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

IMP, CLONE, SURF, OUT, WORK = map(Path, sys.argv[1:6])
PREP = CLONE / "Claude Science Project Sep 29" / "engine" / "hypotheses" / "pleiades" / "prepare"
sys.path.insert(0, str(PREP))
import branch_eof289 as B  # noqa: E402  (module code, read-only)

STRATA = ["next-descent-climb", "next-free", "next-repro-radar", "next-routes"]   # stratum code = index
PFAM = json.loads((IMP / "summary" / "mixture.json").read_text())["p_family"]       # core (b), fixed
OPTIONS = {"r600-bto+alive": "00:19 R600 BTO Only", "none+alive": "00:19 Held Out",
           "r600/no-offset+alive": "00:19 R600 BTO + Raw BFO"}
SLUG = {"r600-bto+alive": "0019-r600-bto-only", "none+alive": "0019-held-out", "r600/no-offset+alive": "0019-r600-bto-raw-bfo"}
N_SOURCES, RNG_SEED = 5000, 20261012
VALS = [f"lnL_{f}_{m}" for f in ("pleiades", "cosmo", "both") for m in ("glorys12", "globcurrent", "mean")]
DT = np.dtype([("stratum", "u1"), ("seed", "u1"), ("row", "<u4"), ("parent", "<i8")] + [(v, "<f4") for v in VALS]
              + [("not_computed", "u1")])
WORK.mkdir(parents=True, exist_ok=True)

mp, models, P, Cm = B.load_fields(SURF)
assert mp["object_rating"][0] == "rho4-0", mp["object_rating"]          # rating-5 objects, 6 clusters
MKEY = {"glorys12": [i for i, m in enumerate(models) if m.startswith("glorys12")][0],
        "globcurrent": [i for i, m in enumerate(models) if m.startswith("globcurrent")][0]}
# per model: P = Pleiades (rating 5, equal cluster weights); C = all four COSMO contacts (C4, pass-marginal)
LP = {k: P[i, 0, 0] for k, i in MKEY.items()}
LC = {k: Cm[i, 1] for k, i in MKEY.items()}
lon0, lat0, nlat, nlon = mp["lon0"], mp["lat0"], int(mp["nlat"]), int(mp["nlon"])
elon = lon0 - B.STEP / 2 + B.STEP * np.arange(nlon + 1)
elat = lat0 - B.STEP / 2 + B.STEP * np.arange(nlat + 1)
GRID_L = B.build_branch(models, P, Cm, 0, 0)        # the module's own grid fields (for the reproduction check)


def cell_index(x, edges, n):
    """np.histogram2d's binning (searchsorted right, last edge inclusive); -1 outside."""
    i = np.searchsorted(edges, x, side="right") - 1
    i = np.where(x == edges[-1], n - 1, i)
    return np.where(np.isfinite(x) & (i >= 0) & (i < n), i, -1)


def lme2(a, b):
    """log of the equal-weight mean of exp(a), exp(b) (NaN if either is NaN)."""
    m = np.maximum(a, b)
    return m + np.log(0.5 * (np.exp(a - m) + np.exp(b - m)))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 24), b""):
            h.update(blk)
    return h.hexdigest()


def columns(sd, scode, k):
    out = OUT / sd.parent.name / sd.name
    f = out / "pleiades-lnL.npy"
    if f.exists():
        return np.load(f, mmap_mode="r")
    out.mkdir(parents=True, exist_ok=True)
    cols = [l.split("\t")[1] for l in (sd / "COLUMNS.txt").read_text().splitlines()]
    A = np.load(sd / "impacts.npy", mmap_mode="r")
    n = A.shape[0]
    lat = np.asarray(A[:, cols.index("latitude_deg")], float)
    lon = np.asarray(A[:, cols.index("longitude_deg")], float)
    par = np.asarray(A[:, cols.index("parent")], float)
    assert np.all(par == np.round(par)) and par.min() >= 0
    iy, ix = cell_index(lat, elat, nlat), cell_index(lon, elon, nlon)
    inside = (iy >= 0) & (ix >= 0)
    iy0, ix0 = np.where(inside, iy, 0), np.where(inside, ix, 0)
    R = np.zeros(n, DT)
    R["stratum"], R["seed"], R["row"], R["parent"] = scode, k, np.arange(n, dtype=np.uint32), par.astype(np.int64)
    v = {}
    for m in ("glorys12", "globcurrent"):
        v[f"lnL_pleiades_{m}"] = np.where(inside, LP[m][iy0, ix0], np.nan)
        v[f"lnL_cosmo_{m}"] = np.where(inside, LC[m][iy0, ix0], np.nan)
        v[f"lnL_both_{m}"] = v[f"lnL_pleiades_{m}"] + v[f"lnL_cosmo_{m}"]    # one ocean drives both (per model)
    for fld in ("pleiades", "cosmo", "both"):
        v[f"lnL_{fld}_mean"] = lme2(v[f"lnL_{fld}_glorys12"], v[f"lnL_{fld}_globcurrent"])
    nc = ~np.all(np.isfinite(np.stack([v[x] for x in VALS])), axis=0)
    for x in VALS:
        R[x] = np.where(nc, np.nan, v[x]).astype(np.float32)
    R["not_computed"] = nc.astype(np.uint8)
    tmp = out / "pleiades-lnL.npy.partial.npy"
    np.save(tmp, R)
    tmp.rename(f)
    (out / "COLUMNS.txt").write_text("".join(f"{i}\t{name}\t{DT[name].str}\n" for i, name in enumerate(DT.names)))
    (out / "SHA256SUMS").write_text(f"{sha(f)}  pleiades-lnL.npy\n")
    return np.load(f, mmap_mode="r")


def option_weights(sd, option):
    """branch_eof289.histograms' weight branch, verbatim in logic, normalised per seed."""
    cols = [l.split("\t")[1] for l in (sd / "COLUMNS.txt").read_text().splitlines()]
    A = np.load(sd / "impacts.npy", mmap_mode="r")
    opt_, _, cause = option.partition("@")
    base, _, con = opt_.partition("+")
    if (cause and cause != "other") or f"loglik:{base}" not in cols:
        w = B.eof_option_weights(sd, base, cause or "other", con)
    else:
        w = np.asarray(A[:, cols.index("weight")]) * np.exp(np.asarray(A[:, cols.index(f"loglik:{base}")]))
        if con:
            w = w * np.exp(B.eof_constraint(sd, A, cols, con))
    w = np.where(np.isfinite(w), w, 0.0)
    return w / w.sum()


def evidence_factor(sd, option):
    """ln Z_00:19 for one seed: ln [ sum_i weight_i exp(ll_i) / sum_i weight_i ], ll = the option's 00:19
    log-likelihood (stored or EoF-derived) + EoF's existence-constraint factor, both from EoF's own code."""
    E = B._eof_module()
    meta = json.loads((sd / "run.json").read_text())
    cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r")
    g = lambda k: np.asarray(X[:, cols[k]], float)
    base, _, con = option.partition("+")
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    ll = g("loglik:" + base) if base in present else E.derived_logliks(meta, g, present)[base]
    ll = np.where(np.isfinite(ll), ll, -np.inf)
    c = E.constraint_log_factor(g, meta["config"]["hypotheses"]["end-of-flight"]["logon"], "other", con) if con else np.zeros_like(ll)
    lla = ll + c
    w = g("weight")
    def lz(x):
        mx = x[np.isfinite(x)].max()
        return float(mx + np.log((w * np.exp(x - mx)).sum() / w.sum()))
    return dict(ln_Z=lz(lla), ln_Z_data_only=lz(ll),
                ln_Z_constraint_only=lz(c))


def ess(x):
    return float(x.sum() ** 2 / (x ** 2).sum()) if x.sum() > 0 else 0.0


def ess_parents(x, par):
    u, inv = np.unique(par, return_inverse=True)
    return ess(np.bincount(inv, weights=x))


# ---------------------------------------------------------------- pass 1: columns, weights, ESS, factors, maps
summary = dict(per_seed=[], options=OPTIONS, p_family_fixed=PFAM, surfaces=str(SURF), models=models)
pw = {o: {} for o in OPTIONS}                       # (stratum, seed) -> normalised flight weights (float64)
maps = {}                                           # (option, stratum) -> lists of per-seed histograms
for s in STRATA:
    for sd in sorted((IMP / s).glob("seed-*")):
        k = int(sd.name.split("-")[1])
        R = columns(sd, STRATA.index(s), k)
        nc = R["not_computed"].astype(bool)
        L = {f: np.where(nc, 0.0, np.exp(np.asarray(R[f"lnL_{f}_mean"], float))) for f in ("pleiades", "cosmo", "both")}
        cols = [l.split("\t")[1] for l in (sd / "COLUMNS.txt").read_text().splitlines()]
        A = np.load(sd / "impacts.npy", mmap_mode="r")
        lat = np.asarray(A[:, cols.index("latitude_deg")], float)
        lon = np.asarray(A[:, cols.index("longitude_deg")], float)
        par = np.asarray(R["parent"])
        for o in OPTIONS:
            p = option_weights(sd, o)
            pw[o][(s, k)] = p.astype(np.float32)
            wH = p * L["both"]
            z = evidence_factor(sd, o)
            rec = dict(stratum=s, seed=k, option=o, rows=int(len(p)), rows_not_computed=int(nc.sum()),
                       flight_weight_not_computed=float(p[nc].sum()), ess_flight=ess(p), ess_H=ess(wH),
                       ess_parents_flight=ess_parents(p, par), ess_parents_H=ess_parents(wH, par),
                       mean_L_both_under_flight=float(wH.sum()), **z)
            summary["per_seed"].append(rec)
            print(json.dumps(rec), flush=True)
            h = {"pre": np.histogram2d(lat, lon, bins=[elat, elon], weights=p)[0]}
            for f in ("pleiades", "cosmo", "both"):
                h[f] = np.histogram2d(lat, lon, bins=[elat, elon], weights=p * L[f])[0]
            maps.setdefault((o, s), []).append(h)
        del A, R

# ---------------------------------------------------------------- reproduction check (module's own summarise)
lat_c, lon_c = 0.5 * (elat[1:] + elat[:-1]), 0.5 * (elon[1:] + elon[:-1])
LAT, LON = np.meshgrid(lat_c, lon_c, indexing="ij")
area = B.area_km2(LAT)
dummy = np.zeros_like(area, bool)
FIELD = {"pleiades": "P", "cosmo": "C4", "both": "P+C4"}
repro = []
mix_maps = {}
for (o, s), hs in maps.items():
    pre = np.mean([h["pre"] for h in hs], axis=0)
    for f, fm in FIELD.items():
        a = B.summarise(pre, GRID_L[fm]["both models"], area, lat_c, lon_c, dummy, dummy, dummy)   # module path
        cpost = np.mean([h[f] for h in hs], axis=0)
        b = B.summarise(cpost, np.ones_like(area), area, lat_c, lon_c, dummy, dummy, dummy)          # columns path
        repro.append(dict(option=o, stratum=s, field=fm, module_hdr90_km2=a["cond_hdr90_km2"],
                          columns_hdr90_km2=b["cond_hdr90_km2"], module_mean_lat=a["cond_mean_lat"],
                          columns_mean_lat=b["cond_mean_lat"], module_mean_lon=a["cond_mean_lon"],
                          columns_mean_lon=b["cond_mean_lon"], uncond_hdr90_km2=a["uncond_hdr90_km2"]))
        mix_maps.setdefault((o, f), []).append((s, pre, cpost))
summary["reproduction"] = repro

# ---------------------------------------------------------------- strata weights (fixed and 00:19-re-weighted)
zf = {}
for o in OPTIONS:
    zf[o] = {}
    for s in STRATA:
        lz = np.array([r["ln_Z"] for r in summary["per_seed"] if r["option"] == o and r["stratum"] == s])
        Z = np.exp(lz - lz.max())
        zf[o][s] = dict(ln_Zhat=float(lz.max() + np.log(Z.mean())), ln_Zhat_se=float(Z.std(ddof=1) / math.sqrt(len(Z)) / Z.mean()),
                        ln_Z_seeds=lz.tolist())
    lm = max(v["ln_Zhat"] for v in zf[o].values())
    un = {s: PFAM[s] * math.exp(zf[o][s]["ln_Zhat"] - lm) for s in STRATA}
    tot = sum(un.values())
    for s in STRATA:
        zf[o][s]["p_family_reweighted"] = un[s] / tot
        zf[o][s]["p_family_fixed"] = PFAM[s]
summary["strata_weights"] = zf

mix = []
for (o, f), lst in mix_maps.items():
    for kind in ("fixed", "reweighted"):
        pf = {s: zf[o][s][f"p_family_{kind}"] for s in STRATA}
        pre = sum(pf[s] * a for s, a, _ in lst)
        cpost = sum(pf[s] * c for s, _, c in lst)
        b = B.summarise(cpost, np.ones_like(area), area, lat_c, lon_c, dummy, dummy, dummy)
        a = B.summarise(pre, np.ones_like(area), area, lat_c, lon_c, dummy, dummy, dummy)
        mix.append(dict(option=o, field=FIELD[f], strata=kind, hdr90_km2_under_H=b["cond_hdr90_km2"],
                        mean_lat_under_H=b["cond_mean_lat"], mean_lon_under_H=b["cond_mean_lon"],
                        hdr90_km2_flight=a["cond_hdr90_km2"], mean_lat_flight=a["cond_mean_lat"], mean_lon_flight=a["cond_mean_lon"]))
summary["mixture_before_search"] = mix

# ---------------------------------------------------------------- source packages (defensive mixture)
for o in OPTIONS:
    rng = np.random.default_rng(RNG_SEED)
    keys = [(s, k) for s in STRATA for k in sorted(kk for ss, kk in pw[o] if ss == s)]
    nseed = {s: sum(1 for ss, _ in keys if ss == s) for s in STRATA}
    pf = {kind: {s: zf[o][s][f"p_family_{kind}"] for s in STRATA} for kind in ("fixed", "reweighted")}
    Lb = {}
    mH = {kind: {} for kind in pf}
    for key in keys:
        R = np.load(OUT / key[0] / f"seed-{key[1]}" / "pleiades-lnL.npy", mmap_mode="r")
        Lb[key] = np.where(R["not_computed"].astype(bool), 0.0, np.exp(np.asarray(R["lnL_both_mean"], float)))
        for kind in pf:
            mH[kind][key] = pf[kind][key[0]] / nseed[key[0]] * float((pw[o][key] * Lb[key]).sum())
    ZH = {kind: sum(mH[kind].values()) for kind in pf}
    # draw with the re-weighted strata (primary); half from the flight posterior, half from the posterior under H
    nh = N_SOURCES // 2
    mF = np.array([pf["reweighted"][s] / nseed[s] for s, _ in keys])
    cF = rng.multinomial(nh, mF / mF.sum())
    cH = rng.multinomial(N_SOURCES - nh, np.array([mH["reweighted"][k] for k in keys]) / ZH["reweighted"])
    rows = []
    for j, key in enumerate(keys):
        p = pw[o][key].astype(float)
        for comp, cnt, prob in ((0, cF[j], p), (1, cH[j], p * Lb[key])):
            if cnt:
                idx = rng.choice(len(p), size=cnt, replace=True, p=prob / prob.sum())
                rows += [(STRATA.index(key[0]), key[1], int(i), comp) for i in idx]
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    st, sk, ri, comp = (np.array(x) for x in zip(*rows))
    qF = {kind: np.empty(len(ri)) for kind in pf}
    qH = {kind: np.empty(len(ri)) for kind in pf}
    lnl = {x: np.empty(len(ri), np.float32) for x in VALS}
    ncs = np.empty(len(ri), np.uint8)
    state, parent = None, np.empty(len(ri), np.int64)
    for key in keys:
        sel = np.where((st == STRATA.index(key[0])) & (sk == key[1]))[0]
        if not len(sel):
            continue
        i = ri[sel]
        sdir = IMP / key[0] / f"seed-{key[1]}"
        A = np.load(sdir / "impacts.npy", mmap_mode="r")
        if state is None:
            state = np.empty((len(ri), A.shape[1]))
            state_cols = [l.split("\t")[1] for l in (sdir / "COLUMNS.txt").read_text().splitlines()]
        assert np.all(np.diff(i) >= 0)
        state[sel] = A[i]
        R = np.load(OUT / key[0] / f"seed-{key[1]}" / "pleiades-lnL.npy", mmap_mode="r")
        r = R[i]
        assert np.all(r["row"] == i) and np.all(r["parent"] == state[sel, state_cols.index("parent")])
        parent[sel] = r["parent"]
        for x in VALS:
            lnl[x][sel] = r[x]
        ncs[sel] = r["not_computed"]
        for kind in pf:
            qF[kind][sel] = pf[kind][key[0]] / nseed[key[0]] * pw[o][key][i]
            qH[kind][sel] = qF[kind][sel] * Lb[key][i] / ZH[kind]
    qM = 0.5 * qF["reweighted"] + 0.5 * qH["reweighted"]
    W = {}
    for kind in pf:
        sfx = "" if kind == "reweighted" else "_fixed"
        W[f"w_flight{sfx}"], W[f"w_H{sfx}"] = qF[kind] / qM, qH[kind] / qM
    E = {f"ess_{k}": ess(v) for k, v in W.items()}
    rec = dict(option=o, option_name=OPTIONS[o], n=len(ri), n_from_flight=int((comp == 0).sum()), n_from_H=int((comp == 1).sum()),
               unique_rows=int(len(set(zip(st.tolist(), sk.tolist(), ri.tolist())))), **E)
    summary.setdefault("sources", []).append(rec)
    print(json.dumps(rec), flush=True)
    payload = dict(stratum=st.astype(np.uint8), stratum_names=np.array(STRATA), seed=sk.astype(np.uint8),
                   row=ri.astype(np.uint32), parent=parent, component=comp.astype(np.uint8), state=state,
                   state_columns=np.array(state_cols), q_mixture=qM, not_computed=ncs, **W,
                   **{k: np.float64(v) for k, v in E.items()}, **lnl,
                   p_family_reweighted=np.array([pf["reweighted"][s] for s in STRATA]),
                   p_family_fixed=np.array([pf["fixed"][s] for s in STRATA]),
                   option=np.array(o), option_name=np.array(OPTIONS[o]), rng_seed=np.int64(RNG_SEED))
    names = [f"sources-{SLUG[o]}.npz"] + (["sources.npz"] if o == "r600-bto+alive" else [])
    for nm in names:
        np.savez(OUT / (nm + ".partial.npz"), **payload)
        (OUT / (nm + ".partial.npz")).rename(OUT / nm)

(WORK / "summary.json").write_text(json.dumps(summary, indent=1))
print("done")
