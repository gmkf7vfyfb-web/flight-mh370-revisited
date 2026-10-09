"""PRE-REGISTRATION and implementation, amended-sequence item 2b: detectors on the IMOS raw data, with
positive controls and a test of Kadri's H01W transients at Perth Canyon. Committed BEFORE any recording
with role 'S', or any recording covering a Kadri window, is read. (Background recordings 'B' were read
for item 1d at b0c5fd0; positive-control recordings lie in B.)

TIME BASE (fixed by 1d): true UTC = footer 'First Data' + sub-second field/65536 s - e(t) (convention A,
accepted at 1d; the sub-second reading reproduces CMST's Scott Reef record start 01:29:45.9 to 0.02 s).

NO ARRAY BEARING ON IMOS. Each logger is a single hydrophone, and the paired loggers (3315/3376,
3274/3275) record in alternating, NON-overlapping 5 min slots. A time-difference bearing is impossible;
the pairs are used for COVERAGE (site coverage = union of their recordings).

DETECTORS (500 Hz decimated series, imos_noise.read_volts/decimate):
  D1 energy ratio: 4th-order Butterworth 5-40 Hz zero-phase; STA = mean square over 2 s, LTA = mean
     square over the 30 s immediately preceding the STA; statistic = STA/LTA, every 0.1 s. The first 32 s
     of each recording cannot be scored (lost coverage, reported as d1_scored_s).
  D2 band-power exceedance: 1 s Hann periodogram levels in 5-20 Hz and in 10-40 Hz minus the logger's
     background median (1d noise_bands.csv p50_1s; 5-20 = power mean of the 5-10 and 10-20 medians,
     10-40 = power mean of 10-20 and 20-40); statistic = max over the two bands of the 3 s running mean
     of the excess, dB.
  D3 two-site coincidence (MH370 windows only): a detection at Perth Canyon (3315/3376) AND at Scott Reef
     or Portland; likelihood ratio = p(dt | stand-in impact) / p(dt | independent, uniform over the two
     windows), pick sd 10 s each.
WINDOW NULL: for a test window of length L, the null is the window-max statistic over ALL windows of
  length min(L, scorable length) (step 1 s) inside the logger's background recordings, LEAVE-ONE-
  RECORDING-OUT when the tested recording is itself in B. p = fraction of the null >= observed.
DETECTION: p < 0.05 for a pre-specified single window (controls, Kadri); for the MH370 search,
  Bonferroni over 5 loggers x 2 detectors: p < 0.005. Otherwise 'not detected', with an UPPER LIMIT =
  the window's maximum 1 s 5-40 Hz band SPL (dB re 1 uPa).
SNR (every window): max 1 s 5-40 Hz SPL in the window minus the background median 1 s 5-40 Hz SPL, dB.

TEST 1, POSITIVE CONTROLS (published arrival times):
  C1 3315 Curtin event 01:33:44 UTC +/- 10 s (CMST 2014-30 p. 6).
  C2 3315 05:03:01 UTC +/- 10 s (CMST p. 15; p. 17 table; high SNR).
  C3 3315 05:18:13 UTC +/- 10 s (CMST p. 15; 'much lower amplitude').
  C4 3250 Curtin event onset 01:32:49 UTC, window [01:32:39, 01:33:09] (CMST Scott Reef note p. 1:
     onset plus the ~10 s 'initial high amplitude arrival').
  Pass: C1, C2 and C4 detected by D1 or D2. C3 reported. A detector failing C1/C2/C4 is reported as
  failed and kept.
  Exploratory: the first 60 s of the first 3376 recording starting after C1 and after C2 (tails; CMST
  reports tails >= 100 s).

TEST 2, MH370 WINDOWS: every recording overlapping S_true (preregistration.json), window = the overlap.
  Per logger x detector: max statistic, time, p, SNR, detection or upper limit; then D3.

TEST 3, KADRI'S H01W TRANSIENTS AT PERTH CANYON. Each of Kadri's events (Table 1, 19 rows; the 306.18 deg
  'major signal' at both of his times, 00:52:03 (text p. 9, Fig. 9c peak) and 00:54:30 (caption p. 14);
  the 57 deg signal at 00:52:03): sources along bearings b +/- 6.6 deg (2 x 3.3 deg demonstrated),
  ranges 300-3000 km from H01W (FDSN centroid); predicted arrival at 3315 and 3376 = t_H01W - r/c +
  d(P, logger)/c, c = 1.482 km/s; window = [min, max] +/- 10 s, clipped to recordings; 'not covered'
  if none. D1/D2 as in TEST 1.
  Amplitude (main candidate): Kadri's level at H01W = RMS over +/- 1 s of the digitised Fig. 9c trace
  at his time (2-40 Hz; CLIPPED at the plot's +/- 1 Pa, so a lower bound), dB re 1 uPa.
  Verdict per time: 'disfavoured at Perth Canyon' if one logger's window is fully covered, nothing is
  detected, and the upper-limit SPL is >= 20 dB below Kadri's H01W level (20 dB allows for C_site and
  canyon-floor coupling); 'detected' if detected; otherwise 'uninformative'.

OUTPUTS: <out>/controls.csv, mh370_windows.csv, d3_coincidence.json, kadri_windows.csv, summary.json.
Usage: python imos_detectors.py <out_dir> <kadri_data_dir> <stand-in summary json>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from pyproj import Geod
from scipy import signal

sys.path.insert(0, str(Path(__file__).parent))
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402

HERE = Path(__file__).parent.parent
GEOD = Geod(ellps="WGS84")
SOS_D1 = signal.butter(4, [5, 40], btype="bandpass", fs=N.FS_D, output="sos")
STA, LTA = 2 * N.FS_D, 30 * N.FS_D
H01W = (-34.890303, 114.142637)
DAY0 = pd.Timestamp("2014-03-08", tz="UTC")
CONTROLS = [("C1", 3315, "01:33:44", 10, 10), ("C2", 3315, "05:03:01", 10, 10), ("C3", 3315, "05:18:13", 10, 10),
            ("C4", 3250, "01:32:49", 10, 20)]
LOGGERS = [3315, 3376, 3250, 3274, 3275]


def subsec(path):
    t = open(path, "rb").read()[-1000:].decode("latin1")
    return int(re.search(r"First Data-\S+ \S+ - (\d+)", t).group(1)) / 65536


def pw(*v):
    return 10 * np.log10(np.mean([10 ** (x / 10) for x in v]))


class Rec:
    def __init__(self, row, meta, cal):
        f = P.IMOS / row.file
        t0 = row.start_logger + pd.Timedelta(seconds=subsec(f))
        self.t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta, t0))
        xd = N.decimate(N.read_volts(f))
        self.n = len(xd)
        y = signal.sosfiltfilt(SOS_D1, xd) ** 2
        cs = np.concatenate([[0], np.cumsum(y)])
        i = np.arange(LTA, self.n - STA + 1, N.FS_D // 10)
        self.d1_t = (i + STA / 2) / N.FS_D
        self.d1 = ((cs[i + STA] - cs[i]) / STA) / np.maximum((cs[i] - cs[i - LTA]) / LTA, 1e-30)
        ns = self.n // N.FS_D
        f1, p1 = signal.periodogram(xd[: ns * N.FS_D].reshape(ns, N.FS_D), fs=N.FS_D, window="hann", detrend="constant", axis=-1)
        p1u = p1 / (10 ** ((np.interp(f1, *cal["gain"]) + cal["sens"]) / 10))
        lev = lambda lo, hi: 10 * np.log10(p1u[:, (f1 >= lo) & (f1 < hi)].mean(1))  # noqa: E731
        k = np.ones(3) / 3
        self.d2 = np.max([np.convolve(lev(5, 20) - cal["m5_20"], k, "same"), np.convolve(lev(10, 40) - cal["m10_40"], k, "same")], axis=0)
        self.d2_t = np.arange(ns) + 0.5
        band = (f1 >= 5) & (f1 < 40)
        self.spl = 10 * np.log10(p1u[:, band].sum(1) * (f1[1] - f1[0]))

    def window(self, a, b, spl_med):
        sa, sb = max((a - self.t0).total_seconds(), 0.0), min((b - self.t0).total_seconds(), self.n / N.FS_D)
        if sb <= sa:
            return None
        m1 = (self.d1_t >= sa) & (self.d1_t <= sb)
        m2 = (self.d2_t >= sa) & (self.d2_t <= sb)
        o = dict(covered_s=round(sb - sa, 1), d1_scored_s=round(m1.sum() / 10, 1), len_s=sb - sa)
        o["d1"] = float(self.d1[m1].max()) if m1.any() else np.nan
        o["d1_t"] = str(self.t0 + pd.Timedelta(seconds=float(self.d1_t[m1][np.argmax(self.d1[m1])]))) if m1.any() else None
        o["d2"] = float(self.d2[m2].max()) if m2.any() else np.nan
        o["d2_t"] = str(self.t0 + pd.Timedelta(seconds=float(self.d2_t[m2][np.argmax(self.d2[m2])]))) if m2.any() else None
        o["spl_max"] = float(self.spl[m2].max()) if m2.any() else np.nan
        o["snr_db"] = o["spl_max"] - spl_med
        return o


def null_max(brecs, det, L, exclude=None):
    vals = []
    for r in brecs:
        if r is exclude:
            continue
        x = getattr(r, det)
        rate = 10 if det == "d1" else 1
        w = min(max(int(round(L * rate)), 1), len(x))
        vals.append(sliding_window_view(x, w)[::rate].max(1))
    return np.concatenate(vals)


def main(out_dir, kadri_dir, summary):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pre = json.loads((HERE / "data/imos/preregistration.json").read_text())
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    nb = pd.read_csv(HERE / "results-data/imos1d/noise_bands.csv")
    meta = P.parse_meta()
    cal, cache, B, med = {}, {}, {}, {}
    for cid in LOGGERS:
        m = meta[str(cid)]
        fg, G = N.gain_db(next(P.IMOS.glob(f"*/*alibration/{m['cal_file']}")))
        d = nb[nb.logger == cid].set_index("band").p50_1s
        cal[cid] = dict(gain=(fg, G), sens=m["sens_db"], m5_20=pw(d["5-10"], d["10-20"]), m10_40=pw(d["10-20"], d["20-40"]))

    def load(row):
        if row.file not in cache:
            cache[row.file] = Rec(row, meta[str(row.logger)], cal[row.logger])
        return cache[row.file]

    for cid in LOGGERS:
        B[cid] = [load(r) for _, r in recs[(recs.logger == cid) & (recs.role == "B")].iterrows()]
        med[cid] = float(np.median(np.concatenate([b.spl for b in B[cid]])))

    def test(cid, a, b, label, extra=None):
        rows = []
        near = recs[(recs.logger == cid) & (recs.start_logger > a - pd.Timedelta(minutes=10))
                    & (recs.start_logger < b + pd.Timedelta(minutes=2))]
        for _, r in near.iterrows():
            rr = load(r)
            w = rr.window(a, b, med[cid])
            if w is None:
                continue
            ex = rr if r.role == "B" else None
            for det in ["d1", "d2"]:
                nl = null_max(B[cid], det, w["len_s"], exclude=ex)
                w[f"p_{det}"] = float((nl >= w[det]).mean()) if np.isfinite(w[det]) else np.nan
            w.update(dict(test=label, logger=cid, file=r.file, role=r.role, win_a=str(a), win_b=str(b), **(extra or {})))
            rows.append(w)
        if not rows:
            rows.append(dict(test=label, logger=cid, file=None, role=None, win_a=str(a), win_b=str(b), covered_s=0.0, **(extra or {})))
        return rows

    # TEST 1
    ctl = []
    for lab, cid, hms, pre_s, post_s in CONTROLS:
        t = DAY0 + pd.Timedelta(hms)
        ctl += test(cid, t - pd.Timedelta(seconds=pre_s), t + pd.Timedelta(seconds=post_s), lab)
    for lab, hms in [("C1-tail-3376", "01:33:44"), ("C2-tail-3376", "05:03:01")]:
        t = DAY0 + pd.Timedelta(hms)
        cand = recs[(recs.logger == 3376) & (recs.start_logger > t - pd.Timedelta(minutes=1)) & (recs.start_logger < t + pd.Timedelta(minutes=16))]
        r0 = min((load(r) for _, r in cand.iterrows()), key=lambda r: r.t0)
        ctl += test(3376, r0.t0, r0.t0 + pd.Timedelta(seconds=60), lab, dict(exploratory=True, lag_after_published_s=(r0.t0 - t).total_seconds()))
    ctl = pd.DataFrame(ctl)
    ctl["detected"] = (ctl.p_d1 < 0.05) | (ctl.p_d2 < 0.05)
    ctl.to_csv(out / "controls.csv", index=False)
    print(ctl[["test", "logger", "covered_s", "d1", "p_d1", "d2", "p_d2", "snr_db", "detected"]].round(4).to_string(index=False))

    # TEST 2
    mh = []
    for cid in LOGGERS:
        a, b = (pd.Timestamp(x) for x in pre["loggers"][str(cid)]["S_true"])
        mh += test(cid, a, b, "MH370")
    mh = pd.DataFrame(mh)
    mh["detected"] = (mh.p_d1 < 0.005) | (mh.p_d2 < 0.005)
    mh.to_csv(out / "mh370_windows.csv", index=False)
    print(mh[["logger", "file", "role", "covered_s", "d1", "p_d1", "d1_t", "d2", "p_d2", "snr_db", "spl_max", "detected"]].round(4).to_string(index=False))

    det = mh[mh.detected]
    d3 = dict(n_detections=int(len(det)), pairs=[])
    pc, far = det[det.logger.isin([3315, 3376])], det[det.logger.isin([3250, 3274, 3275])]
    if len(pc) and len(far):
        rng = np.random.default_rng(P.sct.SEED)
        ridge, grid, dens, _ = P.sct.ridge_and_marginal(summary)
        q, _ = P.sct.fit_small_circle(ridge)
        pr = P.sct.draw_prior(rng, q, grid, dens, P.sct.N_PRIOR, P.sct.BASE["sigma_x_nm"])
        n = len(pr)
        for _, x in pc.iterrows():
            for _, y in far.iterrows():
                mx, my = meta[str(x.logger)], meta[str(y.logger)]
                _, _, dx = GEOD.inv(np.full(n, mx["lon"]), np.full(n, mx["lat"]), pr[:, 1], pr[:, 0])
                _, _, dy = GEOD.inv(np.full(n, my["lon"]), np.full(n, my["lat"]), pr[:, 1], pr[:, 0])
                ddt = (dy - dx) / 1000 / P.C_G
                tx = pd.Timestamp(x.d1_t if x.p_d1 <= x.p_d2 else x.d2_t)
                ty = pd.Timestamp(y.d1_t if y.p_d1 <= y.p_d2 else y.d2_t)
                obs, sd = (ty - tx).total_seconds(), np.sqrt(2) * 10.0
                lik = np.mean(np.exp(-0.5 * ((obs - ddt) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)))
                d3["pairs"].append(dict(a=int(x.logger), b=int(y.logger), dt_s=obs, LR=float(lik * (x.len_s + y.len_s))))
    (out / "d3_coincidence.json").write_text(json.dumps(d3, indent=1))

    # TEST 3
    kd = Path(kadri_dir)
    tab = pd.read_csv(kd / "kadri-table1-transients.csv")
    ev = [(f"T1_{r.time_utc}_{r.bearing_deg}", r.time_utc, float(r.bearing_deg)) for r in tab.itertuples()]
    ev += [("major306_at_005203_text", "00:52:03", 306.18), ("major306_at_005430_caption", "00:54:30", 306.18),
           ("major057_at_005203_caption", "00:52:03", 57.0)]
    rr = np.linspace(300, 3000, 55)
    kw = []
    for name, hms, brg in ev:
        th = DAY0 + pd.Timedelta(hms)
        for cid in [3315, 3376]:
            m = meta[str(cid)]
            ts = []
            for bb in np.linspace(brg - 6.6, brg + 6.6, 23):
                lon2, lat2, _ = GEOD.fwd(np.full(len(rr), H01W[1]), np.full(len(rr), H01W[0]), np.full(len(rr), bb), rr * 1000)
                _, _, d = GEOD.inv(np.full(len(rr), m["lon"]), np.full(len(rr), m["lat"]), lon2, lat2)
                ts.append(-rr / P.C_G + d / 1000 / P.C_G)
            ts = np.concatenate(ts)
            a, b = th + pd.Timedelta(seconds=float(ts.min() - 10)), th + pd.Timedelta(seconds=float(ts.max() + 10))
            kw += test(cid, a, b, "Kadri", dict(event=name, bearing=brg, t_H01W=hms, win_len_s=(b - a).total_seconds()))
    kw = pd.DataFrame(kw)
    kw["detected"] = (kw.p_d1 < 0.05) | (kw.p_d2 < 0.05)
    trc = pd.read_csv(kd / "kadri-figure-extraction/figure9-vector-traces/kadri-2024-figure9-panel-c-H01W.csv")
    tt = (pd.to_datetime(trc.utc, utc=True) - DAY0).dt.total_seconds().values
    amp, verdicts = {}, {}
    for hms in ["00:52:03", "00:54:30"]:
        s = pd.Timedelta(hms).total_seconds()
        msk = (tt >= s - 1) & (tt <= s + 1)
        prms = float(np.sqrt(np.mean(trc.pressure_pa.values[msk] ** 2)))
        amp[hms] = dict(rms_pa=prms, spl_db_re_1uPa=float(20 * np.log10(prms / 1e-6)), clipped_lower_bound=True)
    for name, hms in [("major306_at_005203_text", "00:52:03"), ("major306_at_005430_caption", "00:54:30")]:
        sub = kw[kw.event == name]
        full = any(g.covered_s.sum() >= 0.999 * g.win_len_s.iloc[0] for _, g in sub.groupby("logger"))
        anydet = bool(sub.detected.any())
        ul = float(sub.spl_max.max()) if sub.spl_max.notna().any() else np.nan
        gap = amp[hms]["spl_db_re_1uPa"] - ul if np.isfinite(ul) else np.nan
        v = "detected at Perth Canyon" if anydet else ("disfavoured at Perth Canyon" if (full and np.isfinite(gap) and gap >= 20) else "uninformative")
        verdicts[name] = dict(window_fully_covered_one_logger=bool(full), any_detection=anydet, upper_limit_spl=ul,
                              kadri_h01w_spl_lower_bound=amp[hms]["spl_db_re_1uPa"], gap_db=gap, verdict=v)
    kw.to_csv(out / "kadri_windows.csv", index=False)
    (out / "summary.json").write_text(json.dumps(dict(controls=ctl.to_dict("records"), kadri_amplitude=amp, kadri_verdicts=verdicts,
                                                      d3=d3, background_spl_median=med,
                                                      mh370_detected=mh[mh.detected][["logger", "file"]].to_dict("records")), indent=1, default=str))
    print(json.dumps(verdicts, indent=1, default=str))
    g = kw.groupby(["event", "logger"]).agg(cov=("covered_s", "sum"), L=("win_len_s", "first"), det=("detected", "any"), snr=("snr_db", "max"))
    print(g.round(1).to_string())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
