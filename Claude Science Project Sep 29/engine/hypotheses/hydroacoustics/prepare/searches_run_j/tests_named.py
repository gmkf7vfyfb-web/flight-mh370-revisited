"""BLOCK 5 (iii)-(vi): the named test sets of preregistration.py section 9 against the run J windows:
Kadri Table 1 (19 rows, both times for the 306.18 deg row), the six poster boxes, Royer events B/D1/D2, infrasound.
Usage: python tests_named.py <out_dir>  (after imos_search.py and panel_search.py)
Outputs: table1_verdicts.csv, poster_boxes.csv, royer_verdicts.csv, royer_arrivals.csv, infrasound_row.json, named_summary.json."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.special import gammaln
from pyproj import Geod
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preregistration as R, common_rows as CR
import run_j_windows as W

G = Geod(ellps="WGS84")
KD = R.MODULE / "data" / "kadri_fig9_digitised"
ARC_SRC = R.EXCH / "run-j-tl-grid" / "raw" / "passA" / "sources.csv"


def log_t(x, sd, nu=3.0):
    s = sd / np.sqrt(nu / (nu - 2))
    return gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(nu * np.pi) - np.log(s) - 0.5 * (nu + 1) * np.log1p((x / s) ** 2 / nu)


def log_n(x, sd):
    return -0.5 * np.log(2 * np.pi) - np.log(sd) - 0.5 * (x / sd) ** 2


def wrap(d):
    return (d + 180.0) % 360.0 - 180.0


def arc_polyline():
    s = pd.read_csv(ARC_SRC)
    s = s[s.offset_nm == 0].sort_values("lat")
    return s.lat.values, s.lon.values


def dist_to_arc_km(lat, lon, alat, alon):
    # densify the arc polyline to ~2 km and take the nearest vertex
    pts = []
    for i in range(len(alat) - 1):
        n = max(int(G.inv(alon[i], alat[i], alon[i + 1], alat[i + 1])[2] / 2000), 2)
        pts.append(np.column_stack([np.linspace(alat[i], alat[i + 1], n), np.linspace(alon[i], alon[i + 1], n)]))
    P = np.vstack(pts)
    _, _, d = G.inv(np.full(len(P), lon), np.full(len(P), lat), P[:, 1], P[:, 0])
    j = int(np.argmin(d)); return d[j] / 1000.0, float(P[j, 0]), float(P[j, 1])


def bearing_arc_crossing(rlat, rlon, bearing, alat, alon):
    """Point where the bearing line from the receiver meets the arc: minimum distance to the arc along the line."""
    rs = np.arange(300.0, 4500.0, 2.0)
    lon, lat, _ = G.fwd(np.full(len(rs), rlon), np.full(len(rs), rlat), np.full(len(rs), bearing), rs * 1000.0)
    best = (np.inf, None)
    for r, la, lo in zip(rs[::10], lat[::10], lon[::10]):
        d, _, _ = dist_to_arc_km(la, lo, alat, alon)
        if d < best[0]: best = (d, (r, la, lo))
    return best


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    rx = W.receivers(); alat, alon = arc_polyline()
    Wn = CR.Windows(); bands = pd.read_csv(R.RD / "searches_run_j" / "prereg_impact_time_bands.csv")
    S = np.load(R.GEOM / "sample.npz"); en = json.loads((R.GEOM / "energy.json").read_text())
    bz = pd.read_csv(R.GEOM / "bearing_h01w.csv"); bmid = (bz.baz_lo + bz.baz_hi).values / 2
    cand = pd.concat([pd.read_csv(out.parent / "imos" / "imos_windows.csv"), pd.read_csv(out.parent / "panels" / "panel_windows.csv")], ignore_index=True)
    cand = cand[cand.p < R.SCREEN_P]

    def in_band(tu, o):
        r = bands[bands.option == o].iloc[0]
        for q0, q1, name in (("q25_unix", "q75_unix", "50%"), ("q5_unix", "q95_unix", "90%"), ("q0.5_unix", "q99.5_unix", "99%")):
            if r[q0] <= tu <= r[q1]: return name
        return "outside 99%"

    # ---- (a) Kadri Table 1 -------------------------------------------------------------------------------------
    t1 = pd.read_csv(KD / "kadri-table1-transients.csv")
    rows = []
    tests = [(r.event_id, r.time_utc, r.bearing_deg, "Table 1 time") for _, r in t1.iterrows()]
    tests.append(("event_005430_text", R.KADRI_TIMES["text"], 306.18, "text time 00:52:03 (same bearing row)"))
    for eid, tutc, brg, note in tests:
        tu = R.hms_to_unix(tutc)
        d_arc, (r_km, la, lo) = bearing_arc_crossing(rx["H01W"][0], rx["H01W"][1], brg, alat, alon)
        t_imp = tu - r_km / R.C_KM_S
        bf = {}
        for name, (kind, nu, sd) in R.BEARING_MODELS.items():
            lf = log_t(wrap(brg - bmid), sd) if kind == "t" else log_n(wrap(brg - bmid), sd)
            m = bz["mass_D0"].values
            bf[name] = float(np.log10(np.sum(m * np.exp(lf)) / (1.0 / 360.0)))
        v = bf["demonstrated_t3_3.3"]
        verdict = "disfavoured" if 10 ** v <= R.BF_DISFAVOURED else ("favoured" if 10 ** v >= R.BF_FAVOURED else "uninformative")
        near = cand[(cand.receiver == "H01W") & ((cand.t_unix - tu).abs() <= R.TABLE1_TOL_S)]
        rows.append(dict(event_id=eid, time_utc=tutc, bearing_deg=brg, note=note,
                         **{f"in_H01W_99pct_{o}": bool(Wn.membership("H01W", tu, "SOFAR") not in ("outside", "union only") and o in Wn.membership("H01W", tu, "SOFAR")) for o in R.OPTIONS},
                         in_H01W_union=Wn.membership("H01W", tu, "SOFAR") != "outside",
                         arc_crossing_lat=round(la, 2), arc_crossing_lon=round(lo, 2), line_to_arc_km=round(d_arc, 1), range_km=round(r_km, 0),
                         implied_impact_utc=R.unix_to_hms(t_imp), **{f"implied_time_band_{o}": in_band(t_imp, o) for o in R.OPTIONS},
                         log10_BF_demonstrated_t3_3p3=round(bf["demonstrated_t3_3.3"], 2), log10_BF_claimed_gauss_0p4=round(bf["claimed_gauss_0.4"], 2), bearing_verdict=verdict,
                         panel_rows_within_10s=int(len(near)), panel_min_p=float(near.p.min()) if len(near) else np.nan,
                         panel_best=("; ".join(f"{a.detector} {a.band_hz} p={a.p:.3f} ({a.label})" for _, a in near.sort_values("p").head(2).iterrows()) if len(near) else "none"),
                         caveats=R.CAVEATS))
    T1 = pd.DataFrame(rows); T1.to_csv(out / "table1_verdicts.csv", index=False)

    # ---- (b) poster boxes --------------------------------------------------------------------------------------
    pooled = np.load(R.EXCH / "run-j-windows" / "pooled.npz"); keys = list(pooled["keys"]); H = pooled["H"]
    edges = W.GRID0 + np.arange(W.NBIN + 1) * W.DT
    _, _, dmin = G.inv(np.full(len(alat), rx["H01W"][1]), np.full(len(alat), rx["H01W"][0]), alon, alat)
    j = int(np.argmin(dmin)); d_min_km = dmin[j] / 1000.0
    t_earliest = R.hms_to_unix("00:19:29.0") + d_min_km * 1000.0 / (R.C_FAST * 1000.0)
    t_earliest_nom = R.hms_to_unix("00:19:29.0") + d_min_km / R.C_KM_S
    boxm = pd.read_csv(out.parent / "panels" / "box_minima.csv")
    rows = []
    for name, (a, b) in R.BOXES.items():
        ua, ub = R.hms_to_unix(a), R.hms_to_unix(b)
        frac = {}
        for o in R.OPTIONS:
            h = H[keys.index(f"{o}/p0.5/H01W/SOFAR")]; c = (edges[:-1] >= ua) & (edges[1:] <= ub)
            frac[o] = float(h[c].sum() / max(h.sum(), 1e-300))
        bm = boxm[boxm.box == name]
        rows.append(dict(box=name, start=a, end=b, **{f"H01W_arrival_mass_{o}": frac[o] for o in R.OPTIONS},
                         ends_before_earliest_arc_arrival=bool(ub < t_earliest), minutes_before_earliest=round((t_earliest - ub) / 60, 1),
                         verdict_timing=("source before 00:19:29 or off the arc" if ub < t_earliest else ("marginal" if ub < t_earliest_nom + 120 else "inside the arrival span")),
                         **{f"min_p_{k}": (float(bm[bm.detector == k].min_window_p.min()) if len(bm[bm.detector == k]) else np.nan) for k in ("M1b", "D1", "BE_2-5", "BE_5-9")},
                         caveats=R.CAVEATS))
    PB = pd.DataFrame(rows); PB.to_csv(out / "poster_boxes.csv", index=False)

    # ---- (c) Royer events --------------------------------------------------------------------------------------
    lat, lon, w = S["lat"], S["lon"], S["w_D0"]
    rows, arr = [], []
    for ev, (la, lo, tutc) in R.ROYER.items():
        tu = R.hms_to_unix(tutc)
        d_arc, ala, alo = dist_to_arc_km(la, lo, alat, alon)
        _, _, dd = G.inv(np.full(len(lat), lo), np.full(len(lat), la), lon, lat); dd = dd / 1000.0
        m100, m200, m500 = (float(w[dd <= r].sum()) for r in (100, 200, 500))
        lq = en["D0"]["lat_q"]
        rec = dict(event=ev, lat=la, lon=lo, origin_utc=tutc, distance_to_arc_km=round(d_arc, 0), nearest_arc_lat=round(ala, 2),
                   D0_mass_within_100km=m100, D0_mass_within_200km=m200, D0_mass_within_500km=m500,
                   lat_vs_D0_99pct=("inside" if lq["q0.5"] <= la <= lq["q99.5"] else "outside"), lat_99pct_band=f"{lq['q0.5']:.1f} to {lq['q99.5']:.1f}",
                   **{f"time_band_{o}": in_band(tu, o) for o in R.OPTIONS}, caveats=R.CAVEATS)
        hits = []
        for r in ["H01W", "H08S", "3315", "3376", "3274", "3275", "3250"]:
            d = W.geodesic_km(np.array([la]), np.array([lo]), rx[r][0], rx[r][1])[0]
            ta = tu + d / R.C_KM_S; sd = d * R.C_SD_KM_S / R.C_KM_S ** 2
            tol = R.LAG_PAD_S + 3 * sd
            near = cand[(cand.receiver == r) & ((cand.t_unix - ta).abs() <= tol)]
            held = "panels" if r in ("H01W", "H08S") else "IMOS records"
            arr.append(dict(event=ev, receiver=r, range_km=round(d, 0), predicted_arrival_utc=R.unix_to_hms(ta), tolerance_s=round(tol, 0), held=held,
                            n_rows_within_tol=int(len(near)), min_p=float(near.p.min()) if len(near) else np.nan,
                            best=("; ".join(f"{x.time_utc} {x.detector} {x.band_hz} p={x.p:.3f} ({x.label})" for _, x in near.sort_values("p").head(2).iterrows()) if len(near) else "none")))
            if len(near): hits.append(f"{r}: {len(near)} rows, min p {near.p.min():.3f}")
            if r == "H01W":
                picks = R.ROYER_H01W_PICKS["B" if ev == "B" else "D1/D2"]
                rec["royer_H01W_picks"] = ", ".join(picks)
                rec["H01W_pick_minus_predicted_s"] = ", ".join(f"{R.hms_to_unix(p) - ta:+.0f}" for p in picks)
        rec["coincident_rows_at_predicted_lag"] = "; ".join(hits) if hits else "none at screen level"
        rows.append(rec)
    RY = pd.DataFrame(rows); RY.to_csv(out / "royer_verdicts.csv", index=False)
    pd.DataFrame(arr).to_csv(out / "royer_arrivals.csv", index=False)

    # ---- (d) infrasound ---------------------------------------------------------------------------------------
    inf = dict(R.INFRASOUND); inf["verdict"] = "carries no information (declared row; no statistic)"
    (out / "infrasound_row.json").write_text(json.dumps(inf, indent=1))
    (out / "named_summary.json").write_text(json.dumps(dict(d_min_arc_H01W_km=d_min_km, earliest_arc_arrival_H01W_fast=R.unix_to_hms(t_earliest), earliest_arc_arrival_H01W_nominal=R.unix_to_hms(t_earliest_nom),
                                                           arc_closest_lat=float(alat[j]), arc_source="block-2 TL grid pass A arc fit (sources.csv, offset 0)",
                                                           n_table1_tests=len(T1), n_disfavoured=int((T1.bearing_verdict == "disfavoured").sum()),
                                                           n_uninformative=int((T1.bearing_verdict == "uninformative").sum()), n_favoured=int((T1.bearing_verdict == "favoured").sum())), indent=1))
    print(T1[["time_utc", "bearing_deg", "in_H01W_union", "arc_crossing_lat", "range_km", "implied_impact_utc", "implied_time_band_D0", "log10_BF_demonstrated_t3_3p3", "bearing_verdict", "panel_best"]].to_string(index=False))
    print(PB[["box", "H01W_arrival_mass_D0", "H01W_arrival_mass_D4", "ends_before_earliest_arc_arrival", "minutes_before_earliest", "verdict_timing", "min_p_M1b"]].to_string(index=False))
    print(RY.T.to_string())
    print("d_min", d_min_km, R.unix_to_hms(t_earliest), R.unix_to_hms(t_earliest_nom))


if __name__ == "__main__":
    main(sys.argv[1])
