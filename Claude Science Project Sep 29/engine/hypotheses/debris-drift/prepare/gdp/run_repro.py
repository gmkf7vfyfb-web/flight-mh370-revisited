"""Driver for the Davey ch. 11 reproduction (PROVISIONAL; see davey_ch11.py for method and assumptions).

  python run_repro.py simulate NAME [KEY=VALUE ...]   arrival weights per start -> DERIVED/arrivals_NAME.npz
  python run_repro.py evaluate POSTERIOR_JSON OUT_JSON  likelihood at the posterior map cells, all cases

Single-threaded by construction (numpy/scipy only, no multiprocessing). Each `simulate` is sized to
run in under ten minutes on one core; set OMP_NUM_THREADS=1 etc. in the calling shell.

The posterior is the core run's 0.25 deg (lat, lon) map, `cases[0].map` = [i_lat, i_lon, density
per deg^2], cell = [lat0 + i*step, lat0 + (i+1)*step) (summary.rs map_cell uses floor). Each cell is
treated as ONE weighted particle at the cell centre, weight = density * step^2 (the task's ruling).
Latitude quantiles are read from the per-0.25-deg-row latitude histogram, linear within rows.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import davey_ch11 as dc  # noqa: E402
import load_gdp  # noqa: E402

DATA = "/Users/pete/Downloads/mh370-ocean-data/gdp"
DERIVED = os.path.join(DATA, "derived")
NM_PER_DEG = 60.0

# simulation cases: name -> overrides of dc.CONFIG (plus n_seg / seed)
SIM_CASES = {
    "joined": dict(JOIN_KM=150.0, JOIN_DOY=30),                          # default, ~30 partners
    "joined_seed2": dict(JOIN_KM=150.0, JOIN_DOY=30, SEED=2),             # Monte Carlo replicates
    "joined_seed3": dict(JOIN_KM=150.0, JOIN_DOY=30, SEED=3),
    "joined_seed4": dict(JOIN_KM=150.0, JOIN_DOY=30, SEED=4),
    "unjoined": dict(N_SEG=1),                                            # real drifters only
    "joined_tight": dict(JOIN_KM=50.0, JOIN_DOY=15),                      # ~4 partners
    "joined_R100": dict(JOIN_KM=150.0, JOIN_DOY=30, R_KM=100.0),
    "joined_R400": dict(JOIN_KM=150.0, JOIN_DOY=30, R_KM=400.0),
}
# likelihood cases: (label, simulation, sigma_deg, eps)
POOLS = {"joined_pool4": ["joined", "joined_seed2", "joined_seed3", "joined_seed4"]}
EVAL_CASES = [
    ("POOLED 4 seeds (40 MC per start): joined, 1.0 deg, eps 1e-4", "joined_pool4", 1.0, 1e-4),
    ("POOLED 4 seeds: joined, 0.5 deg, eps 1e-4", "joined_pool4", 0.5, 1e-4),
    ("POOLED 4 seeds: joined, 0.25 deg, eps 1e-4", "joined_pool4", 0.25, 1e-4),
    ("POOLED 4 seeds: joined, 1.0 deg, eps 1e-6", "joined_pool4", 1.0, 1e-6),
    ("POOLED 4 seeds: joined, 0.5 deg, eps 1e-6", "joined_pool4", 0.5, 1e-6),
    ("POOLED 4 seeds: joined, 0.25 deg, eps 1e-6", "joined_pool4", 0.25, 1e-6),
    ("joined seed 3, 1.0 deg, eps 1e-4", "joined_seed3", 1.0, 1e-4),
    ("joined seed 4, 1.0 deg, eps 1e-4", "joined_seed4", 1.0, 1e-4),
    ("seed 3, 0.25 deg, eps 1e-6", "joined_seed3", 0.25, 1e-6),
    ("seed 4, 0.25 deg, eps 1e-6", "joined_seed4", 0.25, 1e-6),
    ("Davey: joined, 1.0 deg, eps 1e-4", "joined", 1.0, 1e-4),
    ("joined seed 2, 1.0 deg, eps 1e-4", "joined_seed2", 1.0, 1e-4),
    ("joined, 0.5 deg, eps 1e-4", "joined", 0.5, 1e-4),
    ("joined, 0.25 deg, eps 1e-4", "joined", 0.25, 1e-4),
    ("joined, 1.0 deg, eps 1e-6", "joined", 1.0, 1e-6),
    ("joined, 0.5 deg, eps 1e-6", "joined", 0.5, 1e-6),
    ("joined, 0.25 deg, eps 1e-6", "joined", 0.25, 1e-6),
    ("seed 2, 0.25 deg, eps 1e-6", "joined_seed2", 0.25, 1e-6),
    ("UN-JOINED, 1.0 deg, eps 1e-4", "unjoined", 1.0, 1e-4),
    ("UN-JOINED, 0.25 deg, eps 1e-6", "unjoined", 0.25, 1e-6),
    ("joined tight (50 km, 15 d), 1.0 deg, eps 1e-4", "joined_tight", 1.0, 1e-4),
    ("joined R = 100 km, 1.0 deg, eps 1e-4", "joined_R100", 1.0, 1e-4),
    ("joined R = 400 km, 1.0 deg, eps 1e-4", "joined_R400", 1.0, 1e-4),
]


def tracks_and_starts(cfg):
    z = load_gdp.load(os.path.join(DERIVED, "gdp_daily_undrogued.npz"))
    tr = dc.Tracks(z["drifter"], z["day"], z["lat"], z["lon"], r_km=cfg["R_KM"])
    lo0, lo1, la0, la1 = cfg["BOX"]
    s = np.flatnonzero(np.isin(tr.month, cfg["MONTHS"]) & (tr.lon >= lo0) & (tr.lon <= lo1)
                       & (tr.lat >= la0) & (tr.lat <= la1))
    return tr, s


def simulate(name, extra):
    cfg = dict(dc.CONFIG, **SIM_CASES.get(name, {}))
    for kv in extra:
        k, v = kv.split("=")
        cfg[k] = type(dc.CONFIG[k])(v)
    tr, s = tracks_and_starts(cfg)
    st = {}
    t = time.time()
    a = dc.simulate(tr, s, cfg=cfg, rng=np.random.default_rng(cfg["SEED"]), n_seg=cfg["N_SEG"], stats=st)
    st.update(seconds=round(time.time() - t, 1), n_starts=int(len(s)), n_mc=cfg["N_MC"],
              arrival_fraction=float(a.mean()), n_starts_arriving=int((a > 0).sum()),
              n_drifters_arriving=int(len(np.unique(tr.drifter[s][a > 0]))),
              n_start_drifters=int(len(np.unique(tr.drifter[s]))),
              start_years=[int(y) for y in np.unique(tr.day[s].astype("datetime64[D]").astype("datetime64[Y]")
                                                     .astype(int) + 1970)[[0, -1]]])
    out = os.path.join(DERIVED, f"arrivals_{name}.npz")
    np.savez_compressed(out, start_idx=s, lat=tr.lat[s], lon=tr.lon[s], arrive=a,
                        config=json.dumps(cfg), stats=json.dumps(st))
    print(json.dumps(dict(name=name, out=out, **st)))


def load_posterior(path):
    j = json.load(open(path))
    m, case = j["map"], j["cases"][0]
    a = np.asarray(case["map"], float)
    step = m["step"]
    lat = m["lat"][0] + (a[:, 0] + 0.5) * step
    lon = m["lon"][0] + (a[:, 1] + 0.5) * step
    w = a[:, 2] * step * step
    nrow = int(round((m["lat"][1] - m["lat"][0]) / step))
    edges = m["lat"][0] + step * np.arange(nrow + 1)
    return dict(lat=lat, lon=lon, w=w, ilat=a[:, 0].astype(int), edges=edges, nrow=nrow, step=step,
                particles=case["particles"], stats=case["stats"])


def hpd(edges, h, p):
    h = np.asarray(h, float) / np.sum(h)
    o = np.argsort(-h / np.diff(edges))
    k = np.searchsorted(np.cumsum(h[o]), p) + 1
    sel = np.sort(o[:k])
    return [float(edges[sel.min()]), float(edges[sel.max() + 1])]


def summarise(P, w):
    h = np.bincount(P["ilat"], weights=w, minlength=P["nrow"])
    q = dc.weighted_quantiles(P["edges"], h, [0.05, 0.25, 0.5, 0.75, 0.95])
    return dict(median=float(q[2]), q50=[float(q[1]), float(q[3])], q90=[float(q[0]), float(q[4])],
                hpd50_rows=hpd(P["edges"], h, 0.5), hpd90_rows=hpd(P["edges"], h, 0.9),
                mean=float(np.sum(w * P["lat"]) / np.sum(w)))


def evaluate(post_path, out_path):
    P = load_posterior(post_path)
    before = summarise(P, P["w"])
    rows, lmaps = [], {}
    for label, sim, sigma, eps in EVAL_CASES:
        files = [os.path.join(DERIVED, f"arrivals_{s_}.npz") for s_ in POOLS.get(sim, [sim])]
        if not all(os.path.exists(f) for f in files):
            rows.append(dict(label=label, sim=sim, missing=True))
            continue
        zs = [np.load(f) for f in files]
        z = zs[0]
        assert all(np.array_equal(zz["start_idx"], z["start_idx"]) for zz in zs)
        arrive = np.mean([zz["arrive"] for zz in zs], axis=0)       # pooled = more MC per start
        cfg = json.loads(str(z["config"]))
        l, num, den = dc.likelihood(z["lat"], z["lon"], arrive, P["lat"], P["lon"], cfg, sigma=sigma, eps=eps)
        w1 = P["w"] * l
        after = summarise(P, w1)
        m = P["w"] > 0
        lw = l[m] / np.sum(P["w"][m] * l[m]) * np.sum(P["w"][m])      # likelihood relative to its prior mean
        rows.append(dict(label=label, sim=sim, sigma_deg=sigma, eps=eps, after=after,
                         shift_median_deg=after["median"] - before["median"],
                         shift_median_nm=(after["median"] - before["median"]) * NM_PER_DEG,
                         shift_mean_nm=(after["mean"] - before["mean"]) * NM_PER_DEG,
                         ess_fraction=dc.ess_fraction(P["w"], l),
                         l_rel_range_over_mass=[float(np.min(lw)), float(np.max(lw))],
                         tv_before_after=float(0.5 * np.sum(np.abs(w1 / w1.sum() - P["w"] / P["w"].sum()))),
                         den_min_over_mass=float(np.min(den[m])), num_max_over_mass=float(np.max(num[m])),
                         sim_stats=[json.loads(str(zz["stats"])) for zz in zs]))
        lmaps[label] = l
    res = dict(posterior=post_path, before=before, cases=rows, n_cells=int(len(P["w"])),
               n_cells_positive=int(np.sum(P["w"] > 0)), particles_pooled=P["particles"],
               core_stats=P["stats"])
    json.dump(res, open(out_path, "w"), indent=1)
    np.savez_compressed(out_path.replace(".json", "_lmaps.npz"), lat=P["lat"], lon=P["lon"], w=P["w"],
                        labels=np.array(list(lmaps)), l=np.array(list(lmaps.values())))
    return res


if __name__ == "__main__":
    if sys.argv[1] == "simulate":
        simulate(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "evaluate":
        r = evaluate(sys.argv[2], sys.argv[3])
        print(json.dumps(r["before"]))
        for c in r["cases"]:
            print(c["label"], {k: c[k] for k in ("shift_median_nm", "ess_fraction")} if "after" in c else "MISSING")
