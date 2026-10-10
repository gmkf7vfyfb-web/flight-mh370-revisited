"""Composer pass 0: per-stratum histograms of the composed products, pooled exactly as summary.rs pools replicates.

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.

This is a line-for-line TRANSCRIPTION of summary.rs (`pooling`, `grid_bin`, the latitude grid) and of the unlanded
patch B (`results/composer-summary-rs.patch`: `authalic_q`, `equal_area_cell`, the 2-D equal-area map). It is not a
second summariser by intent: patch B is not on the branch (summary.rs is core-owned), so the composed products cannot
yet go through summary.rs itself. Delete this file when core lands patch B and the runner stage (core requests B, C).
Smoothing and stats() are applied in report.py, also transcribed.

Writes <out>/<stratum>/hist.npz: per product id, the pooled latitude histogram (summary.rs grid), the two split-half
histograms (seeds 1-2 and 3-4, each pooled by its own pooling()), per-EoF-family histograms, the equal-area cell map
(pooled and per half), per-seed pool factors; and the composed pooled weight at settling's resampled outcome rows.

Usage: python summarise_stratum.py <stratum> <input dir> <rust out dir> <out dir>
"""
import json, pathlib, sys
import numpy as np

GRID_MIN, GRID_MAX, GRID_STEP = -50.0, 50.0, 0.05
MAP_STEP, MAP_LAT, MAP_LON = 0.25, (-50.0, 10.0), (55.0, 125.0)
A_KM, F = 6378.137, 1.0 / 298.257223563
E2 = F * (2.0 - F)
# EoF family_code (compact_impacts.family_labels): 1 A1, 2 A2, 4 A then lost; B split 15:45 -0600 10 Oct into
# 3 B controlled, 5 B controlled then lost, 6 B uncontrolled. Pass 1 ran with range(5), so codes 5 and 6 were not
# histogrammed; report.py recovers B as the complement (see there).
NFAM = 7
BANDS = [(-90.0, -39.0), (-39.0, -36.0), (-36.0, -33.0), (-33.0, -30.0), (-30.0, 0.0)]
NPTS = int(round((GRID_MAX - GRID_MIN) / GRID_STEP)) + 1
SETTLING = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d5fc8d7c-15e5-4858-b15e-9553989a6413/work")
FAMILY_EVIDENCE = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/summary/family-evidence-next-run-b.json")


def authalic_q(lat):
    e = np.sqrt(E2); s = np.sin(np.radians(lat))
    return (1.0 - E2) * (s / (1.0 - E2 * s * s) - np.log((1.0 - e * s) / (1.0 + e * s)) / (2.0 * e))


Q_STEP = authalic_q(MAP_STEP) - authalic_q(0.0)
CELL_KM2 = 0.5 * A_KM * A_KM * np.radians(MAP_STEP) * Q_STEP
NY = int(np.ceil((authalic_q(MAP_LAT[1]) - authalic_q(MAP_LAT[0])) / Q_STEP))
NX = int(round((MAP_LON[1] - MAP_LON[0]) / MAP_STEP))


def grid_bin(lat):
    b = np.floor((lat - GRID_MIN + GRID_STEP / 2.0) / GRID_STEP)
    ok = np.isfinite(b) & (b >= 0) & (b < NPTS)
    return np.where(ok, b, -1).astype(np.int64)


def equal_area_cell(lat, lon):
    inside = (lat >= MAP_LAT[0]) & (lat < MAP_LAT[1]) & (lon >= MAP_LON[0]) & (lon < MAP_LON[1])
    y = np.floor((authalic_q(np.where(inside, lat, 0.0)) - authalic_q(MAP_LAT[0])) / Q_STEP).astype(np.int64)
    x = np.floor((np.where(inside, lon, MAP_LON[0]) - MAP_LON[0]) / MAP_STEP).astype(np.int64)
    ok = inside & (y >= 0) & (y < NY) & (x >= 0) & (x < NX)
    return np.where(ok, y * NX + x, -1)


def pooling(modes):
    """summary.rs pooling(): modes[i][m] = (prior_weight, log_evidence or None, posterior_probability)."""
    prior = np.array([m[0] for m in modes[0]])
    lz = np.array([[(-np.inf if m[1] is None else m[1]) for m in rep] for rep in modes])
    mx = np.max(lz); z = np.exp(lz - mx)
    mean = z.mean(axis=0); weighted = prior * mean; total = weighted.sum()
    mp = weighted / total if total > 0 else np.zeros_like(weighted)
    col = z.sum(axis=0)
    within = np.array([[m[2] for m in rep] for rep in modes])
    share = np.where(col > 0, z / np.where(col > 0, col, 1.0), 0.0)
    return mp[None, :] * share / np.where(within > 0, within, 1.0), mp


def load_inputs(d, k, names):
    h = json.loads((d / f"seed-{k}.json").read_text()); c = h["columns"]
    X = np.memmap(d / f"seed-{k}.f64", dtype="<f8", mode="r", shape=(h["rows"], len(c)))
    return {n: np.array(X[:, c.index(n)]) for n in names}, h


def settling_rows(stratum_short, k, lat, lon, parent):
    """Map settling's resampled outcomes (sets A and C) of seed k onto impacts rows, by exact (parent, lat, lon)."""
    out = {}
    order = np.argsort(lat, kind="stable"); ls = lat[order]
    for T in ("A", "C"):
        f = SETTLING / stratum_short / "field" / f"{T}_impacts.f64"
        if not f.exists():
            continue
        X = np.fromfile(f).reshape(-1, 14); mine = np.where(X[:, 13] == k)[0]
        pos = np.searchsorted(ls, X[mine, 1]); pos = np.minimum(pos, ls.size - 1)
        rows = order[pos]
        ok = (lat[rows] == X[mine, 1]) & (lon[rows] == X[mine, 2]) & (parent[rows] == X[mine, 10])
        out[T] = (mine, rows, ok)
    return out


def main(stratum, ind, rout, outd):
    ind, rout = pathlib.Path(ind), pathlib.Path(rout); outd = pathlib.Path(outd) / stratum; outd.mkdir(parents=True, exist_ok=True)
    short = stratum.replace("next-", "")
    P = json.loads((rout / "products.json").read_text())
    prods = {p["id"]: p for p in P["products"]}
    fe = json.loads(FAMILY_EVIDENCE.read_text())["strata"][stratum]
    lnz_r600_plain = fe["00:19 R600 BTO Only"]["ln_Z_per_seed"]
    with_w = sorted(p.name for p in (rout / "weights").iterdir())
    cols = {}
    for k in (1, 2, 3, 4):
        d, h = load_inputs(ind, k, ["weight", "mode", "family", "latitude_deg", "longitude_deg", "parent", "loglik:r600-bto+alive"])
        d["bin"] = grid_bin(d["latitude_deg"]); d["cell"] = equal_area_cell(d["latitude_deg"], d["longitude_deg"])
        d["srows"] = settling_rows(short, k, d["latitude_deg"], d["longitude_deg"], d["parent"])
        cols[k] = d
    res = {"stratum": stratum, "cell_km2": CELL_KM2, "ny": NY, "nx": NX, "q_step": Q_STEP, "products": {}, "settling_match": {}}
    arrays = {}
    for k in (1, 2, 3, 4):
        for T, (mine, rows, ok) in cols[k]["srows"].items():
            res["settling_match"][f"{T}-seed{k}"] = [int(mine.size), int(ok.sum())]
    for pid in with_w:
        p = prods[pid]
        modes = [r["modes"] for r in p["replicates"]]
        fac, mp = pooling(modes)
        halves = [pooling(modes[:2])[0], pooling(modes[2:])[0]]
        lat_h = np.zeros(NPTS); lat_hh = [np.zeros(NPTS), np.zeros(NPTS)]
        fam_h = np.zeros((NFAM, NPTS)); fam_m = np.zeros(NFAM)
        cell_h = np.zeros(NY * NX); cell_hh = [np.zeros(NY * NX), np.zeros(NY * NX)]
        mass = 0.0
        seabed = {}
        ess_fam, ess_band = {}, {}
        for i, k in enumerate((1, 2, 3, 4)):
            d = cols[k]
            wq = np.fromfile(rout / "weights" / pid / f"seed-{k}.f32", dtype="<f4").astype(float)
            assert wq.size == d["weight"].size
            md = d["mode"].astype(int)
            w = wq * fac[i][md]
            hw = wq * halves[i // 2][i % 2][md]
            b, c, fm = d["bin"], d["cell"], d["family"].astype(int)
            okb, okc = b >= 0, c >= 0
            lat_h += np.bincount(b[okb], weights=w[okb], minlength=NPTS)
            lat_hh[i // 2] += np.bincount(b[okb], weights=hw[okb], minlength=NPTS)
            cell_h += np.bincount(c[okc], weights=w[okc], minlength=NY * NX)
            cell_hh[i // 2] += np.bincount(c[okc], weights=hw[okc], minlength=NY * NX)
            for f in range(NFAM):
                sel = okb & (fm == f)
                fam_h[f] += np.bincount(b[sel], weights=w[sel], minlength=NPTS); fam_m[f] += w[fm == f].sum()
            mass += w.sum()
            # coverage: Kish ESS (rows) of this seed's composed weights, per EoF family and per latitude band
            lat = d["latitude_deg"]
            for f in range(NFAM):
                sw = wq[fm == f]; ess_fam.setdefault(str(f), []).append(float(sw.sum() ** 2 / (sw ** 2).sum()) if (sw ** 2).sum() > 0 else 0.0)
            for lo, hi in BANDS:
                sw = wq[(lat >= lo) & (lat < hi)]
                ess_band.setdefault(f"{lo}..{hi}", []).append(float(sw.sum() ** 2 / (sw ** 2).sum()) if (sw ** 2).sum() > 0 else 0.0)
            # importance weights of settling's outcomes: pooled composed weight over the source option's pooled weight
            for T, (mine, rows, ok) in d["srows"].items():
                if (T == "A") != pid.startswith("heldout"):
                    continue
                ww = d["weight"] / d["weight"].sum()
                if T == "A":
                    src = ww[rows]                                    # none__other: hand-off weight
                else:
                    raw = d["loglik:r600-bto+alive"][rows]            # r600-bto__other; equals the +alive column where alive
                    src = ww[rows] * np.exp(np.where(np.isfinite(raw), raw, -np.inf) - lnz_r600_plain[i])
                with np.errstate(divide="ignore", invalid="ignore"):
                    iw = np.where(src > 0, w[rows] / (0.25 * src), 0.0)
                seabed[k] = (mine, np.where(ok, iw, np.nan))
        res["products"][pid] = {"mass": mass, "mode_probability": mp.tolist(), "pool_factors": fac.tolist(),
                                "family_mass": (fam_m / mass).tolist(), "ess_rows_per_seed_by_family": ess_fam,
                                "ess_rows_per_seed_by_latitude_band": ess_band}
        arrays[f"{pid}|lat"] = lat_h; arrays[f"{pid}|lat_h0"] = lat_hh[0]; arrays[f"{pid}|lat_h1"] = lat_hh[1]
        arrays[f"{pid}|fam"] = fam_h; arrays[f"{pid}|cell"] = cell_h.astype(np.float32)
        arrays[f"{pid}|cell_h0"] = cell_hh[0].astype(np.float32); arrays[f"{pid}|cell_h1"] = cell_hh[1].astype(np.float32)
        for k, (mine, iw) in seabed.items():
            arrays[f"{pid}|seabed_rows_seed{k}"] = mine; arrays[f"{pid}|seabed_iw_seed{k}"] = iw
        print(stratum, pid, "mass", round(mass, 6), flush=True)
    np.savez_compressed(outd / "hist.npz", **arrays)
    (outd / "summary.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
