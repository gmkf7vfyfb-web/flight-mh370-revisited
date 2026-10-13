"""Settling's standard result on a stratified end-of-flight run: the seabed wreckage PDF for the core 00:19 option set.

Ocean settling, 10 Oct 2026. Follows the rulings of ~16:30 UTC (core option set and names), ~19:10 UTC (language;
two footnotes; facts after 00:19: airborne at 00:19:37 and not powered at 01:15:56 = end of flight's `unpowered`;
strata re-weighted by end of flight's 00:19 evidence per family, fixed-weight mixture beside it).

    python3 wf_standard.py prep   <eof smoke dir> <eof run root> <family-evidence json> <tag>
    (settle field/<tag>A_impacts.f64 and field/<tag>B_impacts.f64 with settling::tests::wreckage_field)
    python3 wf_standard.py render <eof smoke dir> <core run.json with reference_arcs> <tag> <label> <settling commit> <eof commit>

Run root holds <stratum>/seed-<k>/{impacts.npy, run.json}. Strata and P(family) come from the evidence file.
Sampling: per option, stratum and seed, a systematic resample of the option posterior (end of flight's
option_posteriors, imported) of ceil(N * max(P_fixed, P_reweighted) / n_seeds) impacts; each mixture is a stride sub-sample
of it at N * P / 4 (no new draws). One settling draw per resampled impact. N = 200,000 for Held Out, 40,000 otherwise.
"""
import sys, os, json, math, pathlib, numpy as np
from collections import Counter

OPTS = [("00:19 Held Out", "none__other", 200000),
        ("00:19 R600 BTO Only", "r600-bto__other", 40000),
        ("00:19 R600 BTO + Raw BFO", "r600_no-offset__other", 40000),
        ("00:19 Holland H1", "both_startup-offset__fuel-exhaustion", 40000),
        ("00:19 Holland H2", "both_no-offset__other", 40000)]
CON = "unpowered"
SEEDS = tuple(int(x) for x in os.environ.get("WF_SEEDS", "1,2,3,4").split(","))
VCOLS = ['unix_s', 'latitude_deg', 'longitude_deg', 'velocity_east_mps', 'velocity_north_mps', 'velocity_up_mps', 'flight_path_angle_deg',
         'mass_kg', 'kinetic_energy_j', 'vertical_kinetic_energy_j', 'parent', 'latent:debris_class']
GRID, R_AUTH = 0.02, 6371.0072


def foot_subs(text, info):
    """Run-specific footnote text: the end-of-flight evidence key actually used (info["evidence_suffix"], "+alive" for files written
    before it was recorded), the seed count, and WF_FOOT_SUBS, a JSON list of [old, new] pairs (e.g. the run C labels)."""
    suf = info.get("evidence_suffix", "+alive")
    text = text.replace("Z_00:19 (+alive)", f"Z_00:19 ({suf})").replace("(+alive)", f"({suf})")
    text = text.replace("4 strata x 4 seeds", f"{len(info['strata'])} strata x {len(SEEDS)} seeds")
    for old, new in json.loads(os.environ.get("WF_FOOT_SUBS", "[]")):
        assert old in text, f"WF_FOOT_SUBS: {old!r} not in footnote"; text = text.replace(old, new)
    return text


def grid_axes(ext):
    le = np.arange(ext[2], ext[3] + GRID / 2, GRID); oe = np.arange(ext[0], ext[1] + GRID / 2, GRID)
    return le, oe


def area90(H, le, oe, smooth_deg=0.1):
    from scipy.ndimage import gaussian_filter
    from displacement_greyscale import hpd_levels
    d = gaussian_filter(H, smooth_deg / GRID, mode="constant"); d = d / d.sum(); l = hpd_levels(d, (0.90,))[0]
    cell = (R_AUTH ** 2) * np.radians(GRID) * np.abs(np.sin(np.radians(le[1:])) - np.sin(np.radians(le[:-1])))[:, None]
    return float((cell * (d >= l)).sum())


def columns(d):
    """(meta, g) for a seed dir in either end-of-flight format: compact impacts32.npy (run C, via end of flight's own
    compact_impacts.load, unix times restored, kinetic energy from mass and velocity) or full impacts.npy."""
    if (d / "impacts32.npy").exists():
        from compact_impacts import load
        return load(d)
    meta = json.loads((d / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(d / "impacts.npy", mmap_mode="r")
    return meta, (lambda name: np.asarray(X[:, cols[name]], float))


def prep(SM, root, evid, tag):
    sys.path.insert(0, SM); from displacement_hist import option_posteriors
    ev = json.loads(pathlib.Path(evid).read_text()); strata = list(ev["p_core"])
    P = {}
    for name, key, _ in OPTS:
        fixed = ev["p_core"]; ck = f"{name} +{CON}" if f"{name} +{CON}" in ev["mixtures"] else f"{name} +alive"; m = ev["mixtures"].get(ck, {})
        rew = m.get("p_family_reweighted") if name not in ("00:19 Holland H1", "00:19 Holland H2") else None
        P[key] = {"fixed": fixed, "reweighted": rew or fixed, "reweighted_source": ck if rew else "not re-weighted (fixed)"}
    rng = np.random.default_rng(20261010)
    # pass 1: extent of every impact (map grid covers all mass)
    lat_min, lat_max, lon_min, lon_max = 90, -90, 360, -360
    for st in strata:
        for s in SEEDS:
            d = root / st / f"seed-{s}"; _, gg = columns(d); la = gg("latitude_deg"); lo = gg("longitude_deg")
            f = np.isfinite(la) & np.isfinite(lo)
            lat_min, lat_max = min(lat_min, la[f].min()), max(lat_max, la[f].max()); lon_min, lon_max = min(lon_min, lo[f].min()), max(lon_max, lo[f].max())
    ext = [math.floor(lon_min) - 1.0, math.ceil(lon_max) + 1.0, math.floor(lat_min) - 1.0, math.ceil(lat_max) + 1.0]
    le, oe = grid_axes(ext)
    H = {key: {st: {} for st in strata} for _, key, _ in OPTS}; ESS = {key: {st: {} for st in strata} for _, key, _ in OPTS}
    sets = {"A": [OPTS[0]], "B": OPTS[1:]}
    tabs = {"A": [], "B": []}; src = {"A": [], "B": []}; occ = {key: {"rows": [], "draws": [], "stratum": [], "seed": [], "fixed": [], "reweighted": []} for _, key, _ in OPTS}
    for si, st in enumerate(strata):
        for s in SEEDS:
            d = root / st / f"seed-{s}"; _, gg = columns(d)
            picks = {}
            for k, p, c in option_posteriors(d, d, constraints=(CON,)):
                base = k[: -len("+" + CON)] if k.endswith("+" + CON) else None
                if base not in H: continue
                p = p / p.sum(); ESS[base][st][s] = float(1 / np.sum(p ** 2))
                H[base][st][s] = np.histogram2d(c["lat"], c["lon"], bins=[le, oe], weights=p)[0].astype(np.float32)
                N = dict((kk, nn) for _, kk, nn in OPTS)[base]
                pm = max(P[base]["fixed"][st], P[base]["reweighted"][st]); n = math.ceil(N * pm / len(SEEDS))
                u = (rng.random() + np.arange(n)) / n; picks[base] = np.minimum(np.searchsorted(np.cumsum(p), u), len(p) - 1)
                for mix in ("fixed", "reweighted"):
                    km = int(round(N * P[base][mix][st] / len(SEEDS))); idx = np.floor((np.arange(km) + 0.5) * n / km).astype(int) if km else np.zeros(0, int)
                    mask = np.zeros(n, bool); mask[idx] = True; occ[base][mix].append(mask)
            assert set(picks) == set(H), f"{st} seed {s}: missing {set(H) - set(picks)}"
            V = None
            for setname, opts in sets.items():
                need, seen_by = {}, {}
                for _, key, _ in opts:
                    seen = Counter(); lst = []
                    for i in picks[key].tolist(): lst.append((i, seen[i])); seen[i] += 1
                    seen_by[key] = lst
                    for i, m in seen.items(): need[i] = max(need.get(i, 0), m)
                if V is None: V = np.column_stack([gg(c) for c in VCOLS])
                ii = np.array(sorted(need)); A = V[ii]
                base_row = len(tabs[setname]); where = {i: base_row + j for j, i in enumerate(ii.tolist())}
                for r, i in zip(A, ii): tabs[setname].append(np.r_[r, need[i], si * 10 + s]); src[setname].append((si, s, i))
                for _, key, _ in opts:
                    occ[key]["rows"] += [where[i] for i, _ in seen_by[key]]; occ[key]["draws"] += [dd for _, dd in seen_by[key]]
                    occ[key]["stratum"] += [si] * len(seen_by[key]); occ[key]["seed"] += [s] * len(seen_by[key])
            print(st, s, flush=True)
    pathlib.Path("field").mkdir(exist_ok=True)
    for setname in sets:
        np.array(tabs[setname]).astype("<f8").tofile(f"field/{tag}{setname}_impacts.f64")
        # source of each table row: stratum index (info["strata"]), seed, and the row index in that seed's impacts file (composer gap 16)
        np.save(f"field/{tag}{setname}_source.npy", np.array(src[setname], dtype=np.int64))
    arrays, info = {}, {"strata": strata, "extent_lon_lon_lat_lat": ext, "constraint": CON, "options": {},
                    "evidence_suffix": "+" + CON if any(f"{n} +{CON}" in ev["mixtures"] for n, _, _ in OPTS) else "+alive"}
    for j, (name, key, N) in enumerate(OPTS):
        for f in ("rows", "draws", "stratum", "seed"): arrays[f"{f}_{j}"] = np.array(occ[key][f])
        for mix in ("fixed", "reweighted"):
            arrays[f"{mix}_{j}"] = np.concatenate(occ[key][mix])
            Pm = P[key][mix]
            Hm = sum(Pm[st] * H[key][st][s].astype(np.float64) / len(SEEDS) for st in strata for s in SEEDS)
            np.save(f"field/{tag}_H_{j}_{mix}.npy", Hm.astype(np.float32))
            ess = 1.0 / sum((Pm[st] / len(SEEDS)) ** 2 / ESS[key][st][s] for st in strata for s in SEEDS)
            hl = len(SEEDS) // 2; halves = (SEEDS[:hl], SEEDS[hl:])
            half = [sum(Pm[st] * H[key][st][s].astype(np.float64) / len(hs) for st in strata for s in hs) for hs in halves]
            info["options"].setdefault(name, {"key": key + "+" + CON, "N": N})[mix] = {
                "p_family": Pm, "source": P[key]["reweighted_source"] if mix == "reweighted" else "core P(family), held fixed",
                "ess_mixture_kish": ess, "impact_area90_km2_full_weights": area90(Hm, le, oe),
                "impact_area90_km2_seed_halves": [area90(h, le, oe) for h in half], "seed_halves": [list(h) for h in halves]}
        info["options"][name]["ess_per_stratum_seed"] = ESS[key]
        info["options"][name]["impact_area90_km2_per_stratum"] = {st: area90(sum(H[key][st][s].astype(np.float64) / len(SEEDS) for s in SEEDS), le, oe) for st in strata}
    np.savez(f"field/{tag}_draws.npz", **arrays)
    pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))
    print("tables", {k: len(v) for k, v in tabs.items()}, "draws", {k: int(np.array(v)[:, 12].sum()) for k, v in tabs.items()})


def render(SM, arcs_json, tag, label, settling_commit, eof_commit):
    sys.path.insert(0, SM)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij")
    T = {s_: np.fromfile(f"field/{tag}{s_}_impacts.f64", "<f8").reshape(-1, 14) for s_ in "AB"}
    EL = {s_: np.fromfile(f"field/{tag}{s_}_elements.f64", "<f8").reshape(-1, 8) for s_ in "AB"}
    names = [n for n, _, _ in OPTS]; letters = "abcdefg"
    for mix in ("reweighted", "fixed"):
        g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": arcs_json,
             "OUTSTEM": f"settling-seabed-wreckage-{label}-{mix}", "STAMP": "Not yet estimable -\ntargeted sampler in progress",
             "TITLES_W": {n: f"({letters[j]}) {n}" for j, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {}}
        for j, n in enumerate(names):
            s_ = "A" if j == 0 else "B"; m = z[f"{mix}_{j}"]
            g["SRC"][n] = (T[s_], z[f"rows_{j}"][m], z[f"draws_{j}"][m], EL[s_])
            Hm = np.load(f"field/{tag}_H_{j}_{mix}.npy").astype(np.float64); nz = Hm > 0
            g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
            g["ESS"][n] = info["options"][n][mix]["ess_mixture_kish"]
        pf = info["options"]["00:19 R600 BTO + Raw BFO"][mix]["p_family"]
        wtxt = ("weighted by the core run's probability of each flight family, then by the 00:19 evidence for each family"
                if mix == "reweighted" else "weighted by the core run's probability of each flight family only (fixed weights)")
        g["TITLE"] = "Where the wreckage is on the seabed, for each use of the 00:19 satellite data"
        g["SUBTITLE"] = ("Flight families weighted by the flight model, then by the 00:19 data" if mix == "reweighted"
                         else "Flight families at the fixed weights of the flight model")
        g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. "
                         "The movement of the wreckage through the water adds less than 1 % to each grey area. The flight model is not yet stable, "
                         "so these areas can change. There are not yet sufficient samples to show a result for Holland H1 and H2.")
        g["FOOT_TECH"] = (f"Settled-mass seabed density (real ocean: GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10 density; GLORYS12V1 surface current; ERA5 wind; "
                          f"AusSeabed then GEBCO_2026), settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight next-run on core (b) "
                          f"(4 strata x 4 seeds, prior track 289.7 deg, EoF {eof_commit}), option_posteriors with +{CON} (airborne at 00:19:37, not powered at 01:15:56). "
                          f"Strata {wtxt.replace('the core run', 'core').replace('the 00:19 evidence', 'end of flight Z_00:19 (+alive)')}; "
                          f"P(family) for R600 BTO + Raw BFO = " + " / ".join(f"{pf[st]:.3f}" for st in info["strata"]) + " (free / repro-radar / descent-climb / routes). "
                          f"Log-on cause: other (H1: fuel exhaustion). Systematic resample, one settling draw each: 200,000 (a), 40,000 (b-e). 0.02 deg grid, Gaussian 0.1 deg, HPD. "
                          f"Mixture ESS by Kish; below {g['ESS_MIN']:,} not estimable (H1/H2: descent-model and sampler changes await Pete; architecture burst study). Labels: core (b) split-half NOT converged; two-tank bookkeeping only; internal-v1 one-engine flow 2x; "
                          f"dive class (b) and Boeing glide PROVISIONAL-OVERNIGHT; Mac, 2 threads.")
        g["FOOT_TECH"] = foot_subs(g["FOOT_TECH"], info)
        exec(open(pathlib.Path(__file__).with_name("wreckage_map_standard.py")).read(), g)
        print(mix, {n: (round(g["stats"][n]["area_km2_99_90_50"]["impact_resampled"][1] / 1e3, 1), round(g["stats"][n]["area_km2_99_90_50"]["wreckage_field"][1] / 1e3, 1),
                        g["stats"][n]["not_computed_impacts"], g["stats"][n]["resampled_impacts"]) for n in names})


if __name__ == "__main__":
    if sys.argv[1] == "prep":
        sys.path.insert(0, sys.argv[2]); prep(sys.argv[2], pathlib.Path(sys.argv[3]), sys.argv[4], sys.argv[5])
    elif sys.argv[1] == "render":
        sys.path.insert(0, sys.argv[2]); render(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
