"""Settling on end of flight's A1-branch conditional pass (`end-of-flight/run-j-a1branch/run-j-waypoints`, 8 seeds), combined
with run J waypoints production (`end-of-flight/run-j/run-j-waypoints`, 24 seeds) by end of flight's stratified estimator
(results/eof-a1-branch-oct18, smoke/a1_branch_estimate.py + a1_branch_combine.py). Work order overnight-2026-10-19 B1.

Branch = onset flame-out-associated (latent:onset_mechanism == 2) and control 'no intervention' (latent:control_realised == 2),
a subset of A1. The pass conditions the PRIOR on the branch, so for any likelihood l (00:19 treatment x cause x survival):
    sum_{production rows in branch} m_l  =  M_prod(D0', branch) x S_pass(l) / S_pass(D0')
with m = the run J settling row mass (wf_runj.seed_masses = option_table_0019 seed_terms, primary cell: both causes, q = 1/3,
C2 silent), S_pass the same mass summed over the pass (seeds pooled equally, each normalised by its UNTHINNED weight sum
thinning.weight_sum_in). Hence every pass row gets mass  m x SCALE,  SCALE = M_prod(D0', branch) / S_pass(D0')  (one scalar, all
treatments), and production rows IN the branch get mass 0. This is end of flight's estimator, row by row:
    Z(d, branch) = Z(D0') P_D0'(branch) E_D0'[L_d | branch].
Products per treatment d (D0'-D5, primary cell):
    total  (N 40,000) = production rows outside the branch + pass rows x SCALE           ('total, A1 stratified')
    A1     (N 10,000) = production A1 rows outside the branch (undemonstrated recoveries) + pass rows x SCALE
Checks: every positive-mass pass row is in the branch; the branch lies inside A1 in production; P_D0'(branch) and the stratified A1
share per treatment reproduce end of flight's a1-branch-combined.json (EoF normalises thinned seeds by the stored weight sum, this
driver by weight_sum_in as option_table_0019 does; the difference is reported).

    python3 wf_a1branch.py pass0 <prod dir> <pass dir> <core stratum dir> <tag> [nproc]
    python3 wf_a1branch.py prep  <core stratum dir> <tag>          (needs pass0 output; root a1root/{prod,pass} symlinks)
    python3 wf_a1branch.py render <tag> <label> <settling commit> <eof commit> core|a1
    python3 wf_a1branch.py publish <tag> <label> <outdir>
"""
import sys, os, json, math, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
SM = HERE / "eof-engine/hypotheses/end-of-flight/smoke"
sys.path.insert(0, str(SM)); sys.path.insert(0, str(HERE))
import wf_rows, wf_runj as R

N_TOT, N_FAM = int(os.environ.get("WF_N_TOT", 40000)), int(os.environ.get("WF_N_FAM", 10000))
DS = R.DS
SCALE = {}
SEEDS_PASS = 8


def products(routes=()):
    P = []
    for d in DS:
        P.append(dict(option=R.DNAME[d], D=d, cell="total", ver="primary", subset="all", N=N_TOT))
        P.append(dict(option=R.DNAME[d], D=d, cell="total", ver="primary", subset="A1", N=N_FAM))
    return P


def _base():
    return [dict(option=R.DNAME[d], D=d, cell="total", ver="primary", subset="all", N=1) for d in DS]


def _labels(g):
    from compact_impacts import family_labels
    br = (g("latent:onset_mechanism") == 2) & (g("latent:control_realised") == 2)
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    return br, f4


def seed_masses(sd, P, c, route_dir=None):
    src = sd.parent.name
    ms, lnz, g = R.seed_masses(sd, _base(), c)
    br, f4 = _labels(g); bm = dict(zip(DS, ms)); out = []
    if src == "pass":
        for d in DS: assert not (bm[d][~br] > 0).any(), f"{sd}: pass row outside the branch has positive mass ({d})"
    else:
        for d in DS: assert not (bm[d][br & (f4 != 1)] > 0).any(), f"{sd}: branch row not in A1"
    for p in P:
        m = bm[p["D"]]
        if src == "pass": mm = m * SCALE["k"]
        else: mm = np.where((~br) if p["subset"] == "all" else ((f4 == 1) & ~br), m, 0.0)
        out.append(mm)
    return out, lnz, g


def _pass0_seed(args):
    src, sd, core, K = args
    R._CORE["dir"] = core
    ms, lnz, g = R.seed_masses(pathlib.Path(sd), _base(), math.log(1.0 / K))
    br, f4 = _labels(g); r = {}
    for d, m in zip(DS, ms):
        r[d] = {"all": float(m.sum()), "branch": float(m[br].sum()), "A1": float(m[f4 == 1].sum()), "A1_out": float(m[(f4 == 1) & ~br].sum()),
                "A2": float(m[f4 == 2].sum()), "B": float(m[np.isin(f4, (3, 6))].sum()), "sq": float((m * m).sum()), "sq_branch": float((m[br] ** 2).sum())}
    return src, pathlib.Path(sd).name, r, float(R._CORE.get("worst", 0.0)), int(br.sum()), int(len(br))


def pass0(prod, pas, core, tag, nproc=4):
    from multiprocessing import Pool
    seeds = lambda d: sorted((p for p in pathlib.Path(d).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
    sp, ss = seeds(prod), seeds(pas); assert len(ss) == SEEDS_PASS, ss
    jobs = [("prod", str(s), core, len(sp)) for s in sp] + [("pass", str(s), core, len(ss)) for s in ss]
    with Pool(int(nproc)) as pool: T = pool.map(_pass0_seed, jobs, chunksize=1)
    out = {"prod": {}, "pass": {}, "worst_lnZ_check": max(t[3] for t in T), "branch_rows": {}}
    for src, k, r, _, nb, n in T: out[src][k] = r; out["branch_rows"][f"{src}/{k}"] = [nb, n]
    tot = lambda src, d, key: sum(v[d][key] for v in out[src].values())
    k = tot("prod", "D0", "branch") / tot("pass", "D0", "all"); out["SCALE"] = k
    out["P_D0_branch"] = tot("prod", "D0", "branch") / tot("prod", "D0", "all")
    eof = json.loads((HERE / "a1-branch-combined.json").read_text()) if (HERE / "a1-branch-combined.json").exists() else None
    out["cells"] = {}
    for d in DS:
        b = k * tot("pass", d, "all"); a1 = b + tot("prod", d, "A1_out"); allm = tot("prod", d, "all") - tot("prod", d, "branch") + b
        e = {"A1_share_stratified": a1 / allm, "A1_branch_share": b / allm, "A1_outside_share": tot("prod", d, "A1_out") / allm,
             "A1_share_production": tot("prod", d, "A1") / tot("prod", d, "all"),
             "A2_share_stratified": tot("prod", d, "A2") / allm, "B_share_stratified": tot("prod", d, "B") / allm,
             "ln_E_L_given_branch_pass": math.log(tot("pass", d, "all") / tot("pass", "D0", "all")) if tot("pass", d, "all") > 0 else None,
             "ln_E_L_given_branch_prod": math.log(tot("prod", d, "branch") / tot("prod", "D0", "branch")) if tot("prod", d, "branch") > 0 else None,
             "pass_branch_row_ess": tot("pass", d, "all") ** 2 / tot("pass", d, "sq"),
             "prod_branch_row_ess": tot("prod", d, "branch") ** 2 / tot("prod", d, "sq_branch") if tot("prod", d, "sq_branch") > 0 else 0.0,
             "pass_halves_A1_share": []}
        for half in ([f"seed-{i}" for i in range(1, 5)], [f"seed-{i}" for i in range(5, 9)]):
            sp_ = sum(out["pass"][s][d]["all"] for s in half) / sum(out["pass"][s]["D0"]["all"] for s in half) * tot("prod", "D0", "branch")
            e["pass_halves_A1_share"].append((sp_ + tot("prod", d, "A1_out")) / (tot("prod", d, "all") - tot("prod", d, "branch") + sp_))
        if eof and d in eof["cells"]:
            e["eof_A1_stratified"] = eof["cells"][d]["stratified"]["A1"]; e["diff_vs_eof"] = e["A1_share_stratified"] - e["eof_A1_stratified"]
        out["cells"][d] = e
    if eof: out["eof_P_D0_branch"] = eof["P_D0_branch"]
    pathlib.Path("field").mkdir(exist_ok=True); pathlib.Path(f"field/{tag}_pass0.json").write_text(json.dumps(out, indent=1))
    print("SCALE", k, "P_D0'(branch)", out["P_D0_branch"], "EoF", out.get("eof_P_D0_branch"), "worst lnZ check", out["worst_lnZ_check"], flush=True)
    for d, e in out["cells"].items():
        print(d, {x: (round(v, 4) if isinstance(v, float) else v) for x, v in e.items() if x != "pass_halves_A1_share"}, "halves", [round(x, 4) for x in e["pass_halves_A1_share"]], flush=True)


def prep(core_dir, tag):
    p0 = json.loads(pathlib.Path(f"field/{tag}_pass0.json").read_text()); SCALE["k"] = p0["SCALE"]
    R._CORE["dir"] = str(core_dir)
    wf_rows.products = products; wf_rows.seed_masses = seed_masses
    os.environ["WF_STRATA"] = "prod=1.0,pass=1.0"
    wf_rows.prep(str(SM), str(HERE / "a1root"), "-", tag)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text())
    info.update(check_vs_option_table_0019_max_abs=R._CORE.get("worst"), lnZ_check_max_abs=R._CORE.get("worst"), core_dir=str(core_dir),
                scheme="00:19 two-factor table (option_table_0019), A1 branch replaced by the A1-branch conditional pass (stratified estimator)",
                SCALE=p0["SCALE"], P_D0_branch=p0["P_D0_branch"], strata_note="stratum index 0 = run J waypoints production (rows outside the branch), 1 = A1-branch pass")
    # internal consistency: A1 product share equals pass0's stratified share
    for p in info["products"]:
        if p["subset"] == "A1":
            want = p0["cells"][p["D"]]["A1_share_stratified"]; p["share_check_vs_pass0"] = p["share_of_option"] - want
            assert abs(p["share_of_option"] - want) < 1e-9, (p["D"], p["share_of_option"], want)
    pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))
    print("check vs option_table_0019 max abs", R._CORE.get("worst"), flush=True)


def render(tag, label, settling_commit, eof_commit, which):
    """wf_runj.render with this pass's product sets ('core' = totals, 'a1' = A1 per treatment) and its own labels."""
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text())
    P = info["products"]
    if which == "core": sel = [j for d in DS for j, p in enumerate(P) if p["D"] == d and p["subset"] == "all"]
    else: sel = [j for d in DS for j, p in enumerate(P) if p["D"] == d and p["subset"] == "A1"]
    return _render(info, tag, label, settling_commit, eof_commit, which, sel)


def _render(info, tag, label, settling_commit, eof_commit, which, sel):
    import matplotlib; matplotlib.use("Agg")
    z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = wf_rows.grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij")
    T = np.fromfile(f"field/{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}_elements.f64", "<f8").reshape(-1, 8)
    P = info["products"]
    def title(p):
        t = R.DNAME[p["D"]] if which == "core" else R.SHORT[p["D"]]
        return t + (" · A1" if p["subset"] == "A1" else "")
    names = [title(P[j]) for j in sel]; letters = "abcdefghijklmnopqrstuvwxyz"
    g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": str(HERE / "reference-arcs-run.json"), "NCOL": 3,
         "OUTSTEM": f"settling-seabed-wreckage-{label}-{which}", "STAMP": "Not yet estimable",
         "TITLES_W": {n: __import__("textwrap").fill(f"({letters[q]}) {n}", 54) for q, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {},
         "PANEL_NOTE": {}, "ESS_WORD": "row ESS", "HSPACE": 0.30, "TOP_EXTRA": 0.15}
    for n, j in zip(names, sel):
        g["SRC"][n] = (T, z[f"rows_{j}"], z[f"draws_{j}"], EL)
        Hm = np.load(f"field/{tag}_H_{j}.npy").astype(np.float64); nz = Hm > 0; g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
        g["ESS"][n] = P[j]["row_ess_kish"]
        if P[j]["subset"] == "A1": g["PANEL_NOTE"][n] = f"share of the treatment {100 * P[j]['share_of_option']:.1f} %"
    g["TITLE"] = {"core": "Where the wreckage is on the seabed, for each use of the 00:19 satellite data (waypoint routes; better sampling of uncontrolled flight)",
                  "a1": "Where the wreckage is on the seabed after fuel exhaustion with no control (A1), for each use of the 00:19 satellite data"}[which]
    g["SUBTITLE"] = {"core": "All types of flight end; the part 'fuel exhaustion, then no control' comes from an extra run that samples only that part",
                     "a1": "A1 = cruise to fuel exhaustion, then no control; waypoint routes; both log-on causes (fuel exhaustion 3 : 1 other)"}[which]
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. Each map uses one way to read "
                     "the 00:19 satellite data. An extra flight-end run samples only the case 'fuel exhaustion, then no control'; its results replace that part of the "
                     "main run, and a known scale factor keeps the probabilities correct. Some parts of the flight model are provisional, so these areas can change. "
                     "When the aircraft breaks up in the air, the model still puts the wreckage at one impact point. Search results are not used here.")
    g["FOOT_TECH"] = (f"Settled-mass seabed density (real ocean: GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10; GLORYS12V1 surface current; ERA5 wind; AusSeabed then "
                      f"GEBCO_2026), settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight run J waypoints stratum only "
                      f"(conditional on it), binary mh370-eof-rj1, EoF tools {eof_commit}: 24 production seeds outside the branch (onset flame-out-associated, no "
                      f"intervention) plus the A1-branch conditional pass (8 seeds x 100,000 hand-off particles, prior conditioned on the branch, D3-aimed scored "
                      f"selection with exact correction, seeds 2-8 Horvitz-Thompson thinned) with mass x {info['SCALE']:.4g} = M_prod(D0', branch) / S_pass(D0') "
                      f"(stratified estimator; P_D0'(branch) = {info['P_D0_branch']:.4f}). Row mass = end of flight's 00:19 two-factor table (option_table_0019 "
                      f"seed_terms; per-seed ln Z reproduced to {info['check_vs_option_table_0019_max_abs']:.0e}): hand-off weight x survival x L(D) x L(cause); "
                      "both causes q = 1/3 with C2 silent, W = 00:10:58-01:15:56. D3 = R600 BTO + both BFOs as recorded; D4 = both BFOs, Holland transient bias added; "
                      "D5 = R600 BFO as recorded + R1200 BFO, Holland transient bias added U[17, 130] Hz. Systematic resample, one settling draw each: "
                      + ", ".join(sorted({f"{P[j]['N']:,}" for j in sel})) + ". 0.02 deg grid, Gaussian 0.1 deg, HPD. Row ESS by Kish; below 1,000 not estimable. "
                      "Held Out is D0' (impact after 00:19:37.443 imposed). Prior track: core run J waypoint routes. No search evidence, no drift evidence. Labels: "
                      "core run J split-half accepted as a pass by project ruling, 16 Oct 2026; uncontrolled-arm dynamics not calibrated (Boeing leave-one-out gate "
                      "failed); piloted-turn model and INTERIM pitch-down PROVISIONAL; in-flight structural outcome PROVISIONAL; breakup rows settled from the intact "
                      "impact point (G-bf); P(left) = 0.8 PROVISIONAL; Mac.")
    exec(open(HERE / "wreckage_map_standard.py").read(), g)


def publish(tag, label, outdir):
    import shutil, hashlib, datetime
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); P = info["products"]
    p0 = json.loads(pathlib.Path(f"field/{tag}_pass0.json").read_text())
    O = {}
    for which in ("core", "a1"):
        for k, v in json.loads(pathlib.Path(f"settling-seabed-wreckage-{label}-{which}.json").read_text())["options"].items(): O[(which, k)] = v
    def find(p):
        k = (R.DNAME[p["D"]] if p["subset"] == "all" else R.SHORT[p["D"]] + " · A1")
        return O.get(("core" if p["subset"] == "all" else "a1", k))
    rows, gaps = [], []
    for j, p in enumerate(P):
        v = find(p); e = p["row_ess_kish"]; a = v["area_km2_99_90_50"] if v else None
        rows.append(f"| P{j:02d} | {R.DNAME[p['D']]} | {'all families (A1 stratified)' if p['subset'] == 'all' else 'A1'} | {p['N']:,} | {e:,.0f} | {100 * p['share_of_option']:.2f} % | "
                    + (f"{a['impact_resampled'][1] / 1e3:.1f} -> {a['wreckage_field'][1] / 1e3:.1f} | {' / '.join(f'{x:.2f}' for x in v['settled_offset_km_p50_p90_p99_mass_weighted'])} | {v['not_computed_impacts']}" if v else "- | - | -")
                    + f" | {'yes' if e >= 1000 else 'NO'} |")
        if e < 1000: gaps.append(f"{R.DNAME[p['D']]} x {p['subset']}: row ESS {e:,.0f}")
    chk = "\n".join(f"    {d}: A1 share stratified {c['A1_share_stratified']:.4f} (EoF {c.get('eof_A1_stratified', float('nan')):.4f}, diff {c.get('diff_vs_eof', float('nan')):+.1e}); "
                    f"production {c['A1_share_production']:.4f}; pass halves {c['pass_halves_A1_share'][0]:.4f} / {c['pass_halves_A1_share'][1]:.4f}; "
                    f"branch row ESS pass {c['pass_branch_row_ess']:,.0f} vs production {c['prod_branch_row_ess']:,.0f}" for d, c in p0["cells"].items())
    txt = f"""Ocean settling - seabed wreckage samples for end of flight's A1-branch conditional pass, combined with run J waypoints production
by the stratified estimator, {datetime.datetime.utcnow():%Y-%m-%d %H:%MZ}. CONDITIONAL on the waypoints stratum (core share 0.9982).
Settling hypothesis/settling 9330d4c (real ocean, 75-115 E, 45-10 S; unchanged since run I); end-of-flight tools {open(HERE / 'eof-smoke-commit.txt').read().strip()}, binary mh370-eof-rj1.
Work order: threads/work-orders/overnight-2026-10-19.md B1. Results note: Claude Science Project Sep 29/results/settling-run-j-a1branch/README.md.
Core run J split-half accepted as a pass by project ruling, 16 Oct 2026. D0 = D0' (impact after 00:19:37.443 imposed in every cell).
CAVEAT (end of flight, verbatim): the uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.

INPUTS: production = end-of-flight/run-j/run-j-waypoints seeds 1-24 (stratum index 0 in the tables); A1-branch pass =
end-of-flight/run-j-a1branch/run-j-waypoints seeds 1-8 (stratum index 1; seeds 2-8 Horvitz-Thompson thinned to ~1M rows, normalised
by thinning.weight_sum_in). Branch = onset flame-out-associated AND control 'no intervention' (subset of A1 = cruise to fuel
exhaustion, then no control).
ROW MASS: run J settling recipe (option_table_0019 seed_terms, primary cell: both log-on causes q = 1/3, C2 silent), seeds pooled
equally within each source. Production rows IN the branch get mass 0; pass rows get mass x SCALE = {p0['SCALE']:.6g}
= M_prod(D0', branch) / S_pass(D0'), one scalar for all treatments: Z(d, branch) = Z(D0') P_D0'(branch) E_D0'[L_d | branch].
P_D0'(branch) = {p0['P_D0_branch']:.5f} (end of flight {p0.get('eof_P_D0_branch', float('nan')):.5f}).
Products per treatment: 'all families (A1 stratified)' N 40,000 and 'A1' N 10,000 (A1 = pass rows + production A1 rows outside the
branch, i.e. undemonstrated recoveries). Each product is a systematic resample, one settling draw each: AVERAGE over outcomes.
A2 and B products are unchanged from settling/run-j/run-j-waypoints (no new rows there); their shares rescale as in end of flight's combine.

Products (j indexes {tag}_draws.npz rows_<j>, draws_<j>, stratum_<j>, seed_<j>); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | family | N | row ESS | share within the treatment | 90 % area | settled offset p50/p90/p99 km | not computed | estimable |
|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

CHECKS (stratified shares against end of flight's results/eof-a1-branch-oct18/a1-branch-combined.json):
{chk}

COVERAGE
(a) Feasible set: fuel exhaustion with no pilot input, every descent the 777 can show (spiral up to 90 deg bank, phugoid, steep dive), as
    end of flight's A1-branch note; the rest of the flight-end families as end of flight's run J note.
(b) Settling's reach: every row reaching the water, settled as an intact impact. Reach gaps: G-bf (in-flight breakup rows settled from
    the intact impact point); attitude-dependent breakup (declared); impact pitch not used (G6).
(c) Proposal coverage (row Kish ESS per product above; gate 1,000). Products below the gate:
""" + ("\n".join("    - " + x for x in gaps) if gaps else "    - none") + f"""
    Waypoints only: free flight, descent-climb and Davey dynamics with radar keep their run J A1 gaps under D3-D5 (no branch pass there).

Files: {tag}_impacts.f64 (f64, 14 columns as run J; column 14 = stratum*10+seed is AMBIGUOUS here (production seeds run to 24) - use {tag}_source.npy or the draws npz stratum_<j>/seed_<j> arrays);
{tag}_source.npy (int64: stratum index 0/1, seed, ROW INDEX into impacts32.npy of end-of-flight/run-j/run-j-waypoints/seed-<k> (0) or
end-of-flight/run-j-a1branch/run-j-waypoints/seed-<k> (1)); {tag}_elements.f64 (8 columns: table row, draw, breakup family, class, fate,
lat, lon, mass kg); {tag}_draws.npz; {tag}_info.json; {tag}_pass0.json (estimator terms); figures settling-seabed-wreckage-{label}-{{core,a1}}.{{png,pdf,json}}.
"""
    for f in [f"{tag}_impacts.f64", f"{tag}_elements.f64", f"{tag}_source.npy", f"{tag}_draws.npz", f"{tag}_info.json"]:
        shutil.move(f"field/{f}", out / f)
    shutil.copy(f"field/{tag}_pass0.json", out)
    for which in ("core", "a1"):
        for ext in ("png", "pdf", "json"): shutil.copy(f"settling-seabed-wreckage-{label}-{which}.{ext}", out)
    (out / "README.txt").write_text(txt)
    lines = []
    for f in sorted(out.iterdir()):
        if f.name in ("SHA256SUMS", "READY"): continue
        h = hashlib.sha256()
        with open(f, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""): h.update(b)
        lines.append(f"{h.hexdigest()}  {f.name}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    print("published (READY not yet written)", out, flush=True)


if __name__ == "__main__":
    {"pass0": pass0, "prep": prep, "render": render, "publish": publish}[sys.argv[1]](*sys.argv[2:])
