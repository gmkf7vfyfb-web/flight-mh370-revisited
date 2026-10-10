"""Settling's standard result split by Pete's hypothesis families (ruling 15:20 -0600, 10 Oct 2026: "results per family first").

Families are end of flight's labels (`compact_impacts.family_labels` on latent:onset_mechanism and latent:control_realised), grouped as
    A1 = codes {1, 4}  (onset at exhaustion, uncontrolled; code 4 "controlled then lost" with A1, end of flight's PROVISIONAL default)
    A2 = code  {2}     (onset at exhaustion, controlled or arrested to the surface)
    B  = codes {3, 5}  (deliberate onset before exhaustion; 5 = control lost en route)
Code 6 (deliberate onset then no intervention) is outside B as ruled; its share is reported, it is in no family panel.
Override with WF_FAMILIES="A1:1,4;A2:2;B:3,5".

Within an option, family F's posterior is p restricted to F and renormalised. Strata are mixed by
P(stratum | data, option, F) ∝ P(stratum | data, option) × share_F(stratum), share_F = seed mean of the posterior mass on F,
with P(stratum | data, option) end of flight's re-weighted P(family) (fixed for Held Out, H1 and H2).

    python3 wf_family.py prep   <eof smoke dir> <run root> <family-evidence json> <tag>
    (settle field/<tag>F<j>_impacts.f64 for each family j with settling::tests::wreckage_field)
    python3 wf_family.py render <eof smoke dir> <core run.json with reference_arcs> <tag> <label> <settling commit> <eof commit>
"""
import sys, os, json, math, pathlib, numpy as np
from collections import Counter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from wf_standard import OPTS, CON, SEEDS, VCOLS, GRID, grid_axes, area90, columns

N_FAM = {"00:19 Held Out": 60000}
N_DEFAULT = 20000
FAMS = [(f.split(":")[0], {float(x) for x in f.split(":")[1].split(",")}) for f in os.environ.get("WF_FAMILIES", "A1:1,4;A2:2;B:3,5").split(";")]
FAM_TEXT = {"A1": "A1: fuel exhaustion, then no control", "A2": "A2: fuel exhaustion, then controlled to the surface",
            "B": "B: deliberate descent before fuel exhaustion"}


def prep(SM, root, evid, tag):
    sys.path.insert(0, SM); from displacement_hist import option_posteriors; from compact_impacts import family_labels
    ev = json.loads(pathlib.Path(evid).read_text()); strata = list(ev["p_core"])
    P0 = {}
    for name, key, _ in OPTS:
        m = ev["mixtures"].get(f"{name} +alive", {})
        rew = m.get("p_family_reweighted") if name not in ("00:19 Holland H1", "00:19 Holland H2") else None
        P0[key] = rew or ev["p_core"]
    rng = np.random.default_rng(20261011)
    # pass 1: grid extent, family shares per stratum and seed, and the per-family posteriors' histograms
    lat_min, lat_max, lon_min, lon_max = 90, -90, 360, -360
    share = {(key, F): {st: {} for st in strata} for _, key, _ in OPTS for F, _ in FAMS}
    other_share = {key: {st: {} for st in strata} for _, key, _ in OPTS}
    for st in strata:
        for s in SEEDS:
            d = root / st / f"seed-{s}"; _, gg = columns(d); la, lo = gg("latitude_deg"), gg("longitude_deg"); f = np.isfinite(la) & np.isfinite(lo)
            lat_min, lat_max = min(lat_min, la[f].min()), max(lat_max, la[f].max()); lon_min, lon_max = min(lon_min, lo[f].min()), max(lon_max, lo[f].max())
    ext = [math.floor(lon_min) - 1.0, math.ceil(lon_max) + 1.0, math.floor(lat_min) - 1.0, math.ceil(lat_max) + 1.0]; le, oe = grid_axes(ext)
    def posteriors(st, s):
        d = root / st / f"seed-{s}"; _, gg = columns(d)
        fam = family_labels(gg("latent:onset_mechanism"), gg("latent:control_realised"))["family_code"]
        masks = {F: np.isin(fam, list(codes)) for F, codes in FAMS}
        for k, p, c in option_posteriors(d, d, constraints=(CON,)):
            base = k[: -len("+" + CON)] if k.endswith("+" + CON) else None
            if base in P0: yield base, p / p.sum(), c, masks, gg
    # pass 1: posterior share of each family per option, stratum and seed (cheap)
    for st in strata:
        for s in SEEDS:
            for base, p, c, masks, _ in posteriors(st, s):
                other_share[base][st][s] = float(p[~np.any(list(masks.values()), axis=0)].sum())
                for F, _ in FAMS: share[(base, F)][st][s] = float(p[masks[F]].sum())
            print("pass1", st, s, flush=True)
    PF = {}
    for name, key, _ in OPTS:
        for F, _ in FAMS:
            w_ = {st: P0[key][st] * np.mean([share[(key, F)][st][s] for s in SEEDS]) for st in strata}; t = sum(w_.values())
            PF[(key, F)] = {st: (w_[st] / t if t > 0 else 0.0) for st in strata}
    # pass 2: per (option, family, stratum, seed) a systematic resample of N * P / n_seeds; mixture histograms and Kish ESS on the fly
    pathlib.Path("field").mkdir(exist_ok=True)
    info = {"strata": strata, "extent_lon_lon_lat_lat": ext, "constraint": CON, "families": {F: sorted(c) for F, c in FAMS}, "entries": {}}
    Hm = {(key, F): np.zeros((len(le) - 1, len(oe) - 1)) for _, key, _ in OPTS for F, _ in FAMS}; inv_ess = {(key, F): 0.0 for _, key, _ in OPTS for F, _ in FAMS}
    tabs = {F: [] for F, _ in FAMS}; occ = {(key, F): {"rows": [], "draws": []} for _, key, _ in OPTS for F, _ in FAMS}
    for st in strata:
        for s in SEEDS:
            seen_by = {}; V = None
            for base, p, c, masks, gg in posteriors(st, s):
                name = [n for n, k_, _ in OPTS if k_ == base][0]
                for F, _ in FAMS:
                    sh = share[(base, F)][st][s]; Pm = PF[(base, F)][st]
                    if sh <= 0 or Pm <= 0: continue
                    pf = np.where(masks[F], p, 0.0) / sh
                    Hm[(base, F)] += Pm / len(SEEDS) * np.histogram2d(c["lat"], c["lon"], bins=[le, oe], weights=pf)[0]
                    inv_ess[(base, F)] += (Pm / len(SEEDS)) ** 2 * np.sum(pf ** 2)
                    n = int(round(N_FAM.get(name, N_DEFAULT) * Pm / len(SEEDS)))
                    if n == 0: continue
                    u = (rng.random() + np.arange(n)) / n; ii = np.minimum(np.searchsorted(np.cumsum(pf), u), len(pf) - 1)
                    seen = Counter(); lst = []
                    for i in ii.tolist(): lst.append((i, seen[i])); seen[i] += 1
                    seen_by[(base, F)] = lst
                if V is None: V = np.column_stack([gg(cn) for cn in VCOLS])
            for F, _ in FAMS:
                need = {}
                for (b_, F_), lst in seen_by.items():
                    if F_ != F: continue
                    for i, d_ in lst: need[i] = max(need.get(i, 0), d_ + 1)
                if not need: continue
                ii = np.array(sorted(need)); base_row = len(tabs[F]); where = {i: base_row + q for q, i in enumerate(ii.tolist())}
                for r, i in zip(V[ii], ii): tabs[F].append(np.r_[r, need[i], strata.index(st) * 10 + s])
                for (b_, F_), lst in seen_by.items():
                    if F_ == F: occ[(b_, F)]["rows"] += [where[i] for i, _ in lst]; occ[(b_, F)]["draws"] += [d_ for _, d_ in lst]
            print("pass2", st, s, flush=True)
    arrays = {}
    for j, (F, _) in enumerate(FAMS):
        np.array(tabs[F]).astype("<f8").tofile(f"field/{tag}F{j}_impacts.f64")
        for q, (name, key, _) in enumerate(OPTS):
            arrays[f"rows_{j}_{q}"] = np.array(occ[(key, F)]["rows"], dtype=np.int64); arrays[f"draws_{j}_{q}"] = np.array(occ[(key, F)]["draws"], dtype=np.int64)
            np.save(f"field/{tag}_H_{j}_{q}.npy", Hm[(key, F)].astype(np.float32))
            post_share = sum(P0[key][st] * np.mean([share[(key, F)][st][s] for s in SEEDS]) for st in strata)
            info["entries"][f"{name} | {F}"] = {"option": name, "family": F, "key": key + "+" + CON, "p_stratum_given_family": PF[(key, F)],
                                                "ess_mixture_kish": (1.0 / inv_ess[(key, F)]) if inv_ess[(key, F)] > 0 else 0.0,
                                                "posterior_share_of_family": post_share,
                                                "impact_area90_km2": area90(Hm[(key, F)], le, oe) if Hm[(key, F)].sum() > 0 else None,
                                                "resampled": int(len(arrays[f"rows_{j}_{q}"]))}
        print("set", F, len(tabs[F]), int(np.array(tabs[F])[:, 12].sum()) if tabs[F] else 0, flush=True)
    for name, key, _ in OPTS:
        info.setdefault("outside_families_share", {})[name] = sum(P0[key][st] * np.mean([other_share[key][st][s] for s in SEEDS]) for st in strata)
    np.savez(f"field/{tag}_draws.npz", **arrays); pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))


def render(SM, arcs_json, tag, label, settling_commit, eof_commit):
    sys.path.insert(0, SM)
    import matplotlib; matplotlib.use("Agg")
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1]); LC, OC = np.meshgrid(lc, oc, indexing="ij")
    fams = list(info["families"]); names = [n for n, _, _ in OPTS]
    g = {"KEYS": [], "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": arcs_json, "NCOL": len(names),
         "OUTSTEM": f"settling-seabed-wreckage-{label}-by-family", "STAMP": "Not yet estimable",
         "TITLES_W": {}, "SRC": {}, "full": {}, "ESS": {}, "PANEL_NOTE": {}}
    for j, F in enumerate(fams):
        T = np.fromfile(f"field/{tag}F{j}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}F{j}_elements.f64", "<f8").reshape(-1, 8)
        for q, n in enumerate(names):
            e = info["entries"][f"{n} | {F}"]; k = f"{n} | {F}"; g["KEYS"].append(k)
            g["TITLES_W"][k] = f"({'abcdefghijklmnopqrstuvwxyz'[j * len(names) + q]}) {n} · {F}"
            g["SRC"][k] = (T, z[f"rows_{j}_{q}"], z[f"draws_{j}_{q}"], EL)
            Hm = np.load(f"field/{tag}_H_{j}_{q}.npy").astype(np.float64); nz = Hm > 0
            g["full"][k] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]; g["ESS"][k] = e["ess_mixture_kish"]
            g["PANEL_NOTE"][k] = f"family share {100 * e['posterior_share_of_family']:.0f} %"
    g["TITLE"] = "Where the wreckage is on the seabed, for each use of the 00:19 satellite data and each type of flight end"
    g["SUBTITLE"] = ("Rows: " + "; ".join(FAM_TEXT.get(F, F) for F in fams) + ". Each panel is conditional on its row; the family share is the "
                     "posterior probability of that row under the column's 00:19 data, not evidence for it.")
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. Each row "
                     "shows one type of flight end. The flight model is not yet stable, and the data hardly change how probable each type is, so do "
                     "not read the shares as evidence. There are not yet sufficient samples for Holland H1 and H2.")
    out = info.get("outside_families_share", {})
    g["FOOT_TECH"] = (f"Settled-mass seabed density, real ocean (GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10; GLORYS12V1 surface current; ERA5 wind; "
                      f"AusSeabed then GEBCO_2026), settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight on "
                      f"core ({label}), {len(info['strata'])} strata x {len(SEEDS)} seeds, prior track 289.7 deg, EoF {eof_commit}, option_posteriors +{CON}; "
                      f"family codes (end of flight family_labels) " + ", ".join(f"{F} = {info['families'][F]}" for F in fams) +
                      " (code 4 with A1 PROVISIONAL; code 6 outside B, share " + ", ".join(f"{v * 100:.1f} %" for v in out.values()) + " by column). "
                      "Strata: P(stratum | option) x share of the family. Systematic resample, one settling draw each: 60,000 (Held Out), 20,000 (others) per "
                      "family. 0.02 deg grid, Gaussian 0.1 deg, HPD. Below 1,000 Kish ESS not estimable. Labels: core split-half NOT converged; two-tank "
                      "bookkeeping only; dive class (b) PROVISIONAL; point mass cannot unload; Mac, 2 threads.")
    exec(open(pathlib.Path(__file__).with_name("wreckage_map_standard.py")).read(), g)
    res = {k: {"impact90": g["stats"][k]["area_km2_99_90_50"]["impact_resampled"][1], "seabed90": g["stats"][k]["area_km2_99_90_50"]["wreckage_field"][1],
               "ess": g["ESS"][k], "estimable": g["stats"][k]["estimable"], "share": info["entries"][k]["posterior_share_of_family"]} for k in g["KEYS"]}
    print(json.dumps({k: [round(v["impact90"] / 1e3, 1), round(v["seabed90"] / 1e3, 1), round(v["ess"]), round(v["share"], 3)] for k, v in res.items()}))


if __name__ == "__main__":
    if sys.argv[1] == "prep":
        prep(sys.argv[2], pathlib.Path(sys.argv[3]), sys.argv[4], sys.argv[5])
    elif sys.argv[1] == "render":
        render(*sys.argv[2:8])
