"""Settling on the run J northern supplement, A1 by end of flight's two conditional strata (overnight-2026-10-20 B1, part 2).

End of flight's stratified A1 (results/eof-run-j-supplement-oct20 section 3; smoke/supplement_a1_outside.py, 45ea4af0):
    Z(d, A1) = Z(D0') [ P1 E_D0'[L_d | b1] + P2 E_D0'[L_d 1_A1 | b2] ]
b1 = onset flame-out-associated & control 'no intervention'; b2 = flame-out-associated & recovery attempted (A1 = its undemonstrated
part). P1, P2 = rule-B branch probabilities under D0' from end of flight's full set (a1-strata.json); Z from summary-full.json.
E1 from the branch-1 pass rows, combined by rule B exactly as end of flight's parts (supplement_combine.row_terms; production part
run-j-a1branch seeds 1-8, u1 = w/8, beta1 = N1/(N1 + N2 r); supplement part north-k2-a1branch, u2 = K w/16 with K = 2,
beta2 = N2 r/(N1 + N2 r); N1 = the 8 seeds' hand-off rows, N2 = 800,004; r = core's r_hat). E2 from the outside pass
(run-j-a1outside seeds 1-8, production alone, u = w/8).
Row by row, in the units of the reduced table's normalised weights under treatment d:
    pass-1 row:  m1_d / S1_D0 x P1 x Z_D0 / Z_d        pass-2 row (A1 only): m2_d 1_A1 / S2_D0 x P2 x Z_D0 / Z_d
    reduced-table row: exp(lnw:comb/d), set to 0 inside b1 and inside (b2 and A1)   [replaced by the strata]
Products per d: A1 (N 10,000) for D0'-D5 and D3s-D5s; total with A1 stratified (N 20,000) for D3-D5 and D3s-D5s.
CHECK: branch-1 and outside shares reproduce a1-strata.json (asserted to 1e-6 relative).

    python3 wf_supp_a1.py pass0 <tag>     python3 wf_supp_a1.py prep <tag>     python3 wf_supp_a1.py render <tag> <label> <commit> a1|total
    python3 wf_supp_a1.py publish <tag> <label> <outdir>
"""
import sys, os, json, math, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
SM = HERE / "eof-engine-45ea4af0/hypotheses/end-of-flight/smoke"
sys.path.insert(0, str(SM)); sys.path.insert(0, str(HERE))
import wf_rows, wf_supp as WS
sys.path.insert(0, str(SM))   # the 45ea4af0 smoke tools must win over the 4605cc21 copy that wf_supp/wf_runj put on the path

EX = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight")
SUPP = EX / "run-j-supplement"; CORE = pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo")
A1S = json.loads((SUPP / "summary-oct20/a1-strata.json").read_text()); SUMF = json.loads((SUPP / "summary-oct20/summary-full.json").read_text())
P1, P2 = A1S["P_D0prime"]["branch1_ruleB"], A1S["P_D0prime"]["branch2_ruleB"]
LNZ = {d: SUMF["cells"][d]["comb"]["imp"]["lnZ"] for d in SUMF["cells"]}
CELLS = ["D0", "D1", "D2", "D3", "D4", "D5", "D3s", "D4s", "D5s"]
N2_B1, K_B1 = 800004.0, 2.0
_C = {}


def strata_dirs():
    return {"b1p": EX / "run-j-a1branch/run-j-waypoints", "b1s": SUPP / "north-k2-a1branch", "b2": SUPP / "run-j-a1outside"}


def handoff_of(src, sd):
    return (CORE / sd.name / "handoff-m0011" / "handoff.npy") if src in ("b1p", "b2") else (sd / "handoff-subset.npy")


def seeds(d):
    return sorted((p for p in pathlib.Path(d).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name.split("-")[1]))


def raw_masses(src, sd):
    """Unnormalised pass row masses m_d (rule B for branch 1, production alone for branch 2) and labels."""
    from supplement_combine import row_terms, r_hat
    R = row_terms(sd, handoff_of(src, sd))
    if src == "b2": c = np.full(len(R["lat"]), 1.0 / 8)
    else:
        N1 = _C["N1"]; r = r_hat(R["lat0011"]); b1 = N1 / (N1 + N2_B1 * r); b2 = N2_B1 * r / (N1 + N2_B1 * r)
        c = b1 / 8 if src == "b1p" else b2 * K_B1 / 16
    m = {d: np.where(np.isfinite(R["t"][d]), np.exp(R["t"][d]) * c, 0.0) for d in CELLS}
    return m, R


def pass0(tag):
    _C["N1"] = float(sum(len(np.load(CORE / sd.name / "handoff-m0011" / "handoff.npy", mmap_mode="r")) for sd in seeds(strata_dirs()["b1p"])))
    S = {"N1_branch1_production": _C["N1"], "sum": {}, "check": {}}
    tot = {src: {d: 0.0 for d in CELLS} for src in strata_dirs()}; a1 = {d: 0.0 for d in CELLS}
    for src, root in strata_dirs().items():
        for sd in seeds(root):
            m, R = raw_masses(src, sd); br = R["br"]; f4 = R["f4"]
            want = 1 if src != "b2" else 2
            assert not (m["D0"][br != want] > 0).any(), f"{sd}: positive-mass row outside branch {want}"
            for d in CELLS:
                tot[src][d] += float(m[d].sum())
                if src == "b2": a1[d] += float(m[d][f4 == 1].sum())
            print("pass0", src, sd.name, len(br), flush=True)
    S1 = tot["b1p"]["D0"] + tot["b1s"]["D0"]; S2 = tot["b2"]["D0"]
    S.update(S1_D0=S1, S2_D0=S2, P1=P1, P2=P2, lnZ=LNZ)
    for d in CELLS:
        sh1 = math.exp(LNZ["D0"] - LNZ[d]) * P1 * (tot["b1p"][d] + tot["b1s"][d]) / S1
        sh2 = math.exp(LNZ["D0"] - LNZ[d]) * P2 * a1[d] / S2
        ref = A1S["cells"].get(d)
        S["check"][d] = {"branch1_share": sh1, "outside_share": sh2, "eof_branch1": ref["branch1_share"] if ref else None, "eof_outside": ref["outside_share"] if ref else None}
        if ref:
            assert abs(sh1 / ref["branch1_share"] - 1) < 1e-6, (d, sh1, ref["branch1_share"])
            if ref["outside_share"] > 0: assert abs(sh2 / ref["outside_share"] - 1) < 1e-6 or abs(sh2 - ref["outside_share"]) < 1e-12, (d, sh2, ref["outside_share"])
    pathlib.Path("field").mkdir(exist_ok=True); pathlib.Path(f"field/{tag}_pass0.json").write_text(json.dumps(S, indent=1))
    for d, c in S["check"].items(): print(d, {k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()}, flush=True)


def products(routes=()):
    P = []
    for d in CELLS:
        nm = WS.DNAME[d]
        if d in ("D3", "D4", "D5", "D3s", "D4s", "D5s"): P.append(dict(option=nm, D=d, cell="total", ver="primary", subset="all", N=20000))
        else: P.append(dict(option=nm, D=d, cell="total", ver="primary", subset="all", N=0))   # share reference only, not resampled
        P.append(dict(option=nm, D=d, cell="total", ver="primary", subset="A1", N=10000))
    return P


def seed_masses(sd, P, c, route_dir=None):
    src = sd.parent.name; p0 = _C["p0"]; out = []; lnz = {}
    if src == "main":
        Z = WS.table(); g = WS.g_of(); f4 = Z["family4_code"]
        om, cr, ra = Z["latent:onset_mechanism"], Z["latent:control_realised"], Z["latent:recovery_attempted"]
        br = np.select([(om == 2) & (cr == 2), (om == 2) & (ra == 1)], [1, 2], 0)
        rest = ~((br == 1) | ((br == 2) & (f4 == 1)))
        for p in P:
            a = Z["lnw:comb/" + p["D"]].astype(np.float64); m = np.where(np.isfinite(a), np.exp(a), 0.0) * rest
            if p["subset"] == "A1": m = np.where(f4 == 1, m, 0.0)
            out.append(m)
        t = g("unix_s")
    else:
        from compact_impacts import load
        m, R = raw_masses(src, sd); _, gg = load(sd); f4 = R["f4"]
        g = lambda n: gg(n)
        S = p0["S2_D0"] if src == "b2" else p0["S1_D0"]; Pb = P2 if src == "b2" else P1
        for p in P:
            k = math.exp(LNZ["D0"] - LNZ[p["D"]]) * Pb / S
            mm = m[p["D"]] * k
            if src == "b2": mm = np.where(f4 == 1, mm, 0.0)
            out.append(mm)
        t = gg("unix_s")
    for mm in out:
        assert not ((mm > 0) & ~(t > WS.T_M0019B)).any(), f"{sd}: positive-mass row at or before 00:19:37.443"
    return out, lnz, g


def prep(tag):
    _C["p0"] = json.loads(pathlib.Path(f"field/{tag}_pass0.json").read_text()); _C["N1"] = _C["p0"]["N1_branch1_production"]
    root = HERE / "suproot2"; (root / "main" / "seed-1").mkdir(parents=True, exist_ok=True)
    for k, v in strata_dirs().items():
        if not (root / k).exists(): (root / k).symlink_to(v)
    wf_rows.products = products; wf_rows.seed_masses = seed_masses
    os.environ["WF_STRATA"] = "main=1.0,b1p=1.0,b1s=1.0,b2=1.0"
    wf_rows.prep(str(SM), str(root), "-", tag)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text())
    for p in info["products"]:
        if p["subset"] == "A1" and p["D"] in A1S["cells"]: p["eof_A1_share_stratified"] = A1S["cells"][p["D"]]["A1_share_stratified"]
    info.update(pass0=_C["p0"], source_reduced=str(WS.RED), eof_tools="45ea4af0", check_vs_option_table_0019_max_abs=None,
                strata_note="stratum 0 reduced rule-B table (rows outside branch 1 and outside branch 2 x A1); 1 run-j-a1branch; 2 north-k2-a1branch; 3 run-j-a1outside (A1 rows only)")
    pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))
    print("prep done", flush=True)


def render(tag, label, settling_commit, which):
    """Maps: 'a1' = A1 per treatment (9 panels), 'total' = all families with A1 stratified (6 panels)."""
    import matplotlib, textwrap; matplotlib.use("Agg")
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); P = info["products"]
    sel = [j for d in CELLS for j, p in enumerate(P) if p["D"] == d and p["N"] > 0 and p["subset"] == ("A1" if which == "a1" else "all")]
    z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = wf_rows.grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij")
    T = np.fromfile(f"field/{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}_elements.f64", "<f8").reshape(-1, 8)
    title = lambda p: (WS.SHORT[p["D"]] + " · A1") if p["subset"] == "A1" else WS.DNAME[p["D"]]
    names = [title(P[j]) for j in sel]; letters = "abcdefghijklmnopqrstuvwxyz"
    g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": str(HERE / "reference-arcs-run.json"), "NCOL": 3,
         "OUTSTEM": f"settling-seabed-wreckage-{label}-{which}", "STAMP": "Not yet estimable",
         "TITLES_W": {n: textwrap.fill(f"({letters[q]}) {n}", 54) for q, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {},
         "PANEL_NOTE": {}, "ESS_WORD": "row ESS", "HSPACE": 0.30, "TOP_EXTRA": 0.15}
    for n, j in zip(names, sel):
        g["SRC"][n] = (T, z[f"rows_{j}"], z[f"draws_{j}"], EL)
        Hm = np.load(f"field/{tag}_H_{j}.npy").astype(np.float64); nz = Hm > 0; g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
        g["ESS"][n] = P[j]["row_ess_kish"]
        if P[j]["subset"] == "A1": g["PANEL_NOTE"][n] = f"share of the treatment {100 * P[j]['share_of_option']:.1f} %"
    g["TITLE"] = {"a1": "Where the wreckage is on the seabed after cruise to fuel exhaustion, then no control (A1), with the extra northern flights",
                  "total": "Where the wreckage is on the seabed, all types of flight end, with the extra northern flights and better sampling of A1"}[which]
    g["SUBTITLE"] = {"a1": "A1 = cruise to fuel exhaustion, then no control; waypoint routes; two extra runs sample only A1 and a known weight keeps the probabilities correct",
                     "total": "The part A1 (cruise to fuel exhaustion, then no control) comes from two extra runs that sample only A1"}[which]
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. Each map uses one way to read the "
                     "00:19 satellite data. Two extra flight-end runs sample only the case 'cruise to fuel exhaustion, then no control' (A1); their results replace that "
                     "part of the main flights, and a known weight keeps the probabilities correct. Some parts of the flight model are provisional. When the aircraft "
                     "breaks up in the air, the model still puts the wreckage at one impact point. Search results and debris drift are not used here.")
    g["FOOT_TECH"] = (f"Settled-mass seabed density (GLORYS12V1 75-115 E, 45-10 S, TEOS-10; ERA5; AusSeabed then GEBCO_2026), settling {settling_commit}, breakup table "
                      "PROVISIONAL, afloat pieces excluded. Impacts: end of flight's rule-B reduced table (run J waypoints production + northern supplement + extra "
                      "descents; mh370-eof-rj1) outside the A1 strata, plus branch 1 (flame-out-associated onset, no intervention: run-j-a1branch seeds 1-8 + "
                      "north-k2-a1branch, rule B, N1 = %d, N2 = 800,004, K = 2) and branch 2 (recovery attempted, A1 part: run-j-a1outside seeds 1-8, run J paths only), "
                      "stratified estimator Z(d, A1) = Z(D0') [P1 E1 + P2 E2], P1 = %.4f, P2 = %.4f (end of flight, 45ea4af0). Both causes q = 1/3 with C2 silent "
                      "('other log-on cause only' = C2-silent arm); D3 = R600 BTO + both BFOs as recorded; D4 = both BFOs, Holland transient bias added; D5 = R600 BFO "
                      "as recorded + R1200 BFO, Holland transient bias added U[17, 130] Hz; BFO error 4.3177 Hz. Systematic resample, one settling draw each. 0.02 deg "
                      "grid, Gaussian 0.1 deg, HPD. Row ESS by Kish; below 1,000 not estimable. Held Out is D0'. Prior track: core run J waypoint routes. Labels: core run "
                      "J split-half accepted as a pass by project ruling, 16 Oct 2026; uncontrolled-arm dynamics not calibrated; piloted-turn model and INTERIM "
                      "pitch-down PROVISIONAL; breakup rows settled from the intact impact point (G-bf); P(left) = 0.8 PROVISIONAL; Mac." % (int(info["pass0"]["N1_branch1_production"]), P1, P2))
    exec(open(HERE / "wreckage_map_standard.py").read(), g)


def publish(tag, label, outdir):
    import shutil, hashlib, datetime
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); P = info["products"]; p0 = info["pass0"]
    O = {}
    for which in ("a1", "total"):
        O.update(json.loads(pathlib.Path(f"settling-seabed-wreckage-{label}-{which}.json").read_text())["options"])
    rows, gaps = [], []
    for j, p in enumerate(P):
        if p["N"] == 0: continue
        k = (WS.SHORT[p["D"]] + " · A1") if p["subset"] == "A1" else WS.DNAME[p["D"]]; v = O.get(k); e = p["row_ess_kish"]; a = v["area_km2_99_90_50"] if v else None
        ref = p.get("eof_A1_share_stratified")
        rows.append(f"| P{j:02d} | {WS.DNAME[p['D']]} | {'A1' if p['subset'] == 'A1' else 'all families (A1 stratified)'} | {p['N']:,} | {e:,.0f} | {100 * p['share_of_option']:.2f} %"
                    + (f" (EoF {100 * ref:.2f} %)" if ref is not None and p["subset"] == "A1" else "") + " | "
                    + (f"{a['impact_resampled'][1] / 1e3:.1f} -> {a['wreckage_field'][1] / 1e3:.1f} | {v['not_computed_impacts']}" if v else "- | -") + f" | {'yes' if e >= 1000 else 'NO'} |")
        if e < 1000: gaps.append(f"{WS.DNAME[p['D']]} x {p['subset']}: row ESS {e:,.0f}")
    chk = "\n".join(f"    {d}: branch 1 share {c['branch1_share']:.6f} (EoF {c['eof_branch1']}), outside share {c['outside_share']:.6f} (EoF {c['eof_outside']})" for d, c in p0["check"].items())
    txt = f"""Ocean settling - A1 by end of flight's two conditional strata on the run J northern supplement (rule B), {datetime.datetime.utcnow():%Y-%m-%d %H:%MZ}.
CONDITIONAL on the waypoints stratum. Work order overnight-2026-10-20 B1 (part 2). Settling 9330d4c; end-of-flight tools 45ea4af0.
Use these A1 products (and the totals with A1 stratified, D3-D5 and D3s-D5s) in place of the unconditional A1 / totals in ../ruleB-waypoints
for A1 under D3-D5. A2 and B: ../ruleB-waypoints.
Stratified estimator (end of flight, results/eof-run-j-supplement-oct20 section 3): Z(d, A1) = Z(D0') [P1 E_D0'[L_d | b1] + P2 E_D0'[L_d 1_A1 | b2]],
P1 = {P1:.6f}, P2 = {P2:.6f} (rule B, a1-strata.json); b1 = flame-out-associated onset + no intervention (passes run-j-a1branch seeds 1-8 and
north-k2-a1branch, rule B: u1 = w/8, beta1 = N1/(N1 + N2 r), u2 = 2w/16, beta2 = N2 r/(N1 + N2 r), N1 = {int(p0['N1_branch1_production']):,}, N2 = 800,004, r = core r_hat);
b2 = flame-out-associated + recovery attempted, A1 part (pass run-j-a1outside seeds 1-8, run J paths, production alone u = w/8).
Reduced-table rows inside b1 or inside (b2 and A1) get mass 0; the strata replace them. Row masses in the reduced table's normalised units.
CHECK (asserted to 1e-6 relative): the strata shares reproduce end of flight's a1-strata.json:
{chk}

Products (j indexes {tag}_draws.npz); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | family | N | row ESS | share within the treatment | 90 % area | not computed | estimable |
|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

COVERAGE (c): products below the row-ESS gate of 1,000:
""" + ("\n".join("    - " + x for x in gaps) if gaps else "    - none") + f"""
    Branch 2 (A1 outside 'no intervention') rests on run J paths only: its northern tail is thin (end of flight: 191 / 45 / 36 distinct
    states in 35-30 / 30-25 / 25-20 S under D4). Under D3 and D5 branch 2 carries < 0.0001 of Z.
Files: {tag}_impacts.f64 (14 columns; column 14 AMBIGUOUS, use {tag}_source.npy: stratum 0 reduced table row index, 1 run-j-a1branch,
2 north-k2-a1branch, 3 run-j-a1outside, then seed, row index into that seed's impacts32.npy); {tag}_elements.f64; {tag}_draws.npz; {tag}_info.json;
figures settling-seabed-wreckage-{label}-{{a1,total}}.{{png,pdf,json}}.
"""
    for f in [f"{tag}_impacts.f64", f"{tag}_elements.f64", f"{tag}_source.npy", f"{tag}_draws.npz", f"{tag}_info.json"]:
        shutil.move(f"field/{f}", out / f)
    for which in ("a1", "total"):
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
    {"pass0": pass0, "prep": prep, "render": render, "publish": publish}[sys.argv[1]](*sys.argv[2:])
