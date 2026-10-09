"""Build the 6-DOF inputs: Mach schedules from CR-2144, a 777 parameter vector, trim and linearisation.

Schedules: the high curve is 40,000 ft (CR-2144 conditions 8, 9 and 10: M 0.70, 0.80, 0.90), extended down to
M 0.50 by condition 5 (20,000 ft). The low curve is 20,000 ft (conditions 5, 6 and 7: M 0.50, 0.65, 0.80). The
simulator blends them linearly between 20,000 and 40,000 ft and holds the low curve below 20,000 ft.
Cm0(M) is the integral of Cm_M along each curve (zero at M 0.50): the data's own transonic pitching-moment
change, nose-up to M 0.88 and tuck beyond. CL0(M) likewise integrates CR-2144's CL_M, less the part the
scheduled CL_alpha already carries, so that dCL/dM at fixed alpha matches the data at every node.
777 transfer: S and b from run.toml, cbar estimated from the planform (S/b x 1.15 for this taper); inertias
from the 747's radii of gyration at the 777's mass and size. Every multiplier in P is a fit parameter.
"""
import numpy as np
from scipy.optimize import fsolve
import aero747 as A
from sixdof import PARAMS, IDX, SCHED, deriv, isa, simulate, G, FT, KT, NM

LB, SLUG, FT2 = 0.45359237, 14.5939029, 0.09290304


def schedules():
    tab = A.table()
    hi = [tab[4], tab[7], tab[8], tab[9]]; lo = [tab[4], tab[5], tab[6]]
    def build(rows):
        mach = np.array([r["mach"] for r in rows]); vals = np.zeros((len(SCHED), len(rows)))
        for j, n in enumerate(SCHED[:-2]):
            vals[j] = [r[n] for r in rows]
        integ = lambda y: np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(mach))])
        vals[SCHED.index("Cm0M")] = integ(np.array([r["Cm_M"] for r in rows]))
        # Lift with Mach at fixed alpha: CR-2144's CL_M less what the scheduled CL_alpha already implies,
        # dCLa/dM (alpha - alpha0L) with (alpha - alpha0L) = CL_trim / CL_alpha at each node.
        cla = np.array([r["CL_alpha"] for r in rows]); dcla = np.gradient(cla, mach)
        resid = np.array([r["CL_M"] for r in rows]) - dcla * np.array([r["CL_trim"] for r in rows]) / cla
        vals[SCHED.index("CL0M")] = integ(resid)
        # Node slopes: the data's own Cm_M and residual CL_M for Cm0 and CL0; neighbouring-node
        # differences for the rest.
        slopes = np.array([np.gradient(v, mach) for v in vals])
        slopes[SCHED.index("Cm0M")] = [r["Cm_M"] for r in rows]
        slopes[SCHED.index("CL0M")] = resid
        return mach, vals, slopes
    mh, vh, sh = build(hi); ml, vl, sl = build(lo)
    return mh, vh, sh, ml, vl, sl


def inertia_777(mass_kg, b=60.93, length=63.7):
    """747 radii of gyration (CR-2144 Table IX-3, conditions 3-10) carried to the 777's mass and size."""
    m747 = A.W_LB[9] * LB; b747 = A.B_FT * FT; l747 = 70.66
    I747 = np.array([A.IX[9], A.IY[9], A.IZ[9], A.IXZ[9]]) * SLUG * FT2
    k = I747 / m747
    sx, sy = (b / b747) ** 2, (length / l747) ** 2
    return mass_kg * k * np.array([sx, sy, 0.5 * (sx + sy), 0.5 * (sx + sy)])


def default_params(**over):
    P = dict.fromkeys(PARAMS, 0.0)
    mass = over.get("mass", 175000.0)
    Ix, Iy, Iz, Ixz = inertia_777(mass)
    k_ind = 1.0 / (np.pi * 60.93 ** 2 / 427.8 * 0.80)
    P.update(mass=mass, Ix=Ix, Iy=Iy, Iz=Iz, Ixz=Ixz, S=427.8, b=60.93, c=427.8 / 60.93 * 1.15, y_eng=9.6,
             T0=415450.0, CD0=(0.5 / 21.1) ** 2 / k_ind, k_ind=k_ind, kw=20.0, Mcc=0.87, dCD_wm=0.00075,
             dCD_rat=0.00035, CLmax=1.30, alpha0L=np.radians(-2.5), alpha_ref=np.radians(2.0),
             m_Clb=1.0, m_Cnb=1.0, m_Clr=1.0, m_Cnr=1.0, m_Clp=1.0, m_Cnp=1.0, m_Cma=1.0, m_Cmq=1.0,
             tuck_x=0.0, Cm_bias=0.0, t1=1e9, t_loss=1e9, t2=1e9, law=1, bap=0, u_stiff=0.8, u_lag=0.8,
             Vref_floor_eas=195.0, ref_tau=60.0, da_offset=0.0, dr_offset=0.0, thr_loss=1.0,
             alt_hold_m=12192.0, eas_floor=175.0 * KT, psi_cmd=180.0, wind_from=246.0, wind_sl=23.5,
             wind_slope=0.79 / 1000.0 / FT, wind_top=25000.0 * FT, dt=0.05, t_end=3000.0, ap_tac=1.0,
             yd_gain=1.5, cmd_lag=1.0, mct=0.8)
    P.update(over)
    return np.array([P[n] for n in PARAMS], dtype=float)


def state(h_m, tas, psi_deg, alpha, P):
    """Level wings-level state: air-relative velocity TAS along heading psi; ground velocity adds the wind."""
    from sixdof import wind_ned
    th = alpha; psi = np.radians(psi_deg)
    cr, sr = np.cos(psi / 2), np.sin(psi / 2); ct, st = np.cos(th / 2), np.sin(th / 2)
    q = np.array([cr * ct, -sr * st, cr * st, sr * ct])  # 3-2-1 with roll 0: yaw psi then pitch theta
    q /= np.linalg.norm(q)
    wn, we = wind_ned(h_m, P)
    from sixdof import qrot
    R = qrot(q)
    vb_air = np.array([tas * np.cos(alpha), 0.0, tas * np.sin(alpha)])
    vb = vb_air + R.T @ np.array([wn, we, 0.0])
    return np.concatenate([[0.0, 0.0, -h_m], vb, q, [0.0, 0.0, 0.0]])


def trim(h_m, tas, psi_deg, P, sched):
    """Solve alpha, elevator and symmetric thrust per engine for steady level flight."""
    mh, vh, sh, ml, vl, sl = sched
    out = np.zeros(8)
    def f(z):
        a, de, T = z
        x = state(h_m, tas, psi_deg, a, P)
        ctl = np.array([de, 0.0, 0.0, T * 1e5, T * 1e5, 0.0])
        d = deriv(0.0, x, ctl, P, mh, vh, sh, ml, vl, sl, out)
        return [d[3], d[5], d[11] * 100]
    z = fsolve(f, [np.radians(2.5), 0.0, 0.5], full_output=True)
    a, de, T = z[0]
    return a, de, T * 1e5, z[2]


def linearise(x0, ctl, P, sched, eps=1e-5):
    mh, vh, sh, ml, vl, sl = sched; out = np.zeros(8)
    f0 = deriv(0.0, x0, ctl, P, mh, vh, sh, ml, vl, sl, out)
    J = np.zeros((13, 13))
    for i in range(13):
        dx = np.zeros(13); dx[i] = eps * max(1.0, abs(x0[i]))
        J[:, i] = (deriv(0.0, x0 + dx, ctl, P, mh, vh, sh, ml, vl, sl, out) - deriv(0.0, x0 - dx, ctl, P, mh, vh, sh, ml, vl, sl, out)) / (2 * dx[i])
    return J
