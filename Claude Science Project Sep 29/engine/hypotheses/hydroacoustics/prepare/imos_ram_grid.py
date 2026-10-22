"""PRE-REGISTRATION and implementation: gap G-TL1 closure. RAM (parabolic equation, coupled modes; pyram) transmission
loss along the whole-arc grid at the five IMOS loggers, replacing the constant per-logger RAM correction of
`imos_tl_ramcorr_arc.csv` (tl_grid_table.ram_correct_imos, decision rule 2 of ram_tl_check.py) by a path-by-path value.
Committed to hypothesis/hydroacoustics BEFORE any RAM value on the grid was computed (the only earlier RAM values on
grid paths are the 8-path exploratory subset, tl_grid_ram_subset.py; they are the acceptance check here, not an input).
Work order 2026-10-21 (hydroacoustics), overnight unattended run 22/23 Oct 2026. PREDICTIVE, NOT CALIBRATED; caveats
C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta
swept over four decades, F-35A upper anchor 2.1e-4) travel with every number. Both Kadri times apply to anything timed
("text time 00:52:03", "caption time 00:54:30"); nothing here is timed.

WHY. The levels track found the two Perth Canyon loggers (3315, 3376; 100 m apart, 13-38 m different in depth) differ
40:1 in detectable share, and the TL-grid track's 8-path RAM subset showed RAM - KRAKEN at the IMOS seabed receivers
varying -29 to -129 dB by path. A constant per-logger correction is therefore wrong by tens of dB path by path.

RECEIVERS: 3315, 3376 (Perth Canyon), 3274, 3275 (Portland), 3250 (Scott Reef); each on its OWN path and bathymetry,
  receiver depth = min(path end depth, last profile depth) - 2 m, exactly as the grid (tl_grid_run_j.run_path).
SOURCES: the grid's arc line (tl_grid_run_j.arc_sources, same arc fit) at 1.0 deg spacing, 41.0 S to 20.0 S (22 rows),
  offsets {-30, 0, +30} NM; source depth 10 m (the grid's reference depth; the 2 m and 30 m rows take the 10 m delta,
  declared, as rule 2 did). Paths whose grid status is `land` or `no_modes_shallow` (a < 15 m profile on the track) are
  NOT run: RAM has no meaning across dry land or a 1.5 m water column; those rows keep the grid's status.
BANDS: 10, 20, 40 Hz third octaves (31.5 Hz only if the timing test shows it fits; it costs ~0.6 of a 40 Hz run).
RAM SETTINGS: identical to tl_grid_ram_subset.ram_job (reused unchanged): pyram split-step Pade, dr = 2 lambda,
  dz = lambda / 20 (lambda at 1,500 m/s), 9 frequencies log-spaced across the third octave, intensity mean over the
  last 500 m of range, 'hard' fluid half-space (cp 1650 m/s, rho 1.9, 0.5 dB/lambda), NO water absorption, spherical
  correction 10 log10(x / sin x). Environment from tl_grid_run_j.build_path (GEBCO 2026 15", WOA23 March) ->
  air9_tl_validation.build_profiles (5 km windows, 25 km sound-speed nodes).
KRAKEN (matched): adiabatic incoherent modes at the band centre, same profiles and bottom, no absorption
  (kraken_tl.tl_path, fg=None), as the subset. DELTA_noabs = TL_KRAKEN_noabs - TL_RAM per path and band.
OUTPUT PER PATH x BAND: tl_ram_db, tl_kraken_noabs_db, ram_minus_kraken_db (= -DELTA), wall_s, rcv_depth_m, range_km.
DROP-IN TABLE `imos_tl_ram_arc.csv` (same schema as imos_tl_ramcorr_arc.csv, one row per 0.5 deg lat x offset x
  logger x band x source depth; new columns ram_grid_covered, ram_grid_mode, band_extrapolated, lat_nodes_used):
  (a) DELTA(lat, offset, f): linear in log f across the computed bands, clamped at the ends (5-8 Hz take the 10 Hz
      value; band_extrapolated = True there; 25 and 31.5 Hz interpolate between 20 and 40); linear in latitude between
      the two nearest 1.0 deg nodes of the SAME offset that carry a finite RAM value (ram_grid_mode = 'interp'); if
      only one node within 1.0 deg carries one, that node (ram_grid_mode = 'nearest'); if none, the row keeps the OLD
      rule-2 value and ram_grid_covered = False (ram_grid_mode = 'old').
  (b) grid status ok:        tl_db = tl_db_raw_kraken - DELTA   (raw KRAKEN carries Francois-Garrison absorption, both
                                                                 noabs models do not, so the result = RAM + absorption).
      grid status no_modes:  tl_db = TL_RAM(log-f interpolated, clamped) + alpha_FG(f) x range  (status 'ram_fill').
      land / no_modes_shallow / zero_field: unchanged.
  (c) no floor (ramcorr_floored = False everywhere the grid is covered; the floor existed only because the constant
      delta could exceed the raw loss); ramcorr_extrapolated recomputed as False where covered. 3250 is corrected
      (it had no correction before).
COVERAGE MASK `imos_tl_ram_coverage.csv`: one row per logger x 1.0 deg lat x offset: run / not run (reason) / failed.
ACCEPTANCE CHECK (fixed now): the subset paths at the IMOS loggers that lie on this grid (3315 at 36.0 S, 3274 at
  38.0 S, 3275 at 40.0 S, 3250 at 24.0 S, offset 0, 40 Hz) must reproduce tl_grid_ram_subset's tl_ram_db to 0.5 dB,
  and 3376 at 38.5 S (not a 1.0 deg node) is rerun at 40 Hz for the same check. The code path is the same function, so
  a miss means an environment or settings drift, and the table is NOT issued until it is explained.
TIMING RULE (fixed now): three paths (3315 at 36 S, 3274 at 38 S, 3250 at 24 S) are timed at 10/20/40 Hz; the total
  is extrapolated to the open path count at the process count in use. Jobs are queued offset 0 first (all latitudes),
  then +-30 NM at even latitudes, then the rest; a wall-clock deadline stops the pool, and whatever is finished is the
  coverage (stated in the note and the mask). Process count: 6 if the 1-minute load at start is <= 10, else 4.
LEVELS RERUN (block step 3): run_j_levels.py `levels` with `--imos-tl-file imos_tl_ram_arc.csv` (amendment 2 of that
  script: file-name switch only, no other change), key D0'/p0.5 only, the IMOS receivers only, eta 2.1e-4 and 1e-3,
  both thresholds; old vs new per logger.
Usage: python imos_ram_grid.py run <out_dir> --at-bin <tools> [--procs 4] [--bands 10 20 40] [--deadline 'YYYY-MM-DDTHH:MM']
                                 [--only TAG ...] [--lat-step 1.0] [--offsets -30 0 30] [--timing]
       python imos_ram_grid.py build <out_dir> <tables_dir_of_tl_grid> <out_tables_dir>
       python imos_ram_grid.py accept <out_dir> <ram_subset.csv>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402
import tl_grid_ram_subset as RS  # noqa: E402
import tl_grid_run_j as TG  # noqa: E402

LOGGERS = ["3315", "3376", "3274", "3275", "3250"]
BANDS_ALL = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
SKIP_STATUS = {"land", "no_modes_shallow"}


def fg_db_per_km(f_hz, T=4.0, S=34.7, pH=8.0, z_m=1000.0):
    """Francois-Garrison (1982) volume absorption, dB/km, the parameters of air9_tl_validation.FG (KRAKEN's 'F')."""
    f = f_hz / 1000.0; c = 1412 + 3.21 * T + 1.19 * S + 0.0167 * z_m; D = z_m / 1000.0; Tk = T + 273
    A1 = 8.86 / c * 10 ** (0.78 * pH - 5); P1 = 1; f1 = 2.8 * np.sqrt(S / 35) * 10 ** (4 - 1245 / Tk)
    A2 = 21.44 * S / c * (1 + 0.025 * T); P2 = 1 - 1.37e-4 * z_m + 6.2e-9 * z_m ** 2; f2 = 8.17 * 10 ** (8 - 1990 / Tk) / (1 + 0.0018 * (S - 35))
    A3 = 4.937e-4 - 2.59e-5 * T + 9.11e-7 * T ** 2 - 1.5e-8 * T ** 3 if T <= 20 else 3.964e-4 - 1.146e-5 * T + 1.45e-7 * T ** 2 - 6.5e-10 * T ** 3
    P3 = 1 - 3.83e-5 * z_m + 4.9e-10 * z_m ** 2
    return A1 * P1 * f1 * f ** 2 / (f ** 2 + f1 ** 2) + A2 * P2 * f2 * f ** 2 / (f ** 2 + f2 ** 2) + A3 * P3 * f ** 2


def job(a):
    """One path x band: RAM (RS.ram_job, unchanged) and matched KRAKEN without absorption."""
    tag, bathy_csv, ssp_csv, fc, rd, work, at_bin = a
    os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
    try:
        r = RS.ram_job((tag, bathy_csv, ssp_csv, fc, 10.0, rd))
    except Exception as e:  # noqa: BLE001 — recorded as failed, the pool goes on
        return dict(tag=tag, fc_hz=fc, src_depth_m=10.0, rcv_depth_m=rd, status="ram_failed", error=str(e)[:200])
    b = pd.read_csv(bathy_csv); s = pd.read_csv(ssp_csv); rprof, prof = A.build_profiles(b, s); L = float(rprof[-1])
    root = f"noabs_{tag}_f{fc:g}".replace(".", "p"); wd = pathlib.Path(work) / tag
    try:
        K.tl_path(wd, root, fc, prof, rprof, np.array([L]), [10.0], [rd], A.BOTTOMS["hard"], at_bin, fg=None)
        sh = K.read_shd(wd / f"{root}.shd"); x = L / 6371.0
        kn = float(-20 * np.log10(np.abs(sh["p"][0, 0, 0, -1])) + 10 * np.log10(x / np.sin(x)))
    except RuntimeError as e:
        kn = np.inf if "no modes" in str(e).lower() else np.nan
    import shutil; shutil.rmtree(wd, ignore_errors=True)
    r.update(tl_kraken_noabs_db=kn, ram_minus_kraken_db=r["tl_ram_db"] - kn if np.isfinite(kn) else np.nan, status="ok")
    return r


def plan(lat_step, offsets, tables_dir):
    """Paths to run, from the grid's own status (40 Hz, 10 m): everything not land / no_modes_shallow."""
    old = pd.read_csv(pathlib.Path(tables_dir) / "imos_tl_ramcorr_arc.csv", dtype={"logger": str})
    st = old[(old.fc_hz == 40.0) & np.isclose(old.src_depth_m, 10.0)].set_index(["logger", "lat", "offset_nm"]).status
    srcs = TG.arc_sources(-41, -20, lat_step, offsets); rx = TG.receivers(LOGGERS)
    rows = []
    for _, s in srcs.iterrows():
        for lg in LOGGERS:
            gs = st.get((lg, s.lat, s.offset_nm), "missing")
            pri = 0 if s.offset_nm == 0 else (1 if abs(s.lat) % 2 == 0 else 2)
            rows.append(dict(tag=f"{s.source_id}-{lg}", logger=lg, lat=s.lat, lon=s.lon, offset_nm=s.offset_nm, grid_status=gs,
                             run=gs not in SKIP_STATUS and gs != "missing", priority=pri))
    return pd.DataFrame(rows).sort_values(["priority", "lat"], ascending=[True, False]).reset_index(drop=True), rx


def run(a):
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True); pdir = out / "paths"; pdir.mkdir(exist_ok=True)
    P_, rx = plan(a.lat_step, a.offsets, a.tables)
    if a.only: P_ = P_[P_.tag.isin(a.only)]
    P_.to_csv(out / ("plan_timing.csv" if a.timing else "plan.csv"), index=False)
    rows_csv = out / ("ram_grid_rows_timing.csv" if a.timing else "ram_grid_rows.csv")
    done = set()
    if rows_csv.exists():
        d0 = pd.read_csv(rows_csv); done = set(zip(d0.tag, d0.fc_hz))
    jobs, meta = [], []
    for _, p in P_[P_.run].iterrows():
        bcsv, scsv = pdir / f"bathy_{p.tag}.csv", pdir / f"ssp_{p.tag}.csv"
        if not (bcsv.exists() and scsv.exists()):
            bathy, ssp, info = TG.build_path(dict(lat=p.lat, lon=p.lon), rx[p.logger]); bathy.to_csv(bcsv, index=False); ssp.to_csv(scsv, index=False)
            json.dump(info, open(pdir / f"info_{p.tag}.json", "w"))
        info = json.load(open(pdir / f"info_{p.tag}.json"))
        b = pd.read_csv(bcsv); s = pd.read_csv(scsv); rprof, prof = A.build_profiles(b, s)
        rd = float(min(min(info["end_depth_m"], prof[-1][0]) - 2.0, prof[-1][0] - 1.0))
        meta.append(dict(tag=p.tag, range_km=float(rprof[-1]), rcv_depth_m=rd, min_corridor_depth_m=info["min_corridor_depth_m"], land=info["land_on_track"]))
        for fc in a.bands:
            if (p.tag, fc) in done: continue
            if info["land_on_track"]: continue
            jobs.append((p.tag, str(bcsv), str(scsv), float(fc), rd, str(out / "work"), a.at_bin))
    pd.DataFrame(meta).to_csv(out / ("paths_meta_timing.csv" if a.timing else "paths_meta.csv"), index=False)
    print("jobs", len(jobs), "procs", a.procs, "deadline", a.deadline, flush=True)
    dl = dt.datetime.fromisoformat(a.deadline) if a.deadline else None
    t0 = time.time(); n = 0; hdr = rows_csv.exists()
    with Pool(a.procs) as P, open(rows_csv, "a") as fh:
        it = P.imap_unordered(job, jobs)
        while True:
            try:
                r = it.next(timeout=max(1.0, (dl - dt.datetime.now()).total_seconds()) if dl else None)
            except StopIteration:
                break
            except Exception as e:  # multiprocessing.TimeoutError at the deadline
                print("deadline reached:", type(e).__name__, flush=True); P.terminate(); break
            r = dict(r); r["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
            pd.DataFrame([r]).to_csv(fh, header=not hdr, index=False); fh.flush(); hdr = True; n += 1
            print(f"[{n}/{len(jobs)}] {r['tag']} f{r['fc_hz']:g} {r.get('status')} ram={r.get('tl_ram_db', float('nan')):.1f} k={r.get('tl_kraken_noabs_db', float('nan')):.1f} {r.get('wall_s', 0):.0f}s", flush=True)
            if dl and dt.datetime.now() > dl:
                print("deadline reached after result", flush=True); P.terminate(); break
    json.dump(dict(wall_s=time.time() - t0, procs=a.procs, bands=a.bands, n_jobs=len(jobs), n_done=n, deadline=a.deadline, timing=a.timing),
              open(out / ("wall_timing.json" if a.timing else "wall.json"), "w"), indent=1)


def _delta_frame(rows):
    """Finite RAM rows -> per (logger, lat, offset): dict band -> (ram, delta_noabs)."""
    R = rows[rows.status == "ok"].copy()
    R["logger"] = R.tag.str.split("-").str[-1]; R["lat"] = -R.tag.str.extract(r"arc(\d+\.\d)S")[0].astype(float)
    R["offset_nm"] = R.tag.str.extract(r"S_([+-]\d+)-")[0].astype(float)
    return R


def _interp_logf(fc_known, v_known, fcs):
    ok = np.isfinite(v_known)
    if ok.sum() == 0: return np.full(len(fcs), np.nan)
    return np.interp(np.log10(fcs), np.log10(np.asarray(fc_known)[ok]), np.asarray(v_known)[ok])


def build(a):
    out = pathlib.Path(a.out); tdir = pathlib.Path(a.tables); odir = pathlib.Path(a.out_tables); odir.mkdir(parents=True, exist_ok=True)
    rows = pd.read_csv(out / "ram_grid_rows.csv"); R = _delta_frame(rows)
    bands = sorted(R.fc_hz.unique()); plan_ = pd.read_csv(out / "plan.csv", dtype={"logger": str})
    # per node x band table (the delta table)
    node = R.pivot_table(index=["logger", "lat", "offset_nm"], columns="fc_hz", values=["tl_ram_db", "tl_kraken_noabs_db", "ram_minus_kraken_db"])
    flat = R[["logger", "lat", "offset_nm", "fc_hz", "range_km", "rcv_depth_m", "tl_ram_db", "tl_kraken_noabs_db", "ram_minus_kraken_db", "wall_s"]].sort_values(["logger", "offset_nm", "lat", "fc_hz"])
    flat.to_csv(odir / "imos_ram_minus_kraken_arc.csv", index=False)
    # coverage mask
    cov = plan_.copy(); got = R.groupby(["logger", "lat", "offset_nm"]).fc_hz.apply(lambda s: " ".join(f"{f:g}" for f in sorted(s)))
    fail = rows[rows.status != "ok"]
    cov["bands_done"] = [got.get((r.logger, r.lat, r.offset_nm), "") for r in cov.itertuples()]
    cov["coverage"] = np.where(~cov.run, "not run: " + cov.grid_status, np.where(cov.bands_done == " ".join(f"{b:g}" for b in bands), "complete",
                                                                              np.where(cov.bands_done == "", "not reached (deadline)" if len(fail) == 0 else "not reached or failed", "partial bands")))
    for r in fail.itertuples():
        m = cov.tag == r.tag; cov.loc[m, "coverage"] = cov.loc[m, "coverage"].where(cov.loc[m, "bands_done"] != "", "failed: " + str(getattr(r, "error", ""))[:60])
    cov.to_csv(odir / "imos_tl_ram_coverage.csv", index=False)
    # drop-in table
    old = pd.read_csv(tdir / "imos_tl_ramcorr_arc.csv", dtype={"logger": str}); new = old.copy()
    new["ram_grid_covered"] = False; new["ram_grid_mode"] = "old"; new["band_extrapolated"] = False; new["lat_nodes_used"] = ""
    nodes = {}
    for (lg, lat, off), g in R.groupby(["logger", "lat", "offset_nm"]):
        g = g.set_index("fc_hz"); nodes[(lg, off)] = nodes.get((lg, off), {}); nodes[(lg, off)][lat] = g
    for i, r in old.iterrows():
        if r.status in SKIP_STATUS or r.status == "zero_field": continue
        nd = nodes.get((r.logger, r.offset_nm), {})
        if not nd: continue
        lats = np.array(sorted(nd)); near = lats[np.abs(lats - r.lat) <= 1.0 + 1e-9]
        if len(near) == 0: continue
        lo = near[near <= r.lat + 1e-9]; hi = near[near >= r.lat - 1e-9]
        def band_vals(lat_node, col):
            g = nd[lat_node]; return _interp_logf(g.index.values, g[col].reindex(bands).values, [r.fc_hz])[0]
        if len(lo) and len(hi):
            l0, l1 = lo.max(), hi.min()
            if abs(l1 - l0) < 1e-9:
                dlt = -band_vals(l0, "ram_minus_kraken_db"); ram = band_vals(l0, "tl_ram_db"); mode = "node"; used = f"{l0:g}"
            else:
                w = (r.lat - l0) / (l1 - l0)
                d0, d1 = -band_vals(l0, "ram_minus_kraken_db"), -band_vals(l1, "ram_minus_kraken_db"); r0, r1 = band_vals(l0, "tl_ram_db"), band_vals(l1, "tl_ram_db")
                if np.isfinite(d0) and np.isfinite(d1): dlt = (1 - w) * d0 + w * d1; ram = (1 - w) * r0 + w * r1; mode = "interp"; used = f"{l0:g} {l1:g}"
                else:
                    k = l0 if np.isfinite(d0) else l1; dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "nearest"; used = f"{k:g}"
        else:
            k = near[np.argmin(np.abs(near - r.lat))]; dlt = -band_vals(k, "ram_minus_kraken_db"); ram = band_vals(k, "tl_ram_db"); mode = "nearest"; used = f"{k:g}"
        if r.status == "ok" and np.isfinite(dlt):
            new.at[i, "tl_db"] = r.tl_db_raw_kraken - dlt
        elif r.status in ("no_modes", "ok") and np.isfinite(ram):
            new.at[i, "tl_db"] = ram + fg_db_per_km(r.fc_hz) * r.range_km; new.at[i, "status"] = "ram_fill"
        else:
            continue
        new.at[i, "ram_grid_covered"] = True; new.at[i, "ram_grid_mode"] = mode; new.at[i, "lat_nodes_used"] = used
        new.at[i, "ram_delta_applied"] = True; new.at[i, "ramcorr_extrapolated"] = False; new.at[i, "ramcorr_floored"] = False
        new.at[i, "band_extrapolated"] = bool(r.fc_hz < min(bands) - 1e-9 or r.fc_hz > max(bands) + 1e-9)
    new.to_csv(odir / "imos_tl_ram_arc.csv", index=False)
    summ = new.groupby("logger").agg(rows=("tl_db", "size"), covered=("ram_grid_covered", "sum"))
    summ["covered_share"] = summ.covered / summ.rows
    print(summ.to_string()); print(cov.groupby(["logger", "offset_nm"]).coverage.value_counts().unstack(fill_value=0).to_string())
    json.dump(dict(bands=bands, n_nodes=int(len(R.groupby(["logger", "lat", "offset_nm"]))), built=dt.datetime.now().isoformat(timespec="seconds"),
                   label="RAM along the arc grid at the IMOS loggers; PREDICTIVE, NOT CALIBRATED; C1, C2"), open(odir / "imos_tl_ram_build.json", "w"), indent=1)


def accept(a):
    out = pathlib.Path(a.out); rows = pd.concat([pd.read_csv(f) for f in [out / "ram_grid_rows.csv", out / "ram_grid_rows_timing.csv", out / "ram_grid_rows_accept.csv"] if f.exists()])
    sub = pd.read_csv(a.subset); sub = sub[sub.tag.str.split("-").str[-1].isin(LOGGERS)]
    m = sub.merge(rows[rows.status == "ok"][["tag", "fc_hz", "tl_ram_db", "tl_kraken_noabs_db"]], on=["tag", "fc_hz"], suffixes=("_subset", "_grid"))
    m["diff_ram_db"] = m.tl_ram_db_grid - m.tl_ram_db_subset; m["diff_kraken_db"] = m.tl_kraken_noabs_db_grid - m.tl_kraken_noabs_db_subset
    m["pass_0p5"] = m.diff_ram_db.abs() <= 0.5
    print(m[["tag", "fc_hz", "tl_ram_db_subset", "tl_ram_db_grid", "diff_ram_db", "diff_kraken_db", "pass_0p5"]].round(3).to_string(index=False))
    m.to_csv(out / "acceptance_check.csv", index=False)
    print("ALL PASS" if m.pass_0p5.all() and len(m) else "FAIL / INCOMPLETE", len(m), "pairs")


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("out"); r.add_argument("--at-bin", required=True); r.add_argument("--procs", type=int, default=4)
    r.add_argument("--bands", nargs="+", type=float, default=[10.0, 20.0, 40.0]); r.add_argument("--deadline"); r.add_argument("--only", nargs="*")
    r.add_argument("--lat-step", type=float, default=1.0); r.add_argument("--offsets", nargs="+", type=float, default=[-30.0, 0.0, 30.0])
    r.add_argument("--tables", default="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables"); r.add_argument("--timing", action="store_true")
    b = sp.add_parser("build"); b.add_argument("out"); b.add_argument("tables"); b.add_argument("out_tables")
    c = sp.add_parser("accept"); c.add_argument("out"); c.add_argument("subset")
    a = ap.parse_args(); {"run": run, "build": build, "accept": accept}[a.cmd](a)


if __name__ == "__main__":
    main()
