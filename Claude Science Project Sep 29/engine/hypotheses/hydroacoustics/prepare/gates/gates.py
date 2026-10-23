"""Checks applied to every hydroacoustic detection row (hydro clean-up run, 23 Oct 2026, proposal v6 block 2).

Each function returns a verdict string and never removes a row. Verdicts are LABELS for the reader; a row is not
called a candidate or "feasible" here. Physical impossibility (coupling > 1, impact before the 7th-arc log-on) is
labelled IMPOSSIBLE; everything else is a label with its reason.

Definitions and their sources (registry ids in registry/REGISTRY.json):
  band corner      IMOS loggers 8 Hz (constant imos_hw_corner); Kadri digitised panels H01W/H08S 5 Hz (kadri_highpass).
                   BELOW_CORNER: whole band below; MOSTLY_BELOW_CORNER: < 50 % of the band width above the corner (flag);
                   PARTLY_BELOW_CORNER: >= 50 % above (information only, not a flag).
  receiver         Scott Reef 3250: path blocked, carries no information (defect D03)
  airgun shots     H08S only; |t - nearest shot| <= 1.5 s (constant shot_window, agent choice, not ruled). Per Pete
                   (23 Oct) a shot coincidence is NOT an exclusion: the row is linked to the existing shot-template
                   subtraction residual (weak-signal test set (c), run-j-weak-signal/h08s/surviving_candidates.csv).
  land path        WGS84 geodesic, 2,000 points, GEBCO 2026 15 arc-second elevation > 0 m, excluding points within
                   10 km of either end (receiver moorings and island stations sit on shelves).
  impact time      implied impact before 00:19:29 UTC is IMPOSSIBLE (last satellite log-on; module convention).
  known events     Royer 2016 events: predicted arrival per receiver within the cross-ID tolerance; at H01W also the
                   digitised pick bars (royer_figure_marks.csv) +/- 2 s and appendix arrows +/- 20 s (the cross-ID
                   tolerance at H01W; Royer's figure marks sit 7.7-16.6 s after his table times, an open question).
                   A match is "time-consistent", not proof.
  coupling         loudness-match coupling scaled from the energy at which it was computed to the q99 run J impact
                   energy at that latitude (D0 weights, +/- 1 deg), then given against 2.1e-4 (old) and 2.26e-3
                   (Metz, pending ruling). eta > 1 at q99 energy is IMPOSSIBLE.
"""
from __future__ import annotations
import json, re
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod

IMOS = {"3315", "3376", "3274", "3275", "3250"}
PANELS = {"H01W", "H08S"}
CORNER_HZ = {**{r: 8.0 for r in IMOS}, **{r: 5.0 for r in PANELS}}
NO_INFO = {"3250": "NO_INFORMATION (Scott Reef 3250: blocked path, D03)"}
ETA_OLD, ETA_METZ = 2.1e-4, 2.26e-3
T_0019 = 19 * 60 + 29  # 00:19:29 in s after midnight UTC
GEOD = Geod(ellps="WGS84")


def hms(s) -> float:
    if not isinstance(s, str) or not s.strip():
        return np.nan
    m = re.match(r"^\s*(\d{1,2}):(\d{2}):(\d{2}(?:\.\d+)?)", s)
    return np.nan if not m else int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def band_check(rx: str, band: str) -> str:
    rx = str(rx)
    if rx not in CORNER_HZ:
        return "UNKNOWN_RECEIVER"
    m = re.match(r"^\s*([\d.]+)\s*-\s*([\d.]+)", str(band))
    if not m:
        return f"NOT_A_BAND ({band})"
    lo, hi, c = float(m[1]), float(m[2]), CORNER_HZ[rx]
    if hi <= c:
        return f"BELOW_CORNER (band {lo:g}-{hi:g} Hz, corner {c:g} Hz)"
    if lo < c:
        frac = (hi - c) / (hi - lo)
        tag = "MOSTLY_BELOW_CORNER" if frac < 0.5 else "PARTLY_BELOW_CORNER"
        return f"{tag} (band {lo:g}-{hi:g} Hz, corner {c:g} Hz, {100*frac:.0f}% of band above corner)"
    return "IN_BAND"


def receiver_check(rx: str) -> str:
    return NO_INFO.get(str(rx), "OK")


class Shots:
    def __init__(self, shots_csv, residual_csv):
        self.t = np.sort(pd.read_csv(shots_csv).t.values.astype(float))
        r = pd.read_csv(residual_csv)
        r["t"] = r.utc.map(hms)
        self.res = r

    def check(self, rx, t, win=1.5):
        if str(rx) != "H08S" or not np.isfinite(t):
            return "n/a", np.nan, "n/a"
        dt = float((self.t - t)[np.argmin(np.abs(self.t - t))])
        if abs(dt) > win:
            return "NOT_COINCIDENT", dt, "n/a"
        near = self.res[(np.abs(self.res.t - t) <= win) & (self.res.stage != "raw")]
        if len(near):
            best = near.sort_values("z", ascending=False).iloc[0]
            res = f"RESIDUAL_PEAK (stage {best.stage}, z {best.z:.1f}, {best.utc}; residual null unknown, G-W3)"
        else:
            res = "NO_RESIDUAL_PEAK_z>=3 (after shot-template subtraction)"
        return "COINCIDENT_WITH_SHOT", dt, res


class Land:
    def __init__(self, gebco_json):
        h = json.load(open(gebco_json))
        self.h = h
        self.z = np.memmap(Path(gebco_json).with_name(h["elevation_file"]), dtype=np.int16, mode="r",
                           shape=(h["nlat"], h["nlon"]))

    def elev(self, lat, lon):
        h = self.h
        i = np.clip(np.rint((np.asarray(lat) - h["lat0"]) / h["step_deg"]).astype(int), 0, h["nlat"] - 1)
        j = np.clip(np.rint((np.asarray(lon) - h["lon0"]) / h["step_deg"]).astype(int), 0, h["nlon"] - 1)
        return np.asarray(self.z[i, j])

    def path(self, lat1, lon1, lat2, lon2, n=2000, end_km=10.0):
        if not all(np.isfinite([lat1, lon1, lat2, lon2])):
            return "NO_POSITION", -1, -1
        pts = np.array(GEOD.npts(lon1, lat1, lon2, lat2, n))
        _, _, dist = GEOD.inv(lon1, lat1, lon2, lat2)
        z = self.elev(pts[:, 1], pts[:, 0])
        s = np.linspace(dist / (n + 1), dist * n / (n + 1), n)
        inner = (s > end_km * 1e3) & (s < dist - end_km * 1e3)
        n_all, n_in = int((z > 0).sum()), int((z[inner] > 0).sum())
        return ("CROSSES_LAND" if n_in > 0 else "WATER_PATH"), n_all, n_in


class Royer:
    def __init__(self, crossid_csv, marks_csv):
        c = pd.read_csv(crossid_csv)
        c["t"] = c.pred.map(hms)
        self.c = c
        m = pd.read_csv(marks_csv)
        self.m = m[m.station.astype(str).str.startswith("H01W")]

    def check(self, rx, t):
        if not np.isfinite(t):
            return "n/a"
        out = []
        k = self.c[(self.c.rx.astype(str) == str(rx)) & (np.abs(self.c.t - t) <= self.c.tol_s)]
        for _, r in k.iterrows():
            lab = r.label if isinstance(r.label, str) else str(r.event)
            out.append(f"Royer event {r.event}{'/' + lab if lab != str(r.event) else ''} ({r.cls}) predicted {r.pred} +/- {r.tol_s:g} s")
        if str(rx) == "H01W":
            for _, r in self.m.iterrows():
                if r.kind == "pick_bar" and r.t_utc_s - 2 <= t <= r.t_end_utc_s + 2:
                    out.append(f"inside Royer {r.figure} pick bar {r.t_utc}-{r.t_end_utc}")
                elif r.kind == "arrow" and abs(t - r.t_utc_s) <= 20:
                    lab = r.nearest_table5_label if isinstance(r.nearest_table5_label, str) else "untabled"
                    out.append(f"within 20 s of Royer {r.figure} arrow {r.t_utc} ({lab})")
        return "; ".join(out) if out else "NO_KNOWN_EVENT_MATCH"


class Energy:
    """q99 and median of run J impact energy within +/- 1 deg latitude, D0 weights (geometry sample)."""

    def __init__(self, sample_npz, grid=np.arange(-45.5, -13.4, 0.25)):
        g = np.load(sample_npz)
        lat, E, w = g["lat"], g["E_j"], g["w_D0"]
        k = w > 0
        lat, E, w = lat[k], E[k], w[k]
        o = np.argsort(lat)
        lat, E, w = lat[o], E[o], w[o]
        self.grid, q99, q50, nn = grid, [], [], []
        for gl in grid:
            a, b = np.searchsorted(lat, [gl - 1, gl + 1])
            nn.append(int(b - a))
            if b - a < 20:
                q99.append(np.nan); q50.append(np.nan); continue
            ee, ww = E[a:b], w[a:b]
            oo = np.argsort(ee); ee, ww = ee[oo], ww[oo]
            cw = np.cumsum(ww) / ww.sum()
            q99.append(float(ee[min(np.searchsorted(cw, 0.99), len(ee) - 1)]))
            q50.append(float(ee[min(np.searchsorted(cw, 0.5), len(ee) - 1)]))
        self.q99, self.q50, self.n = np.array(q99), np.array(q50), np.array(nn)

    def at(self, lat, which="q99"):
        arr = self.q99 if which == "q99" else self.q50
        ok = np.isfinite(arr)
        if not np.isfinite(lat) or lat < self.grid[ok].min() or lat > self.grid[ok].max():
            return np.nan
        return float(np.interp(lat, self.grid[ok], arr[ok]))


def coupling_labels(eta_at_E, E_used, E_q99):
    if not (np.isfinite(eta_at_E) and np.isfinite(E_used) and np.isfinite(E_q99)) or E_q99 <= 0:
        return np.nan, np.nan, np.nan, "NOT_COMPUTABLE"
    eta = eta_at_E * E_used / E_q99
    lab = "IMPOSSIBLE (coupling > 1 even at q99 energy)" if eta > 1 else "POSSIBLE_IN_PRINCIPLE (coupling <= 1)"
    return eta, eta / ETA_OLD, eta / ETA_METZ, lab


def time_check(t_impact):
    if not np.isfinite(t_impact):
        return "NO_IMPLIED_TIME"
    return "IMPOSSIBLE (implied impact before 00:19:29)" if t_impact < T_0019 else "AFTER_0019"
