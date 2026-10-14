"""Item 2: calibrate the point-mass model's free-flight parameters against the ten Boeing engineering-simulator cases, by features.

Design APPROVED by Pete 14 Oct 2026 (results/eof-calibration-tolerances-oct13/README.md): one value per case per target, Gaussian
residual with sigma = tolerance / 2, 7 shared parameters, no per-case nuisance, initial conditions read from each trace,
leave-one-out on all ten cases, dive cases 3, 4, 5, 6 and 10 named.

How a case is predicted. Boeing's trace is kept up to its loss of control (sim/boeing_events.py, t_uncontrolled_s); from there the
module's free dynamics are flown (integrator.rs `boeing_fit_batch`, production step sizes, the simulator's fitted wind) from the
trace's state at the loss, and the two pieces are joined into ONE composite trace. Boeing's full trace and the composite are then
measured by the SAME function, `features`, so a residual is the model's and not the measurement's.

The 7 shared parameters (theta):
  deterministic, one value for the type:  spiral_doubling_s (T2), trim_cl_offset (dcl), windmilling_per_engine (wm), rat_increment
  population, case-to-case variation:     residual_bank_deg upper bound (Bmax; bank ~ U[0, Bmax]), residual_bank_left_probability
                                          (p_left), spiral_divergent_weight (w_div)
Per case the prediction is the module's predictive density, marginalised over the latent draws the production model makes:
bank magnitude, direction, divergent or neutral, and the aerodynamic parameters NOT fitted here (oswald, ld_max, wave drag, tuck),
which keep their run.toml prior bands. The bank is integrated on a fixed grid in degrees with weight 1/Bmax inside [0, Bmax], so the
population parameters only reweight a cached set of flights and the deterministic ones alone require new flights.

Usage:
  python eof_point_fit.py features <sims-dir> <events.csv> <out.json>          Boeing feature table (no model)
  python eof_point_fit.py fit <sims-dir> <events.csv> <out-dir> [--exclude 'Case 03'] [--test-bin PATH] [--maxiter N] [--nuis K]
Boeing files: validation only, not redistributed; only summary statistics leave this script.
"""
import sys, os, json, glob, argparse, subprocess, tempfile, pathlib, time
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.optimize import minimize

G, NM, FT = 9.80665, 1852.0, 0.3048
END_FT = 1500.0            # common end reference: Boeing's records stop between 473 and 1,131 ft
DIVES = ("Case 03", "Case 04", "Case 05", "Case 06", "Case 10")
GLIDES = ("Case 01", "Case 02", "Case 07", "Case 08", "Case 09")
MASS_KG = 174_000.0        # module test mass; MH370 zero-fuel mass 174,369 kg (ATSB). Boeing's simulator mass not released.
# run.toml prior bands of the aerodynamic parameters NOT fitted here (marginalised)
NUIS = {"oswald": (0.76, 0.84), "ld_max": (20.8, 21.4), "wave_drag": (10.0, 40.0), "tuck": (0.0, 0.6)}
CAP_DEG, FLOOR_DEG = 90.0, 1.0   # run.toml spiral_bank_cap_deg, spiral_bank_floor_deg (NOT fitted: see README)
BANK_GRID = np.array([0.0, 1.0, 2.0, 3.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0, 22.5, 25.0, 27.5, 30.0, 32.5, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0])
# theta: name, lower, upper, start (run.toml prior centre). Fit bounds are WIDER than run.toml where the Boeing loss states need it:
# trim_cl_offset's run.toml band [-0.08, 0.08] cannot reach Boeing's post-loss mean EAS (~198 kt) from a loss at ~174 KEAS (that is
# about -0.18 in C_L at 174 t), so the fit searches [-0.30, 0.10] and reports a fitted value outside the band as a reach gap.
# spiral_doubling_s searches [3, 600] s against run.toml's [60, 120]: Boeing's short-case dives pass 15,000 ft/min 15-30 s after the
# loss. A fitted value outside the band is likewise reported as a reach gap, not adopted silently.
THETA = [("spiral_doubling_s", 3.0, 600.0, 90.0), ("trim_cl_offset", -0.30, 0.10, 0.0), ("windmilling_per_engine", 0.0, 0.0015, 0.00075),
         ("rat_increment", 0.0001, 0.0006, 0.00035), ("residual_bank_deg", 2.0, 60.0, 35.0), ("residual_bank_left_probability", 0.02, 0.98, 0.8),
         ("spiral_divergent_weight", 0.02, 0.98, 0.5)]


def load_case(f):
    a = np.genfromtxt(f, delimiter=",", skip_header=1)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3]


def load_events(path):
    rows = [l for l in open(path).read().splitlines() if l and not l.startswith("#")]
    hdr = rows[0].split(","); out = {}
    for r in rows[1:]:
        v = r.strip().split(","); d = dict(zip(hdr, v)); out[d["case"]] = {k: (float(x) if k not in ("case", "regime") else x) for k, x in d.items()}
    return out


def derived_bank(t, x, y):
    vx = savgol_filter(x * NM, 9, 2, deriv=1); vy = savgol_filter(y * NM, 9, 2, deriv=1)
    hdg = np.unwrap(np.arctan2(vx, vy)); om = savgol_filter(hdg, 31, 2, deriv=1)
    return np.degrees(np.arctan(np.hypot(vx, vy) * om / G))      # + right, still air (coordinated-turn relation)


def features(t, x, y, alt, t_ff, t_loss):
    """One value per target. All times from the first flame-out; all on 1 Hz resampled series; the same code for both sides."""
    t = np.asarray(t, float); keep = np.r_[True, np.diff(t) > 0]
    t, x, y, alt = t[keep], np.asarray(x, float)[keep], np.asarray(y, float)[keep], np.asarray(alt, float)[keep]
    tt = np.arange(np.ceil(t[0]), t[-1] + 1e-9, 1.0)
    h = np.interp(tt, t, alt); x = np.interp(tt, t, x); y = np.interp(tt, t, y); t = tt
    iend = int(np.argmax(h <= END_FT)) if (h <= END_FT).any() else len(h) - 1
    t, x, y, h = t[:iend + 1], x[:iend + 1], y[:iend + 1], h[:iend + 1]
    fpm = np.diff(h) / np.diff(t) * 60.0
    acc = np.diff(fpm * FT / 60.0) / np.diff(t[1:])
    i15 = np.where(fpm <= -15000.0)[0]
    dive = bool(len(i15) and (acc <= -0.67 * G).any())
    i_ff = int(np.searchsorted(t, t_ff)); i_loss = int(np.searchsorted(t, t_loss))
    f = {"dive": dive, "t_end_s": float(t[-1] - t_ff), "d_end_nm": float(np.hypot(x[-1] - x[i_ff], y[-1] - y[i_ff])),
         "peak_descent_fpm": float(-fpm.min())}
    f["t15_s"] = float(t[i15[0] + 1] - t_ff) if len(i15) else None
    f["chord15_nm"] = float(np.hypot(x[-1] - x[i15[0] + 1], y[-1] - y[i15[0] + 1])) if len(i15) else None
    # phugoid period and damping: vertical-speed extrema after the loss, before any 15,000 ft/min crossing
    fs = savgol_filter(h, 15, 3, deriv=1) * 60.0 if len(h) > 15 else np.r_[fpm, fpm[-1]]
    lim = (i15[0] if len(i15) else len(fs))
    seg = fs[i_loss:lim]
    pk, _ = find_peaks(seg, prominence=1000, distance=20); tr, _ = find_peaks(-seg, prominence=1000, distance=20)
    sp = np.concatenate([np.diff(pk), np.diff(tr)]).astype(float)
    f["phugoid_period_s"] = float(np.median(sp)) if len(sp) else None
    ext = np.sort(np.concatenate([pk, tr])); zeta = None
    if len(ext) >= 4:
        amp = np.abs(np.diff(seg[ext])) / 2.0                       # half peak-to-trough swings, successive
        r = amp[1:] / amp[:-1]; r = r[(r > 0) & np.isfinite(r)]
        if len(r):
            dlt = -2.0 * np.mean(np.log(r))                         # log decrement per full period (two half swings)
            zeta = float(dlt / np.sqrt(4 * np.pi ** 2 + dlt ** 2))
    f["phugoid_damping"] = zeta
    # bank growth: first sustained roll-off after the loss (|bank| >= 5 deg for 10 s), and |bank| 20 s later
    b = derived_bank(t, x, y) if len(t) > 40 else np.zeros_like(t)
    b[:16] = np.nan; b[-16:] = np.nan
    big = np.abs(b) >= 5.0; roll = None
    for i in range(i_loss, len(b) - 10):
        if big[i:i + 10].all():
            roll = i; break
    f["rolloff_s"] = float(t[roll] - t_ff) if roll is not None else None
    j = roll + 20 if roll is not None else None
    f["bank20_deg"] = float(abs(b[j])) if j is not None and j < len(b) and np.isfinite(b[j]) else None
    f["bank_sign"] = float(np.sign(b[j])) if f["bank20_deg"] is not None else None
    post = b[i_loss:]; post = post[np.isfinite(post)]
    f["max_bank_deg"] = float(np.max(np.abs(post))) if len(post) else None
    return f


def tolerances(case, fb, spread):
    """2-sigma bands per the approved table. spread: derivation-spread.json entry for the case."""
    tol = {}
    if case in GLIDES or case == "Case 05":
        if fb["phugoid_period_s"]: tol["phugoid_period_s"] = 0.10 * fb["phugoid_period_s"]
        if fb["phugoid_damping"] is not None: tol["phugoid_damping"] = 0.02
    if fb["bank20_deg"] is not None:
        tol["bank20_deg"] = float(np.hypot(max(2.0, 0.10 * fb["bank20_deg"]), spread.get("bank_spread_deg_p95", 0.0)))
    if case in DIVES:
        tol["t15_s"] = max(0.10 * fb["t15_s"], 5.0)
        pk = spread.get("peak_vs_fpm_by_window") or [fb["peak_descent_fpm"]]
        dspread = (max(pk) - min(pk)) / np.mean(pk)
        tol["peak_descent_fpm"] = float(fb["peak_descent_fpm"] * np.hypot(0.10, dspread))
        tol["chord15_nm"] = max(0.10 * fb["chord15_nm"], 0.5)
        tol["d_end_nm"] = max(0.10 * fb["d_end_nm"], 1.0)
    else:
        tol["peak_descent_fpm"] = max(300.0, 0.05 * fb["peak_descent_fpm"])
        tol["d_end_nm"] = 0.10 * fb["d_end_nm"]
    tol["t_end_s"] = max(0.10 * fb["t_end_s"], 10.0)
    return tol


def boeing_table(sims, events):
    out = {}
    for f in sorted(glob.glob(os.path.join(sims, "Case *.csv"))):
        c = os.path.basename(f)[:-4]; ev = events[c]
        out[c] = features(*load_case(f), ev["t_first_flameout_s"], ev["t_uncontrolled_s"])
    return out


def main_features(a):
    ev = load_events(a.events); tab = boeing_table(a.sims, ev)
    json.dump(tab, open(a.out, "w"), indent=1)
    keys = ["dive", "t15_s", "peak_descent_fpm", "chord15_nm", "phugoid_period_s", "phugoid_damping", "rolloff_s", "bank20_deg", "bank_sign", "max_bank_deg", "t_end_s", "d_end_nm"]
    print("case," + ",".join(keys))
    for c, f in tab.items():
        print(c.replace(" ", "") + "," + ",".join("-" if f[k] is None else (f"{f[k]:.3f}" if isinstance(f[k], float) else str(f[k])) for k in keys))


# ---------------------------------------------------------------------------------------------------------------- the fit
def nuisance_draws(k, seed=20261014):
    """Fixed draws (common random numbers across theta) of the unfitted aerodynamic parameters from their run.toml bands."""
    from scipy.stats import qmc
    u = qmc.Sobol(4, scramble=True, seed=seed).random(max(2, k))[:k]
    return [{n: lo + ui * (hi - lo) for (n, (lo, hi)), ui in zip(NUIS.items(), row)} for row in u]


def fly(test_bin, rows):
    """rows: list of job tuples (see integrator.rs boeing_fit_batch). Returns {id: (t, east_m, north_m, alt_ft)}."""
    with tempfile.TemporaryDirectory() as d:
        jp, op = os.path.join(d, "jobs.csv"), os.path.join(d, "out.bin")
        with open(jp, "w") as fh:
            fh.write("id,alt,tas,gam,hdg,mass,dcl,bank0,t2,cap,floor,oswald,ldmax,kw,tuck,wm,rat\n")
            for r in rows: fh.write(",".join(repr(float(v)) for v in r) + "\n")
        env = dict(os.environ, EOF_FIT_JOBS=jp, EOF_FIT_OUT=op, RAYON_NUM_THREADS="1")
        subprocess.run([test_bin, "--ignored", "--exact", "end_of_flight::integrator::tests::boeing_fit_batch", "--test-threads", "1", "-q"],
                       env=env, check=True, capture_output=True)
        a = np.fromfile(op, dtype="<f4").reshape(-1, 5).astype(np.float64)
    ids = a[:, 0].astype(np.int64); cut = np.r_[0, np.where(np.diff(ids) != 0)[0] + 1, len(ids)]
    return {int(ids[i]): (a[i:j, 1], a[i:j, 2], a[i:j, 3], a[i:j, 4]) for i, j in zip(cut[:-1], cut[1:])}


class Case:
    def __init__(self, name, path, ev, spread):
        self.name = name; self.t, self.x, self.y, self.h = load_case(path); self.ev = ev
        self.t_ff, self.t_loss = ev["t_first_flameout_s"], ev["t_uncontrolled_s"]
        self.fb = features(self.t, self.x, self.y, self.h, self.t_ff, self.t_loss)
        self.tol = tolerances(name, self.fb, spread)
        i = int(np.searchsorted(self.t, self.t_loss)); self.i_loss = i
        self.start = (ev["alt_at_uncontrolled_ft"], ev["tas_at_uncontrolled_kt"] * NM / 3600.0, ev["gamma_at_uncontrolled_deg"], ev["heading_at_uncontrolled_deg"])

    def composite(self, tr):
        t, e, n, h = tr; i = self.i_loss
        return (np.r_[self.t[:i], self.t_loss + t], np.r_[self.x[:i], self.x[i] + e / NM], np.r_[self.y[:i], self.y[i] + n / NM], np.r_[self.h[:i], h])


def flight_table(cases, test_bin, t2, dcl, wm, rat, nuis):
    """Every latent flight for every case at one deterministic theta. Returns per case: arrays of (bank_index, z, k, sign) and features."""
    rows, meta = [], []
    jid = 0
    for ci, c in enumerate(cases):
        alt, tas, gam, hdg = c.start
        for gi, b in enumerate(BANK_GRID):
            for z in (0, 1):
                for k, nu in enumerate(nuis):
                    for s in (-1.0, 1.0):
                        if b == 0.0 and s < 0 and z == 0:
                            continue       # wings level neutral: direction undefined, flown once
                        rows.append((jid, alt, tas, gam, hdg, MASS_KG, dcl, s * b, t2 if z else 0.0, CAP_DEG, FLOOR_DEG,
                                     nu["oswald"], nu["ld_max"], nu["wave_drag"], nu["tuck"], wm, rat))
                        meta.append((ci, gi, z, k, s)); jid += 1
    traces = fly(test_bin, rows)
    out = [[] for _ in cases]
    for j, (ci, gi, z, k, s) in enumerate(meta):
        c = cases[ci]
        out[ci].append(((gi, z, k, s), features(*c.composite(traces[j]), c.t_ff, c.t_loss)))
    return out


def flight_loglik(c, f):
    """log density of the Boeing case's features under ONE model flight, -inf where a categorical (dive yes/no, direction) differs.
    A continuous target the Boeing case has but the flight lacks contributes the density at 3 sigma (declared penalty)."""
    if f["dive"] != c.fb["dive"]:
        return -np.inf
    if c.fb["bank_sign"] is not None and f["bank_sign"] is not None and f["bank_sign"] != c.fb["bank_sign"]:
        return -np.inf
    ll = 0.0
    for k, tol in c.tol.items():
        s = tol / 2.0
        if f.get(k) is None:
            ll += -0.5 * 9.0 - np.log(s)
        else:
            ll += -0.5 * ((f[k] - c.fb[k]) / s) ** 2 - np.log(s)
    return ll


def bank_weights(bmax):
    """Trapezoid weights on BANK_GRID for the density 1/bmax on [0, bmax] (piecewise-linear integrand, grid truncated at bmax)."""
    g = BANK_GRID; w = np.zeros(len(g))
    for i in range(len(g) - 1):
        a, b = g[i], min(g[i + 1], bmax)
        if b <= a: break
        L = b - a; full = g[i + 1] - g[i]; fr = L / full      # integrand linear between nodes i and i+1
        w[i] += L * (1 - fr / 2); w[i + 1] += L * fr / 2
    return w / bmax


class Objective:
    def __init__(self, cases, test_bin, nuis, include):
        self.cases, self.bin, self.nuis, self.inc = cases, test_bin, nuis, include; self.cache = {}

    def tables(self, td, need_features=False):
        """Per case (latent index array, per-flight log density, per-flight features). Only the arrays are kept for every theta
        visited; the feature dicts (about 1 KB a flight) are dropped and rebuilt on demand, to bound memory over a long fit."""
        key = tuple(np.round(td, 10))
        if key not in self.cache or (need_features and self.cache[key][0][2] is None):
            tab = flight_table(self.cases, self.bin, *td, self.nuis)
            self.cache[key] = [(np.array([m for m, _ in tc]), np.array([flight_loglik(c, f) for _, f in tc]), tc) for c, tc in zip(self.cases, tab)]
        res = self.cache[key]
        if not need_features:
            self.cache[key] = [(m, ll, None) for m, ll, _ in res]
        return res

    def case_loglik(self, td, tp, idx=None):
        bmax, pl, wd = tp; bw = bank_weights(bmax); K = len(self.nuis); out = []
        for ci, (m, ll, _) in enumerate(self.tables(td)):
            if idx is not None and ci not in idx: out.append(np.nan); continue
            gi, z, s = m[:, 0].astype(int), m[:, 1], m[:, 3]
            ps = np.where((BANK_GRID[gi] == 0.0) & (z == 0), 1.0, np.where(s < 0, pl, 1 - pl))
            w = bw[gi] * np.where(z == 1, wd, 1 - wd) * ps / K
            ok = (w > 0) & np.isfinite(ll)
            out.append(float(np.log(np.sum(w[ok] * np.exp(ll[ok]))) if ok.any() else -745.0))
        return np.array(out)

    def total(self, td, tp):
        idx = set(np.flatnonzero(self.inc).tolist())
        return float(np.sum(self.case_loglik(td, tp, idx)[self.inc]))


def to_unit(v, lo, hi): return np.log((v - lo) / (hi - v))
def from_unit(u, lo, hi): return lo + (hi - lo) / (1 + np.exp(-u))


def fit(obj, maxiter, log, smoke=False):
    lo = np.array([t[1] for t in THETA]); hi = np.array([t[2] for t in THETA]); x0 = np.array([t[3] for t in THETA])
    best = {"nll": np.inf}

    def inner(td):
        def f(u):
            return -obj.total(td, from_unit(u, lo[4:], hi[4:]))
        starts = [to_unit(np.clip(best.get("tp", x0[4:]), lo[4:] + 1e-6, hi[4:] - 1e-6), lo[4:], hi[4:]), to_unit(x0[4:], lo[4:], hi[4:])]
        r = min((minimize(f, s, method="Nelder-Mead", options={"maxiter": 400, "xatol": 1e-3, "fatol": 1e-4}) for s in starts), key=lambda r: r.fun)
        return r.fun, from_unit(r.x, lo[4:], hi[4:])

    def outer(u):
        td = from_unit(u, lo[:4], hi[:4]); t0 = time.time(); nll, tp = inner(td)
        if nll < best["nll"]: best.update(nll=nll, td=td.tolist(), tp=tp.tolist())
        log.write(json.dumps({"td": td.tolist(), "tp": tp.tolist(), "nll": nll, "s": round(time.time() - t0, 1)}) + "\n"); log.flush()
        return nll

    # Stage 1: coarse grid over the two parameters that set the regime (doubling time, trim offset), wm and rat at their centres.
    grid = [(t2, d) for t2 in (3.0, 5.0, 8.0, 12.0, 20.0, 40.0, 90.0, 200.0) for d in (-0.25, -0.20, -0.15, -0.10, -0.05, 0.0, 0.05)]
    if smoke:
        grid = [(90.0, -0.15), (8.0, -0.15)]   # code-path check only
    scores = [(outer(to_unit(np.array([t2, d, x0[2], x0[3]]), lo[:4], hi[:4])), t2, d) for t2, d in grid]
    _, t2b, db = min(scores)
    # Stage 2: Nelder-Mead from the best grid point, with an initial simplex of about one grid step in each direction.
    u0 = to_unit(np.array([t2b, db, x0[2], x0[3]]), lo[:4], hi[:4])
    simplex = np.vstack([u0] + [u0 + np.eye(4)[i] * st for i, st in enumerate((0.6, 0.4, 1.0, 1.0))])
    minimize(outer, u0, method="Nelder-Mead", options={"maxiter": maxiter, "xatol": 1e-2, "fatol": 1e-2, "initial_simplex": simplex})
    best["grid"] = [[float(a), b, c] for a, b, c in scores]
    return best


def main_fit(a):
    ev = load_events(a.events)
    spread = json.load(open(pathlib.Path(__file__).resolve().parents[3] / ".." / "results" / "eof-calibration-tolerances-oct13" / "derivation-spread.json"))
    cases = [Case(os.path.basename(f)[:-4], f, ev[os.path.basename(f)[:-4]], spread.get("case" + os.path.basename(f)[5:7], {}))
             for f in sorted(glob.glob(os.path.join(a.sims, "Case *.csv")))]
    excl = [e.strip() for e in a.exclude.split(",")] if a.exclude else []
    include = np.array([c.name not in excl for c in cases])
    obj = Objective(cases, a.test_bin, nuisance_draws(a.nuis), include)
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with open(out / "trace.jsonl", "w") as log:
        best = fit(obj, a.maxiter, log, smoke=a.smoke)
    per = obj.case_loglik(np.array(best["td"]), np.array(best["tp"]))
    res = {"theta": dict(zip([t[0] for t in THETA], best["td"] + best["tp"])), "nll_included": best["nll"], "excluded": excl, "grid": best["grid"],
           "fit_bounds": {t[0]: [t[1], t[2]] for t in THETA},
           "case_loglik": dict(zip([c.name for c in cases], per.tolist())), "nuisance_draws": a.nuis, "bank_grid": BANK_GRID.tolist(),
           "boeing_features": {c.name: c.fb for c in cases}, "tolerances_2sigma": {c.name: c.tol for c in cases}}
    res["prediction"] = predict(obj, np.array(best["td"]), np.array(best["tp"]))
    json.dump(res, open(out / "fit.json", "w"), indent=1)
    print(json.dumps({"theta": res["theta"], "nll": best["nll"], "excluded": excl}))


def predict(obj, td, tp):
    """Per case and target: predictive mean, sd and 2-sigma pass probability of the model's feature, under the fitted latent mixture,
    plus the predictive probability of the right dive class and direction. Pass/fail is judged on the predictive median."""
    bmax, pl, wd = tp; bw = bank_weights(bmax); K = len(obj.nuis); out = {}
    for c, (m, _, tc) in zip(obj.cases, obj.tables(td, need_features=True)):
        gi, z, s = m[:, 0].astype(int), m[:, 1], m[:, 3]
        ps = np.where((BANK_GRID[gi] == 0.0) & (z == 0), 1.0, np.where(s < 0, pl, 1 - pl))
        w = bw[gi] * np.where(z == 1, wd, 1 - wd) * ps / K; w = w / w.sum()
        fl = [f for _, f in tc]
        dive_ok = np.array([f["dive"] == c.fb["dive"] for f in fl])
        sign_ok = np.array([c.fb["bank_sign"] is None or f["bank_sign"] == c.fb["bank_sign"] for f in fl])
        d = {"p_dive_class": float(w[dive_ok].sum()), "p_direction": float(w[sign_ok].sum()), "targets": {}}
        sel = dive_ok & sign_ok
        for k, tol in c.tol.items():
            v = np.array([np.nan if f.get(k) is None else f[k] for f in fl]); good = sel & np.isfinite(v)
            if not good.any(): d["targets"][k] = {"boeing": c.fb[k], "tol": tol, "available": 0.0}; continue
            ww = w[good] / w[good].sum(); vv = v[good]; o = np.argsort(vv); cw = np.cumsum(ww[o])
            med = float(vv[o][np.searchsorted(cw, 0.5)])
            d["targets"][k] = {"boeing": c.fb[k], "tol": tol, "median": med, "mean": float(np.sum(ww * vv)),
                               "p_within": float(np.sum(ww[np.abs(vv - c.fb[k]) <= tol])), "available": float(w[good].sum() / max(w[sel].sum(), 1e-300)),
                               "pass_median": bool(abs(med - c.fb[k]) <= tol)}
        out[c.name] = d
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("sims"); ap.add_argument("events"); ap.add_argument("out")
    ap.add_argument("--exclude", default=None); ap.add_argument("--test-bin", default=None); ap.add_argument("--maxiter", type=int, default=300)
    ap.add_argument("--nuis", type=int, default=4); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.mode == "features":
        main_features(a)
    elif a.mode == "fit":
        main_fit(a)
