"""Settling on end of flight's run I (core run I; `end-of-flight/run-i/<stratum>/`), one stratum at a time (conditional on it).

Row mass per cell of end of flight's 00:19 two-factor table (`smoke/option_table_0019.py`, seed_terms; architecture 01:45Z,
02:05Z, 02:15Z, 12 Oct): m_i = w_i / sum(w) / K x exp(survival + ln L_D + ln L_cause), with
  D0 held out; D1 R600 BTO; D2 R600 BTO + R600 BFO as recorded; D3 R600 BTO + both BFOs as recorded; D4 R600 BTO + both BFOs,
  Holland transient bias added; D5 R600 BTO + R600 BFO as recorded + R1200 BFO, Holland transient bias added (closed form, d5_loglik);
  cause C1 (fuel exhaustion: Erlang lag + unpowered), C2 silent (1/W + silent), and the competing-causes TOTAL at q = 1/3 with C2
  silent (PRIMARY): logaddexp(ln p + C1, ln(1-p) + C2 silent), p = 1/(1+q).
CHECK: for every seed, ln sum(m) of every cell equals end of flight's own seed_terms(...)["all"][0] (asserted to 1e-6), so the row
masses are end of flight's, not a transcription.

Products per D: total (primary, N_TOT), total x family A1 / A2 / B (N_FAM), C1 alone and C2 silent alone (N_CAUSE).
    python3 wf_runi.py prep <stratum dir> <core stratum dir> <tag>
    python3 wf_runi.py render <tag> <label> <settling commit> <eof commit> core|cause|family
"""
import sys, os, json, math, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
SM = HERE / "eof-engine/hypotheses/end-of-flight/smoke"
sys.path.insert(0, str(SM)); sys.path.insert(0, str(HERE))
import wf_rows

N_TOT, N_FAM, N_CAUSE = int(os.environ.get("WF_N_TOT", 40000)), int(os.environ.get("WF_N_FAM", 10000)), int(os.environ.get("WF_N_CAUSE", 20000))
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
DNAME = {"D0": "00:19 Held Out", "D1": "00:19 R600 BTO Only", "D2": "00:19 R600 BTO + Raw BFO", "D3": "00:19 R600 BTO + both BFOs as recorded",
         "D4": "00:19 R600 BTO + both BFOs, Holland transient bias added", "D5": "00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added"}
SHORT = {"D0": "Held Out", "D1": "R600 BTO Only", "D2": "R600 BTO + Raw BFO", "D3": "both BFOs as recorded",
         "D4": "both BFOs, Holland transient bias added", "D5": "R1200 BFO, Holland transient bias added"}
TOTAL = "total q=0.333 (C2 silent)"
CELLS = {"total": TOTAL, "C1": "C1", "C2 silent": "C2 silent"}
_CORE = {}


def products(routes=()):
    P = []
    for d in DS:
        P.append(dict(option=DNAME[d], D=d, cell="total", ver="primary", subset="all", N=N_TOT))
        for F, _ in wf_rows.FAMS: P.append(dict(option=DNAME[d], D=d, cell="total", ver="primary", subset=F, N=N_FAM))
        for c in ("C1", "C2 silent"): P.append(dict(option=DNAME[d], D=d, cell=c, ver=c, subset="all", N=N_CAUSE))
    return P


def seed_masses(sd, P, c, route_dir=None):
    """Row masses per product, from end of flight's seed_terms construction; per-cell ln Z asserted equal to seed_terms'."""
    import option_table_0019 as OT
    from scipy.special import gammaln
    from compact_impacts import load, family_labels
    from displacement_hist import derived_logliks, constraint_log_factor
    import csv
    handoff = pathlib.Path(_CORE["dir"]) / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy"
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(OT.SATCOM_CSV))}
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [x[len("loglik:"):] for x in meta["impact_columns"] if x.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(handoff, mmap_mode="r")[:, 9])[g("parent").astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"), "D4": col("both/startup-offset"), "D5": OT.d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C = {"C1": lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered"), "C2 silent": -np.log(OT.W_S) + constraint_log_factor(g, logon, "other", "silent")}
    p = 1 / (1 + 1 / 3)
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    a_cell = {}
    for d in DS:
        a_cell[(d, "C1")] = lw + surv + D[d] + C["C1"]; a_cell[(d, "C2 silent")] = lw + surv + D[d] + C["C2 silent"]
        a_cell[(d, "total")] = lw + surv + D[d] + np.logaddexp(np.log(p) + C["C1"], np.log(1 - p) + C["C2 silent"])
    # check against end of flight's own seed_terms for this seed
    ref = OT.seed_terms(sd, handoff); worst = 0.0; lnz = {}
    for (d, cell), a in a_cell.items():
        fin = np.isfinite(a); v = float(np.log(np.exp(a[fin] - a[fin].max()).sum()) + a[fin].max()) if fin.any() else -np.inf
        r = ref[f"{d}x{CELLS[cell]}" if cell != "total" else f"{d} {TOTAL}"]["all"][0]
        worst = max(worst, abs(v - r) if np.isfinite(r) else (0.0 if not np.isfinite(v) else 1e9)); lnz[(DNAME[d], cell)] = v
    assert worst < 1e-6, f"{sd}: row masses differ from option_table_0019.seed_terms (worst {worst})"
    _CORE.setdefault("worst", 0.0); _CORE["worst"] = max(_CORE["worst"], worst)
    out = []
    for q in P:
        a = a_cell[(q["D"], q["cell"])]
        mask = np.ones(len(a), bool) if q["subset"] == "all" else (f4 == dict(wf_rows.FAMS)[q["subset"]])
        m = np.exp(a + c); m[~np.isfinite(m)] = 0.0; out.append(np.where(mask, m, 0.0))
    return out, lnz, g


def prep(stratum_dir, core_dir, tag):
    st = pathlib.Path(stratum_dir); _CORE["dir"] = str(core_dir)
    wf_rows.products = products; wf_rows.seed_masses = seed_masses
    os.environ["WF_STRATA"] = f"{st.name}=1.0"
    wf_rows.prep(str(SM), str(st.parent), "-", tag)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text())
    info["check_vs_option_table_0019_max_abs"] = _CORE.get("worst"); info["core_dir"] = str(core_dir); info["scheme"] = "00:19 two-factor table (option_table_0019)"
    info["lnZ_check_max_abs"] = _CORE.get("worst")
    pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))
    print("check vs option_table_0019 max abs", _CORE.get("worst"), flush=True)


def render(tag, label, settling_commit, eof_commit, which):
    import matplotlib; matplotlib.use("Agg")
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = wf_rows.grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij")
    T = np.fromfile(f"field/{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}_elements.f64", "<f8").reshape(-1, 8)
    P = info["products"]; st = info["strata"][0]
    if which == "core": sel = [j for d in DS for j, p in enumerate(P) if p["D"] == d and p["cell"] == "total" and p["subset"] == "all"]; ncol = 3
    elif which == "cause": sel = [j for c in ("C1", "C2 silent") for d in DS for j, p in enumerate(P) if p["D"] == d and p["cell"] == c]; ncol = 6
    else: sel = [j for F, _ in wf_rows.FAMS for d in DS for j, p in enumerate(P) if p["D"] == d and p["cell"] == "total" and p["subset"] == F]; ncol = 6
    def title(p):
        t = SHORT[p["D"]] if which != "core" else DNAME[p["D"]]
        if p["cell"] == "C1": t += " · fuel-exhaustion log-on"
        if p["cell"] == "C2 silent": t += " · other log-on cause"
        if p["subset"] in ("A1", "A2", "B"): t += f" · {p['subset']}"
        return t
    names = [title(P[j]) for j in sel]; letters = "abcdefghijklmnopqrstuvwxyz"
    _wr = any(len(f"(a) {n}") > 54 for n in names)
    g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": str(HERE / "reference-arcs-run.json"), "NCOL": ncol,
         "OUTSTEM": f"settling-seabed-wreckage-{label}-{which}", "STAMP": "Not yet estimable",
         "TITLES_W": {n: __import__("textwrap").fill(f"({letters[q]}) {n}", 54) for q, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {}, "PANEL_NOTE": {}, "ESS_WORD": "row ESS", "HSPACE": 0.30 if _wr else 0.20, "TOP_EXTRA": 0.15 if _wr else 0.0}
    for n, j in zip(names, sel):
        g["SRC"][n] = (T, z[f"rows_{j}"], z[f"draws_{j}"], EL)
        Hm = np.load(f"field/{tag}_H_{j}.npy").astype(np.float64); nz = Hm > 0; g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
        g["ESS"][n] = P[j]["row_ess_kish"]
        if P[j]["subset"] in ("A1", "A2", "B"): g["PANEL_NOTE"][n] = f"share of the treatment {100 * P[j]['share_of_option']:.0f} %"
    sname = {"next-i-waypoints": "waypoint routes", "next-i-free": "free flight", "next-i-descent-climb": "descent-climb", "next-i-repro-radar": "Davey dynamics with radar"}.get(st, st)
    g["TITLE"] = {"core": f"Where the wreckage is on the seabed, for each use of the 00:19 satellite data ({sname})",
                  "cause": f"Where the wreckage is on the seabed, by cause of the 00:19 log-on ({sname})",
                  "family": f"Where the wreckage is on the seabed, by type of flight end ({sname})"}[which]
    g["SUBTITLE"] = {"core": "Both log-on causes together (fuel exhaustion 3 : 1 other); the aircraft did not break up before 00:19:37",
                     "cause": "Top row: log-on after fuel exhaustion. Bottom row: other log-on cause, aircraft silent after 00:19",
                     "family": "Rows: A1 fuel exhaustion, then no control; A2 fuel exhaustion, then controlled to the surface; B deliberate descent before fuel exhaustion"}[which]
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. Each map uses one way to read the "
                     "00:19 satellite data. The flight model is not yet stable, so these areas can change. When the aircraft breaks up in the air, the model still puts the "
                     "wreckage at one impact point.")
    g["FOOT_TECH"] = (f"Settled-mass seabed density (real ocean: GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10; GLORYS12V1 surface current; ERA5 wind; AusSeabed then GEBCO_2026), "
                      f"settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight run I, stratum {st} only (conditional on it; "
                      f"8 seeds; binary mh370-eof-ri1; EoF tools {eof_commit}). Row mass = end of flight's 00:19 two-factor table (option_table_0019 seed_terms, per-seed ln Z "
                      f"reproduced to {info['check_vs_option_table_0019_max_abs']:.0e}): hand-off weight x survival (1 - P(breakup by 00:19:37)) x L(D) x L(cause); "
                      "both causes q = 1/3 with C2 silent, W = 00:10:58-01:15:56. D3 = R600 BTO + both BFOs as recorded; D4 = both BFOs, Holland transient bias added; "
                      "D5 = R600 BFO as recorded + R1200 BFO, Holland transient bias added U[17, 130] Hz. Systematic resample over all rows, one settling draw each: "
                      + ", ".join(sorted({f"{P[j]['N']:,}" for j in sel})) + ". 0.02 deg grid, Gaussian 0.1 deg, HPD. Row ESS by Kish; below 1,000 not estimable. "
                      "Labels: core run I split-half NOT converged (waypoints 0.916 against floor 0.924); piloted-turn model and INTERIM pitch-down PROVISIONAL; "
                      "in-flight structural outcome PROVISIONAL; breakup rows settled from the intact impact point (G-bf); P(left) = 0.8 PROVISIONAL; Mac, 2 threads.")
    exec(open(HERE / "wreckage_map_standard.py").read(), g)




def publish(tag, label, outdir):
    """Move the stratum's samples and figures to the exchange; README with COVERAGE; SHA256SUMS; READY."""
    import shutil, hashlib, datetime
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); P = info["products"]; st = info["strata"][0]
    O = {}
    for which in ("core", "cause", "family"):
        for k, v in json.loads(pathlib.Path(f"settling-seabed-wreckage-{label}-{which}.json").read_text())["options"].items(): O[(which, k)] = v
    def find(j):
        p = P[j]
        for (which, k), v in O.items():
            t = (SHORT[p["D"]] if which != "core" else DNAME[p["D"]]) + {"C1": " · fuel-exhaustion log-on", "C2 silent": " · other log-on cause"}.get(p["cell"], "") + (f" · {p['subset']}" if p["subset"] != "all" else "")
            if t == k and ((which == "core") == (p["cell"] == "total" and p["subset"] == "all")): return v
        return None
    rows, gaps = [], []
    for j, p in enumerate(P):
        v = find(j); e = p["row_ess_kish"]
        a = v["area_km2_99_90_50"] if v else None
        rows.append(f"| P{j:02d} | {DNAME[p['D']]} | {p['cell']} | {p['subset']} | {p['N']:,} | {e:,.0f} | {100 * p['share_of_option'] * {'C1': 0.75, 'C2 silent': 0.25}.get(p['cell'], 1.0):.1f} % | "
                    + (f"{a['impact_resampled'][1] / 1e3:.1f} -> {a['wreckage_field'][1] / 1e3:.1f} | {' / '.join(f'{x:.2f}' for x in v['settled_offset_km_p50_p90_p99_mass_weighted'])} | {v['not_computed_impacts']}" if v else "- | - | -")
                    + f" | {'yes' if e >= 1000 else 'NO'} |")
        if e < 1000: gaps.append(f"{DNAME[p['D']]} x {p['cell']} x {p['subset']}: row ESS {e:,.0f}")
    lnz = info.get("per_seed_lnZ", {})
    txt = f"""Ocean settling - seabed wreckage samples on end of flight's run I, stratum {st} (CONDITIONAL on this stratum), {datetime.datetime.utcnow():%Y-%m-%d %H:%MZ}.
Settling hypothesis/settling 9330d4c (real ocean, 75-115 E, 45-10 S); end-of-flight tools {open(HERE / 'eof-smoke-commit.txt').read().strip()}, binary mh370-eof-ri1.
PROVISIONAL, NOT CONVERGED (core run I split-half: waypoints 0.916 against floor 0.924; other strata below). Core posterior share of
this stratum: see core/run-i/README.md (waypoints 0.9982). Mix strata by core share x Z per cell (per-seed ln Z below / in the info json).

ROW MASS = end of flight's 00:19 two-factor table (smoke/option_table_0019.py seed_terms), per seed: hand-off weight / sum / K x
survival factor x L(D) x L(cause). Per-cell per-seed ln Z equals seed_terms' to {info['check_vs_option_table_0019_max_abs']:.0e} (asserted, every seed, both passes).
Primary cell = both log-on causes, q = 1/3, C2 silent (q = prior odds C2:C1, so P(C1) = p = 1/(1+q) = 0.75, P(C2) = 0.25, option_table_0019 line 4), W = 00:10:58-01:15:56. D4 / D5: Holland transient bias added (wording rule 18:15Z).
Each product is a systematic resample over all rows of the 8 seeds: each (row, draw) outcome has weight 1/N - AVERAGE over outcomes.

Labels (carry): piloted-turn model and INTERIM pitch-down PROVISIONAL; in-flight structural outcome PROVISIONAL (no transonic drag rise);
BREAKUP ROWS SETTLED FROM THE INTACT IMPACT POINT (fragment field not modelled, gap G-bf); P(left) = 0.8 PROVISIONAL; breakup table PROVISIONAL.

Products (j indexes {tag}_draws.npz rows_<j>, draws_<j>, stratum_<j>, seed_<j>); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | cause | family | N | row ESS | posterior share within the treatment (cause rows: prior p x Z ratio, p = 0.75 / 0.25) | 90 % area | settled offset p50/p90/p99 km | not computed | estimable |
|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

COVERAGE
(a) Feasible set: as end of flight's run I note (piloted dives to about 40,000 ft/min, unloading, speeds past VMO/MMO, piloted turns,
    in-flight structural damage or breakup).
(b) Settling's reach: every row reaching the water as an intact impact. Declared reach gaps: G-bf (in-flight breakup rows settled from
    the intact impact point; real field spread along the descent, not modelled); attitude-dependent breakup (declared). Impacts
    refused by the ocean window are carried at the impact position (column 'not computed').
(c) Proposal coverage (row Kish ESS per product above; gate 1,000). Products below the gate (stamped not estimable in the figures):
""" + ("\n".join("    - " + x for x in gaps) if gaps else "    - none") + f"""

Per-seed ln Z per cell (for mixing strata and for end of flight's cross-check):
{json.dumps(lnz)}

Files: {tag}_impacts.f64 (f64, 14 columns: unix_s, lat, lon, v_east, v_north, v_up, flight-path angle, mass, KE, vertical KE, parent,
debris_class, draws, stratum*10+seed); {tag}_source.npy (int64: stratum index, seed, ROW INDEX into end-of-flight/run-i/{st}/seed-<k>/impacts32.npy);
{tag}_elements.f64 (f64, 8 columns: table row, draw, breakup family, class, fate (0 settled, 1 afloat, 2 not computed, -1 refused), lat, lon,
mass kg); {tag}_draws.npz; {tag}_info.json; figures settling-seabed-wreckage-{label}-{{core,cause,family}}.{{png,pdf,json}}.
Key outcomes as row * 2**20 + draw.
"""
    for f in [f"{tag}_impacts.f64", f"{tag}_elements.f64", f"{tag}_source.npy", f"{tag}_draws.npz", f"{tag}_info.json"]:
        shutil.move(f"field/{f}", out / f)
    for which in ("core", "cause", "family"):
        for ext in ("png", "pdf", "json"): shutil.copy(f"settling-seabed-wreckage-{label}-{which}.{ext}", out)
    (out / "README.txt").write_text(txt)
    lines = []
    for f in sorted(out.iterdir()):
        if f.name in ("SHA256SUMS", "READY"): continue
        h = hashlib.sha256()
        with open(f, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""): h.update(b)
        lines.append(f"{h.hexdigest()}  {f.name}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n"); (out / "READY").write_text(f"{datetime.datetime.utcnow():%Y-%m-%dT%H:%MZ}\n")
    print("published", out, flush=True)


def final(outroot, core_readme_shares):
    """Top-level README + stratum mixture weights per cell (core share x Z), after all strata are published."""
    import datetime
    from scipy.special import logsumexp
    root = pathlib.Path(outroot); shares = json.loads(core_readme_shares); mix = {}
    for st, P_s in shares.items():
        info = json.loads(next((root / st).glob("*_info.json")).read_text())
        for key, v in info["per_seed_lnZ"].items():
            _, name, cell = key.split("|"); mix.setdefault(f"{name} | {cell}", {})[st] = math.log(P_s) + float(logsumexp(v) - math.log(len(v)))
    w = {k: {st: float(np.exp(x - logsumexp(list(d.values())))) for st, x in d.items()} for k, d in mix.items()}
    (root / "stratum-mixture-weights.json").write_text(json.dumps({"core_shares": shares, "weights_per_cell": w}, indent=1))
    (root / "README.txt").write_text(f"""Ocean settling - run I seabed wreckage samples, {datetime.datetime.utcnow():%Y-%m-%d %H:%MZ}. One folder per stratum
(next-i-waypoints, next-i-free, next-i-descent-climb, next-i-repro-radar), each CONDITIONAL on its stratum, each with README.txt (incl.
COVERAGE), SHA256SUMS and READY. To mix strata for a cell, weight stratum s by stratum-mixture-weights.json weights_per_cell[cell][s]
(= core share x Z_s(cell), normalised) and, within a stratum, average its outcomes. Waypoints carries core's share 0.9982.
PROVISIONAL, NOT CONVERGED; labels and gaps in each stratum README.
""")
    (root / "READY").write_text(f"{datetime.datetime.utcnow():%Y-%m-%dT%H:%MZ}\n"); print("final", root, flush=True)


if __name__ == "__main__":
    {"prep": prep, "render": render, "publish": publish, "final": final}[sys.argv[1]](*sys.argv[2:])
