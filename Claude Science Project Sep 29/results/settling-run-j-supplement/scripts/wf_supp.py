"""Settling on end of flight's run J northern supplement, full rule-B set (work order overnight-2026-10-20 B1).

Input: end of flight's reduced impact table `end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz` (+ .json), the file its
README names for downstream modules: run J waypoints production (technique 0, 24 seeds) + all supplement rows (technique 1,
16 seeds, both halves) + extra descents (technique 2, D2-D5), one Horvitz-Thompson thinning, per-row ln weights
lnw:comb/<d> = rule B row mass / Z_d / pi (q = 1/3 total, C2 silent, survival factor; D3s-D5s = C2-silent arm only). Rule B and
the 64:256 extra-descent pooling are end of flight's (smoke/supplement_combine.py, supplement_reduced.py); this driver uses the
stored weights as they are, so the combination is exactly end of flight's.

Row mass per product = exp(lnw:comb/d) (masked by family or by impact north of 33 S). Products per d in D0'-D5: total N 40,000;
A1 / A2 / B N 10,000 (family4_code 1 / 2 / 3 as run J); impact north of 33 S N 10,000 (conditional; its share is recorded);
per D3s-D5s: total N 40,000. Systematic resample, one settling draw each (run J recipe, wf_rows.prep).
Impact columns for settling: unix_s = t_impact_s + T0 (compact time base, 2014-03-08 00:00 UTC), parent = handoff_row,
kinetic energies 0.5 m |v|^2 and 0.5 m v_up^2 (as compact_impacts.load): production rows therefore settle bit-identically to run J.

    python3 wf_supp.py prep <tag>
    python3 wf_supp.py render <tag> <label> <settling commit> core|family|north|other
    python3 wf_supp.py publish <tag> <label> <outdir>
"""
import sys, os, json, math, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
SM = HERE / "eof-engine/hypotheses/end-of-flight/smoke"
sys.path.insert(0, str(SM)); sys.path.insert(0, str(HERE))
import wf_rows, wf_runj as R

RED = pathlib.Path(os.environ.get("WF_RED", "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz"))
T0, T_M0019B = 1394236800.0, 1394237977.443
N_TOT, N_FAM, N_NORTH = 40000, 10000, 10000
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]; DSS = ["D3s", "D4s", "D5s"]
DNAME = dict(R.DNAME); SHORT = dict(R.SHORT)
for d in DSS:
    DNAME[d] = R.DNAME[d[:2]] + ", other log-on cause only"; SHORT[d] = R.SHORT[d[:2]] + ", other log-on cause only"
NORTH = -33.0
_Z = {}


def products(routes=()):
    P = []
    for d in DS:
        P.append(dict(option=DNAME[d], D=d, cell="total", ver="primary", subset="all", N=N_TOT))
        for F, _ in wf_rows.FAMS: P.append(dict(option=DNAME[d], D=d, cell="total", ver="primary", subset=F, N=N_FAM))
        P.append(dict(option=DNAME[d], D=d, cell="total", ver="primary", subset="north33", N=N_NORTH))
    for d in DSS: P.append(dict(option=DNAME[d], D=d, cell="C2 silent", ver="primary", subset="all", N=N_TOT))
    return P


def table():
    if not _Z:
        z = np.load(RED); _Z.update({k: z[k] for k in z.files})
    return _Z


def g_of():
    Z = table()
    def g(name):
        if name == "unix_s": return Z["t_impact_s"].astype(np.float64) + T0
        if name == "parent": return Z["handoff_row"].astype(np.float64)
        m, ve, vn, vu = (Z[k].astype(np.float64) for k in ("mass_kg", "velocity_east_mps", "velocity_north_mps", "velocity_up_mps"))
        if name == "kinetic_energy_j": return 0.5 * m * (ve ** 2 + vn ** 2 + vu ** 2)
        if name == "vertical_kinetic_energy_j": return 0.5 * m * vu ** 2
        return Z[name].astype(np.float64)
    return g


def seed_masses(sd, P, c, route_dir=None):
    Z = table(); g = g_of(); f4 = Z["family4_code"]; lat = Z["latitude_deg"].astype(np.float64); t = g("unix_s")
    out, lnz = [], {}
    for p in P:
        a = Z["lnw:comb/" + p["D"]].astype(np.float64)
        m = np.where(np.isfinite(a), np.exp(a), 0.0)
        if p["subset"] in ("A1", "A2", "B"): m = np.where(f4 == dict(wf_rows.FAMS)[p["subset"]], m, 0.0)
        elif p["subset"] == "north33": m = np.where(lat > NORTH, m, 0.0)
        nviol = int(((m > 0) & ~(t > T_M0019B)).sum()); assert nviol == 0, f"{nviol} positive-mass rows impact at or before 00:19:37.443"
        out.append(m)
        if p["subset"] == "all": lnz[(p["option"], p["cell"])] = float(np.log(m.sum()))
    return out, lnz, g


def prep(tag):
    root = HERE / "suproot"; (root / "ruleB" / "seed-1").mkdir(parents=True, exist_ok=True)
    wf_rows.products = products; wf_rows.seed_masses = seed_masses
    os.environ["WF_STRATA"] = "ruleB=1.0"
    wf_rows.prep(str(SM), str(root), "-", tag)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text())
    meta = json.loads(RED.with_suffix(".json").read_text())
    Z = table(); lat = Z["latitude_deg"].astype(np.float64); tech = Z["technique"]
    extra = {}
    for d in DS + DSS:
        w = np.exp(Z["lnw:comb/" + d].astype(np.float64)); wa = np.exp(Z["lnw:alone/" + d].astype(np.float64))
        e = {"sum_w_comb": float(w.sum()), "sum_w_alone": float(wa.sum()), "row_ess_comb": float(w.sum() ** 2 / (w ** 2).sum()),
             "row_ess_alone": float(wa.sum() ** 2 / (wa ** 2).sum()), "share_by_technique": [float(w[tech == k].sum() / w.sum()) for k in (0, 1, 2)], "bands": {}}
        for lo, hi in ((-35, -30), (-30, -25), (-25, -20), (-90, -33), (-33, 0)):
            key = f"{-lo}-{-hi} S" if lo > -90 else "south of 33 S"
            if hi == 0: key = "north of 33 S"
            s = (lat > lo) & (lat <= hi)
            for v, ww in (("comb", w), ("alone", wa)):
                x = ww[s]; e["bands"].setdefault(key, {})[v] = {"mass": float(x.sum() / ww.sum()), "row_ess": float(x.sum() ** 2 / (x ** 2).sum()) if (x > 0).any() else 0.0}
        extra[d] = e
    info.update(source=str(RED), source_rule=meta["rule"], source_rows=meta["rows"], lnw_sum_check=meta["lnw_sum_check"], impact_level=extra,
                scheme="end of flight's rule-B reduced table, stored weights lnw:comb/<d>", check_vs_option_table_0019_max_abs=None)
    pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))
    print("prep done; impact-level D3 north33", extra["D3"]["bands"]["north of 33 S"], flush=True)


def render(tag, label, settling_commit, which):
    import matplotlib, textwrap; matplotlib.use("Agg")
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); P = info["products"]
    sel = {"core": [j for d in DS for j, p in enumerate(P) if p["D"] == d and p["subset"] == "all"],
           "family": [j for F, _ in wf_rows.FAMS for d in DS for j, p in enumerate(P) if p["D"] == d and p["subset"] == F],
           "north": [j for d in DS for j, p in enumerate(P) if p["D"] == d and p["subset"] == "north33"],
           "other": [j for d in DSS for j, p in enumerate(P) if p["D"] == d]}[which]
    z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = wf_rows.grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij")
    T = np.fromfile(f"field/{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}_elements.f64", "<f8").reshape(-1, 8)
    def title(p):
        t = DNAME[p["D"]] if which in ("core", "other") else SHORT[p["D"]]
        if p["subset"] in ("A1", "A2", "B"): t += f" · {p['subset']}"
        if p["subset"] == "north33": t += " · impacts north of 33° S"
        return t
    names = [title(P[j]) for j in sel]; letters = "abcdefghijklmnopqrstuvwxyz"; ncol = 6 if which == "family" else 3
    g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": str(HERE / "reference-arcs-run.json"), "NCOL": ncol,
         "OUTSTEM": f"settling-seabed-wreckage-{label}-{which}", "STAMP": "Not yet estimable",
         "TITLES_W": {n: textwrap.fill(f"({letters[q]}) {n}", 54) for q, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {},
         "PANEL_NOTE": {}, "ESS_WORD": "row ESS", "HSPACE": 0.30, "TOP_EXTRA": 0.15}
    for n, j in zip(names, sel):
        g["SRC"][n] = (T, z[f"rows_{j}"], z[f"draws_{j}"], EL)
        Hm = np.load(f"field/{tag}_H_{j}.npy").astype(np.float64); nz = Hm > 0; g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
        g["ESS"][n] = P[j]["row_ess_kish"]
        if P[j]["subset"] != "all": g["PANEL_NOTE"][n] = f"share of the treatment {100 * P[j]['share_of_option']:.1f} %"
    sname = "waypoint routes, with the extra northern flights"
    g["TITLE"] = {"core": f"Where the wreckage is on the seabed, for each use of the 00:19 satellite data ({sname})",
                  "family": f"Where the wreckage is on the seabed, by type of flight end ({sname})",
                  "north": f"Where the wreckage is on the seabed when the aircraft hits the water north of 33° S ({sname})",
                  "other": f"Where the wreckage is on the seabed when the 00:19 log-on has another cause ({sname})"}[which]
    g["SUBTITLE"] = {"core": "Both log-on causes together (fuel exhaustion 3 : 1 other); the aircraft did not break up before 00:19:37",
                     "family": "Rows: A1 cruise to fuel exhaustion, then no control; A2 cruise to fuel exhaustion, then controlled descent; B planned descent with ditching approach begun before fuel exhaustion",
                     "north": "Each panel is conditional on an impact north of 33° S; its share of the treatment is given in the panel",
                     "other": "Log-on from another cause only (aircraft silent after 00:19); not mixed with fuel exhaustion"}[which]
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. Each map uses one way to read the "
                     "00:19 satellite data. The flight model now has more flights that end in the north; a known weight keeps the probabilities correct. Some parts of the "
                     "flight model are provisional, so these areas can change. When the aircraft breaks up in the air, the model still puts the wreckage at one impact point. "
                     "Search results and debris drift are not used here.")
    g["FOOT_TECH"] = (f"Settled-mass seabed density (real ocean: GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10; GLORYS12V1 surface current; ERA5 wind; AusSeabed then "
                      f"GEBCO_2026), settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight's rule-B reduced table "
                      f"(impacts-ruleB.npz, {info['source_rows']:,} rows): core run J waypoints production (24 seeds) + northern supplement (16 seeds, all rows) + "
                      "extra descents (D2-D5), combined by rule B with core's r_hat, one Horvitz-Thompson thinning; binary mh370-eof-rj1. Waypoints stratum only "
                      "(conditional on it). Row weight = end of flight's stored lnw:comb (hand-off weight x survival x L(00:19 treatment) x L(cause), both causes q = 1/3 "
                      "with C2 silent, W = 00:10:58-01:15:56; 'other log-on cause only' = C2-silent arm). D3 = R600 BTO + both BFOs as recorded; D4 = both BFOs, Holland "
                      "transient bias added; D5 = R600 BFO as recorded + R1200 BFO, Holland transient bias added U[17, 130] Hz; BFO error 4.3177 Hz. Systematic resample, "
                      "one settling draw each: " + ", ".join(sorted({f"{P[j]['N']:,}" for j in sel})) + ". 0.02 deg grid, Gaussian 0.1 deg, HPD. Row ESS by Kish; below "
                      "1,000 not estimable. Held Out is D0' (impact after 00:19:37.443 imposed). Prior track: core run J waypoint routes. Labels: core run J split-half "
                      "accepted as a pass by project ruling, 16 Oct 2026; uncontrolled-arm dynamics not calibrated (Boeing leave-one-out gate failed); piloted-turn model "
                      "and INTERIM pitch-down PROVISIONAL; in-flight structural outcome PROVISIONAL; breakup rows settled from the intact impact point (G-bf); "
                      "P(left) = 0.8 PROVISIONAL; Mac.")
    exec(open(HERE / "wreckage_map_standard.py").read(), g)


def publish(tag, label, outdir):
    import shutil, hashlib, datetime
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); P = info["products"]
    O = {}
    for which in ("core", "family", "north", "other"):
        for k, v in json.loads(pathlib.Path(f"settling-seabed-wreckage-{label}-{which}.json").read_text())["options"].items(): O[k] = v
    def key(p):
        t = DNAME[p["D"]] if (p["subset"] == "all") else SHORT[p["D"]]
        if p["subset"] in ("A1", "A2", "B"): t += f" · {p['subset']}"
        if p["subset"] == "north33": t += " · impacts north of 33° S"
        return t
    rows, gaps = [], []
    for j, p in enumerate(P):
        v = O.get(key(p)); e = p["row_ess_kish"]; a = v["area_km2_99_90_50"] if v else None
        rows.append(f"| P{j:02d} | {DNAME[p['D']]} | {p['subset']} | {p['N']:,} | {e:,.0f} | {100 * p['share_of_option']:.2f} % | "
                    + (f"{a['impact_resampled'][1] / 1e3:.1f} -> {a['wreckage_field'][1] / 1e3:.1f} | {' / '.join(f'{x:.2f}' for x in v['settled_offset_km_p50_p90_p99_mass_weighted'])} | {v['not_computed_impacts']}" if v else "- | - | -")
                    + f" | {'yes' if e >= 1000 else 'NO'} |")
        if e < 1000: gaps.append(f"{DNAME[p['D']]} x {p['subset']}: row ESS {e:,.0f}")
    txt = f"""Ocean settling - seabed wreckage samples on end of flight's run J northern supplement, full rule-B set, {datetime.datetime.utcnow():%Y-%m-%d %H:%MZ}.
CONDITIONAL on the waypoints stratum (core share 0.9982). Work order threads/work-orders/overnight-2026-10-20.md B1.
Settling hypothesis/settling 9330d4c (real ocean, 75-115 E, 45-10 S; unchanged since run I). Results note:
Claude Science Project Sep 29/results/settling-run-j-supplement/README.md.
Core run J split-half accepted as a pass by project ruling, 16 Oct 2026. D0 = D0' (impact after 00:19:37.443 imposed; checked).
CAVEAT (end of flight, verbatim): the uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.

INPUT: end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz ({info['source_rows']:,} rows; the file end of flight names for
downstream modules): run J production + all supplement rows + extra descents (D2-D5), rule B with core's r_hat, one
Horvitz-Thompson thinning. ROW MASS = exp(lnw:comb/<d>) as stored (no re-weighting here). Products: per D0'-D5 total (N 40,000),
A1 / A2 / B (N 10,000; family4_code 1 / 2 / 3; code 6 'other', 0.1-0.2 %, is in the totals only), impacts north of 33 S
(N 10,000, CONDITIONAL; share in the table); per D3s-D5s ('other log-on cause only', C2-silent arm) total (N 40,000).
Each product is a systematic resample, one settling draw each: AVERAGE over outcomes (equal weight 1/N).
A1 under D3 here rests on the unconditional rule-B rows (row ESS below the gate): for A1 under D3-D5 use the stratified A1
products in settling/run-j-a1branch/ (run J paths) or this folder's a1-stratified/ subfolder if present (see its README).

Products (j indexes {tag}_draws.npz rows_<j>, draws_<j>); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | subset | N | row ESS | share within the treatment | 90 % area | settled offset p50/p90/p99 km | not computed | estimable |
|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

COVERAGE
(a) Feasible set: as end of flight's run J and supplement notes (piloted dives to about 40,000 ft/min, unloading, speeds past
    VMO/MMO, piloted turns, in-flight structural damage or breakup; overbank above 90 deg a declared reach gap there).
(b) Settling's reach: every row reaching the water, settled as an intact impact. Reach gaps: G-bf (in-flight breakup rows settled
    from the intact impact point); attitude-dependent breakup (declared); impact pitch not used (G6).
(c) Proposal coverage (row Kish ESS on the reduced table per product above; gate 1,000). Products below the gate:
""" + ("\n".join("    - " + x for x in gaps) if gaps else "    - none") + f"""
    End of flight's distinct-state band ESS (full set) is the authoritative northern coverage figure: results/eof-run-j-supplement-oct20.

Files: {tag}_impacts.f64 (f64, 14 columns: unix_s, lat, lon, v_east, v_north, v_up, flight-path angle, mass, KE, vertical KE,
parent (= handoff_row), debris_class, draws, 0*10+1); {tag}_source.npy (int64: 0, 1, ROW INDEX into reduced/impacts-ruleB.npz);
{tag}_elements.f64 (8 columns: table row, draw, breakup family, class, fate (0 settled, 1 afloat), lat, lon, mass kg);
{tag}_draws.npz; {tag}_info.json (products, impact-level band masses and ESS, comb and alone); figures settling-seabed-wreckage-{label}-{{core,family,north,other}}.{{png,pdf,json}}.
"""
    for f in [f"{tag}_impacts.f64", f"{tag}_elements.f64", f"{tag}_source.npy", f"{tag}_draws.npz", f"{tag}_info.json"]:
        shutil.move(f"field/{f}", out / f)
    for which in ("core", "family", "north", "other"):
        for ext in ("png", "pdf", "json"): shutil.copy(f"settling-seabed-wreckage-{label}-{which}.{ext}", out)
    (out / "README.txt").write_text(txt)
    lines = []
    for f in sorted(out.iterdir()):
        if f.name in ("SHA256SUMS", "READY") or f.is_dir(): continue
        h = hashlib.sha256()
        with open(f, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""): h.update(b)
        lines.append(f"{h.hexdigest()}  {f.name}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    print("published (READY not yet written)", out, flush=True)


if __name__ == "__main__":
    {"prep": prep, "render": render, "publish": publish}[sys.argv[1]](*sys.argv[2:])
