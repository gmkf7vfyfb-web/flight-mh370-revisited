"""Six-degree-of-freedom rigid-body simulator for the end-of-flight stage (reference model, not the sweep).

Frame: flat Earth, NED, which is adequate over 200 NM. Outputs are in Boeing's export form: X east and Y north in NM, altitude in ft, 1 Hz.
Rigid body: quaternion attitude; body rates with the Ixz product of inertia; gravity rotated into body axes.
Air: ISA (troposphere and tropopause); wind from a direction with speed linear in altitude, capped above a top
height (the simulator's own wind is fitted from the traces; see wind_fit.py).
Aerodynamics (all coefficients non-dimensional, body axes for moments):
  CL = CLa(M) (alpha - alpha0L) + CLq qhat + CLde de, saturated at CLmax
  CD = CD0 + k CL^2 + kw (M - Mcc)^4 [M > Mcc] + dCD(windmilling engines, RAT)   (module polar, Boeing glide)
  Cm = Cm0(M) + Cma(M) (alpha - alpha_ref) + Cmq qhat + Cmad adothat + Cmde de
       with Cm0(M) the integral of CR-2144's Cm_M (the data's own Mach tuck) and, above M_x = 0.90, an
       extrapolated tuck slope (fitted)
  CY = CYb beta + CYdr dr;  Cl = Clb beta + Clp phat + Clr rhat + Clda da + Cldr dr;  Cn likewise
  Derivatives are scheduled in Mach from CR-2144 (40,000 ft and 20,000 ft curves, blended in altitude), held
  beyond their last node, and scaled by fitted multipliers (the transfer to the 777 is not assumed).
Thrust: each engine along body x at y = +/- y_eng; maximum continuous T = T0 * mct * sigma * (1 - 0.25 M) (mct fitted); flame-out at t1 (right) and t2 (left).
Control (law codes):
  0 autopilot (altitude hold, then speed floor, i.e. driftdown), heading hold, autothrottle, rudder compensation of
    thrust asymmetry, yaw damper;
  1 normal-like after loss: pitch holds a load factor with speed stability about a reference speed sensed through a lag (C*U-like), turn compensation to 30 deg, optional bank-angle
    protection (roll back to 30 deg above 35 deg), yaw damper, wheel neutral (bank otherwise free);
  2 stick-fixed after loss: elevator frozen at its trim at the loss; ailerons and rudder at fitted trim offsets
    (neutral wheel and pedals); no damper, no protection.
  Rudder compensation of thrust asymmetry is always active under the autopilot, and after the loss only when
  the case's ap_tac flag is set (its survival depends on the unknown electrical configuration).
"""
import math
import numpy as np
try:
    from numba import njit
except ImportError:  # pure-Python fallback, slow
    def njit(*a, **k):
        return (lambda f: f) if not (a and callable(a[0])) else a[0]

G = 9.80665; FT = 0.3048; NM = 1852.0; KT = NM / 3600.0; R_AIR = 287.05287
# Parameter vector layout (P). The names are documented in PARAMS below.
PARAMS = ["mass", "Ix", "Iy", "Iz", "Ixz", "S", "b", "c", "y_eng", "T0",
          "CD0", "k_ind", "kw", "Mcc", "dCD_wm", "dCD_rat", "CLmax", "alpha0L", "alpha_ref",
          "m_Clb", "m_Cnb", "m_Clr", "m_Cnr", "m_Clp", "m_Cnp", "m_Cma", "m_Cmq", "tuck_x", "Cm_bias",
          "t1", "t_loss", "t2", "law", "bap", "u_stiff", "u_lag", "Vref_floor_eas", "ref_tau",
          "da_offset", "dr_offset", "thr_loss", "alt_hold_m", "eas_floor", "psi_cmd",
          "wind_from", "wind_sl", "wind_slope", "wind_top", "dt", "t_end", "ap_tac", "yd_gain", "cmd_lag", "mct"]
IDX = {n: i for i, n in enumerate(PARAMS)}


@njit(cache=True)
def isa(h):
    if h < 11000.0:
        T = 288.15 - 0.0065 * h; p = 101325.0 * (T / 288.15) ** 5.25588
    else:
        T = 216.65; p = 22632.06 * math.exp(-G * (h - 11000.0) / (R_AIR * 216.65))
    return p / (R_AIR * T), math.sqrt(1.4 * R_AIR * T)


@njit(cache=True)
def interp(x, xs, ys, ds, extrapolate):
    """Cubic Hermite through (xs, ys) with node slopes ds. Beyond the ends: continue at the end slope if
    extrapolate, else hold the end value."""
    n = xs.shape[0]
    if x <= xs[0]:
        return ys[0] + (ds[0] * (x - xs[0]) if extrapolate else 0.0)
    if x >= xs[n - 1]:
        return ys[n - 1] + (ds[n - 1] * (x - xs[n - 1]) if extrapolate else 0.0)
    for i in range(n - 1):
        if x <= xs[i + 1]:
            hh = xs[i + 1] - xs[i]; t = (x - xs[i]) / hh
            h00 = 2 * t ** 3 - 3 * t ** 2 + 1; h10 = t ** 3 - 2 * t ** 2 + t
            h01 = -2 * t ** 3 + 3 * t ** 2; h11 = t ** 3 - t ** 2
            return h00 * ys[i] + h10 * hh * ds[i] + h01 * ys[i + 1] + h11 * hh * ds[i + 1]
    return ys[n - 1]


# schedule rows (each a Mach curve at high and low altitude): order fixed here
SCHED = ["CL_alpha", "Cm_alpha", "Cm_q", "Cm_alphadot", "CL_q", "Cm_de", "CL_de", "Cy_beta", "Cy_dr", "Cl_beta",
         "Cn_beta", "Cl_p", "Cn_p", "Cl_r", "Cn_r", "Cl_da", "Cn_da", "Cl_dr", "Cn_dr", "Cm0M", "CL0M"]
SI = {n: i for i, n in enumerate(SCHED)}


@njit(cache=True)
def coeff(j, M, h, mh, vh, sh, ml, vl, sl):
    """Scheduled coefficient j at Mach M and altitude h: blend of the high (40 kft) and low (20 kft) curves.
    Rows 19 (Cm0) and 20 (CL0) continue at the data's end slopes beyond the table; the others are held."""
    ex = j >= 19
    ch = interp(M, mh, vh[j], sh[j], ex); cl = interp(M, ml, vl[j], sl[j], ex)
    f = min(max((h - 6096.0) / (12192.0 - 6096.0), 0.0), 1.0)
    return cl + f * (ch - cl)


@njit(cache=True)
def qrot(q):
    """Body-to-NED rotation matrix from a unit quaternion (w, x, y, z)."""
    w, x, y, z = q[0], q[1], q[2], q[3]
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


@njit(cache=True)
def euler(q):
    w, x, y, z = q[0], q[1], q[2], q[3]
    phi = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    th = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    psi = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return phi, th, psi


@njit(cache=True)
def wind_ned(h, P):
    sp = (P[IDX_WSL] + P[IDX_WSLOPE] * min(h, P[IDX_WTOP])) * KT
    d = math.radians(P[IDX_WFROM]) + math.pi  # blowing towards
    return sp * math.cos(d), sp * math.sin(d)


IDX_WSL, IDX_WSLOPE, IDX_WTOP, IDX_WFROM = IDX["wind_sl"], IDX["wind_slope"], IDX["wind_top"], IDX["wind_from"]


@njit(cache=True)
def deriv(t, x, ctl, P, mh, vh, sh, ml, vl, sl, out):
    """State x: [n, e, d, u, v, w, q0, q1, q2, q3, p, q, r]; ctl: [de, da, dr, T_right, T_left, adot].
    Returns dx; out receives diagnostics [alpha, beta, V, M, eas, nz, h, CL]."""
    n, e, d, u, v, w = x[0], x[1], x[2], x[3], x[4], x[5]
    qt = x[6:10]; p, q, r = x[10], x[11], x[12]
    h = -d; rho, a = isa(max(h, 0.0))
    Rm = qrot(qt)
    wn, we = wind_ned(h, P)
    wb = Rm.T @ np.array([wn, we, 0.0])
    ua, va, wa = u - wb[0], v - wb[1], w - wb[2]
    V = math.sqrt(ua * ua + va * va + wa * wa); V = max(V, 30.0)
    alpha = math.atan2(wa, ua); beta = math.asin(max(-1.0, min(1.0, va / V)))
    M = V / a; qd = 0.5 * rho * V * V
    S, b, c = P[5], P[6], P[7]
    phat, qhat, rhat = p * b / (2 * V), q * c / (2 * V), r * b / (2 * V)
    adhat = ctl[5] * c / (2 * V)
    de, da, dr = ctl[0], ctl[1], ctl[2]
    CLa = coeff(0, M, h, mh, vh, sh, ml, vl, sl)
    CL = (CLa * (alpha - P[17]) + coeff(20, M, h, mh, vh, sh, ml, vl, sl)
          + coeff(4, M, h, mh, vh, sh, ml, vl, sl) * qhat + coeff(6, M, h, mh, vh, sh, ml, vl, sl) * de)
    CL = max(min(CL, P[16]), -0.8 * P[16])
    nwm = (1.0 if t >= P[29] else 0.0) + (1.0 if t >= P[31] else 0.0)
    CD = P[10] + P[11] * CL * CL + nwm * P[14] + (P[15] if t >= P[31] else 0.0)
    if M > P[13]:
        CD += P[12] * (M - P[13]) ** 4
    Mx = 0.90
    Cm0 = coeff(19, M, h, mh, vh, sh, ml, vl, sl)  # data slope continued past the last node (model.schedules)
    if M > Mx:  # beyond the table: an ADDITIONAL extrapolated tuck slope, fitted (labelled extrapolated)
        Cm0 -= P[27] * (M - Mx)
    Cm = (Cm0 + P[28] + P[25] * coeff(1, M, h, mh, vh, sh, ml, vl, sl) * (alpha - P[18])
          + P[26] * coeff(2, M, h, mh, vh, sh, ml, vl, sl) * qhat + coeff(3, M, h, mh, vh, sh, ml, vl, sl) * adhat
          + coeff(5, M, h, mh, vh, sh, ml, vl, sl) * de)
    CY = coeff(7, M, h, mh, vh, sh, ml, vl, sl) * beta + coeff(8, M, h, mh, vh, sh, ml, vl, sl) * dr
    Cl = (P[19] * coeff(9, M, h, mh, vh, sh, ml, vl, sl) * beta + P[23] * coeff(11, M, h, mh, vh, sh, ml, vl, sl) * phat
          + P[21] * coeff(13, M, h, mh, vh, sh, ml, vl, sl) * rhat + coeff(15, M, h, mh, vh, sh, ml, vl, sl) * da
          + coeff(17, M, h, mh, vh, sh, ml, vl, sl) * dr)
    Cn = (P[20] * coeff(10, M, h, mh, vh, sh, ml, vl, sl) * beta + P[24] * coeff(12, M, h, mh, vh, sh, ml, vl, sl) * phat
          + P[22] * coeff(14, M, h, mh, vh, sh, ml, vl, sl) * rhat + coeff(16, M, h, mh, vh, sh, ml, vl, sl) * da
          + coeff(18, M, h, mh, vh, sh, ml, vl, sl) * dr)
    L, D = qd * S * CL, qd * S * CD
    ca, sa = math.cos(alpha), math.sin(alpha)
    Tr, Tl = ctl[3], ctl[4]
    Fx = -D * ca + L * sa + Tr + Tl
    Fz = -D * sa - L * ca
    Fy = qd * S * CY
    mass = P[0]
    g_b = Rm.T @ np.array([0.0, 0.0, G])
    du = Fx / mass + g_b[0] + r * v - q * w
    dv = Fy / mass + g_b[1] + p * w - r * u
    dw = Fz / mass + g_b[2] + q * u - p * v
    Lm = qd * S * b * Cl
    Mm = qd * S * c * Cm
    Nm = qd * S * b * Cn + (Tl - Tr) * P[8]
    Ix, Iy, Iz, Ixz = P[1], P[2], P[3], P[4]
    Gm = Ix * Iz - Ixz * Ixz
    dp = (Iz * (Lm + Ixz * p * q - (Iz - Iy) * q * r) + Ixz * (Nm - (Iy - Ix) * p * q - Ixz * q * r)) / Gm
    dq = (Mm - (Ix - Iz) * p * r - Ixz * (p * p - r * r)) / Iy
    dr_ = (Ixz * (Lm + Ixz * p * q - (Iz - Iy) * q * r) + Ix * (Nm - (Iy - Ix) * p * q - Ixz * q * r)) / Gm
    vel = Rm @ np.array([u, v, w])
    w0, x1, y1, z1 = qt[0], qt[1], qt[2], qt[3]
    dq0 = 0.5 * (-x1 * p - y1 * q - z1 * r); dq1 = 0.5 * (w0 * p + y1 * r - z1 * q)
    dq2 = 0.5 * (w0 * q - x1 * r + z1 * p); dq3 = 0.5 * (w0 * r + x1 * q - y1 * p)
    out[0] = alpha; out[1] = beta; out[2] = V; out[3] = M; out[4] = V * math.sqrt(rho / 1.225)
    out[5] = -Fz / (mass * G); out[6] = h; out[7] = CL
    res = np.empty(13)
    res[0] = vel[0]; res[1] = vel[1]; res[2] = vel[2]
    res[3] = du; res[4] = dv; res[5] = dw
    res[6] = dq0; res[7] = dq1; res[8] = dq2; res[9] = dq3
    res[10] = dp; res[11] = dq; res[12] = dr_
    return res


# ---------------------------------------------------------------- control and integration
@njit(cache=True)
def thrust_avail(h, M, T0, mct):
    """Maximum continuous thrust per engine: lapse with density ratio (cruise-altitude form) and Mach,
    times a fitted maximum-continuous factor."""
    rho, a = isa(max(h, 0.0))
    return T0 * mct * (rho / 1.225) * (1.0 - 0.25 * M)


@njit(cache=True)
def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


@njit(cache=True)
def simulate(P, mh, vh, sh, ml, vl, sl, x0, de0, T0each):
    """Fly from x0 (trimmed, both engines at T0each) to the sea or t_end. Returns a 1 Hz record:
    columns t, X_east_nm, Y_north_nm, alt_ft, bank_deg, mach, eas_kt, nz, alpha_deg, de, theta_deg, heading_deg."""
    dt = P[IDX_DT]; t_end = P[IDX_TEND]; nrec = int(t_end) + 2
    rec = np.full((nrec, 12), np.nan)
    x = x0.copy(); out = np.zeros(8)
    law0 = 0; law = int(P[IDX_LAW])
    deI = de0; Tc = T0each; Tr, Tl = T0each, T0each
    nz_prev = 1.0; alpha_prev = 0.0; adot = 0.0
    V_s = 0.0; V_ref = 0.0; r_hp = 0.0; r_lp = 0.0; V_at = 0.0
    frozen = np.zeros(3); frozen_set = False
    t = 0.0; k = 0; nextrec = 0.0
    ctl = np.zeros(6)
    h_cmd = P[IDX_ALTH]
    while t <= t_end:
        # air data at step start
        d0 = deriv(t, x, ctl, P, mh, vh, sh, ml, vl, sl, out)
        alpha, beta, V, M, eas, nz, h = out[0], out[1], out[2], out[3], out[4], out[5], out[6]
        if h <= 0.0:
            break
        adot = (alpha - alpha_prev) / dt if t > 0 else 0.0; alpha_prev = alpha
        phi, th, psi = euler(x[6:10])
        p, q, r = x[10], x[11], x[12]
        hdot = -d0[2]
        gam = math.asin(max(-1.0, min(1.0, hdot / V)))
        if V_s == 0.0:
            V_s = eas; V_ref = eas; V_at = eas
        V_s += dt / max(P[IDX_ULAG], 1e-3) * (eas - V_s)
        r_lp += dt / 3.0 * (r - r_lp); r_hp = r - r_lp  # washout: the damper must not fight a steady turn
        active = law0 if t < P[IDX_TLOSS] else law
        # engines: right flames out at t1, left at t2; thrust follows command with a lag, decays at flame-out
        Tav = thrust_avail(h, M, P[IDX_T0], P[IDX_MCT])
        if active == 0:
            Tc = min(max(Tc + dt * 2000.0 * (V_at - eas), 0.03 * Tav), Tav)  # autothrottle: hold cruise EAS
        elif not frozen_set:
            Tc = Tc * P[IDX_THRLOSS]
        Tr = (Tr + dt / 5.0 * ((min(Tc, Tav) if t < P[IDX_T1] else 0.0) - Tr))
        Tl = (Tl + dt / 5.0 * ((min(Tc, Tav) if t < P[IDX_T2] else 0.0) - Tl))
        qd = 0.5 * isa(max(h, 0.0))[0] * V * V
        cndr = coeff(18, M, h, mh, vh, sh, ml, vl, sl)
        tac_raw = -((Tl - Tr) * P[IDX_YENG]) / (qd * P[5] * P[6] * cndr)
        tac = tac_raw if (active == 0 or P[IDX_TAC] > 0) else 0.0  # always under the autopilot; after the loss only if flagged
        if active == 0:
            # autopilot: altitude hold, then speed floor (driftdown); heading hold; TAC; yaw damper
            if eas > P[IDX_EASFLOOR] or V_ref == 0.0:
                gc = max(min(0.002 * (h_cmd - h), math.radians(2.0)), math.radians(-2.0))
            else:
                gc = max(min(-0.01 * (P[IDX_EASFLOOR] - eas), math.radians(1.0)), math.radians(-6.0))
            nzc = math.cos(gc) / math.cos(phi) + V / G * 0.15 * (gc - gam)
            err = nzc - nz
            deI += dt * (-0.05 * err)
            de = deI - 0.15 * err + 1.0 * q
            phic = max(min(1.5 * wrap(math.radians(P[IDX_PSI]) - psi), math.radians(25.0)), math.radians(-25.0))
            da = 1.2 * (phic - phi) - 1.0 * p
            dr = tac + P[IDX_YDG] * r_hp
        elif active == 1:
            if not frozen_set:
                V_ref = V_s; frozen_set = True
            V_ref += dt / max(P[IDX_REFTAU], 1.0) * (P[IDX_VREFFL] * KT - V_ref) if P[IDX_REFTAU] > 0 else 0.0
            ph = min(abs(phi), math.radians(30.0))
            nzc = math.cos(gam) / math.cos(ph) + P[IDX_USTIFF] * (V_s - V_ref) / V
            err = nzc - nz
            deI += dt * (-0.05 * err)
            de = deI - 0.15 * err + 1.0 * q
            da = P[IDX_DAOFF]
            if P[IDX_BAP] > 0 and abs(phi) > math.radians(35.0):
                da += -1.5 * (abs(phi) - math.radians(30.0)) * (1.0 if phi > 0 else -1.0) - 0.5 * p
            dr = tac + P[IDX_DROFF] + P[IDX_YDG] * r_hp
        else:
            if not frozen_set:
                frozen[0] = deI; frozen_set = True
            # stick-fixed: elevator and stabiliser frozen at their trim at the loss; wheel and pedals neutral,
            # so ailerons and rudder sit at their trim offsets (fitted per case); no damper, no protection.
            de = frozen[0]; da = P[IDX_DAOFF]; dr = P[IDX_DROFF] + tac
        lim = math.radians(25.0)
        ctl[0] = max(min(de, lim), -lim); ctl[1] = max(min(da, lim), -lim); ctl[2] = max(min(dr, lim), -lim)
        ctl[3] = Tr; ctl[4] = Tl; ctl[5] = adot
        if t >= nextrec - 1e-9 and k < nrec:
            rec[k, 0] = t; rec[k, 1] = x[1] / NM; rec[k, 2] = x[0] / NM; rec[k, 3] = h / FT
            rec[k, 4] = math.degrees(phi); rec[k, 5] = M; rec[k, 6] = eas / KT; rec[k, 7] = nz
            rec[k, 8] = math.degrees(alpha); rec[k, 9] = math.degrees(ctl[0]); rec[k, 10] = math.degrees(th)
            rec[k, 11] = math.degrees(psi) % 360.0
            k += 1; nextrec += 1.0
        # RK4 with controls held
        k1 = d0
        k2 = deriv(t + dt / 2, x + dt / 2 * k1, ctl, P, mh, vh, sh, ml, vl, sl, out)
        k3 = deriv(t + dt / 2, x + dt / 2 * k2, ctl, P, mh, vh, sh, ml, vl, sl, out)
        k4 = deriv(t + dt, x + dt * k3, ctl, P, mh, vh, sh, ml, vl, sl, out)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        nq = math.sqrt(x[6] ** 2 + x[7] ** 2 + x[8] ** 2 + x[9] ** 2)
        x[6:10] = x[6:10] / nq
        t += dt
    return rec[:k]


IDX_DT, IDX_TEND, IDX_LAW, IDX_ALTH = IDX["dt"], IDX["t_end"], IDX["law"], IDX["alt_hold_m"]
IDX_ULAG, IDX_TLOSS, IDX_T0, IDX_EASFLOOR = IDX["u_lag"], IDX["t_loss"], IDX["T0"], IDX["eas_floor"]
IDX_THRLOSS, IDX_T1, IDX_T2, IDX_YENG = IDX["thr_loss"], IDX["t1"], IDX["t2"], IDX["y_eng"]
IDX_TAC, IDX_PSI, IDX_YDG, IDX_REFTAU = IDX["ap_tac"], IDX["psi_cmd"], IDX["yd_gain"], IDX["ref_tau"]
IDX_MCT = IDX["mct"]
IDX_VREFFL, IDX_USTIFF, IDX_DAOFF, IDX_BAP, IDX_DROFF = IDX["Vref_floor_eas"], IDX["u_stiff"], IDX["da_offset"], IDX["bap"], IDX["dr_offset"]
