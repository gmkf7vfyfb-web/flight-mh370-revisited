#!/usr/bin/env python3
"""Searched areas on end of flight's A1-branch conditional pass, run J waypoints (work order overnight-2026-10-19, B3).

    python score_a1branch.py point   <out dir> [nproc]     impact point, every row of production (24 seeds) and the pass (8 seeds)
    python score_a1branch.py settled <out dir>             settled seabed positions (settling/run-j-a1branch), V0-V3 per-cell field
    (reduction: reduce_a1branch.py)

Branch = onset flame-out-associated (latent:onset_mechanism == 2) AND control 'no intervention' (latent:control_realised == 2), a
subset of A1 (cruise to fuel exhaustion, then no control). Stratified estimator (end of flight, results/eof-a1-branch-oct18), row by
row as settling applies it (results/settling-run-j-a1branch): row mass m = the run J settling recipe (wf_runj.seed_masses =
option_table_0019 seed_terms, primary cell 'D<d> total q=0.333 (C2 silent)'; per-seed ln Z asserted equal to seed_terms), seeds
pooled equally inside each source; production rows IN the branch get mass 0; pass rows get mass x SCALE,
SCALE = M_prod(D0', branch) / S_pass(D0').
Searched areas: the base of run.toml, enforced by base_guard.check() (Phase 2 q 0.945; Bluefin-21 q 0.9; OI 2018 q 0.9 f 0.889;
OI 2025-26 outboard q 0.9 f 0.7808; rho 0.05), P(no find | y) = rho + (1 - rho) prod_k (1 - q_k f_k c_k(y)), c_k bilinear on the
0.01 deg .cov rasters on cell centres (as `mh370 evaluate`; checked here against the published run J column on every production row).
Settled: score_spatial_run_j's Lookup and variants (V0 = run.toml base exactly; V1 central; V2 pessimistic; V3 optimistic; ...), the
'mean' field treatment, row likelihood = MEAN of P(no find) over the row's settling draws (alternative outcomes are averaged, never
multiplied).
"""
import hashlib, json, math, os, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MOD = HERE.parent
sys.path.insert(0, str(MOD)); sys.path.insert(0, str(MOD / "spatial"))
import base_guard  # noqa: E402

X = pathlib.Path(os.environ.get("MH370_EXCHANGE", "/Users/pete/Downloads/mh370-exchange"))
WK = pathlib.Path(os.environ.get("SETTLING_WORK", "/Users/pete/Downloads/mh370-settling-work-j"))   # settling's driver (read only)
PROD = X / "end-of-flight/run-j/run-j-waypoints"
PASS = X / "end-of-flight/run-j-a1branch/run-j-waypoints"
CORE = X / "core/run-j/run-j-waypoints"
PUB = X / "searched-areas/run-j/run-j-waypoints"
SETT = X / "settling/run-j-a1branch/run-j-waypoints"
FIELDS = X / "searched-areas/spatial-fields/fields.npz"
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
# name -> (raster, q*f, f); base_guard.check() enforces that run.toml carries exactly these values
LAYERS = {"phase2-2014-2017": ("phase2", 0.945, 1.0), "bluefin-2014": ("bluefin-2014", 0.9, 1.0),
          "ocean-infinity-2018": ("ocean-infinity-2018", 0.9 * 0.889, 0.889), "ocean-infinity-2025": ("ocean-infinity-2025", 0.9 * 0.7808, 0.7808)}
ATSB = ["phase2-2014-2017", "bluefin-2014"]
SCEN = {"base_rho0.05": (list(LAYERS), 0.05), "base_rho0": (list(LAYERS), 0.0), "base_rho0.25": (list(LAYERS), 0.25),
        "base_rho0.5": (list(LAYERS), 0.5), "without_oi_rho0.05": (ATSB, 0.05)}
PUBFILE = {"base_rho0.05": "seabed-lnL.npy", "base_rho0": "seabed-lnL-rho0.npy", "base_rho0.25": "seabed-lnL-rho0.25.npy",
           "base_rho0.5": "seabed-lnL-rho0.5.npy", "without_oi_rho0.05": "seabed-lnL-without-oi.npy"}
_COV = {}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
    return h.hexdigest()


def verify(d, names):
    want = {}
    for l in (d / "SHA256SUMS").read_text().splitlines():
        if l.strip():
            h, n = l.split(None, 1); want[n.strip()] = h
    for n in names:
        if want.get(n) != sha(d / n): sys.exit(f"SHA256 mismatch {d / n}")


def coverage(lat, lon):
    from score_spatial_run_j import bilin
    from build_fields import read_cov
    out = {}
    for n, (f, _, _) in LAYERS.items():
        if f not in _COV: _COV[f] = read_cov(MOD / "coverage" / f"{f}.cov")
        a, g = _COV[f]
        out[n] = bilin(a, g[0], g[1], g[2], lat, lon)
    return out


def p_no_find(cov, names, rho):
    m = np.ones(len(cov[names[0]]))
    for n in names: m = m * (1.0 - cov[n] * LAYERS[n][1])
    return rho + (1.0 - rho) * m


def _settling():
    sys.path.insert(0, str(WK)); sys.path.insert(0, str(WK / "eof-engine/hypotheses/end-of-flight/smoke"))
    import wf_a1branch as A
    A.R._CORE["dir"] = str(CORE)
    return A


def point_seed(args):
    src, sd, K, out = args
    sd, out = pathlib.Path(sd), pathlib.Path(out)
    A = _settling()
    t0 = time.time()
    ms, lnz, g = A.R.seed_masses(sd, A._base(), math.log(1.0 / K))
    br, f4 = A._labels(g)
    par = g("parent").astype(np.int64)
    lat = g("latitude_deg").astype(np.float64); lon = g("longitude_deg").astype(np.float64)
    n = len(lat)
    cov = coverage(lat, lon)
    lnP = {s: np.log(p_no_find(cov, nm, r)) for s, (nm, r) in SCEN.items()}
    sf = 1.0 - np.prod([1.0 - LAYERS[k][2] * cov[k] for k in LAYERS], axis=0)
    atsb = 1.0 - (1.0 - cov["phase2-2014-2017"]) * (1.0 - cov["bluefin-2014"])
    n33 = (lat > -33.0).astype(np.float64)
    chk = {"src": src, "seed": sd.name, "rows": n, "branch_rows": int(br.sum()), "lnZ_check_worst": float(A.R._CORE.get("worst", 0.0))}
    if src == "prod":
        p = PUB / sd.name
        verify(p, list(PUBFILE.values()) + ["seabed-searched-fraction.npy"])
        for s, f in PUBFILE.items():
            q = np.load(p / f).astype(np.float64)
            if len(q) != n: sys.exit(f"{p}/{f}: {len(q)} rows, impacts32 {n}")
            chk[f"max_abs_dlnL_vs_published_{s}"] = float(np.abs(q - lnP[s]).max())
        chk["max_abs_dsf_vs_published"] = float(np.abs(np.load(p / "seabed-searched-fraction.npy").astype(np.float64) - sf).max())
        if chk["max_abs_dlnL_vs_published_base_rho0.05"] > 1e-9: sys.exit(f"impact-point lnL differs from published run J column: {chk}")
        for j in range(len(DS)): assert not (ms[j][br & (f4 != 1)] > 0).any(), "branch row outside A1"
    else:
        for j in range(len(DS)): assert not (ms[j][~br] > 0).any(), "pass row outside the branch has positive mass"
        o = out / "pass" / sd.name; o.mkdir(parents=True, exist_ok=True)
        np.save(o / "seabed-lnL.npy", lnP["base_rho0.05"])
        for s, f in PUBFILE.items():
            if s != "base_rho0.05": np.save(o / f, lnP[s].astype(np.float32))
        np.save(o / "seabed-searched-fraction.npy", sf.astype(np.float32))
        fl = sorted(x.name for x in o.glob("*.npy"))
        (o / "SHA256SUMS").write_text("".join(f"{sha(o / x)}  {x}\n" for x in fl))
    if src == "prod":
        M = {"strat_all": ~br, "strat_A1": (f4 == 1) & ~br, "A2": f4 == 2, "B": np.isin(f4, (3, 6)), "other": ~np.isin(f4, (1, 2, 3, 6)),
             "prod_all": np.ones(n, bool), "prod_A1": f4 == 1, "prod_branch": br}
    else:
        M = {"strat_all": np.ones(n, bool), "strat_A1": np.ones(n, bool), "pass_all": np.ones(n, bool)}
    P = {s: np.exp(v) for s, v in lnP.items()}
    T = {}
    for j, d in enumerate(DS):
        m = ms[j]; T[d] = {}
        for k, mk in M.items():
            mm = np.where(mk, m, 0.0)
            r = {"m": float(mm.sum()), "m2": float((mm * mm).sum()), "on_union": float((mm * sf).sum()), "on_atsb": float((mm * atsb).sum()),
                 "north33": float((mm * n33).sum()), "m_par2": float((np.bincount(par, mm) ** 2).sum())}
            for s, p_ in P.items():
                mp = mm * p_
                r[s] = {"mP": float(mp.sum()), "mP2": float((mp * mp).sum()), "on_union": float((mp * sf).sum()), "on_atsb": float((mp * atsb).sum()),
                        "north33": float((mp * n33).sum())}
                if s == "base_rho0.05": r[s]["mP_par2"] = float((np.bincount(par, mp) ** 2).sum())
            T[d][k] = r
    chk["wall_s"] = time.time() - t0
    return {"check": chk, "terms": T}


def point(out, nproc=4, only=None):
    from multiprocessing import Pool
    label = base_guard.check(MOD / "run.toml")
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    seeds = lambda d: sorted((p for p in d.glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
    sp, ss = seeds(PROD), seeds(PASS)
    assert len(sp) == 24 and len(ss) == 8, (len(sp), len(ss))
    jobs = [("pass", str(s), len(ss), str(out)) for s in ss] + [("prod", str(s), len(sp), str(out)) for s in sp]
    if only:   # validation: one job, e.g. 'prod:seed-1'
        jobs = [j for j in jobs if f"{j[0]}:{pathlib.Path(j[1]).name}" == only]
        r = point_seed(jobs[0]); print(json.dumps(r["check"])); return
    for s in ss: verify(s, ["impacts32.npy", "parents32.npy", "run.json"])
    res = []
    with Pool(int(nproc)) as pool:
        for r in pool.imap_unordered(point_seed, jobs):
            res.append(r); print(json.dumps(r["check"]), flush=True)
    (out / "point_terms.json").write_text(json.dumps({"label": label, "seeds": res}))


# ---------------------------------------------------------------- settled
def settled(out):
    from score_spatial_run_j import Lookup, VARIANTS, variant_P, STRIDE
    label = base_guard.check(MOD / "run.toml")
    out = pathlib.Path(out); t0 = time.time()
    tag = "rja1"
    verify(SETT, [f"{tag}_impacts.f64", f"{tag}_elements.f64", f"{tag}_draws.npz", f"{tag}_source.npy", f"{tag}_info.json"])
    info = json.loads((SETT / f"{tag}_info.json").read_text())
    imp = np.fromfile(SETT / f"{tag}_impacts.f64", "<f8").reshape(-1, 14)
    el = np.memmap(SETT / f"{tag}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8)
    src = np.load(SETT / f"{tag}_source.npy"); dr = np.load(SETT / f"{tag}_draws.npz")
    n_rows = imp.shape[0]; L = Lookup(FIELDS)
    checks = {"table_rows": int(n_rows), "elements": int(el.shape[0]), "label": label}
    key = el[:, 0].astype(np.int64) * STRIDE + el[:, 1].astype(np.int64)
    if np.any(np.diff(key) < 0): sys.exit("element table not in (row, draw) order")
    newblk = np.r_[True, key[1:] != key[:-1]]; okey = key[newblk]; oidx = np.cumsum(newblk) - 1; del newblk
    n_out = len(okey); orow = okey // STRIDE; checks["outcomes"] = int(n_out)
    lat_i, lon_i = imp[:, 1].copy(), imp[:, 2].copy()
    V_row = L(lat_i, lon_i); S_row = {nm: V_row[:, j] for j, nm in enumerate(L.names)}
    P0_row, sf_row = variant_P(S_row, "V0_scalar")
    ref = np.full(n_rows, np.nan)
    for s_, k in sorted({(int(a), int(b)) for a, b in src[:, :2]}):
        r = np.where((src[:, 0] == s_) & (src[:, 1] == k))[0]
        f = (PUB / f"seed-{k}" / "seabed-lnL.npy") if s_ == 0 else (out / "pass" / f"seed-{k}" / "seabed-lnL.npy")
        ref[r] = np.load(f, mmap_mode="r")[src[r, 2]]
        I32 = np.load((PROD if s_ == 0 else PASS) / f"seed-{k}" / "impacts32.npy", mmap_mode="r")
        if np.max(np.abs(np.asarray(I32[src[r, 2], 7], np.float64) - lat_i[r])) > 1e-4: sys.exit("source.npy does not map to impacts32 latitude")
    checks["point_arm_max_abs_dlnL_vs_impact_point_columns"] = float(np.abs(np.log(P0_row) - ref).max())
    if checks["point_arm_max_abs_dlnL_vs_impact_point_columns"] > 1e-6: sys.exit(f"point arm mismatch {checks}")
    nv = V_row.shape[1]; msum = np.zeros(n_out); acc = np.zeros((n_out, nv))
    sel = np.where(np.asarray(el[:, 4]) == 0.0)[0]
    for s in range(0, len(sel), 4_000_000):
        ee = sel[s:s + 4_000_000]
        V = L(np.asarray(el[ee, 5]), np.asarray(el[ee, 6])); o = oidx[ee]; m = np.asarray(el[ee, 7])
        msum += np.bincount(o, weights=m, minlength=n_out)
        for j in range(nv): acc[:, j] += np.bincount(o, weights=m * V[:, j], minlength=n_out)
    carried = msum <= 0
    S_arr = np.where(carried[:, None], V_row[orow], acc / np.maximum(msum, 1e-300)[:, None])
    S = {nm: S_arr[:, j] for j, nm in enumerate(L.names)}
    checks["carried_outcomes"] = int(carried.sum()); checks["settled_elements_scored"] = int(len(sel))
    nd = np.bincount(orow, minlength=n_rows)
    o1 = int(np.where(~carried)[0][0])
    Pa, _ = variant_P({k: v[[o1]] for k, v in S.items()}, "V1_central"); Pb, _ = variant_P({k: v[[o1, o1]] for k, v in S.items()}, "V1_central")
    checks["averaging_test_two_identical_draws_equal_one"] = bool(abs(Pa[0] - Pb.mean()) < 1e-15)
    offg = np.ones(n_out, bool)
    for k in ("c01_p2", "c01_bf", "c01_oi2018", "c01_oi2025", "g5_p2", "g5_oi2018", "g5_oi2025"): offg &= S[k] == 0
    checks["off_ground_outcomes"] = int(offg.sum())
    checks["off_ground_lnL_exactly_zero_all_variants"] = bool(all(np.all(np.log(variant_P({k: v[offg] for k, v in S.items()}, vv)[0]) == 0.0) for vv in VARIANTS))
    Pv, SFv, rows_out = {}, {}, {"n_draws": nd.astype(np.int32)}
    for v in VARIANTS:
        P, sf = variant_P(S, v); Pv[v], SFv[v] = P, sf
        rows_out[f"lnL_{v}"] = np.log(np.bincount(orow, weights=P, minlength=n_rows) / np.maximum(nd, 1))
        if not np.isfinite(rows_out[f"lnL_{v}"]).all(): sys.exit(f"non-finite {v}")
    sfpt = sf_row[orow]
    cbar = {"phase2-2014-2017": S["c01_p2"], "bluefin-2014": S["c01_bf"], "ocean-infinity-2018": S["c01_oi2018"], "ocean-infinity-2025": S["c01_oi2025"]}
    cpt = {"phase2-2014-2017": S_row["c01_p2"][orow], "bluefin-2014": S_row["c01_bf"][orow], "ocean-infinity-2018": S_row["c01_oi2018"][orow],
           "ocean-infinity-2025": S_row["c01_oi2025"][orow]}
    Psc = {s: p_no_find(cbar, nm, r) for s, (nm, r) in SCEN.items()}; Psc_pt = {s: p_no_find(cpt, nm, r) for s, (nm, r) in SCEN.items()}
    checks["V0_scalar_equals_base_rho0.05_max_abs"] = float(np.abs(Psc["base_rho0.05"] - Pv["V0_scalar"]).max())
    n33 = (lat_i > -33.0)[orow]
    prods = []
    for j, p in enumerate(info["products"]):
        r, d = dr[f"rows_{j}"].astype(np.int64), dr[f"draws_{j}"].astype(np.int64)
        o = np.searchsorted(okey, r * STRIDE + d)
        if not np.array_equal(okey[np.clip(o, 0, n_out - 1)], r * STRIDE + d): sys.exit(f"product {j}: outcome missing")
        N = len(o); rec = {k: p[k] for k in ("option", "D", "cell", "subset", "N", "row_ess_kish", "share_of_option")}

        def stats(P, base, sf):
            dd = P - base; w = np.bincount(r, weights=P)
            return {"Z": float(P.mean()), "Z_se": float(P.std(ddof=1) / math.sqrt(N)), "d": float(dd.mean()),
                    "d_se": float(dd.std(ddof=1) / math.sqrt(N)), "on_searched_before": float(sf.mean()),
                    "on_searched_after": float((P * sf).sum() / P.sum()), "north33_after": float((P * n33[o]).sum() / P.sum()),
                    "outcome_ess_after": float(P.sum() ** 2 / (P * P).sum()), "distinct_row_ess_after": float(w.sum() ** 2 / (w * w).sum())}
        rec["point"] = {s: {"Z": float(Psc_pt[s][o].mean()), "on_searched_after": float((Psc_pt[s][o] * sfpt[o]).sum() / Psc_pt[s][o].sum())} for s in SCEN}
        rec["point"]["on_searched_before"] = float(sfpt[o].mean())
        rec["scalar_vs_point"] = {s: stats(Psc[s][o], Psc_pt[s][o], SFv["V0_scalar"][o]) for s in SCEN}
        rec["variants_vs_V0"] = {v: stats(Pv[v][o], Pv["V0_scalar"][o], SFv[v][o]) for v in VARIANTS}
        rec["distinct_rows"] = int(len(np.unique(r)))
        rec["pass_share_of_outcomes"] = float((src[r, 0] == 1).mean())
        prods.append(rec)
    np.savez(out / "rows.part.npz", source=src, **{k: (v if k == "n_draws" else v.astype(np.float32)) for k, v in rows_out.items()},
             lnL_settled_base_rho0_05_f64=rows_out["lnL_V0_scalar"])
    os.replace(out / "rows.part.npz", out / "settled-rows.npz")
    checks["wall_s"] = time.time() - t0
    (out / "settled_summary.json").write_text(json.dumps({"variants": VARIANTS, "checks": checks, "products": prods}, indent=1))
    print(json.dumps(checks), flush=True)


if __name__ == "__main__":
    {"point": point, "settled": settled}[sys.argv[1]](*sys.argv[2:])
