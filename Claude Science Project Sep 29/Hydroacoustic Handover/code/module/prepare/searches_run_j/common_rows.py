"""Shared row-building helpers for the run J searches: p-values against a null, labels, window membership, Kadri
labels, and the 'eta_needed' coupling column (preregistration.py sections 5-7)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
import preregistration as R


def p_value(score, null):
    null = np.asarray(null, float); null = null[np.isfinite(null)]
    k = np.sum(null >= score)
    return (k + 1.0) / (len(null) + 1.0), len(null)


class Windows:
    def __init__(self):
        self.W = pd.read_csv(R.RD / "searches_run_j" / "prereg_windows.csv")

    def union(self, rx, branch):
        r = self.W[(self.W.receiver == rx) & (self.W.branch == branch) & (self.W.kind == "union")].iloc[0]
        return float(r.start_unix), float(r.end_unix)

    def membership(self, rx, t_unix, branch):
        g = self.W[(self.W.receiver == rx) & (self.W.branch == branch)]
        opts = [r.option for _, r in g[g.kind == "option99"].iterrows() if r.start_unix <= t_unix <= r.end_unix]
        if opts: return "+".join(opts)
        u = g[g.kind == "union"].iloc[0]
        return "union only" if u.start_unix <= t_unix <= u.end_unix else "outside"


def kadri_label(t_unix, table1=None):
    labs = []
    for name, (a, b) in R.BOXES.items():
        if R.hms_to_unix(a) <= t_unix <= R.hms_to_unix(b): labs.append(name)
    if table1 is not None:
        for _, r in table1.iterrows():
            if abs(t_unix - R.hms_to_unix(r.time_utc)) <= R.TABLE1_TOL_S: labs.append(f"Table 1 {r.time_utc} ({r.bearing_deg} deg)")
    return "; ".join(labs) if labs else "unlabelled"


def band_fraction(fc_lo, fc_hi, tau):
    """Energy fraction in [fc_lo, fc_hi] for an ESD flat to 1/tau and f^-2 above, normalised over 1-500 Hz
    (imos_stageB_map.band_fraction convention, band edges instead of a third octave)."""
    f = np.logspace(0, np.log10(500), 4000); fr = 1.0 / tau
    esd = np.where(f <= fr, 1.0, (f / fr) ** -2.0)
    tot = np.trapezoid(esd, f); m = (f >= fc_lo) & (f <= fc_hi)
    return float(np.trapezoid(esd[m], f[m]) / tot)


class Coupling:
    """eta_needed = observed excess 5-40 Hz band energy (Pa^2 s) / [E_med rho c/(2 pi) S_5-40(tau_med) 10^(-TL/10)]."""

    def __init__(self):
        en = json.loads((R.GEOM / "energy.json").read_text())["D0"]
        self.E = en["E_j_q"]["q50"]; self.tau = en["tau90_s_q"]["q50"]; self.lat_med = en["lat_q"]["q50"]
        self.Sb = band_fraction(*R.BAND_MAIN, self.tau)
        self.tl = {}
        if R.TL_GRID.exists():
            g = pd.read_csv(R.TL_GRID)
            g = g[(g.src_depth_m == 10.0) & (g.fc_hz >= 5.0) & (g.fc_hz <= 40.0)]
            g = g[np.isfinite(g.tl_db)]
            if len(g):
                src = g.drop_duplicates("source_id")[["source_id", "src_lat"]]
                for rx, gr in g.groupby("receiver"):
                    s = src[src.source_id.isin(gr.source_id)]
                    if not len(s): continue
                    sid = s.iloc[(s.src_lat - self.lat_med).abs().argmin()].source_id
                    v = gr[gr.source_id == sid].tl_db.values
                    self.tl[str(rx)] = (float(-10 * np.log10(np.mean(10 ** (-v / 10)))), sid, len(v))
        self.pred1 = self.E * R.RHO_C / (2 * np.pi) * self.Sb   # Pa^2 s at 1 m, eta = 1

    def eta_needed(self, rx, excess_pa2s):
        if rx not in self.tl:
            return np.nan, "TL pending (grid)"
        tl, sid, n = self.tl[rx]
        if tl > 300:
            return np.inf, f"blocked path (pass A TL {tl:.0f} dB, {sid})"
        if not np.isfinite(excess_pa2s) or excess_pa2s <= 0:
            return np.nan, "no excess"
        return float(excess_pa2s / (self.pred1 * 10 ** (-tl / 10))), f"TL {tl:.1f} dB ({sid}, {n} bands, pass A)"
