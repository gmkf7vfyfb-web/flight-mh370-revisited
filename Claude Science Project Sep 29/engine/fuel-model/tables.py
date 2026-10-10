"""Table lookup for the internal fuel model (fuel session, 9-10 Oct 2026; core request 16 C).

Reads `data/fuel-tables.json` (extract.py output of Ulich's 9M-MRO fuel model v5.6; git-ignored,
never committed or uploaded) and prices a state (FL, gross weight t, Mach) on the standard day.

`fixed=False` reproduces the lookup of `crates/flight/src/fuel.rs` at commit 74e2e15 (the audit's
"as coded" model). `fixed=True` applies the audit's lookup fixes:

  F3  bilinear corners whose interpolation weight is exactly zero need not exist, so an exact grid
      level next to the data frontier (e.g. FL400 beside a missing FL410/FL430 cell) is priced
      instead of being dropped;
  F4  below the slowest schedule: if that schedule is holding and its partner is >= 0.03 Mach away,
      the U-shaped a M^2 + b / M^2 fit (a, b > 0) is kept, which rises again on the back side, but
      never below 0.95 x the holding flow (Boeing's slow items imply at most 3.5 % below holding);
      otherwise the flow is clamped at the slowest schedule's flow (no pockets from close pairs);
  F17 schedules within 5e-3 Mach are still merged (one speed; the averaged flow is the
      least-squares value there).
Below FL060 (only holding is tabulated) the fixed model scales the FL060 Mach curve by the holding
flow ratio hold(FL)/hold(FL060) instead of evaluating at FL060.

Flows are per aircraft (both engines; for the INOP set, the one live engine, not doubled), kg/h, standard day,
before calibration and temperature.
"""

import json
import math
from pathlib import Path

import numpy as np

RACETRACK = 1.05
MERGE_TOL = 5e-3
MIN_TAB_FL = 60.0
MIN_SPAN = 0.03
BACKSIDE_FLOOR = 0.95
SCHEDULES = [("holding_mach", "holding_ff", 1 / RACETRACK), ("mrc_mach", "mrc_ff", 1.0),
             ("ci52_mach", "ci52_ff", 1.0), ("lrc_mach", "lrc_ff", 1.0), (None, "m084_ff", 1.0)]
INOP = [("holding_inop_mach", "holding_inop_ff", 1 / RACETRACK), ("lrc_inop_mach", "lrc_inop_ff", 1.0)]


class Grid:
    """One weight x flight-level grid; filler and missing cells are NaN."""

    def __init__(self, raw):
        self.fls = np.array(raw["flight_levels"], float)
        self.ws = np.array(raw["weights_t"], float)
        v = np.full((len(self.ws), len(self.fls)), np.nan)
        self.cls = [[None] * len(self.fls) for _ in self.ws]
        for i, row in enumerate(raw["values"]):
            for j, x in enumerate(row):
                c = raw["source_class"][i][j]
                self.cls[i][j] = c
                if x is not None and c != "filler":
                    v[i, j] = x
        self.v = v

    def _cell(self, fl, w):
        fls, ws = self.fls, self.ws
        if fl < fls[0] or fl > fls[-1] or w < ws[0] or w > ws[-1]:
            return None
        j = min(max(int(np.searchsorted(fls, fl, side="right") - 1), 0), len(fls) - 2)
        i = min(max(int(np.searchsorted(ws, w, side="right") - 1), 0), len(ws) - 2)
        x = (fl - fls[j]) / (fls[j + 1] - fls[j])
        y = (w - ws[i]) / (ws[i + 1] - ws[i])
        return ((i, j, (1 - x) * (1 - y)), (i + 1, j, (1 - x) * y), (i, j + 1, x * (1 - y)), (i + 1, j + 1, x * y))

    def bilinear(self, fl, w, fixed=True):
        corners = self._cell(fl, w)
        if corners is None:
            return None
        acc = 0.0
        for a, b, wt in corners:
            val = self.v[a, b]
            if math.isnan(val):
                if fixed and wt == 0.0:
                    continue
                return None
            acc += val * wt
        return acc

    def classes_used(self, fl, w):
        corners = self._cell(fl, w)
        return [] if corners is None else [(self.cls[a][b], wt) for a, b, wt in corners if wt > 0]


def drag_fit(m0, f0, m1, f1):
    det = m0**2 / m1**2 - m1**2 / m0**2
    if abs(det) < 1e-6:
        return None
    return (f0 / m1**2 - f1 / m0**2) / det, (m0**2 * f1 - m1**2 * f0) / det


class Tables:
    def __init__(self, path, inop=False, low_rule="physical"):
        self.low_rule = low_rule
        doc = json.loads(Path(path).read_text())
        self.source = doc.get("source", {})
        self.grids = {k: Grid(v) for k, v in doc["tables"].items()}
        sched = INOP if inop else SCHEDULES
        self.schedules = [(self.grids[m] if m else None, self.grids[f], s, f) for m, f, s in sched]
        self.hold = self.schedules[0][1]
        # The twin tables are per engine (x2 for the aircraft); the INOP tables already give the one live
        # engine's flow, so they are NOT doubled (internal-v1 doubled them: fixed in internal-v1.1).
        self.engines = 1.0 if inop else 2.0
        self.fl_grid = sorted({float(x) for _, g, _, _ in self.schedules for x in g.fls})

    def points_at(self, fl, w, fixed=True, names=False):
        pts = []
        for mt, ft, scale, name in self.schedules:
            f = ft.bilinear(fl, w, fixed)
            m = 0.84 if mt is None else mt.bilinear(fl, w, fixed)
            if f is not None and m is not None:
                pts.append((m, f * scale, name))
        pts.sort()
        merged = []
        for m, f, nm in pts:
            if merged and m - merged[-1][0] <= MERGE_TOL:
                n = merged[-1][2] + 1
                merged[-1] = (merged[-1][0] + (m - merged[-1][0]) / n, merged[-1][1] + (f - merged[-1][1]) / n, n,
                              merged[-1][3] + [nm])
            else:
                merged.append((m, f, 1, [nm]))
        self._last_lowest = merged[0][3][0] if merged else None
        return [(m, f, nm) if names else (m, f) for m, f, _, nm in merged]

    def _lowest_is_holding(self, pts):
        return getattr(self, "_last_lowest", None) == self.schedules[0][3]

    def _price(self, pts, mach, fixed, flags):
        if len(pts) == 1:
            flags["single_schedule"] = True
            return pts[0][1], 0
        top = len(pts) - 1
        if mach > pts[top][0]:
            flags["extrap_high"] = True
        if mach < pts[0][0]:
            flags["extrap_low"] = True
        if mach < pts[0][0]:
            k = 0
        elif mach >= pts[top][0]:
            k = top - 1
        else:
            k = max(i for i in range(top) if pts[i][0] <= mach)
        (m0, f0), (m1, f1) = pts[k][:2], pts[k + 1][:2]
        ab = drag_fit(m0, f0, m1, f1)
        if ab is None:
            flags["fit_fallback"] = True
            per = f1
        else:
            per = ab[0] * mach**2 + ab[1] / mach**2
            if not (per > 0 and math.isfinite(per)):
                flags["fit_fallback"] = True
                per = max(f0, f1)
        if fixed and mach < pts[0][0]:
            # The U-shaped fit is trusted only from the holding (minimum-flow) schedule and a partner
            # at least MIN_SPAN Mach away; a close pair (e.g. CI 52 / LRC 0.015 apart near the ceiling)
            # extrapolates to pockets far below any tabulated flow (audit F4), so it is clamped instead.
            ok = (ab is not None and ab[0] > 0 and ab[1] > 0 and self._lowest_is_holding(pts)
                  and pts[1][0] - pts[0][0] >= MIN_SPAN)
            if self.low_rule == "clamp" or not ok:
                if per < pts[0][1]:
                    flags["floor_clamped"] = True
                    per = pts[0][1]
            else:  # "physical": keep the U-shaped fit (a, b > 0), which rises again below M* = (b/a)^1/4
                # Bounded at BACKSIDE_FLOOR x the slowest schedule's flow: Boeing's slow Table 4 items
                # imply flows at most 3.5 % below holding (FL350 M0.694); beyond that the fit is unvalidated.
                floor = max(2.0 * math.sqrt(ab[0] * ab[1]), BACKSIDE_FLOOR * pts[0][1])
                if per < floor:
                    flags["floor_clamped"] = True
                    per = floor
        return per, k

    def ff_isa(self, fl, w, mach, fixed=True, detail=False):
        """(kg/h, flags) on the standard day, uncalibrated; (None, flags) if unpriceable."""
        flags = {}
        scale = 1.0
        fl_eval = fl
        if fl < MIN_TAB_FL:
            flags["below_tables"] = True
            if fixed:
                h_lo = self.hold.bilinear(max(fl, self.hold.fls[0]), w, True)
                h_60 = self.hold.bilinear(MIN_TAB_FL, w, True)
                if h_lo is not None and h_60:
                    scale = h_lo / h_60
            fl_eval = MIN_TAB_FL
        pts = self.points_at(fl_eval, w, fixed)
        if not pts:
            for cand in reversed(self.fl_grid):
                if cand < fl_eval:
                    p = self.points_at(cand, w, fixed)
                    if p:
                        pts, fl_eval = p, cand
                        flags["above_ceiling"] = True
                        break
            if not pts:
                return None, flags
        per, k = self._price(pts, mach, fixed, flags)
        if detail:
            flags["pts"] = pts
            flags["fl_eval"] = fl_eval
            flags["k"] = k
        return self.engines * per * scale, flags

    def ceiling_fl(self, w, fixed=True, step=1.0, lo=200.0):
        """Highest FL (to `step`) at which any schedule prices this weight (the tables' frontier)."""
        fl = 430.0
        while fl >= lo:
            if self.points_at(fl, w, fixed):
                return fl
            fl -= step
        return None


def isa_temp_k(fl):
    h = fl * 100 * 0.3048
    return 288.15 - 0.0065 * h if h < 11000 else 216.65


def isa_mach(fl, tas_kt):
    return tas_kt * 0.514444 / math.sqrt(1.4 * 287.05287 * isa_temp_k(fl))


def delta_isa(fl, sat_c):
    return sat_c + 273.15 - isa_temp_k(fl)
