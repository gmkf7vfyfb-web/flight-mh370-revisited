"""PRE-REGISTRATION and implementation (Pete, 9 Oct): characterise the received energy of each pulse of the
9.98 s airgun-like train at H08S, find cycles that are outliers from it (constructive or destructive
interference from a non-airgun source), and ask whether outliers coincide with an H01W trigger in the way an
impact inside the impact PDF, at its impact time, requires. Committed before any shot or gap energy was
computed.

DATA: Kadri (2024) Figure 9 plotted polylines (kadri_trace_pairs.py; filtered 2-40 Hz, single channel,
  vertex-simplified at a median spacing of 0.049 s). NOT raw IMS. Energies are approximate in absolute
  terms; comparisons are made only between cycles of the same panel.
PHYSICS NOTE, fixed now:
  - Energies of unrelated broadband sources add on average (zero-mean cross term), so EXCESS energy is the
    principled statistic (PRIMARY).
  - A deficit needs an interfering signal comparable to the shot and is no more likely than an excess. It
    is reported (SECONDARY, Pete's request) but carries no weight of its own.
  - The inter-shot GAP is the sensitive interval: shots far exceed ambient noise, gaps are near it.
CYCLES:
  - The trace is resampled at 40 Hz (linear interpolation of the vertices); the envelope is p^2 smoothed by
    a 0.5 s boxcar.
  - Shot peaks are envelope maxima at least 7 s apart, with prominence >= 10 x the panel's median envelope.
  - Cycle i runs from peak i to peak i+1; cycles longer than 15 s are flagged 'missed shot' and excluded.
  - E_shot = integral of p^2 over [peak - 1 s, peak + 3 s].
  - P_gap = mean p^2 over [peak + 4 s, next peak - 1 s].
OUTLIERS:
  - Residual r = log10(E) minus its running median over 13 cycles (centred), separately for E_shot and
    P_gap and for each panel.
  - z = r / (1.4826 MAD(r)), MAD taken over the panel.
  - HIGH: z >= 3 (primary). LOW: z <= -3 (secondary).
  - An outlier's time is the shot peak (shot outliers) or the envelope maximum inside the gap (gap
    outliers).
COINCIDENCE WITH H01W (Cape Leeuwin), and with the impact PDF at its impact time:
  - Inputs: an outlier at t2 and an H01W trigger t1 (strict, loose, or a bearing-gated Table 1 event, as
    kadri_trace_pairs.py).
  - They are COINCIDENT iff t2 - t1 lies in the pre-registered pair span [855.93, 1346.50] s AND the pair's
    log10 Bayes factor is >= 1.
  - The Bayes factor compares an impact in the stand-in PDF against a chance pair, using both arrival times
    against the impact time 00:19:37 + 300 +- 180 s, plus the H01W bearing for Table 1 events (scoring
    identical to the pair-source addendum of 9 Oct).
  - STATISTIC: N = the number of outlier cycles with at least one coincident H01W trigger, for each class
    (shot-high, gap-high, shot-low, gap-low) and each H01W variant.
NULL: cyclic shifts of the outlier flags over the concatenated cycle list (shift k = 1 .. n-1). A shifted
  outlier takes the time of cycle (i+k) mod n plus its own within-cycle offset. p = (1 + #{N_null >= N}) /
  (1 + n - 1).
SENSITIVITY (injection, so that a null result means something):
  - Template: T_C2 (the module's 05:03:01 RCS far-field transient, 5-40 Hz).
  - Injection: interpolated onto the 40 Hz series and added at uniform random times in the H08S span. 300
    injections per SNR_gap in {0, 3, 6, 10, 15, 20, 25} dB, where SNR_gap = template energy over its peak
    4 s divided by (median P_gap x 4 s).
  - Scoring: the injection is detected if its cycle becomes a HIGH outlier (shot or gap).
  - Report P_D(SNR_gap), with the median gap power relative to the median shot energy.
READING (fixed now): p < 0.05 means "more PDF-consistent outlier coincidences than chance": a candidate,
  not a detection. Otherwise "consistent with chance". No likelihood is returned (gate).
PROVENANCE: impact PDF = stand-in from run no-exhaustion-prior (b3dd44b), prior track 295.66 +- 1.0 deg,
  config sensitivity/no-exhaustion-prior.toml.
Usage: python h08s_shot_outliers.py <kadri data dir> <stand-in summary json> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

sys.path.insert(0, str(Path(__file__).parent))
import imos_detectors as D  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402
import kadri_table1_test as KT  # noqa: E402
import kadri_trace_pairs as T  # noqa: E402
import synthetic_composer_test as S  # noqa: E402

HERE = Path(__file__).parent.parent
FS = 40.0
SPAN = (855.93, 1346.50)
SNRS = [0, 3, 6, 10, 15, 20, 25]
N_INJ = 300
SEED = 20261009


def load(kd, pnl):
    tr = pd.read_csv(kd / "kadri-figure-extraction" / "figure9-vector-traces" / f"kadri-2024-figure9-panel-{pnl}-H08S.csv")
    t = (pd.to_datetime(tr.utc) - KT.DAY0).dt.total_seconds().values
    o = np.argsort(t)
    t, p = t[o], tr.pressure_pa.values[o]
    tg = np.arange(t[0], t[-1], 1 / FS)
    return tg, np.interp(tg, t, p)


def cycles(tg, p):
    k = int(0.5 * FS)
    env = np.convolve(p ** 2, np.ones(k) / k, "same")
    pk, _ = signal.find_peaks(env, distance=int(7 * FS), prominence=10 * np.median(env))
    rows = []
    for i in range(len(pk) - 1):
        a, b = tg[pk[i]], tg[pk[i + 1]]
        if b - a > 15.0:
            continue
        ms = (tg >= a - 1) & (tg <= a + 3)
        mg = (tg >= a + 4) & (tg <= b - 1)
        if mg.sum() < FS:
            continue
        jg = np.flatnonzero(mg)[np.argmax(env[mg])]
        rows.append(dict(t_shot=a, t_next=b, E_shot=float(np.sum(p[ms] ** 2) / FS), P_gap=float(np.mean(p[mg] ** 2)), t_gapmax=float(tg[jg])))
    c = pd.DataFrame(rows)
    for col in ["E_shot", "P_gap"]:
        lg = np.log10(c[col].values)
        med = pd.Series(lg).rolling(13, center=True, min_periods=5).median().values
        r = lg - med
        c[f"z_{col}"] = r / (1.4826 * np.nanmedian(np.abs(r - np.nanmedian(r))))
    return c, pk, env


def scorer(summary):
    rng = np.random.default_rng(S.SEED)
    ridge, grid, dens, _ = S.ridge_and_marginal(summary)
    q, _ = S.fit_small_circle(ridge)
    pr = S.draw_prior(rng, q, grid, dens, S.N_PRIOR, S.BASE["sigma_x_nm"])[::10]
    g = S.station_geometry(pr)
    d1, d2, b1 = g["H01W"][0], g["H08S"][0], g["H01W"][1]
    t1p, t2p = d1 / S.C_KM_S, d2 / S.C_KM_S
    sd1 = np.hypot(S.BASE["pick_s"], d1 * S.SD_C_KM_S / S.C_KM_S ** 2)
    sd2 = np.hypot(S.BASE["pick_s"], d2 * S.SD_C_KM_S / S.C_KM_S ** 2)
    t0, st = KT.T_IMPACT_REF + S.BASE["mu_t_s"], S.BASE["sigma_t_s"]
    c11, c22, c12 = sd1 ** 2 + st ** 2, sd2 ** 2 + st ** 2, st ** 2
    det = c11 * c22 - c12 ** 2

    def l10bf(a, b, bear=None):
        r1, r2 = a - t0 - t1p, b - t0 - t2p
        ll = -0.5 * (c22 * r1 ** 2 - 2 * c12 * r1 * r2 + c11 * r2 ** 2) / det - 0.5 * np.log((2 * np.pi) ** 2 * det)
        lbg = -2 * np.log(7200.0)
        if bear is not None:
            sc = 3.3 / np.sqrt(3.0)
            z = S.wrap180(bear - b1) / sc
            ll = ll - 2.0 * np.log1p(z * z / 3.0) - np.log(sc) + np.log(2 / np.pi / np.sqrt(3))
            lbg -= np.log(360.0)
        m = ll.max()
        return float((np.log(np.mean(np.exp(ll - m))) + m - lbg) / np.log(10))
    return l10bf


def coincident(t2, h01, l10bf):
    for a, bear in h01:
        if SPAN[0] <= t2 - a <= SPAN[1] and l10bf(float(a), float(t2), bear) >= 1.0:
            return True
    return False


def template():
    meta = P.parse_meta()
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    sos = signal.butter(4, [5, 40], btype="bandpass", fs=N.FS_D, output="sos")
    t = D.DAY0 + pd.Timedelta("05:03:01")
    for _, r in recs[recs.logger == 3315].iterrows():
        f = P.IMOS / r.file
        t0 = r.start_logger + pd.Timedelta(seconds=D.subsec(f))
        t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta["3315"], t0))
        s = (t - t0).total_seconds()
        xd = N.decimate(N.read_volts(f))
        if 10 <= s <= len(xd) / N.FS_D - 50:
            y = signal.sosfiltfilt(sos, xd[int((s - 2) * N.FS_D): int((s + 20) * N.FS_D)])
            return signal.resample_poly(y, int(FS), N.FS_D)
    raise RuntimeError("template not found")


def main(kd, summary, out_dir):
    kd, out = Path(kd), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    l10bf = scorer(summary)
    h01 = {}
    for op, ratio in T.RATIOS.items():
        ts = []
        for pnl in "abc":
            t, s = T.triggers(kd, pnl, ratio)
            ts.append(t[(t >= s[0]) & (t <= s[1])])
        h01[op] = [(a, None) for a in np.concatenate(ts)]
    table = pd.read_csv(kd / "kadri-table1-transients.csv")
    table["t_s"] = [KT.secs(x) for x in table.time_utc]
    gated = table[(table.bearing_deg >= 246.03) & (table.bearing_deg <= 284.25)]
    h01["table1_gated"] = [(r.t_s, r.bearing_deg) for r in gated.itertuples()]
    series, cyc = {}, []
    for pnl in "de":
        tg, p = load(kd, pnl)
        c, _, _ = cycles(tg, p)
        c["panel"] = pnl
        series[pnl] = (tg, p, c)
        cyc.append(c)
    C = pd.concat(cyc, ignore_index=True)
    classes = {"shot_high": ("z_E_shot", 1, "t_shot"), "gap_high": ("z_P_gap", 1, "t_gapmax"),
               "shot_low": ("z_E_shot", -1, "t_shot"), "gap_low": ("z_P_gap", -1, "t_gapmax")}
    res, outl = {}, []
    n = len(C)
    for cname, (zc, sgn, tcol) in classes.items():
        flag = (sgn * C[zc].values >= 3.0)
        off = C[tcol].values - C.t_shot.values
        for v, h in h01.items():
            obs = sum(coincident(C[tcol].values[i], h, l10bf) for i in np.flatnonzero(flag))
            nl = []
            for k in range(1, n):
                idx = np.flatnonzero(np.roll(flag, k))
                nl.append(sum(coincident(C.t_shot.values[i] + off[(i - k) % n], h, l10bf) for i in idx))
            nl = np.array(nl)
            p = float((1 + (nl >= obs).sum()) / n)
            res[f"{cname}|{v}"] = dict(n_outliers=int(flag.sum()), n_coincident=int(obs), null_mean=float(nl.mean()),
                                       null_q95=float(np.quantile(nl, 0.95)), p=p,
                                       reading="more PDF-consistent coincidences than chance" if p < 0.05 else "consistent with chance")
        for i in np.flatnonzero(flag):
            outl.append(dict(cls=cname, panel=C.panel.iloc[i], t_utc=str(KT.DAY0 + pd.Timedelta(seconds=float(C[tcol].iloc[i])))[11:19], z=float(C[zc].iloc[i]),
                             coincident={v: coincident(C[tcol].values[i], h, l10bf) for v, h in h01.items()}))
    # sensitivity by injection
    tm = template()
    rng = np.random.default_rng(SEED)
    pdrows = []
    w4 = int(4 * FS)
    e4 = np.convolve(tm ** 2, np.ones(w4), "valid").max() / FS
    for snr in SNRS:
        hit = 0
        for _ in range(N_INJ):
            pnl = rng.choice(["d", "e"])
            tg, p, c0 = series[pnl]
            pg = float(np.median(c0.P_gap))
            g = np.sqrt(10 ** (snr / 10) * pg * 4.0 / e4)
            i0 = int(rng.uniform(20 * FS, len(tg) - len(tm) - 20 * FS))
            x = p.copy()
            x[i0: i0 + len(tm)] += g * tm
            c1, _, _ = cycles(tg, x)
            tinj = tg[i0 + int(np.argmax(np.convolve(tm ** 2, np.ones(w4), "same")))]
            j = np.flatnonzero((c1.t_shot.values - 1 <= tinj) & (c1.t_next.values - 1 > tinj))
            if len(j) and ((c1.z_E_shot.values[j[0]] >= 3) or (c1.z_P_gap.values[j[0]] >= 3)):
                hit += 1
        pdrows.append(dict(snr_gap_db=snr, pd=hit / N_INJ, n=N_INJ))
    ratio_gap_shot_db = float(10 * np.log10(np.median(C.P_gap) * 4.0 / np.median(C.E_shot)))
    summ = dict(n_cycles=int(n), cycles_per_panel=C.groupby("panel").size().to_dict(), period_s_median=float(np.median(C.t_next - C.t_shot)),
                gap_vs_shot_energy_db=ratio_gap_shot_db, results=res, injection_pd=pdrows,
                provenance="stand-in prior, run no-exhaustion-prior (b3dd44b), track 295.66 +- 1.0 deg")
    (out / "h08s_shot_outliers.json").write_text(json.dumps(summ, indent=1, default=str))
    C.to_csv(out / "h08s_cycles.csv", index=False)
    pd.DataFrame(outl).to_csv(out / "h08s_outliers.csv", index=False)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:4])
