#!/usr/bin/env python3
"""Searched areas on the run J northern supplement, rule B (work order overnight-2026-10-20 B3).

    python score_supplement.py arcgrid <out>          7th-arc distance grid (binned from end-of-flight rows that carry arc_distance_nm)
    python score_supplement.py reduced <out>          impact point, every row of end of flight's reduced rule-B table
    python score_supplement.py strata  <out> [nproc]  impact point, every row of the A1 strata passes (branch 1: run-j-a1branch +
                                                      north-k2-a1branch; branch 2: run-j-a1outside), masses as settling's wf_supp_a1
    python score_supplement.py settled <out>          settled positions, settling run-j-supplement ruleB-waypoints and a1-stratified
    (reduction: reduce_supplement.py)

Inputs (read only): end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz (rule B, all rows, lnw:comb/<d> and lnw:alone/<d>);
the strata passes; settling/run-j-supplement/{ruleB-waypoints, a1-stratified}; searched-areas/spatial-fields/fields.npz.
P(no find): run.toml base (base_guard.check(), four campaigns, rho 0.05) with the rho sweep and without-OI sensitivity, and the
per-cell field V1 central / V2 pessimistic / V3 optimistic (spatial/score_spatial_run_j.py Lookup and VARIANTS unchanged;
V0_scalar equals the base exactly). Settled: 'mean' field, row likelihood = MEAN over the row's settling draws (alternative
outcomes are averaged, never multiplied).
A1 = end of flight's two conditional strata (results/eof-run-j-supplement-oct20 section 3), row masses from settling's
wf_supp_a1 (raw_masses x exp(lnZ_D0 - lnZ_d) P_b / S_b), in the reduced table's normalised units; reduced-table rows inside branch 1
or inside (branch 2 and A1) are replaced by the strata. Totals: end of flight's convention (eof-convention-weights.json: rest rows
x s_d) and settling's single measure, both reported.
"""
import hashlib, json, math, os, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MOD = HERE.parent
sys.path.insert(0, str(MOD)); sys.path.insert(0, str(MOD / "spatial"))
import base_guard  # noqa: E402

X = pathlib.Path(os.environ.get("MH370_EXCHANGE", "/Users/pete/Downloads/mh370-exchange"))
WK = pathlib.Path(os.environ.get("SETTLING_WORK", "/Users/pete/Downloads/mh370-settling-work-j"))
SUPP = X / "end-of-flight/run-j-supplement"
RED = SUPP / "reduced/impacts-ruleB.npz"
SETT = X / "settling/run-j-supplement"
FIELDS = X / "searched-areas/spatial-fields/fields.npz"
PUB_A1 = X / "searched-areas/run-j-a1branch/pass"
STRATA = {"b1p": X / "end-of-flight/run-j-a1branch/run-j-waypoints", "b1s": SUPP / "north-k2-a1branch", "b2": SUPP / "run-j-a1outside"}
CELLS = ["D0", "D1", "D2", "D3", "D4", "D5", "D3s", "D4s", "D5s"]
LAYERS = {"phase2-2014-2017": 0.945, "bluefin-2014": 0.9, "ocean-infinity-2018": 0.9 * 0.889, "ocean-infinity-2025": 0.9 * 0.7808}
CK = {"phase2-2014-2017": "c01_p2", "bluefin-2014": "c01_bf", "ocean-infinity-2018": "c01_oi2018", "ocean-infinity-2025": "c01_oi2025"}
ATSB = ["phase2-2014-2017", "bluefin-2014"]
SCEN = {"base_rho0.05": (list(LAYERS), 0.05), "base_rho0": (list(LAYERS), 0.0), "base_rho0.25": (list(LAYERS), 0.25),
        "base_rho0.5": (list(LAYERS), 0.5), "without_oi_rho0.05": (ATSB, 0.05)}
VSEL = ["V1_central", "V2_pessimistic", "V3_optimistic"]
EVALS = list(SCEN) + VSEL
BANDS = {"35-30S": (-35.0, -30.0), "30-25S": (-30.0, -25.0), "25-20S": (-25.0, -20.0), "north33S": (-33.0, 0.0), "north30S": (-30.0, 0.0)}
_L = {}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
    return h.hexdigest()


def verify(d, names):
    want = {}
    for l in (d / "SHA256SUMS").read_text().splitlines():
        if l.strip():
            h, n = l.split(None, 1); want[n.strip().lstrip("*").removeprefix("./")] = h
    for n in names:
        if want.get(n) != sha(d / n): sys.exit(f"SHA256 mismatch {d / n}")


def p_scalar(S, names, rho):
    m = np.ones(len(S["c01_p2"]))
    for n in names: m = m * (1.0 - S[CK[n]] * LAYERS[n])
    return rho + (1.0 - rho) * m


def evaluate(S):
    """P(no find) and the searched fraction (before evidence) for every evaluation, from per-point (or field-mean) lookups S."""
    from score_spatial_run_j import variant_P
    P, SF = {}, {}
    p0, sf0 = variant_P(S, "V0_scalar")
    for s, (nm, r) in SCEN.items():
        P[s] = p_scalar(S, nm, r); SF[s] = sf0
    assert np.abs(P["base_rho0.05"] - p0).max() < 1e-15
    for v in VSEL: P[v], SF[v] = variant_P(S, v)
    return P, SF


def lookup(lat, lon, chunk=2_000_000):
    from score_spatial_run_j import Lookup
    if "L" not in _L: _L["L"] = Lookup(FIELDS)
    L = _L["L"]
    V = np.vstack([L(lat[i:i + chunk], lon[i:i + chunk]) for i in range(0, len(lat), chunk)])
    return {n: V[:, j] for j, n in enumerate(L.names)}


# ------------------------------------------------------------------ 7th-arc distance grid
GRID = dict(south=-45.0, west=75.0, step=0.02, rows=1750, cols=1750)


def _rows(d):
    I = np.load(d / "impacts32.npy", mmap_mode="r")
    return np.asarray(I[:, 7], float), np.asarray(I[:, 8], float), np.asarray(I[:, 9], float)


def arcgrid(out):
    """Mean arc_distance_nm per 0.02 deg cell from end-of-flight rows that carry it; validated on held-out seeds."""
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    G = GRID; S = np.zeros((G["rows"], G["cols"])); N = np.zeros_like(S)
    train = [X / "end-of-flight/run-j/run-j-waypoints/seed-1", X / "end-of-flight/run-j/run-j-waypoints/seed-3", SUPP / "north-k2/seed-1001",
             SUPP / "north-k2/seed-1003", SUPP / "north-k2b/seed-1005", STRATA["b2"] / "seed-1"]
    for d in train:
        la, lo, a = _rows(d)
        i = np.floor((la - G["south"]) / G["step"]).astype(int); j = np.floor((lo - G["west"]) / G["step"]).astype(int)
        ok = (i >= 0) & (i < G["rows"]) & (j >= 0) & (j < G["cols"])
        np.add.at(S, (i[ok], j[ok]), a[ok]); np.add.at(N, (i[ok], j[ok]), 1)
    A = np.where(N > 0, S / np.maximum(N, 1), np.nan)
    from scipy import ndimage
    idx = ndimage.distance_transform_edt(np.isnan(A), return_distances=False, return_indices=True)
    A = A[tuple(idx)]
    np.savez(out / "arc-grid.npz", arc=A.astype(np.float32), n=N.astype(np.int32), **{k: v for k, v in G.items()})
    chk = {"train": [str(d.relative_to(X)) for d in train]}
    for d in (X / "end-of-flight/run-j/run-j-waypoints/seed-2", SUPP / "north-k2b/seed-1002"):
        la, lo, a = _rows(d); e = arc_at(la, lo, out) - a
        chk[str(d.relative_to(X))] = {"rows": int(len(a)), "abs_err_p50_nm": float(np.median(np.abs(e))), "abs_err_p99_nm": float(np.quantile(np.abs(e), 0.99)),
                                     "flag_25NM_disagree_fraction": float(((np.abs(a) > 25) != (np.abs(a + e) > 25)).mean())}
    (out / "arc-grid-check.json").write_text(json.dumps(chk, indent=1)); print(json.dumps(chk))


def arc_at(lat, lon, out):
    if "arc" not in _L: _L["arc"] = np.load(pathlib.Path(out) / "arc-grid.npz")
    z = _L["arc"]
    from score_spatial_run_j import bilin
    return bilin(z["arc"].astype(np.float64), float(z["south"]), float(z["west"]), float(z["step"]), lat, lon)


# ------------------------------------------------------------------ sums
def band_masks(lat):
    return {b: (lat > lo) & (lat <= hi) for b, (lo, hi) in BANDS.items()}


def sums(m, P, SF, bm, n25, glide, state, group=None, ngroup=0):
    """m: row mass; P, SF: eval -> arrays; bm: band masks; state: int ids (paths: distinct hand-off rows per replicate; end of flight's 'distinct states' merge duplicate states and are <= paths); group: replicate ids."""
    r = {"m": float(m.sum()), "m2": float((m * m).sum()), "s2": float((np.bincount(state, m) ** 2).sum()), "bands": {}}
    for b, k in bm.items():
        mb = np.where(k, m, 0.0)
        r["bands"][b] = {"m": float(mb.sum()), "m2": float((mb * mb).sum()), "s2": float((np.bincount(state, mb) ** 2).sum())}
    for e in EVALS:
        p, sf = P[e], SF[e]; mp = m * p; rest = 1.0 - sf
        cats = {"searched": sf, "north_of_25S": rest * n25, "beyond_25NM": rest * (~n25) * glide, "near_arc_unsearched": rest * (~n25) * (~glide)}
        q = {"mP": float(mp.sum()), "mP2": float((mp * mp).sum()), "s2": float((np.bincount(state, mp) ** 2).sum()),
             "split_before": {c: float((m * x).sum()) for c, x in cats.items()}, "split_after": {c: float((mp * x).sum()) for c, x in cats.items()}, "bands": {}}
        for b, k in bm.items():
            mb = np.where(k, mp, 0.0)
            q["bands"][b] = {"mP": float(mb.sum()), "mP2": float((mb * mb).sum()), "s2": float((np.bincount(state, mb) ** 2).sum())}
        if group is not None and e in ("base_rho0.05", "V1_central"):
            q["groups"] = {"mP": np.bincount(group, mp, ngroup).tolist(), "m": np.bincount(group, m, ngroup).tolist(),
                           "bands_mP": {b: np.bincount(group, np.where(k, mp, 0.0), ngroup).tolist() for b, k in bm.items()},
                           "bands_m": {b: np.bincount(group, np.where(k, m, 0.0), ngroup).tolist() for b, k in bm.items()}}
        r[e] = q
    return r


def labels_branch(om, cr, ra):
    return np.select([(om == 2) & (cr == 2), (om == 2) & (ra == 1)], [1, 2], 0)


# ------------------------------------------------------------------ reduced table
def reduced(out):
    label = base_guard.check(MOD / "run.toml")
    out = pathlib.Path(out); t0 = time.time()
    verify(SUPP, ["reduced/" + RED.name, "reduced/" + RED.with_suffix(".json").name])
    z = np.load(RED)
    lat = z["latitude_deg"].astype(np.float64); lon = z["longitude_deg"].astype(np.float64); n = len(lat)
    S = lookup(lat, lon); P, SF = evaluate(S)
    arc = arc_at(lat, lon, out); n25 = lat > -25.0; glide = np.abs(arc) > 25.0
    tech = z["technique"].astype(int); seed = z["seed"].astype(np.int64); hr = z["handoff_row"].astype(np.int64)
    sup = (tech > 0).astype(np.int64)
    state = np.unique(sup * 10**12 + seed * 10**8 + hr, return_inverse=True)[1]
    gu, group = np.unique(sup * 10000 + seed, return_inverse=True)
    f4 = z["family4_code"].astype(int)
    br = labels_branch(z["latent:onset_mechanism"].astype(int), z["latent:control_realised"].astype(int), z["latent:recovery_attempted"].astype(int))
    rest = ~((br == 1) | ((br == 2) & (f4 == 1)))
    subs = {"all": np.ones(n, bool), "A1": f4 == 1, "A2": f4 == 2, "B": np.isin(f4, (3, 6)), "rest": rest, "rest_A1": rest & (f4 == 1)}
    bm = band_masks(lat)
    res = {"label": label, "rows": n, "groups": [int(g) for g in gu], "technique_rows": np.bincount(tech).tolist(), "comb": {}, "alone": {}}
    for wt in ("comb", "alone"):
        for d in CELLS:
            a = z[f"lnw:{wt}/{d}"].astype(np.float64); m0 = np.where(np.isfinite(a), np.exp(a), 0.0)
            res[wt][d] = {}
            for k, mk in subs.items():
                if wt == "alone" and k.startswith("rest"): continue
                res[wt][d][k] = sums(np.where(mk, m0, 0.0), P, SF, bm, n25, glide, state, group, len(gu))
        print("reduced", wt, f"{time.time() - t0:.0f}s", flush=True)
    cols = {"lnL_base_rho0.05": np.log(P["base_rho0.05"])}
    cols.update({f"lnL_{e}": np.log(P[e]).astype(np.float32) for e in EVALS if e != "base_rho0.05"})
    cols["searched_fraction_base"] = SF["base_rho0.05"].astype(np.float32); cols["arc_distance_nm_interp"] = arc.astype(np.float32)
    np.savez(out / "reduced-impact-columns.part.npz", **cols); os.replace(out / "reduced-impact-columns.part.npz", out / "reduced-impact-columns.npz")
    res["checks"] = {"finite": bool(all(np.isfinite(v).all() for v in cols.values())), "wall_s": time.time() - t0}
    (out / "reduced_terms.json").write_text(json.dumps(res)); print(json.dumps(res["checks"]))


# ------------------------------------------------------------------ strata
def _ws():
    sys.path.insert(0, str(WK))
    import wf_supp_a1 as A
    p0 = json.loads((WK / "field/rjsa_pass0.json").read_text())
    A._C["N1"] = p0["N1_branch1_production"]; A._C["p0"] = p0
    return A, p0


def strata_seed(args):
    src, sd, out = args; sd = pathlib.Path(sd); out = pathlib.Path(out); t0 = time.time()
    A, p0 = _ws()
    from compact_impacts import load
    m_raw, R = A.raw_masses(src, sd)
    meta, g = load(sd)
    lat = g("latitude_deg").astype(np.float64); lon = g("longitude_deg").astype(np.float64); arc = g("arc_distance_nm").astype(np.float64)
    par = g("parent").astype(np.int64); f4 = R["f4"]; n = len(lat)
    S = lookup(lat, lon); P, SF = evaluate(S)
    chk = {"src": src, "seed": sd.name, "rows": n}
    if src == "b1p":
        q = np.load(PUB_A1 / sd.name / "seabed-lnL.npy")
        chk["max_abs_dlnL_vs_a8e819f_pass_column"] = float(np.abs(q - np.log(P["base_rho0.05"])).max())
        assert chk["max_abs_dlnL_vs_a8e819f_pass_column"] < 1e-9, chk
    o = out / "strata" / src / sd.name; o.mkdir(parents=True, exist_ok=True)
    np.save(o / "seabed-lnL.npy", np.log(P["base_rho0.05"]))
    for e in VSEL: np.save(o / f"seabed-lnL-{e}.npy", np.log(P[e]).astype(np.float32))
    (o / "SHA256SUMS").write_text("".join(f"{sha(x)}  {x.name}\n" for x in sorted(o.glob("*.npy"))))
    LNZ = A.LNZ; Pb = A.P2 if src == "b2" else A.P1; Sb = p0["S2_D0"] if src == "b2" else p0["S1_D0"]
    n25 = lat > -25.0; glide = np.abs(arc) > 25.0; bm = band_masks(lat)
    T = {}
    for d in CELLS:
        mm = m_raw[d] * (math.exp(LNZ["D0"] - LNZ[d]) * Pb / Sb)
        if src == "b2": mm = np.where(f4 == 1, mm, 0.0)
        T[d] = sums(mm, P, SF, bm, n25, glide, par)
    chk["wall_s"] = time.time() - t0
    return {"check": chk, "terms": T}


def strata(out, nproc=4):
    from multiprocessing import Pool
    base_guard.check(MOD / "run.toml")
    out = pathlib.Path(out)
    jobs = [(src, str(sd), str(out)) for src, root in STRATA.items()
            for sd in sorted((p for p in root.glob("seed-*") if p.is_dir()), key=lambda p: int(p.name.split("-")[1]))]
    res = []
    with Pool(int(nproc)) as pool:
        for r in pool.imap_unordered(strata_seed, jobs):
            res.append(r); print(json.dumps(r["check"]), flush=True)
    (out / "strata_terms.json").write_text(json.dumps({"seeds": res}))


# ------------------------------------------------------------------ settled
def settled(out):
    from score_spatial_run_j import STRIDE
    label = base_guard.check(MOD / "run.toml")
    out = pathlib.Path(out); t0 = time.time()
    conv = json.loads((SETT / "a1-stratified/eof-convention-weights.json").read_text())
    rc = np.load(out / "reduced-impact-columns.npz")
    zred = np.load(RED, mmap_mode="r"); lat_red = np.asarray(zred["latitude_deg"], np.float64)
    arc_red = rc["arc_distance_nm_interp"].astype(np.float64); lnl_red = rc["lnL_base_rho0.05"]
    summ = {"label": label, "sets": {}}
    for tag, d in (("rjs", "ruleB-waypoints"), ("rjsa", "a1-stratified")):
        sd = SETT / d
        verify(sd, [f"{tag}_impacts.f64", f"{tag}_elements.f64", f"{tag}_draws.npz", f"{tag}_source.npy", f"{tag}_info.json"])
        info = json.loads((sd / f"{tag}_info.json").read_text())
        imp = np.fromfile(sd / f"{tag}_impacts.f64", "<f8").reshape(-1, 14)
        el = np.memmap(sd / f"{tag}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8)
        src = np.load(sd / f"{tag}_source.npy"); dr = np.load(sd / f"{tag}_draws.npz")
        n_rows = imp.shape[0]; lat_i, lon_i = imp[:, 1].copy(), imp[:, 2].copy()
        ck = {"table_rows": int(n_rows), "elements": int(el.shape[0])}
        S_row = lookup(lat_i, lon_i); P_row, SF_row = evaluate(S_row)
        ref = np.full(n_rows, np.nan); arc = np.full(n_rows, np.nan)
        s0 = np.ones(n_rows, bool) if tag == "rjs" else (src[:, 0] == 0)
        ri = src[s0, 2]
        ref[s0] = lnl_red[ri]; arc[s0] = arc_red[ri]
        if np.max(np.abs(lat_red[ri] - lat_i[s0])) > 1e-4: sys.exit("source does not map to the reduced table")
        if tag == "rjsa":
            for code, srcn in ((1, "b1p"), (2, "b1s"), (3, "b2")):
                for k in np.unique(src[src[:, 0] == code, 1]):
                    r = np.where((src[:, 0] == code) & (src[:, 1] == k))[0]
                    ref[r] = np.load(out / "strata" / srcn / f"seed-{int(k)}" / "seabed-lnL.npy", mmap_mode="r")[src[r, 2]]
                    I32 = np.load(STRATA[srcn] / f"seed-{int(k)}" / "impacts32.npy", mmap_mode="r")
                    arc[r] = np.asarray(I32[src[r, 2], 9], np.float64)
                    if np.max(np.abs(np.asarray(I32[src[r, 2], 7], np.float64) - lat_i[r])) > 1e-4: sys.exit("strata source mismatch")
        ck["point_arm_max_abs_dlnL_vs_impact_point_columns"] = float(np.max(np.abs(np.log(P_row["base_rho0.05"]) - ref)))
        if not ck["point_arm_max_abs_dlnL_vs_impact_point_columns"] < 1e-6: sys.exit(f"point arm mismatch {tag} {ck}")
        key = el[:, 0].astype(np.int64) * STRIDE + el[:, 1].astype(np.int64)
        if np.any(np.diff(key) < 0): sys.exit("element order")
        nb = np.r_[True, key[1:] != key[:-1]]; okey = key[nb]; oidx = np.cumsum(nb) - 1; del nb
        n_out = len(okey); orow = okey // STRIDE
        names = list(S_row); msum = np.zeros(n_out); acc = np.zeros((n_out, len(names)))
        sel = np.where(np.asarray(el[:, 4]) == 0.0)[0]
        for s in range(0, len(sel), 3_000_000):
            ee = sel[s:s + 3_000_000]; V = lookup(np.asarray(el[ee, 5]), np.asarray(el[ee, 6]))
            o = oidx[ee]; mw = np.asarray(el[ee, 7]); msum += np.bincount(o, weights=mw, minlength=n_out)
            for j, nm in enumerate(names): acc[:, j] += np.bincount(o, weights=mw * V[nm], minlength=n_out)
        carried = msum <= 0
        Sf = {nm: np.where(carried, S_row[nm][orow], acc[:, j] / np.maximum(msum, 1e-300)) for j, nm in enumerate(names)}
        del acc
        Pf, SFf = evaluate(Sf)
        ck.update(outcomes=int(n_out), carried=int(carried.sum()), settled_elements=int(len(sel)))
        nd = np.bincount(orow, minlength=n_rows)
        rows_out = {"n_draws": nd.astype(np.int32), "source": src}
        for e in EVALS:
            l = np.log(np.bincount(orow, weights=Pf[e], minlength=n_rows) / np.maximum(nd, 1))
            if not np.isfinite(l).all(): sys.exit(f"non-finite {e}")
            rows_out[f"lnL_settled_{e}"] = l if e == "base_rho0.05" else l.astype(np.float32)
        offg = np.ones(n_out, bool)
        for k_ in ("c01_p2", "c01_bf", "c01_oi2018", "c01_oi2025", "g5_p2", "g5_oi2018", "g5_oi2025"): offg &= Sf[k_] == 0
        ck["off_ground_outcomes"] = int(offg.sum()); ck["off_ground_lnL_zero"] = bool(all(np.all(Pf[e][offg] == 1.0) for e in EVALS))
        n25_o = (lat_i > -25.0)[orow]; gl_o = (np.abs(arc) > 25.0)[orow]
        bm_o = band_masks(lat_i[orow])
        prods = []
        for j, p in enumerate(info["products"]):
            if not p.get("N"): continue
            r, dd = dr[f"rows_{j}"].astype(np.int64), dr[f"draws_{j}"].astype(np.int64)
            o = np.searchsorted(okey, r * STRIDE + dd)
            if not np.array_equal(okey[np.clip(o, 0, n_out - 1)], r * STRIDE + dd): sys.exit(f"{tag} product {j} outcome missing")
            w = np.ones(len(o))
            conv_w = tag == "rjsa" and p["subset"] == "all"
            if conv_w: w = np.where(src[r, 0] == 0, conv[p["D"]]["outcome_weight_for_rest_rows_nonA1"], 1.0)
            rec = {k: p.get(k) for k in ("option", "D", "cell", "subset", "N", "row_ess_kish", "share_of_option")}
            rec["eof_convention_weighted"] = bool(conv_w); W = w.sum()
            for e in EVALS:
                Pp, Pt, sf = Pf[e][o], P_row[e][r], SFf[e][o]; rest = 1.0 - sf
                dlt = Pp - Pt; mu = (w * dlt).sum() / W; se = math.sqrt(((w * (dlt - mu)) ** 2).sum()) / W
                cats = {"searched": sf, "north_of_25S": rest * n25_o[o], "beyond_25NM": rest * (~n25_o[o]) * gl_o[o],
                        "near_arc_unsearched": rest * (~n25_o[o]) * (~gl_o[o])}
                wp = w * Pp; wr = np.bincount(r, weights=wp)
                rec[e] = {"Z_settled_resample": float(wp.sum() / W), "Z_point_resample": float((w * Pt).sum() / W), "delta": float(mu), "delta_se": float(se),
                          "split_before": {c: float((w * x).sum() / W) for c, x in cats.items()},
                          "split_after": {c: float((wp * x).sum() / wp.sum()) for c, x in cats.items()},
                          "bands_after": {b: float((wp * k[o]).sum() / wp.sum()) for b, k in bm_o.items()},
                          "bands_before": {b: float((w * k[o]).sum() / W) for b, k in bm_o.items()},
                          "on_searched_after_point": float((w * Pt * SF_row[e][r]).sum() / (w * Pt).sum()),
                          "distinct_row_ess_after": float(wr.sum() ** 2 / (wr * wr).sum())}
            rec["distinct_rows"] = int(len(np.unique(r)))
            prods.append(rec)
        np.savez(out / f"settled-rows-{d}.part.npz", **rows_out); os.replace(out / f"settled-rows-{d}.part.npz", out / f"settled-rows-{d}.npz")
        summ["sets"][d] = {"checks": ck, "products": prods}
        print(d, json.dumps(ck), f"{time.time() - t0:.0f}s", flush=True)
    (out / "settled_summary.json").write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    {"arcgrid": arcgrid, "reduced": reduced, "strata": strata, "settled": settled}[sys.argv[1]](*sys.argv[2:])
