"""Aimed settling resample: draw the impacts that settling settles from a set of per-row weights supplied by a consumer
(the composer's G / H products), instead of from end of flight's option posterior (composer pass 1 request, ~23:20 UTC 10 Oct 2026).

Input (one directory per product, written by the composer):
    <wdir>/manifest.json   {"product": "r600-G", "label": "00:19 R600 BTO Only, G", "option": "r600-bto__other",
                             "constraint": "unpowered", "run_root": ".../end-of-flight/next-run", "strata": [...], "seeds": [1, 2, 3, 4]}
    <wdir>/<stratum>/seed-<k>.f32   little-endian f32, one value per row of <run_root>/<stratum>/seed-<k>/impacts.npy (same order):
                             the row's FINAL mixture mass (stratum weight x pooled within-stratum weight); any overall scale.
    <wdir>/SHA256SUMS, READY
Rows with weight 0 or NaN are never drawn; NaN weights are counted and reported, never silently dropped.

    python3 wf_aimed.py prep   <eof smoke dir> <tag> <N> <wdir> [<wdir> ...]   -> field/<tag>P<j>_{impacts.f64,source.npy}, <tag>_draws.npz, <tag>_info.json
    (settle field/<tag>P<j>_impacts.f64 with settling::tests::wreckage_field)
    python3 wf_aimed.py render <eof smoke dir> <core run.json with reference_arcs> <tag> <label> <settling commit> <eof commit>

The resample is systematic over all rows of all strata and seeds, so each drawn outcome has equal weight 1/N. The impact
reference contours use every weighted row (not the resample). Kish ESS of the row weights is recorded; the seabed density
is estimable at N draws only if that row ESS is >= 1,000 (settling's floor).
"""
import sys, os, json, math, pathlib, numpy as np
from collections import Counter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from wf_standard import VCOLS, GRID, grid_axes, area90, columns, foot_subs, SEEDS


def _load_w(wdir, st, k, nrows):
    w = np.fromfile(wdir / st / f"seed-{k}.f32", dtype="<f4").astype(np.float64)
    assert w.size == nrows, f"{wdir}/{st}/seed-{k}.f32 has {w.size} rows, impacts.npy has {nrows}"
    return w


def prep(SM, tag, N, *wdirs):
    sys.path.insert(0, SM)
    N = int(N); rng = np.random.default_rng(20261012); wdirs = [pathlib.Path(w) for w in wdirs]
    mans = [json.loads((w / "manifest.json").read_text()) for w in wdirs]
    for w, m in zip(wdirs, mans): assert (w / "READY").exists(), f"{w}: no READY"
    info = {"products": [], "extent_lon_lon_lat_lat": None}
    # pass 1: extent over every impact of every run used, and per-file weight totals
    lat_min, lat_max, lon_min, lon_max = 90, -90, 360, -360
    tot = []
    for w, m in zip(wdirs, mans):
        root = pathlib.Path(m["run_root"]); t = {}
        for st in m["strata"]:
            for k in m["seeds"]:
                d = root / st / f"seed-{k}"; _, gg = columns(d); la, lo = gg("latitude_deg"), gg("longitude_deg"); f = np.isfinite(la) & np.isfinite(lo)
                lat_min, lat_max = min(lat_min, la[f].min()), max(lat_max, la[f].max()); lon_min, lon_max = min(lon_min, lo[f].min()), max(lon_max, lo[f].max())
                ww = _load_w(w, st, k, la.size); bad = ~np.isfinite(ww)
                t[(st, k)] = (float(np.where(bad, 0, ww).sum()), int(bad.sum()), float(np.where(bad, 0, ww ** 2).sum()))
        tot.append(t)
    ext = [math.floor(lon_min) - 1.0, math.ceil(lon_max) + 1.0, math.floor(lat_min) - 1.0, math.ceil(lat_max) + 1.0]; le, oe = grid_axes(ext)
    info["extent_lon_lon_lat_lat"] = ext
    arrays = {}
    for j, (w, m, t) in enumerate(zip(wdirs, mans, tot)):
        root = pathlib.Path(m["run_root"]); W = sum(v[0] for v in t.values()); assert W > 0, f"{w}: zero total weight"
        ess = W ** 2 / sum(v[2] for v in t.values())
        keys = [(st, k) for st in m["strata"] for k in m["seeds"]]
        cum = np.cumsum([t[key][0] / W for key in keys]); lo_edge = np.r_[0.0, cum[:-1]]
        u = (rng.random() + np.arange(N)) / N
        H = np.zeros((len(le) - 1, len(oe) - 1)); tab, src, rows, draws, strat, seed = [], [], [], [], [], []
        for (st, k), a, b in zip(keys, lo_edge, cum):
            uu = u[(u >= a) & (u < b)]; d = root / st / f"seed-{k}"; _, gg = columns(d)
            la, lo = gg("latitude_deg"), gg("longitude_deg"); ww = _load_w(w, st, k, la.size); ww = np.where(np.isfinite(ww), ww, 0.0)
            f = np.isfinite(la) & np.isfinite(lo)
            H += np.histogram2d(la[f], lo[f], bins=[le, oe], weights=ww[f] / W)[0]
            if uu.size == 0: continue
            pick = np.minimum(np.searchsorted(np.cumsum(ww / W), uu - a), la.size - 1)
            assert np.all(ww[pick] > 0), "drew a zero-weight row"
            cnt = Counter(pick.tolist()); ii = np.array(sorted(cnt)); V = np.column_stack([gg(c)[ii] for c in VCOLS])
            si = m["strata"].index(st); base = len(tab); where = {i: base + q for q, i in enumerate(ii.tolist())}
            for r, i in zip(V, ii): tab.append(np.r_[r, cnt[i], si * 10 + k]); src.append((si, k, i))
            seen = Counter()
            for i in pick.tolist(): rows.append(where[i]); draws.append(seen[i]); seen[i] += 1; strat.append(si); seed.append(k)
        np.array(tab).astype("<f8").tofile(f"field/{tag}P{j}_impacts.f64")
        np.save(f"field/{tag}P{j}_source.npy", np.array(src, dtype=np.int64))   # stratum index, seed, impacts.npy row
        for name, v in (("rows", rows), ("draws", draws), ("stratum", strat), ("seed", seed)): arrays[f"{name}_{j}"] = np.array(v, dtype=np.int64)
        np.save(f"field/{tag}_H_{j}.npy", H.astype(np.float32))
        info["products"].append({"wdir": str(w), "manifest": m, "N": N, "row_ess_kish": ess, "distinct_impacts": len(tab),
                                 "nan_weight_rows": int(sum(v[1] for v in t.values())), "impact_area90_km2_all_rows": area90(H, le, oe),
                                 "stratum_mass": {st: sum(t[(st, k)][0] for k in m["seeds"]) / W for st in m["strata"]}})
        print(m["product"], "rows ESS", round(ess), "distinct", len(tab), flush=True)
    np.savez(f"field/{tag}_draws.npz", **arrays); pathlib.Path(f"field/{tag}_info.json").write_text(json.dumps(info, indent=1))


def render(SM, arcs_json, tag, label, settling_commit, eof_commit):
    sys.path.insert(0, SM)
    import matplotlib; matplotlib.use("Agg")
    info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); z = np.load(f"field/{tag}_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]; le, oe = grid_axes(ext); lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    LC, OC = np.meshgrid(lc, oc, indexing="ij"); letters = "abcdefghij"
    names = [p["manifest"]["label"] for p in info["products"]]
    g = {"KEYS": names, "SMOOTH": 0.1, "ESS_MIN": 1000, "GRID_EXTENT": ext, "ARCS_JSON": arcs_json, "NCOL": 2 if len(names) <= 4 else 3,
         "OUTSTEM": f"settling-seabed-wreckage-{label}-aimed", "STAMP": "Not yet estimable -\ntargeted sampler in progress",
         "TITLES_W": {n: f"({letters[j]}) {n}" for j, n in enumerate(names)}, "SRC": {}, "full": {}, "ESS": {}, "PANEL_NOTE": {}}
    for j, (n, p) in enumerate(zip(names, info["products"])):
        T = np.fromfile(f"field/{tag}P{j}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}P{j}_elements.f64", "<f8").reshape(-1, 8)
        g["SRC"][n] = (T, z[f"rows_{j}"], z[f"draws_{j}"], EL)
        Hm = np.load(f"field/{tag}_H_{j}.npy").astype(np.float64); nz = Hm > 0; g["full"][n] = [(LC[nz], OC[nz], Hm[nz] / Hm.sum())]
        g["ESS"][n] = p["row_ess_kish"]
        g["PANEL_NOTE"][n] = f"drawn from the {p['manifest'].get('product', '')} weights"
    m0 = info["products"][0]["manifest"]
    g["TITLE"] = "Where the wreckage is on the seabed, for each combination of evidence"
    g["SUBTITLE"] = "The impacts that go to the seabed calculation are drawn from the weights of each combination of evidence"
    g["FOOT_STE"] = ("Grey areas show where the wreckage is on the seabed. Dashed orange lines show where the aircraft hit the water. Each panel "
                     "uses the weights of one combination of evidence. The flight model and the other evidence are not yet stable, so these areas can change.")
    g["FOOT_TECH"] = (f"Settled-mass seabed density (real ocean: GLORYS12V1 column 75-115 E, 45-10 S, TEOS-10 density; GLORYS12V1 surface current; ERA5 wind; "
                      f"AusSeabed then GEBCO_2026), settling {settling_commit}, breakup table PROVISIONAL, afloat pieces excluded. Impacts: end of flight {label} "
                      f"({len(m0['strata'])} strata x {len(m0['seeds'])} seeds, EoF {eof_commit}); per-row weights from the composer (product per panel; "
                      f"constraint {m0.get('constraint', '?')}). Systematic resample over all rows, one settling draw each: "
                      + ", ".join(f"{p['N']:,}" for p in info["products"]) + ". 0.02 deg grid, Gaussian 0.1 deg, HPD. Row ESS by Kish; below 1,000 not estimable. "
                      f"Labels: {os.environ.get('WF_RUN_LABELS', 'core (b) split-half NOT converged; composer PIPELINE TEST')}; Mac, 2 threads.")
    g["FOOT_TECH"] = foot_subs(g["FOOT_TECH"], {"strata": m0["strata"], "evidence_suffix": "+" + m0.get("constraint", "alive")})
    exec(open(pathlib.Path(__file__).with_name("wreckage_map_standard.py")).read(), g)


if __name__ == "__main__":
    {"prep": prep, "render": render}[sys.argv[1]](*sys.argv[2:])
