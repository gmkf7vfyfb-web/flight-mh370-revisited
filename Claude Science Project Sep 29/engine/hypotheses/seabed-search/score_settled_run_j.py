"""Score settling's run J SETTLED WRECKAGE positions with the seabed searches (Pete, 13 Oct 2026: "apply the search
likelihood to the seabed positions where settling provides them - that is what the sonar searched").

    python hypotheses/seabed-search/score_settled_run_j.py <settling stratum dir> --out <exchange out>/<stratum>
        [--binary <mh370>] [--threads 2] [--chunk 3000000] [--validate-seed K] [--min-free-gib 35]

Configuration UNCHANGED from the impact-point run J scoring (commit 08fb80b, score_run_j.py): run.toml BASE = ATSB Phase 2 +
Bluefin-21 + Ocean Infinity 2018 + Ocean Infinity 2025-26 (outboard band), inferred geometry, enforced by base_guard.check();
label "Ocean Infinity coverage inferred (grade C), included as best estimate". Without Ocean Infinity = labelled sensitivity.
rho 0 / 0.05 / 0.25 / 0.5. The planned next OI area is a MAP LAYER ONLY. Coverage c_k(x) comes from `mh370 evaluate` itself
(the module's own bilinear raster code) at every position; nothing is reimplemented. The algebra
P(no find) = rho + (1 - rho) prod_k [1 - q_k f_k c_k] is asserted against evaluate's own no_find_probability on every row.

Recipe = this module's field-coverage treatment (field_coverage_check.py; results/seabed-field-coverage-289/, run D-he
results/seabed-search-d-he/field-coverage-table.md):
  point  c_k = c_k(impact)                                 (what run J at the impact point used)
  mean   c_k = settled-mass-weighted mean of c_k(x_i)      REPORTED: the field is one object with a covered fraction
  any    c_k = 1 - prod_i [1 - c_k(x_i)]                   optimistic bound: some settled piece on searched ground
Only SETTLED elements (fate 0) count; afloat elements (fate 1) are ocean drift's evidence. An outcome with no settled element
(all afloat / not computed / refused by the ocean window) is CARRIED at its impact position, and counted.

One outcome = one (table row, settling draw). Alternative settling draws are alternative OUTCOMES: per impact row the likelihood
is the MEAN of P(no find) over the row's draws (brief section 2; never multiplied). A product's Z is the plain mean over its
equally weighted outcomes (settling's systematic resample).

Writes to --out:
  outcomes.npz      per outcome: row, draw, n_settled, settled_mass_kg, carried, c_point[4], c_mean[4], c_any[4] (campaign order
                    phase2, bluefin, ocean-infinity-2018, ocean-infinity-2025), keyed row * 2**20 + draw as settling's files
  rows.npz          per settling table row (row-aligned with <tag>_impacts.f64; source.npy maps to impacts32):
                    lnL_settled_<scen> = ln mean_d P(no find | settled field of draw d), lnL_point_<scen>, n_draws,
                    searched_fraction_settled (mean over draws), searched_fraction_point
  summary.json      per product (36, or 24 for both-burst): point / mean / any Z, searched-ground shares before -> after, ESS,
                    paired difference mean - point with its Monte Carlo SE, field-vs-point diagnostics; and all checks
"""
import argparse
import hashlib
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
sys.path.insert(0, str(HERE))
import base_guard  # noqa: E402
import score_run_j as SRJ  # noqa: E402  (LAYERS, BASE, ATSB, RHO_SWEEP, next_area_mask: the run J impact-point code)

BASE, ATSB = SRJ.BASE, SRJ.ATSB
QF = np.array([SRJ.LAYERS[n][1] for n in BASE])            # q_k * f_k
F = np.array([SRJ.LAYERS[n][2] for n in BASE])             # f_k
ATSB_IDX = [BASE.index(n) for n in ATSB]
SCEN = {"base_rho0.05": (0.05, range(4)), "base_rho0": (0.0, range(4)), "base_rho0.25": (0.25, range(4)),
        "base_rho0.5": (0.5, range(4)), "without_oi_rho0.05": (0.05, ATSB_IDX)}
STRIDE = 2 ** 20
SHARED_EXCHANGE = pathlib.Path("/Users/pete/Downloads/mh370-exchange")
IMPACT_COLUMNS = ["weight", "parent", "mode", "alternative", "family", "unix_s", "latitude_deg", "longitude_deg",
                  "velocity_east_mps", "velocity_north_mps", "velocity_up_mps", "flight_path_angle_deg", "mass_kg",
                  "kinetic_energy_j", "vertical_kinetic_energy_j", "takeover_unix_s", "takeover_latitude_deg",
                  "takeover_longitude_deg", "takeover_altitude_ft", "arc_distance_nm", "log_q_correction"]


def pnf(c, scen):
    rho, ks = SCEN[scen]
    m = np.ones(c.shape[0])
    for k in ks:
        m *= 1.0 - QF[k] * c[:, k]
    return rho + (1.0 - rho) * m


def searched(c):
    return 1.0 - np.prod(1.0 - F * c, axis=1)


def atsb_ground(c):
    return 1.0 - (1.0 - c[:, 0]) * (1.0 - c[:, 1])


def free_gib(p):
    return shutil.disk_usage(p).free / 2 ** 30


def coverage(lat, lon, work, binary, threads, min_free):
    """c_k at (lat, lon) from `mh370 evaluate run.toml` itself. Input: a temporary float64 impacts.npy with the 21 core
    columns (weight 1, position set, every other column 0: the seabed-search likelihood reads latitude and longitude only).
    Returns (c[n,4], evaluate's no_find_probability[n])."""
    n = len(lat)
    need = n * (len(IMPACT_COLUMNS) + 12) * 8 / 2 ** 30
    if free_gib(work) - need < min_free:
        sys.exit(f"STOP: free disk {free_gib(work):.1f} GiB minus chunk {need:.2f} GiB would fall below {min_free} GiB")
    src, ev = work / "in", work / "ev"
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(ev, ignore_errors=True)
    (src / "seed-1").mkdir(parents=True)
    (src / "run.json").write_text(json.dumps({"impact_columns": IMPACT_COLUMNS}))
    X = np.lib.format.open_memmap(src / "seed-1" / "impacts.npy", mode="w+", dtype=np.float64, shape=(n, len(IMPACT_COLUMNS)))
    X[:] = 0.0
    X[:, 0] = 1.0
    X[:, 6] = lat
    X[:, 7] = lon
    X.flush()
    del X
    try:
        env = dict(os.environ, RAYON_NUM_THREADS=str(threads))
        subprocess.run([str(binary), "evaluate", str(HERE / "run.toml"), str(src / "seed-1" / "impacts.npy"), str(ev)],
                       check=True, capture_output=True, cwd=ROOT, env=env)
    finally:
        shutil.rmtree(src, ignore_errors=True)
    cols = json.loads((ev / "evaluate.json").read_text())["columns"]
    V = np.load(ev / "evaluate.npy", mmap_mode="r")
    idx = {c: i for i, c in enumerate(cols)}
    c = np.column_stack([np.asarray(V[:, idx[f"seabed-search:covered_fraction_{nm}"]], np.float64) for nm in BASE])
    p = np.asarray(V[:, idx["seabed-search:no_find_probability"]], np.float64)
    del V
    shutil.rmtree(ev, ignore_errors=True)
    if c.shape[0] != n:
        sys.exit(f"evaluate returned {c.shape[0]} rows for {n} positions")
    return c, p


def verify(sd, files):
    want = {}
    for line in (sd / "SHA256SUMS").read_text().splitlines():
        h, _, p = line.partition("  ")
        want[p.strip()] = h.strip()
    for fn in files:
        h = hashlib.sha256()
        with open(sd / fn, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""):
                h.update(b)
        if want.get(fn) != h.hexdigest():
            sys.exit(f"CHECKSUM FAILED {sd / fn}: refusing to use it")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stratum_dir", type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--binary", type=pathlib.Path, default=ROOT / "target" / "release" / "mh370")
    ap.add_argument("--scratch", type=pathlib.Path, default=ROOT / "runs" / "seabed-search-analysis" / "scratch-settled-j")
    ap.add_argument("--threads", default="2")
    ap.add_argument("--chunk", type=int, default=3_000_000)
    ap.add_argument("--validate-seed", type=int, default=0, help="score only the table rows of this seed (validation)")
    ap.add_argument("--min-free-gib", type=float, default=35.0)
    ap.add_argument("--no-verify", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    label = base_guard.check()
    sd, st = a.stratum_dir, a.stratum_dir.name
    tag = next(sd.glob("*_impacts.f64")).name[: -len("_impacts.f64")]
    files = [f"{tag}_{x}" for x in ("impacts.f64", "elements.f64", "draws.npz", "source.npy", "info.json")]
    if not (sd / "READY").is_file():
        sys.exit(f"{sd}: no READY")
    if not a.no_verify:
        verify(sd, files)
    info = json.loads((sd / f"{tag}_info.json").read_text())
    imp = np.memmap(sd / f"{tag}_impacts.f64", dtype="<f8", mode="r").reshape(-1, 14)
    el = np.memmap(sd / f"{tag}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8)
    src = np.load(sd / f"{tag}_source.npy")
    dr = np.load(sd / f"{tag}_draws.npz")
    n_rows = imp.shape[0]
    work = a.scratch / f"{st}{'-v' + str(a.validate_seed) if a.validate_seed else ''}"
    work.mkdir(parents=True, exist_ok=True)
    checks = {"label": label, "table_rows": int(n_rows), "elements": int(el.shape[0])}

    # ---- outcomes: key = row * 2**20 + draw (settling's declared convention); element table is in key order
    erow = el[:, 0].astype(np.int64)
    edraw = el[:, 1].astype(np.int64)
    if edraw.max() >= STRIDE:
        sys.exit("draw index exceeds 2**20")
    key = erow * STRIDE + edraw
    if np.any(np.diff(key) < 0):
        sys.exit("element table not in (row, draw) order")
    newblk = np.empty(len(key), bool)
    newblk[0] = True
    newblk[1:] = key[1:] != key[:-1]
    okey = key[newblk]
    oidx = np.cumsum(newblk) - 1                           # outcome index of every element
    del newblk
    n_out = len(okey)
    orow = okey // STRIDE
    odraw = okey % STRIDE
    checks["outcomes"] = int(n_out)
    checks["outcomes_equal_sum_of_draws_column"] = bool(n_out == int(imp[:, 12].sum()))
    checks["every_row_has_an_outcome"] = bool(np.array_equal(np.unique(orow), np.arange(n_rows)))
    fate = el[:, 4]
    checks["element_fates"] = {str(int(f)): int(c) for f, c in zip(*np.unique(fate, return_counts=True))}

    # restrict to one seed for validation
    if a.validate_seed:
        rsel = np.where(src[:, 1] == a.validate_seed)[0]
        rmask = np.zeros(n_rows, bool)
        rmask[rsel] = True
    else:
        rmask = np.ones(n_rows, bool)
    omask = rmask[orow]

    # ---- coverage at the table's impact positions
    lat_i, lon_i = imp[:, 1].copy(), imp[:, 2].copy()
    c_row = np.zeros((n_rows, 4))
    rs = np.where(rmask)[0]
    for s in range(0, len(rs), a.chunk):
        ii = rs[s:s + a.chunk]
        c, p = coverage(lat_i[ii], lon_i[ii], work, a.binary, a.threads, a.min_free_gib)
        c_row[ii] = c
        d = float(np.abs(pnf(c, "base_rho0.05") - p).max())
        checks["max_abs_dP_algebra_vs_rust_impact"] = max(checks.get("max_abs_dP_algebra_vs_rust_impact", 0.0), d)
    if checks["max_abs_dP_algebra_vs_rust_impact"] > 1e-12:
        sys.exit(f"algebra does not reproduce evaluate at impact positions: {checks}")

    # cross-module: point arm = the published run J impact-point column at the source row (searched-areas/run-j)
    pub = SHARED_EXCHANGE / "searched-areas" / ("run-j-both-burst/run-j-waypoints" if "both-burst" in st else f"run-j/{st}")
    dmax, ncmp = 0.0, 0
    lnp_row = np.log(pnf(c_row, "base_rho0.05"))
    for k in np.unique(src[rs, 1]):
        rk = rs[src[rs, 1] == k]
        col = np.load(pub / f"seed-{k}" / "seabed-lnL.npy", mmap_mode="r")
        dmax = max(dmax, float(np.abs(lnp_row[rk] - np.asarray(col[src[rk, 2]])).max()))
        ncmp += len(rk)
    checks["point_vs_published_run_j_lnL"] = {"rows": int(ncmp), "max_abs_dlnL": dmax, "source": str(pub)}
    if dmax > 1e-5:
        sys.exit(f"point arm does not reproduce the published run J column: {dmax}")

    # ---- settled elements: chunked evaluate, accumulate per outcome
    sel_el = np.where((fate == 0.0) & omask[oidx])[0]
    checks["settled_elements_scored"] = int(len(sel_el))
    msum = np.zeros(n_out)
    nset = np.zeros(n_out, np.int64)
    mc = np.zeros((n_out, 4))
    lg = np.zeros((n_out, 4))
    dpe = 0.0
    nchunks = (len(sel_el) + a.chunk - 1) // a.chunk
    for ci, s in enumerate(range(0, len(sel_el), a.chunk)):
        ee = sel_el[s:s + a.chunk]
        c, p = coverage(el[ee, 5], el[ee, 6], work, a.binary, a.threads, a.min_free_gib)
        dpe = max(dpe, float(np.abs(pnf(c, "base_rho0.05") - p).max()))
        o = oidx[ee]
        m = el[ee, 7]
        msum += np.bincount(o, weights=m, minlength=n_out)
        nset += np.bincount(o, minlength=n_out)
        for k in range(4):
            mc[:, k] += np.bincount(o, weights=m * c[:, k], minlength=n_out)
            lg[:, k] += np.bincount(o, weights=np.log1p(-np.clip(c[:, k], 0.0, 1.0 - 1e-12)), minlength=n_out)
        print(json.dumps({"stratum": st, "chunk": ci + 1, "of": nchunks, "free_gib": round(free_gib(work), 1),
                          "wall_s": round(time.time() - t0, 1)}), flush=True)
    checks["max_abs_dP_algebra_vs_rust_elements"] = dpe
    if dpe > 1e-12:
        sys.exit("algebra does not reproduce evaluate at element positions")

    c_point = c_row[orow]
    carried = (nset == 0) | (msum <= 0)
    c_mean = np.where(carried[:, None], c_point, mc / np.maximum(msum, 1e-300)[:, None])
    c_any = np.where(carried[:, None], c_point, 1.0 - np.exp(lg))
    checks["outcomes_carried_at_impact_position"] = int((carried & omask).sum())
    checks["outcomes_in_scope"] = int(omask.sum())

    # ---- tests from the brief (section 8) on this data
    # averaging test: a row whose outcome is duplicated must keep its likelihood (mean, not product)
    o1 = int(np.where(omask & ~carried)[0][0])
    P1 = pnf(c_mean[[o1]], "base_rho0.05")[0]
    P2 = pnf(c_mean[[o1, o1]], "base_rho0.05").mean()
    checks["averaging_test_two_identical_draws_equal_one"] = bool(abs(P1 - P2) < 1e-15)
    # off-ground test: an outcome whose settled pieces all lie off coverage returns ln L exactly 0
    off = omask & ~carried & (c_mean.max(axis=1) == 0.0)
    checks["off_ground_outcomes"] = int(off.sum())
    checks["off_ground_lnL_exactly_zero"] = bool(np.all(np.log(pnf(c_mean[off], "base_rho0.05")) == 0.0)) if off.any() else None

    # ---- per row aggregate (mean over the row's draws, never a product)
    rows_out = {"n_draws": np.bincount(orow, minlength=n_rows)}
    nd = np.maximum(rows_out["n_draws"], 1)
    for scen in SCEN:
        Pm = pnf(c_mean, scen)
        rows_out[f"lnL_settled_{scen}"] = np.log(np.bincount(orow, weights=Pm, minlength=n_rows) / nd)
        rows_out[f"lnL_point_{scen}"] = np.log(pnf(c_row, scen))
    rows_out["lnL_settled_any_base_rho0.05"] = np.log(np.bincount(orow, weights=pnf(c_any, "base_rho0.05"), minlength=n_rows) / nd)
    rows_out["searched_fraction_settled"] = np.bincount(orow, weights=searched(c_mean), minlength=n_rows) / nd
    rows_out["searched_fraction_point"] = searched(c_row)
    for k, v in rows_out.items():
        if k.startswith("lnL") and not np.isfinite(v[rmask]).all():
            sys.exit(f"non-finite {k}")
    checks["rows_finite"] = True

    # ---- products
    nxt_row = SRJ.next_area_mask(lat_i, lon_i).astype(np.float64)
    north_row = (lat_i > -33.0).astype(np.float64)
    prods = []
    if not a.validate_seed:
        for j, pr in enumerate(info["products"]):
            r, d = dr[f"rows_{j}"].astype(np.int64), dr[f"draws_{j}"].astype(np.int64)
            o = np.searchsorted(okey, r * STRIDE + d)
            if not np.array_equal(okey[np.clip(o, 0, n_out - 1)], r * STRIDE + d):
                sys.exit(f"product {j}: an outcome is absent from the element table")
            N = len(o)
            rec = {k: pr[k] for k in ("option", "D", "cell", "subset", "N", "row_ess_kish", "share_of_option")}
            rec["carried"] = int(carried[o].sum())
            for tname, C in (("point", c_point[o]), ("mean", c_mean[o]), ("any", c_any[o])):
                sf, ag = searched(C), atsb_ground(C)
                nx, no = nxt_row[r], north_row[r]
                t = {"on_searched_before": float(sf.mean()), "on_atsb_before": float(ag.mean()),
                     "next_area_before": float(nx.mean()), "north33_before": float(no.mean())}
                for scen in SCEN:
                    P = pnf(C, scen)
                    S = P.sum()
                    t[scen] = {"Z": float(P.mean()), "Z_se": float(P.std(ddof=1) / np.sqrt(N)),
                               "on_searched_after": float((P * sf).sum() / S), "on_atsb_after": float((P * ag).sum() / S),
                               "next_area_after": float((P * nx).sum() / S), "north33_after": float((P * no).sum() / S),
                               "outcome_ess_after": float(S * S / (P * P).sum())}
                rec[tname] = t
            for scen in SCEN:
                dd = pnf(c_mean[o], scen) - pnf(c_point[o], scen)
                da = pnf(c_any[o], scen) - pnf(c_point[o], scen)
                rec.setdefault("paired", {})[scen] = {"mean_minus_point": float(dd.mean()), "se": float(dd.std(ddof=1) / np.sqrt(N)),
                                                      "any_minus_point": float(da.mean()), "se_any": float(da.std(ddof=1) / np.sqrt(N))}
            sp, sm = searched(c_point[o]), searched(c_mean[o])
            rec["diagnostics"] = {"share_point_off_field_on": float(((sp == 0) & (sm > 0)).mean()),
                                  "share_point_on_field_off": float(((sp > 0) & (sm == 0)).mean()),
                                  "share_abs_dsearched_gt_0.05": float((np.abs(sm - sp) > 0.05).mean()),
                                  "mean_settled_elements": float(nset[o].mean())}
            prods.append(rec)

    # ---- publish
    a.out.mkdir(parents=True, exist_ok=True)
    def save(fn, **arrs):
        tmp = a.out / (fn + ".part.npz")
        np.savez(tmp, **arrs)
        os.replace(tmp, a.out / fn)
    sl = slice(None)
    save("outcomes.npz", row=orow.astype(np.int32), draw=odraw.astype(np.int32), n_settled=nset.astype(np.int32),
         settled_mass_kg=msum.astype(np.float32), carried=carried.astype(np.uint8), in_scope=omask.astype(np.uint8),
         c_point=c_point[sl].astype(np.float32), c_mean=c_mean.astype(np.float32), c_any=c_any.astype(np.float32),
         campaigns=np.array(BASE))
    save("rows.npz", **{k: (v.astype(np.float64) if k == "lnL_settled_base_rho0.05" else
                           v.astype(np.int32) if k == "n_draws" else v.astype(np.float32)) for k, v in rows_out.items()})
    checks["wall_s"] = time.time() - t0
    (a.out / "summary.json").write_text(json.dumps({"stratum": st, "tag": tag, "validate_seed": a.validate_seed,
                                                    "checks": checks, "products": prods}, indent=1))
    sums = []
    for fn in ("outcomes.npz", "rows.npz", "summary.json"):
        sums.append(f"{hashlib.sha256((a.out / fn).read_bytes()).hexdigest()}  {fn}")
    (a.out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"stratum": st, "done": True, **{k: v for k, v in checks.items() if k != "label"}}), flush=True)


if __name__ == "__main__":
    main()
