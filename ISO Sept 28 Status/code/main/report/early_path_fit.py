"""Continuous 18:22-19:41 paths fitted to every early BTO/BFO, for route candidates from the 18:22 radar point.

Usage: .venv/bin/python report/early_path_fit.py [OUTPUT_PDF]   (default runs/early-path/early_path.pdf)

Measurements (14): the 18:25-18:28 bursts in data/satcom-1825-sequence.csv (7 BTOs with their
channel corrections and sigmas; the 4 BFOs not in the log-on warm-up transient), the 18:39:55
C-channel BFO and the 19:41:02 BTO and BFO (data/satcom-observations.csv). BFO sigma 7 Hz; one
BFO bias shared by all, profiled against the core's prior N(150, 25) Hz.

Path model, FL350 and level throughout:
  1. 18:22:12-18:28:15: a constant ground speed v1 (the sequence alone fixes it) along the
     scenario's geometry: a free initial bearing, or a waypoint route (fly-by, 15 deg bank).
  2. From 18:28:15: constant Mach M on the same geometry, ground speed from the ERA5 wind.
  3. Final major turn at 15 deg bank (turn rate g tan(bank) / TAS) onto a constant true
     track h3, still at Mach M, until 19:41:02. In a route scenario the turn starts at a free
     time but no later than arrival over the route's last waypoint (so "at or before").
The start is the 18:22:12 radar point, 10 NM past MEKAR on the scenario's first leg (the
radar position is not precise enough to separate N571 from MEKAR-SAMAK, 10 deg apart).
Everything uses satcom_model (the core's BTO/BFO equations, Inmarsat satellite states, ERA5).
"""

import csv
import math
import multiprocessing
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from satcom_model import (  # noqa: E402
    FIR_MERIDIAN, ROOT, T0, WP, afc, bearing, bfo_nobias, bto, dest, dist_nm, ground_speed, mach_of, satstate, unix,
    weather,
)

ALT = 35000.0
BANK = math.radians(15.0)
SIGMA_BFO = 7.0
BIAS_PRIOR = (150.0, 25.0)
T_ACCEL = unix("2014-03-07T18:28:15")
T_END = unix("2014-03-07T19:41:02")
T_LATEST_TURN = unix("2014-03-07T18:39:55")


def measurements():
    rows = []
    for r in csv.DictReader(open(ROOT / "data/satcom-1825-sequence.csv")):
        t = unix(r["time_utc"])
        if r["bto_sd_us"]:
            rows.append(("bto", t, float(r["bto_raw_us"]) + float(r["bto_correction_us"]), float(r["bto_sd_us"]), "1825"))
        if "transient" not in r["note"]:
            rows.append(("bfo", t, float(r["bfo_hz"]), SIGMA_BFO, "1825"))
    for r in csv.DictReader(open(ROOT / "data/satcom-observations.csv")):
        if r["epoch_id"] in ("m1839", "m1941"):
            t, tag = unix(r["time_utc"]), r["epoch_id"][1:]
            if r["bto_us"]:
                rows.append(("bto", t, float(r["bto_us"]), float(r["bto_sd_us"]), tag))
            rows.append(("bfo", t, float(r["bfo_hz"]), float(r["bfo_sd_hz"]), tag))
    return sorted(rows, key=lambda m: m[1])


MEAS = measurements()
T_OBS = sorted({m[1] for m in MEAS})
SAT = {t: satstate(t) for t in T_OBS}


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def simulate(route, v1, mach, t_turn, h3, first=None, turn_before_nm=None):
    """States (lat, lon, track, ground speed) at the observation times, plus the turn start and path.

    `route` is a list of points; the path steers to each in turn (fly-by at 15 deg bank), then
    holds the last leg's track. The final turn starts at t_turn, `turn_before_nm` short of the
    last route point, or on arrival over it, whichever is first."""
    first = route[0] if first is None else first
    pos = dest(WP["MEKAR"], bearing(WP["MEKAR"], first), 10.0)
    trk = bearing(pos, route[0])
    legs, k = list(route), 0
    t, out, path, turn_at = T0, {}, [(T0, pos)], None
    grid = sorted(set(np.arange(T0, T_END, 10.0).tolist()) | set(T_OBS) | {T_ACCEL, T_END})
    phase = "route"
    for i, t in enumerate(grid):
        temp, ue, vn = weather(t, ALT, *pos)
        tas = mach * math.sqrt(1.4 * 287.05287 * temp) / 0.514444
        if t < T_ACCEL:
            gs = v1
        else:  # track mode: the wind's cross-track part is crabbed out of the true airspeed
            cross = -vn * math.sin(trk) + ue * math.cos(trk)
            gs = ue * math.sin(trk) + vn * math.cos(trk) + math.sqrt(max(tas * tas - cross * cross, 0.0))
        if t in SAT:
            out[t] = (pos, trk, gs)
        if i + 1 == len(grid):
            break
        dt = grid[i + 1] - t
        rate = 9.80665 * math.tan(BANK) / (tas * 0.514444)
        if phase == "route" and k < len(legs):
            if dist_nm(pos, legs[k]) < gs * 20 / 3600 and k + 1 < len(legs):
                k += 1  # anticipate the next leg (fly-by)
            elif dist_nm(pos, legs[k]) < gs * dt / 3600:
                k = len(legs)
                phase = "turn"
        if phase == "route" and turn_before_nm is not None and k == len(legs) - 1 and dist_nm(pos, legs[k]) <= turn_before_nm:
            phase = "turn"
        if phase == "route" and t >= t_turn:
            phase = "turn"
        if phase == "turn" and turn_at is None:
            turn_at = (t, pos)
        want = h3 if phase == "turn" else (bearing(pos, legs[k]) if k < len(legs) else trk)
        trk = trk + max(-rate * dt, min(rate * dt, wrap(want - trk)))
        pos = dest(pos, trk, gs * dt / 3600)
        path.append((t + dt, pos))
    return out, turn_at, path


def score(states):
    """Chi-square by component and the profiled BFO bias."""
    parts, bfo_res = {}, []
    for kind, t, value, sd, tag in MEAS:
        pos, trk, gs = states[t]
        sat, satv = SAT[t]
        if kind == "bto":
            r = (value - bto(sat, pos[0], pos[1], ALT)) / sd
            parts[f"BTO {tag}"] = parts.get(f"BTO {tag}", 0.0) + r * r
        else:
            pred = bfo_nobias(sat, satv, afc(t), pos[0], pos[1], ALT, gs * math.cos(trk), gs * math.sin(trk))
            bfo_res.append((tag, value - pred, sd))
    m0, s0 = BIAS_PRIOR
    w = sum(1 / sd**2 for _, _, sd in bfo_res) + 1 / s0**2
    bias = (sum(r / sd**2 for _, r, sd in bfo_res) + m0 / s0**2) / w
    for tag, r, sd in bfo_res:
        parts[f"BFO {tag}"] = parts.get(f"BFO {tag}", 0.0) + ((r - bias) / sd) ** 2
    parts["bias prior"] = ((bias - m0) / s0) ** 2
    return sum(parts.values()), parts, bias


def nelder_mead(f, x0, step, iters=400):
    n = len(x0)
    simplex = [np.array(x0, float)] + [np.array(x0, float) + np.eye(n)[i] * step[i] for i in range(n)]
    vals = [f(x) for x in simplex]
    for _ in range(iters):
        order = np.argsort(vals)
        simplex, vals = [simplex[i] for i in order], [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < 1e-4:
            break
        c = np.mean(simplex[:-1], axis=0)
        xr = c + (c - simplex[-1]); fr = f(xr)
        if fr < vals[0]:
            xe = c + 2 * (c - simplex[-1]); fe = f(xe)
            simplex[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            simplex[-1], vals[-1] = xr, fr
        else:
            xc = c + 0.5 * (simplex[-1] - c); fc = f(xc)
            if fc < vals[-1]:
                simplex[-1], vals[-1] = xc, fc
            else:
                simplex = [simplex[0] + 0.5 * (s - simplex[0]) for s in simplex]
                vals = [f(s) for s in simplex]
    i = int(np.argmin(vals))
    return simplex[i], vals[i]


# Parameters: v1 (kt), Mach after 18:28:15, turn start (minutes after 18:28:15), final track h3 (deg),
# and for the free scenario the initial bearing h1 (deg). Bounds keep them physical.
BOUNDS = {"v1": (250, 560), "mach": (0.60, 0.86), "turn_min": (0.0, 11.7), "h3": (150, 240), "h1": (270, 340)}


def scenario(name, route_of, free=(), fixed=None, first=None):
    fixed = fixed or {}
    names = [p for p in ("v1", "mach", "turn_min", "h3", "h1") if p in free]

    def unpack(x):
        p = dict(fixed)
        for key, v in zip(names, x):
            lo, hi = BOUNDS[key]
            p[key] = min(max(v, lo), hi)
        return p

    def run(p):
        route = route_of(p)
        return simulate(route, p["v1"], p["mach"], T_ACCEL + 60 * p.get("turn_min", 1e6), math.radians(p["h3"]),
                        first=first(p) if first else None, turn_before_nm=p.get("turn_nm"))

    def objective(x):
        p = unpack(x)
        penalty = sum(1e3 * (v - min(max(v, BOUNDS[k][0]), BOUNDS[k][1])) ** 2 for k, v in zip(names, x))
        return score(run(p)[0])[0] + penalty

    starts = [dict(v1=v1, mach=0.78, turn_min=tm, h3=185.0, h1=h1)
              for v1 in (340, 450) for tm in (4.0, 9.0) for h1 in (300.0, 312.0)]
    seen, best = set(), None
    for s in starts:
        x0 = [s[k] for k in names]
        if tuple(x0) in seen:
            continue
        seen.add(tuple(x0))
        step = [{"v1": 30, "mach": 0.03, "turn_min": 2.0, "h3": 8.0, "h1": 4.0}[k] for k in names]
        x, v = nelder_mead(objective, x0, step)
        x, v = nelder_mead(objective, x, [s_ / 4 for s_ in step])
        if best is None or v < best[1]:
            best = (x, v)
    p = unpack(best[0])
    states, turn_at, path = run(p)
    total, parts, bias = score(states)
    return dict(name=name, params=p, total=total, parts=parts, bias=bias, turn_at=turn_at, path=path, states=states)


FAR = lambda h1: dest(WP["MEKAR"], math.radians(h1), 3000.0)  # noqa: E731
SCENARIOS = [
    ("Free: straight bearing h1, then turn", lambda p: [FAR(p["h1"])], ("v1", "mach", "turn_min", "h3", "h1"), None, None),
    ("Free, one Mach throughout (no speed change at 18:28)", lambda p: [FAR(p["h1"])], ("mach", "turn_min", "h3", "h1"),
     None, None),
    ("N571 (NILAM, IGOGU), turn at or before IGOGU", lambda p: [WP["NILAM"], WP["IGOGU"]], ("v1", "mach", "turn_min", "h3"),
     None, None),
    ("NILAM-SAMAK, turn at or before SAMAK", lambda p: [WP["NILAM"], WP["SAMAK"]], ("v1", "mach", "turn_min", "h3"), None,
     None),
    ("NILAM-SAMAK, fly-by SAMAK then track 180 (FIR boundary)", lambda p: [WP["NILAM"], WP["SAMAK"]], ("v1", "mach"),
     {"h3": 180.0}, None),
    ("MEKAR-SAMAK, turn at or before SAMAK", lambda p: [WP["SAMAK"]], ("v1", "mach", "turn_min", "h3"), None,
     lambda p: WP["SAMAK"]),
    ("MEKAR-SAMAK, fly-by SAMAK then track 180 (FIR boundary)", lambda p: [WP["SAMAK"]], ("v1", "mach"), {"h3": 180.0},
     lambda p: WP["SAMAK"]),
]


def main():
    out_pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "runs/early-path/early_path.pdf"
    with multiprocessing.get_context("fork").Pool(len(SCENARIOS)) as pool:
        results = pool.map(fit, range(len(SCENARIOS)))
        profile = pool.map(fit_profile, range(len(PROFILE)))
    for r in results:
        report(r, results[0]["total"])
    free = results[0]["total"]
    print("\n== Profile: final turn forced to start d NM before the last waypoint (v1, Mach, final track free) ==")
    print("route          d(NM)  turn start  18:22-28 kt (Mach)  Mach after  final trk  18:39:55 trk  "
          "chi2   delta  BFO1839  BTO1941  BFO1941")
    for (r, d), res in zip(PROFILE, profile):
        p, pr = res["params"], res["parts"]
        t, q = res["turn_at"]
        _, trk39, _ = res["states"][T_LATEST_TURN]
        pos, trk, _ = res["states"][min(res["states"], key=lambda t: abs(t - unix("2014-03-07T18:26:30")))]
        m1 = mach_of(p["v1"], trk, unix("2014-03-07T18:26:30"), ALT, *pos)
        print(f"{PROFILE_ROUTES[r][0]:14s} {d:4d}   {hhmmss(t)}   {p['v1']:4.0f} ({m1:.2f})         {p['mach']:.3f}     "
              f"{p['h3']:6.1f}     {math.degrees(trk39) % 360:6.0f}     {res['total']:6.1f} {res['total'] - free:+6.1f}  "
              f"{pr['BFO 1839']:6.1f}  {pr['BTO 1941']:6.1f}  {pr['BFO 1941']:6.1f}")
    plot(results, profile, free, out_pdf)
    print(f"\nwrote {out_pdf}")


# Profile: the final turn forced to start d NM short of the route's last waypoint (v1, Mach, h3 free).
PROFILE_ROUTES = [
    ("N571 to IGOGU", [WP["NILAM"], WP["IGOGU"]], None),
    ("NILAM-SAMAK", [WP["NILAM"], WP["SAMAK"]], None),
    ("MEKAR-SAMAK", [WP["SAMAK"]], WP["SAMAK"]),
]
PROFILE_NM = (0, 10, 20, 30, 40, 50, 60, 70, 80)
PROFILE = [(r, d) for r in range(len(PROFILE_ROUTES)) for d in PROFILE_NM]


def fit_profile(i):
    r, d = PROFILE[i]
    label, route, first = PROFILE_ROUTES[r]
    return scenario(f"{label}, turn {d} NM before", lambda p: route, ("v1", "mach", "h3"), {"turn_nm": float(d)},
                    (lambda p: first) if first else None)


def fit(i):
    name, route_of, free, fixed, first = SCENARIOS[i]
    if "one Mach" in name:
        return fit_one_mach(name, route_of, free)
    return scenario(name, route_of, free, fixed, first)


def fit_one_mach(name, route_of, free):
    """Free geometry with v1 tied to Mach M (ERA5 ground speed on bearing h1 at the 18:26 position)."""
    here = dest(WP["MEKAR"], math.radians(300.0), 40.0)
    t26 = unix("2014-03-07T18:26:00")

    def route(p):
        return route_of(p)

    names = list(free)

    def unpack(x):
        p = {}
        for key, v in zip(names, x):
            lo, hi = BOUNDS[key]
            p[key] = min(max(v, lo), hi)
        p["v1"] = ground_speed(p["mach"], math.radians(p["h1"]), t26, ALT, *here)
        return p

    def objective(x):
        p = unpack(x)
        penalty = sum(1e3 * (v - min(max(v, BOUNDS[k][0]), BOUNDS[k][1])) ** 2 for k, v in zip(names, x))
        states = simulate(route(p), p["v1"], p["mach"], T_ACCEL + 60 * p["turn_min"], math.radians(p["h3"]))[0]
        return score(states)[0] + penalty

    best = None
    for m in (0.60, 0.80):
        for h1 in (300.0, 312.0):
            x0 = [{"mach": m, "turn_min": 6.0, "h3": 185.0, "h1": h1}[k] for k in names]
            step = [{"mach": 0.03, "turn_min": 2.0, "h3": 8.0, "h1": 4.0}[k] for k in names]
            x, v = nelder_mead(objective, x0, step)
            x, v = nelder_mead(objective, x, [s / 4 for s in step])
            if best is None or v < best[1]:
                best = (x, v)
    p = unpack(best[0])
    states, turn_at, path = simulate(route(p), p["v1"], p["mach"], T_ACCEL + 60 * p["turn_min"], math.radians(p["h3"]))
    total, parts, bias = score(states)
    return dict(name=name, params=p, total=total, parts=parts, bias=bias, turn_at=turn_at, path=path, states=states)


def hhmmss(t):
    s = int(round(t - unix("2014-03-07T00:00:00")))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def report(r, reference):
    p, st = r["params"], r["states"]
    t1826 = min(st, key=lambda t: abs(t - unix("2014-03-07T18:26:30")))
    pos, trk, gs = st[t1826]
    m1 = mach_of(p["v1"], trk, t1826, ALT, *pos)
    print(f"\n== {r['name']} ==")
    print(f"  18:22-18:28: {p['v1']:.0f} kt ground speed on track {math.degrees(trk) % 360:.0f} deg (Mach {m1:.2f}); "
          f"after 18:28:15 Mach {p['mach']:.3f}")
    if r["turn_at"]:
        t, q = r["turn_at"]
        extra = ""
        if q[1] < FIR_MERIDIAN + 0.05:
            extra = " (at/west of the FIR boundary meridian)"
        print(f"  turn starts {hhmmss(t)} at {q[0]:.2f}N {q[1]:.2f}E{extra}; final track {p['h3']:.1f} deg; "
              f"SAMAK is {dist_nm(q, WP['SAMAK']):.0f} NM away, IGOGU {dist_nm(q, WP['IGOGU']):.0f} NM")
    pos39, trk39, gs39 = st[T_LATEST_TURN]
    pos41, trk41, gs41 = st[T_END]
    print(f"  18:39:55: {pos39[0]:.2f}N {pos39[1]:.2f}E, track {math.degrees(trk39) % 360:.0f}, {gs39:.0f} kt;  "
          f"19:41:02: {pos41[0]:.2f}N {pos41[1]:.2f}E, track {math.degrees(trk41) % 360:.0f}, {gs41:.0f} kt")
    comp = "  ".join(f"{k} {v:.1f}" for k, v in r["parts"].items())
    print(f"  chi2 {r['total']:.1f} (delta {r['total'] - reference:+.1f} vs free); bias {r['bias']:.1f} Hz;  {comp}")


def plot(results, profile, free, out_pdf):
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf = PdfPages(out_pdf)
    fig, ax = plt.subplots(figsize=(8.3, 7.5))
    colours = plt.cm.tab10.colors
    for i, r in enumerate(results):
        lat = [q[0] for _, q in r["path"]]
        lon = [q[1] for _, q in r["path"]]
        ax.plot(lon, lat, color=colours[i], lw=1.2, label=f"{r['name']}  (chi2 {r['total']:.1f})")
        for t in (T_LATEST_TURN, T_END):
            q = r["states"][t][0]
            ax.plot(q[1], q[0], "o", color=colours[i], ms=3)
    for n, (la, lo) in WP.items():
        ax.plot(lo, la, "k^", ms=4)
        ax.annotate(n, (lo, la), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.plot([FIR_MERIDIAN, FIR_MERIDIAN, 98.0], [8.1, 6.0, 6.0], "k--", lw=0.8, label="Kuala Lumpur FIR boundary")
    ax.set_aspect(1 / math.cos(math.radians(5)))
    ax.set_xlabel("longitude (deg E)")
    ax.set_ylabel("latitude (deg N)")
    ax.set_title("Best-fit continuous paths 18:22-19:41 (dots: 18:39:55 and 19:41:02)", fontsize=9)
    ax.legend(fontsize=6, loc="lower right")
    fig.tight_layout()
    pdf.savefig(fig)
    fig, ax = plt.subplots(figsize=(8.3, 5))
    for r, (label, _, _) in enumerate(PROFILE_ROUTES):
        rows = [(d, res["total"] - free) for (k, d), res in zip(PROFILE, profile) if k == r]
        ax.plot([d for d, _ in rows], [c for _, c in rows], "o-", label=label)
    ax.axhline(4.0, color="k", lw=0.6, ls=":", label="delta chi2 = 4")
    ax.set_xlabel("final turn starts this far before the last waypoint (NM)")
    ax.set_ylabel("chi2 minus free best fit")
    ax.set_title("Turn position: v1, Mach after 18:28 (0.60-0.86) and final track re-fitted at each point", fontsize=9)
    ax.legend(fontsize=8)
    fig.tight_layout()
    pdf.savefig(fig)
    pdf.close()


if __name__ == "__main__":
    main()
