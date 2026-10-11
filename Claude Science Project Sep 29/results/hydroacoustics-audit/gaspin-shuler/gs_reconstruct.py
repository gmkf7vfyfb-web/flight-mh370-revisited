"""Re-implementation of the Gaspin & Shuler (1971, NOLTR 71-160) idealized pressure-time construction (section 5,
printed pp. 7-9; Table 2 printed p. 8; Fig. 2 printed p. 25) and its 1/3-octave energy spectrum (section 5.5, p. 9).

G&S hand-drew the curves from Table 2; the shapes between the tabulated points are NOT given in the report. The
shape choices here are declared options (SHAPES) and are judged only by how well they reproduce G&S Table 3
(printed p. 12) at G&S's own five conditions. Nothing here is fitted to SUS or hydrophone data.

Units: W lb TNT, depth ft, R ft (100 yd = 300 ft), pressures psi, time s. Output: dB re 1 erg/cm^2/Hz at 100 yd,
one-sided energy flux spectral density E(f) = 2|P(f)|^2/(rho c), band-averaged over ideal bands.
External input (declared): Arons TNT shock impulse I_W = 1.46 W^(1/3) (W^(1/3)/R)^0.89 psi s (Arons 1954 / Cole 1948
similitude, quoted from the secondary literature) scaled by G&S Fig. 23 (printed p. 46, DIGITISED) Is/Iw(depth).
"""
import numpy as np

PSI = 68947.57          # dyn/cm^2 per psi
RHOC = 1.026 * 1.50e5   # g cm^-2 s^-1 (sea water, declared; G&S do not state their rho c)
R_FT = 300.0

_fig23 = None


def is_over_iw(depth_ft):
    global _fig23
    if _fig23 is None:
        import os
        _fig23 = np.loadtxt(os.path.join(os.path.dirname(__file__), "gs1971_fig23_impulse_ratio_DIGITISED.csv"),
                            delimiter=",", skiprows=1)
    x = np.log10(_fig23[:, 0]); y = _fig23[:, 1]
    lx = np.log10(depth_ft)
    if lx > x.max():   # linear extrapolation in log depth beyond 2990 ft (flagged by caller)
        k = np.polyfit(x[-60:], y[-60:], 1); return float(np.polyval(k, lx))
    return float(np.interp(lx, x, y))


def params(W, depth_ft, R=R_FT):
    a = W ** (1 / 3); Z = depth_ft + 33.0; s = a / Z ** (5 / 6)
    p = dict(P0=2.08e4 * (a / R) ** 1.13, Pmin=77 * Z ** (1 / 3) * a / R, P1=3300 * a / R,
             theta=5.8e-5 * a * (a / R) ** -0.22, Tpp=0.555 * s, Tnp=3.10 * s, Tbp=1.10 * s, T1=4.34 * s,
             T2=3.06 * s, T3=2.48 * s, T4=2.31 * s)
    p["P2"], p["P3"], p["P4"] = 0.22 * p["P1"], 0.10 * p["P1"], 0.03 * p["P1"]
    p["Iw"] = 1.46 * a * (a / R) ** 0.89
    p["Is"] = is_over_iw(depth_ft) * p["Iw"]
    p["fb"] = 1.0 / p["T1"]
    return p


def _cusp(t, tc, hl, hr, kappa):
    """unit peak at tc, zero at tc-hl and tc+hr, exponential-cusp shape with decay constant h/kappa."""
    out = np.zeros_like(t)
    for side, h in ((t <= tc, hl), (t > tc, hr)):
        u = np.abs(t[side] - tc) / h
        e = np.exp(-kappa)
        out[side] = np.clip((np.exp(-kappa * u) - e) / (1 - e), 0, None)
    return out


def pulse(W, depth_ft, kappa=3.0, neg="halfsine", is_scale=1.0, R=R_FT, dt=None, tmax_periods=1.6):
    p = params(W, depth_ft, R)
    th = p["theta"]; dt = dt or th / 12
    tend = p["T1"] + p["T2"] + p["T3"] + p["T4"] + 0.6 * p["Tbp"]
    t = np.arange(0, tend * tmax_periods, dt)
    x = np.zeros_like(t)
    # shock: exponential to 2 theta, then power-law tail to zero at Tpp carrying the rest of Is
    Is = p["Is"] * is_scale
    m = t <= 2 * th; x[m] = p["P0"] * np.exp(-t[m] / th)
    I_exp = p["P0"] * th * (1 - np.exp(-2))
    L = p["Tpp"] - 2 * th; A = p["P0"] * np.exp(-2)
    n = max(A * L / max(Is - I_exp, 1e-12) - 1.0, 0.0)
    m = (t > 2 * th) & (t < p["Tpp"]); u = (t[m] - 2 * th) / L; x[m] = A * (1 - u) ** n
    p["shock_tail_exponent"] = n
    # bubble positive phases
    centres = [p["T1"], p["T1"] + p["T2"], p["T1"] + p["T2"] + p["T3"], p["T1"] + p["T2"] + p["T3"] + p["T4"]]
    peaks = [p["P1"], p["P2"], p["P3"], p["P4"]]
    per = [p["T1"], p["T2"], p["T3"], p["T4"]]
    b0 = p["Tpp"] + p["Tnp"]; hl1 = p["T1"] - b0; hr1 = b0 + p["Tbp"] - p["T1"]
    edges = []
    for k in range(4):
        sc = per[k] / per[0] if k else 1.0
        hl, hr = hl1 * sc, hr1 * sc
        x += peaks[k] * _cusp(t, centres[k], hl, hr, kappa)
        edges.append((centres[k] - hl, centres[k] + hr))
    # negative phases: first between Tpp and bubble 1 start with depth Pmin; later ones between bubbles,
    # amplitude Pmin * q^k with q chosen so that the residual impulse to the end of bubble 4 is zero (G&S 5.4)
    negs = [(p["Tpp"], edges[0][0])] + [(edges[k][1], edges[k + 1][0]) for k in range(3)]
    shapes = []
    for (a_, b_) in negs:
        y = np.zeros_like(t); mm = (t >= a_) & (t <= b_)
        uu = (t[mm] - a_) / (b_ - a_)
        y[mm] = np.sin(np.pi * uu) if neg == "halfsine" else np.sin(np.pi * uu) ** 2
        shapes.append(y)
    iend = t <= edges[3][1]
    Ipos = np.trapezoid(x[iend], t[iend])
    I1 = p["Pmin"] * np.trapezoid(shapes[0][iend], t[iend])
    rest = [np.trapezoid(s_[iend], t[iend]) for s_ in shapes[1:]]

    def resid(q):
        return Ipos - I1 - p["Pmin"] * sum(q ** (k + 1) * r for k, r in enumerate(rest))
    lo, hi = 0.0, 1.0
    if resid(hi) > 0:      # cannot null with q <= 1: allow q > 1 but flag
        hi = 5.0
    if resid(lo) < 0:      # first negative phase alone over-balances: q = 0, flag
        q = 0.0
    else:
        for _ in range(80):
            mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if resid(mid) > 0 else (lo, mid)
        q = 0.5 * (lo + hi)
    x -= p["Pmin"] * shapes[0]
    for k, s_ in enumerate(shapes[1:]):
        x -= p["Pmin"] * q ** (k + 1) * s_
    p["neg_ratio_q"] = q; p["residual_impulse"] = float(np.trapezoid(x[iend], t[iend]))
    p["impulse_balance"] = dict(Ipos=Ipos, I1=I1)
    return t, x, p


def esd_db(t, x, f):
    """one-sided energy flux spectral density, dB re 1 erg/cm^2/Hz, at frequencies f (direct DFT sum)."""
    dt = t[1] - t[0]
    P = np.array([np.sum(x * np.exp(-2j * np.pi * fi * t)) * dt for fi in f]) * PSI
    return 10 * np.log10(2 * np.abs(P) ** 2 / RHOC)


def band_db(t, x, lo, hi, n=60):
    f = np.geomspace(lo, hi, n)
    e = 10 ** (esd_db(t, x, f) / 10)
    return 10 * np.log10(np.trapezoid(e, f) / (hi - lo))
