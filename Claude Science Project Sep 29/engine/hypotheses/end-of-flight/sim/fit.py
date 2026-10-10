"""Fit the 6-DOF to Boeing's ten engineering-simulator traces (Pete's ruling, 9 Oct 2026: full traces may be
fitted; the files are not redistributed).

Likelihood: Gaussian on the 1 Hz X, Y (NM) and altitude (ft) traces, time-aligned at the export's t = 0, with noise
growing with time since the loss of control, tau = max(t - t_loss, 0):
    sigma_h = 200 ft + 2 ft/s tau,  sigma_xy = 0.2 NM + 0.01 NM/s tau
(a circling descent cannot be phase-matched indefinitely, and the model must not claim it can), tripled where
Boeing's own EAS exceeds 450 kt (ATSB: some motion left the simulator's database; this is the stand-in marker).
If the model reaches the sea first, the remaining Boeing samples are scored against its last point.
Pinned per case from the event extraction (boeing_events.py): start altitude, TAS, first flame-out, loss of
control, second flame-out (long cases), heading from the start track corrected for the fitted wind.
Fitted per case: mass, mct, eas_floor (long cases), da_offset, dr_offset, thr_loss and t2 after the loss
(short cases), law in {1 normal-like, 2 stick-fixed}, and ap_tac in {0, 1} (short cases).
Fitted shared: SHARED below.
"""
import csv, os, json, math, pathlib, sys
import numpy as np
from scipy.optimize import minimize
from model import schedules, default_params, trim, state
from sixdof import simulate, FT, KT, NM, IDX, wind_ned

SHARED = {"m_Clb": (0.3, 3.0, 1.0), "m_Cnb": (0.3, 3.0, 1.0), "m_Clr": (0.3, 3.0, 1.0), "m_Cnr": (0.3, 3.0, 1.0),
          "m_Cma": (0.5, 2.0, 1.0), "m_Cmq": (0.5, 2.0, 1.0), "tuck_x": (0.0, 3.0, 0.0), "kw": (0.0, 60.0, 20.0),
          "Mcc": (0.80, 0.92, 0.87), "u_stiff": (0.2, 3.0, 0.8), "u_lag": (0.2, 2.5, 0.8), "Cm_bias": (-0.02, 0.02, 0.0)}
CASE_LONG = {"mass": (150e3, 200e3, 175e3), "mct": (0.4, 1.0, 0.75), "eas_floor_kt": (150.0, 185.0, 165.0),
             "da_offset_deg": (-1.0, 1.0, 0.0), "dr_offset_deg": (-1.0, 1.0, 0.0)}
CASE_SHORT = {"mass": (150e3, 200e3, 175e3), "da_offset_deg": (-1.0, 1.0, 0.0), "dr_offset_deg": (-1.0, 1.0, 0.0),
              "thr_loss": (0.2, 1.0, 1.0), "t2_after_s": (0.0, 900.0, 900.0)}
ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHED = None


def load(runs=ROOT / "runs/boeing"):
    rows = list(csv.reader(l for l in open(runs / "boeing-runs-targets.csv") if not l.startswith("#")))
    tg = {r[0].replace("Case ", "case"): dict(zip(rows[0], r)) for r in rows[1:]}
    Z = np.load(runs / "cases.npz")
    data = {c: {k: Z[f"{c}/{k}"] for k in ("t_s", "x_nm", "y_nm", "alt_ft", "gs_mps")} for c in tg}
    return tg, data


def to_box(z, spec):
    return {k: lo + (hi - lo) / (1 + math.exp(-v)) for (k, (lo, hi, _)), v in zip(spec.items(), z)}


def from_box(vals, spec):
    out = []
    for k, (lo, hi, d) in spec.items():
        f = min(max((vals.get(k, d) - lo) / (hi - lo), 1e-4), 1 - 1e-4); out.append(math.log(f / (1 - f)))
    return np.array(out)


def setup(case, tg, data, shared, nuis, law, tac):
    t = tg[case]; long = t["regime"] == "long"
    h0 = float(t["start_alt_ft"]) * FT; tas = float(t["start_tas_kt"]) * KT
    P0 = default_params(**shared)
    # start heading: ground track over the first 30 s, corrected for the wind at the start altitude
    d = data[case]; vx = (d["x_nm"][30] - d["x_nm"][0]) * NM / 30; vy = (d["y_nm"][30] - d["y_nm"][0]) * NM / 30
    wn, we = wind_ned(h0, P0)
    psi = math.degrees(math.atan2(vx - we, vy - wn)) % 360
    t1 = float(t["t_first_flameout_s"]); tl = float(t["t_uncontrolled_s"])
    kw = dict(shared); kw.update(mass=nuis["mass"], psi_cmd=psi, alt_hold_m=h0, t1=t1, law=law,
                                  da_offset=math.radians(nuis["da_offset_deg"]), dr_offset=math.radians(nuis["dr_offset_deg"]),
                                  t_end=float(d["t_s"][-1]) + 60)
    if long:
        t2 = float(t["t_second_flameout_s"])
        kw.update(t2=t2, t_loss=t2, mct=nuis["mct"], eas_floor=nuis["eas_floor_kt"] * KT, ap_tac=1.0)
    else:
        kw.update(t_loss=tl, t2=tl + nuis["t2_after_s"], thr_loss=nuis["thr_loss"], ap_tac=float(tac), mct=0.75)
    P = default_params(**kw)
    al, de, T, ok = trim(h0, tas, psi, P, SCHED)
    return P, state(h0, tas, psi, al, P), de, T, ok


# Objective options (10 Oct 2026, the 6-DOF gate diagnosis, results/eof-diagnostic-smokes-oct10). Defaults reproduce the
# 9-10 Oct fit exactly. The diagnosis: altitude tolerance grows 2 ft/s after the loss of control (to ~3,000 ft by the
# end of a glide), so Boeing's 300-1,200 ft phugoids cost almost nothing to miss, and nothing scores the vertical speed,
# so the dives (cases 4, 5, 10) are not pulled in. EOF_FIT_ALT_GROWTH sets the growth (ft/s); EOF_FIT_VS_SD (ft/min,
# 0 = off) adds a vertical-speed residual on 3-s smoothed central differences of both traces, the same estimator as
# the calibration statistics; EOF_FIT_MASS = "lo,hi" (kg) narrows the case mass box (ZFW ~174 t plus the left
# tank's residual at the right flame-out: 172-178 t), which the 9 Oct fit drove to its 200 t bound.
OBJ = {"alt_growth": float(os.environ.get("EOF_FIT_ALT_GROWTH", "2.0")), "vs_sd_fpm": float(os.environ.get("EOF_FIT_VS_SD", "0"))}
if os.environ.get("EOF_FIT_MASS"):
    _lo, _hi = (float(v) for v in os.environ["EOF_FIT_MASS"].split(","))
    for _spec in (CASE_LONG, CASE_SHORT):
        _spec["mass"] = (_lo, _hi, min(max(_spec["mass"][2], _lo), _hi))


def _vs_fpm(t, h):
    hs = np.convolve(h, np.ones(3) / 3, mode="same"); v = np.gradient(hs, t) * 60.0
    v[0] = v[1]; v[-1] = v[-2]
    return v


def residuals(case, tg, data, shared, nuis, law, tac, return_rec=False):
    """Weighted residual vector r with nll = 0.5 r.r + const (the const is the log-sd term, which does not depend on
    the shared physics except through the time of loss, held by the nuisance)."""
    P, x0, de, T, ok = setup(case, tg, data, shared, nuis, law, tac)
    d = data[case]; n = len(d["t_s"])
    if ok != 1:
        k = 3 * n + (n if OBJ["vs_sd_fpm"] > 0 else 0)
        return (np.full(k, 1e3), None, None) if return_rec else np.full(k, 1e3)
    rec = simulate(P, *SCHED, x0, de, T)
    idx = np.minimum(np.arange(n), len(rec) - 1); sim = rec[idx]
    tl = P[IDX["t_loss"]]; tau = np.maximum(d["t_s"] - tl, 0)
    sh = 200 + OBJ["alt_growth"] * tau; sxy = 0.2 + 0.01 * tau
    rho = np.array([math.sqrt(max(1e-6, (288.15 - 0.0019812 * min(a, 36089)) / 288.15) ** 4.256) for a in d["alt_ft"]])
    out_db = (d["gs_mps"] * np.sqrt(rho) / KT) > 450
    sh = np.where(out_db, 3 * sh, sh); sxy = np.where(out_db, 3 * sxy, sxy)
    parts = [(sim[:, 3] - d["alt_ft"]) / sh, (sim[:, 1] - d["x_nm"]) / sxy, (sim[:, 2] - d["y_nm"]) / sxy]
    const = float(np.sum(np.log(sh) + 2 * np.log(sxy)))
    if OBJ["vs_sd_fpm"] > 0:
        svs = np.where(out_db, 3 * OBJ["vs_sd_fpm"], OBJ["vs_sd_fpm"])
        # past the end of the simulated record the model is on the surface: score it as such
        ended = np.arange(n) >= len(rec)
        vs_sim = np.where(ended, 0.0, _vs_fpm(d["t_s"], sim[:, 3]))
        parts.append((vs_sim - _vs_fpm(d["t_s"], d["alt_ft"])) / svs); const += float(np.sum(np.log(svs)))
    r = np.concatenate(parts)
    return (r, const, rec) if return_rec else r


def nll(case, tg, data, shared, nuis, law, tac, return_rec=False):
    if OBJ["alt_growth"] == 2.0 and OBJ["vs_sd_fpm"] == 0:
        return _nll_v1(case, tg, data, shared, nuis, law, tac, return_rec)
    r, const, rec = residuals(case, tg, data, shared, nuis, law, tac, return_rec=True)
    if rec is None:
        return (1e9, None) if return_rec else 1e9
    val = 0.5 * float(r @ r) + const
    return (val, rec) if return_rec else val


def _nll_v1(case, tg, data, shared, nuis, law, tac, return_rec=False):
    P, x0, de, T, ok = setup(case, tg, data, shared, nuis, law, tac)
    if ok != 1:
        return 1e9
    rec = simulate(P, *SCHED, x0, de, T)
    d = data[case]; n = len(d["t_s"]); m = len(rec)
    idx = np.minimum(np.arange(n), m - 1)
    sim = rec[idx]
    tl = P[IDX["t_loss"]]; tau = np.maximum(d["t_s"] - tl, 0)
    eas = d["gs_mps"]  # ground speed as a cheap overspeed marker; the EAS marker is applied below
    sh = 200 + 2 * tau; sxy = 0.2 + 0.01 * tau
    rho = np.array([math.sqrt(max(1e-6, (288.15 - 0.0019812 * min(a, 36089)) / 288.15) ** 4.256) for a in d["alt_ft"]])
    out_db = (d["gs_mps"] * np.sqrt(rho) / KT) > 450
    sh = np.where(out_db, 3 * sh, sh); sxy = np.where(out_db, 3 * sxy, sxy)
    r = (((sim[:, 3] - d["alt_ft"]) / sh) ** 2 + ((sim[:, 1] - d["x_nm"]) / sxy) ** 2 + ((sim[:, 2] - d["y_nm"]) / sxy) ** 2)
    val = 0.5 * float(np.sum(r)) + float(np.sum(np.log(sh) + 2 * np.log(sxy)))
    return (val, rec) if return_rec else val


def fit_case(case, tg, data, shared, law, tac=0, maxiter=300, x_init=None):
    spec = CASE_LONG if tg[case]["regime"] == "long" else CASE_SHORT
    z0 = from_box(x_init or {}, spec)
    f = lambda z: nll(case, tg, data, shared, to_box(z, spec), law, tac)
    if os.environ.get("EOF_FIT_CASE_METHOD", "powell") == "lsq":
        # Trust-region least squares on the residual vector (10 Oct): converges where Powell's line searches stall.
        from scipy.optimize import least_squares
        rf = lambda z: residuals(case, tg, data, shared, to_box(z, spec), law, tac)
        r = least_squares(rf, z0, method="trf", diff_step=1e-3, max_nfev=max(5, maxiter // (len(spec) + 1)))
        z = r.x if f(r.x) <= f(z0) else z0
        return f(z), to_box(z, spec), int(r.nfev)
    res = minimize(f, z0, method="Powell", options=dict(maxfev=maxiter, xtol=1e-2, ftol=1e-3))
    return res.fun, to_box(res.x, spec), res.nfev


def main():
    global SCHED
    SCHED = schedules(); tg, data = load()
    case, law = sys.argv[1], int(sys.argv[2]); tac = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    maxiter = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    shared = {k: v[2] for k, v in SHARED.items()}
    base = nll(case, tg, data, shared, {k: v[2] for k, v in (CASE_LONG if tg[case]["regime"] == "long" else CASE_SHORT).items()}, law, tac)
    val, nuis, nfev = fit_case(case, tg, data, shared, law, tac, maxiter)
    out = dict(case=case, law=law, tac=tac, nll_default=base, nll=val, nfev=nfev, nuisance=nuis, shared=shared)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
