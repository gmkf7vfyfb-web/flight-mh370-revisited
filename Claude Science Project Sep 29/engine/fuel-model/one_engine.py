#!/usr/bin/env python3
"""One-engine-inoperative data for core C-7(a) and end of flight (fuel session, 10 Oct 2026).

Usage (from engine/):  python fuel-model/one_engine.py
Writes results/fuel-model/one-engine-*.csv (derived values only) and, LOCAL ONLY (git-ignored),
data/external/fuel-model/one-engine-v1.json (speed grids at the table nodes, ceiling table, drift-down model).

Sources (all from data/fuel-tables.json = Ulich v5.6, plus the workbook for the holding-INOP blocks):
  * LRC INOP Mach and fuel flow (FL070-300 x 140-300 t; 296 fppm-open cells, 1 fppm-confidential).
  * Holding INOP KIAS and Mach: read directly from the workbook sheet "Holding INOP Mach", whose two blocks
    (KIAS at B3:L12, Mach at M3:W12) extract.py concatenates into one table with a repeated FL axis
    (`holding_inop_mach` in fuel-tables.json: FL 15..300 twice). internal-v1's grid_inop happens to read the
    Mach half (checked: identical at 14,115 test states), so no delivered number changes.
  * Boeing glide 0.0034 NM/ft (SIR App. 1.6E p. 8) -> L/D = 20.7 (both engines windmilling; used for the
    one-engine drift-down, so slightly conservative).
Method:
  * Ceiling = LRC-INOP table frontier (highest FL with a non-filler LRC INOP cell). Fit W_c(h) = A delta(h)^n
    (the weight whose LRC-INOP thrust-limited ceiling is h); n = max-continuous-thrust lapse with pressure.
  * Level-off at minimum-drag speed: W_c,md = C_LRC W_c with C_LRC = D(LRC INOP)/D_min from the public polar.
  * Temperature: the tables are standard day. MCT is assumed flat-rated (no loss) to 0.7 %/C thrust loss
    (turbine-temperature-limited); central 0.35 %/C. No gain assumed when colder than ISA. ASSUMPTION.
  * Drift-down: altitude held while speed decays at g/(L/D) (D(V)/D_min - C W_c(h)/W), then constant KCAS at
    the holding-INOP KIAS with ROD = V_TAS / (L/D) (1 - C W_c(h)/W) (energy method, no kinetic-energy
    correction: ROD overstated by <= ~8 % at M0.55-0.65).
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import openpyxl
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import internal  # noqa: E402
import tables  # noqa: E402

ENGINE = HERE.parent
REPO = ENGINE.parent.parent
WORKBOOK = REPO / "library_full_audit/MH370/9M-MRO Fuel Model V5.X.xlsm"
OUTR = ENGINE.parent / "results/fuel-model"
OUTJ = ENGINE / "data/external/fuel-model/one-engine-v1.json"
LD = 20.7
G = 9.80665
K_TEMP = {"flat": 0.0, "central": 0.0035, "t4_limited": 0.007}
NODES_FIT = (180, 190, 200, 210, 220)  # weights whose LRC-INOP frontier lies inside the table (< FL300)
pr = internal.pressure_ratio


def kcas(fl, m):
    p = 101325 * pr(fl)
    qc = p * ((1 + 0.2 * m * m) ** 3.5 - 1)
    return 661.4786 * math.sqrt(5 * ((qc / 101325 + 1) ** (2 / 7) - 1))


def mach_from_kcas(fl, kc):
    qc = 101325 * ((1 + 0.2 * (kc / 661.4786) ** 2) ** 3.5 - 1)
    return math.sqrt(5 * ((qc / (101325 * pr(fl)) + 1) ** (2 / 7) - 1))


def holding_inop_blocks():
    """(KIAS grid, Mach grid) from the two blocks of the workbook sheet, with extract.py's source classes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("extract", ENGINE / ".sources/fuel-performance/extract.py")
    ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
    ws = openpyxl.load_workbook(WORKBOOK, data_only=True)["Holding INOP Mach"]

    def block(label):
        lab = ws[label]
        for r in ws.iter_rows(min_row=lab.row, max_row=40):
            hdr = [c for c in r if lab.column <= c.column < lab.column + 11 and isinstance(c.value, (int, float))]
            if len(hdr) >= 3:
                break
        wcol, body, rr = hdr[0].column - 1, [], hdr[0].row + 1
        while isinstance(ws.cell(rr, wcol).value, (int, float)):
            body.append(rr); rr += 1
        vals = [[None] * len(hdr) for _ in body]; cls = [[None] * len(hdr) for _ in body]
        for i, b in enumerate(body):
            for j, h in enumerate(hdr):
                c = ws.cell(b, h.column)
                if isinstance(c.value, (int, float)):
                    vals[i][j] = float(c.value); cls[i][j] = ex.source_class(c, ws.title)
        return dict(flight_levels=[float(h.value) for h in hdr], weights_t=[float(ws.cell(b, wcol).value) for b in body],
                    values=vals, source_class=cls)

    return tables.Grid(block("D3")), tables.Grid(block("O3"))


class OneEngine:
    def __init__(self, tables_path=ENGINE / "data/fuel-tables.json", public_json=OUTR / "public-model.json"):
        tb = tables.Tables(tables_path, inop=True)
        self.lm, self.lf = tb.grids["lrc_inop_mach"], tb.grids["lrc_inop_ff"]
        self.hk, self.hm = holding_inop_blocks()
        self.hf = tb.grids["holding_inop_ff"]
        p = json.loads(Path(public_json).read_text())["params"]
        self.A, self.B = p[0], p[1]
        self.nodes = self._frontier_nodes()
        x = np.log([pr(f) for w, f in self.nodes if w in NODES_FIT]); y = np.log([w for w, f in self.nodes if w in NODES_FIT])
        self.n, self.lnA = np.polyfit(x, y, 1)
        self.fit_rms = float(np.std(y - (self.n * x + self.lnA)))
        self.c_lrc = float(np.mean([self.drag_ratio(fl, w) for fl in (200, 250, 280) for w in (170, 175, 180)]))

    def _frontier_nodes(self):
        out = []
        for i, w in enumerate(self.lm.ws):
            ok = [fl for j, fl in enumerate(self.lm.fls) if not np.isnan(self.lm.v[i, j]) and not np.isnan(self.lf.v[i, j])]
            out.append((float(w), float(max(ok)) if ok else None))
        return out

    def drag_rel(self, fl, w, m):
        q = 0.7 * 101325 * pr(fl) * m * m
        cl = w * 1000 * G / (q * internal.S_REF)
        return q * (self.A + self.B * cl**2)

    def m_md(self, fl, w):
        return math.sqrt(w * 1000 * G / (0.7 * 101325 * pr(fl) * internal.S_REF * math.sqrt(self.A / self.B)))

    def drag_ratio(self, fl, w):
        return self.drag_rel(fl, w, self.lm.bilinear(fl, w, True)) / self.drag_rel(fl, w, self.m_md(fl, w))

    def W_c(self, fl, k=0.0, disa=0.0):
        return math.exp(self.lnA) * pr(fl) ** self.n * (1 - k * max(disa, 0.0))

    def ceiling_fl(self, w, k=0.0, disa=0.0, mindrag=False):
        w_eff = w / self.c_lrc if mindrag else w
        return brentq(lambda fl: self.W_c(fl, k, disa) - w_eff, 100, 450)

    def driftdown(self, fl0, w, m0=0.80, kc_dd=None, k=0.0, disa=0.0, dt=1.0, rod_stop=100.0):
        kc_dd = kc_dd if kc_dd is not None else self.hk.bilinear(min(fl0, 300.0), w, True) or 220.0
        isa = tables.isa_temp_k
        h, t, V = fl0 * 30.48, 0.0, m0 * math.sqrt(1.4 * 287.05 * (isa(fl0) + disa))
        while True:  # altitude held, speed decays
            fl = h / 30.48; m = V / math.sqrt(1.4 * 287.05 * (isa(fl) + disa))
            if kcas(fl, m) <= kc_dd:
                break
            acc = G / LD * (self.drag_rel(fl, w, m) / self.drag_rel(fl, w, self.m_md(fl, w)) - self.c_lrc * self.W_c(fl, k, disa) / w)
            if acc <= 0:
                return dict(fl0=fl0, weight_t=w, disa_k=disa, kcas_dd=kc_dd, t_decel_min=None, note="holds cruise speed")
            V -= acc * dt; t += dt
        t_dec, h0, rods = t, h, []
        while t - t_dec < 3 * 3600:
            fl = h / 30.48; m = mach_from_kcas(fl, kc_dd); V = m * math.sqrt(1.4 * 287.05 * (isa(fl) + disa))
            rod = V / LD * (1 - self.c_lrc * self.W_c(fl, k, disa) / w)
            if rod * 196.85 < rod_stop:
                break
            rods.append(rod * 196.85); h -= rod * dt; t += dt
        return dict(fl0=fl0, weight_t=w, disa_k=disa, kcas_dd=kc_dd, t_decel_min=t_dec / 60,
                    decel_kt_per_min=(kcas(fl0, m0) - kc_dd) / (t_dec / 60) if t_dec > 0 else None,
                    t_descent_min=(t - t_dec) / 60, level_fl=h / 30.48,
                    mean_rod_fpm=(h0 - h) / (t - t_dec) * 196.85 if t > t_dec else 0.0, initial_rod_fpm=rods[0] if rods else 0.0,
                    level_off_mindrag_fl=self.ceiling_fl(w, k, disa, True))


def main():
    import pandas as pd
    oe = OneEngine()
    ce = []
    for w in np.arange(150, 221, 5.0):
        for d in (-10, 0, 10, 20):
            r = dict(weight_t=w, disa_k=d)
            for lab, k in K_TEMP.items():
                r[f"ceiling_lrc_inop_fl_{lab}"] = oe.ceiling_fl(w, k, d)
                r[f"level_off_mindrag_fl_{lab}"] = oe.ceiling_fl(w, k, d, True)
            ce.append(r)
    pd.DataFrame(ce).round(1).to_csv(OUTR / "one-engine-ceiling.csv", index=False)
    pd.DataFrame([dict(weight_t=w, lrc_inop_table_frontier_fl=f, at_table_top=(f == 300.0)) for w, f in oe.nodes if 140 <= w <= 230]
                 ).to_csv(OUTR / "one-engine-ceiling-table-frontier.csv", index=False)
    sp = []
    for fl in (150, 200, 250, 270, 280, 290, 300):
        for w in (172.5, 177.5, 182.5, 187.5, 197.5):  # off-node weights: interpolated, derived values
            ml = oe.lm.bilinear(fl, w, True); kh = oe.hk.bilinear(fl, w, True); mh = oe.hm.bilinear(fl, w, True)
            sp.append(dict(fl=fl, weight_t=w, lrc_inop_mach=ml, lrc_inop_kcas=kcas(fl, ml) if ml else None,
                           driftdown_kcas_holding_inop=kh, driftdown_mach=mh, above_lrc_inop_frontier=ml is None))
    pd.DataFrame(sp).round(4).to_csv(OUTR / "one-engine-speed-schedule.csv", index=False)
    dd = [oe.driftdown(fl0, w, k=k, disa=d) for fl0 in (300, 350, 370, 400) for w in (175, 178, 185, 200)
          for d, k in ((0, 0.0), (10, K_TEMP["central"]))]
    pd.DataFrame(dd).round(2).to_csv(OUTR / "one-engine-driftdown.csv", index=False)
    # local-only file in core's schema
    fls = [float(x) for x in range(70, 301, 10)]; ws_ = [float(x) for x in range(150, 251, 1)]
    grid = lambda g: [[(lambda v: None if v is None else round(v, 4))(g.bilinear(fl, w, True)) for w in ws_] for fl in fls]
    doc = dict(
        source=dict(note="LOCAL USE ONLY: derived from Ulich v5.6 FPPM grids (fppm-open, one fppm-confidential LRC INOP cell)."),
        ceiling=dict(weight_t=ws_, disa_k=[-10.0, 0.0, 10.0, 20.0],
                     lrc_inop_fl={lab: [[oe.ceiling_fl(w, k, d) for d in (-10, 0, 10, 20)] for w in ws_] for lab, k in K_TEMP.items()},
                     level_off_mindrag_fl={lab: [[oe.ceiling_fl(w, k, d, True) for d in (-10, 0, 10, 20)] for w in ws_] for lab, k in K_TEMP.items()},
                     recommended="central", table_frontier=oe.nodes,
                     model=dict(W_c="exp(lnA) * delta(FL)^n * (1 - k max(dISA, 0))", n=oe.n, lnA=oe.lnA, fit_rms=oe.fit_rms,
                                c_lrc=oe.c_lrc, k_temp=K_TEMP)),
        speed=dict(fl=fls, weight_t=ws_, lrc_inop_mach=grid(oe.lm), driftdown_kcas=grid(oe.hk), driftdown_mach=grid(oe.hm),
                   note="lrc_inop_mach: one-engine cruise (LRC INOP); driftdown_*: holding-INOP speed (min-drag proxy), "
                        "the E/O drift-down speed. null above the table frontier."),
        driftdown=dict(model="ROD = V_TAS/(L/D) * (1 - c_lrc * W_c(FL)/W) at constant drift-down KCAS; "
                             "deceleration at altitude g/(L/D) * (D(V)/D_min - c_lrc W_c/W)", l_over_d=LD, c_lrc=oe.c_lrc,
                       cases=dd))
    OUTJ.parent.mkdir(parents=True, exist_ok=True)
    OUTJ.write_text(json.dumps(doc, allow_nan=True).replace("NaN", "null"))
    print(f"n = {oe.n:.3f} (fit rms {oe.fit_rms:.4f}), c_lrc = {oe.c_lrc:.4f}; wrote {OUTJ}")


if __name__ == "__main__":
    main()
