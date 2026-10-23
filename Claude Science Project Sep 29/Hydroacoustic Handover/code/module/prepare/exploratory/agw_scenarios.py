"""PRE-REGISTRATION (EXPLORATORY; order-of-magnitude only; never a likelihood term). Committed before any noise
record was fetched and before any signal level was computed. Pete, 10 Oct 2026: "any way we could estimate AGW for
the same scenarios?"

QUESTION: for the two impact scenarios on the scenario charts (a: steep high-speed entry, F-35A type, 175 t; b:
controlled ditching, 175 t), how large is the low-frequency (0.03-5 Hz) full-water-column signal - the acoustic-
gravity / low-order acoustic modes - at Cape Leeuwin (H01W) and Diego Garcia South (H08S), compared with measured
ocean pressure noise in the same band?

GEOMETRY (as the scenario charts): impact 37.23 S 89.58 E. Receivers H01W1 and H08S1 (data/stations.csv),
hydrophone depths 1,063 m and 1,413 m. Great-circle paths sampled every 10 km; water depth from GEBCO_2026
(agw_regime.depth_at, 3x3 median). Source depth h_s and receiver water depth h_r from the same grid.

SIGNAL MODEL (stated now, not tuned):
  - Source: a vertical surface force impulse J (N s) = m v_z, with a single-pole roll-off
    |F(f)|^2 = J^2 / (1 + (2 pi f tau)^2). The impact is a point force on a pressure-release surface, which is
    equivalent to a vertical dipole just below the surface. Horizontal momentum is NOT modelled (a horizontal
    surface force is a further-cancelled source); declared.
  - Waveguide: isovelocity c = 1,500 m/s, rigid bottom, no gravity term (gravity changes the modes by
    O(g / (omega c)) <= 2 % at f >= 0.05 Hz). Pressure modes psi_n = sqrt(2/h) sin(gamma_n z),
    gamma_n = (n - 1/2) pi / h. Projecting the Helmholtz equation on psi_n with p(0) = F delta(r) gives
    a_n = (i/4) psi_n'(0) F H0(k_n r) (the point-source normal-mode result, Jensen et al. 2011, ch. 5, with the
    source term moved into the surface boundary condition). Adiabatic along the path:
    |P_n|^2 = |F|^2 / 16 * (2/h_s) gamma_n,s^2 * (1/h_r) * 2 / (pi kbar_n r)   [receiver-depth average of sin^2 = 1/2]
    where kbar_n is the path-mean horizontal wavenumber. A mode is carried only if it propagates at every path
    point: f > (n - 1/2) c / (2 h_min), h_min the path minimum depth (receiver point included). Modes cut off
    on the path are taken as fully LOST (no tunnelling; Kadri, Abdolali & Kirby 2025 describe partial tunnelling,
    which would restore some energy; declared).
  - Arrival duration: per mode and third-octave band, T_n = max(10 s, r |1/u_n(f_lo) - 1/u_n(f_hi)|),
    u_n = c sqrt(1 - (gamma_n c / omega)^2) evaluated with the path-mean depth.
  - Signal power spectral density during the arrival: S(f) = sum_n [ 2 int_band |P_n|^2 df ] / (T_n B),
    in Pa^2/Hz (one-sided). Summing modes that do not overlap in time overstates S (favours detection); declared.
  - Bottom: rigid gives the largest mode amplitudes; a sediment or elastic bottom (Kadri 2019) loses energy.
    Model uncertainty is stated as +/-10 dB (not propagated beyond the stated band).
SCENARIOS (fixed now):
  (a) m = 175 t, v = 270-360 m/s, entry angle 30-90 deg -> J = m v sin(gamma) = 2.36e7 to 6.30e7 N s;
      tau = 0.1-0.3 s (aircraft length / speed).
  (b) m = 175 t, vertical speed 2.4-8.3 m/s (the vertical KE 0.5-6 MJ of the scenario chart) -> J = 4.2e5 to
      1.45e6 N s; tau = 1-3 s.
  Band drawn between (J_lo, tau_hi) and (J_hi, tau_lo); the line is the geometric mean of J with mean tau.

NOISE (measured, fixed now): RHUM-RUM (RESIF network YV) differential pressure gauges on the deep floor of the
  south-west Indian Ocean, channel BDH: RR50 (25.52 S 70.02 E, 4,118 m), RR40 (28.15 S 63.30 E, 4,780 m),
  RR38 (30.56 S 59.69 E, 4,560 m), RR34 (32.08 S 52.21 E, 4,265 m). Dates 2013-03-01 to 2013-03-14 (same season
  as 8 Mar 2014), 00:00-03:00 UTC each day (the MH370 window hours). Response removed to Pa with obspy
  (pre_filt 0.003/0.005/10/20 Hz). PSD: Welch, 600 s Hann, 50 % overlap, per 3-h block. Reported: median and
  10-90 % over all blocks, and per-station medians. A block is dropped if it has gaps > 1 % or a max |p| > 1e4 Pa
  (glitch); drops are counted.
  PLAUSIBILITY GATE (fixed now): the pooled median must peak (secondary microseism) between 0.1 and 0.5 Hz with a
  peak level between 1e-2 and 1e4 Pa^2/Hz. If it fails, the station is reported and excluded; if all fail, the
  chart is not drawn and the failure is reported.
  CAVEATS declared now: the noise is measured on the sea floor, while the IMS hydrophones sit at 1.0-1.4 km in the
  water column; DPG gains carry ~ +/-3 dB calibration uncertainty (Doran et al. 2019); 2013, not 2014.

DECISION RULE for the wording (fixed now): in each band, SNR = S / N_median. "Not detectable" if the upper end
  of the scenario band is below N_10% by more than 10 dB; "possibly detectable" if the upper end is above
  N_median; otherwise "marginal". The IMS instrument response (-47 dB at 0.1 Hz re 10 Hz) attenuates signal and
  noise alike; the comparison assumes ambient noise stays above instrument self-noise (unverified; if not, the
  signal is harder to see).

OUTPUTS: <out>/rhumrum_dpg_psd.npz, <out>/rhumrum_dpg_summary.json, <out>/agw_scenarios.csv (band, station,
  scenario, S_lo, S_mid, S_hi, N10, N50, N90, n_modes, T_mean), <out>/agw_paths.json (h_s, h_r, h_min, ranges).
Usage: python agw_scenarios.py <out_dir> noise | signal
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agw_regime import depth_at  # noqa: E402

C = 1500.0
R_EARTH = 6371.0088e3
SRC = (-37.23, 89.58)
RECV = {"H01W": (-34.892899, 114.153900, 1063.0), "H08S": (-7.645300, 72.474403, 1413.0)}
DPG = ["RR50", "RR40", "RR38", "RR34"]
SCEN = {
    "a": dict(J=(175e3 * 270 * 0.5, 175e3 * 360 * 1.0), tau=(0.1, 0.3)),
    "b": dict(J=(175e3 * 2.4, 175e3 * 8.3), tau=(1.0, 3.0)),
}
FC = 10 ** (np.arange(-15, 8) / 10.0)


def gc_path(a, b, step=10e3):
    la1, lo1, la2, lo2 = map(np.radians, (a[0], a[1], b[0], b[1]))
    d = 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))
    n = max(2, int(d * R_EARTH / step) + 1)
    t = np.linspace(0, 1, n)
    A = np.sin((1 - t) * d) / np.sin(d)
    B = np.sin(t * d) / np.sin(d)
    x = A * np.cos(la1) * np.cos(lo1) + B * np.cos(la2) * np.cos(lo2)
    y = A * np.cos(la1) * np.sin(lo1) + B * np.cos(la2) * np.sin(lo2)
    z = A * np.sin(la1) + B * np.sin(la2)
    return np.degrees(np.arctan2(z, np.hypot(x, y))), np.degrees(np.arctan2(y, x)), d * R_EARTH


def signal(out: Path):
    rows, paths = [], {}
    for st, (la, lo, zr) in RECV.items():
        plat, plon, r = gc_path(SRC, (la, lo))
        h = depth_at(plat, plon)
        h_s, h_r = float(h[0]), float(h[-1])
        h_min = float(h.min())
        h_bar = float(np.mean(h[h > 0])) if (h > 0).any() else 0.0
        paths[st] = dict(range_km=r / 1e3, h_s=h_s, h_r=h_r, h_min=h_min, h_mean=h_bar,
                         land_points=int((h <= 0).sum()), receiver_depth_m=zr,
                         h_min_at=[float(plat[h.argmin()]), float(plon[h.argmin()])])
        for f0 in FC:
            flo, fhi = f0 * 2 ** (-1 / 6), f0 * 2 ** (1 / 6)
            ff = np.linspace(flo, fhi, 64)
            B = fhi - flo
            nmax = int(2 * fhi * max(h_s, 1) / C + 1)
            for sc, p in SCEN.items():
                out_S = {}
                for tag, J, tau in (("lo", p["J"][0], p["tau"][1]), ("hi", p["J"][1], p["tau"][0]),
                                    ("mid", np.sqrt(p["J"][0] * p["J"][1]), np.mean(p["tau"]))):
                    S, nm, Ts = 0.0, 0, []
                    for n in range(1, nmax + 1):
                        f_cut = (n - 0.5) * C / (2 * min(h_min, h_s, h_r)) if h_min > 0 else np.inf
                        ok = ff > f_cut
                        if not ok.any():
                            continue
                        w = 2 * np.pi * ff[ok]
                        g_s = (n - 0.5) * np.pi / h_s
                        g_b = (n - 0.5) * np.pi / h_bar
                        kbar = np.sqrt(np.maximum((w / C) ** 2 - g_b ** 2, 1e-30))
                        F2 = J ** 2 / (1 + (w * tau) ** 2)
                        P2 = F2 / 16 * (2 / h_s) * g_s ** 2 * (1 / h_r) * 2 / (np.pi * kbar * r)
                        E = 2 * np.trapezoid(P2, ff[ok]) if ok.sum() > 1 else 2 * P2[0] * B
                        u = C * np.sqrt(np.maximum(1 - (g_b * C / w) ** 2, 1e-12))
                        T = max(10.0, r * abs(1 / u.min() - 1 / u.max()))
                        S += E / (T * B)
                        nm += 1
                        Ts.append(T)
                    out_S[tag] = (S, nm, float(np.mean(Ts)) if Ts else np.nan)
                rows.append(dict(station=st, f_hz=f0, scenario=sc, S_lo=out_S["lo"][0], S_mid=out_S["mid"][0],
                                 S_hi=out_S["hi"][0], n_modes=out_S["mid"][1], T_mean_s=out_S["mid"][2]))
    import pandas as pd
    df = pd.DataFrame(rows)
    nz = out / "rhumrum_dpg_psd.npz"
    if nz.exists():
        d = np.load(nz)
        f, q = d["f"], d["pooled_q"]
        for k, name in enumerate(("N10", "N50", "N90")):
            df[name] = np.interp(np.log(df.f_hz), np.log(f[1:]), q[k, 1:])
    df.to_csv(out / "agw_scenarios.csv", index=False)
    (out / "agw_paths.json").write_text(json.dumps(paths, indent=1))
    print(json.dumps(paths, indent=1))


def noise(out: Path):
    from obspy import UTCDateTime
    from obspy.clients.fdsn import Client
    from scipy.signal import welch
    cl = Client("RESIF", timeout=300)
    psds, meta, drops = {}, {}, {}
    for sta in DPG:
        inv = cl.get_stations(network="YV", station=sta, channel="BDH", level="response",
                              starttime=UTCDateTime("2013-03-01"), endtime=UTCDateTime("2013-03-15"))
        meta[sta] = str(inv[0][0][0].response.instrument_sensitivity)
        psds[sta], drops[sta] = [], 0
        for day in range(1, 15):
            t0 = UTCDateTime(2013, 3, day, 0, 0)
            try:
                s = cl.get_waveforms("YV", sta, "00", "BDH", t0 - 600, t0 + 3 * 3600 + 600)
            except Exception as e:  # no data
                drops[sta] += 1
                print(sta, day, "no data", type(e).__name__)
                continue
            s.merge(fill_value=None)
            tr = s[0]
            if np.ma.isMaskedArray(tr.data) and tr.data.mask.mean() > 0.01:
                drops[sta] += 1
                continue
            tr.data = np.ma.filled(tr.data, 0).astype(float) if np.ma.isMaskedArray(tr.data) else tr.data.astype(float)
            tr.detrend("demean")
            tr.remove_response(inventory=inv, output="DEF", pre_filt=(0.003, 0.005, 10, 20), water_level=None)
            tr.trim(t0, t0 + 3 * 3600)
            if len(tr.data) < 0.99 * 3 * 3600 * tr.stats.sampling_rate or np.abs(tr.data).max() > 1e4:
                drops[sta] += 1
                continue
            fs = tr.stats.sampling_rate
            f, p = welch(tr.data, fs=fs, window="hann", nperseg=int(600 * fs), noverlap=int(300 * fs))
            keep = f <= 5.5
            psds[sta].append(p[keep])
            fk = f[keep]
            print(sta, day, "ok", f"{np.interp(0.2, fk, p[keep]):.3g}")
    allp = np.array([p for v in psds.values() for p in v])
    q = np.percentile(allp, [10, 50, 90], axis=0)
    band = (fk >= 0.1) & (fk <= 0.5)
    i = np.argmax(np.where(band, q[1], -np.inf))
    gate = bool(0.1 <= fk[i] <= 0.5 and 1e-2 <= q[1][i] <= 1e4)
    per = {s: np.median(np.array(v), axis=0) for s, v in psds.items() if v}
    np.savez(out / "rhumrum_dpg_psd.npz", f=fk, pooled_q=q, **{f"median_{s}": v for s, v in per.items()})
    summ = dict(stations=DPG, blocks={s: len(v) for s, v in psds.items()}, drops=drops, sensitivity=meta,
                pooled_peak_hz=float(fk[i]), pooled_peak_pa2_hz=float(q[1][i]), gate_pass=gate,
                levels_db_re_1upa2_hz={f"{x:g}": [float(10 * np.log10(np.interp(x, fk[1:], qq[1:]) / 1e-12)) for qq in q]
                                       for x in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)})
    (out / "rhumrum_dpg_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    o = Path(sys.argv[1])
    o.mkdir(parents=True, exist_ok=True)
    {"noise": noise, "signal": signal}[sys.argv[2]](o)
