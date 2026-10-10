"""Stand-in composition (architecture stand-in for ocean settling, 10 Oct 2026). NOT module code.

Combines settling's four per-stratum wreckage-field runs (work/<stratum>/field/{A,B}_*) into core's P(family)
mixture and draws it with settling's own, unchanged renderer (results/settling-wreckage-field-289-priorities/
wreckage_map_priorities.py), which is exec'd exactly as wreckage_map_priorities_run.py execs it.

Mixture rule (held fixed; core (b)'s P(family) is NOT converged):
- impact PDF (dashed contours): every impact at full option-posterior weight; seed weight 1/4 within a stratum,
  stratum weight P(family). Passed to the renderer as 16 per-seed entries scaled by 4 * P_f (the renderer
  averages its entries).
- seabed field: each stratum's systematic resample (one settling draw per resampled impact, unchanged) is
  systematically sub-sampled (stride, offset 1/2) so that stratum counts are proportional to P(family); the
  largest-weight stratum (free) keeps all of its resampled impacts. No new settling draws.
- ESS of the mixed weights: 1 / sum_f P_f^2 sum_s (1/16) / ESS_fs.

    python3 combine_mixture.py <eof smoke dir> <runs root> <arcs run.json> <settling results dir> [alive]
"""
import sys, os, json, pathlib, numpy as np, matplotlib
matplotlib.use("Agg")
SM, E, ARCS_JSON, RDIR = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], pathlib.Path(sys.argv[4])
CON = sys.argv[5] if len(sys.argv) > 5 else ""
sys.path.insert(0, SM); sys.path.insert(0, str(RDIR))
from displacement_hist import option_posteriors, T_M0019B
PF = {"free": 0.6948, "repro-radar": 0.1527, "descent-climb": 0.1376, "routes": 0.0149}
STRATA = list(PF); SEEDS = [1, 2, 3, 4]
KEYS = ["none__other", "r600_no-offset__fuel-exhaustion", "both_startup-offset__fuel-exhaustion", "both_no-offset__other"]
SUFFIX = f"+{CON}" if CON else ""
full = {k: [] for k in KEYS}; inv = {k: 0.0 for k in KEYS}; ess_fs = {k: {} for k in KEYS}
for f in STRATA:
    for s in SEEDS:
        run = E / f"next-{f}" / f"seed-{s}"
        for k, p, c in option_posteriors(run, run, constraints=(CON,) if CON else ()):
            if k.endswith(SUFFIX) and k[:len(k) - len(SUFFIX)] in KEYS and (CON or "+" not in k):
                k = k[:len(k) - len(SUFFIX)]
                p = p / p.sum(); nz = np.nonzero(p)[0]
                full[k].append((c["lat"][nz], c["lon"][nz], p[nz] * 4 * PF[f]))
                e = float(1 / np.sum(p ** 2)); ess_fs[k][f"{f}/seed-{s}"] = e; inv[k] += PF[f] ** 2 * (1 / 16) / e
ESS = {k: 1.0 / inv[k] for k in KEYS}
assert all(len(full[k]) == 16 for k in KEYS), {k: len(full[k]) for k in KEYS}

SRC, MIXN = {}, {}
for tag in ("A", "B"):
    per = {}
    for f in STRATA:
        d = pathlib.Path("work") / f / "field"
        T = np.fromfile(d / f"{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(d / f"{tag}_elements.f64", "<f8").reshape(-1, 8)
        per[f] = (T, EL, np.load(d / f"{tag}_draws.npz"))
    keys = per[STRATA[0]][2]["keys"].tolist()
    # one concatenated table per tag; element rows re-indexed by the table offset
    off, Ts, ELs = {}, [], []; base = 0
    for f in STRATA:
        T, EL, _ = per[f]; off[f] = base
        EL = EL.copy(); EL[:, 0] += base; Ts.append(T); ELs.append(EL); base += len(T)
    TT, EE = np.concatenate(Ts), np.concatenate(ELs)
    for j, k in enumerate(keys):
        RD = {}
        for f in STRATA:
            r, d_ = per[f][2][f"rows_{j}"], per[f][2][f"draws_{j}"]
            if CON == "alive":  # settling's rule: keep resampled impacts after 00:19:37.443 (rejection, no new draws)
                keep = per[f][0][r, 0] > T_M0019B; r, d_ = r[keep], d_[keep]
            elif CON:
                raise SystemExit(f"constraint {CON} needs its own resample")
            RD[f] = (r, d_)
        N = min(len(RD[f][0]) / PF[f] for f in STRATA)  # largest mixture with counts proportional to P(family)
        rows, dr, MIXN[k] = [], [], {}
        for f in STRATA:
            r, d_ = RD[f]
            m = min(len(r), int(round(PF[f] * N)))
            ix = np.minimum(((0.5 + np.arange(m)) * len(r) / m).astype(np.int64), len(r) - 1) if m else np.array([], np.int64)
            rows.append(r[ix] + off[f]); dr.append(d_[ix]); MIXN[k][f] = int(m)
        SRC[k] = (TT, np.concatenate(rows), np.concatenate(dr), EE)

ESS_MIN = 1000; SMOOTH = 0.1
OUTSTEM = os.environ.get("WF_OUTSTEM", "settling-wreckage-field-next-run-b-mixture") + ("-alive" if CON else "")
TITLES_W = {"none__other": "(a) Held out: no 00:19 BFO; no log-on cause",
            "r600_no-offset__fuel-exhaustion": "(b) R600 as observed, no offset (as Ashton); fuel-exh.",
            "both_startup-offset__fuel-exhaustion": "(c) Holland H1: both bursts, start-up offset; fuel-exh.",
            "both_no-offset__other": "(d) Holland H2: both bursts, no offset; other"}
TITLE = ("Seabed wreckage PDF under the four 00:19 priority hypotheses (next-run-b, core (b) P(family) mixture"
         + (f", {SUFFIX} (PROVISIONAL-OVERNIGHT)" if CON else "") + ")")
cnt = "; ".join(f"{k.split('__')[0]}: " + "/".join(f"{MIXN[k][f]:,}" for f in STRATA) for k in KEYS)
SUB = ("Grey: seabed wreckage PDF, weighted by settled mass (afloat pieces excluded). Dashed orange: impact PDF, every impact at full weight. Before any seabed-search evidence.\n"
       "Impacts: end of flight next-run (EoF 3c6319f on core (b) m0011 hand-offs; prior track 289.7°; descent idle floor ON; run by an architecture stand-in), strata free/Davey dynamics+radar/descent-climb/routes\n"
       "mixed at core (b) P(family) 0.6948/0.1527/0.1376/0.0149, held fixed and NOT converged (core split-half 0.71-0.88 < 0.896); seeds equal weight within a stratum. Weights = option_posteriors (EoF 3c6319f).\n"
       f"Seabed field: settling's per-stratum resamples (unchanged recipe), systematically sub-sampled to P(family) proportions, no new draws. Mixture counts free/Davey/descent-climb/routes - {cnt}.\n"
       "Settling (hypothesis/settling 9823b4e): real ocean, GLORYS12V1 column (TEOS-10) and surface current, ERA5 wind, AusSeabed then GEBCO_2026; breakup table PROVISIONAL; implosion, occupants off.\n"
       "0.02° grid, Gaussian 0.1° (6 NM), HPD on the smoothed density. Arcs drawn from core reference-289 (core (b)'s own arcs lie ~2 km away). Impacts north of 18° S: not computed, excluded (JSON).\n"
       f"NOT ESTIMABLE: mixed-weight impact ESS below {ESS_MIN:,}. Platform: Mac, 2 threads. Stand-in composition script (not module code) around settling's unchanged renderer.\n"
       "Run labels: core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; settling run by an architecture stand-in, module to review"
       + (f"; {SUFFIX}: airborne at 00:19:37.443 (end of flight, PROVISIONAL-OVERNIGHT), by rejection from the plain resample" if CON else "") + ".")
exec(open(RDIR / "wreckage_map_priorities.py").read())
J = json.loads(pathlib.Path(OUTSTEM + ".json").read_text())
J["mixture"] = {"p_family": PF, "ess_rule": "1/sum_f P_f^2 sum_s (1/16)/ESS_fs", "ess_per_stratum_seed": ess_fs,
                "seabed_resample_counts_per_stratum": MIXN, "constraint": CON or None}
pathlib.Path(OUTSTEM + ".json").write_text(json.dumps(J, indent=1))
print(OUTSTEM, {k: round(ESS[k]) for k in KEYS}, MIXN)
