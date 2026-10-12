"""Settling on end of flight's H1/H2 sweep (core run D, `end-of-flight/next-run-d-he/`) and later sweeps of the same format.

Row mass, exactly end of flight's `smoke/holland_sweep_summary.py` (seed_terms / main):
    m_i = (P_s / K_s) x (w_i / sum_k w_k) x exp(ln L_i(option) [+ log-on lag density for fuel-exhaustion] + unpowered factor)
          x (1 - latent:inflight_p_breakup_to_m0019b)            [PRIMARY; 'without survival factor' omits the last term]
P_s = the summary's strata_weights (core P(family)), K_s seeds per stratum. Seeds are pooled by their evidence and strata by
P_s x end-of-flight evidence. Per seed, ln sum(m) is CHECKED against the summary's per_stratum_seed_lnZ (assert to 1e-4).

Products, per standard 00:19 option (CORE): primary (all rows), primary A1 / A2 / B (family4_code 1 / 2 / 3), without survival factor,
primary with contact speed <= 212 m/s (latent:contact_speed_feasible; architecture ruling 20:35 -0600 10 Oct, G-H2). Each product: a
systematic resample of N over ALL rows of all seeds (two passes: totals, then draws), so each (row, draw) outcome has weight 1/N.
All products share one impact table (unique rows; draws = the largest copy count over products) and one element file.

    python3 wf_rows.py prep <eof smoke dir> <run root> <summary json> <tag>     -> field/<tag>_{impacts.f64,source.npy,draws.npz,info.json,H_<j>.npy}
    (settle field/<tag>_impacts.f64 with settling::tests::wreckage_field)
    python3 wf_rows.py render <eof smoke dir> <core run.json with reference_arcs> <tag> <label> <settling commit> <eof commit> <set>
      <set> = core | family | sens  (which products go in the figure)
"""
import sys, os, json, math, pathlib, numpy as np
from collections import Counter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from wf_standard import VCOLS, GRID, grid_axes, area90, columns

N_ALL, N_FAM = int(os.environ.get("WF_N_ALL", 40000)), int(os.environ.get("WF_N_FAM", 20000))
FAMS = (("A1", 1.0), ("A2", 2.0), ("B", 3.0))


ROUTE_NAMES = {43: "MEKAR-SAMAK-ISBIX", 19: "NILAM-SAMAK-ISBIX", 3: "NILAM-IGOGU-ISBIX", 11: "NILAM-ANOKO-ISBIX", 10: "NILAM-ANOKO-BULVA", 2: "NILAM-IGOGU-BULVA"}
N_ROUTE = int(os.environ.get("WF_N_ROUTE", 20000))


def products(routes=()):
    from smoke_compare import CORE
    P = []
    for name, o, cause in CORE:
        P.append(dict(option=name, opt=o, cause=cause, ver="primary", subset="all", N=N_ALL))
        for F, _ in FAMS: P.append(dict(option=name, opt=o, cause=cause, ver="primary", subset=F, N=N_FAM))
        P.append(dict(option=name, opt=o, cause=cause, ver="without survival factor", subset="all", N=N_ALL))
        P.append(dict(option=name, opt=o, cause=cause, ver="primary", subset="cap212", N=N_ALL))
        for r in routes: P.append(dict(option=name, opt=o, cause=cause, ver="primary", subset=f"route:{r}", N=N_ROUTE))
    return P


def route_of_rows(route_dir, sd, g):
    """Route of each row = core's route_index.csv[parent] (as end of flight's run_h_summary.py)."""
    import csv
    k = sd.name.split("-")[1]
    route = np.array([int(r["route_index"]) for r in csv.DictReader(open(pathlib.Path(route_dir) / f"seed-{k}" / "route_index.csv"))])
    return route[g("parent").astype(np.int64)]


def seed_masses(sd, P, c, route_dir=None):
    """Per product, the row masses of one seed (float64), and the columns needed later. Expressions copied from seed_terms."""
    from scipy.special import gammaln
    from compact_impacts import load, family_labels
    from displacement_hist import derived_logliks, constraint_log_factor
    meta, g = load(sd)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [x[len("loglik:"):] for x in meta["impact_columns"] if x.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    pb19 = np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1); feas = g("latent:contact_speed_feasible") == 1
    out, lnz = [], {}
    cache = {}
    for p in P:
        k = (p["opt"], p["cause"], p["ver"])
        if k not in cache:
            base = der[p["opt"]] if p["opt"] in der else g("loglik:" + p["opt"])
            ll0 = np.where(np.isfinite(base), base, -np.inf) + (lfe if p["cause"] == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, p["cause"], "unpowered")
            with np.errstate(divide="ignore"):
                a = lw + ll0 + (np.log1p(-pb19) if p["ver"] == "primary" else 0.0)
            cache[k] = a
        a = cache[k]
        if p["subset"].startswith("route:"):
            if "route" not in cache: cache["route"] = route_of_rows(route_dir, sd, g)
            mask = cache["route"] == int(p["subset"].split(":")[1])
        else:
            mask = np.ones(len(a), bool) if p["subset"] == "all" else (feas if p["subset"] == "cap212" else (f4 == dict(FAMS)[p["subset"]]))
        out.append(np.where(mask, np.exp(a + c), 0.0))
        if p["subset"] == "all": lnz[(p["option"], p["ver"])] = float(np.log(np.exp(a - a.max()).sum()) + a.max())
    return out, lnz, g


def prep(SM, root, summ, tag):
    sys.path.insert(0, SM)
    root = pathlib.Path(root)
    if summ != "-": S = json.loads(pathlib.Path(summ).read_text()); strata = S["strata_weights"]
    else: S = None; strata = {a.split("=")[0]: float(a.split("=")[1]) for a in os.environ["WF_STRATA"].split(",")}
    route_dir = os.environ.get("WF_ROUTE_DIR"); routes = [int(x) for x in os.environ.get("WF_ROUTES", "").split(",") if x]
    P = products(routes)
    seeds = [(si, st, sd) for si, st in enumerate(strata) for sd in sorted((p for p in (root / st).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name.split("-")[1]))]
    K = Counter(st for _, st, _ in seeds)
    # pass 1: per-seed product totals, extent, and the ln Z check against end of flight's summary
    lnz_rec = {}
    tot = np.zeros((len(seeds), len(P))); lat_min, lat_max, lon_min, lon_max = 90, -90, 360, -360; worst = 0.0
    for q, (si, st, sd) in enumerate(seeds):
        ms, lnz, g = seed_masses(sd, P, math.log(strata[st] / K[st]), route_dir)
        tot[q] = [m.sum() for m in ms]
        for (name, ver), v in lnz.items():
            lnz_rec.setdefault(f"{st}|{name}|{ver}", []).append(v)
            if S is not None:
                ref = S["per_stratum_seed_lnZ"][f"{st}|{name}|{ver}"][int(sd.name.split("-")[1]) - 1]; worst = max(worst, abs(v - ref))
        la, lo = g("latitude_deg"), g("longitude_deg"); f = np.isfinite(la) & np.isfinite(lo)
        lat_min, lat_max = min(lat_min, la[f].min()), max(lat_max, la[f].max()); lon_min, lon_max = min(lon_min, lo[f].min()), max(lon_max, lo[f].max())
        print("pass1", st, sd.name, "max |lnZ - summary|", f"{worst:.2e}", flush=True)
    assert worst < 1e-4, f"row masses do not reproduce end of flight's per-seed ln Z (worst {worst})"
    if S is None: worst = None
    ext = [math.floor(lon_min) - 1.0, math.ceil(lon_max) + 1.0, math.floor(lat_min) - 1.0, math.ceil(lat_max) + 1.0]; le, oe = grid_axes(ext)
    W = tot.sum(axis=0); cum = np.cumsum(tot / W, axis=0); lo_edge = np.vstack([np.zeros(len(P)), cum[:-1]])
    rng = np.random.default_rng(20261012); U = [(rng.random() + np.arange(p["N"])) / p["N"] for p in P]
    H = [np.zeros((len(le) - 1, len(oe) - 1), np.float32) for _ in P]; sq = np.zeros(len(P))
    tab, src = [], []; occ = [{"rows": [], "draws": [], "stratum": [], "seed": []} for _ in P]
    for q, (si, st, sd) in enumerate(seeds):
        ms, _, g = seed_masses(sd, P, math.log(strata[st] / K[st]), route_dir)
        la, lo = g("latitude_deg"), g("longitude_deg"); f = np.isfinite(la) & np.isfinite(lo)
        picks = {}
        for j, m in enumerate(ms):
            H[j] += np.histogram2d(la[f], lo[f], bins=[le, oe], weights=m[f] / W[j])[0].astype(np.float32); sq[j] += float(((m / W[j]) ** 2).sum())
            uu = U[j][(U[j] >= lo_edge[q, j]) & (U[j] < cum[q, j])]
            if uu.size == 0: continue
            pk = np.minimum(np.searchsorted(np.cumsum(m / W[j]), uu - lo_edge[q, j]), len(m) - 1); assert np.all(m[pk] > 0), "zero-mass row drawn"
            picks[j] = pk
        need = Counter()
        for j, pk in picks.items():
            for i, cnt in Counter(pk.tolist()).items(): need[i] = max(need[i], cnt)
        ii = np.array(sorted(need)); 
        if ii.size:
            V = np.column_stack([g(cn)[ii] for cn in VCOLS]); base = len(tab); where = {i: base + n for n, i in enumerate(ii.tolist())}
            k = int(sd.name.split("-")[1])
            for r, i in zip(V, ii): tab.append(np.r_[r, need[i], si * 10 + k]); src.append((si, k, i))
            for j, pk in picks.items():
                seen = Counter()
                for i in pk.tolist():
                    occ[j]["rows"].append(where[i]); occ[j]["draws"].append(seen[i]); seen[i] += 1; occ[j]["stratum"].append(si); occ[j]["seed"].append(k)
        print("pass2", st, sd.name, "table", len(tab), flush=True)
    pathlib.Path("field").mkdir(exist_ok=True)
    np.array(tab).astype("<f8").tofile(f"field/{tag}_impacts.f64"); np.save(f"field/{tag}_source.npy", np.array(src, dtype=np.int64))
    arrays = {f"{n}_{j}": np.array(o[n], dtype=np.int64) for j, o in enumerate(occ) for n in o}
    np.savez(f"field/{tag}_draws.npz", **arrays)
    info = {"strata": list(strata), "strata_weights": strata, "extent_lon_lon_lat_lat": ext, "summary": str(summ), "lnZ_check_max_abs": worst, "per_seed_lnZ": lnz_rec, "route_dir": route_dir,
            "route_names": {str(r): ROUTE_NAMES.get(r, str(r)) for r in routes}, "products": []}
    for j, p in enumerate(P):
        np.save(f"field/{tag}_H_{j}.npy", H[j])
        info["products"].append(dict(p, row_ess_kish=float(1.0 / sq[j]), share_of_option=float(W[j]), resampled=len(occ[j]["rows"]),
                                     distinct=len(set(occ[j]["rows"])), impact_area90_km2_all_rows=area90(H[j].astype(np.float64), le, oe)))
    # shares relative to the option's primary-all mass
    allm = {p["option"]: W[j] for j, p in enumerate(P) if p["ver"] == "primary" and p["subset"] == "all"}
    for d in info["products"]: d["share_of_option"] = d["share_of_option"] / allm[d["option"]]
    pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))
    print("table rows", len(tab), "draws", int(np.array(tab)[:, 12].sum()), flush=True)


def render(SM, arcs_json, tag, label, settling_commit, eof_commit, which):
    sys.path.insert(0, SM)
    import matplotlib; matplotlib.use("Agg")
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij")
    T = np.fromfile(f"field/{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}_elements.f64", "<f8").reshape(-1, 8)
    P = info["products"]
    if which == "core": sel = [j for j, p in enumerate(P) if p["ver"] == "primary" and p["subset"] == "all"]
    elif which == "family": sel = [j for F in ("A1", "A2", "B") for j, p in enumerate(P) if p["ver"] == "primary" and p["subset"] == F]
    elif which == "routes":
        rs = sorted({p["subset"] for p in P if p["subset"].startswith("route:")}, key=lambda r: -sum(q["share_of_option"] for q in P if q["subset"] == r))
        opts = list(dict.fromkeys(p["option"] for p in P))
        sel = [j for r in rs for o in opts for j, p in enumerate(P) if p["subset"] == r and p["option"] == o and p["ver"] == "primary"]
    else: sel = [j for j, p in enumerate(P) if p["option"] in ("00:19 Holland H1", "00:19 Holland H2") and p["subset"] in ("all", "cap212")]
    def title(p):
        t = p["option"]
        if p["subset"] in ("A1", "A2", "B"): t += f" · {p['subset']}"
        if p["subset"] == "cap212": t += ", impacts at or below 212 m/s"
        if p["subset"].startswith("route:"): t = t.replace("00:19 ", "") + " · " + info["route_names"].get(p["subset"].split(":")[1], p["subset"])
        if p["ver"] != "primary": t += ", breakup before 00:19:37 allowed"
        return t
    names = [title(P[j]) for j in sel]; letters = "abcdefghijklmnopqrstuvwxyz"
    ncol = 5 if which in ("family", "routes") else 3
    g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": arcs_json, "NCOL": ncol,
         "OUTSTEM": f"settling-seabed-wreckage-{label}-{which}", "STAMP": "Not yet estimable",
         "TITLES_W": {n: f"({letters[q]}) {n}" for q, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {}, "PANEL_NOTE": {}}
    for n, j in zip(names, sel):
        g["SRC"][n] = (T, z[f"rows_{j}"], z[f"draws_{j}"], EL)
        Hm = np.load(f"field/{tag}_H_{j}.npy").astype(np.float64); nz = Hm > 0; g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
        g["ESS"][n] = P[j]["row_ess_kish"]
        if P[j]["subset"] in ("A1", "A2", "B", "cap212") or P[j]["subset"].startswith("route:"):
            g["PANEL_NOTE"][n] = f"share of the option {100 * P[j]['share_of_option']:.0f} %"
    g["TITLE"] = {"core": "Where the wreckage is on the seabed, for each use of the 00:19 satellite data",
                  "family": "Where the wreckage is on the seabed, for each use of the 00:19 satellite data and each type of flight end",
                  "sens": "Where the wreckage is on the seabed under the Holland readings: two checks",
                  "routes": "Where the wreckage is on the seabed, for each route after 18:01 and each use of the 00:19 satellite data"}[which]
    g["SUBTITLE"] = {"core": "Flight model with descents aimed at the two 00:19 bursts; the aircraft did not break up before 00:19:37",
                     "family": "Rows: A1 fuel exhaustion, then no control; A2 fuel exhaustion, then controlled to the surface; B deliberate descent before fuel exhaustion",
                     "sens": "Left: as reported. Middle: descents that broke up before 00:19:37 are kept. Right: only impacts at or below 212 m/s",
                     "routes": "Rows: one route each (named by its waypoints), in order of probability; each panel is conditional on its route"}[which]
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. The flight model "
                     "is not yet stable, so these areas can change. In most Holland descents the aircraft would break up in the air before it hit the water; "
                     "the model still puts the wreckage at one impact point.")
    s = info["strata_weights"]
    g["FOOT_TECH"] = (f"Settled-mass seabed density (real ocean: GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10 density; GLORYS12V1 surface current; ERA5 wind; "
                      f"AusSeabed then GEBCO_2026), settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight H1/H2 sweep "
                      f"on {os.environ.get('WF_RUN_NAME', 'core run D')} ({len(s)} strata x {os.environ.get('WF_NSEEDS', '4')} seeds; EoF {eof_commit}); row mass = core P(family) / seeds x hand-off weight x 00:19 likelihood "
                      f"(+unpowered; log-on lag density for H1) x (1 - P(in-flight breakup by 00:19:37)) [primary], as end of flight's holland_sweep_summary "
                      f"" + (f"(per-seed ln Z reproduced to {info['lnZ_check_max_abs']:.0e}); " if info['lnZ_check_max_abs'] is not None else "(no end-of-flight summary yet: ln Z recorded, not checked); ")
                      + "strata " + ", ".join(f"{k} {v:.3f}" for k, v in s.items()) + ". Systematic resample over all rows, one settling draw each: "
                      + ", ".join(sorted({f"{P[j]['N']:,}" for j in sel})) + ". 0.02 deg grid, Gaussian 0.1 deg, HPD. Row ESS by Kish; below 1,000 not estimable. "
                      "Labels: " + os.environ.get("WF_CORE_LABEL", "core run D split-half NOT converged") + "; piloted rapid descent to 40,000 ft/min with unloading to -1.0 g; INTERIM pitch-down; "
                      "in-flight structural outcome PROVISIONAL (upper side: no transonic drag rise); breakup rows "
                      "settled from the intact impact point (fragment field not modelled, G-bf); " + os.environ.get("WF_GAP_LABEL", "A1 under H1/H2 136 / 59 effective impacts (COVERAGE GAP)") + "; "
                      "P(left) = 0.8 PROVISIONAL; Mac, 2 threads.")
    exec(open(pathlib.Path(__file__).with_name("wreckage_map_standard.py")).read(), g)


if __name__ == "__main__":
    {"prep": prep, "render": render}[sys.argv[1]](*sys.argv[2:])
