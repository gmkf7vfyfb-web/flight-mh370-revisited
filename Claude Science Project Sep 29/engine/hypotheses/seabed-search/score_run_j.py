"""Score end of flight's run J (compact format) with the seabed searches, at the IMPACT point, and publish the columns.

    python hypotheses/seabed-search/score_run_j.py <eof stratum dir> <seed-N> --out <exchange out>/<stratum>/<seed-N>
        [--core <core run-j root>] [--summary <json>] [--binary <mh370>] [--threads 2]

BASE (Pete, 13 Oct 2026; restated 18 Oct 2026): ATSB Phase 2 + Bluefin-21 + Ocean Infinity 2018 + Ocean Infinity 2025-26 (outboard
band) at the inferred geometry, label "Ocean Infinity coverage inferred (grade C), included as best estimate". run.toml carries it and
`base_guard.check()` refuses anything else. "Without Ocean Infinity" is a labelled sensitivity. The PLANNED next Ocean Infinity area
(2025-26 inboard / north-west band) is a MAP LAYER ONLY: published as a 0/1 column, never part of any likelihood.

Format conversion (Pete approved the module's interim conversion edits, 18 Oct 2026 00:41Z). Run J is in end of flight's compact
format (impacts32.npy + parents32.npy + per-seed run.json, run-i-dive layout). `mh370 evaluate` refuses it because run.json
`impact_columns` does not begin with the 21 core IMPACT_COLUMNS (a core-owned check in crates/mh370/src/impacts.rs, NOT changed).
The conversion is the stub accepted by this module on 11 Oct 2026 (architecture.md ~16:40 UTC, amended to per-seed temporary
directories): `pleiades/prepare/compact_eval.eval_input` rebuilds a TEMPORARY float64 file with exactly the 21 core columns:
  - latitude_deg, longitude_deg and every other stored column: copied from the compact file through end of flight's own reader
    (`end-of-flight/smoke/compact_impacts.load`), with unix times restored as t + T0;
  - mode / alternative: joined from parents32 by `parent`;
  - kinetic_energy_j = 1/2 m |v|^2, vertical_kinetic_energy_j = 1/2 m v_up^2 (end of flight's stated identities);
  - log_q_correction = 0 (compact `weight` already carries the within-parent correction).
The seabed-search likelihood reads latitude and longitude only, so no rebuilt column enters it (checked bit-identical on run C,
11 Oct). The temporary directory is per SEED and deleted after evaluate has run.

Columns written, row-aligned with the seed's impacts32.npy (row i here = row i there):
  seabed-lnL.npy                         float64  ln P(no find | impact), BASE, rho 0.05 - evaluate's own `loglik` column
  seabed-lnL-rho0.npy / -rho0.25 / -rho0.5  float32  same base, rho swept (exact algebra on the coverage columns, checked)
  seabed-lnL-without-oi.npy              float32  SENSITIVITY: Phase 2 + Bluefin-21 only, rho 0.05
  seabed-searched-fraction.npy           float32  1 - prod_k (1 - f_k c_k(y)) over the four base campaigns ("on searched ground")
  next-oi-area-layer.npy                 uint8    1 inside the planned next OI area (inboard band), MAP LAYER ONLY, not evidence
With --with-coverage (validation and on request; NOT in the run J publication, to keep disk small) also the raw raster coverage
c_k(y) per campaign, float32: seabed-coverage-{phase2, bluefin, ocean-infinity-2018, ocean-infinity-2025}.npy.
P(no find | y) = rho + (1 - rho) prod_k [1 - c_k(y) q_k f_k], point target, shared misses (lib.rs).
"""
import argparse
import hashlib
import inspect
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                     # engine/
PROJ = ROOT.parent                                         # 'Claude Science Project Sep 29'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "hypotheses" / "pleiades" / "prepare"))
sys.path.insert(0, str(ROOT / "hypotheses" / "end-of-flight" / "smoke"))
import base_guard  # noqa: E402
import compact_eval as ce  # noqa: E402

# name -> (file tag, q_k * f_k, f_k): the values in run.toml, which base_guard.check() enforces
LAYERS = {"phase2-2014-2017": ("phase2", 0.945 * 1.0, 1.0), "bluefin-2014": ("bluefin", 0.9 * 1.0, 1.0),
          "ocean-infinity-2018": ("ocean-infinity-2018", 0.9 * 0.889, 0.889),
          "ocean-infinity-2025": ("ocean-infinity-2025", 0.9 * 0.7808, 0.7808)}
BASE = list(LAYERS)
ATSB = ["phase2-2014-2017", "bluefin-2014"]
RHO_SWEEP = (0.0, 0.05, 0.25, 0.5)
NEXT_GEOJSON = PROJ.parent / "Sept 27 2026 backup PL ChatGPT instance" / "2026-09-28_codex_drift_and_search_update" / \
    "combined_panel_versions" / "search_footprints.geojson"
NEXT_ID = "oi2024_proposed_inboard_northwest"
CELL = lambda d: f"{d} total q=0.333 (C2 silent)"           # end of flight's headline cell; D0 = D0' (00:19 values held out)
DKEYS = [f"D{d}" for d in range(6)]
FAMS = {"A1": (1,), "A2": (2,), "B": (3, 6)}               # as the composer (family B = codes 3 + 6)


def p_no_find(cov, names, rho):
    m = np.ones(len(cov[names[0]]))
    for n in names:
        m *= 1.0 - cov[n] * LAYERS[n][1]
    return rho + (1.0 - rho) * m


def next_area_mask(lat, lon):
    """Point in polygon (with holes) on the traced inboard band, read by path from the frozen snapshot. Not evidence."""
    from matplotlib.path import Path as MPath
    doc = json.loads(NEXT_GEOJSON.read_text())
    f = next(f for f in doc["features"] if f["properties"].get("id") == NEXT_ID)
    geom = f["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    inside = np.zeros(len(lat), bool)
    box = (lat > -40) & (lat < -30) & (lon > 88) & (lon < 100)
    pts = np.column_stack([lon[box], lat[box]])
    acc = np.zeros(len(pts), bool)
    for rings in polys:
        ib = MPath(np.asarray(rings[0])[:, :2]).contains_points(pts)
        for hole in rings[1:]:
            ib &= ~MPath(np.asarray(hole)[:, :2]).contains_points(pts)
        acc |= ib
    inside[np.where(box)[0]] = acc
    return inside


def verify(sd):
    """SHA256 of the files this module reads, against the producer's SHA256SUMS."""
    want = {}
    for line in (sd / "SHA256SUMS").read_text().splitlines():
        h, _, p = line.partition("  ")
        want[pathlib.Path(p.strip()).name] = h.strip()
    for fn in ("impacts32.npy", "parents32.npy", "run.json"):
        h = hashlib.sha256()
        with open(sd / fn, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""):
                h.update(b)
        if want.get(fn) != h.hexdigest():
            sys.exit(f"CHECKSUM FAILED {sd / fn}: refusing to use it")


def seed_cells_fn():
    """end of flight's option_table_0019.seed_terms, unchanged up to its final reduction (as the composer's reduce_seed_views)."""
    import displacement_hist as DH
    import option_table_0019 as OT
    DH.SATCOM_CSV = (ROOT / "data" / "satcom-observations.csv").resolve()
    OT.SATCOM_CSV = DH.SATCOM_CSV
    src = inspect.getsource(OT.seed_terms)
    src = src[:src.index("    out = {}")] + "    return cells, f4, g\n"
    ns = dict(OT.__dict__)
    exec(src, ns)
    return ns["seed_terms"]


def summarise(cells, f4, lnP, union, atsb, nxt, lat):
    """Per (00:19 option, family) sums for pooling across seeds: log scale s, and sums of m, mP, m*on, m*on*P, m^2, (mP)^2."""
    out = {}
    for d in DKEYS:
        a = cells[CELL(d)]
        fin = np.isfinite(a)
        s = float(a[fin].max()) if fin.any() else 0.0
        m = np.where(fin, np.exp(a - s), 0.0)
        rec = {"s": s}
        for fam, codes in [("all", None)] + list(FAMS.items()):
            mf = m if codes is None else m * np.isin(f4, codes)
            r = {"m": float(mf.sum()), "m2": float((mf * mf).sum()),
                 "on_union": float((mf * union).sum()), "on_atsb": float((mf * atsb).sum()),
                 "next": float((mf * nxt).sum()), "north33": float((mf * (lat > -33.0)).sum())}
            for key, lp in lnP.items():
                mp = mf * np.exp(lp)
                r[key] = {"mP": float(mp.sum()), "mP2": float((mp * mp).sum()),
                          "on_union": float((mp * union).sum()), "on_atsb": float((mp * atsb).sum()),
                          "next": float((mp * nxt).sum()), "north33": float((mp * (lat > -33.0)).sum())}
            rec[fam] = r
        out[d] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stratum_dir", type=pathlib.Path)
    ap.add_argument("seed")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--core", type=pathlib.Path, default=pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/run-j"))
    ap.add_argument("--summary", type=pathlib.Path)
    ap.add_argument("--binary", type=pathlib.Path, default=ROOT / "target" / "release" / "mh370")
    ap.add_argument("--scratch", type=pathlib.Path, default=ROOT / "runs" / "seabed-search-analysis" / "scratch-run-j")
    ap.add_argument("--threads", default="2")
    ap.add_argument("--with-coverage", action="store_true")
    ap.add_argument("--keep-eval", type=pathlib.Path, help="copy evaluate.npy/json here (validation only)")
    a = ap.parse_args()
    t0 = time.time()
    label = base_guard.check()
    st, sd = a.stratum_dir.name, a.stratum_dir / a.seed
    verify(sd)
    a.scratch.mkdir(parents=True, exist_ok=True)
    tmp = a.scratch / f"c-{st}-{a.seed}"          # per SEED (the 11 Oct amendment), so concurrent seeds never collide
    ev = a.scratch / f"e-{st}-{a.seed}"
    n_rows = int(np.load(sd / "impacts32.npy", mmap_mode="r").shape[0])
    try:
        src = ce.eval_input(sd, tmp)
        env = dict(os.environ, RAYON_NUM_THREADS=str(a.threads))
        subprocess.run([str(a.binary), "evaluate", str(HERE / "run.toml"), str(src), str(ev)],
                       check=True, capture_output=True, cwd=ROOT, env=env)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    cols = json.loads((ev / "evaluate.json").read_text())["columns"]
    V = np.load(ev / "evaluate.npy")
    if a.keep_eval:
        a.keep_eval.mkdir(parents=True, exist_ok=True)
        shutil.copy(ev / "evaluate.json", a.keep_eval / "evaluate.json")
    shutil.rmtree(ev, ignore_errors=True)
    idx = {c: i for i, c in enumerate(cols)}
    cov = {n: V[:, idx[f"seabed-search:covered_fraction_{n}"]].astype(np.float64) for n in BASE}
    rust_lnL = V[:, idx["seabed-search:loglik"]].astype(np.float64)
    rust_p = V[:, idx["seabed-search:no_find_probability"]].astype(np.float64)
    del V

    # ---- checks: rows, finiteness, algebra against the Rust on every row
    checks = {"rows_impacts32": n_rows, "rows_evaluate": int(len(rust_lnL))}
    if len(rust_lnL) != n_rows:
        sys.exit(f"{sd}: evaluate returned {len(rust_lnL)} rows for {n_rows} impacts")
    P = {r: p_no_find(cov, BASE, r) for r in RHO_SWEEP}
    checks["max_abs_dP_algebra_vs_rust"] = float(np.abs(P[0.05] - rust_p).max())
    checks["max_abs_dlnL_algebra_vs_rust"] = float(np.abs(np.log(P[0.05]) - rust_lnL).max())
    if checks["max_abs_dP_algebra_vs_rust"] > 1e-12 or checks["max_abs_dlnL_algebra_vs_rust"] > 1e-10:
        sys.exit(f"{sd}: algebra does not reproduce evaluate: {checks}")
    lnP = {"base_rho0.05": rust_lnL}
    for r in (0.0, 0.25, 0.5):
        lnP[f"base_rho{r:g}"] = np.log(P[r])
    lnP["without_oi_rho0.05"] = np.log(p_no_find(cov, ATSB, 0.05))
    for k, v in lnP.items():
        if not np.isfinite(v).all():
            sys.exit(f"{sd}: non-finite {k} on {int((~np.isfinite(v)).sum())} rows")
    checks["finite_all_rows"] = True

    union = 1.0 - np.prod([1.0 - LAYERS[n][2] * cov[n] for n in BASE], axis=0)
    atsb = 1.0 - (1.0 - cov["phase2-2014-2017"]) * (1.0 - cov["bluefin-2014"])
    _, g, _ = ce.seed_reader(sd)
    lat, lon = g("latitude_deg"), g("longitude_deg")
    nxt = next_area_mask(lat, lon)
    # map layer only: confirm it is not searched ground in the base (it may touch it at the band edges)
    checks["next_area_rows"] = int(nxt.sum())
    checks["next_area_rows_with_base_coverage"] = int((nxt & ((cov["ocean-infinity-2025"] > 0) | (cov["ocean-infinity-2018"] > 0)
                                                               | (cov["phase2-2014-2017"] > 0))).sum())

    # ---- publish (temporary names, renamed when complete)
    a.out.mkdir(parents=True, exist_ok=True)
    files = [("seabed-lnL.npy", rust_lnL.astype(np.float64)),
             ("seabed-lnL-rho0.npy", lnP["base_rho0"].astype(np.float32)),
             ("seabed-lnL-rho0.25.npy", lnP["base_rho0.25"].astype(np.float32)),
             ("seabed-lnL-rho0.5.npy", lnP["base_rho0.5"].astype(np.float32)),
             ("seabed-lnL-without-oi.npy", lnP["without_oi_rho0.05"].astype(np.float32)),
             ("seabed-searched-fraction.npy", union.astype(np.float32)),
             ("next-oi-area-layer.npy", nxt.astype(np.uint8))]
    if a.with_coverage:
        files += [(f"seabed-coverage-{LAYERS[n][0]}.npy", cov[n].astype(np.float32)) for n in BASE]
    sums = []
    for fn, arr in files:
        assert arr.shape[0] == n_rows
        tmpf = a.out / (fn + ".part.npy")
        np.save(tmpf, arr)
        os.replace(tmpf, a.out / fn)
        h = hashlib.sha256((a.out / fn).read_bytes()).hexdigest()
        sums.append(f"{h}  {fn}")
    (a.out / "SHA256SUMS").write_text("\n".join(sums) + "\n")

    # ---- per-seed reduction under end of flight's own option cells (D0' etc.), for the results note
    if a.summary:
        hand = a.core / st / "bto-bfo" / a.seed / "handoff-m0011" / "handoff.npy"
        cells, f4, _ = seed_cells_fn()(sd, hand)
        summ = summarise(cells, np.asarray(f4), lnP, union, atsb, nxt.astype(np.float64), lat)
        a.summary.parent.mkdir(parents=True, exist_ok=True)
        a.summary.write_text(json.dumps({"stratum": st, "seed": a.seed, "rows": n_rows, "label": label, "checks": checks,
                                         "options": summ, "wall_s": time.time() - t0}, indent=0))
    print(json.dumps({"stratum": st, "seed": a.seed, "rows": n_rows, "wall_s": round(time.time() - t0, 1), **checks}), flush=True)


if __name__ == "__main__":
    main()
