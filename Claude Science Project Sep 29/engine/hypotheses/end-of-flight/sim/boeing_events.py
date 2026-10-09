"""Calibration targets from Boeing's ten end-of-flight engineering-simulator runs.

PORTED (9 Oct 2026) from the frozen ISO snapshot, `ISO Sept 28 Status/code/branch-diffs/hypothesis__end-of-flight.patch`
(prepare/boeing_runs.py), with only its paths changed: the zip and the output directory are command-line arguments.
Run: python sim/boeing_events.py <eof-sims.zip> <out-dir>. The method text below is the original's.

Input: data/external/end-of-flight/2018-08-19-eof-sims.zip. These are the ten 1 Hz
time / X / Y (NM) / altitude (ft) exports that ATSB defined in April 2016 and Boeing flew
in its engineering simulator (ATSB, "MH370 - Search and debris examination update",
2 Nov 2016, pp. 7-8); they were shared publicly by Iannello (19 Aug 2018) with ATSB's
permission. ATSB: they "do not represent all possible scenarios, nor ... the exact
response of the accident aircraft". No configuration labels, Mach, attitude or control
channels were released, so everything below is inferred from the track.

Method, per case:
- Simulator wind. The six long cases circle for 15-25 minutes. Low-passing the ground
  velocity over one phugoid period leaves a circle of radius TAS centred on the wind;
  a circle fit per loop gives the wind at that loop's mean altitude. One profile
  (speed linear in altitude, one direction) is fitted to all loops and used for every
  case, above 25,000 ft held at its 25,000 ft value.
- Events. t1: first flame-out, where the level-flight ground-speed decay extrapolates
  back to the initial speed, or the onset of descent, whichever is first. tu: onset of
  uncontrolled flight, the first time the 20 s mean |turn rate| of the air-relative
  velocity exceeds 0.15 deg/s. Long cases (tu - t1 > 120 s) kept the autopilot through
  the first flame-out; short cases lost it there. t2: second flame-out in the long cases,
  the last time before tu that the 10 s mean descent rate was under 1,000 fpm (the
  autopilot's driftdown ends and the nose drops); t2 = tu in the short cases. The model's
  calibration flights start at t2.
- After tu: bank from the coordinated-turn relation tan(bank) = V_h * turn rate / g,
  EAS from ISA density at the recorded altitude, phugoid period from successive downward
  zero crossings of the vertical speed about its 90 s running mean, descent-rate
  milestones on 1 s differences, and an energy-height L/D over the circling descent:
  L/D = sum(n * V dt) / (loss of h + V^2 / 2g), n = 1/cos(bank), over the circling
  descent below 260 KEAS. The runs end 470-1,860 ft above the sea; the impact time
  extrapolates the mean descent rate of the last 90 s (at least 1,000 fpm).

Writes boeing-runs-targets.csv next to this script (small derived data, committed) and
diagnostic figures to runs/end-of-flight/prepare/ (generated, never committed).

Calibration: the model's ignored test `calibration_traces` (calibrate.rs) flies each case from
its onset state in the same wind and writes 1 Hz traces in the exports' own X/Y/altitude
form to runs/end-of-flight/prepare/calibration-traces.csv. Given that file, this script
measures the simulated traces with the same code and writes calibration.csv and figures.

Run from the repository root:  .venv/bin/python hypotheses/end-of-flight/prepare/boeing_runs.py
"""

import csv
import io
import pathlib
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import sys
ZIP = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
HERE = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(".")
FIGURES = HERE
ROOT = HERE

NM, KT, FT, G = 1852.0, 1852.0 / 3600.0, 0.3048, 9.80665


def isa_density(h_m):
    t = np.maximum(288.15 - 0.0065 * h_m, 216.65)
    p = np.where(h_m <= 11_000, 101_325 * (t / 288.15) ** 5.25588,
                 22_632.06 * np.exp(-G * (h_m - 11_000) / (287.05287 * 216.65)))
    return p / (287.05287 * t)


def centred(v, w):
    """Running mean over w samples, NaN where the window is incomplete."""
    out = np.full(v.shape, np.nan)
    c = np.convolve(v, np.ones(w) / w, mode="valid")
    out[w // 2: w // 2 + len(c)] = c
    return out


def load():
    with zipfile.ZipFile(ZIP) as z:
        names = sorted(n for n in z.namelist() if n.endswith(".csv"))
        return {n[:-4]: np.loadtxt(io.StringIO(z.read(n).decode()), delimiter=",", skiprows=1).T for n in names}


def fit_circle(vx, vy, t):
    """Wind (m/s east, north) and TAS (m/s, linear in time) from a low-passed ground-velocity circle."""
    w = np.array([vx.mean(), vy.mean()])
    a, b, tt = 120.0, 0.0, t - t.mean()
    for _ in range(60):
        dx, dy = vx - w[0], vy - w[1]
        r = np.hypot(dx, dy)
        res = r - (a + b * tt)
        jac = np.column_stack([-dx / r, -dy / r, -np.ones_like(tt), -tt])
        step = np.linalg.lstsq(jac, -res, rcond=None)[0]
        w += step[:2]
        a += step[2]
        b += step[3]
    turned = np.unwrap(np.arctan2(vx - w[0], vy - w[1]))
    return w, abs(turned[-1] - turned[0])


def wind_profile(cases):
    """Fit one wind profile to per-loop circle fits of the long cases."""
    rows = []
    for name, (t, x, y, h) in cases.items():
        if t[-1] < 1500:
            continue
        vx = centred(centred(np.gradient(x, t) * NM, 88), 88)
        vy = centred(centred(np.gradient(y, t) * NM, 88), 88)
        hs = centred(h, 88)
        start = t[np.argmax(np.abs(np.gradient(np.unwrap(np.arctan2(vx, vy)), t)) > np.radians(0.2))]
        for w0 in np.arange(start + 60, t[-1] - 480, 120):
            s = (t >= w0) & (t < w0 + 480) & np.isfinite(vx)
            w, turned = fit_circle(vx[s], vy[s], t[s])
            if turned > np.radians(300):
                rows.append((hs[s].mean() * FT, w[0], w[1]))
    rows = np.array(rows)
    direction = np.arctan2(rows[:, 1].mean(), rows[:, 2].mean())
    speed = np.hypot(rows[:, 1], rows[:, 2])
    slope, intercept = np.polyfit(rows[:, 0], speed, 1)
    return direction, intercept, slope, rows


def analyse(name, t, x, y, h, wind, onset=None, long=None):
    """Measure one trace. Simulated traces start at their `onset` (s) and take `long` from the run."""
    direction, intercept, slope, _ = wind
    hm = h * FT
    speed = intercept + slope * np.minimum(hm, 25_000 * FT)
    wx, wy = speed * np.sin(direction), speed * np.cos(direction)
    vx = np.gradient(x, t) * NM - wx
    vy = np.gradient(y, t) * NM - wy
    vz = np.gradient(hm, t)
    vh = np.hypot(vx, vy)
    v = np.hypot(vh, vz)
    heading = np.unwrap(np.arctan2(vx, vy))
    turn = centred(np.gradient(heading, t), 20)
    bank = np.degrees(np.arctan(vh * np.nan_to_num(turn) / G))
    eas = v * np.sqrt(isa_density(hm) / 1.225)
    gs = np.hypot(np.gradient(x, t), np.gradient(y, t)) * NM
    gs30 = centred(gs, 30)

    # t1: first flame-out.
    g0 = np.nanmean(gs30[15:60])
    i_drop = np.argmax(gs30 < g0 - 5 * KT)
    j = slice(i_drop, i_drop + 60)
    k, c = np.polyfit(t[j], gs30[j], 1)
    t_decay = (g0 - c) / k if k < 0 else np.inf
    t_descent = t[np.argmax(centred(vz, 10) < -500 * FT / 60)]
    # A level deceleration of at least a minute before the descent marks a flame-out
    # with the autopilot still engaged; otherwise the descent itself is the first event.
    t1 = t_decay if 0 < t_decay < t_descent - 60 else t_descent
    iu = np.argmax((np.abs(turn) > np.radians(0.15)) & (t > t1))
    if onset is not None:
        t1, iu = onset, int(np.argmin(np.abs(t - onset)))
    tu = t[iu]
    long_case = tu - t1 > 120 if long is None else long
    i2 = iu
    if long_case and onset is None:
        slow = np.where((centred(vz, 10) > -1000 * FT / 60) & (t < tu))[0]
        i2 = slow[-1] if len(slow) else iu

    after = t >= tu
    descent_ft_s = -np.mean(np.gradient(h, t)[-90:])
    t_impact = t[-1] + h[-1] / max(descent_ft_s, 1000 / 60)
    vz_fpm = vz / FT * 60

    def first(mask):
        m = mask & after
        return t[np.argmax(m)] - tu if m.any() else np.nan

    # Phugoid: downward zero crossings of vz about its 90 s running mean.
    dv = vz - centred(vz, 90)
    s = after & np.isfinite(dv)
    zc = t[1:][(dv[1:] < 0) & (dv[:-1] >= 0) & s[1:]]
    zc = zc[np.concatenate([[True], np.diff(zc) > 30])] if len(zc) else zc
    periods = np.diff(zc)
    ok = (periods > 40) & (periods < 200)
    mid = 0.5 * (zc[1:] + zc[:-1])
    phugoid = np.median(periods[ok]) if ok.any() else np.nan
    phugoid_tas = np.interp(mid[ok], t, centred(v, 90)).mean() / KT if ok.any() else np.nan

    # Energy-height L/D while circling below the first high-speed excursion (long cases).
    ld = np.nan
    if long_case:
        m = (t > tu + 120) & (t < t[-1] - 60)
        m &= np.cumsum(m & (eas > 260 * KT)) == 0
        n = 1 / np.cos(np.radians(bank[m]))
        e = hm + v ** 2 / (2 * G)
        ld = np.sum(n * v[m]) / (e[m][0] - e[m][-1]) if m.sum() > 60 else np.nan

    xu, yu = x[iu], y[iu]
    wind_shift = np.array([np.sum(wx[after]), np.sum(wy[after])]) / NM
    return {
        "case": name, "regime": "long" if long_case else "short",
        "start_alt_ft": round(h[0]), "start_tas_kt": round(np.mean(v[5:60]) / KT, 1),
        "t_first_flameout_s": round(t1, 1), "t_uncontrolled_s": round(tu, 1),
        "alt_at_uncontrolled_ft": round(h[iu]), "tas_at_uncontrolled_kt": round(v[iu] / KT, 1),
        "eas_at_uncontrolled_kt": round(eas[iu] / KT, 1),
        "t_second_flameout_s": round(t[i2], 1), "alt_at_second_ft": round(h[i2]),
        "tas_at_second_kt": round(np.mean(v[max(i2 - 5, 0):i2 + 5]) / KT, 1),
        "eas_at_second_kt": round(np.mean(eas[max(i2 - 5, 0):i2 + 5]) / KT, 1),
        "heading_at_second_deg": round(np.degrees(np.nanmean(heading[max(i2 - 5, 0):i2 + 5])) % 360, 1),
        "gamma_at_second_deg": round(np.degrees(np.arctan2(np.mean(vz[max(i2 - 5, 0):i2 + 5]), np.mean(vh[max(i2 - 5, 0):i2 + 5]))), 2),
        "heading_at_uncontrolled_deg": round(np.degrees(np.nanmean(heading[max(iu - 5, 0):iu + 5])) % 360, 1),
        "gamma_at_uncontrolled_deg": round(np.degrees(np.arctan2(np.mean(vz[max(iu - 5, 0):iu + 5]), np.mean(vh[max(iu - 5, 0):iu + 5]))), 2),
        "duration_uncontrolled_s": round(t_impact - tu, 1),
        "ground_distance_nm": round(np.hypot(x[-1] - xu, y[-1] - yu), 2),
        "air_distance_nm": round(np.hypot(x[-1] - xu - wind_shift[0], y[-1] - yu - wind_shift[1]), 2),
        "path_length_nm": round(np.sum(np.hypot(np.diff(x[after]), np.diff(y[after]))), 1),
        "mean_eas_kt": round(np.nanmean(eas[after & (t < t[-1] - 30)]) / KT, 1),
        "max_eas_kt": round(np.nanmax(eas[after]) / KT, 1),
        "median_abs_bank_deg": round(np.nanmedian(np.abs(bank[after & (eas < 300 * KT)])), 1),
        "phugoid_period_s": round(phugoid, 1), "phugoid_tas_kt": round(phugoid_tas, 1),
        "max_descent_fpm": round(-np.min(vz_fpm[after])),
        "t_to_10k_fpm_s": first(vz_fpm < -10_000), "t_to_15k_fpm_s": first(vz_fpm < -15_000),
        "energy_ld": round(ld, 2),
        "_series": (t, x, y, h, eas / KT, vz_fpm, bank, t1, tu),
    }


METRICS = ["duration_uncontrolled_s", "air_distance_nm", "ground_distance_nm", "mean_eas_kt", "median_abs_bank_deg",
           "phugoid_period_s", "max_descent_fpm", "t_to_15k_fpm_s", "max_eas_kt", "energy_ld"]


def single_engine(data, wind, by_case):
    """The autopilot's single-engine phase: model from each run's first flame-out against the run."""
    m0 = data["set"] == "single-engine"
    if not m0.any():
        return
    names = list(dict.fromkeys(data["case"][m0]))
    fig, axes = plt.subplots(len(names), 2, figsize=(12, 2.4 * len(names)))
    print("single-engine phase, at the second flame-out: altitude ft and KEAS, model / run")
    for ax, name in zip(np.atleast_2d(axes), names):
        m = m0 & (data["case"] == name)
        b = by_case[name]
        r = analyse(name, data["t"][m], data["x_nm"][m], data["y_nm"][m], data["alt_ft"][m], wind, onset=0.0, long=False)["_series"]
        tb = b["_series"][0] - b["t_first_flameout_s"]
        keep = (tb >= -30) & (tb <= b["t_second_flameout_s"] - b["t_first_flameout_s"] + 30)
        ax[0].plot(tb[keep], b["_series"][3][keep], "k-", lw=0.8, label="Boeing")
        ax[0].plot(r[0], r[3], "r-", lw=0.8, label="model")
        ax[1].plot(tb[keep], b["_series"][4][keep], "k-", lw=0.8)
        ax[1].plot(r[0], r[4], "r-", lw=0.8)
        ax[0].set_title(f"{name}: altitude, ft (from the first flame-out)")
        ax[1].set_title("EAS, kt")
        ax[0].legend(fontsize=7)
        print(f"  {name}: {r[3][-1]:.0f} / {b['alt_at_second_ft']:.0f} ft, {np.nanmean(r[4][-6:-1]):.0f} / {b['eas_at_second_kt']:.0f} KEAS")
    fig.tight_layout()
    fig.savefig(ROOT / "runs/end-of-flight/prepare/calibration-single-engine.png", dpi=60)
    plt.close(fig)


def compare(wind, results):
    """Measure the model's calibration traces with the same code and tabulate them against the runs."""
    traces = ROOT / "runs/end-of-flight/prepare/calibration-traces.csv"
    if not traces.exists():
        return
    data = np.genfromtxt(traces, delimiter=",", names=True, dtype=None, encoding=None)
    rows = []
    by_case = {b["case"]: b for b in results}
    single_engine(data, wind, by_case)
    for label in [s for s in dict.fromkeys(data["set"]) if s != "single-engine"]:
        for name in dict.fromkeys(data["case"][data["set"] == label]):
            m = (data["set"] == label) & (data["case"] == name)
            b = by_case[name]
            r = analyse(name, data["t"][m], data["x_nm"][m], data["y_nm"][m], data["alt_ft"][m], wind,
                        onset=b["t_uncontrolled_s"] - b["t_second_flameout_s"], long=b["regime"] == "long")
            rows.append({"set": label, "case": name, **{k: r[k] for k in METRICS}, "_series": r["_series"]})
    with open(ROOT / "runs/end-of-flight/prepare/calibration.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["set", "case", *METRICS])
        w.writeheader()
        for r in [{"set": "boeing", "case": b["case"], **{k: b[k] for k in METRICS}} for b in results] + rows:
            w.writerow({k: r[k] for k in ["set", "case", *METRICS]})
    sets = list(dict.fromkeys(r["set"] for r in rows))
    print(f"{'set':34s}" + "".join(f"{k[:14]:>15s}" for k in METRICS))
    for label in sets:
        mine = [r for r in rows if r["set"] == label]
        # Mean relative error per metric over the cases this set flew.
        err = []
        for k in METRICS:
            e = [(r[k] - by_case[r["case"]][k]) / by_case[r["case"]][k] for r in mine
                 if np.isfinite(r[k]) and np.isfinite(by_case[r["case"]][k]) and by_case[r["case"]][k] != 0]
            err.append(np.mean(e) if e else np.nan)
        print(f"{label:34s}" + "".join(f"{e:+15.3f}" for e in err))
    for name in dict.fromkeys(r["case"] for r in rows):
        b = by_case[name]
        print(f"{name:10s} boeing " + " ".join(f"{k[:8]}={b[k]}" for k in METRICS))
        for r in rows:
            if r["case"] == name:
                print(f"{'':10s} {r['set'][:30]:30s} " + " ".join(f"{r[k]:.4g}" for k in METRICS))

    # Model against the run, per case, for each simulated set.
    for label in sets:
        mine = [r for r in rows if r["set"] == label]
        fig, axes = plt.subplots(len(mine), 4, figsize=(18, 2.6 * len(mine)))
        for ax, r in zip(np.atleast_2d(axes), mine):
            b = by_case[r["case"]]["_series"]
            # Both aligned on the second flame-out (the model's t = 0).
            tb = b[0] - by_case[r["case"]]["t_second_flameout_s"]
            for series, style, lab in [(b, "k-", "Boeing"), (r["_series"], "r-", "model")]:
                t = tb if series is b else series[0]
                ax[0].plot(series[1] - series[1][np.argmin(np.abs(t))], series[2] - series[2][np.argmin(np.abs(t))], style, lw=0.7, label=lab)
                ax[1].plot(t, series[3], style, lw=0.7)
                ax[2].plot(t, series[4], style, lw=0.7)
                ax[3].plot(t, series[6], style, lw=0.7)
            ax[0].set_aspect("equal")
            ax[0].legend(fontsize=7)
            ax[0].set_title(f"{r['case']}: track from onset, NM")
            ax[1].set_title("altitude, ft")
            ax[2].set_title("EAS, kt")
            ax[3].set_title("bank, deg")
            for a in ax[1:]:
                a.set_xlim(-60, max(tb[-1], r["_series"][0][-1]) + 30)
                a.grid(alpha=0.3)
        fig.suptitle(label)
        fig.tight_layout()
        fig.savefig(ROOT / "runs/end-of-flight/prepare" / f"calibration-{label.replace(' ', '_')}.png", dpi=55)
        plt.close(fig)
    return rows


def main():
    cases = load()
    wind = wind_profile(cases)
    direction, intercept, slope, loops = wind
    results = [analyse(n, *cases[n], wind) for n in cases]

    fields = [k for k in results[0] if not k.startswith("_")]
    with open(HERE / "boeing-runs-targets.csv", "w", newline="") as f:
        f.write(f"# Derived by prepare/boeing_runs.py from {ZIP.name}. Simulator wind fitted: "
                f"from {np.degrees(direction) + 180:.0f} deg, {intercept / KT:.1f} kt at sea level "
                f"{slope * 1000 * FT / KT:+.2f} kt per 1000 ft up to 25,000 ft.\n")
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in fields})

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(results), 4, figsize=(18, 3.0 * len(results)))
    for ax, r in zip(axes, results):
        t, x, y, h, eas, vz, bank, t1, tu = r["_series"]
        ax[0].plot(x, y, lw=0.8)
        ax[0].plot(x[t == tu], y[t == tu], "ro")
        ax[0].set_aspect("equal")
        ax[0].set_title(f"{r['case']} ({r['regime']}): track, NM; red = uncontrolled onset")
        ax[1].plot(t, h, lw=0.8)
        ax[1].set_title("altitude, ft")
        ax[2].plot(t, eas, lw=0.8)
        ax[2].set_title("EAS, kt (wind removed)")
        ax[3].plot(t, bank, lw=0.8, label="bank, deg")
        ax[3].plot(t, vz / 1000, lw=0.8, label="vertical speed, 1000 fpm")
        ax[3].legend(loc="lower left", fontsize=7)
        for a in ax[1:]:
            a.axvline(t1, color="k", ls=":", lw=0.8)
            a.axvline(tu, color="r", ls=":", lw=0.8)
            a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES / "boeing-runs.png", dpi=60)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(loops[:, 0] / FT, np.hypot(loops[:, 1], loops[:, 2]) / KT, "o", label="per-loop circle fits")
    hh = np.linspace(0, 25_000 * FT, 10)
    ax.plot(hh / FT, (intercept + slope * hh) / KT, "-", label="profile used")
    ax.set_xlabel("altitude, ft")
    ax.set_ylabel("wind speed, kt")
    ax.set_title(f"Simulator wind, from {np.degrees(direction) + 180:.0f} deg")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "boeing-wind.png", dpi=80)

    compare(wind, results)


if __name__ == "__main__":
    main()
