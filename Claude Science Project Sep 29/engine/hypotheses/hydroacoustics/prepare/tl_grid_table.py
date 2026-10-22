"""Drop-in replacement for the module's TL latitude tables from the whole-arc grid (block 2, work order 2026-10-21).

INPUT: the raw grid written by tl_grid_run_j.py (one or more pass directories, concatenated).
OUTPUT (<out>/, the module's results-data/tl_grid_run_j/ and the exchange copy):
  tl_grid.npz / tl_grid.csv.gz       every (source, receiver, band, source depth) row of the grid (npz = one array per column), with
                                     status in {ok, no_modes, no_modes_shallow, land, zero_field}; tl_db NaN unless ok.
                                     zero_field: FIELD returned |p| = 0 at the receiver (no mode reaches the receiver
                                     depth at the path end); treated as blocked (zero received energy), never imputed.
  ims_tl_kraken_arc.csv              schema of results-data/near_limits/ims_tl_kraken.csv (station, quantile, fc_hz,
                                     src_depth_m, range_km, tl_db) + lat, lon, offset_nm, status. RAW KRAKEN, as the old
                                     file: lhyd.Model subtracts the RAM delta (ims_ram_delta.csv) itself. H08N added
                                     (no RAM delta exists for it: ram_delta_available = False; the loader applies none).
  imos_tl_ramcorr_arc.csv            schema of results-data/ram_check/imos_tl_ramcorr.csv (quantile, logger, fc_hz,
                                     src_depth_m, rcv_depth_m, range_km, tl_db, status, n_modes_first, n_modes_min,
                                     min_profile_depth_m) + lat, lon, offset_nm. RAM-CORRECTED with the module's existing
                                     rule (ram_tl_check.py decision rule 2, ram_vs_kraken.csv): Perth Canyon delta
                                     (imp500_3376) for 3315/3376, Portland delta (imp500_3274) for 3274/3275, linear in
                                     log f, clamped, delta at 10 m also for 2 m; 'no_modes' bands take the RAM band value
                                     as before. 3250 added with NO correction (none exists; flagged). zero_field and land
                                     stay NaN.
  table_points.json                  point label -> (lat, lon, offset_nm), replacing the request.json latitude lookup.
  comparison_old_vs_new.csv          the method check: the grid method rerun at the OLD five quantile points (imp025..975,
                                     same coordinates) against the old tables, per station/logger, band, source depth,
                                     and the new offset-0 table interpolated at the old latitudes against the old tables.

FLAGS (added after the pass-A inspection, before any table was used; raw values are never altered):
  source_water_depth_m, ridge_source   GEBCO depth at the source point; ridge_source = depth < 2000 m. At 32.0 S the arc
                                       crosses Broken Ridge (1,035 m): the adiabatic model then couples the 10 m source far
                                       more strongly into the deep channel (5-13 dB lower TL at H01W and 8-31 dB at H08S, growing
                                       with frequency; about 100 dB lower at Portland than the neighbouring rows). This is the source-end form of the
                                       declared reach gap G-N2/K5 (ridge paths; adiabatic assumption). The effect is graded
                                       (2,200-2,500 m sources at 29.5-29.0 S and 22.0 S give 10-13 dB lower TL than their
                                       neighbours), and down-slope conversion of near-surface sound into the channel is a
                                       real mechanism, so the rows are KEPT in the drop-in table (ridge_policy='keep' default;
                                       'neighbours' drops flagged points and interpolates across them) and flagged; the
                                       evidence-alone band summaries are reported with and without them.
  ramcorr_floored                      IMOS only, ridge_source rows only: see ram_correct_imos; the corrected value was raised
                                       to the reference RAM value (range-scaled, -10 dB) because the constant delta would
                                       otherwise give a physically impossible loss. Elsewhere rule 2 is applied unchanged,
                                       including where it is extrapolated (flag only).
  axis_depth_m, adiabatic_suspect,     see adiabatic_flags (architecture message of 22 Oct, TL-recalibration track): TL on a
  adiabatic_suspect_excl_rx            suspect path is an upper bound on loss (adiabatic).
  ramcorr_extrapolated                 IMOS only: |raw KRAKEN - raw KRAKEN of the reference path (imp500_3376 / imp500_3274)|
                                       > 10 dB in that band, i.e. the constant RAM delta of rule 2 is applied outside the
                                       range it was derived on. Reported as coverage gap G-TL1 (RAM along the grid needed).

POINT LABELS: "quantile" carries the source_id (e.g. arc035.0S_+0). Old labels 025..975 are kept in the old files only.

INTERPOLATION RULE (stated; implemented in load_table / tl_at):
  * Primary (per_impact_lnl.py / lhyd.Model use latitude only): TL(lat) = linear interpolation in latitude along the
    offset-0 arc line, clamped at 41.0 S and 20.0 S (the old rule, np.interp on the sorted point latitudes, with the
    span 38.46-31.64 S replaced by 41-20 S). Blocked bands (NaN) propagate as NaN -> zero received energy where either
    neighbour is blocked; this is the conservative reading and is reported as such.
  * Offset-aware (optional, for callers that carry arc_distance_nm): bilinear in (lat, offset), offset clamped to the
    grid's offset span (±30 NM for the mandated grid; ±60 NM where the supplementary pass exists); points beyond the
    span take the edge value and are a declared coverage gap.
  * Within a band, no interpolation across the blocked/open boundary is attempted: a NaN neighbour gives NaN.
  * ridge_source points (see FLAGS) are kept (ridge_policy='keep'); 'neighbours' drops them before interpolation.

Usage: python tl_grid_table.py <out_dir> <pass_dir> [<pass_dir> ...]
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ram_tl_check as RC  # noqa: E402

RD = HERE.parent / "results-data"
IMS = ["H01W", "H08S", "H08N"]
IMOS = ["3315", "3376", "3250", "3274", "3275"]
RAM_GROUP = {"3315": "imp500_3376", "3376": "imp500_3376", "3274": "imp500_3274", "3275": "imp500_3274"}


def load_raw(pass_dirs):
    d = pd.concat([pd.read_csv(pathlib.Path(p) / "tl_grid.csv") for p in pass_dirs], ignore_index=True)
    zero = np.isinf(d.tl_db) & (d.status == "ok")
    d.loc[zero, "status"] = "zero_field"; d.loc[zero, "tl_db"] = np.nan
    d = d.drop_duplicates(subset=["source_id", "receiver", "fc_hz", "src_depth_m"], keep="last")
    return d


def axis_depth(lat, lon):
    """WOA23 March sound-channel axis depth (minimum c between 200 and 2,500 m) at a point."""
    import tl_grid_run_j as TG
    z, p = TG.woa_profile(float(lat), float(lon)); c = p["c_mean"]
    m = (z >= 200) & (z <= 2500) & np.isfinite(c)
    return float(z[m][np.argmin(c[m])]) if m.any() else np.nan


def adiabatic_flags(d):
    """TL-recalibration track result (22 Oct, architecture message): on sill-crossing paths the adiabatic KRAKEN excess is largely
    an artefact (air7 -> H01W: adiabatic +55 dB, RAM +16 to +22 dB). Per path: axis_depth_m at the path midpoint;
    adiabatic_suspect = 1 where the minimum corridor depth anywhere on the path (receiver end included) is shallower than
    axis + 1,500 m, or any feature is shallower than 2,000 m. Because the IMS hydrophones sit on slopes (seafloor 1,570-1,590 m
    under H01W/H08S) and the IMOS loggers on the seabed, this rule flags every path; adiabatic_suspect_excl_rx applies the
    same rule to the on-track depth excluding the last 100 km (the receiver approach), which separates sill crossings from
    the terminal slope. TL on a suspect path is an UPPER BOUND on loss (adiabatic)."""
    from pyproj import Geod
    G = Geod(ellps="WGS84")
    keys = d.drop_duplicates(["source_id", "receiver"])[["source_id", "receiver", "src_lat", "src_lon", "rcv_lat", "rcv_lon"]]
    ax = {}
    for _, r in keys.iterrows():
        mid = G.npts(r.src_lon, r.src_lat, r.rcv_lon, r.rcv_lat, 1)[0]
        ax[(r.source_id, r.receiver)] = axis_depth(mid[1], mid[0])
    d = d.copy()
    d["axis_depth_m"] = [ax[(a, b)] for a, b in zip(d.source_id, d.receiver)]
    d["adiabatic_suspect"] = ((d.min_corridor_depth_m < d.axis_depth_m + 1500.0) | (d.min_corridor_depth_m < 2000.0)).astype(int)
    d["adiabatic_suspect_excl_rx"] = ((d.min_depth_excl_last100_m < d.axis_depth_m + 1500.0) | (d.min_depth_excl_last100_m < 2000.0)).astype(int)
    return d


def ram_correct_imos(g):
    """g: grid rows of one IMOS logger. Applies ram_tl_check decision rule 2 unchanged (3250: none available)."""
    g = g.copy(); g["ram_delta_applied"] = False; g["tl_db_raw_kraken"] = g.tl_db; g["ramcorr_extrapolated"] = False; g["ramcorr_floored"] = False
    lg = str(g.receiver.iloc[0])
    if lg not in RAM_GROUP:
        return g
    cmp_ = pd.read_csv(RD / "ram_check/ram_vs_kraken.csv")
    ref = cmp_[(cmp_.path == RAM_GROUP[lg]) & np.isclose(cmp_.src_depth_m, 10.0)].set_index("fc_hz").tl_kraken_db
    ref_i = np.interp(np.log10(g.fc_hz.values), np.log10(ref.dropna().index.values), ref.dropna().values)
    g["ramcorr_extrapolated"] = (g.status == "ok") & (np.abs(g.tl_db.values - ref_i) > 10.0) & (g.fc_hz.values >= ref.dropna().index.min())
    for zs in (10.0, 30.0):
        c = cmp_[(cmp_.path == RAM_GROUP[lg]) & np.isclose(cmp_.src_depth_m, zs)].set_index("fc_hz")
        m = g.src_depth_m >= 30 if zs == 30.0 else g.src_depth_m < 30
        fcs = g.loc[m, "fc_hz"].values
        delta = RC.delta_interp(c.delta_db.to_dict(), fcs)
        ram = RC.delta_interp(c.tl_ram_db.to_dict(), fcs)
        ok = (g.loc[m, "status"] == "ok").values; nm = (g.loc[m, "status"] == "no_modes").values
        tl = g.loc[m, "tl_db"].values.astype(float)
        tl[ok] = tl[ok] - delta[ok]
        tl[nm] = ram[nm]
        # FLOOR (added after the pass-A inspection, before any use; ridge-source rows ONLY, so the old rule is unchanged
        # everywhere else): the constant delta double-counts where a ridge-top source already lowers the raw KRAKEN value
        # (35 dB "TL" over 4,100 km at Portland from 32.0 S). On ridge_source rows the corrected value may not fall below
        # the reference RAM value scaled cylindrically in range, minus 10 dB: floor = TL_RAM_ref(band) + 10 log10(R/R_ref) - 10.
        rref = float(cmp_[cmp_.path == RAM_GROUP[lg]].range_km.iloc[0])
        floor = ram + 10 * np.log10(g.loc[m, "range_km"].values / rref) - 10.0
        ridge = g.loc[m, "ridge_source"].values
        bite = ok & ridge & (tl < floor)
        tl[bite] = floor[bite]
        g.loc[m, "tl_db"] = tl; g.loc[m, "ram_delta_applied"] = True
        g.loc[g.index[m][bite], "ramcorr_floored"] = True
    return g


def build(out, pass_dirs):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    d = load_raw(pass_dirs)
    import tl_grid_run_j as TG
    m_, el_, _ = TG.gebco(); i_, j_ = TG._ij(m_, d.src_lat.values, d.src_lon.values)
    d["source_water_depth_m"] = -el_[i_, j_].astype(float); d["ridge_source"] = d.source_water_depth_m < 2000.0
    d = adiabatic_flags(d)
    arc = d[d.source_id.str.startswith("arc")].copy()
    np.savez_compressed(out / "tl_grid.npz", **{c: arc[c].to_numpy() for c in arc.columns})   # column arrays; csv index beside
    arc.to_csv(out / "tl_grid.csv.gz", index=False)
    pts = {r.source_id: dict(lat=float(r.src_lat), lon=float(r.src_lon), offset_nm=float(r.offset_nm)) for _, r in arc.drop_duplicates("source_id").iterrows()}
    (out / "table_points.json").write_text(json.dumps(pts, indent=0))
    ims = arc[arc.receiver.isin(IMS)]
    pd.DataFrame(dict(station=ims.receiver, quantile=ims.source_id, fc_hz=ims.fc_hz, src_depth_m=ims.src_depth_m, range_km=ims.range_km,
                      tl_db=ims.tl_db, lat=ims.src_lat, lon=ims.src_lon, offset_nm=ims.offset_nm, status=ims.status,
                      ram_delta_available=ims.receiver.isin(["H01W", "H08S"]), source_water_depth_m=ims.source_water_depth_m,
                      ridge_source=ims.ridge_source, axis_depth_m=ims.axis_depth_m, min_corridor_depth_m=ims.min_corridor_depth_m,
                      adiabatic_suspect=ims.adiabatic_suspect, adiabatic_suspect_excl_rx=ims.adiabatic_suspect_excl_rx)).to_csv(out / "ims_tl_kraken_arc.csv", index=False)
    im = pd.concat([ram_correct_imos(g) for _, g in arc[arc.receiver.isin(IMOS)].groupby("receiver")])
    pd.DataFrame(dict(quantile=im.source_id, logger=im.receiver, fc_hz=im.fc_hz, src_depth_m=im.src_depth_m, rcv_depth_m=im.rcv_depth_m,
                      range_km=im.range_km, tl_db=im.tl_db, status=im.status, n_modes_first=im.n_modes_first, n_modes_min=im.n_modes_min,
                      min_profile_depth_m=im.min_profile_depth_m, lat=im.src_lat, lon=im.src_lon, offset_nm=im.offset_nm,
                      ram_delta_applied=im.ram_delta_applied, tl_db_raw_kraken=im.tl_db_raw_kraken, ramcorr_extrapolated=im.ramcorr_extrapolated,
                      ramcorr_floored=im.ramcorr_floored,
                      source_water_depth_m=im.source_water_depth_m, ridge_source=im.ridge_source, axis_depth_m=im.axis_depth_m,
                      min_corridor_depth_m=im.min_corridor_depth_m, adiabatic_suspect=im.adiabatic_suspect,
                      adiabatic_suspect_excl_rx=im.adiabatic_suspect_excl_rx)).to_csv(out / "imos_tl_ramcorr_arc.csv", index=False)
    comparison(out, d, arc)
    return d


def comparison(out, d, arc):
    """(a) same points, same method: grid rerun at imp025..975 vs the old tables. (b) new offset-0 table interpolated
    in latitude at the old points' latitudes vs the old tables (includes the geometry difference)."""
    kt = pd.read_csv(RD / "near_limits/ims_tl_kraken.csv", dtype={"quantile": str})
    im = pd.read_csv(RD / "ram_check/imos_tl_ramcorr.csv", dtype={"quantile": str, "logger": str})
    ik = pd.read_csv(RD / "stageB/imos_tl.csv", dtype={"quantile": str, "logger": str})       # old IMOS raw KRAKEN
    old = d[d.source_id.str.startswith("imp")]
    rows = []
    for _, r in old.iterrows():
        q = r.source_id[3:]
        if r.receiver in ("H01W", "H08S"):
            o = kt[(kt.station == r.receiver) & (kt["quantile"] == q) & (kt.fc_hz == r.fc_hz) & np.isclose(kt.src_depth_m, r.src_depth_m)]
            kind = "ims_raw_kraken"
        elif r.receiver in ("3315", "3376", "3274", "3275"):
            o = ik[(ik.logger == r.receiver) & (ik["quantile"] == q) & (ik.fc_hz == r.fc_hz) & np.isclose(ik.src_depth_m, r.src_depth_m)]
            kind = "imos_raw_kraken"
        else:
            continue
        if len(o) == 0:
            continue
        rows.append(dict(check="same_point_same_method", receiver=r.receiver, point=q, fc_hz=r.fc_hz, src_depth_m=r.src_depth_m, kind=kind,
                         tl_old=float(o.tl_db.iloc[0]), tl_new=float(r.tl_db), status_new=r.status, status_old=o.status.iloc[0] if "status" in o else "ok",
                         range_old=float(o.range_km.iloc[0]), range_new=float(r.range_km)))
    # (b) interpolated offset-0 line at the old latitudes
    req = json.loads((HERE.parent / "data/ocean_paths/request.json").read_text())
    qlat = {p["name"][3:6]: p["a"][1] for p in req["paths"] if p["name"].startswith("imp")}
    line = arc[arc.offset_nm == 0]
    for rec, oldtab, kind in ((IMS[:2], kt, "ims_raw_kraken"), (["3315", "3376", "3274", "3275"], ik, "imos_raw_kraken")):
        key = "station" if kind.startswith("ims") else "logger"
        for st in rec:
            g = line[line.receiver == st]
            for fc in sorted(g.fc_hz.unique()):
                for zs in sorted(g.src_depth_m.unique()):
                    h = g[(g.fc_hz == fc) & (g.src_depth_m == zs)].sort_values("src_lat")
                    for q, la in qlat.items():
                        o = oldtab[(oldtab[key] == st) & (oldtab["quantile"] == q) & (oldtab.fc_hz == fc) & np.isclose(oldtab.src_depth_m, zs)]
                        if len(o) == 0:
                            continue
                        tn = float(np.interp(la, h.src_lat.values, h.tl_db.values))   # NaN propagates
                        rows.append(dict(check="interp_offset0_at_old_lat", receiver=st, point=q, fc_hz=fc, src_depth_m=zs, kind=kind,
                                         tl_old=float(o.tl_db.iloc[0]), tl_new=tn, status_new="interp", status_old=o.status.iloc[0] if "status" in o else "ok",
                                         range_old=float(o.range_km.iloc[0]), range_new=np.nan))
    c = pd.DataFrame(rows); c["delta_db"] = c.tl_new - c.tl_old
    c.to_csv(out / "comparison_old_vs_new.csv", index=False)
    s = c.dropna(subset=["delta_db"]).groupby(["check", "kind", "receiver"]).delta_db.agg(["count", "mean", lambda x: float(np.max(np.abs(x))), lambda x: float(np.sqrt(np.mean(x ** 2)))])
    s.columns = ["n", "mean_db", "max_abs_db", "rms_db"]
    s.to_csv(out / "comparison_summary.csv")
    print(s.round(2).to_string())


# ----------------------------------------------------------------------------- loader for consumers
def load_table(table_dir, bands, src_depths, offset_nm=None, ridge_policy="keep"):
    """Returns (xs, tabs) like lhyd.Model: xs sorted latitudes of the offset line (default 0), tabs[receiver][(fc, z)] =
    tl_db array over xs (NaN where blocked). IMS tables are raw KRAKEN (the caller subtracts the RAM delta as lhyd does);
    IMOS tables are RAM-corrected as the old file. offset_nm selects the arc line (nearest available offset)."""
    td = pathlib.Path(table_dir)
    ims = pd.read_csv(td / "ims_tl_kraken_arc.csv"); imo = pd.read_csv(td / "imos_tl_ramcorr_arc.csv", dtype={"logger": str})
    off = 0.0 if offset_nm is None else float(min(np.unique(ims.offset_nm), key=lambda o: abs(o - offset_nm)))
    ims, imo = ims[ims.offset_nm == off], imo[imo.offset_nm == off]
    if ridge_policy == "neighbours":      # drop ridge-source points; np.interp over the remaining latitudes spans them
        ims, imo = ims[~ims.ridge_source], imo[~imo.ridge_source]
    xs = np.array(sorted(ims.lat.unique()))
    tabs = {}
    for st, g in ims.groupby("station"):
        tabs[st] = {(fc, z): g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z)].set_index("lat").tl_db.reindex(xs).values for fc in bands for z in src_depths}
    for lg, g in imo.groupby("logger"):
        tabs[lg] = {(fc, z): g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z)].set_index("lat").tl_db.reindex(xs).values for fc in bands for z in src_depths}
    return xs, tabs


def apply_to_model(m, table_dir):
    """Swap the lhyd.Model / per_impact_lnl.Terms tables for the grid tables (amendment 9). IMS: RAM delta subtracted as
    lhyd.Model.__init__ does (imp500 path delta, 10 m for z < 30, log-f interpolation). Returns the latitude span."""
    F = m.F
    xs, tabs = load_table(table_dir, F.BANDS, F.SRC)
    rd = pd.read_csv(RD / "near_limits/ims_ram_delta.csv")
    m.xs = xs
    for lg in m.B.LOGGERS:
        m.tl_imos[lg] = tabs[lg]
    for stn in ("H01W", "H08S"):
        dd = rd[rd.path == f"imp500_{stn}"]; tab = {}
        for fc in F.BANDS:
            for z in F.SRC:
                zz = 30.0 if z >= 30 else 10.0; h = dd[np.isclose(dd.src_depth_m, zz)].set_index("fc_hz").delta_db
                delta = float(np.interp(np.log10(fc), np.log10(h.index.values), h.values))
                tab[(fc, z)] = tabs[stn][(fc, z)] - delta
        m.tl_ims[stn] = tab
    return [float(xs.min()), float(xs.max())]


def tl_at(xs, col, lat):
    """Primary rule: linear in latitude, clamped at the ends; NaN neighbours give NaN (blocked)."""
    la = np.clip(np.asarray(lat, float), xs.min(), xs.max())
    v = np.interp(la, xs, np.nan_to_num(col, nan=np.inf))
    return np.where(np.isfinite(v), v, np.nan)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2:])
