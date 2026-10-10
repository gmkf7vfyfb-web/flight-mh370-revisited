#!/usr/bin/env python3
"""Public parametric fuel-flow law for 9M-MRO (fuel session, 10 Oct 2026; delivery 3).

Fitted to PUBLIC numbers only: SIR App. 1.6E Table 3 (5 segment burns, p. 5) and Table 4 (22 endurances,
p. 6), standard day (p. 3), from the ACARS state at 17:06:43 (p. 1, p. 4). No FPPM cell, no licensed
performance database, no Ulich value enters the fit.

    FF = TSFC * D                                                 kg/h, both engines
    TSFC = c_T * (1 + b_M * M) * theta^a                          theta = T / 288.15 (actual SAT)
    D    = q S [ C_D0 + K C_L^2 + C_w max(0, M - M_crit)^4 ]       q = 0.7 p M^2, C_L = W g / (q S)
    M_crit = m0 - (C_L - 0.5) / (10 cos^3 sweep)                  (Korn's C_L dependence, sweep 31.6 deg)

  * Thrust = drag in level flight; C_D0 + K C_L^2 is the parabolic polar; the 20 (M - M_crit)^4 wave-drag
    term is Lock's empirical law; TSFC rising linearly with Mach and with a power of the temperature ratio
    is the standard high-bypass turbofan form. S = 427.8 m^2 (777 reference wing area).
  * Only the products c_T*C_D0 and c_T*K are identifiable from fuel data, so the fit parameters are
    A = c_T*C_D0, B = c_T*K, Cw = c_T*C_w, b_M, a, m0 (Lock's law has C_w = 20).
  * Temperature: at fixed Mach and pressure altitude, drag is unchanged; corrected fuel flow
    W_f / (delta sqrt(theta)) is then constant, so FF scales as (T / T_ISA)^0.5 (0.23 %/C at FL350).
    The standard-day altitude lapse of TSFC is a separate fitted exponent a on T_ISA / 288.15.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import optimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sources  # noqa: E402
import tables  # noqa: E402

G0, P0, S_REF = 9.80665, 101325.0, 427.8
A_TEMP = 0.5
NAMES = ["A", "B", "Cw", "b_M", "a", "m0"]
SWEEP_DEG = 31.6  # 777 quarter-chord sweep (public)
M1_KORN = 1 / (10 * math.cos(math.radians(SWEEP_DEG)) ** 3)  # Korn: dM_dd/dC_L = -1 / (10 cos^3 sweep)


def pressure_ratio(fl):
    h = np.asarray(fl, float) * 30.48
    return np.where(h < 11000, (1 - 2.25577e-5 * h) ** 5.25588, 0.22336 * np.exp(-(h - 11000) / 6341.62))


def isa_k(fl):
    h = np.asarray(fl, float) * 30.48
    return np.where(h < 11000, 288.15 - 0.0065 * h, 216.65)


def ff(p, fl, w_t, mach, disa=0.0):
    """Both-engine flow, kg/h. p = (A, B, Cw, b_M, a, m0) with A = 1e5 c_T C_D0, B = 1e5 c_T K,
    Cw = 1e5 c_T * 20 (Lock's wave-drag coefficient times TSFC scale); M_crit = m0 - M1_KORN (C_L - 0.5)."""
    A, B, Cw, bM, a, m0 = p
    q = 0.7 * P0 * pressure_ratio(fl) * mach**2
    cl = w_t * 1000 * G0 / (q * S_REF)
    wave = np.maximum(0.0, mach - (m0 - M1_KORN * (cl - 0.5))) ** 4
    t_isa = isa_k(fl)
    # altitude lapse of TSFC on the standard day (fitted exponent a), times the corrected-parameter
    # temperature scaling at fixed Mach and pressure altitude: W_f / (delta sqrt(theta)) constant at fixed
    # F / delta, so FF ~ (T / T_ISA)^A_TEMP with A_TEMP = 0.5 (dimensional analysis; not fitted, Boeing's
    # numbers are all standard day)
    return (1e-5 * (A + B * cl**2 + Cw * wave) * q * S_REF * (1 + bM * mach) * (t_isa / 288.15) ** a
            * ((t_isa + disa) / t_isa) ** A_TEMP)


def items(sir):
    """Constant-state Boeing items as arrays for vectorised integration."""
    zfw = sir["zfw_kg"]
    rows, start = [], sir["fuel0_kg"]
    for i, s in enumerate(sir["seg"], 1):
        target = start - s["end_lb"] * sources.LB
        q = 0.001 if i in (2, 5) else 0.01
        rows.append(dict(kind="burn", item=f"T3 seg {i}", fl=s["fl"], mach=s["mach"], fuel0=start, hours=s["hours"], obs=target,
                         se=q / math.sqrt(12) / s["hours"]))
        start = s["end_lb"] * sources.LB
    for e in sir["end"]:
        qq = 0.01 if abs(e["hours"] * 10 - round(e["hours"] * 10)) > 1e-9 else 0.1
        rows.append(dict(kind="endurance", item=f"T4 FL{e['fl']:.0f} {e['tas']:.0f} kt", fl=e["fl"], mach=tables.isa_mach(e["fl"], e["tas"]),
                         fuel0=sir["arc1_kg"], hours=e["hours"], obs=e["hours"], se=qq / math.sqrt(12) / e["hours"]))
    return rows, zfw


def simulate(p, rows, zfw, dt_h=1 / 60, disa=0.0):
    """Model burn (T3) or endurance (T4) for every item, vectorised; mid-step weight."""
    n = len(rows)
    fl = np.array([r["fl"] for r in rows]); m = np.array([r["mach"] for r in rows])
    fuel = np.array([r["fuel0"] for r in rows], float)
    burn_h = np.array([r["hours"] if r["kind"] == "burn" else np.inf for r in rows])
    t = np.zeros(n); done = np.zeros(n, bool); out = np.full(n, np.nan); fuel0 = fuel.copy()
    for _ in range(int(12 / dt_h)):
        act = ~done
        if not act.any():
            break
        step = np.where(np.isfinite(burn_h), np.minimum(dt_h, burn_h - t), dt_h)
        f0 = ff(p, fl, (zfw + fuel) / 1000, m, disa)
        f = ff(p, fl, (zfw + fuel - 0.5 * f0 * step) / 1000, m, disa)
        b = f * step
        endur = (~np.isfinite(burn_h)) & act & (b >= fuel)
        out[endur] = t[endur] + step[endur] * fuel[endur] / b[endur]
        done |= endur
        upd = act & ~endur
        fuel[upd] -= b[upd]; t[upd] += step[upd]
        fin = np.isfinite(burn_h) & upd & (t >= burn_h - 1e-12)
        out[fin] = fuel0[fin] - fuel[fin]
        done |= fin
    return out


def implied_kappa(p, rows, zfw):
    sim = simulate(p, rows, zfw)
    obs = np.array([r["obs"] for r in rows])
    return np.where([r["kind"] == "burn" for r in rows], obs / sim, sim / obs)


def fit(rows, zfw, p0=(1.0, 3.0, 1000.0, 0.5, 0.6, 0.78), sel=None, sigma_model=0.012):
    sel = np.ones(len(rows), bool) if sel is None else sel
    se = np.array([r["se"] for r in rows])

    def resid(p):
        k = implied_kappa(p, rows, zfw)
        return (np.log(k) / np.sqrt(se**2 + sigma_model**2))[sel]

    lo = [0.01, 0.01, 0.0, -1.0, 0.0, 0.6]; hi = [20, 100, 1e6, 5.0, 1.5, 0.95]
    r = optimize.least_squares(resid, p0, bounds=(lo, hi), x_scale="jac")
    J = r.jac; cov = np.linalg.pinv(J.T @ J)
    k = implied_kappa(r.x, rows, zfw)
    return r.x, cov, k
