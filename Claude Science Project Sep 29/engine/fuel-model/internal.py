"""Internal fuel model for 9M-MRO: all table data, corrected lookup, temperature term, calibration.

Fuel session, 10 Oct 2026 (core request 16 C; brief threads/master-prompts/fuel-model.md).
LOCAL USE ONLY: it prices from data/fuel-tables.json, which includes FPPM-confidential cells.

    FF(FL, W, M, dISA) = kappa * D_hi(M) * tau(dISA, M) * FF_tab(FL, W, M)      [kg/h, both engines]

  FF_tab  tables.Tables(fixed=True, low_rule="physical"): Ulich v5.6 grids (holding / 1.05, MRC,
          CI 52, LRC, M0.84), bilinear in FL and W with the zero-weight-corner fix (F3), the
          a M^2 + b / M^2 law between bracketing schedules, the U-shaped fit kept below the slowest
          schedule when it is well posed (a, b > 0) and clamped at that schedule otherwise (F4).
  D_hi    1 + C_HI * max(0, M - 0.84) * (CL / 0.35)^Q_HI: compressibility drag rise the tables do not
          carry above M0.84, growing with lift coefficient CL = W g / (0.7 p M^2 S), S = 427.8 m^2.
          Fitted to the five Boeing items flown above M0.84 at FL >= 250 (provisional: residual
          s.d. about 2 %, 2 parameters on 5 points). Zero at and below M0.84.
  tau     1 + 0.003 * dISA * (1 + 0.2 M^2): the FPPM rule of +3 % per +10 C of TAT above standard
          (footnote recorded by extract.py), written in ISA deviation of SAT. At M0.82 this is
          0.34 %/C. Standard day: tau = 1.
  kappa   calibration MULTIPLIER (Boeing / model; > 1 burns more than the tables). Fitted by
          calibrate.py; see results/fuel-model/internal-calibration.md. Defined the right way
          round (audit F1): it multiplies flow and is never divided.
"""

import math

import tables

C_HI_DEFAULT = 0.0
Q_HI_DEFAULT = 0.0
CL_REF = 0.35
M_DD = 0.84
S_REF = 427.8
FLAG_BITS = {"extrap_high": 1, "extrap_low": 2, "below_tables": 4, "above_ceiling": 8,
             "single_schedule": 16, "fit_fallback": 32, "floor_clamped": 64}


def tau_fppm(disa, mach):
    return 1.0 + 0.003 * disa * (1.0 + 0.2 * mach * mach)


def tau_none(disa, mach):
    return 1.0


class Internal:
    def __init__(self, tables_path, kappa=1.0, c_hi=C_HI_DEFAULT, q_hi=Q_HI_DEFAULT, temp=tau_fppm, inop=False,
                 low_rule="physical"):
        self.tb = tables.Tables(tables_path, inop=inop, low_rule=low_rule)
        self.kappa, self.c_hi, self.q_hi, self.temp = kappa, c_hi, q_hi, temp

    def ff_shape(self, fl, w_t, mach):
        """Standard-day flow before kappa (tables x drag rise), and flags."""
        f, flags = self.tb.ff_isa(fl, w_t, mach, fixed=True)
        if f is None:
            return None, flags
        return f * drag_rise(fl, w_t, mach, self.c_hi, self.q_hi), flags

    def ff(self, fl, w_t, mach, disa=0.0):
        f, flags = self.ff_shape(fl, w_t, mach)
        if f is None:
            return None, flags
        return self.kappa * self.temp(disa, mach) * f, flags


def pressure_ratio(fl):
    h = fl * 100 * 0.3048
    return (1 - 2.25577e-5 * h) ** 5.25588 if h < 11000 else 0.22336 * math.exp(-(h - 11000) / 6341.62)


def lift_coefficient(fl, w_t, mach):
    return w_t * 1000 * 9.80665 / (0.7 * 101325 * pressure_ratio(fl) * mach * mach * S_REF)


def drag_rise(fl, w_t, mach, c, q):
    if mach <= M_DD or c == 0.0:
        return 1.0
    return 1.0 + c * (mach - M_DD) * (lift_coefficient(fl, w_t, mach) / CL_REF) ** q


def flag_mask(flags):
    return sum(b for k, b in FLAG_BITS.items() if flags.get(k))


class GridModel:
    """The model of record (internal-v1): trilinear interpolation of the dense standard-day grid.

    The table lookup extrapolates the drag law from interpolated schedule points, which is not
    linear in FL; between FL nodes in the extrapolated regions it can differ from the grid by up
    to ~10 %. Core interpolates the grid, so the calibration is computed on the grid too.
    Outside the grid: FL is clamped to [15, 430] (flagged below_tables / above_ceiling as the
    nodes are), weight and Mach are clamped to the grid edges and flagged `outside_grid`.
    """

    def __init__(self, doc_grid, kappa=1.0, temp=tau_fppm):
        import numpy as np
        self.np = np
        self.fls = np.array(doc_grid["fl_nodes"], float)
        self.ws = np.array(doc_grid["weight_t"], float)
        self.ms = np.array(doc_grid["mach"], float)
        self.flow = np.array([[[np.nan if v is None else v for v in r] for r in p] for p in doc_grid["flow_kg_h"]], float)
        self.flags = np.array(doc_grid["flags"], dtype=np.int64)
        self.kappa, self.temp = kappa, temp

    def _idx(self, nodes, x):
        np = self.np
        xc = min(max(x, nodes[0]), nodes[-1])
        k = int(np.clip(np.searchsorted(nodes, xc, side="right") - 1, 0, len(nodes) - 2))
        return k, (xc - nodes[k]) / (nodes[k + 1] - nodes[k]), xc != x

    def ff_shape(self, fl, w_t, mach):
        (i, x, o1), (j, y, o2), (k, z, o3) = self._idx(self.fls, fl), self._idx(self.ws, w_t), self._idx(self.ms, mach)
        acc, mask, wsum = 0.0, 0, 0.0
        for di, wx in ((0, 1 - x), (1, x)):
            for dj, wy in ((0, 1 - y), (1, y)):
                for dk, wz in ((0, 1 - z), (1, z)):
                    wt = wx * wy * wz
                    if wt == 0.0:
                        continue
                    v = self.flow[i + di, j + dj, k + dk]
                    if v != v:  # NaN corner: unpriceable
                        return None, {"unpriceable": True}
                    acc += wt * v
                    mask |= int(self.flags[i + di, j + dj, k + dk])
        flags = {name: True for name, b in FLAG_BITS.items() if mask & b}
        if o2 or o3:
            flags["outside_grid"] = True
        return acc, flags

    def ff(self, fl, w_t, mach, disa=0.0):
        f, flags = self.ff_shape(fl, w_t, mach)
        if f is None:
            return None, flags
        return self.kappa * self.temp(disa, mach) * f, flags
